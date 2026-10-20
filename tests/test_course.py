import copy
import csv
import importlib.util
import json
import io
import hashlib
import uuid
from pathlib import Path
from statistics import mean
import unittest
from unittest.mock import patch
import numpy as np
import torch
from torch_geometric.data import Data
from course.common import ROOT, RESEARCH, jobs, validate_config, sha256
from course.metrics import accuracy, aggregate
from src.factory import build_model, configure_determinism, seed_all
from src.train import train_model
from src.paths import tensor_hash
from ablation_mlp.factory import build_model as build_component


class MetricTests(unittest.TestCase):
    def test_known_answer_units_direction(self):
        actual=accuracy([0,1,2,1],[0,2,2,0],[True,True,True,False],range(4),range(4))
        self.assertEqual(actual['correct'],2)
        self.assertEqual(actual['size'],3)
        self.assertEqual(actual['accuracy'],2/3)
        self.assertAlmostEqual(actual['accuracy_percent'],200/3)
        self.assertTrue(actual['higher_is_better'])
        numpy_result=accuracy(np.array([0,1]),np.array([0,1]),np.array([True,True]))
        self.assertEqual(json.loads(json.dumps(numpy_result))['correct'],2)
        self.assertGreater(accuracy([0,1],[0,1])['accuracy'],accuracy([1,0],[0,1])['accuracy'])

    def test_alignment_and_invalid_masks(self):
        for call in (
            lambda:accuracy([0],[0,1]),
            lambda:accuracy([0,1],[0,1],prediction_ids=[1,0],label_ids=[0,1]),
            lambda:accuracy([0,1],[0,1],prediction_ids=[0,0],label_ids=[0,0]),
            lambda:accuracy([0],[0],[False]),
            lambda:aggregate([80.,90.])):
            with self.assertRaises(ValueError):call()

    def test_equal_split_weight_and_sample_sd(self):
        result=aggregate([.5,1.0])
        self.assertEqual(result['mean'],.75)
        self.assertAlmostEqual(result['sample_sd'],2**.5/4)
        self.assertEqual(result['ddof'],1)


class ModelAndProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(1)
        configure_determinism()

    def graph(self):
        seed_all(30)
        return Data(x=torch.randn(8,5),
            edge_index=torch.tensor([[0,1,2,3,4,5,6,7,1,4],[1,2,3,4,5,6,7,0,4,1]]),
            y=torch.tensor([0,1,2,0,1,2,0,1]),
            train_mask=torch.tensor([1,1,1,1,0,0,0,0],dtype=torch.bool),
            val_mask=torch.tensor([0,0,0,0,1,1,0,0],dtype=torch.bool),
            test_mask=torch.tensor([0,0,0,0,0,0,1,1],dtype=torch.bool))

    def test_four_scorers_k_shapes_gradients_reset(self):
        for method in ('dot','mlp','mlp_ln','mlp_gelu'):
            for k in (1,2,3,4):
                with self.subTest(method=method,k=k):
                    factory=build_model if method in ('dot','mlp') else build_component
                    model,_=factory(5,3,k,method,42,'cpu')
                    graph=self.graph();model.eval()
                    out,details=model(graph.x,graph.edge_index,return_diagnostics=True)
                    self.assertEqual(tuple(out.shape),(8,3))
                    self.assertEqual(tuple(details[0]['hops'].shape),(8,k+1,32))
                    self.assertEqual(float(details[0]['iterations'][0]['logits'].abs().max()),0.)
                    alpha=details[0]['used_alpha']
                    torch.testing.assert_close(alpha.sum(1),torch.ones(8))
                    self.assertTrue(bool(torch.isfinite(out).all()))
                    torch.nn.functional.nll_loss(out[graph.train_mask],graph.y[graph.train_mask]).backward()
                    for name,p in model.named_parameters():
                        if p.grad is not None:self.assertTrue(bool(torch.isfinite(p.grad).all()))
                        if '.scorer.' in name and name.endswith('weight'):
                            self.assertIsNotNone(p.grad)
                            self.assertGreater(float(p.grad.norm()),0.)
                    with torch.no_grad():again=model(graph.x,graph.edge_index)
                    torch.testing.assert_close(out,again,rtol=0,atol=0)

    def test_fair_configs_and_three_seed_plan(self):
        dot=json.loads((ROOT/'configs/baseline_texas.json').read_text())
        mlp=json.loads((ROOT/'configs/mlp_texas.json').read_text())
        self.assertEqual(dot['training'],mlp['training'])
        for key in ('datasets','ks','splits','seeds'):self.assertEqual(dot[key],mlp[key])
        future=json.loads((ROOT/'configs/future_three_seeds.json').read_text())
        planned=list(jobs(future))
        self.assertEqual(len(planned),1440)
        self.assertEqual(len(set(future['seeds'])),3)
        altered=copy.deepcopy(dot);altered['training']['hidden_dim']=64
        with self.assertRaises(AssertionError):validate_config(altered)

    def test_test_labels_do_not_select_checkpoint(self):
        config=json.loads((ROOT/'configs/baseline_texas.json').read_text())['training']
        config={**config,'epochs':4}
        for method in ('dot','mlp'):
            graph=self.graph();changed=graph.clone()
            changed.y[changed.test_mask]=(changed.y[changed.test_mask]+1)%3
            first,_=build_model(5,3,2,method,42,'cpu');second=copy.deepcopy(first)
            seed_all(97);one=train_model(first,graph,config)
            seed_all(97);two=train_model(second,changed,config)
            self.assertEqual(tensor_hash(first.state_dict()),tensor_hash(second.state_dict()))
            self.assertEqual(one['best_validation_epoch'],two['best_validation_epoch'])

    def test_imported_frozen_sources_are_byte_identical(self):
        mapping=json.loads((ROOT/'experiments/source_mapping.json').read_text())
        for row in mapping['files']:
            self.assertEqual(sha256(ROOT/row['destination']),row['sha256'])

    def test_failure_provenance_does_not_overwrite(self):
        path=ROOT/'scripts/run_experiment.py'
        spec=importlib.util.spec_from_file_location('course_runner',path)
        runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
        config=json.loads((ROOT/'configs/baseline_texas.json').read_text())
        before=set((ROOT/'outputs').glob('*/metadata.json'))
        # Force a missing-data path, even on a future machine with prepared data.
        with patch.object(runner,'RESEARCH',ROOT/'outputs/intentionally_missing_synthetic_fixture'):
            code=runner.execute(next(jobs(config)),config,'synthetic-test-config-sha','cpu')
        self.assertEqual(code,1)
        created=set((ROOT/'outputs').glob('*/metadata.json'))-before
        self.assertEqual(len(created),1)
        path=created.pop();record=json.loads(path.read_text())
        for key in ('run_id','git','config','started_utc','finished_utc','wall_seconds','device',
                    'source_sha256','status','failure_reason','exit_code','output_path'):
            self.assertIn(key,record)
        self.assertEqual(record['status'],'failed')
        self.assertTrue((path.parent/'terminal.log').is_file())
        # This intentionally failed fixture is retained under ignored outputs/.

    def test_successful_synthetic_run_provenance_and_saved_evaluation(self):
        path=ROOT/'scripts/run_experiment.py'
        spec=importlib.util.spec_from_file_location('course_success_runner',path)
        runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
        fixture=ROOT/'outputs'/('synthetic-data-fixture-'+uuid.uuid4().hex[:12])
        (fixture/'data').mkdir(parents=True,exist_ok=False)
        (fixture/'data/manifest.json').write_text('{"synthetic_test_fixture":true}')
        graph=self.graph()
        torch.save({'x':graph.x,'edge_index':graph.edge_index},fixture/'synthetic_graph.pt')
        masks=[graph[k].numpy() for k in ('train_mask','val_mask','test_mask')]
        np.savez(fixture/'synthetic_split.npz',train_mask=masks[0],val_mask=masks[1],test_mask=masks[2])
        class ToyDataset:
            num_node_features=5
            num_classes=3
            processed_paths=[str(fixture/'synthetic_graph.pt')]
            def __getitem__(self,index):return graph.clone()
        config=json.loads((ROOT/'configs/baseline_texas.json').read_text())
        config['synthetic_test_fixture']=True
        config['training']['epochs']=4
        for device in ('cpu','cuda') if torch.cuda.is_available() else ('cpu',):
            before=set((ROOT/'outputs').glob('*/metadata.json'))
            with patch.object(runner,'RESEARCH',fixture), \
                 patch('src.data.load_dataset',return_value=ToyDataset()), \
                 patch('src.data.load_masks',return_value=masks), \
                 patch('src.data.split_path',return_value=fixture/'synthetic_split.npz'):
                code=runner.execute(next(jobs(config)),config,'synthetic-fixture-config-sha',device)
            self.assertEqual(code,0)
            created=set((ROOT/'outputs').glob('*/metadata.json'))-before
            self.assertEqual(len(created),1)
            metadata_path=created.pop();metadata=json.loads(metadata_path.read_text())
            self.assertEqual(metadata['status'],'complete')
            self.assertEqual(metadata['cuda_workspace_reset'],device=='cuda')
            self.assertIn('model.pt',metadata['artifacts'])
            self.assertIn('metrics.json',metadata['artifacts'])
            result=json.loads((metadata_path.parent/'metrics.json').read_text())
            self.assertEqual(result['report']['test_accuracy'],result['independently_checked']['accuracy'])
            self.assertEqual(result['report']['git']['commit'],metadata['git']['commit'])
            self.assertEqual(result['report']['seed'],42)
            self.assertTrue(metadata['config']['synthetic_test_fixture'])


class EvidenceTests(unittest.TestCase):
    def test_verified_download_rejects_truncation_and_reuses_correct_cache(self):
        path=ROOT/'scripts/prepare_data.py'
        spec=importlib.util.spec_from_file_location('course_data_adapter',path)
        adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
        fixture=ROOT/'outputs'/('download-fixture-'+uuid.uuid4().hex[:12])
        payload=b'synthetic graph input; not benchmark data'
        rel='data/cache/Texas/texas/raw/out1_graph_edges.txt'
        expected={'raw_files':{rel:hashlib.sha256(payload).hexdigest()}}
        with patch.object(adapter,'RESEARCH',fixture), \
             patch.object(adapter.urllib.request,'urlopen',side_effect=[io.BytesIO(b''),io.BytesIO(payload)]) as spy:
            adapter.verify_raw_cache('Texas',expected,False)
            self.assertEqual(spy.call_count,2)
            self.assertEqual((fixture/rel).read_bytes(),payload)
            adapter.verify_raw_cache('Texas',expected,True)
            self.assertEqual(spy.call_count,2)

    def test_registry_has_unique_ids_and_no_retrospective_commits(self):
        with (ROOT/'experiments/registry.csv').open(encoding='utf8',newline='') as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),1566)
        self.assertEqual(len({r['experiment_id'] for r in rows}),1566)
        self.assertTrue(all(r['code_commit']=='UNKNOWN' for r in rows))
        self.assertTrue(all(r['source_type']=='pre-git experiment' for r in rows))
        self.assertTrue(all(r['teacher_approval']=='NOT_VERIFIED' for r in rows))


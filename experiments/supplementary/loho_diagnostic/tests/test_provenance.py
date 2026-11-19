import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from experiments.loho_diagnostic.src.common import unique_run,save,sha
from experiments.loho_diagnostic.src.inputs import masks_for
from experiments.loho_diagnostic.src.summarize import collect,aggregate
from experiments.loho_diagnostic.src.evaluate import run_one

class Provenance(unittest.TestCase):
    def test_unique_missing_and_failed_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            a=unique_run(tmp,'run');b=unique_run(tmp,'run');self.assertNotEqual(a,b)
            save(a/'batch.json',dict(evaluation_set='val',expected_jobs=[dict(dataset='Texas',split_id=0,seed=2026)]))
            cells,missing,failures=collect([tmp]);self.assertEqual(len(missing),1)
            with patch('experiments.loho_diagnostic.src.evaluate.graph_for',side_effect=ValueError('deliberate fixture')):
                m=run_one(dict(dataset='Texas',split_id=0,seed=2026),dict(device='cpu'),'val',b)
            self.assertEqual(m['status'],'failed')
            folder=b/m['run_id'];self.assertTrue((folder/'exception.log').exists());self.assertTrue((folder/'metadata.json').exists())
            cells,missing,failures=collect([tmp]);self.assertEqual(len(failures),1)
    def test_integrity_rejects_wrong_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'test_mlp/data/splits/texas_split_0.6_0.2_0.npz';path.parent.mkdir(parents=True)
            np.savez(path,train_mask=np.array([1,1,1,0,0],bool),val_mask=np.array([0,0,0,1,0],bool),test_mask=np.array([0,0,0,0,1],bool))
            with patch('experiments.loho_diagnostic.src.inputs.source_root',return_value=Path(tmp)):
                with self.assertRaisesRegex(ValueError,'ordering'): masks_for('Texas',0,5)
    def test_seed_then_split_aggregation(self):
        rows=[dict(dataset='d',split_id=s,seed=z,m=v) for s,z,v in [(0,1,1),(0,2,3),(1,1,9),(1,2,7)]]
        splits=aggregate(rows,['dataset','split_id'],['m']);self.assertEqual([r['m_mean'] for r in splits],[2,8])
        ds=aggregate(splits,['dataset'],['m_mean'])[0]
        self.assertEqual(ds['m_mean_mean'],5);self.assertAlmostEqual(ds['m_mean_sample_sd'],18**.5)
if __name__=='__main__': unittest.main()

"""Run the frozen Baseline/MLP code with new, non-overwriting Git provenance."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from course.common import ROOT, RESEARCH, save, sha256, git_state, utc_now, jobs
import argparse
import contextlib
import importlib.metadata
import json
import time
import traceback
import uuid
import warnings


def execute(job, config, config_sha, device):
    state = git_state()
    if state['dirty'] or state['commit'] == 'UNKNOWN':
        warnings.warn('Uncommitted code: this run will record dirty status and source checksums.')
    run_id = utc_now().replace(':', '').replace('+', '_') + '-' + uuid.uuid4().hex[:12]
    output = ROOT / 'outputs' / run_id
    output.mkdir(parents=True, exist_ok=False)
    versions = {}
    for name in ('torch', 'torch-geometric', 'numpy', 'scipy'):
        try: versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: versions[name] = 'NOT_INSTALLED'
    metadata = dict(run_id=run_id, status='running', started_utc=utc_now(), git=state,
                    config=config, config_sha256=config_sha, job=job, device=str(device),
                    output_path=str(output.relative_to(ROOT)), monetary_cost='UNKNOWN',
                    teacher_approval=config.get('teacher_approval', 'NOT_VERIFIED'),
                    source_sha256={str(p.relative_to(ROOT)): sha256(p)
                        for folder in (ROOT/'course', ROOT/'scripts', RESEARCH/'src', RESEARCH/'ablation_mlp')
                        for p in folder.glob('*.py')},
                    environment=versions)
    save(output / 'config.json', config)
    save(output / 'metadata.json', metadata)
    start = time.perf_counter()
    exit_code = 0
    with (output / 'terminal.log').open('w', encoding='utf-8') as log:
        with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
            try:
                import numpy as np
                import torch
                from src.data import load_dataset, load_masks, split_path
                from src.factory import build_model, configure_determinism
                from src.train import run_one
                from ablation_mlp.factory import build_model as component_model
                from course.metrics import accuracy
                if device == 'auto': device = 'cuda' if torch.cuda.is_available() else 'cpu'
                metadata['device'] = str(device)
                configure_determinism()
                manifest_path = RESEARCH / 'data/manifest.json'
                if not manifest_path.exists():
                    raise RuntimeError('Data not prepared. Run python scripts/prepare_data.py first.')
                dataset = load_dataset(job['dataset'])
                graph = dataset[0].to(device)
                for label, mask in zip(('train_mask', 'val_mask', 'test_mask'),
                                       load_masks(job['dataset'], job['split_id'], graph.num_nodes)):
                    graph[label] = torch.from_numpy(mask).to(device)
                builder = build_model if job['method'] in ('dot', 'mlp') else component_model
                model, initial = builder(dataset.num_node_features, dataset.num_classes, job['k'],
                                         job['method'], job['seed'], device)
                assert model.convs[0].powers == list(range(job['k'] + 1))
                assert len(model.convs) == 1 and model.convs[0].num_iterations == 2
                metadata.update(data_manifest_sha256=sha256(manifest_path),
                    processed_data_sha256=sha256(dataset.processed_paths[0]),
                    split_sha256=sha256(split_path(job['dataset'], job['split_id'])),
                    split_seed=102 + job['split_id'],
                    actual_device_name=torch.cuda.get_device_name() if str(device).startswith('cuda') else 'CPU')
                meta = dict(dataset=job['dataset'], routing_method=job['method'], k=job['k'],
                    powers=list(range(job['k']+1)), actual_gamma_layers=1, r=2,
                    seed=job['seed'], split_id=job['split_id'], run_id=run_id,
                    git=state, config_sha256=config_sha, data_manifest_sha256=metadata['data_manifest_sha256'],
                    processed_data_sha256=metadata['processed_data_sha256'],
                    split_sha256=metadata['split_sha256'], **initial)
                report = run_one(model, graph, config['training'], meta, output)
                with np.load(output / 'predictions.npz', allow_pickle=False) as p:
                    checked = accuracy(p['predictions'], p['labels'], p['test_mask'],
                                       np.arange(len(p['labels'])), np.arange(len(p['labels'])))
                assert checked['accuracy'] == report['test_accuracy']
                save(output / 'metrics.json', dict(report=report, independently_checked=checked))
                metadata['status'] = 'complete'
                metadata['metrics'] = checked
            except Exception as error:
                exit_code = 1
                metadata.update(status='failed', failure_type=type(error).__name__, failure_reason=str(error),
                                traceback=traceback.format_exc())
                print(traceback.format_exc())
    metadata.update(finished_utc=utc_now(), wall_seconds=time.perf_counter()-start, exit_code=exit_code)
    metadata['artifacts'] = {p.name: sha256(p) for p in output.iterdir() if p.name != 'metadata.json'}
    save(output / 'metadata.json', metadata)
    print(json.dumps(dict(run_id=run_id, status=metadata['status'], output=metadata['output_path'])))
    return exit_code


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--device', default='auto')
    parser.add_argument('--plan', action='store_true', help='Enumerate jobs without downloading or training.')
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding='utf-8'))
    planned = list(jobs(config))
    if args.plan:
        print(json.dumps(dict(jobs=len(planned), first=planned[0], last=planned[-1],
            approval=config.get('teacher_approval', 'NOT_VERIFIED'), training_started=False), indent=2))
        return 0
    codes = [execute(job, config, sha256(args.config), args.device) for job in planned]
    return int(any(codes))


if __name__ == '__main__': sys.exit(main())

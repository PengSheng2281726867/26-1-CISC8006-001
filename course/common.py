from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / 'research'
sys.dont_write_bytecode = True
if str(RESEARCH) not in sys.path:
    sys.path.insert(0, str(RESEARCH))


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''): h.update(block)
    return h.hexdigest()


def save(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + '\n',
                    encoding='utf-8', newline='\n')


def git_state():
    def get(args):
        return subprocess.check_output(['git', '--no-optional-locks', *args],
                                       cwd=ROOT, stderr=subprocess.DEVNULL).decode().strip()
    try:
        commit = get(['rev-parse', 'HEAD'])
        status = get(['status', '--porcelain=v1', '--untracked-files=normal'])
        return dict(commit=commit, dirty=bool(status), status=status.splitlines(),
                    interpretation='current run only; not a recovered execution commit')
    except subprocess.CalledProcessError:
        return dict(commit='UNKNOWN', dirty=True, status=['NO_COMMIT_AVAILABLE'])


def validate_config(config):
    assert config['datasets'] and config['ks'] and config['methods'] and config['splits'] and config['seeds']
    assert set(config['datasets']) <= {'Texas', 'Wisconsin', 'Cornell', 'Chameleon', 'Squirrel', 'Actor'}
    assert set(config['ks']) <= {1, 2, 3, 4}
    assert set(config['methods']) <= {'dot', 'mlp', 'mlp_ln', 'mlp_gelu'}
    assert all(isinstance(s, int) and 0 <= s < 10 for s in config['splits'])
    assert all(isinstance(s, int) and s >= 0 for s in config['seeds'])
    for key in ('datasets', 'ks', 'methods', 'splits', 'seeds'):
        assert len(config[key]) == len(set(config[key])), f'duplicate {key}'
    fixed = dict(hidden_dim=32, mlp_hidden_dim=32, actual_gamma_layers=1,
                 routing_iterations=2, include_zero_hop=True, input_dropout=.2, hidden_dropout=.8)
    for key, expected in fixed.items():
        assert config['training'][key] == expected, f'{key} disagrees with frozen model behavior'
    assert config['training']['epochs'] >= 1
    assert config['training']['early_stopping_patience'] >= 1
    return config


def jobs(config):
    validate_config(config)
    for dataset in config['datasets']:
        for k in config['ks']:
            for split in config['splits']:
                for seed in config['seeds']:
                    methods = config['methods'] if (split + seed) % 2 == 0 else list(reversed(config['methods']))
                    for method in methods:
                        yield dict(dataset=dataset, k=k, split_id=split, seed=seed, method=method)


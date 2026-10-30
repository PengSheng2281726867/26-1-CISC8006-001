"""Local evidence helpers; no private inputs are written into the public tree."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess
import sys

STUDY = Path(__file__).resolve().parents[1]
REPO = STUDY.parents[1]
sys.path.insert(0, str(REPO))
sys.dont_write_bytecode = True
os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(4*1024*1024), b''):
            h.update(b)
    return h.hexdigest()


def save(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n', encoding='utf8')
    tmp.replace(path)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def git_state():
    def get(args):
        return subprocess.check_output(['git','-c','safe.directory='+REPO.as_posix(),
                                        '--no-optional-locks',*args],cwd=REPO,
                                       stderr=subprocess.DEVNULL).decode().strip()
    try:
        status = get(['status','--porcelain=v1','--untracked-files=normal'])
        return dict(commit=get(['rev-parse','HEAD']), branch=get(['branch','--show-current']),
                    dirty=bool(status), status=status.splitlines())
    except subprocess.CalledProcessError:
        return dict(commit='UNKNOWN', branch='UNKNOWN', dirty=True, status=['GIT_QUERY_FAILED'])


def sources():
    paths = list((STUDY/'src').glob('*.py')) + [STUDY/'scripts'/n for n in ('run.py','prepare.py','eval_only.py')]
    paths += list((REPO/'research/src').glob('*.py'))
    return {p.relative_to(REPO).as_posix():sha(p) for p in sorted(paths)}


def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def external(path):
    path = Path(path).resolve()
    if path.is_relative_to(REPO):
        raise ValueError('Use an external data/run directory outside the Git checkout')
    return path

"""External private artifacts and reproducible public scalar evidence."""
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
sys.path.insert(0, str(REPO/'research'))
sys.dont_write_bytecode = True
os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
if (REPO.parent/'private_git'/'HEAD').exists():
    os.environ['GIT_DIR'] = str(REPO.parent/'private_git')
    os.environ['GIT_WORK_TREE'] = str(REPO)
os.environ['GIT_CONFIG_COUNT'] = '1'
os.environ['GIT_CONFIG_KEY_0'] = 'safe.directory'
os.environ['GIT_CONFIG_VALUE_0'] = REPO.as_posix()
def now(): return datetime.now(timezone.utc).isoformat()
def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(8*1024*1024), b''): h.update(block)
    return h.hexdigest()
def digest(obj): return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def save(path,obj):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n',encoding='utf8')
    temp.replace(path)
def external(path):
    path=Path(path).resolve()
    if path.is_relative_to(REPO): raise ValueError('Private directory must be outside checkout')
    return path
def git_state():
    def get(args): return subprocess.check_output(['git',*args],cwd=REPO,stderr=subprocess.DEVNULL).decode().strip()
    try: return dict(commit=get(['rev-parse','HEAD']),branch=get(['branch','--show-current']),dirty=bool(get(['status','--porcelain'])))
    except subprocess.CalledProcessError: return dict(commit='UNKNOWN',dirty=True)
def sources():
    paths=[STUDY/'src'/n for n in ('common.py','distance.py','model.py','run.py')]+list((REPO/'research/src').glob('*.py'))
    paths += [REPO/'experiments/hop_scope_study/src'/n for n in ('data.py','common.py')]
    return {p.relative_to(REPO).as_posix():sha(p) for p in sorted(paths)}
def verify_freeze():
    freeze=read(STUDY/'results/protocol_freeze.json')
    for rel,expected in freeze['files'].items():
        if sha(STUDY/rel)!=expected: raise ValueError('Frozen protocol/config changed: '+rel)
    return sha(STUDY/'PROTOCOL.md')

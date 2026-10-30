"""Provenance and private output helpers."""
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
from datetime import datetime, timezone
import uuid
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / 'experiments/loho_diagnostic'
def now(): return datetime.now(timezone.utc).isoformat()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def save(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n', encoding='utf-8')
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()
def git_state():
    def run(*args): return subprocess.check_output(['git',*args],cwd=ROOT).decode().strip()
    return dict(commit=run('rev-parse','HEAD'),dirty=bool(run('status','--porcelain')))
def unique_run(root,prefix):
    folder=Path(root)/(prefix+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex)
    folder.mkdir(parents=True,exist_ok=False)
    return folder
def csv_write(path,rows):
    rows=list(rows); Path(path).parent.mkdir(parents=True,exist_ok=True)
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with Path(path).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
        w.writerows({k:('NA' if v is None else v) for k,v in r.items()} for r in rows)
def private_root(): return Path(os.environ.get('LOHO_PRIVATE_ROOT',ROOT.parent/'private_outputs'))

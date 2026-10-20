"""All process-local caches and outputs stay inside test_mlp."""
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
for name, suffix in {'TEMP':'cache/tmp','TMP':'cache/tmp','TMPDIR':'cache/tmp',
                     'MPLCONFIGDIR':'cache/matplotlib','TORCH_HOME':'cache/torch',
                     'CUDA_CACHE_PATH':'cache/cuda','XDG_CACHE_HOME':'cache/xdg'}.items():
    target=ROOT/suffix
    target.mkdir(parents=True,exist_ok=True)
    os.environ[name]=str(target)
tempfile.tempdir=str(ROOT/'cache/tmp')
os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'

def sha256(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(8*1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def save_json(path,value):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    temporary.replace(path)

def tensor_hash(state):
    h=hashlib.sha256()
    for key,value in sorted(state.items()):
        array=value.detach().cpu().contiguous().numpy()
        h.update(key.encode());h.update(str(array.shape).encode());h.update(str(array.dtype).encode());h.update(array.tobytes())
    return h.hexdigest()

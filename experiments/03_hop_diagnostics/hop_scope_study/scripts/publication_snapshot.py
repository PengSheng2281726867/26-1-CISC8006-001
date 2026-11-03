"""Exact-index publication audit with separate writable snapshot metadata.

Useful with read-only clone metadata. All writes stay in --run-root; the original
.git is read only. This script never pushes, changes refs, or edits scientific code.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.common import STUDY,REPO,external,save,now,sha
import argparse
import os
import subprocess
import uuid
p=argparse.ArgumentParser();p.add_argument('--run-root',type=Path,required=True)
p.add_argument('--commit',action='store_true');a=p.parse_args()
out=external(a.run_root)/'publication'/('snapshot-'+uuid.uuid4().hex[:12]);out.mkdir(parents=True,exist_ok=False)
objects=out/'objects';objects.mkdir()
env=os.environ.copy();env.update(GIT_DIR=str(REPO/'.git'),GIT_WORK_TREE=str(REPO),
    GIT_INDEX_FILE=str(out/'candidate.index'),GIT_OBJECT_DIRECTORY=str(objects),
    GIT_ALTERNATE_OBJECT_DIRECTORIES=str(REPO/'.git/objects'),GIT_CONFIG_COUNT='1',
    GIT_CONFIG_KEY_0='safe.directory',GIT_CONFIG_VALUE_0=str(REPO))

def git(args,**kwargs):
    r=subprocess.run(['git',*args],cwd=REPO,env=env,capture_output=True,check=True,**kwargs)
    return r.stdout

paths=['README.md','AI_USAGE.md','docs/IMPROVEMENTS.md']
paths += [p.relative_to(REPO).as_posix() for p in sorted(STUDY.rglob('*')) if p.is_file()]
if any('/__pycache__/' in p for p in paths):raise RuntimeError('Unexpected bytecode file')
git(['read-tree','HEAD'])
# Explicit allowlist; preserve actual source bytes rather than applying host EOL conversion.
git(['-c','core.autocrlf=false','add','--',*paths])
changed=git(['diff','--cached','--name-only']).decode().splitlines()
if any(p not in paths for p in changed):raise RuntimeError('Unexpected staged path')
stat=git(['diff','--cached','--stat']).decode();print(stat)
(out/'staged.diff').write_bytes(git(['diff','--cached','--binary']))
check=subprocess.run([sys.executable,'-B',str(REPO/'scripts/check_publication.py')],cwd=REPO,env=env,
                     capture_output=True,text=True,encoding='utf8',errors='replace')
(out/'publication_check.txt').write_text(check.stdout+check.stderr,encoding='utf8');print(check.stdout)
if check.returncode:raise RuntimeError('Exact-index publication check failed; evidence retained')
# Index blob bytes must exactly reproduce every new scientific source/config file.
for rel in paths:
    blob=git(['show',':'+rel])
    if blob!=(REPO/rel).read_bytes():raise RuntimeError('Index EOL/content differs: '+rel)
tree=git(['write-tree']).decode().strip();parent=git(['rev-parse','HEAD']).decode().strip()
receipt=dict(utc=now(),status='passed',tree_sha=tree,parent_sha=parent,changed_files=changed,
             exact_index_check_sha256=sha(out/'publication_check.txt'),
             protected_clone_metadata_modified=False,index_source_bytes_identical=True)
if a.commit:
    # Explicit AI authorship, without attributing agent work to an unverified human.
    env.update(GIT_AUTHOR_NAME='Codex',GIT_AUTHOR_EMAIL='codex@openai.com',
               GIT_COMMITTER_NAME='Codex',GIT_COMMITTER_EMAIL='codex@openai.com')
    message='Add fixed-K5 variable-hop routing diagnostic study and measured results\n'
    receipt['local_commit_sha']=git(['commit-tree',tree,'-p',parent],input=message.encode()).decode().strip()
save(out/'receipt.json',receipt)
print('Snapshot evidence:',out.name)
print('Tree:',tree)
if 'local_commit_sha' in receipt:print('Local commit:',receipt['local_commit_sha'])

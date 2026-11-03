"""Verify private before inventories; publish only counts and checksums."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.common import STUDY,REPO,read,save,sha,now
import argparse
import subprocess
p=argparse.ArgumentParser();p.add_argument('--target-before',type=Path,required=True)
p.add_argument('--original-before',type=Path,required=True);p.add_argument('--original-root',type=Path,required=True)
a=p.parse_args();original=a.original_root.resolve();target_before=read(a.target_before);original_before=read(a.original_before)
original_after={str(p.relative_to(original)):sha(p) for p in original.rglob('*')
                if p.is_file() and '.git' not in p.parts and p.suffix in ('.py','.md','.csv','.json')
                and not any(s in ('cache','data') for s in p.relative_to(original).parts)}
original_changes=[name for name in set(original_before)|set(original_after) if original_before.get(name)!=original_after.get(name)]
allowed={'README.md','AI_USAGE.md','docs/IMPROVEMENTS.md'};protected_changes=[];appended=[]
for name,before in target_before.items():
    path=REPO/name
    if not path.is_file():protected_changes.append(name);continue
    if sha(path)==before:continue
    if name not in allowed:protected_changes.append(name);continue
    old=subprocess.check_output(['git','-c','safe.directory='+REPO.as_posix(),'show','HEAD:'+name],cwd=REPO)
    if not path.read_bytes().startswith(old):protected_changes.append(name)
    else:appended.append(name)
report=dict(utc=now(),status='passed' if not original_changes and not protected_changes else 'failed',
            original_source_doc_result_files_checked=len(original_before),original_changed_count=len(original_changes),
            target_existing_files_checked=len(target_before),target_protected_changed_count=len(protected_changes),
            allowed_append_only_updates=sorted(appended),
            target_before_manifest_sha256=sha(a.target_before),original_before_manifest_sha256=sha(a.original_before),
            scope='Original .py/.md/.csv/.json excluding caches/data/Git, plus every originally tracked target file; full private inventory remains local')
save(STUDY/'results/preservation.json',report)
print(report)
if original_changes or protected_changes:raise RuntimeError('Protected changes detected; inspect private inventories before publishing')

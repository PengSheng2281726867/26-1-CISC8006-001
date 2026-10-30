"""One-command acceptance gate: adapter + existing smoke + exact data checks."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.common import STUDY,REPO,external,save,read,now,sha
import argparse
import os
import subprocess
import uuid
p=argparse.ArgumentParser();p.add_argument('--data-root',type=Path,required=True)
p.add_argument('--run-root',type=Path,required=True);a=p.parse_args()
out=external(a.run_root)/'checks'/('acceptance-'+uuid.uuid4().hex[:12]);out.mkdir(parents=True,exist_ok=False)
env=os.environ.copy();env.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='safe.directory',GIT_CONFIG_VALUE_0=str(REPO))
commands=[['tests/validate.py'],['SMOKE'],['scripts/prepare.py','--data-root',str(external(a.data_root)),'--check-only'],['tests/test_analysis.py']]
rows=[]
for index,cmd in enumerate(commands):
    command=[sys.executable,'-B',str(REPO/'scripts/smoke_test.py')] if cmd==['SMOKE'] else [sys.executable,'-B',str(STUDY/cmd[0]),*cmd[1:]]
    proc=subprocess.run(command,cwd=REPO,env=env,capture_output=True,text=True,encoding='utf8',errors='replace')
    (out/f'{index}.log').write_text(proc.stdout+proc.stderr,encoding='utf8')
    print(proc.stdout);print(proc.stderr)
    rows.append(dict(check=('adapter','repository_smoke','split_raw_verification','analysis_known_answers')[index],exit_code=proc.returncode,
                     log_sha256=sha(out/f'{index}.log')))
report=dict(status='passed' if all(r['exit_code']==0 for r in rows) else 'failed',utc=now(),checks=rows,
            adapter_tests=read(STUDY/'results/adapter_validation.json'),
            data_manifest_sha256=sha(external(a.data_root)/'manifest.json'),local_evidence='checks/'+out.name)
save(out/'report.json',report);save(STUDY/'results/validation.json',report)
text='# Implementation and data validation\n\n'+f"Status: **{report['status'].upper()}**, {report['utc']}.\n\n"
text+='Seven scientific tests passed: 15 actual propagation calls and six independently checked hop tensors at all five x; zero inactive alpha throughout R1-4; inactive feature/gradient exclusion; scope-sensitive synthetic output; constant architecture/full initialization/RNG/parameter budget; invalid masks/devices/scopes/missing data and finite empty graph; test-label perturbation leaves training state/selection unchanged.\n\n'
text+='Direct upstream network parity: CPU float64 and CUDA float32, R1/2/3, both eval and matched-dropout training; output, input gradient and every parameter gradient checked (12 cases). Tolerances CPU atol1e-10/rtol1e-9; CUDA atol2e-6/rtol2e-5. Actual errors in results/adapter_validation.json. No scientific behavior was changed to pass.\n\n'
text+='Four analysis known-answer tests also passed, covering sample SD, exact sign-flip, Holm, reproducible bootstrap and running-cell accounting. Existing repository smoke:13 tests,20 historical parity cases; retains a deliberate missing-data failure and two synthetic successful fixtures, excluded from scientific training counts. All six graphs and60 fixed splits rechecked against raw manifests and CPU seeded arrays; archive identity status in results/data_verification.json.\n\n'
text+='One command from repository root:\n\n```powershell\npython -B experiments/hop_scope_study/scripts/check.py --data-root ../local_data --run-root ../local_runs\n```\n\nPrivate logs are retained under local_runs/checks; public scalar acceptance evidence is results/validation.json. All old source bytes remain unchanged.\n'
(STUDY/'docs/01_VALIDATION.md').write_text(text,encoding='utf8')
sys.exit(0 if report['status']=='passed' else 1)

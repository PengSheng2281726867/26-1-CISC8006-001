"""Append only this study's navigation/AI evidence to three authorized root docs."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.common import STUDY,REPO,read,now
status=read(STUDY/'results/status.json');hyp=read(STUDY/'results/hypotheses_summary.json')
if status['primary_complete']!=300 or status['posthoc_evaluations']!=300:
    raise RuntimeError('Do not label integration complete until both matrices finish')
marker=b'Fixed-propagation / variable-hop-gating study (2026-10-25)'

def append(path,text):
    path=REPO/path
    if marker in path.read_bytes():raise RuntimeError('Already integrated; review instead of duplicating')
    with path.open('ab') as f:f.write(('\n\n'+text+'\n').encode('utf8'))

append('README.md','- [Fixed-propagation / variable-hop-gating study (2026-10-25)](experiments/hop_scope_study/README.md):300 retrainings and300 inference-only mask evaluations; technical matrix complete, teacher approval NOT_VERIFIED.')
append('AI_USAGE.md','''## Fixed-propagation / variable-hop-gating study (2026-10-25)

This session's real user request was to read the local AGENTS instructions and
complete audit, tests, Pilot, Full, analysis and publication of the fixed-K5 study.
The user also asked why local Git writes were denied. No complete private chat
export is published. Execution authorization is explicit; teacher approval and
human scientific/code acceptance remain NOT_VERIFIED/PENDING.

| Date | Phase | Actual work | Agent | Interaction / command evidence | Decision / human verification |
| --- | --- | --- | --- | --- | --- |
| 2026-10-25 | Audit, build, test | Read frozen protocols, isolate a Routing mask, verify all-hop propagation and upstream forward/gradients | Codex, this session; exact serving variant UNKNOWN | Current user request; new study docs00/01; scripts/check.py; results/validation.json | Executed; human acceptance PENDING |
| 2026-10-25 | Pilot and Full |12 Pilot cells followed by the remaining288; same full budget and initialization;300 actual checkpoint reload checks | Codex, this session | scripts/run.py with configs/pilot.json and full.json; docs02/03; results/per_run.jsonl and attempts.jsonl | Completed technically; teacher approval NOT_VERIFIED |
| 2026-10-25 | Final evaluation and publication preparation |300 no-update masks; paired statistics/negative results; append-only integration and exact-index audit | Codex, this session | scripts/eval_only.py, aggregate.py, finalize_report.py, publication_snapshot.py; docs03-06 | Technical analyses executed; actual publication outcome is in the Git history/local receipt, not inferred from this row |

Original scientific code, old experiments and attribution remain unchanged.
Local Git metadata writes were denied. A separate candidate index/object store
inside the writable external run directory permits the original whole-index
publication checker to inspect exact blobs without changing protected metadata.
All training records truthfully retain their base commit plus dirty/source hashes;
the later publication commit is not claimed as their execution version.
''')
val=', '.join(f'{d}={x}' for d,x in hyp['h2_validation_best_mean_x'].items())
append('docs/IMPROVEMENTS.md',f'''## I4 - Fixed-propagation / variable-hop-gating study (2026-10-25)

Status: **Full technical diagnostic evaluation**, user-authorized; teacher approval
**NOT_VERIFIED**. This is not an implemented adaptive selector or an improvement
claim. [Protocol and report](../experiments/hop_scope_study/README.md).

Propagation stays powers0..5 (15 actual calls, max chain5); only active routing
scope0..x changes, x1-5. One actual GAMMA layer, hidden32,R2, original Dot/LN/squash,
constant parameter budget and identical full initialization within split/seed.
300 primary trainings including12 verified Pilot cells;300 no-update diagnostics
from60 new full-hop checkpoints. All saved primary checkpoints were reloaded.
No scientific training failed. Engineering failures and the interim running-cell
count correction remain documented separately.

Mean test curves are nonmonotone in all six datasets. None of24 primary contrasts
is below0.05 after within-dataset Holm4 correction. Descriptive validation-mean
best x: {val}. Per-split selection and all test curves/negative cases are reported;
no test-based best-x selection. Validation reuse and overlapping splits limit inference.
Post-hoc and retrain curves are distinct interventions, not interchangeable models.
No overall acceleration is claimed because full propagation remains present.

A future sparse per-node budget with mandatory0-hop, nested validation and multiple
optimization seeds is **PROPOSED ONLY**. No MLP scorer, attention, extra GNN layer
or new loss was added in this study. Historical I1-I3 and frozen baselines remain
unchanged; new K5/x5 is solely this experiment's matched full-hop control.
''')
p=STUDY/'README.md';s=p.read_text(encoding='utf-8-sig')
s=s.replace('This diagnostic ablation always computes', 'Technical execution: **300/300 primary trainings and300/300 mask evaluations complete**, with0 scientific training failures. All primary checkpoint reload checks passed.\n\nThis diagnostic ablation always computes')
p.write_text(s,encoding='utf8')
print('Appended only README, AI_USAGE, IMPROVEMENTS; updated new study status')

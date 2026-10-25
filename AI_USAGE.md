# AI usage evidence log

Historical interaction evidence is incomplete. Existing research reports and code
show outputs, not a complete prompt transcript or teacher-approved use history.
No prior agent/tool timestamps or acceptance decisions are invented. The current
conversation supplied the repository-recovery instruction; no full chat export is
available as a public artifact. Local assistant summaries are not a verified log
of every earlier interaction.

| Date | Project phase | Task | Coding agent | Prompt / interaction reference | Agent proposal | Human verification | Decision | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-10-20 | Repository recovery and audit | Inspect sources/license, recover records, prepare safe Git snapshot | Codex, this session; precise model version UNKNOWN | Current user message titled CISC8006 Course Project — Repository Initialization & Research Evidence Recovery; verbatim export NOT_AVAILABLE | Separate course directory, immutable source copies, honest pre-git registry, synthetic checks and prospective provenance | PENDING; user has authorized execution, which is not scientific validation | Implementation executed; human acceptance NOT_VERIFIED | experiments/recovery_manifest.json; docs/CODE_AUDIT.md; Git commits from current date |
| 2026-10-20 | Testing and provenance | Add metric sanity, matched configs, unique outputs, commit/dirty/data/seed metadata | Codex, this session | Same current task, Phases C–F | Preserve model bytes and test adapters independently; no long training | PENDING | Tests and documentation pending final human review | reports/SYSTEM_TESTS.md; course/; tests/ |

Before this date: author-code history exists, but the local research executions are
pre-git; complete agent prompts, dates, model versions and per-interaction human
decisions are UNKNOWN. Do not fill those gaps from plausibility.

For future work append real entries containing Date, Project Phase, Task, Coding
Agent/model if known, a real prompt/reference (redact secrets), Agent Proposal,
Human Verification, Accepted/Modified/Rejected and Evidence Link. Keep the actual
prompt artifact when authorized; do not upload private conversation content by default.

Course requirement for agent use across three phases: **Partial / NOT_VERIFIED**.
This recovery session documents audit and engineering work; it does not establish
the missing historical reproduction, improvement-design and final-evaluation
interactions. Human verification of this log and phase coverage is still required.
Commits use the authorized repository account; this does not imply that the human
person manually wrote agent-generated code or reviewed every scientific decision.


## Fixed-propagation / variable-hop-gating study (2026-10-25)

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


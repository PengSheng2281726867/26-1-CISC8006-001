# CISC8006 course compliance audit

Assessed 2026-10-20 against requirements supplied in the current user request.
The official syllabus/rubric and teacher approval records were not supplied;
their independent confirmation is NOT_VERIFIED. No compliance status implies
teacher acceptance. Human decisions and proposed future runs remain pending.

| Requirement | Status | Evidence or gap |
| --- | --- | --- |
| One Clear Claim | Complete | One operational component claim; teacher approval NOT_VERIFIED |
| Reproduction Level | Complete | Component, explicitly not Exact/Table1 replication |
| Frozen Protocol | Partial | Historical code/config hashes; no approved course freeze |
| Dataset and Split | Complete | Raw hashes, shapes, seed-generated persisted masks; no data redistribution |
| Evaluation Sanity Check | Complete | Known answers, IDs, units, direction and aggregation |
| Three Seeds | Partial | 10 seeds across10 splits;1 per fixed split. Proposed3-seed follow-up not run |
| Paper Comparison | Complete | Primary Table3 numbers juxtaposed with different local protocol |
| Difference Analysis | Complete | Layer count, splits, normalization, hops, training/selection, edge counts, hardware |
| Three Improvement Ideas | Complete | MLP executed; scale control and hop dropout Proposed, not piloted |
| Two Approved Pilots | Partial | MLP/LN/GELU pilots executed; teacher approval NOT_VERIFIED |
| One Full Evaluation | Partial | Full technical MLP/LN/GELU matrices; course approval and3-seed requirement unresolved |
| Fair Controls and Ablations | Partial | Matched common initialization/configs, LN/GELU ablations; capacity/seed confounds remain |
| Failed / Negative Runs | Partial | Negative results and superseded pilots retained; some raw historical failure logs missing |
| Git Commit Traceability | Partial | Prospective runner captures commit/dirty status; all historical execution commits UNKNOWN |
| Experiment Registry | Complete | 1,566 unique rows with evidence grades and unknown fields |
| Locked Environment | Partial | Installed versions recovered; fresh clean rebuild and dependency hash lock NOT_VERIFIED |
| One-command Smoke Test | Complete | python -B scripts/smoke_test.py; actual report linked |
| AI_USAGE.md | Partial | Current session logged; historical3-phase transcripts and human verification missing |
| CONTRIBUTIONS.md | Not Verified | No human contributions inferred from paths or account identity |
| README.md | Complete | Install/data/run/evaluate/smoke/limits documented, installation validation limits explicit |
| Report and Slides | Partial | Technical Markdown report and figures present; course-final report review/slides missing |
| Week12 Freeze | Missing | Date/approval UNKNOWN; no final tag created |


## Minimum remaining human/research actions

1. Confirm the exact claim/reproduction level, get teacher approval for claim,
   protocol and at least two piloted improvements; attach actual approval evidence.
2. Run at least3 optimization seeds per fixed split under a newly frozen clean
   commit, or get explicit approval for the historical uncertainty alternative.
   No extra seeds were generated during this recovery.
3. Verify AI-use logs and names/contributions, restore real prior interaction
   references if available, and document remaining course phases prospectively.
4. Verify fresh installation/data preparation in a clean environment; arrange an
   authorized durable archive for external artifacts and record its accessibility.
5. Prepare/review the actual course report and slides; confirm Week12 schedule,
   freeze experiments and commit only at the authorized final milestone.

[Code audit](CODE_AUDIT.md), [claim](CLAIM_AND_REPRODUCTION.md),
[improvements](IMPROVEMENTS.md), [recovery](EXPERIMENT_RECOVERY.md),
[actual smoke evidence](../reports/SYSTEM_TESTS.md), [AI usage](../AI_USAGE.md),
[contributions](../CONTRIBUTIONS.md).

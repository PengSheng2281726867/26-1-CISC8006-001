# Experiment organization and integration record

## Integration on 2026-11-03

The user requested merging published experiment work and organizing files by
experiment. GitHub and remote refs were checked during execution:

| Study | PR | State before this task | Integration |
| --- | --- | --- | --- |
| Fixed K5 / variable gating scope | [#1](https://github.com/PengSheng2281726867/26-1-CISC8006-001/pull/1) | Already merged | Included in base `5e7eb902d32bda4665b5235582dc59eebf556178` |
| Frozen-weight LOHO | [#2](https://github.com/PengSheng2281726867/26-1-CISC8006-001/pull/2) | Already merged | Included in the same base |
| Exact-distance / query gating | [#3](https://github.com/PengSheng2281726867/26-1-CISC8006-001/pull/3) | Open, mergeable | Merged in this task as `673a4759d51b2eb56d712635c51b9d1f196cb4df` |

PR3 was merged with expected head
`ef9afe037053df34da6aa19e04e0e4638e5d68fb`, preserving its four commits.
A fresh fetch confirmed main before the organization branch was created.
No force push, history rewrite or course freeze tag was used. The organization
commit and its merge outcome are identified by Git history.

## Organization

The [experiment index](../experiments/README.md) provides eight entry directories:

```text
experiments/
  README.md                  experiment index and shared-file guide
  catalog.json               repository-relative experiment-to-file mapping
  historical_readme/         original README reproduction: 100 records
  early_gate/                early K2 Dot/Uniform: 120 records
  gate_sweep/                K2-4 Dot/Uniform: 360 records
  dot_mlp/                   480 main + 24 superseded Pilot + 2 anchors
  mlp_components/            480 LN/GELU records; controls stay shared
  hop_scope_study/           300 trainings and 300 no-update masks
  loho_diagnostic/           180 frozen checkpoints, validation and test
  exact_distance_query/     720 primary trainings, 9 controls, inference profiles
```

Each entry has a file map for its actual code, configurations, protocols,
reports, results, figures and tests. The five historical entry directories map
the original files under `analysis/`, `protocols/`, root `configs/`, `research/`
and `reports/`. These canonical paths preserve script references, provenance
hashes and immutable historical records. No scientific source or result files
are duplicated. The three newer studies keep their existing layouts and receive
the same navigation convention.

The 1,566-entry historical registry is partitioned exactly once by the catalog
stage selectors, including 24 superseded Pilot and two anchor records. Newer
study coverage comes from its own evidence. Pilot reuse, shared controls,
training and inference counts remain distinct. Proposed configurations stay
marked as future work, and negative results remain accessible.

Historical publication receipts describe what was observed when written.
An old receipt saying a PR was open remains evidence of that date; the table
above and live GitHub history identify subsequent merges.

## Validation

Scientific checks ran in the existing documented GAMMA environment
(Python3.12.14, torch2.8.0+cu128, PyG2.7.0) on the combined tree before PR3 merged:

| Check | Result |
| --- | --- |
| `python -B scripts/smoke_test.py` | 13 passed, including20 author-alignment subcases |
| `python -B -m unittest discover -s experiments/hop_scope_study/tests -p validate.py -v` | 7 passed; discovery avoids overwriting historical acceptance JSON |
| `python -B experiments/hop_scope_study/tests/test_analysis.py` | 4 passed |
| `python -B -m unittest discover -s experiments/loho_diagnostic/tests -v` | 9 passed |
| `python -B -m unittest discover -s experiments/exact_distance_query/tests -v` | 16 passed |
| Exact-index publication audit before PR3 merge | Passed:410 files,0 findings |
| Comparison with pre-merge main | Frozen source, adapters, historical records and both earlier studies unchanged |

Total:49 tests passed. These include existing synthetic fixtures and require no
new benchmark training or dataset downloads. GitHub returned no workflow runs
or commit statuses for PR3; local results are not represented as CI results.

The organization checks passed:94 catalog paths and194 Markdown targets exist;
all1,566 historical entries are assigned once with exact stage counts;405 original
files outside the five navigation/AI-use edits are byte-identical to `673a475`.
The exact index must pass `scripts/check_publication.py` before commit and push.
New data, labels, predictions, weights and private paths are excluded.
No benchmark results or scientific implementations change in this organization.

Teacher approval and human scientific acceptance remain **NOT_VERIFIED**.

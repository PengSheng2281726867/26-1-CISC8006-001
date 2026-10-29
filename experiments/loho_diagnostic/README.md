# Frozen GAMMA LOHO diagnostic

This independent adapter implements Final-only and Full-routing deletion of
hops1..K while retaining0-hop. It never edits or trains the protected model.
Read [PROTOCOL.md](PROTOCOL.md), [audit](reports/IMPLEMENTATION_AUDIT.md) and
[final report](reports/FINAL_REPORT.md). Teacher approval: NOT_VERIFIED.
GAMMA authorship/license: root LICENSE and NOTICE.md.

Use the existing compatible torch/PyG environment documented in the root README.
Set `LOHO_SOURCE_ROOT` to the owner-provided original artifact root containing
`test_mlp/` and `stability_validation/`. Set `LOHO_PRIVATE_ROOT` optionally to
private writable storage; default is `../private_outputs` relative to repository
root. Artifact/data access is private; public hashes do not supply these files.
Graph caches are copied into private storage before PyG loading. No source
workspace writes, dataset downloads or new training are needed.

From repository root (all interfaces below are implemented):

```powershell
python -B -m experiments.loho_diagnostic.src.audit
python -B -m experiments.loho_diagnostic.src.evaluate --config experiments/loho_diagnostic/configs/loho_pilot.json --plan
python -B -m unittest discover -s experiments/loho_diagnostic/tests -v
python -B scripts/smoke_test.py
python -B -m experiments.loho_diagnostic.src.evaluate --config experiments/loho_diagnostic/configs/loho_pilot.json --split val
python -B -m experiments.loho_diagnostic.src.evaluate --config experiments/loho_diagnostic/configs/loho_full.json --split val
```

Each execution prints its private batch directory. To combine pilot and remaining
cells, supply repeated `--input` arguments. Identical cells are deduplicated only
if their raw-array hashes agree; conflicting duplicates, failures and missing
expected cells cause summary failure. The full config can also run all180 cells
alone. No result directory is overwritten.

```powershell
python -B -m experiments.loho_diagnostic.src.summarize --input ../private_outputs/BATCH_ID --output experiments/loho_diagnostic/results/UNIQUE_SUMMARY_ID
python -B -m experiments.loho_diagnostic.src.plots --input ../private_outputs/BATCH_ID --output experiments/loho_diagnostic/results/UNIQUE_FIGURES_ID
```

Replace the uppercase IDs with actual printed directories. Summarization needs
NumPy/SciPy; plotting additionally needs matplotlib. Plotting can run in a
separate environment without torch/PyG. No shared environment was changed.
After freezing analysis and validation report, use the same full config with
`--split test`; generate separate summaries/figures. Test exposure in earlier
studies is disclosed; no pristine graph-level confirmation is claimed.

Public CSVs contain checkpoint-level statistics, seed means/SD per split, then
mean/sample SD across split means. `NA` denotes undefined statistics; reasons
are in correlations/per-checkpoint tables. Accuracy is a fraction; positive
accuracy_change helps, while positive delta NLL means deletion hurts.
`*_mean_mean` is equal-weight split mean of seed means; `*_mean_sample_sd` is
sample SD across split means. Within-split `*_sample_sd` measures seed variation.
Per-node arrays include all required losses, weights, predictions, correctness
and true-label probabilities, with dataset/split/seed/checkpoint/mask/hop encoded
by metadata and column axes. They are private and never staged.

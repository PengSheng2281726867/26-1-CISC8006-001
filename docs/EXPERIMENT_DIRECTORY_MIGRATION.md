# Four-group experiment directory migration

The user explicitly requested physically organizing the GitHub project into
the four groups discussed in the conversation. This migration starts at
`101b13406673fba50a9dd001bc1faa83f04a99da`; it supersedes the earlier flat
navigation layout. The old organization record remains a dated account of the
previous integration, not a description of the current folder tree.

## Current directories

```text
experiments/
  01_reproduction/
    historical_readme/
    early_gate/
    gate_sweep/
  02_scorer_ablation/
    dot_mlp/
    mlp_components/
  03_hop_diagnostics/
    hop_scope_study/
    loho_diagnostic/
  04_distance_query/
    exact_distance_query/
```

These are actual moved directories, including the dedicated studies' code,
configurations, figures, results and tests. Each group has a README explaining
its children and the comparisons. Historical groups continue to reference
shared canonical `analysis/`, `protocols/`, root `configs/`, registry and report
files; frozen implementations stay under root `research/`. Scientific data and
source are not duplicated. [Catalog](../experiments/catalog.json) and
[directory mapping](../experiments/layout_migration.json) describe the layout.

## Runtime and evidence compatibility

The three repository-root adapters locate the actual repository by its frozen
research source instead of a fixed parent count. The Exact-distance source
manifest follows the relocated Hop-scope data helpers. Source manifests include
the package routing file. No model, optimizer, loss or training algorithm changes.

`experiments/__init__.py` extends the package search path to the four group
directories. Public Python names such as `experiments.loho_diagnostic` and
`experiments.exact_distance_query` remain valid without old-directory stubs,
duplicate code, symlinks, numeric identifiers in import statements or global
environment changes. Cross-study imports and existing patch targets keep the
same module names. For example, from repository root:

```powershell
python -B -m experiments.exact_distance_query.src.run full --plan
python -B -m experiments.loho_diagnostic.src.evaluate --help
python -B experiments/03_hop_diagnostics/hop_scope_study/scripts/run.py --config experiments/03_hop_diagnostics/hop_scope_study/configs/full.json --data-root ../local_data --run-root ../local_runs --plan
```

File paths in live documentation and executable scripts use the grouped layout.
Run/result/provenance JSON, CSV, JSONL, figures, configuration files and frozen
protocols retain their exact bytes at their new locations. Their historical
path strings and hashes describe their execution versions. The directory map
and base commit provide the path translation; records are never rewritten to
pretend old runs used the new layout. The earlier study preservation checkers
describe their original import boundaries and are not migration verifiers.

Path and adapter changes produce new current source fingerprints. Existing
private runs are not silently accepted as current-version training or rewritten
to pass reuse checks. Historical execution sources remain available through Git.
This task starts no new benchmark training or data download.

## Verification

The migration adds regression checks for all eight directory assignments,
complete historical-stage partitioning, public module resolution, repository
root discovery, real source-manifest paths and original protocol freeze hashes.
The existing repository smoke, Hop adapter/statistics, LOHO and Exact-distance
suites must pass after the move. CLI plans are exercised without private data.

Before publication, all Markdown targets and catalog paths are checked, original
evidence bytes are compared through the migration map, and the exact staged
index must pass `python -B scripts/check_publication.py`. The published Git tree
is compared with the audited local index. The final commit/PR and merge outcome
are recorded in Git. Teacher approval and human scientific review remain
**NOT_VERIFIED**.

### Executed migration checks

- Repository smoke:16 tests passed, including3 new migration regressions and20
  author-alignment subcases. Hop adapter:7 passed; Hop statistics:4 passed;
  LOHO:9 passed; Exact-distance:16 passed. Total:52 tests passed.
- CLI plans confirmed720 Exact-distance primary cells,300 Hop-scope primary
  cells and180 LOHO checkpoints/1,620 conditions without training. Stable module
  imports and source manifests also worked from an external working directory.
- All8 directories moved, relocating278 tracked files. All418 original files
  remain present through the directory map;395 retain identical bytes. All273
  frozen source/evidence/config/protocol/figure files in the preservation check
  are byte-identical. The23 authorized edits are navigation, catalog, path
  adapters, a test fixture path and reporting command strings.
- All72 per-study catalog paths and258 Markdown file targets resolve. The1,566
  historical records are assigned exactly once by the migration regression.
- An initial Hop fixture correction placed its intentionally missing data path
  inside the checkout and triggered the external-data guard. It was corrected
  to the original external parent location, and all7 adapter tests then passed.
  The guard and scientific implementation were preserved.

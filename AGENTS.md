# Research repository rules

Preserve `research/src/`, `research/ablation_mlp/` and `research/upstream_snapshot/`
as imported, byte-verified scientific implementations. Isolate improvements and
training/provenance adapters. Do not change a validated Baseline to make tests pass.

- Each new scientific comparison needs its own config, stated claim, approval
  status and pre-run frozen protocol. Never mark a protocol teacher-approved
  without an accessible approval record. Do not start expensive training implicitly.
- Every real run must record a unique ID, Git commit and dirty status, exact config,
  seed, data/split checksums, start/end time, runtime, device, metrics, logs, output
  location and failure status. Prefer a clean committed tree; record dirty runs honestly.
- Never overwrite an old run. Preserve failures, negative results and superseded
  resource-measurement pilots. Scientific changes require a new experiment group.
- Use the shared training/evaluation path for fair comparisons. A method change
  does not authorize asymmetric hyperparameter tuning or test-set model selection.
- Important code changes need meaningful tests and corresponding README, audit,
  registry, provenance and AI-use updates. Run `python scripts/smoke_test.py`.
- Do not invent data, metrics, seeds, timestamps, historical commits, approvals,
  human verification, agent transcripts or team contributions. Recovered runs
  remain `pre-git experiment`; missing evidence stays UNKNOWN/NOT_VERIFIED.
- Before each commit/push run `python scripts/check_publication.py` against the
  exact index. Review credentials, private absolute paths, binaries, size and
  licenses. Never stage datasets, labels, predictions, checkpoints, `.env`, keys
  or tokens. Do not print discovered secrets.
- No force push or history rewrite. A reconstructed Baseline tag must say so;
  no Week 12 final tag before the human freeze decision.
- The original research workspace is read-only. This course repository is an
  independent copy; do not move or alter the original research to clean it up.

# Failure and exception record

All raw logs and failed artifacts remain local. Engineering failures below are
not failed scientific training cells. Exact event timestamps are UNKNOWN where
no dedicated machine timestamp was captured; this record was written 2026-10-25.

| Event | Observed outcome | Resolution / effect |
| --- | --- | --- |
| Initial HTTPS clone, Schannel | SEC_E_NO_CREDENTIALS | Per-command OpenSSL backend succeeded; no TLS verification disabled |
| Fetch/branch writes in clone | Permission denied on FETCH_HEAD/ref locks | Original Git metadata retained read-only; remote branch created through authorized GitHub connector |
| Request for sandbox escalation | Policy rejected: sandbox_approval=false | No escalation; use only writable local outputs and authorized connector |
| apply_patch new document | Failed file/parent write | PowerShell writes within authorized workspace succeeded; no original file modified |
| Read-only Git inventory from another process identity | Git dubious ownership | Per-command safe.directory for this one independent clone; no global Git settings changed |
| Plotting dependency in GAMMA environment | ModuleNotFoundError: matplotlib | Existing separate base Python3.14.6, Matplotlib3.11.0, NumPy2.4.6 used for plots; training environment unchanged |
| Read-only remote query using origin from task root | Origin not found | Explicit repository path and URL query verified main and experiment branch |

Existing repository smoke deliberately creates a missing-data failed fixture and
two synthetic successful runs per invocation. They are retained under ignored
outputs/ and excluded from this study's real-training totals. A mocked truncated
download/retry in smoke is a successful test, not a real dataset download failure.

Scientific attempt statuses, failure types, local artifact hashes and output IDs
are exported in results/attempts.jsonl and results/run_matrix.csv. An absent error
record does not stand for an attempted run: pending cells remain not_run. Failures
are never replaced by invented metrics or silently removed from denominators.

During an interim aggregation, a still-running attempt was initially counted as
failed/incomplete by the presentation layer. The aggregator now reports running
cells separately; raw run metadata was never changed and no actual training
failure was inferred from this interim count. No scientific execution/source or
protocol changed; the final matrix is regenerated from immutable metadata.

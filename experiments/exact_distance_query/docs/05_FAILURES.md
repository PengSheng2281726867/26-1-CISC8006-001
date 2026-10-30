# Failures, deviations and recovery

All scientific failures and missing units are exported by analyze into per-phase
failures.json/missing_cells.csv. Attempts and private tracebacks are never deleted
or overwritten. Negative accuracy deltas are ordinary completed results.

1. Default Python had no torch. Located the existing read-only GAMMA environment;
   no installation or shared environment edit was made.
2. Initial Schannel clone failed SEC_E_NO_CREDENTIALS. Command-local OpenSSL clone
   succeeded. Global TLS/security settings unchanged.
3. Nested .git writes refused branch ref creation. Kept that metadata untouched;
   an independent external Git metadata clone with GIT_DIR/GIT_WORK_TREE supports
   the actual local branch and commits. No force push or main modification.
4. First test invocation used workspace root rather than checkout root, causing
   unittest discovery error. Corrected working directory; all tests passed.
5. apply_patch could not write into a generated nested directory; ordinary Python
   file writes within the authorized workspace succeeded. No permissions changed.
6. Pilot analysis initially failed on missing matplotlib. Existing separate
   plotting interpreter now runs standalone plot.py; no retraining was required.
7. Publication preparation found CRLF whitespace in new generated evidence under
   the repository's byte-preserving attributes. Normalized only new study text
   artifacts to LF. Frozen source/protocol bytes were unaffected. An inline edit
   also hit a quoting SyntaxError and was corrected through a script.
8. Smoke group order was counterbalanced G2/G3/G0/G1 rather than G0-first. Original
   CPU/CUDA synthetic parity preceded all training; real G0 parity passed before
   Pilot. No outcome exclusion or training-budget change followed this deviation.
9. Short GPU smoke tests overlapped a few early Full timings during the Pilot
   evidence commit. Training runtime is an operational measurement, subject to
   background hardware load. Any dedicated final inference profiling is reported
   separately; parameter equality alone is never called compute fairness.

The legacy smoke suite intentionally creates a missing-data failed fixture under
ignored outputs. This is expected test evidence, not a scientific run failure.
Teacher approval and human review remain NOT_VERIFIED.

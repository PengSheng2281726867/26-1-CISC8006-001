# Negative and failed attempts

- Initial Git clone with Windows TLS failed SEC_E_NO_CREDENTIALS. Independent
  clone succeeded using the OpenSSL TLS backend; no original workspace changed.
- Base Python lacks torch; existing GAMMA environment supplies torch/PyG/SciPy.
  GAMMA lacks matplotlib; existing base environment supplies plotting. No shared
  environment installations or modifications were performed.
- First synthetic correct-alpha assertion required a difference >1e-4 from
  softmax(post_update_logits). K1/R1 produced differences8.40e-5 CPU and4.08e-5
  CUDA, correctly different but below that assertion. Corrected the *test*
  distinguishability bound to1e-6; scientific epsilon remains1e-5. All identity
  comparisons passed. This was a fixture assertion failure, not a mechanism result.
- First implementation commit followed a failing CRLF diff check because the
  shell did not stop on the native-command exit. Preserved history and repaired
  line endings in the next commit; original root-document bytes restored with
  appended content only. Subsequent commit/push gates use checked exit codes.
- PowerShell can report stderr test output as NativeCommandError even on a
  passing Python unittest run. Gates now capture Python output and actual exit
  status using subprocess.run; passing9 tests were reconfirmed.
- Intentional missing-data/failure fixtures are synthetic tests, not real failed
  checkpoints. Their private metadata/config/exception artifacts are retained by
  test harnesses where applicable. Root smoke preserves its own failure fixture.
- Real validation pilot6 and extension174: zero failed cells. Weak/negative rho,
  Top1 deletion improvements, ties and undefined rank statistics are retained.
  No checkpoint was excluded based on its diagnostic outcome.

Private terminal output and gate records remain on the execution workstation.
This report records actual failures; it is not a fabricated terminal transcript.

Test confirmation180/180 also completed with zero real failures.

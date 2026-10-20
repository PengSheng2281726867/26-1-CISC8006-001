# Failures and minimal fixes during current recovery

All items here occurred in the current session; historical issues stay separate.

| Issue | Evidence / hypothesis | Minimal handling | Outcome |
| --- | --- | --- | --- |
| Git schannel SEC_E_NO_CREDENTIALS on remote read | Actual Git command failed before data transfer | Use repository-local OpenSSL; no global trust or credential changes | ls-remote succeeded and showed no refs |
| Git dubious ownership on original author clone | Actual read-only Git command rejected ownership | One-shot safe.directory argument for this exact clone; no global exception | Author commit/remote could be read |
| gh command unavailable | Executable not found | Use existing Git and authenticated GitHub connector | Repo metadata/permissions checked |
| Freeze contains direct build reference | Pin-only import validation rejected it | Convert the package to installed metadata version; retain source-freeze hash and conversion note | Public version list generated; fresh rebuild still NOT_VERIFIED |
| Forty README metric records have no explicit training_seeds | Registry import raised missing-key error | Record UNKNOWN seed with NOT_VERIFIED metadata status | No invented seed values |
| Public scan found private paths in two JSON dictionary keys | Exact-index scanner blocked publication | Sanitize keys as well as values in public derivatives | Rerun passed; originals unchanged |
| Whitespace diff on frozen import emitted excessive CRLF/trailing-space output | Author/recovered bytes were intentionally preserved | Do not normalize validated source; restrict future whitespace review to new files | Scientific bytes remain identical |
| New synthetic success-path test found NumPy int64 was not JSON serializable | New metric adapter returned a NumPy count after reading predictions | Convert comparisons to native Python integer counts; add NumPy-input serialization regression | Fixed only new adapter; rerun evidence retained in smoke reports |
| PyG fresh Wisconsin download produced an empty split archive | Actual EOFError during NumPy loading, original cache untouched | New data adapter checks historical raw SHA256 before processing and retries into only its own cache | Truncated-download unit test added; fresh-download result recorded separately |
| Normal Git HTTPS push dry-run could not read Username | No credential is available to the noninteractive shell | Use the authorized GitHub connector for publication; preserve local branch and fetch published history | No credential extraction, force push or old-history rewriting |
| Archival publication scan found private paths in3 report generators | Scanner rejected copied source text before commit | Publish explicitly path-redacted text derivatives with original and derivative hashes;36 other archived files remain exact | Original scientific model/factory/train files remain byte-identical |

Subsequent test failures, if any, remain in ignored `outputs/smoke-*/tests.log`;
passing evidence does not remove prior failures. The smoke test also deliberately
exercises and retains a missing-data failure to verify provenance; it is a synthetic
test fixture, not a failed scientific experiment.

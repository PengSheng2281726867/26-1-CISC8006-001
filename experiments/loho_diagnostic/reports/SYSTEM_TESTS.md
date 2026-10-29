# Actual validation and system checks

Executed2026-10-29 using existing compatible environments.

| Check | Actual result |
| --- | --- |
| python -B scripts/smoke_test.py | PASS:13 tests,20 source alignment cases |
| python -B -m unittest discover -s experiments/loho_diagnostic/tests -v | PASS:9 tests, with CPU/CUDA and K/R subcases |
| No-mask output/used-alpha/NLL vs original | PASS:360 real checkpoint-evaluation cells; max output/alpha error0; atol2e-6/rtol2e-5 |
| Final-only earlier logits/alpha/fusion | PASS: unchanged round0 on all real K4/R2 cells |
| Full-routing alpha exactly0, other weights normalized, finite outputs | PASS on every real intervention |
|0-hop policy,K1/K4/K5,R1/R2/R3 | PASS synthetic boundaries;0-hop rejected if masked |
| Loss sign and true labels | PASS toy hand calculation: log2 and log.75 |
| Node/global equivalence | PASS synthetic nodes and one actual target per real intervention; only audited one-layer model accepted |
| State immutability | PASS before/after state hashes on360 cells;240 original files unchanged |
| Data/split/order integrity | PASS graph tensor hashes, split SHA/permutation and saved predictions/masks for all180 weights |
| Output provenance | PASS UUID directories, deliberate failure/config/log retention and expected-cell missing detection |
| Aggregation | PASS seed-then-split known answer/sample SD; effective counts retained |
| Pretest freeze | PASS all13 source/config/protocol/report hashes unchanged |
| Exact Git index publication/whitespace gates | PASS for validation freeze and final exact-index gates (see private gate records) |

The correct-alpha fixture initially failed an overstrict distinguishability bound;
its correction is recorded in NEGATIVE_AND_FAILED_RUNS.md. This is not a changed
scientific epsilon. All real validation and test cells completed successfully.
Raw successful/failed terminal artifacts remain private; hashes are published.
No benchmark training was started. Teacher approval NOT_VERIFIED.

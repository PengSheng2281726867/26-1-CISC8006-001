# Final LOHO diagnostic report

Completed 2026-10-29. All six phases (audit, implementation/tests, pilot,
extended validation, fixed test confirmation and publication preparation) were
executed. This is a frozen-weight sensitivity diagnostic, not an improved model.
Teacher approval and human scientific acceptance: NOT_VERIFIED.

## Main finding

High last-used alpha does **not exhibit a universal positive relationship** with
positive deletion loss. The prespecified descriptive pooled Spearman is weakly
positive on Chameleon/Squirrel and weakly negative on Actor/Texas/Wisconsin/
Cornell, on both validation and test. We did not calculate inferential p-values,
so these results do not establish a statistically significant association or its
absence. They also do not prove incorrect agreement learning.

## Executed coverage and controls

Primary cohort:180 actual trained stability_v1/core Dot checkpoints, K4/R2,
powers[0,1,2,3,4], one true GAMMA layer plus nodewise LayerNorm/Linear, six graphs,
ten fixed splits and three independent optimization seeds2026/2027/2028 per
split. Split seeds102..111 are different from training seeds. All180 passed
strict loading, saved artifact/state/graph/split hash checks and saved-prediction
alignment. The graph hash includes normalized features, exact edge order and
labels/node order.60 historical v2 K4 checkpoints were inventoried separately;
300 prior variable-hop checkpoints (propagation5/gating1..5,60 each) were read-only
candidates excluded because their forward semantics differ. Other K and model
families were outside the frozen primary cohort, not silently missing results.

Pilot: Chameleon/Actor split0, three seeds each,54 conditions. Extension reused
those six results and executed174 new checkpoints. Validation and test each have
180 checkpoint-evaluation cells and1,620 conditions (full plus8 deletions),
3,240 conditions total. There were no missing primary cells or failed real runs.
No new benchmark training, optimization or test-set configuration selection.
Root smoke uses its existing tiny synthetic training fixtures.

Every real evaluation passed original-vs-adapter output/used-alpha/NLL identity
(atol2e-6,rtol2e-5), mask normalization/zero-hop controls, final-only earlier-round
isolation and target-node/global equivalence. Maximum output and alpha error
were0 across all360 evaluations. All trained-state hashes before/after were
identical; all240 inventoried original checkpoint file hashes remained identical
after evaluation. Protected model/source files and old registries/results have
no changes relative to repository base935a4303ed0d1410e29d9374cc1ce91b82dc527c.

LOHO unit suite:9 tests with CPU/CUDA, K1/4/5 and R1/2/3 subcases. Root smoke:
13 tests and20 original-source alignment cases. Failure cases include missing
outputs, wrong node/split ordering, forbidden0-hop, coupled architectures,
incorrect loss signs and constant/nonfinite correlations. See SYSTEM_TESTS.md.

## Weight and loss alignment

Each number is an equal-weight mean over ten split means, each split first
averaging three optimization seeds. +/- is sample SD across split means, not a
confidence interval. Rho pools nodes and nonzero hops *within each checkpoint*
before this hierarchy; per-hop rho is separately available in summary tables.

| Dataset | Mask | Validation rho +/- SD | Test rho +/- SD | Validation within-node mean | Test within-node mean |
| --- | --- | ---: | ---: | ---: | ---: |
| Actor | final_only | -0.0806 +/- 0.0406 | -0.0917 +/- 0.0433 | -0.0357 | -0.0498 |
| Actor | full_routing | -0.0757 +/- 0.0433 | -0.0864 +/- 0.0476 | -0.0173 | -0.0320 |
| Chameleon | final_only | +0.0686 +/- 0.0756 | +0.0965 +/- 0.1018 | +0.1073 | +0.1292 |
| Chameleon | full_routing | +0.0891 +/- 0.0856 | +0.1037 +/- 0.1088 | +0.0978 | +0.1005 |
| Cornell | final_only | -0.0542 +/- 0.0879 | -0.1115 +/- 0.0953 | -0.0245 | -0.0446 |
| Cornell | full_routing | -0.0555 +/- 0.0891 | -0.0870 +/- 0.0948 | +0.0327 | +0.0050 |
| Squirrel | final_only | +0.1052 +/- 0.0381 | +0.1049 +/- 0.0387 | +0.0807 | +0.0906 |
| Squirrel | full_routing | +0.1450 +/- 0.0495 | +0.1448 +/- 0.0525 | +0.0717 | +0.0888 |
| Texas | final_only | -0.0925 +/- 0.1292 | -0.0517 +/- 0.1543 | -0.0969 | +0.0356 |
| Texas | full_routing | -0.0296 +/- 0.1170 | -0.0457 +/- 0.1491 | -0.0056 | +0.1097 |
| Wisconsin | final_only | -0.1212 +/- 0.0826 | -0.1138 +/- 0.0975 | -0.0188 | -0.0436 |
| Wisconsin | full_routing | -0.1064 +/- 0.0844 | -0.1009 +/- 0.1132 | +0.0267 | -0.0127 |

Within-node means use only defined correlations across hops1..4. Constants are
NA, never zero-imputed. Undefined proportions, effective valid node counts and
within-node medians are reported for every checkpoint in correlations.csv and
aggregated by split. The validation undefined fraction ranges from about19%
to62%; this is a material limitation, particularly on Chameleon/Squirrel. Per-hop
correlations and means need not share the sign of the pooled correlation; pooled
weight differences across hops/nodes are not within-node explanatory evidence.

## Highest-weight nonzero hop can improve loss when removed

Top1 means argmax alpha among hops1..4, excludes0-hop and resolves exact ties by
lowest hop. It is relative highest among eligible hops, not necessarily high in
absolute mass or the overall maximum including0-hop. Negative means delta<-1e-5.

| Dataset | Mask | Validation negative % | Test negative % | Validation Top1 tie % | Test Top1 tie % |
| --- | --- | ---: | ---: | ---: | ---: |
| Actor | final_only | 53.48 | 54.27 | 29.93 | 29.98 |
| Actor | full_routing | 53.37 | 54.21 | 29.93 | 29.98 |
| Chameleon | final_only | 45.00 | 44.41 | 62.04 | 61.52 |
| Chameleon | full_routing | 45.39 | 45.05 | 62.04 | 61.52 |
| Cornell | final_only | 36.76 | 40.70 | 17.22 | 19.56 |
| Cornell | full_routing | 37.04 | 40.79 | 17.22 | 19.56 |
| Squirrel | final_only | 43.87 | 43.62 | 57.70 | 57.35 |
| Squirrel | full_routing | 42.96 | 42.75 | 57.70 | 57.35 |
| Texas | final_only | 41.11 | 38.16 | 21.76 | 23.07 |
| Texas | full_routing | 41.76 | 38.68 | 21.76 | 23.07 |
| Wisconsin | final_only | 35.20 | 33.66 | 26.73 | 26.47 |
| Wisconsin | full_routing | 36.67 | 34.97 | 26.73 | 26.47 |

Positive and near-zero Top1 fractions and loss mean/median are preserved in the
same tables. Ties are common, so deterministic Top1 is not a unique preferred-hop
interpretation. No effect threshold or tie rule was tuned to increase negatives.
A negative intervention effect does not identify the original hop as inherently
harmful: deleting it also changes other weights and the inference distribution.

## Per-hop behavior and condition metrics

The ranges below span hop1..4 **dataset-level means**, not node extrema. Accuracy
is a fraction; positive accuracy_change means masked accuracy increases. Positive
mean delta NLL means deletion increases loss. Baseline accuracy/NLL repeat across
mask/hop conditions by design. Exact per-hop medians, mean weights, correlations,
NLLs, prediction flips and positive/negative/zero fractions are in summary CSVs.

| Dataset | Mask | Validation full accuracy / NLL | Validation mean delta range | Test full accuracy / NLL | Test mean delta range |
| --- | --- | ---: | ---: | ---: | ---: |
| Actor | final_only | 0.3591 / 1.4835 | +0.00079 to +0.00626 | 0.3529 / 1.4695 | -0.00179 to +0.00598 |
| Actor | full_routing | 0.3591 / 1.4835 | +0.00557 to +0.01358 | 0.3529 / 1.4695 | +0.00171 to +0.01164 |
| Chameleon | final_only | 0.5218 / 1.6997 | +0.02146 to +0.03313 | 0.4898 / 1.7472 | +0.02523 to +0.03924 |
| Chameleon | full_routing | 0.5218 / 1.6997 | +0.05978 to +0.07132 | 0.4898 / 1.7472 | +0.06903 to +0.07966 |
| Cornell | final_only | 0.8259 / 1.0992 | -0.01401 to +0.01734 | 0.7561 / 1.1979 | -0.02776 to -0.00108 |
| Cornell | full_routing | 0.8259 / 1.0992 | -0.00976 to +0.02914 | 0.7561 / 1.1979 | -0.03155 to +0.00485 |
| Squirrel | final_only | 0.3591 / 1.7704 | +0.01937 to +0.05004 | 0.3403 / 1.7816 | +0.01657 to +0.05184 |
| Squirrel | full_routing | 0.3591 / 1.7704 | +0.06117 to +0.11195 | 0.3403 / 1.7816 | +0.05394 to +0.11315 |
| Texas | final_only | 0.8315 / 1.0367 | -0.08884 to +0.00385 | 0.8079 / 0.9033 | -0.06669 to +0.00225 |
| Texas | full_routing | 0.8315 / 1.0367 | -0.08941 to -0.00409 | 0.8079 / 0.9033 | -0.07193 to -0.01165 |
| Wisconsin | final_only | 0.8973 / 0.5798 | -0.00280 to -0.00028 | 0.8464 / 0.6961 | -0.00593 to -0.00036 |
| Wisconsin | full_routing | 0.8973 / 0.5798 | -0.00255 to -0.00075 | 0.8464 / 0.6961 | -0.00945 to -0.00368 |

## Full-routing versus Final-only

Final-only freezes the firstR-1 rounds and changes only the last used fusion.
Full-routing changes every fusion and hence the subsequent agreement state.
Paired effects below are averaged over hops1..4 after the seed/split hierarchy.
Positive full-minus-final means Full-routing deletion causes more loss increase.

| Dataset | Val paired mean | Test paired mean | Val absolute paired mean | Test absolute paired mean | Test sign reversal % |
| --- | ---: | ---: | ---: | ---: | ---: |
| Actor | +0.005333 | +0.004009 | 0.019134 | 0.018623 | 4.62 |
| Chameleon | +0.037993 | +0.041701 | 0.061287 | 0.066179 | 2.53 |
| Cornell | +0.005051 | -0.001230 | 0.023662 | 0.031288 | 10.31 |
| Squirrel | +0.048403 | +0.046641 | 0.098694 | 0.100105 | 3.54 |
| Texas | -0.007395 | -0.013573 | 0.034435 | 0.028449 | 6.78 |
| Wisconsin | -0.000313 | -0.003418 | 0.006696 | 0.010155 | 4.15 |

There is no universal compensation direction. In particular, mean Full-routing
sensitivity is larger on several graphs but can be smaller on Texas. The masks
intervene at different stages, so their difference establishes dependence on
routing history without identifying a causal compensation process. Unconfirmed
alternatives include correlated branches, redistribution toward0-hop, nonlinear
squash/LayerNorm/head effects and distribution shift. No small delta proves
complete redundancy. No causal ground-truth contribution was measured.

## Consequences and limits

These observations motivate studying the relationship between agreement and task
sensitivity, and could inform separately approved sparse-hop selection,
leave-one-out agreement or learned scoring hypotheses. They do not show that any
of those methods improves held-out accuracy or compute. An intervention-based
label-dependent selector would require a separate training/validation protocol,
matched controls and prospective budget; no such method was implemented here.

Coverage is complete for this six-graph K4/R2 cohort, not for every K, deep model
or graph distribution. Three seeds within a split do not create three independent
graphs. Ten overlapping splits describe variation on the same graph; no node
bootstrap, p-values, corrected significance claims or causal generalization.
Many graph/hop comparisons are exploratory. Existing checkpoints were selected
by validation during training, so validation diagnostic labels are not a fresh
holdout. Test confirmation used the committed identical analysis/cohort, but
these datasets and checkpoint test metrics were previously exposed in historical
studies; this is conditional confirmation, not a pristine study-level test.
Graph structure includes validation/test nodes in this transductive setting;
this differs from using test labels to optimize a new method.

Raw labels, predictions, per-node arrays, checkpoints and private absolute paths
are not published. Public SHA256 evidence does not make private artifacts
publicly downloadable. Human scientific review, teacher acceptance, external
artifact access and broader/new-model causal studies remain outstanding. No new
training or recovery was required. No PR merge or final course tag is authorized.

## Reproducibility and outputs

Commands and environment separation are in README.md. PROTOCOL.md was frozen
before outcomes; PRETEST_FREEZE.json and commit85bcfce froze validation/report
and all analysis code before test execution. All13 freeze hashes were verified
unchanged after test. Results/full_val and results/full_test contain checkpoint,
split and dataset summaries, alignment, paired effects and evidence CSVs.
Pilot results remain separately available without duplication in full summaries.
68 real-data figures were generated:8 pilot,30 full validation,30 test. Titles
state graph,K,R,mask,eval set,seed/checkpoint counts. Selected figure layouts were
visually checked. Raw observations shown in plots are dependent observations,
not independent replications. EVIDENCE_MANIFEST.md identifies private storage and
hash mappings; SYSTEM_TESTS.md records checks. NEGATIVE_AND_FAILED_RUNS.md retains
engineering failures and negative/undefined scientific outcomes.

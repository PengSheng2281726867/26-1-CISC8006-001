# Validation report and analysis freeze

2026-10-29. Completed180/180 prespecified checkpoints (six graphs x ten fixed
splits x three optimization seeds),1,620 conditions, K4/R2 Dot. The six pilot
cells are reused once, with174 new cells. All graph/split/checkpoint controls
passed. No weights changed. No missing primary cells or failed real executions.
Only validation-node labels were used for these new diagnostic losses.

The table reports mean +/- sample SD across ten split means, after equal-weight
averaging the three optimization seeds within each split. Rho is descriptive,
not a significance test. Top1 excludes0-hop, ties choose lowest hop, and negative
means delta NLL < -1e-5. Other signs and near-zero fractions remain in CSVs.

| Dataset | Mask | Pooled rho (mean +/- SD) | Within-node rho mean | Top1 negative % | Undefined within-node % | Top1 tied % |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Actor | final_only | -0.0806 +/- 0.0406 | -0.0357 | 53.48 | 29.87 | 29.93 |
| Actor | full_routing | -0.0757 +/- 0.0433 | -0.0173 | 53.37 | 29.87 | 29.93 |
| Chameleon | final_only | +0.0686 +/- 0.0756 | +0.1073 | 45.00 | 62.04 | 62.04 |
| Chameleon | full_routing | +0.0891 +/- 0.0856 | +0.0978 | 45.39 | 62.04 | 62.04 |
| Cornell | final_only | -0.0542 +/- 0.0879 | -0.0245 | 36.76 | 18.52 | 17.22 |
| Cornell | full_routing | -0.0555 +/- 0.0891 | +0.0327 | 37.04 | 18.80 | 17.22 |
| Squirrel | final_only | +0.1052 +/- 0.0381 | +0.0807 | 43.87 | 57.70 | 57.70 |
| Squirrel | full_routing | +0.1450 +/- 0.0495 | +0.0717 | 42.96 | 57.70 | 57.70 |
| Texas | final_only | -0.0925 +/- 0.1292 | -0.0969 | 41.11 | 20.56 | 21.76 |
| Texas | full_routing | -0.0296 +/- 0.1170 | -0.0056 | 41.76 | 20.83 | 21.76 |
| Wisconsin | final_only | -0.1212 +/- 0.0826 | -0.0188 | 35.20 | 21.47 | 26.73 |
| Wisconsin | full_routing | -0.1064 +/- 0.0844 | +0.0267 | 36.67 | 22.07 | 26.73 |

Alignment differs by graph: Chameleon/Squirrel pooled rho is weakly positive,
while Actor and the three WebKB graphs are weakly negative. This does not
establish inferential significance or a universal relation between weight and
benefit. Undefined within-node correlations reflect constant rank inputs;
all finite validation data were retained and NA was not replaced by zero.
High tie rates limit deterministic Top1 interpretation. Within-node medians and
valid sample counts, per-hop correlations, seed variation within each split,
all accuracy/NLL conditions and flip/sign fractions are in full_val CSVs.

## Intervention difference (validation)

Values below average over the four nonzero hops after the seed/split hierarchy.
Positive full-minus-final difference means Full-routing deletion hurts more.

| Dataset | Mean paired delta NLL | Mean absolute paired difference | Sign reversal % |
| --- | ---: | ---: | ---: |
| Actor | +0.005333 | 0.019134 | 4.75 |
| Chameleon | +0.037993 | 0.061287 | 2.64 |
| Cornell | +0.005051 | 0.023662 | 8.52 |
| Squirrel | +0.048403 | 0.098694 | 3.60 |
| Texas | -0.007395 | 0.034435 | 7.38 |
| Wisconsin | -0.000313 | 0.006696 | 5.03 |

Different interventions perturb different routing states, so differences are
expected without identifying whether routing compensates. Correlated hops,
renormalization, nonlinear squash/norm/head and mask-induced distribution shift
are plausible alternatives to a scorer defect. Near-zero effects do not prove
redundancy. These results motivate a separate hypothesis-driven study, not an
accuracy-improvement claim or evidence of MLP/sparse-selection superiority.

## Test confirmation frozen before execution

The complete cohort, epsilon, tie rule, interventions, statistics and figure
implementation are fixed. Test will use the same180 checkpoints, without
selecting graphs/hops/seeds based on validation. This report and source are
committed before test diagnostics. No hyperparameter or selection strategy is
learned. Earlier studies already exposed test results for these checkpoints;
confirmation is conditional on this model collection, not a pristine independent
graph-level validation. Overlapping splits supply descriptive variability only.
Teacher approval and human scientific acceptance remain NOT_VERIFIED.

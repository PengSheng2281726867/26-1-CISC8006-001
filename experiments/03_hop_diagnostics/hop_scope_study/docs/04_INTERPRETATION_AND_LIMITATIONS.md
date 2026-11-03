# Interpretation, negative results and limits

The registered technical matrix is complete:300 independent primary trainings (including12 verified Pilot cells) and300 no-update mask evaluations from60 full-hop checkpoints. No historical baseline was altered or pooled. Teacher approval remains **NOT_VERIFIED**. This is a diagnostic fixed-x intervention, not a newly implemented per-node hop selector.

H1: mean test curves are not monotonically nondecreasing in 6/6 datasets (Texas, Wisconsin, Cornell, Chameleon, Squirrel, Actor). This is descriptive evidence under the frozen local protocol, not proof that high-hop features are intrinsically redundant or harmful. Increasing x can improve, plateau or degrade a trained model; changing the candidates also changes optimization and normalization of routing weights.

H2: validation-best **mean** x (descriptive, not a new pooled test-selected model): Texas=2, Wisconsin=3, Cornell=3, Chameleon=5, Squirrel=1, Actor=1. Per-split x selection and test evaluation are separately reported in validation_selection.csv. Different selected scopes can reflect real graph differences, small/noisy validation sets, coarse accuracy ties and initialization as well as signal usefulness. The chosen tie rule favors smaller x on exact validation ties.

There are 0/24 primary contrasts below0.05 after Holm correction within each dataset (four x-vs5 contrasts). Families are not corrected across all six datasets. Overlapping splits limit inferential independence; do not treat these thresholds as independent-graph confirmation.

## Concrete positive and negative examples

Largest positive descriptive contrast: Texas, x=2 minus x5 is +2.89 pp, sampleSD 10.34, paired bootstrap95% interval [-3.16,+9.21], Holm p=1.00000. This example was selected to illustrate the complete test curve after execution, not to choose a deployed x or claim an unbiased winner.

Largest negative descriptive contrast: Texas, x=3 minus x5 is -2.11 pp, sampleSD 8.40, paired bootstrap95% interval [-7.37,+2.63], Holm p=1.00000. This example was selected to illustrate the complete test curve after execution, not to choose a deployed x or claim an unbiased winner.

H3 exploratory: the largest absolute mean post-hoc-minus-retrain gap among x1-4 is Squirrel, x=1: -4.48 pp (sampleSD 2.23). A model trained using all hops can respond differently to removing candidates than a model trained for that scope. Post-hoc masks change the training/inference distribution, so a post-hoc loss cannot be equated with a retrained architecture's intrinsic quality. x5 itself is checked against the saved full-control accuracy and all diagnostic state hashes stay unchanged.

## Mechanism, costs and limitations

Inactive candidates have exactly zero routing coefficients and classification gradients in every iteration. They retain parameter rows and remain subject to optimizer weight decay. Shared projection, LayerNorm, squash, classifier and all propagation operations remain present. Every forward uses15 additive propagate calls across independent branches, maximum chain5, six tensors; masking therefore does not remove the propagation expense. Measured time/peak/incremental allocated GPU memory and parameters are in resource_summary.csv; inference timings use5 warmups/20 repeats and GPU synchronization. CPU RSS/extra host memory and monetary cost are UNKNOWN. Costs were observed on a Windows/WDDM workstation with display activity and concurrent host-side documentation/analysis work, not an isolated speed benchmark. No total speedup claim.

One optimization seed per split couples split and initialization variation. Ten splits overlap within one graph. The same validation set chooses epoch and scope, so selected test estimates have potential selection bias; no nested selection was run. Small WebKB validation sets have coarse accuracy resolution. No method-specific hyperparameter search, extra independent graph, causal per-node attribution, data leakage intervention beyond label-isolation tests, or strict paper-style protocol replication was performed. Gate weights alone do not establish causal hop usefulness. The inherited normalized-entropy scalar divides by log(6), the full candidate count, at all x; it must not be read as active-count-normalized confidence across scopes.

Local source-faithful protocol differs from the paper text: one actual GAMMA layer, LayerNorm,60/20/20,early stopping and inclusive0..x. New six-hop initialization differs from historical K4 canonical initialization. All arms in this experiment have the same complete parameter state and RNG at initialization. Dropout operations have matched shapes; different stopping times use different total RNG draws.

Execution Git SHA identifies base main plus dirty source hashes; the later publication commit is not relabeled as the training commit. Fresh environment installation and public checkpoint hosting remain NOT_VERIFIED/NOT_PROVIDED. Original source and protected historical evidence are checked separately. Scientific zero/negative results and engineering failure records are retained.

## Most useful next adaptive-hop direction (proposed only)

Study a sparse per-node hop budget within the existing Dot routing, keeping a mandatory0-hop and a full-hop matched control. First compare stability across multiple optimization seeds per fixed split and use nested validation for budget selection. Then test whether selective candidates generalize when trained with the same intervention they receive at inference; use node-level counterfactual masks rather than interpreting large alpha as causal importance. This is a prospective research direction motivated by scope dependence and post-hoc/retrain mismatch, not an implemented architecture or a promised improvement. Freeze its protocol and obtain any required teacher approval before a new study.

# Interpretation and limitations

All720 primary cells were trained anew;48 Pilot and4 Smoke cells were verified and reused, without duplicate counting. Nine separate empty-policy controls were trained. All720 selected primary checkpoints and9 control checkpoints were saved, hashed, reloaded and output-checked. No scientific training failed. Teacher approval and human review are NOT_VERIFIED.

## Pre-specified paired comparisons

|Dataset|G1-G0 pp|G2-G1 pp|G3-G1 pp|G3-G2 pp (exploratory)|
|---|---:|---:|---:|---:|
|Texas|+0.351|+1.228|-4.211|-5.439|
|Wisconsin|-1.634|+2.288|-3.529|-5.817|
|Cornell|+3.070|+2.018|-1.579|-3.596|
|Chameleon|+0.402|-0.724|-0.928|-0.205|
|Squirrel|-0.106|-0.842|+1.085|+1.928|
|Actor|-0.026|+1.237|-0.257|-1.493|

The full accuracy/uncertainty tables are in03_FULL_RESULTS.md and results/full. Split means are the units of aggregation; seeds are averaged within split first. All signs and raw paired cells are retained. Holm3 p-values and bootstrap intervals are descriptive on overlapping splits, not independent-graph confirmation. There was no test-based method or checkpoint selection.

## Query behavior and scale

|Dataset|G0 entropy / Q norm|G1 entropy / Q norm|G2 entropy / Q norm|G3 entropy / Q norm|
|---|---:|---:|---:|---:|
|Texas|0.375 / 0.768|0.281 / 0.917|0.004 / 6.105|0.297 / 2.694|
|Wisconsin|0.341 / 0.779|0.330 / 0.909|0.024 / 6.080|0.180 / 2.806|
|Cornell|0.467 / 0.768|0.347 / 0.904|0.002 / 6.172|0.221 / 2.543|
|Chameleon|0.598 / 0.706|0.342 / 0.955|0.005 / 6.026|0.174 / 2.217|
|Squirrel|0.597 / 0.749|0.391 / 0.958|0.014 / 5.846|0.263 / 2.347|
|Actor|0.559 / 0.846|0.457 / 0.936|0.029 / 6.204|0.198 / 3.015|

Entropy above is normalized per node by log(number of eligible candidates), with0 for a single eligible candidate. These normalized entropy, query-scale, concentration and matched-denominator cosine summaries are supplementary post-Pilot diagnostics, not new preregistered outcome tests. Original preregistered unnormalized entropies and all raw/gamma/LN cosines remain in mechanisms.json.

Fixed-query definitions preserve LN(gamma*H0/H4); Consensus uses squash(mean(valid candidates)). Their query norms and therefore dot-score scales differ by construction. A more concentrated fixed-query softmax cannot be attributed exclusively to query information. A shared-temperature/query-norm ablation would be a separate future study, not an unreported model change. G2 often puts nearly all mass on0-hop because the H0 query matches its own candidate. Such a result is consistent with self-feature reliance, not evidence that high-hop selection improved.

Primary cosine summaries compare all G0 candidate pairs versus valid Exact pairs; denominators differ. The dedicated profiling CSV additionally reports LN cosine using the same topology-valid pair masks for every group. Positive/negative similarity changes and gate concentration are correlations. Neither establishes a strict causal mechanism or information redundancy.

## Measured inference and resources

|Dataset|G0 ms|G1 ms|G2 ms|G3 ms|
|---|---:|---:|---:|---:|
|Texas|6.751|1.757|1.505|3.686|
|Wisconsin|6.981|1.708|1.496|3.940|
|Cornell|6.860|1.764|1.490|3.753|
|Chameleon|8.184|1.750|1.580|4.224|
|Squirrel|28.914|1.816|1.624|12.545|
|Actor|8.156|1.887|1.614|4.417|

Dedicated inference measurements reload all720 hash-verified checkpoints and run5 warmups/20 synchronized repeats, serially after training and controls. No optimizer or model selection is performed. Training runtime remains an operational measure subject to background system load and different early-stop epochs; epoch timing and stopped-epoch means are also published.

G0 preserves the frozen implementation:5 projections and10 PyG propagations. G1/G2 use1 projection and4 sparse shell mm; G3 adds4 Walk propagations. Timing differences therefore reflect both semantics and implementation reuse, not solely topology distance. All parameter counts match within dataset. GPU peak allocation is the total harness allocation during training; the shared B cache remains resident even in G0, so this is not isolated minimal model memory. CSR storage and one-time BFS construction time are separately reported in distance_<dataset>.json. Monetary cost UNKNOWN; fresh environment installation NOT_VERIFIED.

## Bounded empty-hop policy control

|Group|Legacy minus masked Test pp, mean of3 seeds|
|---|---:|
|G1|-1.754|
|G2|+0.000|
|G3|-0.877|

This is Texas split0 only, a pre-specified bounded control, not a six-graph estimate. Legacy leaves affine-LN empty shells eligible; primary zeroes and masks them. Initial state, graph/split and parameter counts were verified identical. Single-split outcomes cannot isolate empty-policy effects throughout the Full matrix.

## Negative illustrative case (post-hoc, retained)

Largest G3-G1 deterioration: Wisconsin, split9, seed42, -25.490pp. G3 run `2026-10-30T043808643491+0000-5dcd57fe` test=52.941%, validation=88.000%, selected epoch19; G1 run `2026-10-30T043814066733+0000-fa011b04` test=78.431%, validation=92.000%, selected epoch81.
This case was selected after results for illustration, never for tuning or exclusion. Compare its stored alpha/entropy, selected epochs, validation scores and query-scale diagnostics. A high-order Walk reference can misalign with useful Exact candidates; scale, feature mixing, optimization and validation variance are alternative explanations. No causal attribution is claimed.

## Scope of conclusion

G1-G0 jointly changes Walk multiplicity, distance mixing, shell size, empty policy and compute. G2/G3 hold Exact candidates fixed but change the prescribed query function, including its scale. The four-arm study is not the full2x3 aggregation-by-query factorial: Walk+H0/H4 remain unexecuted. Results support dataset-dependent behavior and preserve negative findings. They do not prove universal Exact-distance or fixed-query superiority, reproduce paper Table3, establish causality, or establish course approval.

## Observed cosine and0-hop preference

|Dataset|G0 matched cosine|G1|G2|G3|G2 mean alpha0|
|---|---:|---:|---:|---:|---:|
|Texas|0.570|0.332|0.337|0.563|0.999|
|Wisconsin|0.581|0.395|0.364|0.643|0.992|
|Cornell|0.483|0.301|0.299|0.605|1.000|
|Chameleon|0.754|0.614|0.531|0.710|0.997|
|Squirrel|0.699|0.702|0.501|0.746|0.985|
|Actor|0.803|0.745|0.801|0.855|0.989|

Matched-denominator LN hop cosine is lower for G1 than G0 on5/6 graphs, but is
slightly higher on Squirrel. Lower similarity does not consistently improve
accuracy: Wisconsin decreases while Cornell increases. Learned W/gamma/LN differ
after training, so these cross-model feature statistics mix topology and learned
representation changes. G2's near0-hop preference and very low entropy support
self-feature reliance; they do not support a claim of better high-hop selection.
Actor G2-G1 is+1.237pp with nominal Holm3 p=.00586; Texas/Chameleon G3-G1 are
negative with nominal Holm3 p=.02344/.03516. No G1-G0 contrast passes Holm3.
All these p-values are descriptive under correlated splits; no strict causal or
independent-graph significance conclusion is made.

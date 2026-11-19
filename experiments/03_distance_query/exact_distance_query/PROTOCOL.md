# Exact-distance and query-gating protocol v1

Prospective technical study, explicitly user-authorized. Teacher approval: **NOT_VERIFIED**.
Base main: `5e7eb902d32bda4665b5235582dc59eebf556178`. Freeze timestamp and hashes
are in results/protocol_freeze.json; no real training has started at freeze.

L_actual=1, K=4, powers=[0,1,2,3,4], original_R=2, hidden_dim=32.
Retain the frozen biased shared projection Z=Linear(X), gamma channel scaling,
shared affine LayerNorm, squash, final bias, output LayerNorm, Linear/log_softmax,
input/hidden dropout .2/.8. Z includes the existing bias (the shorthand XW omits it).
No added parameters. All groups initialize from the same canonical K4 Dot state,
and reset training RNG per cell. B construction never consumes training RNG.

G0 uses the exact frozen independent-branch Walk implementation and two rounds of
consensus. G1 replaces candidates with Bp Z, preserving consensus. Bp[target,source]
is binary shortest directed message distance p, B0=I. No symmetrization, added
self-loops, degree normalization or walk counts. Original A preserves weights,
duplicate edges and source-to-target direction. G2 query is LN(gamma0*Z);
G3 query is LN(gamma4*A^4 Z), not E4. Exact candidates only, always including0.
G2/G3 use one dot/softmax/fusion, then the same squash and final bias.
Mask empty Exact shells after LayerNorm and before every softmax. G0 is unchanged.
G1-one-shot uses squash(mean(valid normalized candidates)) as query: compare
forward, used_alpha and gradients with R2, synthetic and real trained checkpoints.
Bias is added after final fusion, never to the initial consensus query.

Sparse reverse-neighbor BFS truncated at4 constructs deterministic CSR shells;
duplicate topology edges collapse for B only, self-distance remains0. Guard total
NNZ at100 million before allocation growth; a guard failure is a resource failure,
not permission to change protocol. Record topology/order/cache/content hashes,
build time, NNZ, shell counts and empty fractions. No dense NxN float default.
Use sparse mm from current Z every forward; do not cache trainable embeddings.

Six datasets, NormalizeFeatures, verified raw hashes and fixed60/20/20 CPU
randperm splits102..111. Three optimization seeds42/43/44 per split (reuse the
prospective three-seed convention, unlike historical42+split). Adam .02, wd1e-4,
clip1, ReduceLROnPlateau max/factor.5/patience50/min_lr1e-6, max500 epochs,
early stopping50. Strict validation improvement and deep-copy earliest best.
Reuse frozen train_model unchanged; CrossEntropy on log_softmax is equivalent
to NLL. Test assessed only after checkpoint selection. No method-specific tuning.
One serial GPU process, threads1, deterministic algorithms, TF32 off.

Sequence: synthetic tests and legacy smoke; real Texas split0 all four groups,
full training budget; Pilot Chameleon/Actor, splits0/1, 3 seeds, 48 cells;
resource/pilot review; Full6*10*3*4=720 cells. Pilot can count toward Full only
if scientific code/protocol/config training/data/split/init/artifact hashes match.
Smoke cells may also be reused under the same checks. Failure attempts retained.
Counterbalance group order by split/seed. Resume never overwrites an attempt.
No arbitrary time cap; resource failures remain explicit missing cells.

Bounded empty-policy control: Texas split0, seeds42/43/44, G1/G2/G3, legacy
unmasked affine-LN empty shells versus primary masked arms (9 extra trainings).
It is a separate ablation, never pooled with primary cells. Real checkpoint
one-shot equivalence is inference/backward validation, not another training arm.

Report seed means within split first, then equal-weight split mean and sample SD;
also publish raw cell scores and within-split seed SD. Primary paired deltas:
G1-G0, G2-G1, G3-G1; G3-G2 exploratory. Descriptive bootstrap95% CI over split
means, 20000 draws, seed20261030; exact two-sided sign flip over split means,
Holm3 per dataset for the primary family. Overlapping splits on one graph are
not independent graph samples; statistical evidence remains descriptive.
No test-best model selection or universal improvement claim.

Diagnostics: used_alpha means/SD/quantiles and entropy; pairwise hop cosine
before scaling, after gamma and after LN (valid-pair denominator); shell counts,
empty fractions; training/inference wall time and GPU memory; parameter counts.
Record actual operation counts: G0 repeats ten PyG propagations/five projections;
G1/G2 four sparse shell mm/one projection; G3 additionally four Walk propagations.
One-time B build/storage is separate. Timing depends on sparse pattern and kernels.
Walk counts, distance mixing, aggregate scale, empty policy and cost all change;
do not attribute performance exclusively to reduced redundancy or causal gating.

All attempts have unique IDs, timestamps, Git/dirty, source/config/protocol hashes,
graph/split/init/RNG hashes, environment, epoch traces, selected checkpoint and
artifact hashes. Private arrays/labels/weights/logs/cache remain outside Git.
Public outputs are safe scalar summaries, plots, relative identifiers and hashes.
Historical source, registry and experiment files are immutable. MIT attribution:
Amir Ghazizadeh, Rickard Ewetz, Hao Zheng; root LICENSE/NOTICE apply.

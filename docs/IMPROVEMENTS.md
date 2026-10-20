# Improvements: recovered evaluation and proposed ideas

## I1 — shared MLP agreement (executed, approval NOT_VERIFIED)

Hypothesis: a learned nonlinear compatibility function can improve classification
relative to a fixed dot interaction, with an effect that may depend on maximum K.

Original: a[i,p]=sum_d H[i,p,d]*v[i,d]. Existing modification:
z=concat(H[i,p],v[i]); a[i,p]=w2^T ReLU(W1 z+c1)+c2.
The actual scorer is Linear(64,32)→ReLU→Linear(32,1), shared across nodes, hops
and routing iterations. H is[N,P,32], v[N,32], input[N,P,64], output[N,P].
No detach/no_grad cuts the classification-loss gradient. Score accumulation,
softmax, weighted sum, squash and bias remain unchanged. Two linears add2,113
parameters, independently of K. Output node representation remains32; output
score stays scalar; original normalization, dropout and training budget are unchanged.

Executed status: **Full technical evaluation**, not just Pilot: six datasets×four
K×two methods×ten splits=480 trainings, with24 verified Pilot runs reused.
MLP has240 runs with nonzero finite scorer gradients and parameter updates.
MLP−Dot averages−0.51 pp,12 improvements/12 declines, no Holm24 significance.
Train-step cost is about+7.2%, inference+8.3%, peak allocation+0.272MiB against
the matched original Dot/MLP measurements. This does not support universal MLP
superiority. No parameter-matched Dot control was performed, which limits an
interpretation separating function class from parameter capacity.

Technical fairness: identical splits, shared GAMMA initial parameters and RNG,
same optimizers/budget/selection, no method-specific tuning. Remaining weaknesses:
one seed per fixed split, overlapping splits, no independent graph validation,
historical execution Git hash UNKNOWN and teacher approval NOT_VERIFIED.
Course full evaluation status is therefore Partial despite a completed technical matrix.

## Executed follow-up ablations (not newly proposed or approved)

- LN-only: Linear64→32→LayerNorm32(eps1e-5,affine)→ReLU→Linear32→1.
  Adds64 parameters to MLP; mean+0.02pp vsMLP,13/1/10 improved/tied/degraded.
- GELU-only: replace only ReLU with exact GELU; adds0 parameters to MLP;
  mean+0.47pp,15/0/9. Relative to original Dot, overall mean remains−0.04pp.
- Both variants each have240 Full runs, preceded by a shared24-run Pilot matrix.
  Neither has a significant fixed-K direct improvement after its Holm24 family.
  Actor/GELU K3-versus-K1 relative-gain interaction pHolm18=0.03516 is distinct.
- No LN+GELU combined experiment was executed. These variants establish
  sensitivity to activation/normalization, not independent confirmation of a new architecture.

## I2 — scale-controlled agreement: PROPOSED, NOT_PILOTED

Motivation: observed score magnitude and softmax concentration vary by graph and
method. Proposal: compare a normalized cosine agreement or a pre-specified shared
temperature against Dot while holding all other settings fixed. They are alternative
subvariants; choose/freeze one before testing. Use equal validation budgets for
both arms, record score dispersion/entropy plus accuracy, check gradients and
cost. This is not the existing hidden-LN experiment. No code or results are claimed.
Teacher approval: NOT_VERIFIED.

## I3 — hop-level dropout regularization: PROPOSED, NOT_PILOTED

Motivation: high-hop branches may be noisy, and training–test gaps are large on
some graphs. Proposal: a pre-specified training-only branch-drop probability with
all hops restored at inference; include0-hop preservation as an explicit setting.
Compare method-matched controls under the same validation budget, at least3 seeds
per fixed split, node-mask isolation, and fixed inference graph. Measure generalization
and routing concentration without interpreting weights as causal contribution.
It requires a separate implementation/version; no pilot or improvement is claimed.
Teacher approval: NOT_VERIFIED.

## Fair follow-up protocol and necessary ablations

Proposed configs keep shared source, training and fixed masks unchanged. First run
the same split with seeds42/43/44 for Dot and MLP (6runs); then the frozen six-graph
K1–4/10split/3seed matrix (1,440runs) if approved and budgeted. Keep run-level results,
compare methods within each split/seed, report variation by both factors and
pre-specify multiplicity. Existing LN/GELU ablations have proposed three-seed pilot
config, not launched. A parameter-budget control and a strictly paper-style1..K
hop experiment need separate, approved versions; do not pool their results with0..K.

No expensive follow-up was started during repository initialization. Negative results
and all superseded resource records remain in the registry.

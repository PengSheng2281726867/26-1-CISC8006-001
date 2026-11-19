# Validation pilot report

Executed 2026-10-29 on existing K4/R2 Dot models: Chameleon/Actor, split0,
three optimization seeds each (six checkpoints,54 conditions). No training.
Original/new output and alpha maximum error0; true-label NLL identity and
single-node/global controls passed; all state hashes unchanged.

| Dataset | Mask | Pooled rho (seed mean) | Within-node rho mean | Top1 negative % | Undefined within-node % | Top1 tie % |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Actor | final_only | -0.0316 | -0.0423 | 50.57 | 30.92 | 31.03 |
| Actor | full_routing | -0.0257 | -0.0242 | 50.37 | 30.92 | 31.03 |
| Chameleon | final_only | 0.0558 | 0.0514 | 45.35 | 63.52 | 63.52 |
| Chameleon | full_routing | 0.0653 | 0.0526 | 46.01 | 63.52 | 63.52 |

There is no uniform positive alignment in these pilot observations. Top1 means
highest alpha among hops1..4;0-hop is excluded and ties choose the lowest hop.
A high tie/undefined fraction, especially Chameleon, limits rank interpretation;
constants are NA, never imputed0. Top1 negative uses fixed delta < -1e-5.
One split supplies no across-split SD or inferential significance. Three seeds
on a fixed split are reported separately in correlations.csv, not treated as
three datasets. All effects/signs retained; no threshold/configuration changed.

Full-routing yields larger mean Top1 loss changes than Final-only here, but this
does not establish a compensation mechanism. Reallocation, nonlinear fusion,
correlated branches and out-of-distribution masking are alternative explanations.
Full six-dataset/ten-split validation was launched with the same frozen settings,
reusing these six checkpoint results without rerunning them. Test labels have
not been used for new diagnostic metrics at this stage; historical checkpoint
reports contain earlier test results, so a pristine study holdout is not claimed.

Tables: results/pilot_val/. Figures: results/pilot_val/figures/.
Pilot results motivate completing the prespecified matrix, not selecting new
methods or claiming that GAMMA learned incorrectly. Teacher approval NOT_VERIFIED.

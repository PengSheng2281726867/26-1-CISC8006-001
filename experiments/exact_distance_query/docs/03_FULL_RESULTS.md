# Full results

Technical coverage: **720/720**, status **FULL**. Teacher approval **NOT_VERIFIED**.
All models were trained anew from matched random parameters. Counts include hash-verified reuse only.
Reused smoke=4, Pilot=48. Complete run manifests, raw paired cells and any missing units are in results/full/.

Accuracy percent: average seeds within each fixed split, then mean +/- sample SD across splits.

|Dataset|G0|G1|G2|G3|
|---|---:|---:|---:|---:|
|Texas|81.93 +/- 6.40|82.28 +/- 7.49|83.51 +/- 3.25|78.07 +/- 7.80|
|Wisconsin|84.38 +/- 2.19|82.75 +/- 3.23|85.03 +/- 3.51|79.22 +/- 6.94|
|Cornell|72.46 +/- 5.73|75.53 +/- 5.87|77.54 +/- 6.01|73.95 +/- 8.99|
|Chameleon|49.34 +/- 1.16|49.74 +/- 1.57|49.02 +/- 1.88|48.82 +/- 1.35|
|Squirrel|34.00 +/- 1.20|33.89 +/- 1.03|33.05 +/- 1.14|34.98 +/- 1.41|
|Actor|35.39 +/- 1.12|35.37 +/- 0.84|36.60 +/- 1.05|35.11 +/- 0.94|

Paired deltas in percentage points; seed means within split. Bootstrap CI is descriptive;
overlapping graph splits do not supply independent graph samples. Holm3 covers the three primary contrasts within dataset.

|Dataset|Contrast|Mean +/- SD pp|95% CI|Holm3 p|
|---|---|---:|---|---:|
|Texas|G1-G0|0.35 +/- 3.66|[-1.67, 2.54]|1.00|
|Texas|G2-G1|1.23 +/- 5.94|[-1.75, 5.09]|1.00|
|Texas|G3-G1|-4.21 +/- 3.22|[-6.14, -2.37]|0.02|
|Texas|G3-G2|-5.44 +/- 6.10|[-9.30, -2.19]|NA|
|Wisconsin|G1-G0|-1.63 +/- 2.56|[-3.14, -0.13]|0.25|
|Wisconsin|G2-G1|2.29 +/- 4.47|[-0.46, 4.84]|0.25|
|Wisconsin|G3-G1|-3.53 +/- 5.49|[-6.86, -0.52]|0.25|
|Wisconsin|G3-G2|-5.82 +/- 5.54|[-9.08, -2.68]|NA|
|Cornell|G1-G0|3.07 +/- 4.24|[0.61, 5.61]|0.19|
|Cornell|G2-G1|2.02 +/- 5.00|[-0.70, 5.18]|0.59|
|Cornell|G3-G1|-1.58 +/- 4.85|[-4.39, 1.32]|0.59|
|Cornell|G3-G2|-3.60 +/- 6.43|[-7.46, 0.09]|NA|
|Chameleon|G1-G0|0.40 +/- 0.98|[-0.12, 1.01]|0.27|
|Chameleon|G2-G1|-0.72 +/- 1.37|[-1.51, 0.10]|0.27|
|Chameleon|G3-G1|-0.93 +/- 1.00|[-1.54, -0.37]|0.04|
|Chameleon|G3-G2|-0.20 +/- 1.56|[-1.08, 0.73]|NA|
|Squirrel|G1-G0|-0.11 +/- 0.51|[-0.42, 0.19]|0.54|
|Squirrel|G2-G1|-0.84 +/- 1.02|[-1.43, -0.24]|0.09|
|Squirrel|G3-G1|1.09 +/- 1.24|[0.34, 1.77]|0.09|
|Squirrel|G3-G2|1.93 +/- 1.64|[0.95, 2.88]|NA|
|Actor|G1-G0|-0.03 +/- 0.58|[-0.36, 0.31]|0.89|
|Actor|G2-G1|1.24 +/- 0.70|[0.84, 1.65]|0.01|
|Actor|G3-G1|-0.26 +/- 0.48|[-0.52, 0.04]|0.27|
|Actor|G3-G2|-1.49 +/- 0.77|[-1.95, -1.05]|NA|

0 failed scientific attempts; 9 completed bounded empty-policy control cells.
Every completed G0 matched the frozen original forward, used_alpha and parameter gradients;
every completed G1 matched one-shot consensus including trained bias/Norm and empty-hop rules.
Every selected checkpoint was saved, hashed, reloaded and output-verified.

See resources.csv for measured training/inference/GPU allocation and operation counts;
distance_<dataset>.json separates one-time topology preprocessing/storage. G3 adds four Walk propagations;
parameter equality does not imply equal compute. Plots include all four groups and negative deltas.

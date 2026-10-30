# Pilot results

Technical coverage: **48/48**, status **FULL**. Teacher approval **NOT_VERIFIED**.
All models were trained anew from matched random parameters. Counts include hash-verified reuse only.
Reused smoke=0, Pilot=48. Complete run manifests, raw paired cells and any missing units are in results/pilot/.

Accuracy percent: average seeds within each fixed split, then mean +/- sample SD across splits.

|Dataset|G0|G1|G2|G3|
|---|---:|---:|---:|---:|
|Texas|NA|NA|NA|NA|
|Wisconsin|NA|NA|NA|NA|
|Cornell|NA|NA|NA|NA|
|Chameleon|49.60 +/- 1.60|51.21 +/- 2.84|48.79 +/- 3.26|49.67 +/- 0.67|
|Squirrel|NA|NA|NA|NA|
|Actor|34.59 +/- 0.05|34.86 +/- 0.23|35.58 +/- 0.33|34.61 +/- 0.43|

Paired deltas in percentage points; seed means within split. Bootstrap CI is descriptive;
overlapping graph splits do not supply independent graph samples. Holm3 covers the three primary contrasts within dataset.

|Dataset|Contrast|Mean +/- SD pp|95% CI|Holm3 p|
|---|---|---:|---|---:|
|Texas|G1-G0|NA|NA|NA|
|Texas|G2-G1|NA|NA|NA|
|Texas|G3-G1|NA|NA|NA|
|Texas|G3-G2|NA|NA|NA|
|Wisconsin|G1-G0|NA|NA|NA|
|Wisconsin|G2-G1|NA|NA|NA|
|Wisconsin|G3-G1|NA|NA|NA|
|Wisconsin|G3-G2|NA|NA|NA|
|Cornell|G1-G0|NA|NA|NA|
|Cornell|G2-G1|NA|NA|NA|
|Cornell|G3-G1|NA|NA|NA|
|Cornell|G3-G2|NA|NA|NA|
|Chameleon|G1-G0|1.61 +/- 1.24|[0.73, 2.49]|1.00|
|Chameleon|G2-G1|-2.41 +/- 0.41|[-2.70, -2.12]|1.00|
|Chameleon|G3-G1|-1.54 +/- 2.17|[-3.07, 0.00]|1.00|
|Chameleon|G3-G2|0.88 +/- 2.58|[-0.95, 2.70]|NA|
|Squirrel|G1-G0|NA|NA|NA|
|Squirrel|G2-G1|NA|NA|NA|
|Squirrel|G3-G1|NA|NA|NA|
|Squirrel|G3-G2|NA|NA|NA|
|Actor|G1-G0|0.26 +/- 0.28|[0.07, 0.46]|1.00|
|Actor|G2-G1|0.72 +/- 0.56|[0.33, 1.12]|1.00|
|Actor|G3-G1|-0.25 +/- 0.20|[-0.39, -0.11]|1.00|
|Actor|G3-G2|-0.98 +/- 0.76|[-1.51, -0.44]|NA|

0 failed scientific attempts; 0 completed bounded empty-policy control cells.
Every completed G0 matched the frozen original forward, used_alpha and parameter gradients;
every completed G1 matched one-shot consensus including trained bias/Norm and empty-hop rules.
Every selected checkpoint was saved, hashed, reloaded and output-verified.

See resources.csv for measured training/inference/GPU allocation and operation counts;
distance_<dataset>.json separates one-time topology preprocessing/storage. G3 adds four Walk propagations;
parameter equality does not imply equal compute. Plots include all four groups and negative deltas.

Resource review before Full: sparse construction and all four arms passed on both
graphs. No OOM, nonfinite gradients, checkpoint or parity failure. Largest Pilot
shell cache Actor:5.61M total NNZ,45.23MB archive,67.68MB CSR representation;
observed total harness allocation below0.45GiB. Full was started with the same
scientific fingerprint and unchanged protocol; no outcome-based tuning.
Chameleon G1-G0 +1.61pp; Actor +0.26pp. Three-seed/two-split uncertainty is large.

The smoke runner counterbalanced group order G2/G3/G0/G1 rather than the requested
G0-first chronology; original parity had already passed synthetic CPU/CUDA tests,
and real G0 parity passed before Pilot. This sequence deviation is disclosed;
no models or outcomes were excluded.

Plotting initially failed because the shared GAMMA environment lacks matplotlib.
No environment was changed: standalone plot.py runs in the existing plotting
environment, selected by GAMMA_PLOT_PYTHON. Analysis values were unaffected.

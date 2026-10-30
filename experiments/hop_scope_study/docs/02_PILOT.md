# Pilot results and decision

Recorded 2026-10-25T10:43:27.712384+00:00. 12/12 required Pilot cells complete; all successful checkpoints reloaded and independently checked.

| Dataset | x | n | Test accuracy %, mean +/- sample SD |
| --- | --- | --- | --- |
| Texas | 1 | 2 | 81.58 +/- 3.72 |
| Texas | 3 | 2 | 73.68 +/- 0.00 |
| Texas | 5 | 2 | 76.32 +/- 7.44 |
| Chameleon | 1 | 2 | 50.00 +/- 2.48 |
| Chameleon | 3 | 2 | 50.00 +/- 0.31 |
| Chameleon | 5 | 2 | 50.33 +/- 0.16 |

Pilot uses split0/1 only; these preliminary scores do not determine hyperparameters or remove datasets.

Texas: mean wall time 5.12s per run (range 3.65-7.23s).

Chameleon: mean wall time 4.41s per run (range 3.29-7.66s).

Pilot failures: 0. No OOM or nonfinite result is claimed unless present in the attempt ledger.

All matched cells share complete initialization hashes and graph/split/protocol/source fingerprints. The full500/50 protocol is retained. **GO to Full**: remaining288 cells plus all full-checkpoint diagnostics; reuse the12 verified Pilot cells without retraining. Throughput is hardware/runtime dependent; larger graphs may cost more than this Pilot. No scientific changes were made after Pilot.

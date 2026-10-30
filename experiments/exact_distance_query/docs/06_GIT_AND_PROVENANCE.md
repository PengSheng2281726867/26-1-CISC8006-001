# Git and provenance

Base main5e7eb902d32bda4665b5235582dc59eebf556178 was checked remotely before
branch creation. Local branch exp/exact-distance-query uses an external Git
metadata directory because nested .git ref writes are protected; the original
nested metadata is untouched. No main writes, history rewrite, force push or
course final tag. Original research and both prior experiments are byte-protected.

Pre-training audit/protocol/models/tests commit:
298719418e9f5d11e4115ae24b69ae2f278d6785. Pilot evidence/analysis commit:
bd605e2d5269290d5c7f22474300e7c5a5cf594d. All training-source hashes are the
same throughout Smoke/Pilot/Full; reporting files added later do not alter the
training fingerprint. Each run records the actual commit and dirty flag, not
a retrospective clean assertion. Phase matrix config files differ in selection
only; reused cells match the per-cell scientific config, source, protocol,
data/split, initial parameters/RNG and checkpoint hashes.

Private data/cache: <PRIVATE_DATA_ROOT>. Private logs/epochs/model.pt and metadata:
<PRIVATE_RUN_ROOT>/<run_id>/. Public run manifests contain scalar outcomes,
relative artifact names and cryptographic hashes, with no labels or node arrays.
Checkpoints were newly trained; original weights were never overwritten.
Dataset redistribution/fresh environment rebuild/human review/teacher approval
remain NOT_VERIFIED. User authorization does not establish teacher approval.

Smoke tests, all study tests, exact staged-index publication scans and changed
file reviews precede commits/pushes. Publication status will be recorded only
after actual remote-head and PR verification.

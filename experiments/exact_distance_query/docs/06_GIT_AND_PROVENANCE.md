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

## Verified publication

Scientific results commit `be66778841fa2596dda3f9503df1ef82d973e12f` was pushed
successfully to [exp/exact-distance-query](https://github.com/PengSheng2281726867/26-1-CISC8006-001/tree/exp/exact-distance-query).
git ls-remote confirmed the exact head and unchanged main. [PR3](https://github.com/PengSheng2281726867/26-1-CISC8006-001/pull/3)
is open, mergeable and unmerged, base main, head exp/exact-distance-query. The
GitHub connector independently verified both branch SHAs and PR state. No PR
merge or course tag was performed. This later provenance-only commit records
the verified scientific commit; it does not invent a self-referential head hash.

Immediately before scientific commit/push:13 legacy tests and16 study tests
passed,20 author-alignment cases passed, exact index publication scan passed
(409 files,0 findings). Protection checks found no historical changes outside
the three explicitly allowed navigation appendices. Full report, diagrams,
aggregate figures and hash-only artifact manifests are published. All729 private
weights/logs and raw graph data remain outside Git. Publication is not teacher
approval or evidence of human scientific review; both remain NOT_VERIFIED.

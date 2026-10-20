# Public repository publication review

Scope: this independent course repository only; the original research and its
data/checkpoints/logs are retained locally. No original file is deleted, moved or
silently edited. The model/factory/train copies are hash-locked to recovered files.

Allowlist: MIT author code and license; derivative research code; new course
harnesses; non-sensitive configs; derived metrics/figures; artifact/source checksums;
selected epoch logs; audited and explicitly uncertain research documentation.

Exclude: `.env`, secrets/tokens/credentials, home/drive paths, nested `.git`, graph
data/labels, split archives, predictions, checkpoints and the paper PDF. Dataset
redistribution permission is NOT_VERIFIED; no data license is inferred from MIT.
Large-file limit in the index checker is10MiB per file; current figures/metrics
are smaller. `outputs/`, `research/data/` and caches are ignored.

Before each commit run `python -B scripts/check_publication.py`. It reads actual
index blobs, checks forbidden paths/binaries/size and credential/private-path patterns,
and emits filenames/categories without printing matched secrets. The first audit
blocked absolute path dictionary keys in two derivative JSON files; only public
copies were sanitized and the rerun passed. A secret scan is a safeguard, not a
guarantee that every possible secret format is recognized. Human review remains
appropriate for public sharing, without inventing a completed review.

The frozen snapshot intentionally retains original whitespace and line endings;
a general whitespace diff check is noisy on those original bytes. It is not
"fixed" by changing scientific source. New harness/docs use LF and pass their
own syntax/evaluation checks. No global Git or environment settings were changed.

# Source and publication notice

GAMMA: Gated Multi-hop Message Passing for Homophily-Agnostic Node Representation
in GNNs, Amir Ghazizadeh, Rickard Ewetz, Hao Zheng, NeurIPS 2025.

- Official source: https://github.com/amir-ghz/GAMMA
- Frozen upstream commit: `36d054b4ae53c0c8e360d85d056f5207d61c8281`.
- `research/upstream_snapshot/` is the seven-file author snapshot, including its
  MIT license. Its bytes and hashes are preserved.
- `research/src/` is the independently implemented source-faithful reproduction
  and existing MLP extension. It is derived from the MIT-licensed GAMMA design
  and code. `research/ablation_mlp/` contains the existing independent LN/GELU
  single-factor variants. These are imported together; no prior Git chronology
  is claimed. Source-to-destination hashes are in `experiments/source_mapping.json`.
- `research/tests/test_baseline.py` is the existing independent alignment test.
- `LICENSE` preserves the original authors' copyright and MIT notice. Course
  recovery documentation and harnesses identify their actual creation in Git
  and AI_USAGE.md; no historical human contribution or authorship is inferred.
- Dataset files, graph labels, splits, model weights, raw predictions and private
  credentials are excluded. Dataset redistribution permission is NOT_VERIFIED;
  obtain each benchmark from its upstream through PyG. Publishing author code
  under MIT does not license the datasets or the paper PDF.
- Public evidence consists of derived metrics, checksums, selected epoch traces,
  source/configuration metadata and experiment figures. Originals remain outside
  this course repository. Absolute local paths are redacted in derivative records;
  original historical files have not been edited.


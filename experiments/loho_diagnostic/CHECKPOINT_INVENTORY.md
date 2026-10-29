# Checkpoint inventory

Actual existing files only: [machine-readable inventory](results/checkpoint_inventory.csv).
Discovery under original owner artifact root:5,421 model.pt files;1,284 contain
`/dot/` in their relative path, which alone is not proof of a valid Dot model.
Primary cohort:180 stability_v1/core K4/R2 checkpoints, powers0..4, one actual
GAMMA layer, seeds2026/2027/2028, six datasets x ten splits. All passed strict
loading plus state/artifact/graph/split hash verification. Inventory records
SHA256, config, graph/split identifiers and relative owner artifact locations.
60 historical v2 K4 Dot weights passed strict CPU load and state/file checks;
marked LOADABLE_NOT_PRIMARY because primary graph provenance is stronger.
They are excluded from primary statistics. Missing checkpoint files are never
represented as zero-effect results. All180 primary cells are available.

Prior hop workspace was separately inspected read-only: it contains models from
a variable gating-hop study (including propagation5/gating1). Those intervention
semantics differ and were excluded, even when filenames are model.pt. Remote
main has no weights; recovered artifact manifests supply checksums and provenance,
not public download rights. Existing registry and historical records were not
modified. Raw artifacts remain on the owner-authorized local machine, outside
public Git. No anonymous public access is implied.

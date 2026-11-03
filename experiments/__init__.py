"""Stable Python module names for studies stored in numbered topic folders.

For example, ``experiments.loho_diagnostic`` resolves to the actual study under
``03_hop_diagnostics``. Extending the package search path keeps public module
commands and cross-study imports working without duplicate source or symlinks.
"""
from pathlib import Path

_root = Path(__file__).resolve().parent
for _group in (
    '01_reproduction',
    '02_scorer_ablation',
    '03_hop_diagnostics',
    '04_distance_query',
):
    __path__.append(str(_root / _group))
del _root, _group

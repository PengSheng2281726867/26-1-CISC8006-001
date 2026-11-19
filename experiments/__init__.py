"""Stable module names for the baseline, three experiments and supplement."""
from pathlib import Path

_root = Path(__file__).resolve().parent
for _group in ('00_baseline', '01_scorer', '02_hop_scope', '03_distance_query', 'supplementary'):
    __path__.append(str(_root / _group))
del _root, _group

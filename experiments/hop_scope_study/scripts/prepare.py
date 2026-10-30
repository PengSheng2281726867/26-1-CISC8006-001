from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.common import external, STUDY, save
from src.data import prepare
import argparse
p=argparse.ArgumentParser()
p.add_argument('--data-root',type=Path,required=True)
p.add_argument('--import-from',type=Path)
p.add_argument('--check-only',action='store_true')
a=p.parse_args()
manifest=prepare(a.data_root,a.import_from,a.check_only)
if not a.check_only:
    save(STUDY/'results/data_verification.json',manifest)

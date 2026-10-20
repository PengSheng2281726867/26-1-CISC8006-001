"""Recompute saved-prediction accuracy or summarize recovered run fractions."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from course.common import ROOT,save
from course.metrics import accuracy,aggregate
import argparse
import collections
import csv
import json


def main():
    p=argparse.ArgumentParser()
    inputs=p.add_mutually_exclusive_group(required=True)
    inputs.add_argument('--predictions',type=Path)
    inputs.add_argument('--registry',type=Path)
    p.add_argument('--stage',default='dot_mlp')
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    if args.predictions:
        import numpy as np
        with np.load(args.predictions,allow_pickle=False) as data:
            ids=np.arange(len(data['labels']))
            result=accuracy(data['predictions'],data['labels'],data['test_mask'],ids,ids)
    else:
        groups=collections.defaultdict(list)
        with args.registry.open(encoding='utf-8',newline='') as f:
            for row in csv.DictReader(f):
                if row['stage']==args.stage:
                    groups[row['dataset'],int(row['k']),row['method']].append(float(row['test_accuracy']))
        if not groups: raise ValueError('No records for requested stage.')
        result=dict(stage=args.stage,groups=[dict(dataset=d,k=k,method=m,**aggregate(v))
                    for (d,k,m),v in sorted(groups.items())])
    if args.output:
        target=args.output.resolve()
        if not target.is_relative_to((ROOT/'outputs').resolve()):
            raise ValueError('Evaluation outputs must stay in the ignored outputs/ directory.')
        if target.exists(): raise FileExistsError('Refusing to overwrite prior evaluation output.')
        save(target,result)
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()

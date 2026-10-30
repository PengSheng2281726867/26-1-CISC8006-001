"""Supplementary descriptive diagnostics; run in the plotting environment."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
STUDY=Path(__file__).resolve().parents[1]
DATASETS=('Texas','Wisconsin','Cornell','Chameleon','Squirrel','Actor')
GROUPS=('G0','G1','G2','G3')
def main():
    out=STUDY/'results/full';summary=json.loads((out/'dedicated_summary.json').read_text())
    distances={d:json.loads((STUDY/'results'/('distance_'+d+'.json')).read_text()) for d in DATASETS}
    fig,axes=plt.subplots(2,2,figsize=(12,8),dpi=150)
    for d in DATASETS:
        s=distances[d]['shells']
        axes[0,0].plot(range(1,5),[r['empty_fraction'] for r in s[1:]],'-o',ms=3,label=d)
        axes[0,1].plot(range(1,5),[r['nnz'] for r in s[1:]],'-o',ms=3,label=d)
    axes[0,0].set(xlabel='Exact hop',ylabel='Fraction without upstream nodes',ylim=(0,1),title='Directed topology; primary mask eligibility')
    axes[0,0].legend(fontsize=8,ncol=2)
    axes[0,1].set(xlabel='Exact hop',ylabel='NNZ (log scale)',yscale='log',title='Binary shell sizes; not Walk counts')
    for j,g in enumerate(GROUPS):
        rs=[next(r for r in summary if r['dataset']==d and r['group']==g) for d in DATASETS]
        x=np.arange(6)+(j-1.5)*.18
        axes[1,0].bar(x,[r['normalized_entropy_mean'] for r in rs],width=.18,label=g)
        axes[1,1].bar(x,[r['query_norm_mean'] for r in rs],width=.18,label=g)
    for ax in axes[1]:ax.set_xticks(range(6),DATASETS,rotation=25);ax.legend(fontsize=8,ncol=2)
    axes[1,0].set(ylabel='Entropy / log(eligible hop count)',title='Supplementary normalized gate entropy')
    axes[1,1].set(ylabel='Mean query L2 norm',title='Query function changes scale as well as source')
    fig.tight_layout();fig.savefig(out/'empty_size_entropy_query.png');plt.close(fig)
    fig,axes=plt.subplots(2,3,figsize=(11,6),dpi=150)
    for ax,d in zip(axes.flat,DATASETS):
        rs=[r for r in summary if r['dataset']==d]
        ax.bar([r['group'] for r in rs],[r['inference_ms_mean'] for r in rs],color=['#3a5e8c','#d27b26','#3e9470','#9b5ba5'])
        ax.set(title=d,ylabel='Inference ms,20 synchronized repeats')
    fig.suptitle('Dedicated serial inference after training:30 checkpoints per group/dataset')
    fig.tight_layout();fig.savefig(out/'dedicated_inference.png');plt.close(fig)
if __name__=='__main__':main()

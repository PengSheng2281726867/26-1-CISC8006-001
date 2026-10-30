from pathlib import Path
import json
import numpy as np
GROUPS=('G0','G1','G2','G3')
DATASETS=('Texas','Wisconsin','Cornell','Chameleon','Squirrel','Actor')
def mean(v): return float(np.mean(v)) if v else None
def plot(out,accuracy,paired,resources,gates,mechanisms):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':9,'figure.dpi':150})
    colors=['#3a5e8c','#d27b26','#3e9470','#9b5ba5']
    fig,axes=plt.subplots(2,3,figsize=(11,6));
    for ax,d in zip(axes.flat,DATASETS):
        rs=[r for r in accuracy if r['dataset']==d and r['cells']]
        ax.bar([r['group'] for r in rs],[r['mean_percent'] for r in rs],yerr=[r['sample_sd_percent'] or 0 for r in rs],color=colors[:len(rs)],capsize=3)
        ax.set_title(d);ax.set_ylabel('Test accuracy (%)');ax.set_ylim(0,100)
        if not rs:ax.text(.5,.5,'Not in Pilot',transform=ax.transAxes,ha='center')
    fig.suptitle('Seed means within split, then mean +/- split sample SD');fig.tight_layout();fig.savefig(out/'accuracy.png');plt.close(fig)
    fig,axes=plt.subplots(2,3,figsize=(11,6))
    for ax,d in zip(axes.flat,DATASETS):
        ax.axvline(0,color='gray',lw=1)
        rs=[r for r in paired if r['dataset']==d and r['paired_cells']]
        for i,r in enumerate(rs):
            if r['ci95_low'] is not None:ax.plot([r['ci95_low'],r['ci95_high']],[i,i],color=colors[i])
            ax.scatter(r['split_means'],[i]*len(r['split_means']),color=colors[i],alpha=.35,s=10)
            ax.scatter([r['mean_pp']],[i],color=colors[i],marker='D',s=25)
        ax.set_yticks(range(len(rs)),[r['contrast'] for r in rs]);ax.set_title(d);ax.set_xlabel('Paired delta (pp), descriptive bootstrap95% CI')
    fig.tight_layout();fig.savefig(out/'paired_deltas.png');plt.close(fig)
    fig,axes=plt.subplots(2,3,figsize=(11,6))
    for ax,d in zip(axes.flat,DATASETS):
        for g,c in zip(GROUPS,colors):
            rs=[r for r in gates if r['dataset']==d and r['group']==g]
            if rs:ax.plot([r['p'] for r in rs],[r['alpha_mean'] for r in rs],'-o',label=g,color=c,ms=3)
        ax.set_title(d);ax.set_xlabel('Candidate hop');ax.set_ylabel('Mean used_alpha');ax.set_ylim(0,1)
    axes[1,0].legend(ncol=2);fig.tight_layout();fig.savefig(out/'gates.png');plt.close(fig)
    fig,axes=plt.subplots(2,3,figsize=(11,6))
    for ax,d in zip(axes.flat,DATASETS):
        rs=[r for r in resources if r['dataset']==d]
        ax.bar([r['group'] for r in rs],[r['inference_ms_mean'] for r in rs],color=colors[:len(rs)]);ax.set_title(d);ax.set_ylabel('Inference (ms),20 synchronized repeats')
    fig.tight_layout();fig.savefig(out/'inference_cost.png');plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(12,3.5))
    for ax,key in zip(axes,['cosine_raw','cosine_gamma_scaled','cosine_layernorm']):
        matrix=[]
        for d in DATASETS:
            matrix.append([mean([mean([v['mean'] for v in r[key] if v['mean'] is not None]) for r in mechanisms if r['dataset']==d and r['group']==g]) for g in GROUPS])
        arr=np.array([[np.nan if v is None else v for v in row] for row in matrix]);im=ax.imshow(arr,vmin=-1,vmax=1,cmap='coolwarm')
        ax.set_xticks(range(4),GROUPS);ax.set_yticks(range(6),DATASETS);ax.set_title(key.replace('cosine_',''))
    fig.colorbar(im,ax=axes.ravel().tolist(),shrink=.7,label='Valid-pair mean cross-hop cosine');fig.savefig(out/'hop_similarity.png',bbox_inches='tight');plt.close(fig)

if __name__=='__main__':
 import sys
 out=Path(sys.argv[1]); a=json.loads((out/'analysis.json').read_text()); m=json.loads((out/'mechanisms.json').read_text()); plot(out,a['accuracy'],a['paired'],a['resources'],a['gate'],m)

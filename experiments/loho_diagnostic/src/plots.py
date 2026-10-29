"""Publication figures from private real arrays; matplotlib runs separately."""
import argparse
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .summarize import collect
from .statistics import rho

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',action='append',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
    from pathlib import Path
    out=Path(args.output)
    if out.exists(): raise ValueError('Refuse to overwrite figures')
    out.mkdir(parents=True)
    cells,missing,failed=collect(args.input)
    if missing or failed: raise ValueError('Incomplete cells')
    for dataset,ev in sorted({(k[0],k[3]) for k in cells}):
        chosen=[(k,v) for k,v in sorted(cells.items()) if k[0]==dataset and k[3]==ev]
        al=[];ds={m:[] for m in ('final_only','full_routing')};rhos={m:[] for m in ds};top={m:[] for m in ds}
        for k,(path,meta) in chosen:
            with np.load(path.with_name('nodes.npz')) as z:
                a=z['alpha_used_full'][:,1:];al.append(a)
                for m in ds:
                    d=z[m+'_delta_loss'];ds[m].append(d);rhos[m].append((k[1],rho(a,d)[0]));top[m].append(d[np.arange(len(d)),a.argmax(1)])
        a=np.concatenate(al);ds={m:np.concatenate(v) for m,v in ds.items()}
        ns=len({k[2] for k,_ in chosen});nc=len(chosen)
        title=f'{dataset} | K=4 R=2 | {ev} | seeds={ns} checkpoints={nc}'
        prefix=f'{dataset.lower()}_{ev}'
        def finish(fig,name):
            fig.suptitle(title+'\nFinal-only / Full-routing',fontsize=11);fig.tight_layout(rect=(0,0,1,.91));fig.savefig(out/(prefix+'_'+name+'.png'),dpi=150);plt.close(fig)
        fig,axes=plt.subplots(1,2,figsize=(10,4.6))
        rng=np.random.default_rng(102)
        flat=a.ravel();idx=rng.choice(len(flat),min(5000,len(flat)),replace=False)
        for ax,(m,d) in zip(axes,ds.items()):
            ax.scatter(flat[idx],d.ravel()[idx],s=4,alpha=.2,rasterized=True);ax.axhline(0,color='black',lw=.7);ax.set(xlabel='alpha used (nonzero hops)',ylabel='NLL(masked) - NLL(full)',title=m)
        finish(fig,'scatter')
        fig,axes=plt.subplots(1,2,figsize=(10,4.6))
        for ax,(m,d) in zip(axes,ds.items()):
            ax.bar(np.arange(1,5)-.16,a.mean(0),width=.32,label='mean alpha',color='steelblue');ax.set(xlabel='removed hop',ylabel='mean alpha',title=m,xticks=range(1,5));ax2=ax.twinx();ax2.plot(range(1,5),d.mean(0),'o-',color='darkred');ax2.axhline(0,color='darkred',lw=.5);ax2.set_ylabel('mean delta NLL',color='darkred')
        finish(fig,'hop_means')
        fig,axes=plt.subplots(1,2,figsize=(10,4.6))
        for ax,(m,vs) in zip(axes,top.items()):
            d=np.concatenate(vs);ax.hist(d,bins=55,color='steelblue',alpha=.8);ax.axvline(0,color='black',lw=.7);ax.set(xlabel='Top1 nonzero-hop delta NLL',ylabel='node observations (dependent)',title=m+f' | negative={100*(d < -1e-5).mean():.1f}%')
        finish(fig,'top1')
        fig,ax=plt.subplots(figsize=(8,4.6));diff=ds['full_routing']-ds['final_only'];ax.boxplot([diff[:,j] for j in range(4)],showfliers=False);ax.axhline(0,color='black',lw=.7);ax.set(xlabel='removed hop',ylabel='delta(full-routing) - delta(final-only)');finish(fig,'paired')
        if len({k[1] for k,_ in chosen})>1:
            fig,ax=plt.subplots(figsize=(8,4.6))
            for m,vs in rhos.items():
                sp=sorted({s for s,r in vs});mean=[];sd=[]
                for s in sp:
                    vals=[r for s2,r in vs if s2==s and r is not None];mean.append(np.mean(vals));sd.append(np.std(vals,ddof=1) if len(vals)>1 else 0)
                ax.errorbar(sp,mean,yerr=sd,fmt='o-',capsize=3,label=m)
            ax.axhline(0,color='black',lw=.7);ax.set(xlabel='split ID (bars = within-split seed SD)',ylabel='pooled descriptive Spearman');ax.legend();finish(fig,'split_rho')
    print('figures:',len(list(out.glob('*.png'))))
if __name__=='__main__':main()

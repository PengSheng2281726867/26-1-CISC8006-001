"""Export static, shareable research figures from scalar analysis evidence."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.common import STUDY,read
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
analysis=read(STUDY/'results/analysis.json');names=['Texas','Wisconsin','Cornell','Chameleon','Squirrel','Actor']
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
for kind,filename in [('accuracy','accuracy_vs_x'),('delta','paired_delta'),('protocol','posthoc_vs_retrain')]:
    fig,axes=plt.subplots(2,3,figsize=(12,7),constrained_layout=True)
    for ax,name in zip(axes.flat,names):
        rows=analysis['paired_delta'] if kind=='delta' else [r for r in analysis['accuracy'] if r['metric']=='test']
        rows=sorted([r for r in rows if r['dataset']==name and r['n']],key=lambda r:r['x'])
        if rows:
            xs=[r['x'] for r in rows];ys=[r['mean'] for r in rows];sd=[r['sample_sd'] or 0 for r in rows]
            ax.errorbar(xs,ys,yerr=sd,marker='o',capsize=3,label='Retrain',color='#126c9c')
        if kind=='protocol':
            rows=sorted([r for r in analysis['posthoc'] if r['dataset']==name and r['n']],key=lambda r:r['x'])
            if rows:ax.errorbar([r['x'] for r in rows],[r['mean'] for r in rows],yerr=[r['sample_sd'] or 0 for r in rows],
                               marker='s',capsize=3,label='Post-hoc (frozen x5)',color='#ca6b19')
        if kind=='delta':ax.axhline(0,color='gray',lw=.8)
        n=min([r['n'] for r in rows]) if rows else 0
        ax.set(title=f'{name} (n={n} splits)',xlabel='Maximum routing hop x (always includes 0)',
               ylabel='Paired test delta vs x=5 (pp)' if kind=='delta' else 'Test accuracy (%)',xticks=range(1,6))
        ax.grid(alpha=.15)
        if kind=='protocol' and name=='Texas':ax.legend(fontsize=8)
    state=analysis['status'];fig.suptitle(f"Fixed propagation K_max=5 | {state['status']}: {state['primary_complete']}/300 primary cells | Error bars: sample SD")
    fig.savefig(STUDY/'figures'/f'{filename}.png',dpi=170);plt.close(fig)
print('Exported three research figures')

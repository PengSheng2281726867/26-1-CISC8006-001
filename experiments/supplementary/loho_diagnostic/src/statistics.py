"""Descriptive statistics: no independent-node significance claims."""
import numpy as np
from scipy.stats import rankdata

def rho(x,y):
    x=np.asarray(x,dtype=float).ravel();y=np.asarray(y,dtype=float).ravel()
    if len(x)!=len(y) or len(x)<2: return None,'insufficient_pairs'
    if not np.isfinite(x).all() or not np.isfinite(y).all(): return None,'nonfinite'
    if np.ptp(x)==0 or np.ptp(y)==0: return None,'constant_vector'
    return float(np.corrcoef(rankdata(x),rankdata(y))[0,1]),''

def fractions(delta,eps=1e-5):
    d=np.asarray(delta)
    if not np.isfinite(d).all() or not d.size: raise ValueError('Invalid effects')
    return dict(positive_fraction=float((d>eps).mean()),negative_fraction=float((d < -eps).mean()),near_zero_fraction=float((np.abs(d)<=eps).mean()))

def stats(arr,mask,eps=1e-5):
    a=arr['alpha_used_full'][:,1:];d=arr[mask+'_delta_loss'];pred=arr[mask+'_pred_masked'];cor=arr[mask+'_correct_masked']
    within=[rho(x,y)[0] for x,y in zip(a,d)];valid=[x for x in within if x is not None]
    top=np.argmax(a,axis=1);td=d[np.arange(len(d)),top]
    overall,reason=rho(a,d)
    shared=dict(overall_rho=overall,overall_rho_reason=reason,within_mean=float(np.mean(valid)) if valid else None,within_median=float(np.median(valid)) if valid else None,within_valid=len(valid),within_undefined_fraction=1-len(valid)/len(within),top1_mean_delta=float(td.mean()),top1_median_delta=float(np.median(td)),top1_tie_fraction=float(((a==a.max(1,keepdims=True)).sum(1)>1).mean()),**{'top1_'+k:v for k,v in fractions(td,eps).items()})
    rows=[]
    for j in range(4):
        rr,why=rho(a[:,j],d[:,j])
        rows.append(dict(hop=j+1,mean_alpha=float(a[:,j].mean()),mean_delta=float(d[:,j].mean()),median_delta=float(np.median(d[:,j])),rho=rr,rho_reason=why,accuracy_full=float(arr['correct_full'].mean()),accuracy_masked=float(cor[:,j].mean()),accuracy_change=float(cor[:,j].mean()-arr['correct_full'].mean()),nll_full=float(arr['loss_full'].mean()),nll_masked=float(arr[mask+'_loss_masked'][:,j].mean()),flip_fraction=float((pred[:,j]!=arr['pred_full']).mean()),**fractions(d[:,j],eps)))
    return shared,rows

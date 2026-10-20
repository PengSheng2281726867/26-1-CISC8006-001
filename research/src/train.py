"""Common, validation-selected training and measurement for both scorers."""
from .paths import ROOT,save_json,sha256,tensor_hash
import copy
import csv
import json
import math
from pathlib import Path
import time

import numpy as np
import torch

def synchronize(device):
    if torch.device(device).type=='cuda': torch.cuda.synchronize(device)

def scorer_norm(model):
    values=[p.grad.reshape(-1) for name,p in model.named_parameters() if '.scorer.' in name and p.grad is not None]
    return float(torch.linalg.vector_norm(torch.cat(values))) if values else 0.0

def train_model(model,graph,config,trace_path=None):
    device=graph.x.device
    optimizer=torch.optim.Adam(model.parameters(),lr=config['learning_rate'],weight_decay=config['weight_decay'])
    scheduler=torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer,mode='max',**config['scheduler'])
    criterion=torch.nn.CrossEntropyLoss()
    best=-math.inf;best_epoch=0;best_state=None;stale=0
    history=[];first_scorer_grad=0.0
    handle=Path(trace_path).open('w',newline='',encoding='utf-8') if trace_path else None
    columns=['epoch','train_loss','val_correct','val_size','val_accuracy','train_step_ms','validation_ms',
             'epoch_wall_ms','learning_rate','gradient_norm_before_clip','improved']
    writer=csv.DictWriter(handle,fieldnames=columns) if handle else None
    if writer: writer.writeheader()
    start=time.perf_counter()
    try:
        for epoch in range(1,config['epochs']+1):
            synchronize(device);epoch_start=time.perf_counter()
            model.train();optimizer.zero_grad()
            out=model(graph.x,graph.edge_index)
            loss=criterion(out[graph.train_mask],graph.y[graph.train_mask])
            if not bool(torch.isfinite(loss)): raise FloatingPointError(f'nonfinite loss at epoch {epoch}')
            loss.backward()
            grad_norm=torch.nn.utils.clip_grad_norm_(model.parameters(),config['gradient_clip'],error_if_nonfinite=True)
            optimizer.step()
            synchronize(device);train_ms=1000*(time.perf_counter()-epoch_start)
            if epoch==1: first_scorer_grad=scorer_norm(model)
            model.eval();synchronize(device);validation_start=time.perf_counter()
            with torch.no_grad():
                pred=model(graph.x,graph.edge_index).argmax(dim=1)
                correct=int((pred[graph.val_mask]==graph.y[graph.val_mask]).sum())
                val_size=int(graph.val_mask.sum());val=correct/val_size
            synchronize(device);validation_ms=1000*(time.perf_counter()-validation_start)
            scheduler.step(val)
            improved=val>best
            if improved:
                best=val;best_epoch=epoch;stale=0
                best_state=copy.deepcopy(model.state_dict())
            else: stale+=1
            row=dict(epoch=epoch,train_loss=float(loss.detach()),val_correct=correct,val_size=val_size,val_accuracy=val,
                     train_step_ms=train_ms,validation_ms=validation_ms,epoch_wall_ms=1000*(time.perf_counter()-epoch_start),
                     learning_rate=optimizer.param_groups[0]['lr'],gradient_norm_before_clip=float(grad_norm),improved=int(improved))
            history.append(row)
            if writer: writer.writerow(row);handle.flush()
            if stale>=config['early_stopping_patience']: break
    finally:
        if handle: handle.close()
    assert best_state is not None
    model.load_state_dict(best_state)
    return dict(best_validation_accuracy=best,best_validation_epoch=best_epoch,stopped_epoch=epoch,
                train_loss_at_best=history[best_epoch-1]['train_loss'],last_train_loss=history[-1]['train_loss'],
                epoch_training_ms_mean=float(np.mean([row['train_step_ms'] for row in history])),
                epoch_wall_ms_mean=float(np.mean([row['epoch_wall_ms'] for row in history])),
                training_seconds=time.perf_counter()-start,scorer_gradient_norm_first=first_scorer_grad,history=history)

def inference_benchmark(model,graph,warmup=5,repeats=20):
    model.eval();times=[];device=graph.x.device
    with torch.no_grad():
        for _ in range(warmup): model(graph.x,graph.edge_index)
        synchronize(device)
        for _ in range(repeats):
            synchronize(device);start=time.perf_counter()
            model(graph.x,graph.edge_index)
            synchronize(device);times.append((time.perf_counter()-start)*1000)
    return dict(inference_ms_mean=float(np.mean(times)),inference_ms_std=float(np.std(times)),
                inference_ms_median=float(np.median(times)),inference_repeats=repeats)

def mechanism_metrics(details):
    layer=details[0]
    alpha=layer['used_alpha'].cpu().numpy()
    scores=layer['iterations'][0]['agreement'].cpu().numpy()
    hops=layer['hops'].cpu().numpy()
    entropy=-(alpha*np.log(np.clip(alpha,1e-30,None))).sum(axis=1)
    normed=hops/np.maximum(np.linalg.norm(hops,axis=-1,keepdims=True),1e-8)
    rng=np.random.default_rng(102)
    first=rng.integers(0,len(hops),size=min(2000,len(hops)*2))
    second=rng.integers(0,len(hops),size=len(first))
    node_cosine=(normed[first]*normed[second]).sum(axis=-1).mean(axis=0)
    pair_cosines=[]
    for left in range(hops.shape[1]):
        for right in range(left+1,hops.shape[1]):
            pair_cosines.append(float((normed[:,left]*normed[:,right]).sum(-1).mean()))
    centered=scores-scores.mean(axis=1,keepdims=True)
    return dict(hop_weights_mean=alpha.mean(axis=0).tolist(),hop_weights_std=alpha.std(axis=0).tolist(),
                hop_weights_quantiles=np.quantile(alpha,[0,.25,.5,.75,1],axis=0).tolist(),
                gating_entropy_mean=float(entropy.mean()),gating_entropy_std=float(entropy.std()),
                gating_entropy_normalized=float(entropy.mean()/np.log(alpha.shape[1])),
                max_weight_over_095_fraction=float((alpha.max(axis=1)>.95).mean()),
                score_mean=float(scores.mean()),score_std=float(scores.std()),score_min=float(scores.min()),score_max=float(scores.max()),
                centered_score_std=float(centered.std()),node_cosine_by_hop=node_cosine.tolist(),
                mean_cross_hop_cosine=float(np.mean(pair_cosines)))

def run_one(model,graph,config,meta,output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    initial_scorer={name:p.detach().cpu().clone() for name,p in model.named_parameters() if '.scorer.' in name}
    device=graph.x.device
    if device.type=='cuda':
        torch.cuda.reset_peak_memory_stats(device)
        base_memory=torch.cuda.memory_allocated(device)
    else: base_memory=0
    training=train_model(model,graph,config,output/'epochs.csv')
    peak=torch.cuda.max_memory_allocated(device) if device.type=='cuda' else 0
    reserved=torch.cuda.max_memory_reserved(device) if device.type=='cuda' else 0
    model.eval()
    with torch.no_grad():
        logits,details=model(graph.x,graph.edge_index,return_diagnostics=True)
        if not bool(torch.isfinite(logits).all()): raise FloatingPointError('nonfinite evaluation logits')
        pred=logits.argmax(dim=1)
        accuracies={}
        for label in ('train','val','test'):
            mask=graph[f'{label}_mask'];correct=int((pred[mask]==graph.y[mask]).sum());size=int(mask.sum())
            accuracies.update({f'{label}_accuracy':correct/size,f'{label}_correct':correct,f'{label}_size':size})
        assert accuracies['val_accuracy']==training['best_validation_accuracy']
        mechanism=mechanism_metrics(details)
        arrays=dict(predictions=pred.cpu().numpy(),log_probs=logits.cpu().numpy(),labels=graph.y.cpu().numpy(),
                    alpha=details[0]['used_alpha'].cpu().numpy(),first_agreement=details[0]['iterations'][0]['agreement'].cpu().numpy())
        for label in ('train','val','test'): arrays[f'{label}_mask']=graph[f'{label}_mask'].cpu().numpy()
    benchmark=inference_benchmark(model,graph,config['infer_warmup'],config['infer_repeats'])
    state={name:value.detach().cpu().clone() for name,value in model.state_dict().items()}
    change=sum(float(((state[name]-value)**2).sum()) for name,value in initial_scorer.items())**.5
    report={**meta,**{key:value for key,value in training.items() if key!='history'},**accuracies,**benchmark,**mechanism,
            'parameter_count':sum(p.numel() for p in model.parameters()),
            'scorer_parameter_count':sum(p.numel() for name,p in model.named_parameters() if '.scorer.' in name),
            'scorer_parameter_change_l2':change,'peak_gpu_allocated_mb':peak/1024**2,
            'peak_gpu_reserved_mb':reserved/1024**2,'initial_gpu_allocated_mb':base_memory/1024**2,
            'peak_training_increment_mb':(peak-base_memory)/1024**2,'trained_state_sha256':tensor_hash(state)}
    torch.save(dict(state_dict=state,model_kwargs=meta['model_kwargs'],report=report),output/'model.pt')
    np.savez_compressed(output/'predictions.npz',**arrays)
    report['artifacts']={name:sha256(output/name) for name in ('model.pt','predictions.npz','epochs.csv')}
    report['status']='complete'
    save_json(output/'result.json',report)
    return report

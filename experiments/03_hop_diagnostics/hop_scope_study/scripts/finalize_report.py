"""Write interpretation using actual complete results, without selecting x by test."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.common import STUDY,REPO,read,save,sha,digest,now
import collections
import json
analysis=read(STUDY/'results/analysis.json');status=analysis['status']
if status['primary_complete']!=300 or status['posthoc_evaluations']!=300:
    raise RuntimeError('Final interpretation requires the complete registered matrix and diagnostics')
records=[json.loads(line) for line in (STUDY/'results/per_run.jsonl').read_text().splitlines()]
source_bundles={digest(r['source_sha256']) for r in records}
if len(source_bundles)!=1:raise ValueError('Multiple scientific source versions; adjudicate before pooling')
summary=analysis['accuracy'];names=['Texas','Wisconsin','Cornell','Chameleon','Squirrel','Actor']
val_best={};nonmonotone=[];selected={}
for name in names:
    val=[r for r in summary if r['dataset']==name and r['metric']=='val']
    totals={x:sum(r['val_correct'] for r in records if r['dataset']==name and r['max_gating_hop']==x) for x in range(1,6)}
    val_best[name]=min(totals,key=lambda x:(-totals[x],x))
    curve=sorted([r for r in summary if r['dataset']==name and r['metric']=='test'],key=lambda r:r['x'])
    if any(b['mean']<a['mean']-1e-12 for a,b in zip(curve,curve[1:])):nonmonotone.append(name)
    selected[name]=dict(sorted(collections.Counter(r['x_star'] for r in analysis['selection'] if r['dataset']==name).items()))
contrasts=[r for r in analysis['paired_delta'] if r['x']<5]
significant=[r for r in contrasts if r['p_holm']<.05]
positive=max(contrasts,key=lambda r:r['mean']);negative=min(contrasts,key=lambda r:r['mean'])
posthoc=[r for r in analysis['posthoc_minus_retrain'] if r['x']<5]
example=max(posthoc,key=lambda r:abs(r['mean']))
hypotheses=dict(utc=now(),primary_complete=300,posthoc_evaluations=300,
                h1_nonmonotone_mean_test_datasets=nonmonotone,
                h2_validation_best_mean_x=val_best,validation_selected_x_counts=selected,
                holm_within_dataset_below_005=significant,
                exploratory_largest_positive_delta=positive,exploratory_largest_negative_delta=negative,
                exploratory_largest_posthoc_retrain_gap=example)
save(STUDY/'results/hypotheses_summary.json',hypotheses)
save(STUDY/'results/source_provenance.json',dict(base_main_sha='935a4303ed0d1410e29d9374cc1ce91b82dc527c',
     upstream_sha='36d054b4ae53c0c8e360d85d056f5207d61c8281',scientific_source_bundle_sha256=next(iter(source_bundles)),
     scientific_sources=records[0]['source_sha256'],
     analysis_and_acceptance_sources={p.relative_to(REPO).as_posix():sha(p) for folder in ('scripts','tests') for p in (STUDY/folder).glob('*.py')},
     protocol_sha256=records[0]['protocol_sha256'],execution_git_commits=sorted({r['git']['commit'] for r in records}),
     all_executions_truthfully_dirty=all(r['git']['dirty'] for r in records),
     all_checkpoint_reloads_verified=all(r['checkpoint_reload_verified'] for r in records)))
text='# Interpretation, negative results and limits\n\n'
text+='The registered technical matrix is complete:300 independent primary trainings (including12 verified Pilot cells) and300 no-update mask evaluations from60 full-hop checkpoints. No historical baseline was altered or pooled. Teacher approval remains **NOT_VERIFIED**. This is a diagnostic fixed-x intervention, not a newly implemented per-node hop selector.\n\n'
text+=f"H1: mean test curves are not monotonically nondecreasing in {len(nonmonotone)}/6 datasets ({', '.join(nonmonotone)}). This is descriptive evidence under the frozen local protocol, not proof that high-hop features are intrinsically redundant or harmful. Increasing x can improve, plateau or degrade a trained model; changing the candidates also changes optimization and normalization of routing weights.\n\n"
text+='H2: validation-best **mean** x (descriptive, not a new pooled test-selected model): '+', '.join(f'{d}={x}' for d,x in val_best.items())+'. Per-split x selection and test evaluation are separately reported in validation_selection.csv. Different selected scopes can reflect real graph differences, small/noisy validation sets, coarse accuracy ties and initialization as well as signal usefulness. The chosen tie rule favors smaller x on exact validation ties.\n\n'
text+=f"There are {len(significant)}/24 primary contrasts below0.05 after Holm correction within each dataset (four x-vs5 contrasts). Families are not corrected across all six datasets. Overlapping splits limit inferential independence; do not treat these thresholds as independent-graph confirmation.\n\n"
text+='## Concrete positive and negative examples\n\n'
for label,row in [('Largest positive descriptive contrast',positive),('Largest negative descriptive contrast',negative)]:
    text+=f"{label}: {row['dataset']}, x={row['x']} minus x5 is {row['mean']:+.2f} pp, sampleSD {row['sample_sd']:.2f}, paired bootstrap95% interval [{row['ci95_low']:+.2f},{row['ci95_high']:+.2f}], Holm p={row['p_holm']:.5f}. This example was selected to illustrate the complete test curve after execution, not to choose a deployed x or claim an unbiased winner.\n\n"
text+=f"H3 exploratory: the largest absolute mean post-hoc-minus-retrain gap among x1-4 is {example['dataset']}, x={example['x']}: {example['mean']:+.2f} pp (sampleSD {example['sample_sd']:.2f}). A model trained using all hops can respond differently to removing candidates than a model trained for that scope. Post-hoc masks change the training/inference distribution, so a post-hoc loss cannot be equated with a retrained architecture's intrinsic quality. x5 itself is checked against the saved full-control accuracy and all diagnostic state hashes stay unchanged.\n\n"
text+='## Mechanism, costs and limitations\n\n'
text+='Inactive candidates have exactly zero routing coefficients and classification gradients in every iteration. They retain parameter rows and remain subject to optimizer weight decay. Shared projection, LayerNorm, squash, classifier and all propagation operations remain present. Every forward uses15 additive propagate calls across independent branches, maximum chain5, six tensors; masking therefore does not remove the propagation expense. Measured time/peak/incremental allocated GPU memory and parameters are in resource_summary.csv; inference timings use5 warmups/20 repeats and GPU synchronization. CPU RSS/extra host memory and monetary cost are UNKNOWN. Costs were observed on a Windows/WDDM workstation with display activity and concurrent host-side documentation/analysis work, not an isolated speed benchmark. No total speedup claim.\n\n'
text+='One optimization seed per split couples split and initialization variation. Ten splits overlap within one graph. The same validation set chooses epoch and scope, so selected test estimates have potential selection bias; no nested selection was run. Small WebKB validation sets have coarse accuracy resolution. No method-specific hyperparameter search, extra independent graph, causal per-node attribution, data leakage intervention beyond label-isolation tests, or strict paper-style protocol replication was performed. Gate weights alone do not establish causal hop usefulness. The inherited normalized-entropy scalar divides by log(6), the full candidate count, at all x; it must not be read as active-count-normalized confidence across scopes.\n\n'
text+='Local source-faithful protocol differs from the paper text: one actual GAMMA layer, LayerNorm,60/20/20,early stopping and inclusive0..x. New six-hop initialization differs from historical K4 canonical initialization. All arms in this experiment have the same complete parameter state and RNG at initialization. Dropout operations have matched shapes; different stopping times use different total RNG draws.\n\n'
text+='Execution Git SHA identifies base main plus dirty source hashes; the later publication commit is not relabeled as the training commit. Fresh environment installation and public checkpoint hosting remain NOT_VERIFIED/NOT_PROVIDED. Original source and protected historical evidence are checked separately. Scientific zero/negative results and engineering failure records are retained.\n\n'
text+='## Most useful next adaptive-hop direction (proposed only)\n\n'
text+='Study a sparse per-node hop budget within the existing Dot routing, keeping a mandatory0-hop and a full-hop matched control. First compare stability across multiple optimization seeds per fixed split and use nested validation for budget selection. Then test whether selective candidates generalize when trained with the same intervention they receive at inference; use node-level counterfactual masks rather than interpreting large alpha as causal importance. This is a prospective research direction motivated by scope dependence and post-hoc/retrain mismatch, not an implemented architecture or a promised improvement. Freeze its protocol and obtain any required teacher approval before a new study.\n'
(STUDY/'docs/04_INTERPRETATION_AND_LIMITATIONS.md').write_text(text,encoding='utf8')
print(json.dumps(hypotheses,indent=2))

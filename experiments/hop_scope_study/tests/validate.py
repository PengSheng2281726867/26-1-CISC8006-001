"""Scientific acceptance tests; no full real training."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.common import REPO,STUDY,save,now,sha,git_state
from src.model import ScopeLayer,ScopeNet,checked_mask
from src.data import load_graph,DATASETS
import copy
import importlib.util
import io
import unittest
from unittest.mock import patch
import torch
from torch_geometric.data import Data
from research.src.model import GammaNet
from research.src.train import train_model
from research.src.paths import tensor_hash

CASES=[]

def official():
    name='GAMMA_layer';path=REPO/'research/upstream_snapshot/GAMMA_layer.py'
    spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod;spec.loader.exec_module(mod)
    name='scope_official_net';path=REPO/'research/upstream_snapshot/gamma_multi_split.py'
    spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod;spec.loader.exec_module(mod)
    return mod.GAMMA_GNN

OFFICIAL=official()

class ScopeTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1);torch.manual_seed(73)
        self.edge=torch.tensor([[0,1,2,3,4,5,0,2],[1,2,3,4,5,0,3,5]])
        self.x=torch.randn(6,5)

    def test_all_scopes_compute_all_five_hops(self):
        for x in range(1,6):
            layer=ScopeLayer(5,8,max_gating_hop=x)
            with patch.object(layer,'propagate',wraps=layer.propagate) as spy:
                _,d=layer(self.x,self.edge,return_diagnostics=True)
                self.assertEqual(spy.call_count,15)
            self.assertEqual(layer.powers,list(range(6)));self.assertEqual(d['hops'].shape,(6,6,8))
            for p in range(6):
                h=layer.shared_linear(self.x)
                for _ in range(p):
                    nxt=torch.zeros_like(h);nxt.index_add_(0,self.edge[1],h[self.edge[0]]);h=nxt
                expected=layer.layer_norm(h*layer.scale_params[p])
                torch.testing.assert_close(d['hops'][:,p],expected,rtol=0,atol=0)
            CASES.append(dict(test='propagation',x=x,calls=15,max_power=5,retained_hops=6))

    def test_zero_mask_every_iteration_and_gradient(self):
        for r in (1,2,3,4):
            for x in range(1,6):
                layer=ScopeLayer(5,8,max_gating_hop=x,num_iterations=r)
                h=torch.randn(6,6,8,requires_grad=True)
                out,d=layer.route(h,True)
                for entry in d['iterations']:
                    self.assertEqual(torch.count_nonzero(entry['alpha'][:,x+1:]).item(),0)
                    torch.testing.assert_close(entry['alpha'].sum(1),torch.ones(6))
                (out*torch.randn_like(out)).sum().backward()
                self.assertEqual(torch.count_nonzero(h.grad[:,x+1:]).item(),0)
                self.assertGreater(h.grad[:,:x+1].abs().sum().item(),0)
                altered=h.detach().clone();altered[:,x+1:]=torch.randn_like(altered[:,x+1:])*100
                torch.testing.assert_close(layer.route(altered),out.detach(),rtol=0,atol=0)

    def test_x5_official_full_network_forward_backward(self):
        for device,dtype in [('cpu',torch.float64),('cuda',torch.float32)]:
            if device=='cuda' and not torch.cuda.is_available():continue
            for r in (1,2,3):
                for training in (False,True):
                    original=OFFICIAL(5,8,3,powers=list(range(6)),num_layers=2,num_iterations=r).to(device=device,dtype=dtype)
                    masked=ScopeNet(5,8,3,num_iterations=r).to(device=device,dtype=dtype)
                    masked.load_state_dict(original.state_dict());original.train(training);masked.train(training)
                    first=self.x.to(device=device,dtype=dtype).clone().requires_grad_()
                    second=first.detach().clone().requires_grad_();edge=self.edge.to(device)
                    torch.manual_seed(58);a=original(first,edge)
                    torch.manual_seed(58);b=masked(second,edge)
                    atol,rtol=(1e-10,1e-9) if dtype==torch.float64 else (2e-6,2e-5)
                    torch.testing.assert_close(a,b,atol=atol,rtol=rtol)
                    probe=torch.arange(18,device=device,dtype=dtype).reshape(6,3)/19
                    (a*probe).sum().backward();(b*probe).sum().backward()
                    torch.testing.assert_close(first.grad,second.grad,atol=atol,rtol=rtol)
                    errors=[]
                    for (n,p),(m,q) in zip(original.named_parameters(),masked.named_parameters()):
                        self.assertEqual(n,m);torch.testing.assert_close(p.grad,q.grad,atol=atol,rtol=rtol)
                        errors.append(float((p.grad-q.grad).abs().max()))
                    CASES.append(dict(test='official_parity',device=device,dtype=str(dtype),r=r,training=training,
                                      forward_max_error=float((a-b).abs().max().detach()),gradient_max_error=max(errors)))

    def test_architecture_initialization_rng_and_scale_gradients(self):
        hashes=[];counts=[];rng=[]
        for x in range(1,6):
            torch.manual_seed(42);model=ScopeNet(5,32,3,max_gating_hop=x)
            hashes.append(tensor_hash(model.state_dict()));counts.append(sum(p.numel() for p in model.parameters()))
            rng.append(tensor_hash({'rng':torch.get_rng_state()}))
            self.assertEqual(len(model.convs),1);self.assertEqual(model.convs[0].num_iterations,2)
            self.assertEqual(model.convs[0].scale_params.shape,(6,32))
            model.eval();out=model(self.x,self.edge);(out*torch.randn_like(out)).sum().backward()
            grad=model.convs[0].scale_params.grad
            self.assertTrue(torch.isfinite(grad).all());self.assertEqual(torch.count_nonzero(grad[x+1:]).item(),0)
            self.assertGreater(grad[:x+1].abs().sum().item(),0)
        self.assertEqual(len(set(hashes)),1);self.assertEqual(len(set(counts)),1);self.assertEqual(len(set(rng)),1)
        CASES.append(dict(test='fair_initialization',identical_full_hash=hashes[0],parameters=counts[0]))

    def test_scope_changes_synthetic_output(self):
        layer=ScopeLayer(5,8,max_gating_hop=1)
        # The only late-hop mass points along dimension 1; early hops point along 0.
        hops=torch.zeros(2,6,8);hops[:,:2,0]=1;hops[:,2:,1]=3
        a=layer.route(hops);layer.set_scope(5);b=layer.route(hops)
        self.assertGreater((a-b).abs().max().item(),.1)

    def test_invalid_masks_inputs_and_finite_zero_graph(self):
        for kwargs in [dict(max_gating_hop=0),dict(max_gating_hop=6),dict(max_propagation_hop=4),dict(num_iterations=0)]:
            with self.assertRaises(ValueError):ScopeLayer(5,8,**kwargs)
        hops=torch.zeros(2,6,8)
        for mask in [torch.zeros(6,dtype=torch.bool),torch.ones(2,6,dtype=torch.bool),torch.ones(6)]:
            with self.assertRaises(ValueError):checked_mask(mask,hops)
        if torch.cuda.is_available():
            with self.assertRaises(ValueError):checked_mask(torch.ones(6,dtype=torch.bool,device='cuda'),hops)
        model=ScopeNet(5,8,3);out=model(torch.zeros(6,5),torch.empty(2,0,dtype=torch.long))
        self.assertTrue(torch.isfinite(out).all())
        with self.assertRaises(ValueError):model.set_scope(0)
        from src.data import dataset
        with self.assertRaises(ValueError):dataset('INVALID',Path('.'))
        with self.assertRaises(FileNotFoundError):load_graph(Path(__file__).resolve().parents[4]/'nonexistent_input_fixture','Texas',0,'cpu')

    def test_test_labels_do_not_affect_training_or_gate(self):
        graph=Data(x=self.x,edge_index=self.edge,y=torch.tensor([0,1,2,0,1,2]),
                   train_mask=torch.tensor([1,1,1,0,0,0],dtype=torch.bool),
                   val_mask=torch.tensor([0,0,0,1,0,0],dtype=torch.bool),
                   test_mask=torch.tensor([0,0,0,0,1,1],dtype=torch.bool))
        config=dict(learning_rate=.02,weight_decay=.0001,scheduler=dict(factor=.5,patience=50,min_lr=1e-6),
                    gradient_clip=1,epochs=4,early_stopping_patience=50)
        states=[];scores=[]
        for change in (False,True):
            other=graph.clone()
            if change:other.y[other.test_mask]=(other.y[other.test_mask]+1)%3
            torch.manual_seed(31);model=ScopeNet(5,8,3,max_gating_hop=3)
            torch.manual_seed(88);report=train_model(model,other,config)
            states.append(tensor_hash(model.state_dict()));scores.append(report['best_validation_accuracy'])
        self.assertEqual(states[0],states[1]);self.assertEqual(scores[0],scores[1])


def main():
    from research.src.factory import configure_determinism
    configure_determinism();stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ScopeTests))
    log=stream.getvalue();print(log)
    save(STUDY/'results/adapter_validation.json',dict(status='passed' if result.wasSuccessful() else 'failed',
         utc=now(),git=git_state(),tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),
         cases=CASES,source_sha256=sha(STUDY/'src/model.py')))
    # Full acceptance includes separately executed repository smoke and all splits.
    return 0 if result.wasSuccessful() else 1

if __name__=='__main__':sys.exit(main())

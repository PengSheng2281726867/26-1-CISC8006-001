import unittest
import tempfile
from pathlib import Path
import numpy as np
import torch
from experiments.exact_distance_query.src.common import verify_freeze, read, STUDY
from experiments.exact_distance_query.src.distance import build, tensors, cached, edge_hash
from experiments.exact_distance_query.src.model import build_model
from experiments.exact_distance_query.src.run import equivalence, jobs, science
from src.model import GammaLayer,GammaNet
from src.factory import configure_determinism
from torch_geometric.data import Data

class DistanceTests(unittest.TestCase):
    def shells(self,edges,n): return build(torch.tensor(edges,dtype=torch.long).T.contiguous(),n)[0]
    def sets(self,shell):
        ptr,col=shell;return [set(col[ptr[i]:ptr[i+1]].tolist()) for i in range(len(ptr)-1)]
    def test_five_chain_all_nodes(self):
        s=self.shells([(i,j) for i in range(5) for j in range(5) if abs(i-j)==1],5)
        for p in range(5): self.assertEqual(self.sets(s[p]),[{j for j in range(5) if abs(i-j)==p} for i in range(5)])
    def test_triangle_and_four_cycle_backtracking(self):
        for n in (3,4):
            e=[(i,(i+1)%n) for i in range(n)];e += [(j,i) for i,j in e]
            s=self.shells(e,n)
            self.assertTrue(all(not x for x in self.sets(s[3])))
            a=torch.zeros(n,n)
            for i,j in e:a[j,i]+=1
            self.assertTrue(bool((a.matrix_power(3)>0).any()))
    def test_directed_duplicate_reverse_loops(self):
        s=self.shells([(0,1),(0,1),(1,2),(2,3),(2,2),(1,0)],5)
        self.assertEqual(self.sets(s[1]),[{1},{0},{1},{2},set()])
        self.assertEqual(self.sets(s[2]),[set(),set(),{0},{1},set()])
        self.assertEqual(self.sets(s[3]),[set(),set(),set(),{0},set()])
        self.assertEqual(self.sets(s[0]),[{i} for i in range(5)])
    def test_labels_not_accepted_and_cache_stable(self):
        e=torch.tensor([[0,1,1],[1,2,1]])
        with tempfile.TemporaryDirectory() as tmp:
            a,m=cached(e,4,Path(tmp));b,n=cached(e,4,Path(tmp))
            self.assertEqual(m,n)
            for x,y in zip(a,b):
                for u,v in zip(x,y):np.testing.assert_array_equal(u,v)
            # Label permutations cannot reach this topology-only API.
            for labels in (torch.arange(4),torch.arange(4).flip(0)):
                _,check=build(e,4);self.assertEqual(check['shell_content_sha256'],m['shell_content_sha256'])
    def test_cpu_gpu_sparse_reference_and_gradient(self):
        e=torch.tensor([[0,0,1,2,2],[1,1,2,3,2]]);shells,_=build(e,5)
        for dev in ('cpu','cuda') if torch.cuda.is_available() else ('cpu',):
            ops,valid=tensors(shells,5,dev);z=torch.randn(5,4,device=dev,requires_grad=True)
            for op,(ptr,col) in zip(ops,shells):
                ref=torch.zeros_like(z)
                for i in range(5):
                    if ptr[i]!=ptr[i+1]:ref[i]=z[torch.tensor(col[ptr[i]:ptr[i+1]],device=dev)].sum(0)
                torch.testing.assert_close(torch.sparse.mm(op,z),ref)
                torch.sparse.mm(op,z).sum().backward(retain_graph=True)
            self.assertTrue(z.grad.isfinite().all())
    def test_invalid_and_resource_guard(self):
        with self.assertRaises(ValueError):build(torch.tensor([[0],[5]]),3)
        with self.assertRaises(MemoryError):build(torch.tensor([[0],[1]]),3,max_nnz=1)

class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):torch.set_num_threads(1);configure_determinism()
    def fixture(self,device='cpu'):
        torch.manual_seed(18)
        e=torch.tensor([[0,0,1,2,3,4,5,2],[1,1,2,3,4,5,0,2]],device=device)
        g=Data(x=torch.randn(8,6,device=device),edge_index=e,y=torch.arange(8,device=device)%3,
            train_mask=torch.tensor([1,1,1,1,0,0,0,0],dtype=torch.bool,device=device))
        shells,_=build(e,8);ops,valid=tensors(shells,8,device);return g,ops,valid
    def test_four_groups_shape_params_gradient_mask_save(self):
        g,ops,valid=self.fixture();counts=[];inits=[]
        for group in ('G0','G1','G2','G3'):
            m,init=build_model(6,3,group,42,'cpu',ops,valid);m.eval();inits.append(init)
            out,d=m(g.x,g.edge_index,True);self.assertEqual(tuple(out.shape),(8,3))
            torch.testing.assert_close(out.exp().sum(1),torch.ones(8))
            self.assertTrue(out.isfinite().all());torch.testing.assert_close(d[0]['used_alpha'].sum(1),torch.ones(8))
            if group!='G0':
                self.assertTrue((d[0]['used_alpha'][~valid]==0).all())
                self.assertTrue((d[0]['hops'][~valid]==0).all())
            torch.nn.functional.nll_loss(out,g.y).backward()
            for n,p in m.named_parameters():self.assertIsNotNone(p.grad,n);self.assertTrue(p.grad.isfinite().all(),n)
            self.assertGreater(float(m.convs[0].shared_linear.weight.grad.norm()),0)
            self.assertGreater(float(m.convs[0].scale_params.grad.norm()),0)
            counts.append(sum(p.numel() for p in m.parameters()))
            with tempfile.TemporaryDirectory() as tmp:
                torch.save(m.state_dict(),Path(tmp)/'model.pt');m.load_state_dict(torch.load(Path(tmp)/'model.pt',weights_only=True))
                torch.testing.assert_close(m(g.x,g.edge_index),out)
        self.assertEqual(len(set(counts)),1);self.assertTrue(all(i==inits[0] for i in inits))
    def test_original_forward_alpha_input_parameter_gradients(self):
        for dev in ('cpu','cuda') if torch.cuda.is_available() else ('cpu',):
            g,ops,valid=self.fixture(dev);m,_=build_model(6,3,'G0',42,dev,ops,valid)
            self.assertEqual(equivalence(m,g,'G0')['status'],'passed')
            ref=GammaNet(6,32,3,powers=list(range(5))).to(dev);ref.load_state_dict(m.state_dict());m.eval();ref.eval()
            x=g.x.clone().requires_grad_();y=g.x.clone().requires_grad_()
            a,_=m(x,g.edge_index,True);b,_=ref(y,g.edge_index,True)
            a.square().sum().backward();b.square().sum().backward();torch.testing.assert_close(x.grad,y.grad,atol=2e-6,rtol=2e-5)
    def test_walk_fallback_equals_original_with_weights(self):
        g,ops,valid=self.fixture();m,_=build_model(6,3,'G1',42,'cpu',ops,valid,aggregation='walk')
        ref=GammaLayer(6,32,powers=list(range(5)));ref.load_state_dict(m.convs[0].state_dict())
        w=torch.linspace(.2,1.7,g.num_edges)
        a,ad=m.convs[0](g.x,g.edge_index,w,True);b,bd=ref(g.x,g.edge_index,w,True)
        torch.testing.assert_close(a,b);torch.testing.assert_close(ad['used_alpha'],bd['used_alpha'])
    def test_consensus_one_shot_bias_norm_empty_gradients(self):
        for dev in ('cpu','cuda') if torch.cuda.is_available() else ('cpu',):
            g,ops,valid=self.fixture(dev)
            for policy in ('mask','legacy'):
                m,_=build_model(6,3,'G1',42,dev,ops,valid,policy)
                with torch.no_grad():m.convs[0].layer_norm.bias.fill_(.7);m.convs[0].bias.fill_(.3)
                self.assertEqual(equivalence(m,g,'G1')['status'],'passed')
    def test_fixed_query_h0_h4_and_shared_candidates(self):
        g,ops,valid=self.fixture();allh=[]
        for group,p in [('G2',0),('G3',4)]:
            m,_=build_model(6,3,group,42,'cpu',ops,valid);m.eval();out,d=m(g.x,g.edge_index,True);c=m.convs[0];z=c.shared_linear(g.x)
            h=z
            for _ in range(p):h=c.propagate(g.edge_index,x=h,edge_weight=torch.ones(g.num_edges))
            query=c.layer_norm(h*c.scale_params[p]);torch.testing.assert_close(d[0]['query'],query)
            score=(d[0]['hops']*query[:,None]).sum(-1).masked_fill(~valid,-torch.inf)
            torch.testing.assert_close(d[0]['used_alpha'],score.softmax(1));allh.append(d[0]['hops'])
            if p==4:self.assertGreater(float((query-d[0]['hops'][:,4]).abs().max()),.01)
        torch.testing.assert_close(*allh)
    def test_empty_affine_bias_and_used_alpha(self):
        g,ops,valid=self.fixture();m,_=build_model(6,3,'G1',42,'cpu',ops,valid);m.eval()
        with torch.no_grad():m.convs[0].layer_norm.bias.fill_(2.)
        out,d=m(g.x,g.edge_index,True);d=d[0]
        self.assertTrue((d['hops'][~valid]==0).all());self.assertTrue((d['used_alpha'][~valid]==0).all())
        self.assertGreater(float((d['used_alpha']-d['post_update_logits'].masked_fill(~valid,-torch.inf).softmax(1)).abs().max()),1e-4)
    def test_protocol_and_plan_counts(self):
        verify_freeze()
        for phase,n in [('smoke',4),('pilot',48),('full',720),('empty_control',9)]:
            cfg=read(STUDY/'configs'/(phase+'.json'));self.assertEqual(len(jobs(cfg)),n)
        self.assertEqual(science(read(STUDY/'configs/pilot.json')),science(read(STUDY/'configs/full.json')))
if __name__=='__main__':unittest.main()

import unittest
import numpy as np
import torch
import torch.nn.functional as F
from research.src.model import GammaNet
from research.src.paths import tensor_hash
from experiments.loho_diagnostic.src.intervention import forward,validate_model
from experiments.loho_diagnostic.src.statistics import rho,fractions,stats

torch.set_num_threads(1)
class Interventions(unittest.TestCase):
    def fixture(self,k=4,r=2,device='cpu',dtype=torch.float32):
        torch.manual_seed(3)
        model=GammaNet(5,8,3,powers=list(range(k+1)),num_iterations=r).to(device=device,dtype=dtype).eval()
        x=torch.randn(7,5,device=device,dtype=dtype)
        edge=torch.tensor([[0,1,2,3,4,5,6,1,5],[1,2,3,4,5,6,0,5,1]],device=device)
        return model,x,edge
    def test_no_mask_identity_and_actual_alpha(self):
        for device in ['cpu']+(['cuda'] if torch.cuda.is_available() else []):
            for k in (1,4,5):
                for r in (1,2):
                    with self.subTest(device=device,k=k,r=r),torch.inference_mode():
                        m,x,e=self.fixture(k,r,device);o,d=m(x,e,return_diagnostics=True);v,t=forward(m,x,e)
                        torch.testing.assert_close(o,v,atol=2e-6,rtol=2e-5)
                        torch.testing.assert_close(d[0]['used_alpha'],t['used_alpha'],atol=0,rtol=0)
                        labels=torch.arange(7,device=device)%3
                        torch.testing.assert_close(F.nll_loss(o,labels,reduction='none'),F.nll_loss(v,labels,reduction='none'))
                        torch.testing.assert_close(t['used_alpha'],t['iterations'][-1]['alpha'])
                        self.assertGreater(float((t['used_alpha']-t['post_update_logits'].softmax(1)).abs().max()),1e-6)
                        reconstruct=m.convs[0].squash((t['used_alpha'][:,:,None]*t['hops']).sum(1))+m.convs[0].bias
                        torch.testing.assert_close(v,F.log_softmax(m.lin(m.norms[0](reconstruct)),1))
                        if r==1: torch.testing.assert_close(t['used_alpha'],torch.full_like(t['used_alpha'],1/(k+1)))
    def test_isolation_masking_normalization_and_immutability(self):
        for k in (1,4,5):
            for r in (1,2,3):
                m,x,e=self.fixture(k,r);before=tensor_hash(m.state_dict())
                with torch.inference_mode():
                    base,d=forward(m,x,e)
                    for mask in ('final_only','full_routing'):
                        for hop in range(1,k+1):
                            out,t=forward(m,x,e,mask,hop)
                            self.assertTrue(bool(torch.isfinite(out).all()))
                            for i,it in enumerate(t['iterations']):
                                torch.testing.assert_close(it['alpha'].sum(1),torch.ones(7))
                                if mask=='full_routing' or i==r-1:
                                    self.assertTrue(bool((it['alpha'][:,hop]==0).all()))
                                    self.assertTrue(bool((it['alpha'][:,0]>0).all()))
                                else:
                                    for key in ('logits','fused','alpha'): torch.testing.assert_close(it[key],d['iterations'][i][key],atol=0,rtol=0)
                            for node in (0,3,6):
                                single,_=forward(m,x,e,mask,hop,nodes=[node])
                                torch.testing.assert_close(single[node],out[node],atol=2e-6,rtol=2e-5)
                                other=[i for i in range(7) if i!=node]
                                torch.testing.assert_close(single[other],base[other])
                    for mask in ('final_only','full_routing'):
                        for hop in (0,-1,k+1):
                            with self.assertRaises(ValueError): forward(m,x,e,mask,hop)
                self.assertEqual(before,tensor_hash(m.state_dict()))
    def test_full_mask_independent_of_removed_branch(self):
        m,x,e=self.fixture();layer=m.convs[0]
        from experiments.loho_diagnostic.src.intervention import route
        with torch.inference_mode():
            h=layer.hop_embeddings(x,e);out,d=route(layer,h,'full_routing',2)
            changed=h.clone();changed[:,2]=1000
            out2,d2=route(layer,changed,'full_routing',2)
            torch.testing.assert_close(out,out2,atol=0,rtol=0)
    def test_unsupported_coupling_and_training_rejected(self):
        m,x,e=self.fixture();m.train()
        with self.assertRaises(ValueError): forward(m,x,e)
        m=GammaNet(5,8,3,num_layers=3).eval()
        with self.assertRaises(ValueError): validate_model(m)
        m,x,e=self.fixture();m.norms[0]=torch.nn.BatchNorm1d(8).eval()
        with self.assertRaises(ValueError): validate_model(m)
    def test_loss_sign_and_statistics(self):
        labels=torch.tensor([0,1]);full=torch.log(torch.tensor([[.8,.2],[.4,.6]]));masked=torch.log(torch.tensor([[.4,.6],[.2,.8]]))
        d=F.nll_loss(masked,labels,reduction='none')-F.nll_loss(full,labels,reduction='none')
        np.testing.assert_allclose(d.numpy(),np.log([2,.75]),atol=1e-7)
        self.assertEqual(fractions(d.numpy())['negative_fraction'],.5)
        self.assertEqual(rho([1,2,3],[3,2,1])[0],-1)
        self.assertEqual(rho([1,1],[1,2]),(None,'constant_vector'))
        self.assertEqual(rho([1,np.nan],[1,2]),(None,'nonfinite'))
        self.assertAlmostEqual(rho([1,1,2],[2,2,3])[0],1)
    def test_r1_interventions_equal(self):
        m,x,e=self.fixture(r=1)
        with torch.inference_mode():
            for h in range(1,5):
                a,_=forward(m,x,e,'final_only',h);b,_=forward(m,x,e,'full_routing',h)
                torch.testing.assert_close(a,b,atol=0,rtol=0)

if __name__=='__main__':unittest.main()

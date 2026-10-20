import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.paths import ROOT,save_json
import importlib.util
import unittest
import torch
from src.model import GammaLayer,GammaNet

torch.set_num_threads(1)

def official_modules():
    path=ROOT/'upstream_snapshot/GAMMA_layer.py'
    spec=importlib.util.spec_from_file_location('GAMMA_layer',path)
    layer=importlib.util.module_from_spec(spec);sys.modules['GAMMA_layer']=layer;spec.loader.exec_module(layer)
    spec=importlib.util.spec_from_file_location('official_gamma_multi_split',ROOT/'upstream_snapshot/gamma_multi_split.py')
    training=importlib.util.module_from_spec(spec);sys.modules[spec.name]=training;spec.loader.exec_module(training)
    return layer,training

OFFICIAL_LAYER,OFFICIAL_NET=official_modules()
ALIGNMENT=[]

class BaselineTests(unittest.TestCase):
    def compare(self,device,dtype,k,r,training):
        torch.manual_seed(41)
        edge=torch.tensor([[0,1,2,3,4,5,0,2,4],[1,2,3,4,5,0,2,4,0]],device=device)
        official=OFFICIAL_NET.GAMMA_GNN(5,8,3,powers=list(range(k+1)),num_layers=2,num_iterations=r).to(device=device,dtype=dtype)
        independent=GammaNet(5,8,3,powers=list(range(k+1)),num_layers=2,num_iterations=r).to(device=device,dtype=dtype)
        independent.load_state_dict(official.state_dict(),strict=True)
        official.train(training);independent.train(training)
        x=torch.randn(6,5,device=device,dtype=dtype)
        first=x.clone().requires_grad_(True);second=x.clone().requires_grad_(True)
        torch.manual_seed(59);out1=official(first,edge)
        torch.manual_seed(59);out2=independent(second,edge)
        atol,rtol=(1e-10,1e-9) if dtype==torch.float64 else (2e-6,2e-5)
        torch.testing.assert_close(out1,out2,atol=atol,rtol=rtol)
        probe=torch.arange(1,19,device=device,dtype=dtype).reshape(6,3)/20
        (out1*probe).sum().backward();(out2*probe).sum().backward()
        torch.testing.assert_close(first.grad,second.grad,atol=atol,rtol=rtol)
        grad_error=0.0
        for (key,p1),(key2,p2) in zip(official.named_parameters(),independent.named_parameters()):
            self.assertEqual(key,key2)
            torch.testing.assert_close(p1.grad,p2.grad,atol=atol,rtol=rtol)
            grad_error=max(grad_error,float((p1.grad-p2.grad).abs().max()))
        ALIGNMENT.append(dict(device=str(device),dtype=str(dtype),k=k,r=r,training=training,
                              output_max_error=float((out1-out2).abs().max().detach()),parameter_gradient_max_error=grad_error))

    def test_cpu_forward_and_gradients(self):
        for k in (1,2,3,4):
            for r in (1,2,3):
                with self.subTest(k=k,r=r): self.compare('cpu',torch.float64,k,r,False)

    @unittest.skipUnless(torch.cuda.is_available(),'CUDA not available')
    def test_cuda_forward_and_gradients(self):
        torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False
        for k in (1,2,3,4):
            for training in (False,True):
                with self.subTest(k=k,training=training): self.compare('cuda',torch.float32,k,2,training)

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(BaselineTests))
    save_json(ROOT/'results/baseline_alignment.json',dict(passed=result.wasSuccessful(),cases=ALIGNMENT))
    sys.exit(0 if result.wasSuccessful() else 1)

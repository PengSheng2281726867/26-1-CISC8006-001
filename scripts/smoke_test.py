"""One-command synthetic checks; never download datasets or run full training."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from course.common import ROOT,save,utc_now,git_state,sha256
import importlib.util
import io
import json
import time
import unittest
import uuid


def main():
    import torch
    import torch_geometric
    import numpy as np
    start=time.perf_counter()
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_*.py')
    spec=importlib.util.spec_from_file_location('recovered_alignment',ROOT/'research/tests/test_baseline.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(module.BaselineTests))
    stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    stamp=uuid.uuid4().hex[:12]
    folder=ROOT/'outputs'/('smoke-'+stamp)
    folder.mkdir(parents=True,exist_ok=False)
    text=stream.getvalue()
    (folder/'tests.log').write_text(text,encoding='utf8')
    report=dict(status='passed' if result.wasSuccessful() else 'failed',utc=utc_now(),git=git_state(),
        tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),
        alignment_cases=module.ALIGNMENT,seconds=time.perf_counter()-start,
        environment=dict(python=sys.version.split()[0],torch=torch.__version__,pyg=torch_geometric.__version__,
                         numpy=np.__version__,cuda_available=torch.cuda.is_available()),
        synthetic_only=True,dataset_downloaded=False,full_training_started=False,
        source_mapping_sha256=sha256(ROOT/'experiments/source_mapping.json'))
    save(folder/'report.json',report)
    print(text)
    print(json.dumps(dict(status=report['status'],tests_run=result.testsRun,
                         alignment_cases=len(module.ALIGNMENT),report=str((folder/'report.json').relative_to(ROOT)))))
    return 0 if result.wasSuccessful() else 1


if __name__=='__main__':sys.exit(main())

import unittest
from experiments.exact_distance_query.src.analyze import holm, signflip, interval, mean, sd
class AnalysisTests(unittest.TestCase):
    def test_known_signflip(self):
        self.assertEqual(signflip([1.,1.]),.5)
        self.assertEqual(signflip([0.,0.]),1.)
        self.assertEqual(signflip([1.,-1.]),1.)
    def test_holm_and_hierarchical_units(self):
        self.assertEqual(holm([.01,.04,.03]),[.03,.06,.06])
        self.assertEqual(mean([mean([0.,100.]),mean([100.,100.])]),75.)
        self.assertAlmostEqual(sd([1.,3.]),2**.5)
    def test_bootstrap_reproducible_bounded(self):
        self.assertEqual(interval([1.,2.,3.]),interval([1.,2.,3.]))
        low,high=interval([1.,2.,3.]);self.assertGreaterEqual(low,1);self.assertLessEqual(high,3)

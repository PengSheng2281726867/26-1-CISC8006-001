"""Known-answer checks for statistical summaries, independent of measured scores."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from aggregate import paired,holm,statistics,cell_status
import unittest
class AnalysisTests(unittest.TestCase):
    def test_running_retry_is_not_a_failed_or_pending_cell(self):
        self.assertEqual(cell_status(None,[]),'not_run')
        self.assertEqual(cell_status(None,[dict(status='running')]),'running')
        self.assertEqual(cell_status(None,[dict(status='failed'),dict(status='running')]),'running')
        self.assertEqual(cell_status(dict(status='complete'),[dict(status='failed')]),'complete')
        self.assertEqual(cell_status(None,[dict(status='complete')]),'invalid_artifacts')
    def test_sample_sd_and_exact_two_sided_sign_flip(self):
        s=statistics([0,2]);self.assertAlmostEqual(s['sample_sd'],2**.5)
        self.assertEqual(paired([1]*10)['p_sign_flip'],2/1024)
        self.assertEqual(paired([1,-1])['p_sign_flip'],1)
        self.assertEqual(paired([0]*10)['ci95_low'],0)
        self.assertEqual(paired([0]*10)['ci95_high'],0)
        self.assertIsNone(statistics([])['mean'])
    def test_holm_monotonic_family(self):
        rows=[dict(p_sign_flip=x) for x in (.01,.03,.04,.2)];holm(rows)
        for row,expected in zip(rows,(.04,.09,.09,.2)):
            self.assertAlmostEqual(row['p_holm'],expected)
    def test_bootstrap_reproducible_and_paired(self):
        a=paired([1,2,3,4]);b=paired([1,2,3,4]);self.assertEqual(a,b)
        self.assertLessEqual(a['ci95_low'],a['mean']);self.assertGreaterEqual(a['ci95_high'],a['mean'])
if __name__=='__main__':unittest.main(verbosity=2)

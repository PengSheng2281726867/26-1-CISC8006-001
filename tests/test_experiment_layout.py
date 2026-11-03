"""Regression checks for moving studies beneath numbered topic directories."""
from collections import Counter
import csv
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ExperimentLayoutTests(unittest.TestCase):
    def test_groups_cover_each_study_and_historical_registry_once(self):
        catalog = json.loads((ROOT/'experiments/catalog.json').read_text(encoding='utf8'))
        self.assertEqual({g['id'] for g in catalog['groups']}, {
            '01_reproduction', '02_scorer_ablation', '03_hop_diagnostics', '04_distance_query'})
        studies = [study for g in catalog['groups'] for study in g['experiments']]
        self.assertEqual(len(studies), 8)
        self.assertEqual(len(set(studies)), len(studies))
        self.assertEqual(set(studies), {e['id'] for e in catalog['experiments']})
        with (ROOT/'experiments/registry.csv').open(encoding='utf8', newline='') as stream:
            actual = Counter(row['stage'] for row in csv.DictReader(stream))
        assigned = {}
        for study in catalog['experiments']:
            self.assertFalse((ROOT/'experiments'/study['id']).exists())
            self.assertTrue((ROOT/study['entrypoint']).is_file())
            self.assertIn('/'+study['group_id']+'/', study['entrypoint'])
            for stage, count in study['stages'].items():
                self.assertNotIn(stage, assigned)
                assigned[stage] = count
        self.assertEqual(dict(actual), assigned)
        self.assertEqual(sum(assigned.values()), 1566)

    def test_public_modules_find_grouped_studies_and_repository_root(self):
        targets = {
            'hop_scope_study': '03_hop_diagnostics',
            'loho_diagnostic': '03_hop_diagnostics',
            'exact_distance_query': '04_distance_query',
        }
        for study, group in targets.items():
            with self.subTest(study=study):
                spec = importlib.util.find_spec('experiments.'+study+'.src.common')
                expected = ROOT/'experiments'/group/study
                self.assertEqual(Path(spec.origin).resolve(), expected/'src/common.py')
                module = importlib.import_module('experiments.'+study+'.src.common')
                self.assertEqual(getattr(module, 'REPO', getattr(module, 'ROOT', None)), ROOT)
                self.assertEqual(getattr(module, 'STUDY', getattr(module, 'EXPERIMENT', None)), expected)

    def test_source_manifests_use_existing_paths_and_protocol_freeze_survives(self):
        for study in ('hop_scope_study', 'exact_distance_query'):
            module = importlib.import_module('experiments.'+study+'.src.common')
            sources = module.sources()
            self.assertIn('research/src/model.py', sources)
            self.assertIn('experiments/__init__.py', sources)
            for name, checksum in sources.items():
                with self.subTest(study=study, source=name):
                    path = ROOT/name
                    self.assertTrue(path.is_file())
                    self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), checksum)
        exact = importlib.import_module('experiments.exact_distance_query.src.common')
        frozen = json.loads((exact.STUDY/'results/protocol_freeze.json').read_text())
        self.assertEqual(exact.verify_freeze(), frozen['files']['PROTOCOL.md'])


if __name__ == '__main__':
    unittest.main(verbosity=2)

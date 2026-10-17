"""Offline contract tests; no Toolkit, GPU, or game required."""
import copy
import importlib.util
import tempfile
import unittest
from unittest.mock import patch
import subprocess
from types import SimpleNamespace
from pathlib import Path

spec = importlib.util.spec_from_file_location('remix_runner', Path(__file__).with_name('run_remix_ingest.py'))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class ContractTests(unittest.TestCase):
    def test_configuration_only_changes_copied_context(self):
        original = {'context_plugin': {'name': 'AssetImporter', 'data': {'input_files': [], 'keep': 7}},
                    'checks': [{'untouched': True}]}
        before = copy.deepcopy(original)
        result = runner.configure_schema(original, Path('input/ship.obj'), Path('output'))
        self.assertEqual(original, before)
        self.assertEqual(result['checks'], before['checks'])
        self.assertEqual(result['context_plugin']['data']['output_usd_extension'], 'usda')
        self.assertFalse(result['context_plugin']['data']['allow_empty_input_files_list'])
        self.assertEqual(result['context_plugin']['data']['keep'], 7)

    def test_unknown_context_rejected(self):
        with self.assertRaises(ValueError):
            runner.configure_schema({'context_plugin': {'name': 'Other'}}, 'a', 'b')

    def test_winding_and_coordinates_not_silently_repaired(self):
        with tempfile.TemporaryDirectory() as tmp:
            obj = Path(tmp) / 'ship.obj'
            obj.write_text('v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n')
            mesh = {'points': [[0, 0, 0], [1, 0, 0], [0, 1, 0]], 'counts': [3], 'indices': [1, 2, 0]}
            self.assertTrue(runner.compare_geometry(obj, {'meshes': [mesh]})['triangles_match_native_coordinates_and_winding'])
            mesh['indices'] = [0, 2, 1]
            self.assertFalse(runner.compare_geometry(obj, {'meshes': [mesh]})['triangles_match_native_coordinates_and_winding'])
            mesh['indices'] = [0, 1, 2]
            mesh['points'][1] = [2, 0, 0]
            self.assertFalse(runner.compare_geometry(obj, {'meshes': [mesh]})['triangles_match_native_coordinates_and_winding'])

    def test_metadata_refuses_overwrite_and_oversize(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'result.json'
            runner.write_json(path, {'safe': True})
            with self.assertRaises(FileExistsError):
                runner.write_json(path, {})
            with self.assertRaises(ValueError):
                runner.write_json(Path(tmp) / 'large.json', {'value': 'a'*65536})

    def test_job_deadline_preserved_without_inspection(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            guard = work / 'fake.exe'
            guard.write_bytes(b'fixture only')
            runner.write_json(work / 'job-result.json', {'stop_reason': 22, 'exit_code': 22,
                                                        'remaining_owned_processes': 0})
            with patch.object(runner.subprocess, 'run', return_value=SimpleNamespace(returncode=1)):
                result = runner.execute(work, {'fixture': True, 'command': []}, guard)
            self.assertEqual(result['status'], 'FAIL')
            self.assertIn('stop_reason=22', result['error'])
            self.assertEqual(result['job']['stop_reason'], 22)

    def test_outer_guard_timeout_is_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            guard = work / 'fake.exe'
            guard.write_bytes(b'fixture only')
            with patch.object(runner.subprocess, 'run', side_effect=subprocess.TimeoutExpired('fake', 200)):
                result = runner.execute(work, {'fixture': True, 'command': []}, guard)
            self.assertEqual(result['status'], 'FAIL')
            self.assertTrue((work/'result.json').is_file())


if __name__ == '__main__':
    unittest.main()

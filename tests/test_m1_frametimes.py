import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'tools/m1_component/capture_m1_frametimes.py'
spec = importlib.util.spec_from_file_location('frametimes', SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class FrameTelemetryTests(unittest.TestCase):
    def test_actual_presentmon_v1_lowercase_ms_header(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'frames.csv'
            path.write_text('Application,ProcessID,SwapChainAddress,Runtime,msBetweenPresents\n'
                            'StarFleetOP.exe,22376,0x551CE10,DXGI,16.5\n')
            self.assertEqual(module.analyze_csv(path, 22376)['rows'], 1)

    def test_analysis_keeps_swap_chains_separate(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'frames.csv'
            path.write_text('ProcessID,SwapChainAddress,MsBetweenPresents\n42,a,0\n42,a,10\n42,b,100\n42,a,20\n')
            result = module.analyze_csv(path, 42)
            self.assertEqual(result['swap_chains']['a']['p95_ms'], 20)
            self.assertEqual(result['swap_chains']['b']['mean_ms'], 100)

    def test_invalid_or_absent_data_rejected(self):
        for text in ('', 'ProcessID,SwapChainAddress,MsBetweenPresents\n',
                     'ProcessID,SwapChainAddress,msBetweenPresents,MsBetweenPresents\n42,a,10,11\n',
                     'ProcessID,SwapChainAddress,MsBetweenPresents\n43,a,10\n',
                     'ProcessID,SwapChainAddress,MsBetweenPresents\n42,a,nan\n',
                     'ProcessID,SwapChainAddress,MsBetweenPresents\n42,a,-1\n'):
            with tempfile.TemporaryDirectory() as root:
                path = Path(root) / 'frames.csv'
                path.write_text(text)
                with self.assertRaises(ValueError):
                    module.analyze_csv(path, 42)

    def test_success_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'frames.csv'
            result = module.capture([sys.executable, '-c', 'print("hello")'], path, 1)
            self.assertTrue(result['complete'])
            self.assertTrue(json.loads(path.with_suffix('.csv.capture.json').read_text())['complete'])
            with self.assertRaises(FileExistsError):
                module.capture([sys.executable, '-c', 'print("bad")'], path, 1)

    def test_cap_and_owned_child_cleanup(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'frames.csv'
            result = module.capture([sys.executable, '-u', '-c',
                'import time\nwhile True:\n print("x"*100)\n time.sleep(.001)'], path, 1, 150)
            self.assertFalse(result['complete'])
            self.assertLessEqual(path.stat().st_size, 150)
            self.assertIsNotNone(result['exit_code'])

    def test_nonzero_exit_and_long_line(self):
        for code in ('raise SystemExit(7)', 'print("x"*9000)'):
            with tempfile.TemporaryDirectory() as root:
                result = module.capture([sys.executable, '-c', code], Path(root) / 'frames.csv', 1)
                self.assertFalse(result['complete'])

    def test_wall_guard_stops_silent_child(self):
        with tempfile.TemporaryDirectory() as root:
            result = module.capture([sys.executable, '-c', 'import time; time.sleep(60)'],
                                    Path(root) / 'frames.csv', .01, guard_seconds=.01)
            self.assertFalse(result['complete'])
            self.assertIn('wall-time', result['error'])
            self.assertIsNotNone(result['exit_code'])

    def test_cancellation_stops_owned_child(self):
        with tempfile.TemporaryDirectory() as root:
            stop = Path(root) / 'stop.signal'
            stop.write_text('cancel')
            result = module.capture([sys.executable, '-c', 'import time; time.sleep(60)'],
                                    Path(root) / 'frames.csv', 1800, stop_file=stop)
            self.assertFalse(result['complete'])
            self.assertIn('cancellation', result['error'])
            self.assertIsNotNone(result['exit_code'])


if __name__ == '__main__':
    unittest.main()

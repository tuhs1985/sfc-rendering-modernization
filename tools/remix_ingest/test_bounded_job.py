"""Explicit native guard integration tests. Starts only disposable Python jobs."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
GUARD = ROOT / 'artifacts/remix-ingest/bin/bounded_job.exe'
SCRATCH = ROOT / 'artifacts/m1/test-temp'


class JobTests(unittest.TestCase):
    def run_job(self, code, seconds=5, disk=1024*1024, log=65536):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
            result = subprocess.run([str(GUARD), tmp, str(seconds), str(disk), str(log),
                                     sys.executable, '-c', code], timeout=15, capture_output=True)
            report = json.loads((Path(tmp)/'job-result.json').read_text())
            self.assertEqual(report['remaining_owned_processes'], 0, report)
            self.assertLessEqual((Path(tmp)/'job-console.log').stat().st_size, log)
            return result, report

    def test_normal_completion_and_quoted_arguments(self):
        result, report = self.run_job('print("space and quote: \\\" okay")')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report['stop_reason'], 0)

    def test_console_flood_is_capped(self):
        result, report = self.run_job('import sys;sys.stdout.write("x"*2000000);sys.stdout.flush()', log=4096)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(report['stop_reason'], 20)
        self.assertEqual(report['console_bytes'], 4096)

    def test_multi_ship_scratch_can_exceed_old_image_cap(self):
        # Sparse disposable file proves admission above128MiB without image dumps.
        result,report=self.run_job('import time;f=open("sparse.bin","wb");f.seek(129*1024*1024);f.write(b"x");f.close();time.sleep(.2)',disk=20_000_000_000)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(report['stop_reason'],0)
        self.assertGreater(report['peak_scratch_bytes'],128*1024*1024)

    def test_scratch_poll_stops_writer(self):
        result, report = self.run_job('import time;open("bulk.bin","wb").write(b"x"*131072);time.sleep(10)', disk=65536)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(report['stop_reason'], 21)

    def test_deadline_kills_owned_descendant_not_unrelated_process(self):
        unrelated = subprocess.Popen([sys.executable, '-c', 'import time;time.sleep(30)'])
        try:
            result, report = self.run_job('import subprocess,sys,time;subprocess.Popen([sys.executable,"-c","import time;time.sleep(30)"]);time.sleep(30)', seconds=1)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(report['stop_reason'], 22)
            self.assertIsNone(unrelated.poll())
        finally:
            unrelated.terminate()
            unrelated.wait(timeout=5)


if __name__ == '__main__':
    SCRATCH.mkdir(parents=True, exist_ok=True)
    unittest.main()

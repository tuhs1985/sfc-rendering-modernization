"""Negative startup tests: no game/renderer/child is created by these inputs."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / 'artifacts/remix-runtime/return-bin'


@unittest.skipUnless((BIN / 'return_launcher.exe').is_file(), 'Build return probe first')
class ReturnLauncherTests(unittest.TestCase):
    def rejected(self, *args):
        run = subprocess.run([str(BIN / 'return_launcher.exe'), *args],
                             capture_output=True, text=True, timeout=10)
        self.assertNotEqual(run.returncode, 0)
        self.assertNotIn('VERIFIED_CHILD', run.stdout)
        return run.stdout

    def test_original_install_refused(self):
        output = self.rejected('--game',
            r'C:\Games\Taldren Software Inc\Starfleet Command Orion Pirates\StarFleetOP.exe',
            str(BIN / 'SFCRemixReturn.dll'), '0' * 64, '0' * 64)
        self.assertIn('not the approved copied client', output)

    def test_wrong_hash_refused_before_child(self):
        output = self.rejected('--game',
            r'C:\Project\SFC-Remix-Return-Test\StarFleetOP.exe',
            str(BIN / 'SFCRemixReturn.dll'), '0' * 64, '0' * 64)
        self.assertIn('launcher SHA mismatch', output)

    def test_invalid_mode_refused(self):
        self.assertIn('launcher mode', self.rejected(
            '--unknown', 'unused', 'unused', '0' * 64, '0' * 64))


if __name__ == '__main__':
    unittest.main()

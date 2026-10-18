"""Reject ambiguous/incomplete read-only modes before file access or child launch."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1] / 'tools/remix_runtime'


class VisibilityCliTests(unittest.TestCase):
    def rejected(self, script, arguments, expected):
        run = subprocess.run([sys.executable, str(ROOT / script), *arguments],
                             capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 2)
        self.assertIn(expected, run.stderr)
        self.assertNotIn('Traceback', run.stderr)

    def test_observation_requires_earlier_scope(self):
        self.rejected('run_return_game.py', ['--observation-only'],
                      '--observation-only requires --inspect-early-depth')

    def test_early_and_late_cannot_be_combined(self):
        self.rejected('run_return_game.py',
                      ['--inspect-visibility', '--inspect-early-depth'],
                      'not allowed with argument')

    def test_fixture_depth_requires_earlier_scope(self):
        self.rejected('run_return_fixture.py', ['--with-depth'],
                      '--with-depth requires --inspect-early-depth')
    def test_expanded_search_cannot_start_remix(self):
        self.rejected('run_return_game.py', ['--search-depth'],
                      '--search-depth requires --observation-only')
    def test_broad_cannot_start_remix(self):
        self.rejected('run_return_game.py',['--broad-capture'],
                      '--broad-capture requires --observation-only')
    def test_calibration_requires_depth_only(self):
        self.rejected('run_return_game.py',['--calibration'],
                      '--calibration requires --depth-snapshots --observation-only')
    def test_depth_snapshots_cannot_start_remix(self):
        self.rejected('run_return_game.py',['--depth-snapshots'],
                      '--depth-snapshots requires --observation-only')
    def test_depth_snapshots_cannot_mix_search(self):
        self.rejected('run_return_game.py',['--depth-snapshots','--search-depth'],
                      'not allowed with argument')
    def test_broad_fixture_requires_graceful_control(self):
        self.rejected('run_return_fixture.py',['--broad-capture'],
                      '--broad-capture requires --observation-only and --graceful')


if __name__ == '__main__':
    unittest.main()

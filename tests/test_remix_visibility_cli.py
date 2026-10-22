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
    def test_scene_depth_is_not_long_tuning(self):
        self.rejected('run_return_game.py',['--scene-depth','--light-tuning'],
                      '--scene-depth is a bounded standalone test')
    def test_scene_depth_does_not_mix_calibration(self):
        self.rejected('run_return_game.py',['--scene-depth','--calibration'],
                      '--private-ship is separate from calibration/observation-only')
    def test_source_timing_cannot_start_renderer(self):
        self.rejected('run_return_game.py',['--source-timing'],'--source-timing requires observation-only')
    def test_source_timing_fixture_requires_observation(self):
        self.rejected('run_return_fixture.py',['--source-timing'],'--source-timing requires --observation-only --graceful')
    def test_additive_cannot_mix_sdk_geometry(self):
        self.rejected('run_return_game.py',['--d3d9-additive','--private-ship'],
                      '--d3d9-additive is separate from SDK/private/capture modes')
    def test_additive_cannot_mix_extended_tuning(self):
        self.rejected('run_return_game.py',['--d3d9-additive','--light-tuning'],
                      '--d3d9-additive is separate from SDK/private/capture modes')


if __name__ == '__main__':
    unittest.main()

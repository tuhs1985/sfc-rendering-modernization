import json
from pathlib import Path
import tempfile
import tomllib
import unittest
import sys
from contextlib import redirect_stderr
from io import StringIO
from unittest.mock import patch
import run_mesh_preview as preview


class PreviewTests(unittest.TestCase):
    def fixture(self, root):
        job = root/'accepted'
        (job/'output').mkdir(parents=True)
        (job/'output/ship.usda').write_text('#usda 1.0\n')
        (job/'result.json').write_text(json.dumps({'fixture': False, 'status': 'GEOMETRY_INGESTED_PREVIEW_PENDING'}))
        (job/'corner-comparison-numeric.json').write_text(json.dumps({'match': True, 'expected_triangles': 452}))
        return job

    def test_exact_asset_hash_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            job = self.fixture(Path(tmp))
            with self.assertRaises(ValueError):
                preview.verify_input(job)

    def test_fixture_or_unqualified_corners_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            job = self.fixture(Path(tmp))
            with patch.object(preview, 'digest', return_value=preview.USD_HASH):
                self.assertEqual(preview.verify_input(job), job/'output/ship.usda')
                (job/'result.json').write_text(json.dumps({'fixture': True, 'status': 'GEOMETRY_INGESTED_PREVIEW_PENDING'}))
                with self.assertRaises(ValueError):
                    preview.verify_input(job)

    def test_kit_config_is_minimal_and_registry_off(self):
        config = tomllib.loads(Path(preview.__file__).with_name('sfc_mesh_preview.kit').read_text())
        self.assertFalse(config['settings']['app']['extensions']['registryEnabled'])
        self.assertIn('lightspeed.hydra.remix.core', config['dependencies'])
        self.assertNotIn('lightspeed.app.trex.stagecraft', config['dependencies'])

    def test_textures_are_explicit_same_run_verified_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            job = self.fixture(Path(tmp))
            value = preview.digest(job/'output/ship.usda')
            (job/'job-metadata.json').write_text(json.dumps({'textures': True, 'expected_triangles': 452}))
            result = {'fixture': False, 'status': 'GEOMETRY_INGESTED_PREVIEW_PENDING',
                      'texture_preview_candidate': True, 'usd_sha256': value}
            (job/'result.json').write_text(json.dumps(result))
            self.assertEqual(preview.verify_input(job, textures=True), job/'output/ship.usda')
            with self.assertRaises(ValueError): preview.verify_input(job)
            result['usd_sha256'] = 'wrong'
            (job/'result.json').write_text(json.dumps(result))
            with self.assertRaises(ValueError): preview.verify_input(job, textures=True)

    def test_cameras_and_lights_only_session_no_save(self):
        script = Path(preview.__file__).with_name('kit_mesh_preview.py').read_text()
        self.assertIn('SetEditTarget(stage.GetSessionLayer())', script)
        self.assertNotIn('.Save(', script)
        self.assertNotIn('SetDoubleSided', script)
        self.assertLess(script.index('SetEditTarget(stage.GetSessionLayer())'), script.index('CreateOrientationAttr'))
        self.assertIn("if surface_diagnostic == 'left-handed':", script)
        self.assertIn('index_or_normal_edits', script)

    def test_preview_process_disables_default_neural_cache(self):
        self.assertEqual(preview.PREVIEW_ENV, {'DXVK_GRAPHICS_PRESET_TYPE': '4',
                                            'RTX_INTEGRATE_INDIRECT_MODE': '0'})

    def test_sponsor_camera_convention_does_not_rotate_asset(self):
        self.assertEqual(preview.VIEWS['Front'], (1,0,0))
        self.assertEqual(preview.VIEWS['Side'], (0,0,1))
        self.assertEqual(preview.ABOVE_UP, (1,0,0))

    def test_filter_diagnostic_is_explicit_session_only_and_smoke_limited(self):
        script = Path(preview.__file__).with_name('kit_mesh_preview.py').read_text()
        runner = Path(preview.__file__).read_text()
        self.assertLess(script.index('SetEditTarget(stage.GetSessionLayer())'), script.index("CreateInput('filter_mode'"))
        self.assertIn('len(shaders) != 5', script)
        self.assertIn("Sdf.ValueTypeNames.Int", script)
        self.assertIn('args.nearest_filter and (args.base_mip_only or args.sharper_mip or not args.textures or not args.smoke)', runner)

    def test_new_sampling_modes_reject_unsafe_combinations_before_preparation(self):
        cases = [ ['--nearest-filter'], ['--resident-textures'],
                 ['--surface-diagnostic', 'left-handed'],
                 ['--textures', '--resident-textures', '--surface-diagnostic', 'left-handed'],
                 ['--textures', '--resident-textures', '--smoke', '--provisional-lighting', '--surface-diagnostic', 'quarter-light'],
                 ['--provisional-lighting'], ['--textures', '--provisional-lighting'],
                 ['--textures', '--nearest-filter'], ['--smoke', '--resident-textures'],
                 ['--textures', '--smoke', '--nearest-filter', '--base-mip-only'],
                 ['--textures', '--smoke', '--resident-textures', '--sharper-mip'],
                 ['--textures', '--smoke', '--resident-textures', '--nearest-filter'] ]
        for args in cases:
            with self.subTest(args=args), patch.object(sys, 'argv', ['preview', *args]), \
                    patch.object(preview, 'prepare') as prepare, redirect_stderr(StringIO()):
                self.assertEqual(preview.main(), 1)
                prepare.assert_not_called()

    def test_residency_prepare_only_keeps_dds_and_source_intact(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            source = work/'ship.usda'
            source.write_text('#usda 1.0\n')
            (work/'preview_renderer.conf').write_text('rtx.bloom.enable = False\n')
            texture = work/'sample.dds'
            texture.write_bytes(b'original mip chain')
            before = (source.read_bytes(), texture.read_bytes())
            with patch.object(sys, 'argv', ['preview', '--textures', '--resident-textures', '--prepare-only']), \
                    patch.object(preview, 'prepare', return_value=(work, source, [])):
                self.assertEqual(preview.main(), 0)
            self.assertEqual(before, (source.read_bytes(), texture.read_bytes()))
            self.assertIn('rtx.texturemanager.neverDowngradeTextures = True', (work/'preview_renderer.conf').read_text())
            self.assertTrue(json.loads((work/'texture-residency-test.json').read_text())['textures_unchanged'])

    def test_textured_launcher_retains_separate_grey_baseline(self):
        here = Path(preview.__file__).parent
        self.assertIn('--textures --resident-textures', (here/'start_textured_preview.cmd').read_text())
        self.assertNotIn('--textures', (here/'start_mesh_preview.cmd').read_text())


if __name__ == '__main__':
    unittest.main()

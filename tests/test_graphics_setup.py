import sys
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/area) for area in ('src/launcher', 'src/runtime', 'tools/remix_runtime')]
import graphics_setup as setup
from runtime_context import packaged


class GraphicsSetupTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.context = packaged(Path(temporary.name)/'Game/SFCRemix')
        self.context.package_root.mkdir(parents=True)
        self.game = self.context.game_root
        self.old = self.game/'dxgi.dll'
        self.old.write_bytes(b'tester original')
        self.ini = self.game/'sfc.ini'
        self.ini.write_bytes(b'player settings')
        self.reshade = self.game/'ReShade.ini'
        self.reshade.write_bytes(b'[GENERAL]\nPresetPath=custom.ini\n')
        self.wrapper = self.game/'dgVoodoo.conf'
        self.wrapper.write_bytes(b'[General]\nAdapters=1\n;tester option\n')
        self.sources = {'dxgi.dll': b'qualified standard', 'DDraw.dll': b'qualified wrapper'}
        self.real_candidates = setup.candidates
        for name, options in (
            ('candidates', {'return_value': (self.sources, '0:12')}),
            ('verify_game_profile', {}),
        ):
            mock = patch.object(setup, name, **options)
            mock.start()
            self.addCleanup(mock.stop)

    @staticmethod
    def game_running():
        return False

    def prepare(self, answer='y'):
        with setup.launch_lock(self.context):
            setup.prepare_graphics(self.context, {}, self.game_running, confirm=lambda _: answer)

    def test_cancel_keeps_existing_files(self):
        with self.assertRaisesRegex(ValueError, 'cancelled'):
            self.prepare('n')
        self.assertFalse(setup.setup_root(self.context).exists())
        self.assertEqual(self.old.read_bytes(), b'tester original')
        self.assertEqual(self.reshade.read_bytes(), b'[GENERAL]\nPresetPath=custom.ini\n')

    def test_prepare_repeat_and_restore_keeps_preferences(self):
        self.prepare()
        self.assertEqual(self.old.read_bytes(), self.sources['dxgi.dll'])
        self.reshade.write_bytes(b'[GENERAL]\nPresetPath=changed.ini\n')
        self.prepare('n')  # The existing verified setup is reused without prompting.
        self.assertTrue(setup.restore(self.context, self.game_running))
        self.assertEqual(self.old.read_bytes(), b'tester original')
        self.assertEqual(self.reshade.read_bytes(), b'[GENERAL]\nPresetPath=changed.ini\n')
        self.assertEqual(self.ini.read_bytes(), b'player settings')
        self.assertEqual(self.wrapper.read_bytes(), b'[General]\nAdapters=1\n;tester option\n')

    def test_first_run_prepares_required_settings_and_gpu_without_editing_original(self):
        files = {}
        hashes = {}
        for name, role in setup.TARGETS.items():
            path = self.context.package_root/role
            path.write_bytes(role.encode('ascii'))
            files[role] = path
            hashes[name] = sha256(path.read_bytes()).hexdigest()
        before = b'[General]\r\nOutputAPI=bestavailable\r\n[DirectX]\r\nAntialiasing=appdriven\r\nFiltering=16x\r\n'
        self.wrapper.write_bytes(before)
        self.ini.write_bytes(b'[3D]\r\nWidth=1280\r\nHeight=720\r\n')
        from game_profile import wrapper_requirements, wrapper_profile
        from setup_adapter import current_setting, wrapper_config

        def probe(_context, _manifest, wrapper, preferred):
            self.assertEqual(preferred, 'all')
            wrapper_requirements(wrapper)
            self.assertEqual(wrapper_profile(wrapper)[1:], (b'1280x720', b'h:1280, v:720'))
            return wrapper_config(wrapper, '2'), '0:12'

        with patch.object(setup, 'game_profile_issues', return_value=['dgVoodoo.conf: profile needs setup']), \
             patch.object(setup, 'verified_role', side_effect=lambda _ctx, _manifest, role: files[role]), \
             patch.object(setup, 'choose', side_effect=probe):
            sources, luid = self.real_candidates(self.context, {'game_profile': {'files': hashes}})
        self.assertEqual(luid, '0:12')
        self.assertEqual(current_setting(sources['dgVoodoo.conf']), '2')
        self.assertIn(b'Filtering=16x\r\n', sources['dgVoodoo.conf'])
        self.assertEqual(self.wrapper.read_bytes(), before)
        self.assertFalse(setup.setup_root(self.context).exists())
        self.sources.update(sources)
        self.prepare()
        self.assertEqual(self.wrapper.read_bytes(), sources['dgVoodoo.conf'])
        self.assertTrue(setup.restore(self.context, self.game_running))
        self.assertEqual(self.wrapper.read_bytes(), before)

    def test_interrupted_apply_is_recovered(self):
        actual = setup.replace_file

        def interrupt(root, path, raw):
            if path.name == 'DDraw.dll':
                raise KeyboardInterrupt
            actual(root, path, raw)

        with patch.object(setup, 'replace_file', side_effect=interrupt), self.assertRaises(KeyboardInterrupt):
            self.prepare()
        self.assertEqual(self.old.read_bytes(), self.sources['dxgi.dll'])
        self.assertTrue(setup.restore(self.context, self.game_running))
        self.assertEqual(self.old.read_bytes(), b'tester original')

    def test_restore_preserves_independent_edits_and_backups(self):
        self.prepare()
        self.old.write_bytes(b'changed after setup')
        with self.assertRaisesRegex(ValueError, 'Backup retained'):
            setup.restore(self.context, self.game_running)
        self.assertEqual(self.old.read_bytes(), b'changed after setup')
        self.assertEqual((setup.setup_root(self.context)/'dxgi.dll').read_bytes(), b'tester original')


if __name__ == '__main__':
    unittest.main()

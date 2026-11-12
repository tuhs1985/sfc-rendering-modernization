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

    def test_gpu_mismatch_suggests_setting_without_replacing_wrapper(self):
        files = {}
        hashes = {}
        for name, role in setup.TARGETS.items():
            path = self.context.package_root/role
            path.write_bytes(role.encode('ascii'))
            files[role] = path
            hashes[name] = sha256(path.read_bytes()).hexdigest()
        before = self.wrapper.read_bytes()
        with patch.object(setup, 'game_profile_issues', return_value=[]), \
             patch.object(setup, 'verified_role', side_effect=lambda _ctx, _manifest, role: files[role]), \
             patch.object(setup, 'choose', return_value=(before.replace(b'Adapters=1', b'Adapters=2'), '0:12')), \
             self.assertRaisesRegex(ValueError, 'Adapters=2'):
            self.real_candidates(self.context, {'game_profile': {'files': hashes}})
        self.assertEqual(self.wrapper.read_bytes(), before)
        self.assertFalse(setup.setup_root(self.context).exists())

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

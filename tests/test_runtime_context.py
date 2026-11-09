from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/remix_runtime'))
from runtime_context import development, packaged, load


class RuntimeContextTests(unittest.TestCase):
    def test_development_preserves_existing_locations(self):
        context = development(ROOT)
        self.assertFalse(context.release)
        self.assertEqual(context.artifact('remix-runtime/return-bin'), ROOT / 'artifacts/remix-runtime/return-bin')
        self.assertEqual(context.setting('rendering.toml'), ROOT / 'tools/remix_runtime/config/rendering.toml')
        self.assertEqual(context.child_environment(), {})

    def test_package_roots_move_without_machine_paths_or_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            for directory in ('Copied SFC é', 'Moved SFC 舰'):
                root = Path(tmp) / directory / 'SFCRemix'
                context = packaged(root)
                self.assertEqual(context.game_root, root.parent)
                self.assertEqual(context.artifact('remix-runtime/deps/candidate-1.6.1'), root / 'runtime/remix-runtime/deps/candidate-1.6.1')
                self.assertEqual(context.artifact('remix-runtime/runs/session'), root / 'data/runs/session')
                self.assertEqual(context.artifact('remix-runtime/test-install'), root / 'data/baseline')
                self.assertEqual(context.setting('lights.toml'), root / 'settings/lights.toml')
                self.assertEqual(context.artifact('d3d9-proof/environment-cache'), root / 'data/cache/environment')
                self.assertEqual(context.python, root / 'python/python.exe')
                self.assertEqual(context.child_environment(), {'SFC_RELEASE_ROOT': str(root)})
                self.assertFalse(root.exists(), 'Context construction must not create or seed files')

    def test_escape_and_ambiguous_paths_rejected(self):
        context = packaged(ROOT / 'artifacts/test-temp/SFCRemix')
        for name in ('', '../outside', '/outside', 'C:/outside', 'a\\b', 'a/../b', 'a/./b', 'a//b'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                context.artifact(name)
        for name in ('../lights.toml', 'other/lights.toml', 'lights.py'):
            with self.assertRaises(ValueError):context.setting(name)
        with self.assertRaises(ValueError):packaged(ROOT / 'wrong')

    def test_explicit_release_context_does_not_depend_on_working_directory(self):
        root = ROOT / 'artifacts/test-temp/Game/SFCRemix'
        self.assertEqual(load({'SFC_RELEASE_ROOT': str(root)}), packaged(root))
        self.assertFalse(load({}).release)


if __name__ == '__main__':
    unittest.main()

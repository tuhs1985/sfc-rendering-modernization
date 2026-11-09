from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
for directory in ('release','remix_runtime','d3d9_proof','scene_bridge','remix_ingest','m1_component'):
    sys.path.insert(0,str(ROOT/'tools'/directory))
from inventory_dependencies import python_closure,RUNTIME_RESOURCES
from runtime_context import packaged
from bootstrap import check_scene_profiles


class ReleaseSceneProfilesTests(unittest.TestCase):
    def fixture(self,root):
        context=packaged(Path(root)/'SFCRemix')
        roles={role:'code/'+name for role,name in RUNTIME_RESOURCES.items()}
        for role,name in RUNTIME_RESOURCES.items():
            target=context.package_root/roles[role]
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes((ROOT/name).read_bytes())
        return context,dict(roles=roles)

    def test_import_closure_explicitly_includes_non_python_profiles(self):
        closure=python_closure(ROOT/'tools/release/bootstrap.py')
        self.assertEqual(closure['resources'],RUNTIME_RESOURCES)
        self.assertEqual(set(closure['resources'].values()),{
            'tools/d3d9_proof/multi_ship.toml','tools/d3d9_proof/offset_ship.toml'})

    def test_installed_profiles_parse_from_moved_unicode_package(self):
        with tempfile.TemporaryDirectory(prefix='SFC é ') as tmp:
            context,manifest=self.fixture(tmp)
            check_scene_profiles(context,manifest)
            self.assertFalse(context.data_root.exists())
            self.assertFalse(context.settings_root.exists())

    def test_missing_malformed_or_redirected_profile_fails_before_launch(self):
        for case in ('missing','malformed','redirected'):
            with self.subTest(case=case),tempfile.TemporaryDirectory() as tmp:
                context,manifest=self.fixture(tmp)
                target=context.package_root/manifest['roles']['scene_placement']
                if case=='missing':target.unlink()
                elif case=='malformed':target.write_text('camera_left_distance = "invalid"')
                else:manifest['roles']['scene_placement']=manifest['roles']['owner_selection']
                with self.assertRaises((OSError,ValueError)):
                    check_scene_profiles(context,manifest)
                self.assertFalse(context.data_root.exists())

    def test_actual_light_binding_uses_installed_settings_not_development_tree(self):
        import live_light_binding
        from light_transport import initialize
        from test_fast_light_transport import Channel
        with tempfile.TemporaryDirectory(prefix='SFC lights é ') as tmp:
            context=packaged(Path(tmp)/'SFCRemix')
            context.settings_root.mkdir(parents=True)
            raw=(ROOT/'tools/remix_runtime/config/lights.toml').read_bytes()
            context.setting('lights.toml').write_bytes(raw)
            gpu=context.data_root/'runs/fixture/gpu';gpu.mkdir(parents=True)
            receiver=SimpleNamespace(channel=Channel())
            receiver.name=receiver.channel.name
            initialize(receiver.channel)
            with patch.object(live_light_binding,'CONTEXT',context):
                binding=live_light_binding.Binding(gpu.parent,gpu,receiver,[0]*96,persistent=True)
            self.assertEqual(binding.config,context.setting('lights.toml'))
            self.assertEqual((gpu/'lights-config-accepted.toml').read_bytes(),raw)
            self.assertTrue((gpu/'light-shapes.bin').is_file())
            self.assertFalse((context.code_root/'tools/remix_runtime/config').exists())


if __name__=='__main__':unittest.main()

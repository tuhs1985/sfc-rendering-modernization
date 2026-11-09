from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
for directory in ('release','remix_runtime','d3d9_proof','scene_bridge','remix_ingest','m1_component'):
    sys.path.insert(0,str(ROOT/'tools'/directory))
from inventory_dependencies import production_files,RUNTIME_RESOURCES
from runtime_context import packaged


class ReleaseSceneProfilesTests(unittest.TestCase):
    def test_production_has_no_diagnostic_scene_profile_dependency(self):
        from release_manifest import REQUIRED_ROLES
        self.assertEqual(RUNTIME_RESOURCES,{})
        self.assertNotIn('scene_placement',REQUIRED_ROLES)
        self.assertNotIn('owner_selection',REQUIRED_ROLES)
        self.assertNotIn('tools/d3d9_proof/owner_selection.py',production_files())

    def test_all_appearance_controls_remain_in_production(self):
        files=production_files()
        for name in ('material_controls','image_controls','quality_controls','light_controls'):
            self.assertIn('tools/remix_runtime/'+name+'.py',files)

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

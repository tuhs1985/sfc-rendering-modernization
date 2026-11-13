import sys
from pathlib import Path
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
from runtime_context import packaged
from portable_reshade import prepare


class PortableReShadeTests(unittest.TestCase):
    def test_relative_inputs_preserved_outputs_under_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            context=packaged(Path(tmp)/'Game é space/SFCRemix')
            work=context.data_root/'runs/session';work.mkdir(parents=True)
            original=b'[GENERAL]\nEffectSearchPaths=.\\shaders\\**\nTextureSearchPaths=.\\textures\nPresetPath=.\\preset.ini\nIntermediateCachePath=C:\\old\n'
            path=context.game_root/'ReShade.ini';path.write_bytes(original)
            env=prepare(context,work)
            root=Path(env['RESHADE_BASE_PATH_OVERRIDE'])
            text=(root/'ReShade.ini').read_text(encoding='utf-8')
            self.assertIn(str(context.game_root/'shaders'/'**'),text)
            self.assertIn(str(context.game_root/'preset.ini'),text)
            self.assertIn(str(root/'cache'),text)
            self.assertIn(str(root/'screenshots'),text)
            self.assertEqual(path.read_bytes(),original)

    def test_outside_paths_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            context=packaged(Path(tmp)/'Game/SFCRemix');context.package_root.mkdir(parents=True)
            (context.game_root/'ReShade.ini').write_text('[GENERAL]\nPresetPath=../outside.ini\n')
            work=context.data_root/'run';work.mkdir(parents=True)
            with self.assertRaisesRegex(ValueError,'outside game copy'):prepare(context,work)

    def test_missing_ini_uses_session_defaults_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            context=packaged(Path(tmp)/'Game/SFCRemix')
            work=context.data_root/'run';work.mkdir(parents=True)
            prepare(context,work)
            self.assertTrue((work/'reshade/ReShade.ini').is_file())
            self.assertFalse((context.game_root/'ReShade.ini').exists())


if __name__=='__main__':unittest.main()

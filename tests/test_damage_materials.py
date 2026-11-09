import importlib.util
from pathlib import Path
import unittest
import argparse
import ast
import contextlib
import io
import sys
from unittest.mock import patch
from PIL import Image

p=Path(__file__).resolve().parents[1]/'tools/d3d9_proof/damage_materials.py'
spec=importlib.util.spec_from_file_location('damage_materials',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class DamageMaterialTests(unittest.TestCase):
    def test_exact_black_only_and_rgb_preserved(self):
        source=Image.new('RGB',(4,1));source.putdata([(0,0,0),(1,0,0),(0,0,1),(255,0,0)])
        before=source.tobytes();out=m.black_cutout(source)
        self.assertEqual(list(out.getdata()),[(0,0,0,0),(1,0,0,255),(0,0,1,255),(255,0,0,255)])
        self.assertEqual(source.tobytes(),before)
    def test_all_three_families(self):
        self.assertEqual(len(m.PAIRS),9);self.assertEqual(len({n.casefold() for pair in m.PAIRS for n in pair}),18)

class DamageLaunchDefaults(unittest.TestCase):
    def options(self,*arguments):
        # Run the actual production argument setup, stopping before any game,
        # registry, qualification, process or filesystem preparation calls.
        path=p.parents[1]/'remix_runtime/run_return_game.py'
        main=next(n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='main')
        body=[];parsed=False;after_parse=0
        for node in main.body:
            body.append(node)
            if parsed:
                after_parse+=1
                if after_parse==2:break # default resolution and play-session admission
            if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='args' for t in node.targets):parsed=True
        self.assertTrue(parsed)
        body.append(ast.Return(value=ast.Name(id='args',ctx=ast.Load())))
        fn=ast.FunctionDef(name='options',args=ast.arguments(posonlyargs=[],args=[],kwonlyargs=[],kw_defaults=[],defaults=[]),body=body,decorator_list=[])
        from runtime_context import CONTEXT
        module=ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[]));scope={'argparse':argparse,'CONTEXT':CONTEXT}
        exec(compile(module,str(path),'exec'),scope)
        with patch.object(sys,'argv',['runner',*arguments]):return scope['options']()

    def test_native_default_enables_damage(self):
        self.assertTrue(self.options('--native-all-ships').damage_textures)
    def test_explicit_disable_preserves_native_mode(self):
        options=self.options('--native-all-ships','--no-damage-textures')
        self.assertTrue(options.native_all_ships);self.assertFalse(options.damage_textures)
    def test_existing_explicit_enable_remains_supported(self):
        self.assertTrue(self.options('--native-all-ships','--damage-textures').damage_textures)
    def test_other_workflows_do_not_enable_damage(self):
        self.assertFalse(self.options().damage_textures)
    def test_conflicting_options_are_rejected(self):
        with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):
            self.options('--native-all-ships','--damage-textures','--no-damage-textures')

    def test_play_session_keeps_damage_baseline(self):
        options=self.options('--native-all-ships','--play-session')
        self.assertTrue(options.play_session);self.assertTrue(options.damage_textures)

    def test_play_session_excludes_diagnostic_capture(self):
        for flag in ('--completion-diagnostics','--light-diagnostics','--light-tuning',
                     '--lifecycle-capture','--offscreen-position','--capture-ship-image',
                     '--broad-capture','--capture-native-lights','--source-timing'):
            with self.subTest(flag=flag),contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):
                self.options('--native-all-ships','--play-session',flag)
        with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):
            self.options('--play-session')

if __name__=='__main__':unittest.main()

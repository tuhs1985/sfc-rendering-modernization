import os
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src/launcher'),str(ROOT/'tools/release'),str(ROOT/'tools/remix_runtime')]
from package_layout import copy_python,copy_remix,excluded,ARM_RUNTIME
from runtime_context import packaged
from bootstrap import prepare


class ReleaseLayoutTests(unittest.TestCase):
    def test_python_staging_excludes_only_root_build_tools_and_bytecode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'upstream'
            for name in ('include/Python.h','libs/python312.lib','Scripts/f2py.exe',
                         'python.exe','LICENSE','Lib/ctypes/__init__.py','Lib/numpy.libs/needed.dll',
                         'Lib/numpy/include/kept.h','Lib/__pycache__/old.pyc'):
                p=source/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'synthetic')
            copy_python(source,root/'installed')
            for name in ('include','libs','Scripts','Lib/__pycache__'):
                self.assertFalse((root/'installed'/name).exists())
            for name in ('python.exe','LICENSE','Lib/ctypes/__init__.py','Lib/numpy.libs/needed.dll','Lib/numpy/include/kept.h'):
                self.assertTrue((root/'installed'/name).is_file())
            self.assertTrue((source/'include/Python.h').is_file())

    def test_x64_runtime_keeps_its_libraries_and_vendor_notices(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'upstream';source.mkdir()
            for name in ('d3d9_a64ec.dll','d3d9_x64.dll','LICENSE','nvngx_dlss.dll'):(source/name).write_bytes(b'synthetic')
            copy_remix(source,root/'installed')
            self.assertFalse((root/'installed/d3d9_a64ec.dll').exists())
            for name in ('d3d9_x64.dll','LICENSE','nvngx_dlss.dll'):self.assertTrue((root/'installed'/name).exists())
            self.assertTrue(excluded(ARM_RUNTIME))
            self.assertTrue(excluded('python/Scripts/f2py.exe'))
            self.assertFalse(excluded('python/Lib/site-packages/numpy.libs/runtime.dll'))

    def test_prepare_creates_operational_directories_without_development_folders(self):
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ):
            context=packaged(Path(tmp)/'Game/SFCRemix')
            context.game_root.mkdir(parents=True);(context.game_root/'sfc.ini').write_bytes(b'baseline')
            with patch('bootstrap.seed_settings'):prepare(context,{})
            self.assertEqual({p.name for p in context.data_root.iterdir()},{'runs','baseline','cache','tmp'})


if __name__=='__main__':unittest.main()

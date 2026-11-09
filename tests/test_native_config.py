import ctypes
import os
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
from native_config import write


@unittest.skipUnless(os.name=='nt','Actual Windows native INI reader required')
class NativeConfigurationTests(unittest.TestCase):
    def test_unicode_output_and_controller_paths_reach_native_reader_exactly(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)/'Game 日本語 é space';directory.mkdir()
            config=directory/'component.ini';output=directory/'output';controller=directory/'controller.exe'
            write(config,f'[m1]\nOutputDirectory={output}\nControllerPath={controller}\nMaxSeconds=90\n')
            self.assertEqual(config.read_bytes()[:2],b'\xff\xfe')
            kernel=ctypes.WinDLL('kernel32',use_last_error=True)
            kernel.GetPrivateProfileStringW.argtypes=[ctypes.c_wchar_p]*3+[ctypes.c_wchar_p,ctypes.c_uint32,ctypes.c_wchar_p]
            kernel.GetPrivateProfileStringW.restype=ctypes.c_uint32
            for key,expected in (('OutputDirectory',output),('ControllerPath',controller)):
                value=ctypes.create_unicode_buffer(4096)
                count=kernel.GetPrivateProfileStringW('m1',key,'',value,len(value),str(config))
                self.assertEqual(value.value,str(expected));self.assertEqual(count,len(str(expected)))


if __name__=='__main__':unittest.main()

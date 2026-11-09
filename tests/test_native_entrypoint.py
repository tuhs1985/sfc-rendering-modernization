import os
from pathlib import Path
import subprocess
import unittest

EXE=Path(__file__).resolve().parents[1]/'artifacts/alpha/launcher-bin/launcher.exe'


@unittest.skipUnless(os.name=='nt' and EXE.exists(),'Built native application entry point required')
class NativeEntryPointTests(unittest.TestCase):
    def test_help_and_invalid_options_do_not_request_elevation_or_start_game(self):
        for args,expected in ((['--help'],0),(['--unexpected'],1),(['--restore','--preflight'],1)):
            result=subprocess.run([str(EXE),*args],capture_output=True,text=True,timeout=10,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            self.assertEqual(result.returncode,expected,result.stdout+result.stderr)
        self.assertIn('SFCRemix-Launch.cmd',subprocess.check_output([str(EXE),'--help'],text=True))


if __name__=='__main__':unittest.main()

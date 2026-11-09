import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
BIN=ROOT/'artifacts/remix-runtime/return-bin'
CLIENT=Path('C:/Project/SFC-Remix-Return-Test/StarFleetOP.exe')


@unittest.skipUnless(os.name=='nt' and (BIN/'return_launcher.exe').exists() and CLIENT.exists(),'Built native launcher and qualified local fixture required')
class InstalledLauncherTests(unittest.TestCase):
    def test_actual_launcher_checks_moved_unicode_package_before_creating_game(self):
        with tempfile.TemporaryDirectory() as tmp:
            game=Path(tmp)/'Game 日本語 é space';package=game/'SFCRemix'
            folder=package/'runtime/remix-runtime/return-bin';folder.mkdir(parents=True)
            exe=folder/'return_launcher.exe';addon=folder/'SFCRemixReturn.dll'
            shutil.copyfile(BIN/'return_launcher.exe',exe);shutil.copyfile(BIN/'SFCRemixReturn.dll',addon)
            shutil.copyfile(CLIENT,game/'StarFleetOP.exe')
            sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
            pin=sha(game/'StarFleetOP.exe');dll=sha(addon)
            def run(client,root=package):
                return subprocess.run([str(exe),'--check-game',str(client),str(addon),pin,dll],cwd=game,
                    env={**os.environ,'SFC_RELEASE_ROOT':str(root)},capture_output=True,text=True,timeout=30,
                    creationflags=subprocess.CREATE_NO_WINDOW)
            checked=run(game/'StarFleetOP.exe')
            self.assertEqual(checked.returncode,0,checked.stdout+checked.stderr)
            self.assertIn('LAUNCH_PREFLIGHT_PASS no_process_created=1 package_bound=1',checked.stdout)
            self.assertNotIn('VERIFIED_CHILD',checked.stdout)
            foreign=Path(tmp)/'StarFleetOP.exe';shutil.copyfile(CLIENT,foreign)
            self.assertNotEqual(run(foreign).returncode,0)
            self.assertNotEqual(run(game/'StarFleetOP.exe',game).returncode,0)
            addon.write_bytes(addon.read_bytes()+b'changed')
            self.assertNotEqual(run(game/'StarFleetOP.exe').returncode,0)


if __name__=='__main__':unittest.main()

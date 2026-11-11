"""Exercise compatibility imports and direct CLI without launching the game."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]


class SessionSeparationTests(unittest.TestCase):
    def run_python(self,*args):
        return subprocess.run([sys.executable,'-I','-B',*args],cwd=tempfile.gettempdir(),
                              capture_output=True,text=True,timeout=15)

    @unittest.skipUnless(os.name=='nt','Windows-only coordinator imports')
    def test_legacy_imports_share_canonical_modules_and_report_state(self):
        code=f"""import sys
from pathlib import Path
root=Path({str(ROOT)!r})
sys.path.insert(0,str(root/'tools/remix_runtime'))
import run_return_game,session_exit,run_report
import coordinator,exit_monitor,reports
assert run_return_game.DiagnosticSession.__base__ is coordinator.Session
assert session_exit is exit_monitor
assert run_report is reports
assert coordinator.run_report is reports
assert coordinator.NormalGameExit is exit_monitor.NormalGameExit
reports.current_folder=Path('shared-report-state')
assert run_report.current_folder==reports.current_folder
run_report.current_folder=None
assert reports.current_folder is None
print('SHARED_CANONICAL_MODULES_PASS')
"""
        result=self.run_python('-c',code)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('SHARED_CANONICAL_MODULES_PASS',result.stdout)

    @unittest.skipUnless(os.name=='nt','Windows-only coordinator imports')
    def test_direct_and_legacy_cli_admit_and_reject_same_options_before_game_access(self):
        for entry in ('src/session/coordinator.py','tools/remix_runtime/run_return_game.py'):
            for options,expected in ((['--help'],0),(['--async-material-checkout'],2)):
                with self.subTest(entry=entry,options=options):
                    result=self.run_python(str(ROOT/entry),*options)
                    self.assertEqual(result.returncode,expected,result.stderr)
                    self.assertNotIn('Traceback',result.stderr)
                    self.assertNotIn('Evidence:',result.stdout)

    def test_package_manifest_lists_application_modules_not_compatibility_tools(self):
        value=json.loads((ROOT/'tools/release/runtime_modules.json').read_text())
        names=set(value['files'])
        self.assertEqual(len(names),61)
        self.assertTrue({'src/session/coordinator.py','src/session/exit_monitor.py','src/session/reports.py'}<=names)
        for name in ('run_return_game','session_exit','run_report'):
            self.assertNotIn('tools/remix_runtime/'+name+'.py',names)

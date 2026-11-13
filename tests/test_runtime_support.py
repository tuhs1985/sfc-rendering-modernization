"""Runtime ownership, developer compatibility and diagnostic-free recovery."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
MODULES=('runtime_context','release_manifest','windows_processes','runtime_files','copied_preferences')


class RuntimeSupportTests(unittest.TestCase):
    def test_legacy_imports_execute_the_canonical_application_module_once(self):
        for order in ('legacy','application'):
            code=r'''
import importlib,sys
from pathlib import Path
root=Path(sys.argv[1]);order=sys.argv[2]
sys.path.insert(0,str(root/('tools/remix_runtime' if order=='legacy' else 'src/runtime')))
names=('runtime_context','release_manifest','windows_processes','runtime_files','copied_preferences')
first={name:importlib.import_module(name) for name in names}
for name,module in first.items():assert Path(module.__file__).resolve()==root/'src/runtime'/(name+'.py'),module.__file__
sys.path.insert(0,str(root/('src/runtime' if order=='legacy' else 'tools/remix_runtime')))
assert all(importlib.import_module(name) is module for name,module in first.items())
import recover_broad_session,session_recovery
assert recover_broad_session is session_recovery
assert Path(session_recovery.__file__).resolve()==root/'src/runtime/session_recovery.py'
print('CANONICAL_RUNTIME_IDENTITY_PASS')
'''
            with self.subTest(order=order):
                result=subprocess.run([sys.executable,'-I','-B','-c',code,str(ROOT),order],
                                      capture_output=True,text=True,timeout=15)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertIn('CANONICAL_RUNTIME_IDENTITY_PASS',result.stdout)

    def test_recovery_runs_without_broad_capture_or_any_developer_forwarder(self):
        code=r'''
import importlib.abc,json,sys,tempfile
from pathlib import Path
from unittest.mock import patch
root=Path(sys.argv[1]);sys.path[:0]=[str(root/'src/runtime'),str(root/'src/session')]
class Guard(importlib.abc.MetaPathFinder):
 def find_spec(self,fullname,path=None,target=None):
  if fullname in {'broad_capture','recover_broad_session','run_return_game','modes'}:raise AssertionError('Unexpected developer import: '+fullname)
sys.meta_path.insert(0,Guard())
import runtime_context,session_recovery as recovery,graphics_transaction as graphics
with tempfile.TemporaryDirectory() as temp:
 context=runtime_context.packaged(Path(temp)/'Game space é/SFCRemix')
 game=context.game_root;game.mkdir(parents=True)
 run=context.artifact('remix-runtime/runs')/'interrupted-in-game';run.mkdir(parents=True)
 for path,data in ((game/'dxgi.dll',b'full'),(game/'ReShade.ini',b'edited'),(game/'StarFleetOP.exe',b'client'),(run/'dxgi-original.rollback',b'original'),(run/'ReShade.original.ini',b'settings')):path.write_bytes(data)
 old=graphics.digest(run/'dxgi-original.rollback');full=graphics.digest(game/'dxgi.dll')
 baseline={'dxgi.dll':old,'ReShade.ini':graphics.digest(run/'ReShade.original.ini'),'StarFleetOP.exe':graphics.digest(game/'StarFleetOP.exe')}
 (run/'manifest.json').write_text(json.dumps({'probe':'NATIVE-COHORT-001','full_support_qualification':{'result':'RELEASE_MANIFEST_INPUTS'},'copied_critical_before':baseline}))
 with patch.multiple(recovery,CONTEXT=context,TEST=game,OLD_SHA=old,FULL_SHA=full),patch.multiple(graphics,OLD_SHA=old,FULL_SHA=full):
  try:recovery.recover_pending(lambda:True)
  except RuntimeError:pass
  else:raise AssertionError('Recovered live game')
  assert (game/'dxgi.dll').read_bytes()==b'full'
  assert recovery.recover_pending(lambda:False)
  assert (game/'dxgi.dll').read_bytes()==b'original'
  assert (game/'ReShade.ini').read_bytes()==b'settings'
  assert recovery.recover_pending(lambda:False) is None
  assert json.loads((run/'recovery.json').read_text())['game_absent_verified']
  isolated=context.artifact('remix-runtime/runs')/'isolated-in-game';isolated.mkdir()
  (isolated/'dxgi-original.rollback').write_bytes(b'original')
  (isolated/'manifest.json').write_text(json.dumps({'probe':'NATIVE-COHORT-001',
    'full_support_qualification':{'result':'RELEASE_MANIFEST_INPUTS'},
    'copied_critical_before':{**baseline,'sfc.ini':'OLD','dgVoodoo.conf':'OLD'},
    'reshade_config_isolated':True,'tester_config_owned':True}))
  (game/'dxgi.dll').write_bytes(b'full')
  (game/'ReShade.ini').write_bytes(b'tester custom settings')
  (game/'sfc.ini').write_bytes(b'tester sfc settings')
  (game/'dgVoodoo.conf').write_bytes(b'tester wrapper settings')
  assert recovery.recover_pending(lambda:False)
  assert (game/'dxgi.dll').read_bytes()==b'original'
  assert (game/'ReShade.ini').read_bytes()==b'tester custom settings'
  assert (game/'sfc.ini').read_bytes()==b'tester sfc settings'
  assert (game/'dgVoodoo.conf').read_bytes()==b'tester wrapper settings'
  assert not json.loads((isolated/'recovery.json').read_text())['config_restored']
print('APPLICATION_RECOVERY_WITHOUT_DIAGNOSTICS_PASS')
'''
        result=subprocess.run([sys.executable,'-I','-B','-c',code,str(ROOT)],
                              capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('APPLICATION_RECOVERY_WITHOUT_DIAGNOSTICS_PASS',result.stdout)

    def test_shipping_inputs_and_static_closure_select_application_support(self):
        sys.path.insert(0,str(ROOT/'tools/release'))
        from inventory_dependencies import production_files,python_closure
        files=set(production_files())
        for name in MODULES:
            self.assertIn('src/runtime/'+name+'.py',files)
            self.assertNotIn('tools/remix_runtime/'+name+'.py',files)
        self.assertIn('src/runtime/session_recovery.py',files)
        self.assertNotIn('tools/remix_runtime/recover_broad_session.py',files)
        closure=python_closure(ROOT/'src/launcher/bootstrap.py')['files']
        self.assertIn('src/runtime/session_recovery.py',closure)
        self.assertFalse(any('tools/remix_runtime/'+name+'.py' in closure for name in MODULES))
        # Static closure includes inactive qualification branches; the actual
        # execution guard above proves recovery itself never imports captures.
        self.assertIn('src/runtime/runtime_context.py',closure)


if __name__=='__main__':unittest.main()

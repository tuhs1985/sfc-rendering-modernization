import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
import run_return_game as runner
import recover_broad_session as recovery
import broad_capture as broad
import windows_processes

class StartupSafetyTests(unittest.TestCase):
    def state(self,**fields):
        return dict(gamePid=1,startupVerified=1,startupRestored=1,ready=0,error=0,**fields)
    def test_waits_for_readiness_before_return(self):
        snapshots=iter([self.state(),{**self.state(),'ready':1}]);pauses=[]
        result=runner.wait_component_ready(lambda:next(snapshots),1,lambda:None,lambda:None,
            clock=lambda:0,pause=pauses.append)
        self.assertEqual(len(pauses),1);self.assertEqual(result['ready'],1)
    def test_exit_or_error_not_retried_as_injection(self):
        for snapshot,poll in ((self.state(),lambda:0),({**self.state(),'error':1},lambda:None)):
            with self.assertRaises(RuntimeError):runner.wait_component_ready(lambda:snapshot,1,poll,lambda:None,clock=lambda:0)
    def test_timeout_without_readiness(self):
        ticks=iter([0,0,2])
        with self.assertRaisesRegex(RuntimeError,'no tactical gate injection'):
            runner.wait_component_ready(self.state,1,lambda:None,lambda:None,timeout=1,clock=lambda:next(ticks),pause=lambda _:None)
    def test_wrong_pid_cannot_satisfy_readiness(self):
        ticks=iter([0,0,2])
        with self.assertRaises(RuntimeError):runner.wait_component_ready(lambda:{**self.state(),'ready':1},2,lambda:None,lambda:None,timeout=1,clock=lambda:next(ticks),pause=lambda _:None)
    def test_multi_ship_selection_timeout_preserves_legacy_and_total_budget(self):
        self.assertEqual(runner.tactical_gate_timeout(False),90)
        self.assertEqual(runner.tactical_gate_timeout(True),120)
        self.assertLessEqual(runner.tactical_gate_timeout(True)+120+30+15,285)
    def test_only_recorded_supported_proxy_transactions_are_recoverable(self):
        for probe in ('D3D9-ADDITIVE-001','D3D9-MULTISHIP-001'):
            self.assertTrue(recovery.supported_transaction({'probe':probe,'full_support_qualification':{'result':'qualified'}}))
            self.assertFalse(recovery.supported_transaction({'probe':probe}))
        self.assertFalse(recovery.supported_transaction({'probe':'UNKNOWN','full_support_qualification':{'result':'qualified'}}))
    def test_verified_recovery_and_live_game_refusal(self):
        self.recovery_case({'broad_capture':{'enabled':True}})
    def test_verified_multi_ship_recovery_and_live_game_refusal(self):
        self.recovery_case({'probe':'D3D9-MULTISHIP-001','full_support_qualification':{'result':'qualified'}})
    def recovery_case(self,transaction):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);run=root/'artifacts/remix-runtime/runs/test-in-game';run.mkdir(parents=True)
            test=root/'test';test.mkdir();(test/'dxgi.dll').write_bytes(b'full');(test/'ReShade.ini').write_bytes(b'changed')
            (test/'StarFleetOP.exe').write_bytes(b'client')
            (run/'dxgi-original.rollback').write_bytes(b'old');(run/'ReShade.original.ini').write_bytes(b'config')
            old=broad.digest(run/'dxgi-original.rollback');full=broad.digest(test/'dxgi.dll')
            expected={'dxgi.dll':old,'ReShade.ini':broad.digest(run/'ReShade.original.ini'),'StarFleetOP.exe':broad.digest(test/'StarFleetOP.exe')}
            (run/'manifest.json').write_text(json.dumps({**transaction,'copied_critical_before':expected}))
            with mock.patch.multiple(recovery,ROOT=root,TEST=test,OLD_SHA=old,FULL_SHA=full),mock.patch.multiple(broad,OLD_SHA=old,FULL_SHA=full):
                with self.assertRaises(RuntimeError):recovery.recover(run,lambda:True)
                self.assertEqual((test/'dxgi.dll').read_bytes(),b'full')
                self.assertIsNotNone(recovery.recover_pending(lambda:False))
                self.assertEqual((test/'dxgi.dll').read_bytes(),b'old')
                self.assertEqual((test/'ReShade.ini').read_bytes(),b'config')
                self.assertIsNone(recovery.recover_pending(lambda:False))
    def test_process_discovery_failure_is_not_absence(self):
        with mock.patch.object(windows_processes,'process_names',side_effect=OSError('denied')):
            with self.assertRaises(OSError):runner.game_running()
    def test_process_discovery_checks_actual_name(self):
        with mock.patch.object(windows_processes,'process_names',return_value=['StarFleetOP.exe']):self.assertTrue(runner.game_running())
        with mock.patch.object(windows_processes,'process_names',return_value=['notStarFleetOP.exe']):self.assertFalse(runner.game_running())
    def test_ambiguous_recovery_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            for name in ('one-in-game','two-in-game'):
                run=root/'artifacts/remix-runtime/runs'/name;run.mkdir(parents=True)
                (run/'dxgi-original.rollback').write_bytes(b'backup')
                (run/'manifest.json').write_text(json.dumps({'broad_capture':{'enabled':True}}))
            with mock.patch.object(recovery,'ROOT',root),self.assertRaisesRegex(RuntimeError,'Multiple unfinished'):
                recovery.recover_pending(lambda:False)

if __name__=='__main__':unittest.main()

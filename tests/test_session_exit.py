import ctypes as C
import json
from pathlib import Path
import subprocess as sp
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
from session_exit import Monitor,NormalGameExit,retire_controller,early_without_output,partial_live_result


class SessionExitTests(unittest.TestCase):
    def test_live_game_does_no_file_io_or_wait(self):
        process=Mock();process.poll.return_value=None
        m=Monitor(process,Path('does-not-exist'))
        for _ in range(100):m.check()
        process.wait.assert_not_called()

    def test_normal_exit_is_not_an_error_at_any_observation_phase(self):
        with tempfile.TemporaryDirectory() as temp:
            log=Path(temp)/'launcher.log';log.write_text('VERIFIED_CHILD pid=1\nCHILD_EXIT code=0\n')
            for phase in ('startup','mission_selection','preparation','tactical','cleanup'):
                with self.subTest(phase=phase):
                    p=Mock();p.poll.return_value=0
                    with self.assertRaises(NormalGameExit):Monitor(p,log).check()

    def test_target_exit_preempts_launcher_receipt_race(self):
        with tempfile.TemporaryDirectory() as temp:
            log=Path(temp)/'launcher.log';log.write_text('CHILD_EXIT code=0')
            p=Mock();p.poll.return_value=None;p.wait.return_value=0
            m=Monitor(p,log);m.handle=1;m.kernel=Mock();m.kernel.WaitForSingleObject.return_value=0
            with self.assertRaises(NormalGameExit):m.check()
            p.wait.assert_called_once_with(timeout=5)

    def test_missing_or_abnormal_exit_receipt_remains_error(self):
        with tempfile.TemporaryDirectory() as temp:
            log=Path(temp)/'launcher.log';log.write_text('CHILD_EXIT code=1')
            for code in (0,1):
                p=Mock();p.poll.return_value=code
                with self.assertRaisesRegex(RuntimeError,'abnormally'):Monitor(p,log).check()

    def test_controller_is_never_terminated_for_a_live_game(self):
        p=Mock();p.poll.return_value=None
        self.assertFalse(retire_controller(p,False));p.wait.assert_not_called();p.terminate.assert_not_called()

    def test_controller_retires_without_waiting_for_observation_timer(self):
        p=Mock();p.poll.return_value=None;p.wait.return_value=8
        self.assertFalse(retire_controller(p,True));p.wait.assert_called_once_with(timeout=5)
        p.wait.side_effect=[sp.TimeoutExpired('controller',5),0]
        self.assertTrue(retire_controller(p,True));p.terminate.assert_called_once()

    def test_startup_wait_propagates_normal_exit_instead_of_waiting_for_timer(self):
        from run_return_game import wait_component_ready
        enforce=Mock(side_effect=NormalGameExit)
        snapshot=Mock();pause=Mock()
        with self.assertRaises(NormalGameExit):
            wait_component_ready(snapshot,1,Mock(),enforce,pause=pause)
        snapshot.assert_not_called();pause.assert_not_called()

    def test_normal_exit_check_precedes_worker_poll_and_cleanup_precedes_analysis(self):
        # Check orchestration, not just the monitor: cleanup must run even when
        # collection exits before the tactical observation loop has completed.
        import ast
        tree=ast.parse((ROOT/'src/session/coordinator.py').read_text())
        calls=lambda node,name:[n.lineno for n in ast.walk(node) if isinstance(n,ast.Call)
            and isinstance(n.func,ast.Attribute) and ast.unparse(n.func)==name]
        enforce=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='enforce')
        self.assertLess(calls(enforce,'exit_monitor.check')[0],calls(enforce,'timing_relay.poll')[0])
        block=next(n for n in ast.walk(tree) if isinstance(n,ast.Try)
            and any(isinstance(h.type,ast.Name) and h.type.id=='NormalGameExit' for h in n.handlers))
        final=ast.Module(body=block.finalbody,type_ignores=[])
        self.assertTrue(calls(final,'timing_relay.stop'))
        self.assertLess(calls(final,'timing_relay.stop')[0],calls(final,'timing_relay.finish')[0])
        self.assertLess(calls(final,'timing_relay.finish')[0],calls(final,'receiver.close')[0])

    def test_no_output_is_partial_but_cleanup_failures_still_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);(folder/'gpu').mkdir();job=folder/'gpu/job-result.json'
            process=Mock();process.poll.return_value=0
            relay=SimpleNamespace(process=None,selected=None,prewarm_process=process,folder=folder)
            self.assertTrue(early_without_output(relay))
            job.write_text(json.dumps(dict(exit_code=0,stop_reason='',remaining_owned_processes=0)))
            self.assertTrue(partial_live_result(relay)['normal_owned_exit'])
            job.write_text(json.dumps(dict(exit_code=0,stop_reason='',remaining_owned_processes=1)))
            with self.assertRaisesRegex(RuntimeError,'cleanup failed'):partial_live_result(relay)
            relay.error='preparation worker failed'
            with self.assertRaisesRegex(RuntimeError,'worker failure'):partial_live_result(relay)

    @unittest.skipUnless(sys.platform=='win32','Windows process-handle lifetime')
    def test_real_process_exit_handle_and_cleanup(self):
        with tempfile.TemporaryDirectory() as temp:
            log=Path(temp)/'launcher.log'
            child=sp.Popen([sys.executable,'-c','import sys;sys.stdin.readline()'],stdin=sp.PIPE,creationflags=sp.CREATE_NO_WINDOW)
            m=Monitor(child,log)
            try:
                m.attach(child.pid);m.check()
                log.write_text('CHILD_EXIT code=0');child.communicate(b'quit\n',timeout=5)
                with self.assertRaises(NormalGameExit):m.check()
            finally:
                m.close()
                if child.poll() is None:child.terminate();child.wait(timeout=5)
            self.assertIsNone(m.handle)


if __name__=='__main__':unittest.main()

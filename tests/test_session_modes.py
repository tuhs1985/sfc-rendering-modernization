"""Exercise shared lifetime and real file rollback without launching SFC."""
from contextlib import ExitStack,redirect_stdout
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock,patch

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src/session'),str(ROOT/'src/launcher'),str(ROOT/'tools/remix_runtime')]
import coordinator as app
import graphics_transaction as graphics


class SessionModesTests(unittest.TestCase):
    def test_normal_parser_defaults_and_rejects_test_modes(self):
        args=app.play_options([])
        self.assertTrue(args.play_session and args.native_all_ships)
        self.assertEqual(args.native_insertion_policy,'ExtraFrame')
        self.assertEqual(args.pipeline_mode,'performance')
        for flag in ('--completion-diagnostics','--broad-capture','--light-tuning','--capture-ship-image'):
            with self.subTest(flag=flag),redirect_stdout(io.StringIO()),patch('sys.stderr',io.StringIO()):
                with self.assertRaises(SystemExit):app.play_options([flag])

    def test_normal_exit_and_failure_restore_actual_graphics_transaction(self):
        for fail in (False,True):
            with self.subTest(fail=fail),tempfile.TemporaryDirectory() as folder,ExitStack() as stack:
                root=Path(folder);game=root/'Game space é';game.mkdir()
                bins=root/'bin';bins.mkdir();artifacts=root/'artifacts';artifacts.mkdir()
                (artifacts/'remix-runtime/runs').mkdir(parents=True)
                for name in app.CRITICAL:(game/name).write_bytes(b'fixture '+name.encode())
                (game/'sfc.ini').write_bytes(b'[3D]\nwidth=1920\nheight=1080\n[Network]\nPlayerName=Test\n')
                for name in ('return_host.exe','return_launcher.exe','SFCRemixReturn.dll'):(bins/name).write_bytes(b'helper '+name.encode())
                for name in ('m1/bin/m1_gate.dll','m1/bin/m1_controller.exe','remix-runtime/native-light-tests/m1_light_component.dll'):
                    target=artifacts/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b'fixture component')
                original={n:(game/n).read_bytes() for n in app.CRITICAL}
                replacement=root/'full.dll';replacement.write_bytes(b'qualified replacement')
                runtime=root/'runtime.dll';runtime.write_bytes(b'fixture runtime')
                events=[];state=dict(gamePid=42,startupRestored=1,startupVerified=1,ready=1,error=0)
                channel=Mock();channel.snapshot.side_effect=lambda:dict(state)
                channel.set.side_effect=lambda k,v:events.append(('control',k,v))
                channel.close.side_effect=lambda:events.append('control.close')
                receiver=Mock(name='receiver');receiver.name='Local\\SFCBridge_'+'a'*32
                receiver.close.side_effect=lambda:events.append('receiver.close')
                relay=Mock();relay.servicing=False
                relay.start_on_launch.side_effect=lambda pid:events.append('prewarm')
                relay.stop.side_effect=lambda:events.append('relay.stop')
                relay.finish_play.side_effect=lambda pid:events.append('relay.finish') or {'native_gate_summary':{}}
                processes=[]
                def launch(command,**kwargs):
                    process=Mock();process.pid=100+len(processes);process.returncode=0
                    process.poll.return_value=None
                    process.wait.side_effect=lambda **kw:process.poll.configure_mock(return_value=0) or 0
                    processes.append(process)
                    if len(processes)==1:
                        kwargs['stdout'].write(b'SESSION Local\\SFC-Remix-Return-{00000000-0000-0000-0000-000000000001}\n');kwargs['stdout'].flush()
                    elif len(processes)==2:
                        kwargs['stdout'].write(b'VERIFIED_CHILD pid=42 suspended_path_match=1 disk_sha_match=1 startup_import_only=1\n');kwargs['stdout'].flush()
                    else:
                        self.assertIn('--max-seconds',command)
                        self.assertEqual(command[command.index('--max-seconds')+1],'0')
                    return process
                monitor=Mock();checks=0
                def check():
                    nonlocal checks
                    checks+=1
                    if checks>=4:
                        processes[1].poll.return_value=0
                        with (session.work/'launcher.log').open('a') as stream:stream.write('CHILD_EXIT code=0\n')
                        if fail:raise RuntimeError('fixture renderer failed')
                        raise app.NormalGameExit()
                monitor.check.side_effect=check
                context=SimpleNamespace(release=False,artifact=lambda name:artifacts/name)
                class Prepared(app.Session):
                    def _prepare(self):
                        self.args=app.play_options(['--execute','--break-models'])
                        self.args.damage_textures=True
                        self.q={'backend_inputs':{'release':'1.6.1'}}
                        self.checkout_backend=self.q['backend_inputs']
                        return True
                session=Prepared()
                changes=dict(CONTEXT=context,SOURCE=game,TEST=game,BIN=bins,DLL=runtime,
                             CLIENT=app.digest(game/'StarFleetOP.exe'),game_running=lambda:False,
                             launcher_paths=lambda:{},compat_flags=lambda:'',image_path=lambda pid:str(game/'StarFleetOP.exe'),
                             Channel=Mock(return_value=channel),Monitor=Mock(return_value=monitor),
                             wait_component_ready=lambda *a,**k:events.append('device.ready'),
                             wait_live_gate=lambda *a,**k:events.append('tactical.ready'))
                for name,value in changes.items():stack.enter_context(patch.object(app,name,value))
                stack.enter_context(patch.object(app.C.windll.shell32,'IsUserAnAdmin',return_value=True))
                stack.enter_context(patch.object(app.sp,'Popen',side_effect=launch))
                stack.enter_context(patch.object(app.winsound,'Beep'))
                stack.enter_context(patch.object(graphics,'FULL',replacement))
                stack.enter_context(patch.object(graphics,'FULL_SHA',app.digest(replacement)))
                stack.enter_context(patch.object(graphics,'OLD_SHA',app.digest(game/'dxgi.dll')))
                stack.enter_context(patch('scene_receiver.Receiver',return_value=receiver))
                stack.enter_context(patch('async_material_checkout.Relay',return_value=relay))
                stack.enter_context(redirect_stdout(io.StringIO()))
                if fail:
                    with self.assertRaisesRegex(RuntimeError,'fixture renderer failed'):session.run()
                else:
                    session.run()
                    first_work=session.work
                    # Exit before first output, then immediately run the same
                    # entry again against the restored game/files, not a new copy.
                    processes.clear();events.clear();checks=0
                    session=Prepared();session.run()
                    self.assertNotEqual(session.work,first_work)
                self.assertEqual({n:(game/n).read_bytes() for n in app.CRITICAL},original)
                self.assertEqual(len(processes),3)
                self.assertLess(events.index('prewarm'),events.index('device.ready'))
                self.assertLess(events.index('relay.stop'),events.index('relay.finish'))
                self.assertLess(events.index('relay.finish'),events.index('receiver.close'))
                self.assertFalse(relay.completion_diagnostics or relay.light_diagnostics)
                self.assertTrue(relay.damage_textures and relay.break_models)
                config=session.config.read_text(encoding='utf-16')
                self.assertIn('MaxSeconds=0',config);self.assertIn('EnableGeometryHook=0',config)
                result=json.loads((session.work/'result.json').read_text())
                self.assertTrue(result['final_report_complete'] and result['broad_proxy_restored'])
                self.assertEqual(result['result'],'PARTIAL_PLAY_SESSION' if fail else 'PLAY_SESSION_FINISHED_NORMAL_EXIT')
                self.assertFalse(result['diagnostic_capture'])
                app.run_report.current_folder=None

    def test_normal_dependencies_import_with_diagnostic_modules_forbidden(self):
        code=r'''
import sys,importlib.abc
from pathlib import Path
root=Path(sys.argv[1])
sys.path[:0]=[str(root/'src/session'),str(root/'src/launcher'),str(root/'tools/remix_runtime'),str(root/'tools/d3d9_proof')]
blocked={'modes','broad_capture','light_discovery','depth_snapshot_analysis','run_offline','offscreen_position','native_insertion_capture','renderer_reports','present_calibration','runtime_candidate','live_bridge_review'}
class Guard(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        if fullname.split('.')[0] in blocked:raise AssertionError('Diagnostic import: '+fullname)
sys.meta_path.insert(0,Guard())
import coordinator,component_qualification,graphics_transaction,recover_broad_session
import async_material_checkout,scene_receiver,multi_scene_resources,renderer_backend
assert not blocked.intersection(sys.modules)
print('NORMAL_IMPORT_BOUNDARY_PASS')
'''
        result=subprocess.run([sys.executable,'-I','-B','-c',code,str(ROOT)],capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('NORMAL_IMPORT_BOUNDARY_PASS',result.stdout)

    def test_diagnostic_modes_reuse_process_graphics_and_mapping_lifetime(self):
        sys.path.insert(0,str(ROOT/'tools/session_diagnostics'))
        from modes import DiagnosticSession
        for name in ('run','_launch_game','_launch_controller','_wait_host','_await_device','_arm',
                     '_stop_workers','_restore_graphics','_close_mappings','_verify_files'):
            with self.subTest(method=name):self.assertIs(getattr(DiagnosticSession,name),getattr(app.Session,name))

    def test_existing_diagnostic_modes_keep_their_configuration_and_phase_policy(self):
        sys.path.insert(0,str(ROOT/'tools/session_diagnostics'))
        import modes
        class BeforePreflight(Exception):pass
        cases=(
            (['--depth-snapshots','--observation-only'],False,90),
            (['--broad-capture','--observation-only'],False,90),
            (['--source-timing','--observation-only'],True,90),
            (['--native-all-ships','--native-insertion-policy','Strict','--completion-diagnostics'],True,120),
            (['--native-all-ships','--native-insertion-policy','ExtraFrame','--break-models'],True,120),
            (['--multi-ship','--async-material-checkout','--light-tuning'],True,1800),
        )
        with patch.dict(os.environ,{},clear=False):
            for arguments,semantic,seconds in cases:
                with self.subTest(arguments=arguments),tempfile.TemporaryDirectory() as folder:
                    session=modes.DiagnosticSession(arguments)
                    with patch.object(modes,'preflight',side_effect=BeforePreflight),self.assertRaises(BeforePreflight):
                        session._prepare()
                    self.assertEqual(session.semantic_enabled,semantic)
                    session.work=Path(folder);session.pid=42;session.metadata={}
                    session.receiver=SimpleNamespace(name='Local\\SFCBridge_'+'a'*32)
                    if session.args.capture_native_lights:session.light_qualification={}
                    with redirect_stdout(io.StringIO()):session._configure_controller()
                    config=session.config.read_text(encoding='utf-16')
                    self.assertIn('MaxSeconds='+str(seconds if semantic else 90),config)
                    self.assertIn('EnableGeometryHook=0',config) if semantic else None
                    self.assertEqual(session.controller_args[session.controller_args.index('--max-seconds')+1],str(seconds))
        self.assertEqual([modes.observation_phase(x) for x in (0,30,45,60)],[0,1,2,3])
        self.assertEqual(modes.observation_phase(60,continuous=True),0)

    def test_existing_probe_entry_points_resolve_legacy_helpers(self):
        for entry in ('effect_probe/run_probe.py','early_model_probe/run_probe.py','damage_probe/run_probe.py'):
            with self.subTest(entry=entry):
                result=subprocess.run([sys.executable,'-B',str(ROOT/'tools'/entry),'--help'],
                                      cwd=tempfile.gettempdir(),capture_output=True,text=True,timeout=20)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertIn('usage:',result.stdout)


if __name__=='__main__':unittest.main()

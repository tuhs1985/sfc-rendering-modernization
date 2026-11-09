import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch
import io
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools/release'),str(ROOT/'tools/remix_runtime')]
from runtime_context import packaged
from session_recording import mark,finish,REPORT_COUNT,REPORT_BYTES
import multi_scene_resources as resources
import bootstrap


class RecordingTests(unittest.TestCase):
    def session(self,root,number=0,mode='off',restored=True):
        context=packaged(Path(root)/'SFCRemix')
        work=context.data_root/'runs'/f'20261108-190000-{number:06}-in-game'
        work.mkdir(parents=True)
        mark(work,mode)
        (work/'result.json').write_text(json.dumps(dict(final_report_complete=True,
            broad_proxy_restored=restored,normal_game_exit=True,error='sample error',result='CLOSED')))
        (work/'captured-model.bin').write_bytes(b'RUNTIME DATA NOT A REPORT')
        (work/'verbose.log').write_text('DO NOT RETAIN')
        return context,work

    def test_default_keeps_no_run_history_and_preserves_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            context,work=self.session(tmp)
            context.settings_root.mkdir();settings=context.setting('lights.toml');settings.write_text('MY SETTINGS')
            self.assertEqual(finish(context,lambda:False)['removed'],1)
            self.assertFalse(work.exists())
            self.assertFalse((context.data_root/'troubleshooting').exists())
            self.assertEqual(settings.read_text(),'MY SETTINGS')

    def test_optional_reports_rotate_without_stopping_and_contain_no_payloads(self):
        with tempfile.TemporaryDirectory() as tmp:
            for i in range(9):
                context,work=self.session(tmp,i,'minimal')
                finish(context,lambda:False)
            reports=list((context.data_root/'troubleshooting').glob('*.json'))
            self.assertEqual(len(reports),REPORT_COUNT)
            self.assertLessEqual(sum(p.stat().st_size for p in reports),REPORT_COUNT*REPORT_BYTES)
            self.assertTrue(all('verbose.log' not in p.read_text() and 'RUNTIME DATA' not in p.read_text() for p in reports))
            self.assertEqual(min(p.name for p in reports),'20261108-190000-000004-in-game.json')

    def test_interruption_and_live_game_preserve_recovery_then_clean_after_restore(self):
        with tempfile.TemporaryDirectory() as tmp:
            context,work=self.session(tmp,restored=False)
            finish(context,lambda:False);self.assertTrue(work.exists())
            (work/'recovery.json').write_text('{"proxy_restored":true}')
            self.assertTrue(finish(context,lambda:True)['deferred']);self.assertTrue(work.exists())
            finish(context,lambda:False);self.assertFalse(work.exists())

    def test_old_unmarked_evidence_is_not_deleted(self):
        with tempfile.TemporaryDirectory() as tmp:
            context,work=self.session(tmp);(work/'release-recording.json').unlink()
            finish(context,lambda:False);self.assertTrue(work.exists())

    def test_incomplete_policy_or_recovery_record_does_not_block_launch_or_delete_backup(self):
        for name in ('release-recording.json','recovery.json'):
            with self.subTest(name=name),tempfile.TemporaryDirectory() as tmp:
                context,work=self.session(tmp,restored=False)
                (work/name).write_text('{')
                finish(context,lambda:False)
                self.assertTrue(work.exists())

    def test_installed_play_has_no_evidence_quota_but_keeps_real_disk_checks(self):
        with patch.object(resources,'release_play',return_value=True):
            resources.require_capacity(100,inventory=10**15,free=10**12)
            self.assertIsNone(resources.policy()['aggregate_cap_bytes'])
            with self.assertRaisesRegex(ValueError,'disk space'):
                resources.require_capacity(100,inventory=0,free=1)

    def test_bootstrap_default_and_opt_in_hide_developer_output_and_finalize(self):
        for mode in ('off','minimal'):
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as tmp:
                context=packaged(Path(tmp)/'SFCRemix')
                context.data_root.mkdir(parents=True)
                def play():
                    self.assertEqual(os.environ['SFC_RELEASE_RECORDING'],mode)
                    print('DEVELOPMENT LINK MUST NOT APPEAR')
                    _,work=self.session(tmp,mode=mode)
                output=io.StringIO()
                with patch.object(bootstrap,'CONTEXT',context),patch.object(bootstrap,'CODE',context.code_root),\
                     patch.object(bootstrap,'verify',return_value={}),patch.object(bootstrap,'verify_game_profile'),\
                     patch.object(bootstrap,'check_scene_profiles'),patch.object(bootstrap,'check_native_launcher'),\
                     patch.object(bootstrap,'prepare'),patch('windows_processes.game_running',return_value=False),\
                     patch('recover_broad_session.recover_pending',return_value=None),patch('run_return_game.main',side_effect=play),\
                     patch.dict(os.environ),patch.object(sys,'argv',['bootstrap',*(['--troubleshoot'] if mode=='minimal' else [])]),\
                     patch('sys.stdout',output):
                    bootstrap.main()
                self.assertNotIn('DEVELOPMENT LINK',output.getvalue())
                self.assertFalse(any((context.data_root/'runs').iterdir()))
                reports=list((context.data_root/'troubleshooting').glob('*.json'))
                self.assertEqual(len(reports),int(mode=='minimal'))


GUARD=ROOT/'artifacts/remix-ingest/bin/bounded_job.exe'
@unittest.skipUnless(os.name=='nt' and GUARD.exists(),'Built Windows job guard required')
class RecordingGuardTests(unittest.TestCase):
    def test_actual_guard_does_not_end_release_play_at_recording_quota(self):
        for release,expected in ((True,0),(False,1)):
            with self.subTest(release=release),tempfile.TemporaryDirectory() as tmp:
                work=Path(tmp)
                script=work/'child.py'
                script.write_text('import pathlib,time\npathlib.Path("working.bin").write_bytes(bytes(200000))\nprint("x"*10000)\ntime.sleep(0.4)\n')
                env={**os.environ,'SFC_PLAY_SESSION':'1','SFC_PLAY_PARENT_PID':str(os.getpid())}
                env.pop('SFC_RELEASE_ROOT',None)
                if release:env['SFC_RELEASE_ROOT']=str(work/'SFCRemix')
                result=subprocess.run([str(GUARD),str(work),'0','65536','1024',sys.executable,str(script)],
                    env=env,cwd=work,capture_output=True,text=True,timeout=15)
                self.assertEqual(result.returncode,expected,result.stdout+result.stderr)
                report=json.loads((work/'job-result.json').read_text())
                self.assertEqual(report['stop_reason'],0 if release else 21)
                if release:self.assertGreater(report['console_discarded_bytes'],0)


if __name__=='__main__':unittest.main()

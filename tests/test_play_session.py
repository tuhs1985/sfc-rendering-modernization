"""Untimed helper cancellation and compact exit records; never launches SFC."""
import json
import ast
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
sys.path.insert(0,str(ROOT/'tools/d3d9_proof'))
from return_channel import Channel
from present_calibration import Receiver
import multi_scene
from multi_scene_relay import Relay


class PlaySessionTests(unittest.TestCase):
    def test_production_controller_launch_receives_session_environment(self):
        # Execute the actual production Popen expression against a guaranteed
        # invalid PID. This reaches argument admission only, never injection.
        tree=ast.parse((ROOT/'src/session/coordinator.py').read_text())
        launch=next(node.value for node in ast.walk(tree) if isinstance(node,ast.Assign)
                    and any(isinstance(t,ast.Attribute) and t.attr=='controller' for t in node.targets)
                    and isinstance(node.value,ast.Call))
        expression=compile(ast.Expression(launch),'production controller launch','eval')
        for play,seconds,expected in ((True,0,3),(False,0,2),(False,120,3)):
            with self.subTest(play=play,seconds=seconds):
                env=dict(os.environ,SFC_PLAY_SESSION='1' if play else '0')
                command=[str(ROOT/'artifacts/m1/bin/m1_controller.exe'),'--pid','4294967294',
                         '--dll','unused.dll','--config','unused.ini','--max-seconds',str(seconds)]
                state=SimpleNamespace(env=env,controller_args=command,out=lambda _:subprocess.PIPE)
                child=eval(expression,dict(sp=subprocess,ROOT=ROOT,self=state))
                output=child.communicate(timeout=5)[0].decode(errors='replace')
                self.assertEqual(child.returncode,expected,output)
                self.assertIn('OpenProcess failed' if expected==3 else 'Usage:',output)

    def test_exit_before_first_asset_keeps_small_valid_summary(self):
        receiver=Receiver()
        try:
            multi_scene.initialize(receiver.channel)
            with tempfile.TemporaryDirectory() as tmp:
                relay=SimpleNamespace(stop=Mock(),receiver=receiver,folder=Path(tmp),selected=None,
                    catalog=[],attempts=set(),image_bytes=0,partial=[],binding_events=[])
                report=Relay.finish_play(relay,os.getpid())
                relay.stop.assert_called_once()
                self.assertIsNone(report['native_cohort']);self.assertIsNone(report['native_gate_summary'])
                self.assertEqual(report['multi_scene']['qualified_assets'],0)
                self.assertEqual(report['selected'],{})
                files=list(Path(tmp).iterdir());self.assertEqual(len(files),1)
                self.assertLess(files[0].stat().st_size,2048)
                self.assertEqual(json.loads(files[0].read_text())['result'],'PLAY_SESSION_ENDED')
        finally:receiver.close()

    def control_helper(self,parent=None):
        env=dict(os.environ,SFC_PLAY_SESSION='1',SFC_PLAY_PARENT_PID=str(parent or os.getpid()))
        child=subprocess.Popen([str(ROOT/'artifacts/remix-runtime/return-bin/return_host.exe'),'--observe-only'],
            env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
        channel=None
        try:
            # The helper emits MODE and SESSION once; startup is the only wait.
            self.assertIn('OBSERVATION_ONLY',child.stdout.readline())
            name=child.stdout.readline().strip().removeprefix('SESSION ')
            channel=Channel(name)
            self.assertIsNone(child.poll())
            if parent:
                return child,channel
            channel.set('stop',1)
            child.wait(timeout=5);self.assertEqual(child.returncode,0,child.stderr.read())
        except BaseException:
            if child.poll() is None:child.terminate();child.wait(timeout=5)
            if channel:channel.close()
            raise
        if channel:channel.close()
        child.stdout.close();child.stderr.close()

    def test_passive_control_can_stop_before_first_output(self):
        self.control_helper()

    def test_supervisor_exit_retires_passive_control(self):
        parent=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)'],creationflags=subprocess.CREATE_NO_WINDOW)
        child=channel=None
        try:
            child,channel=self.control_helper(parent.pid)
            parent.terminate();parent.wait(timeout=5)
            child.wait(timeout=5);self.assertEqual(child.returncode,0,child.stderr.read())
            self.assertEqual(channel.snapshot()['stop'],1)
        finally:
            if parent.poll() is None:parent.terminate();parent.wait(timeout=5)
            if child:
                if child.poll() is None:child.terminate();child.wait(timeout=5)
                child.stdout.close();child.stderr.close()
            if channel:channel.close()


if __name__=='__main__':unittest.main()

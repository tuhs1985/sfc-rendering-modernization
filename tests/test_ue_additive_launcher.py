"""Additive launcher/controller argument compatibility; never launches SFC."""
import os,subprocess,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace as NS
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/ue_wrapper'))
from run_additive_session import AdditiveSession

class AdditiveLauncherTests(unittest.TestCase):
    def test_bounded_diagnostic_controller_uses_supported_duration(self):
        with tempfile.TemporaryDirectory() as folder:
            s=AdditiveSession.__new__(AdditiveSession)
            s.work=Path(folder);s.pid=2147483647;s.receiver=NS(name='Local\\SFCBridge_'+'a'*32)
            s.metadata={};s.args=NS(budget_seconds=285)
            s._configure_controller()
            self.assertEqual(s.controller_args[s.controller_args.index('--max-seconds')+1],'285')
            self.assertIn('MaxSeconds=285\n',s.config.read_text(encoding='utf-16'))
            env=dict(os.environ,SFC_PLAY_SESSION='0')
            result=subprocess.run(s.controller_args,env=env,capture_output=True,timeout=10)
            # An odd Windows PID cannot be a real process. Successful parsing
            # reaches OpenProcess and stops, before any DLL or target access.
            self.assertEqual(result.returncode,3,result.stdout+result.stderr)
            self.assertIn(b'OpenProcess failed',result.stderr)
            self.assertNotIn(b'Usage:',result.stderr)

if __name__=='__main__':unittest.main()

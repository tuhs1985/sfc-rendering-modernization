import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
from controller_shutdown import wait_removed


class ShutdownTests(unittest.TestCase):
    def exercise(self,end,deadline):
        now=[95.];calls=[]
        class Controller:
            def poll(self):return 0 if now[0]>=end else None
        result=wait_removed(Controller(),lambda:calls.append(now[0]),0,120,deadline,
                            clock=lambda:now[0],pause=lambda seconds:now.__setitem__(0,now[0]+seconds))
        return result,now[0],calls
    def test_short_preparation_does_not_expire_at_old_110s(self):
        result,now,calls=self.exercise(123,285)
        self.assertEqual(result,0);self.assertGreater(now,120);self.assertTrue(calls)
    def test_unresponsive_controller_remains_bounded(self):
        result,now,_=self.exercise(999,285)
        self.assertIsNone(result);self.assertLess(now,155.1)
    def test_workflow_deadline_wins(self):
        result,now,_=self.exercise(999,101)
        self.assertIsNone(result);self.assertLess(now,101.1)
    def test_failed_controller_exit_is_not_promoted_to_success(self):
        class Controller:
            def poll(self):return 8
        self.assertEqual(wait_removed(Controller(),lambda:None,0,120,285),8)
    def test_safety_failure_propagates(self):
        class Controller:
            def poll(self):return None
        def enforce():raise RuntimeError('output cap')
        with self.assertRaisesRegex(RuntimeError,'output cap'):
            wait_removed(Controller(),enforce,0,120,285,clock=lambda:100)


if __name__=='__main__':unittest.main()

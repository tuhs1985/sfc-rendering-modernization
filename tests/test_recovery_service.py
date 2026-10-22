import sys
from pathlib import Path
import threading
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/d3d9_proof'))
from recovery_service import Service


class ServiceTests(unittest.TestCase):
    def test_one_worker_drains_then_joins_before_release(self):
        observed=threading.Event();threads=[]
        def step():threads.append(threading.get_ident());observed.set()
        s=Service(step)
        try:self.assertTrue(observed.wait(2));s.check()
        finally:s.close()
        self.assertFalse(s.thread.is_alive());self.assertEqual(len(set(threads)),1)
    def test_failure_is_not_silently_accepted(self):
        def step():raise ValueError('malformed capture')
        s=Service(step);s.thread.join(2)
        with self.assertRaisesRegex(RuntimeError,'malformed capture'):s.check()
        s.close()


if __name__=='__main__':unittest.main()

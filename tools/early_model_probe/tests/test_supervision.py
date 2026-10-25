import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('early_supervision',Path(__file__).resolve().parents[1]/'supervision.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class SupervisionTests(unittest.TestCase):
    def wait(self,predicate,*,snapshot=lambda:{'error':0},poll=lambda:None,deadline=1):
        now=[0.0];self.samples=0
        def checked():self.samples+=1;return snapshot()
        module.wait_for(predicate,1,'bounded timeout',deadline=deadline,enforce=lambda:None,
                        snapshot=checked,poll=poll,clock=lambda:now[0],pause=lambda dt:now.__setitem__(0,now[0]+dt))
    def test_real_dictionary_contract_during_startup(self):
        calls=[False,False,True]
        self.wait(lambda:calls.pop(0));self.assertEqual(self.samples,3)
    def test_already_ready_still_checks_error(self):
        self.wait(lambda:True);self.assertEqual(self.samples,1)
    def test_native_error_is_not_ignored(self):
        with self.assertRaisesRegex(RuntimeError,'Native observer'):self.wait(lambda:True,snapshot=lambda:{'error':223})
    def test_child_exit_before_ready(self):
        with self.assertRaisesRegex(RuntimeError,'exited'):self.wait(lambda:False,poll=lambda:1)
    def test_normal_exit_predicate_succeeds(self):
        self.wait(lambda:True,poll=lambda:0)
    def test_timeout_remains_bounded(self):
        with self.assertRaisesRegex(RuntimeError,'bounded timeout'):self.wait(lambda:False,deadline=.1)
        self.assertEqual(self.samples,2)
    def test_malformed_channel_fails_closed(self):
        with self.assertRaises(KeyError):self.wait(lambda:True,snapshot=lambda:{})


if __name__=='__main__':unittest.main()

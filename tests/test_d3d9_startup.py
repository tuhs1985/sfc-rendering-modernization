from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/d3d9_proof'))
from startup import classify


def fixture(active='Default',works=True):
    text='SESSION 1\nTHREAD_DESKTOP=Default\nINPUT_DESKTOP='+active+'\nADAPTER_COUNT 1\nADAPTER 0 description=fixture\n'
    for fmt in (21,22,0):
        value='0x0' if works else '0x8876086a'
        text+=f'COMBINATION adapter=0 backbuffer={fmt} type={value} depth={value} create={value}\n'
    return text+f'PROBE_DONE successes={3 if works else 0} api_refs=0\n'


class NativeStartupTests(unittest.TestCase):
    def test_available_is_not_reference_pass(self):
        result=classify(fixture());self.assertEqual(result['status'],'NATIVE_STARTUP_AVAILABLE_REFERENCE_TESTS_STILL_REQUIRED')
        self.assertEqual(result['supported_adapters'],[0])

    def test_inactive_desktop_blocks_without_claiming_cause(self):
        result=classify(fixture('Screen-saver',False))
        self.assertEqual(result['status'],'BLOCKED_INACTIVE_INPUT_DESKTOP');self.assertIn('UNRESOLVED',result['cause'])

    def test_inactive_even_if_create_succeeds(self):
        self.assertEqual(classify(fixture('Other'))['status'],'BLOCKED_INACTIVE_INPUT_DESKTOP')

    def test_awake_unsupported_remains_blocked(self):
        self.assertEqual(classify(fixture(works=False))['status'],'BLOCKED_NATIVE_DEVICE_UNAVAILABLE')

    def test_incomplete_ambiguous_and_count_mismatch_reject(self):
        for text in (fixture().replace('INPUT_DESKTOP=Default','INPUT_DESKTOP_error=5'),
                     fixture()+'INPUT_DESKTOP=Other\n',fixture().replace('backbuffer=0','backbuffer=21'),
                     fixture().replace('successes=3','successes=0')):
            with self.subTest(text=text),self.assertRaises(ValueError):classify(text)

    def test_retained_api_refs_reject(self):
        with self.assertRaises(ValueError):classify(fixture().replace('api_refs=0','api_refs=1'))


if __name__=='__main__':unittest.main()

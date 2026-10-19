from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
import light_discovery
from test_native_light_controls import packet


class LightDiscoveryTests(unittest.TestCase):
    def test_summary_retains_enabled_hole_and_no_light_name_guess(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'raw.bin';path.write_bytes(packet())
            r=light_discovery.analyze(path)
            self.assertEqual(r['records'],1)
            bank=r['banks']['65536']
            self.assertTrue(bank['slots']['2']['ever_enabled'])
            self.assertFalse(bank['slots']['2']['ever_consumed'])
            self.assertEqual(bank['prefix_values'],[1])

    def test_malformed_and_repeated_records_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'raw.bin'
            for raw in (b'',packet()[:-1],packet()+packet()):
                path.write_bytes(raw)
                with self.assertRaises(ValueError):light_discovery.analyze(path)

    def test_runner_uses_dedicated_binary_and_resets_environment(self):
        source=(Path(__file__).resolve().parents[1]/'tools/remix_runtime/run_return_game.py').read_text()
        self.assertIn("env.pop('SFC_NATIVE_LIGHT_DISCOVERY',None)",source)
        self.assertIn("native-light-tests/m1_light_component.dll",source)
        self.assertIn('require_light_qualification()',source)


if __name__=='__main__':unittest.main()

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'tools/m1_component/prepare_m1_c01_packet.py'
SPEC = importlib.util.spec_from_file_location('c01_packet', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PacketTests(unittest.TestCase):
    def test_windows_preserve_continuation_and_exclude_unrelated_code(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'dump.txt'
            path.write_text('  004162B9: 55 push ebp\n continuation\n'
                            '  0042E4B2: 55 push ebp\n'
                            '  006ABF80: 53 push ebx\n'
                            '  00700000: 90 nop\n unrelated\n')
            result = MODULE.select_windows(path)
            self.assertIn(' continuation', result['ship_transform_handoff'])
            self.assertFalse(any('unrelated' in line for lines in result.values()
                                 for line in lines))

    def test_missing_window_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'dump.txt'
            path.write_text('004162B9: nop\n')
            with self.assertRaises(ValueError):
                MODULE.select_windows(path)

    def test_client_mismatch_rejected_before_disassembly(self):
        with patch.object(MODULE, 'digest', return_value='BAD'):
            with self.assertRaises(ValueError):
                MODULE.prepare(Path('client'), Path('dump'))

    def test_packet_does_not_promote_input_contract(self):
        with patch.object(MODULE, 'digest', return_value=MODULE.CLIENT_SHA256), \
                patch.object(MODULE, 'select_windows', return_value={'fixture': []}):
            result = MODULE.prepare(Path('client'), Path('dump'))
            self.assertEqual(result['status'], 'INPUT_QUALIFICATION_PENDING')
            self.assertIn('coordinate space', result['unresolved'])

    def test_historical_owner_and_sample_are_not_live_structure_claims(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'events.csv'
            path.write_text('event,owner_id,return_address,ship,visual,model0,source,'
                            'elapsed_ms,tint_applied,tint_original_rgb\n'
                            'model0,1,0x0042FDD5,0x10,0x20,0x30,0x40,1,1,0x00FFFFFF\n')
            result = MODULE.owner_evidence(path)
            self.assertEqual(result['owners'][1]['identity_changes'], 0)
            self.assertIn('not a source distribution', result['limitation'])


if __name__ == '__main__':
    unittest.main()

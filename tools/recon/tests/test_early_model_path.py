import csv
import io
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from verify_early_model_path import ANCHORS, qualify_rows, historical_trace


class FakeImage:
    def read(self, va, size):
        return b'\x90' * size


class EarlyModelTests(unittest.TestCase):
    def rows(self):
        return [(va, b'\x90', op, args) for va, (op, args) in ANCHORS.items()]

    def test_all_named_path_anchors_required(self):
        rows, calls = qualify_rows(FakeImage(), self.rows())
        self.assertEqual(len(rows), len(ANCHORS))
        self.assertIn(0x0041574E, calls)

    def test_missing_anchor_rejects(self):
        with self.assertRaisesRegex(ValueError, 'missing/changed'):
            qualify_rows(FakeImage(), self.rows()[1:])

    def test_changed_pe_byte_rejects(self):
        rows = self.rows()
        va, _, op, args = rows[0]
        rows[0] = va, b'\xCC', op, args
        with self.assertRaisesRegex(ValueError, 'PE mismatch'):
            qualify_rows(FakeImage(), rows)

    def test_duplicate_instruction_rejects(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            qualify_rows(FakeImage(), self.rows() + self.rows()[:1])

    def trace(self, *, md5='abc', caller='0x0042F5DC', second_sequence='2', duplicate_meta=False):
        s = io.StringIO()
        w = csv.writer(s)
        w.writerow(['kind', 'elapsed_ms', 'sequence_or_event', 'event_or_detail', 'eip', 'return_or_stack0'])
        w.writerow(['META', 0, 'target_md5', md5])
        if duplicate_meta:
            w.writerow(['META', 0, 'target_md5', 'different'])
        w.writerow(['META', 0, 'image_base', '0x00400000'])
        w.writerow(['META', 0, 'probe_point', 'one'])
        w.writerow(['META', 0, 'probe_point', 'two'])
        w.writerow(['SAMPLE', 100, 1, 'model_parse', '0x0042FEF9', caller])
        w.writerow(['SAMPLE', 130, second_sequence, 'geometry_submit', '0x006AB410', '0x006AC503'])
        return s.getvalue()

    def review(self, text):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / 'old.csv'
            p.write_text(text, encoding='utf-8')
            return historical_trace(p, 'abc')

    def test_old_evidence_is_entry_not_readiness(self):
        r = self.review(self.trace())
        self.assertEqual(r['events']['model_parse']['first_ms'], 100)
        self.assertIn('no named asset', r['interpretation'])
        self.assertNotIn('ready_ms', r)

    def test_wrong_client_rejects(self):
        with self.assertRaisesRegex(ValueError, 'identity'):
            self.review(self.trace(md5='wrong'))

    def test_conflicting_identity_rejects(self):
        with self.assertRaisesRegex(ValueError, 'Conflicting'):
            self.review(self.trace(duplicate_meta=True))

    def test_wrong_parser_caller_rejects(self):
        with self.assertRaisesRegex(ValueError, 'origin'):
            self.review(self.trace(caller='0x00000000'))

    def test_duplicate_sequence_rejects(self):
        with self.assertRaisesRegex(ValueError, 'sequence'):
            self.review(self.trace(second_sequence='1'))


if __name__ == '__main__':
    unittest.main()

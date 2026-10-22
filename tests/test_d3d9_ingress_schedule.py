from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/d3d9_proof'))
from analyze_ingress import assess


class IngressScheduleTests(unittest.TestCase):
    def row(self, sequence, on_time=1):
        return dict(sequence=sequence, source_frame=44, offered_qpc=100, deadline_qpc=116,
                    completed_qpc=110 if on_time else 140, frequency=1000, on_time=on_time)

    def test_late_then_skip_and_recover(self):
        result = assess([self.row(74), self.row(75, 0), self.row(78)], 75)
        self.assertEqual(result['late_sequences'], [75])
        self.assertEqual(result['first_on_time_after_injected_lag'], 78)
        self.assertEqual(result['omitted_source_sequences'], 297)

    def test_reject_repeated_out_of_order_and_false_success(self):
        for rows in ([self.row(2), self.row(2)], [self.row(2), self.row(1)]):
            with self.assertRaises(ValueError):
                assess(rows)
        bad = self.row(1)
        bad['completed_qpc'] = bad['deadline_qpc']
        with self.assertRaises(ValueError):
            assess([bad])

    def test_keep_late_costs_and_no_automatic_pass(self):
        result = assess([self.row(1, 0), self.row(2)])
        self.assertEqual(result['source_to_receiver_ack_ms']['max'], 40)
        self.assertEqual(result['late_completions'], 1)
        self.assertNotIn('PASS', result.get('result', ''))

    def test_bad_frequency(self):
        rows = [self.row(1), self.row(2)]
        rows[1]['frequency'] = 2000
        with self.assertRaises(ValueError):
            assess(rows)


if __name__ == '__main__':
    unittest.main()

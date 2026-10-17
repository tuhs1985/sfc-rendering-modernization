import copy
import unittest
from tools.m1_component.analyze_m1_corner_snapshot import analyze


def fixture():
    matrix = [0] * 17
    for index in (0, 5, 10, 15):
        matrix[index] = 0x3F800000
    records = []
    for owner in (1, 2):
        for window in range(6):
            records.append({'owner': owner, 'thread': 1, 'window': window, 'elapsed_ms': window * 5000,
                            'ship': owner * 100, 'visual': owner * 200, 'model': owner * 300,
                            'source': owner * 400, 'manager': 50, 'vertex_count': 3, 'status': 0,
                            'sample_truncated': False, 'object_transform': matrix.copy(),
                            'position_transform': matrix.copy(), 'dispatch': [0, 0, 0],
                            'polygons': [[1000, 0, 3, 35, 0, 0, 0]],
                            'corners': [[0, 0, 0x3F800000, 0, 0, 0, 0, 0],
                                        [0, 1, 0, 0x3F800000, 0, 0, 0, 0]]})
    return {'schema': 'm1.c01.corners.v1', 'captured': 12, 'written': 12,
            'output_truncated': False, 'records': records}


class CornerAnalysisTests(unittest.TestCase):
    def epoch_fixture(self):
        data = fixture()
        base = [data['records'][0], data['records'][6]]
        data['records'] = []
        for index, prototype in enumerate(base):
            for window in range(18):
                sample = copy.deepcopy(prototype)
                sample.update(filter=index, window=window, elapsed_ms=window * 5000)
                sample['owner'] = index + 1 if window < 4 else index + 3
                data['records'].append(sample)
        mask = (1 << 18) - 1
        data.update(schema='m1.c01.corners.v3', captured=36, written=36,
                    filters=[[base[i]['ship'], base[i]['visual'], i + 3, mask, mask, 0, 0] for i in (0, 1)],
                    transitions=[[20000, 3, i, i + 1, i + 3, 1, base[i]['visual']] for i in (0, 1)],
                    transition_dropped=0, outside_filter_calls=0)
        return data

    def test_epoch_aware_coverage_does_not_merge_identity(self):
        report = analyze(self.epoch_fixture())
        self.assertFalse(report['issues'])
        self.assertFalse(report['identity_continuity_across_epochs_asserted'])
        self.assertFalse(report['records'][4]['object_transform_changed'])
        self.assertEqual(report['records'][4]['owner'], 3)
        self.assertFalse(report['coverage'][0]['missing_snapshot_windows'])
        self.assertFalse(report['normal_space_qualified'])

    def test_epoch_mismatch_and_ledger_saturation_are_visible(self):
        data = self.epoch_fixture()
        data['transition_dropped'] = 10
        data['filters'][0][6] = 2
        self.assertEqual(len(analyze(data)['issues']), 2)
        data['records'][0]['visual'] = 999
        with self.assertRaises(ValueError):
            analyze(data)

    def test_v2_expanded_budget_and_late_motion(self):
        data = fixture()
        base = [data['records'][0], data['records'][6]]
        data['records'] = []
        for owner_sample in base:
            for window in range(18):
                sample = copy.deepcopy(owner_sample)
                sample['window'] = window
                sample['elapsed_ms'] = window * 5000
                if window >= 10:
                    sample['object_transform'][3] = 0x3F800000
                data['records'].append(sample)
        data.update(schema='m1.c01.corners.v2', captured=36, written=36)
        result = analyze(data)
        self.assertFalse(result['issues'])
        self.assertTrue(result['records'][10]['object_transform_changed'])
        self.assertEqual(result['records'][17]['requested_action'], 'ship_turn_camera_angle_held')
        self.assertFalse(result['normal_space_qualified'])

    def test_reports_sharing_not_space_pass(self):
        report = analyze(fixture())
        self.assertEqual(report['status'], 'INPUT_EVIDENCE_READY_FOR_LEAD_REVIEW')
        self.assertFalse(report['normal_space_qualified'])
        self.assertEqual(report['records'][0]['source_groups_with_multiple_vector_bit_patterns'], [0])

    def test_camera_matrix_change_is_not_object_change(self):
        data = fixture()
        data['records'][1]['position_transform'][3] = 0x3F800000
        report = analyze(data)['records'][1]
        self.assertTrue(report['position_transform_changed'])
        self.assertFalse(report['object_transform_changed'])

    def test_nonfinite_data_not_promoted(self):
        data = fixture()
        data['records'][0]['corners'][0][2] = 0x7FC00000
        self.assertTrue(analyze(data)['issues'])

    def test_cross_association_not_promoted(self):
        data = fixture()
        data['records'][1]['visual'] = 123
        self.assertTrue(analyze(data)['issues'])

    def test_missing_owner_and_guard_failure(self):
        data = fixture()
        data['records'] = data['records'][:6]
        data['captured'] = data['written'] = 6
        data['records'][0]['status'] = 1
        self.assertTrue(analyze(data)['issues'])

    def test_duplicate_and_oversized_packets_refused(self):
        data = fixture()
        data['records'][1] = copy.deepcopy(data['records'][0])
        with self.assertRaises(ValueError):
            analyze(data)
        data = fixture()
        data['records'] *= 2
        with self.assertRaises(ValueError):
            analyze(data)


if __name__ == '__main__':
    unittest.main()

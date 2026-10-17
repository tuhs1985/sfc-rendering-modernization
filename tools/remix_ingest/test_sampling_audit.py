import unittest
from preview_sampling_audit import collect


class SamplingAuditTests(unittest.TestCase):
    def test_published_values_are_not_claimed_as_native_state(self):
        values={'/rtx': {'texture': {'mipBias': 2}, 'unrelated': 7}}
        result=collect(values, (1024,640))
        self.assertEqual(result['published_kit_values']['/rtx/texture/mipBias'], 2)
        self.assertNotIn('/rtx/unrelated', result['published_kit_values'])
        self.assertFalse(result['settings_written'])
        self.assertIn('NOT_EXPOSED', result['native_gpu_sampled_mip'])
        self.assertEqual(values['/rtx']['texture']['mipBias'], 2)

    def test_missing_is_not_zero_and_large_trees_are_bounded(self):
        result=collect({}, (1024,640))
        self.assertFalse(result['queried_roots_present']['/rtx'])
        values={'/rtx': {'texture'+str(i): i for i in range(10000)}}
        result=collect(values, (1024,640))
        self.assertTrue(result['truncated'])
        self.assertLessEqual(len(result['published_kit_values']), 256)

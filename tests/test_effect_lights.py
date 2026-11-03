import ctypes as C
import struct
import sys
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools/remix_runtime'),str(ROOT/'tools/d3d9_proof')]
import effect_lights as e
from test_fast_light_transport import Channel

class EffectTests(unittest.TestCase):
    def test_old_configs_leave_effects_off(self):
        self.assertFalse(any(r['enabled'] for r in e.controls({})))
    def test_config_defaults_and_individual_override(self):
        rows=e.controls(dict(effects=dict(enabled=True,intensity_multiplier=2),effect_lights=[dict(slot=3,color_multiplier=[0,1,.5])]))
        self.assertEqual(len(rows),62);self.assertEqual(rows[1]['color_multiplier'],[0,1,.5]);self.assertEqual(rows[1]['intensity_multiplier'],2)
        self.assertEqual(rows[0]['color_multiplier'],[1,1,1])
    def test_master_off_wins_over_override(self):
        self.assertFalse(any(r['enabled'] for r in e.controls(dict(effects=dict(enabled=False),effect_lights=[dict(slot=2,enabled=True)]))))
    def test_unknown_nonfinite_and_duplicate_rejected(self):
        for data in (dict(effects=dict(shape='spot')),dict(effects=dict(radius=float('nan'))),dict(effect_lights=[dict(slot=64)]),dict(effect_lights=[dict(slot=2),dict(slot=2)])):
            with self.subTest(data=data),self.assertRaises(ValueError):e.controls(data)
    def test_actual_fixed_channel_config_and_enable_switch(self):
        c=Channel();e.initialize(c);rows=e.publish(c,dict(effects=dict(enabled=True,intensity_multiplier=2)),7)
        self.assertTrue(rows[0]['enabled']);self.assertEqual(struct.unpack('<I',c.read(e.SOURCE_OFFSET+40,4))[0],1)
        raw=c.read(e.CONFIG_OFFSET+80,1512)
        from live_lights import fnv
        self.assertEqual(struct.unpack_from('<4I',raw),(e.CONFIG_MAGIC,1,1512,7));self.assertEqual(struct.unpack_from('<Q',raw,1504)[0],fnv(raw[:1504]))
        self.assertEqual(struct.unpack_from('<3f',raw,20),(2,2,2))
        e.publish(c,dict(effects=dict(enabled=False)),8);self.assertEqual(struct.unpack('<I',c.read(e.SOURCE_OFFSET+40,4))[0],0)
    def test_native_conversion_and_master_apply_without_changing_scene_controls(self):
        c=Channel();e.initialize(c);e.publish(c,dict(conversion_scale=2,master_multiplier=.5,effects=dict(enabled=True,intensity_multiplier=3)),1)
        self.assertEqual(struct.unpack('<3f',c.read(e.CONFIG_OFFSET+100,12)),(3,3,3))

if __name__=='__main__':unittest.main()

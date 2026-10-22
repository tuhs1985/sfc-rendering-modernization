from pathlib import Path
import math
import struct
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/scene_bridge'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/d3d9_proof'))
from simulation_pose import pose
from live_light_binding import world_light_context

class PoseTests(unittest.TestCase):
    def row(self):
        identity=[float(i//4==i%4) for i in range(16)]
        return dict(base_position=[10,20,30],position=[2,3,4],base_angles=[0,0,0],ship_angles_raw=[0,0,0],
            rotation_words=list(struct.unpack('<16I',struct.pack('<16f',*identity)))+[0x100])
    def test_base_position_and_added_offset_not_render_cache(self):
        row=self.row();row['cache_words']=[0]*17;p=pose(row)
        self.assertEqual([p[i] for i in (3,7,11)],[12,23,34]);self.assertAlmostEqual(p[6],-1)
        row['base_position'][0]=50;self.assertEqual(pose(row)[3],52)
    def test_native_angle_period_and_rotation_order(self):
        row=self.row();a=pose(row);row['base_angles'][0]=8192
        self.assertEqual(pose(row),a);row['ship_angles_raw'][2]=2048;p=pose(row)
        self.assertAlmostEqual(p[1],-1);self.assertAlmostEqual(p[8],1)
    def test_nonfinite_rejected(self):
        row=self.row();row['base_position'][0]=float('nan')
        with self.assertRaises(ValueError):pose(row)
    def test_world_light_context_is_explicit_derived_copy(self):
        original=dict(owner_epoch=1,model_process_local=2,source_process_local=3,slots=[dict(native_type=0),dict(native_type=0)])
        row=[0]*96;row[1]=4;row[5]=5;row[6]=6
        mapped=world_light_context(original,row)
        self.assertEqual(original['owner_epoch'],1);self.assertEqual(mapped['owner_epoch'],4)
        self.assertIs(original['slots'],mapped['slots'])
        original['slots'][1]['native_type']=1
        with self.assertRaises(ValueError):world_light_context(original,row)

if __name__=='__main__':unittest.main()

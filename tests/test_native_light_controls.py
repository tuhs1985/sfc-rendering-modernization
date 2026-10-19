import copy
import math
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
import light_controls as controls
import native_light_state as native


class LightControlsTests(unittest.TestCase):
    def setUp(self):
        self.registry={'scene-reviewed':{'kind':'directional'},'effect-reviewed':{'kind':'point'}}
        self.data=dict(schema_version=1,backend='remix_sdk_0_6_4',lights=[dict(id='scene-reviewed')])

    def test_example_is_honestly_empty(self):
        path=Path(__file__).resolve().parents[1]/'tools/remix_runtime/config/lights.example.toml'
        self.assertEqual(controls.load(path,{}),[])

    def test_supported_values_and_direction(self):
        self.data['lights'][0].update(enabled=False,intensity_multiplier=2,direction_override=[0,-2,0])
        out=controls.validate(self.data,self.registry)[0]
        self.assertFalse(out['enabled']);self.assertEqual(out['direction_override'],[0,-1,0])
        self.assertEqual(out['intensity_multiplier'],2)

    def test_no_fake_per_light_ray_toggle(self):
        self.data['lights'][0]['raytracing']='off'
        with self.assertRaisesRegex(ValueError,'no qualified per-light'):controls.validate(self.data,self.registry)

    def test_invalid_or_unqualified_controls_rejected(self):
        for extra in ({'id':'slot0-sun-guessed'},{'radius':1},{'enabled':1},
                      {'intensity_multiplier':float('nan')},{'intensity_multiplier':-1},
                      {'color_multiplier':[1,1]},{'direction_override':[0,0,0]},
                      {'invented_control':True}):
            data=copy.deepcopy(self.data);data['lights'][0].update(extra)
            with self.assertRaises(ValueError):controls.validate(data,self.registry)
        self.data['lights']*=2
        with self.assertRaises(ValueError):controls.validate(self.data,self.registry)

    def test_point_shape(self):
        self.data['lights']=[dict(id='effect-reviewed',radius=.2,position_offset=[1,2,3])]
        self.assertEqual(controls.validate(self.data,self.registry)[0]['radius'],.2)


def packet():
    raw=bytearray(native.SIZE)
    struct.pack_into('<16I',raw,0,0x54494c4e,1,native.SIZE,1,1,2,3,4,2,100,1000,0x10000,0x20000,0x30000,4,0)
    raw[4296:4299]=bytes([1,0,1]);struct.pack_into('<I',raw,6152,1)
    return raw


class NativeLightDecodeTests(unittest.TestCase):
    def test_prefix_and_later_enable_preserved(self):
        r=native.decode(packet());self.assertEqual(r['consumed_prefix'],1)
        self.assertTrue(r['slots'][0]['consumed_by_native_response'])
        self.assertEqual(r['slots'][2]['enabled_byte'],1)
        self.assertFalse(r['slots'][2]['consumed_by_native_response'])
        self.assertNotIn('sun',r['slots'][0]['interpretation'])

    def test_gate_and_native_type_not_directx_enum(self):
        raw=packet();struct.pack_into('<I',raw,200,5);struct.pack_into('<I',raw,6152,0)
        r=native.decode(raw);self.assertFalse(r['slots'][0]['consumed_by_native_response'])
        self.assertEqual(r['slots'][0]['interpretation'],'special_positional_unknown')

    def test_nonfinite_kept_as_words_not_json_nan(self):
        raw=packet();struct.pack_into('<f',raw,204,float('nan'))
        r=native.decode(raw);self.assertIsNone(r['slots'][0]['values'])
        self.assertEqual(r['slots'][0]['numeric_status'],'NONFINITE_NOT_USABLE')

    def test_malformed_identity_and_size(self):
        for offset in (0,4,8,12,32,36,44,48,52,56):
            raw=packet();struct.pack_into('<I',raw,offset,0)
            with self.assertRaises(ValueError):native.decode(raw)
        with self.assertRaises(ValueError):native.decode(packet()[:-1])


if __name__=='__main__':unittest.main()

import copy
import struct
import tempfile
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
import light_controls as controls
import light_shapes
from live_lights import REGISTRY,fnv

class Shapes(unittest.TestCase):
    def data(self,kind):return dict(schema_version=1,backend='remix_sdk_0_6_4',lights=[dict(id=f'native_directional_{i}',type=kind if i==1 else 'directional') for i in range(2)])
    def test_any_type_for_either_native_light(self):
        for kind in light_shapes.TYPES:
            for i in range(2):
                data=self.data('directional');data['lights'][i]['type']=kind
                self.assertEqual(controls.validate(data,REGISTRY)[i]['shape']['type'],kind)
    def test_invalid_shapes_and_multiple_domes(self):
        for extra in ({'type':'guess'},{'space':'camera'},{'axis':[0,0,0]},{'radius':0},
                      {'width':float('nan')},{'cone_softness':2},{'environment_image':1}):
            data=self.data('dome');data['lights'][1].update(extra)
            with self.assertRaises(ValueError):controls.validate(data,REGISTRY)
        data=self.data('dome');data['lights'][0]['type']='dome'
        with self.assertRaises(ValueError):controls.validate(data,REGISTRY)
    def test_companion_layout_uniform_dome_and_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            rows=controls.validate(self.data('dome'),REGISTRY)
            packet,manifest=light_shapes.build({r['id']:r for r in rows},7,directory,directory)
            self.assertEqual(len(packet),808)
            self.assertEqual(struct.unpack_from('<Q',packet,16)[0],7)
            self.assertEqual(struct.unpack_from('<I',packet,292)[0],1)
            self.assertEqual(struct.unpack_from('<Q',packet,800)[0],fnv(packet[:800]))
            image=Path(directory)/'textures'/manifest[1]['prepared_environment']
            self.assertTrue(image.read_bytes().startswith(b'DDS '))
            self.assertEqual(len(list(image.parent.glob('*.dds'))),1)
            light_shapes.build({r['id']:r for r in rows},8,directory,directory)
            self.assertEqual(len(list(image.parent.glob('*.dds'))),1)
    def test_missing_environment_is_not_substituted(self):
        with tempfile.TemporaryDirectory() as directory:
            data=self.data('dome');data['lights'][1]['environment_image']='missing.png'
            rows=controls.validate(data,REGISTRY)
            with self.assertRaises(OSError):light_shapes.build({r['id']:r for r in rows},1,directory,directory)

    def test_independent_project_dome_and_single_environment_bound(self):
        data=self.data('directional')
        data['lights'].append(dict(id='project_fill',type='dome',enabled=True,intensity_multiplier=.05))
        with tempfile.TemporaryDirectory() as directory:
            rows=controls.validate(data,REGISTRY)
            result,manifest=light_shapes.build({r['id']:r for r in rows},1,directory,directory)
            self.assertEqual(struct.unpack_from('<4I',result,544),(2,1,1,1))
            rgb=struct.unpack_from('<3f',result,544+16+15*4)
            self.assertAlmostEqual(rgb[0],.05)
            self.assertEqual(manifest[2]['id'],'project_fill')
        data['lights'][1]['type']='dome'
        with self.assertRaises(ValueError):controls.validate(data,REGISTRY)

    def test_project_light_can_change_type_too(self):
        for kind in light_shapes.TYPES:
            data=self.data('directional');data['lights'].append(dict(id='project_fill',type=kind,enabled=True))
            self.assertEqual(controls.validate(data,REGISTRY)[2]['shape']['type'],kind)

if __name__=='__main__':unittest.main()

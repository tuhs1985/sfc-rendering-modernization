import io
from pathlib import Path
import struct
import sys
import unittest
from unittest.mock import patch
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
for name in ('d3d9_proof','remix_runtime','scene_bridge'):sys.path.insert(0,str(ROOT/'tools'/name))
from remix_coordinates import bgra,base_image
from material_binding import encode_remix_material_dds
from parallel_assets import Pipeline

class RemixCoordinateTests(unittest.TestCase):
    def original(self):
        im=Image.new('RGBA',(2,3));im.putdata([(255,0,0,255),(0,255,0,128),(0,0,255,255),(64,32,16,255),(255,255,0,0),(0,255,255,255)])
        return dict(image=im,bgra=im.tobytes('raw','BGRA'),metadata=dict(width=2,height=3),raw=b'original-file',sha256='source-hash')

    def test_first_upload_and_enhanced_map_have_identical_mapping(self):
        original=self.original();before=original['image'].tobytes();converted=base_image(original)
        with Image.open(io.BytesIO(encode_remix_material_dds(original['image']))) as decoded:
            self.assertEqual(converted['bgra'],decoded.convert('RGBA').tobytes('raw','BGRA'))
        self.assertEqual(converted['bgra'][:8],original['bgra'][-8:])
        self.assertNotEqual(converted['bgra'],original['bgra'])
        self.assertEqual(original['image'].tobytes(),before)
        self.assertEqual(original['raw'],converted['raw']);self.assertEqual(original['sha256'],converted['sha256'])
        self.assertIs(original['image'],converted['image'])

    def test_material_identity_matches_first_uploaded_bytes(self):
        original=self.original();p=object.__new__(Pipeline);p.values=()
        job=dict(gpu=ROOT,manifest={'textures':[dict(filename='a',width=2,height=3)]},
                 capture=(None,None,None,{'refs':{'resources':[]},'groups':[]}),images={'a':original})
        with patch('mesh_checksum.texture_identity',return_value=0xabc) as identity:
            self.assertEqual(p._materials(job)[1],['abc'])
        identity.assert_called_once_with(base_image(original)['bgra'],2,3)

    def test_reference_conversion_does_not_accept_arbitrary_texture_bytes(self):
        from qualify_async_material import reference_adaptation
        original=self.original();raw=struct.pack('<4I',0x31544653,2,3,len(original['bgra']))+original['bgra']
        key='run/gpu/assets/1/texture-0.bin'
        class Archive:
            def read(self,name):return raw
        converted,names=reference_adaptation(Archive(),{key:{}},'1')
        self.assertEqual(converted['texture-0.bin'],raw[:16]+base_image(original)['bgra'])
        self.assertEqual(len(names),1)
        old,new=next(iter(names.items()));self.assertEqual(len(old),20);self.assertEqual(len(new),20)
        self.assertNotEqual(old,new)

    def test_shared_owner_reference_accepts_only_declared_pose(self):
        from qualify_async_material import coherent_fixture_frame
        from scene_bundle import FRAME
        def words(values):return struct.unpack('<16I',struct.pack('<16f',*values))
        identity=[1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.]
        row=[0]*96;row[1]=31;row[7]=63;row[2]=200000
        for a in (8,49,66):row[a:a+17]=[*words(identity),0x100]
        row[83:89]=struct.unpack('<6I',struct.pack('<6f',200,30,1720,1020,860,510))
        rows=struct.pack('<96I',*row)*4
        prefix=struct.pack('<8I',1,1,3,3,1,1,1920,1080)+bytes(3*32+3*4+16)
        frame=FRAME.pack(31,63,200100,1,*identity,*identity,*identity,200,30,1720,1020)
        old=prefix+FRAME.pack(3,3,200001,1,*identity,*identity,*identity,200,30,1720,1020)
        self.assertTrue(coherent_fixture_frame(old,prefix+frame,rows))
        altered=bytearray(prefix+frame);struct.pack_into('<f',altered,len(prefix)+16+12,99.)
        self.assertFalse(coherent_fixture_frame(old,altered,rows))
        self.assertFalse(coherent_fixture_frame(old,prefix+frame,bytes(384*4)))

    def test_qualifier_pose_check_imports_in_clean_process(self):
        import subprocess
        code="import sys;sys.path[:0]="+repr([str(ROOT/'tools'/n) for n in ('remix_runtime','d3d9_proof','scene_bridge')])+";from qualify_async_material import coherent_fixture_frame;assert not coherent_fixture_frame(bytes(32),bytes(31),bytes(1536))"
        result=subprocess.run([sys.executable,'-B','-c',code],capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_bad_layout_rejected_and_single_row_unchanged(self):
        for raw,w,h in [(b'',2,3),(b'1234',0,1),(b'1234',1,4097)]:
            with self.assertRaises(ValueError):bgra(raw,w,h)
        self.assertEqual(bgra(b'12345678',2,1),b'12345678')

if __name__=='__main__':unittest.main()

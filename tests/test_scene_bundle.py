import io
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/scene_bridge'))
from scene_bundle import MAGIC,FRAME,read_replay,resolve_image,texture,prepare


def replay():
    eye=[1.,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]
    vertices=[(0.,0,0,0,0,1,0,0),(1.,0,0,0,0,1,1,0),(0.,1,0,0,0,1,0,1)]
    return (struct.pack('<8I',MAGIC,1,3,3,1,1,960,540)+
            b''.join(struct.pack('<8f',*v) for v in vertices)+struct.pack('<3I',0,1,2)+
            struct.pack('<4I',7,0,0,3)+FRAME.pack(1,2,3,1,*eye,*eye,*eye,200,30,1720,1020))


class SceneBundleTests(unittest.TestCase):
    def decode(self,raw):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'scene.bin';path.write_bytes(raw);return read_replay(path)

    def test_preserves_corner_uv_normals_groups_identity(self):
        data=self.decode(replay())
        self.assertEqual(data['vertices'][1],(1,0,0,0,0,1,1,0))
        self.assertEqual(data['groups'],[(7,0,0,3)])
        self.assertEqual(data['frames'][0][:4],(1,2,3,1))

    def test_schema_and_length_rejections(self):
        for raw in (b'',replay()[:-1],replay()+b'X',bytes(32)):
            with self.subTest(length=len(raw)),self.assertRaises(ValueError):self.decode(raw)
        for index,value in ((0,0),(1,2),(2,32769),(3,4),(4,257),(5,17),(6,1921),(7,1081)):
            raw=bytearray(replay());struct.pack_into('<I',raw,index*4,value)
            with self.subTest(header=index),self.assertRaises(ValueError):self.decode(raw)

    def test_nonfinite_geometry_and_transform(self):
        for offset in (32,32+3*32+3*4+16+16):
            raw=bytearray(replay());struct.pack_into('<f',raw,offset,math.nan)
            with self.assertRaises(ValueError):self.decode(raw)

    def test_indices_and_groups(self):
        for offset,value in ((32+3*32,3),(32+3*32,1),(32+3*32+12+8,1),(32+3*32+12+12,0)):
            raw=bytearray(replay());struct.pack_into('<I',raw,offset,value)
            with self.assertRaises(ValueError):self.decode(raw)

    def test_frame_and_viewport(self):
        start=32+3*32+12+16
        for offset,value in ((start,0),(start+12,2)):
            raw=bytearray(replay());struct.pack_into('<I',raw,offset,value)
            with self.assertRaises(ValueError):self.decode(raw)
        raw=bytearray(replay());struct.pack_into('<f',raw,len(raw)-16,-1)
        with self.assertRaises(ValueError):self.decode(raw)

    def test_texture_origin_and_encoded_pixels(self):
        from PIL import Image
        image=Image.new('RGB',(2,2));image.putdata([(255,0,0),(0,255,0),(0,0,255),(255,255,0)])
        output=io.BytesIO();image.save(output,format='BMP');meta,bgra=texture(output.getvalue())
        self.assertEqual((meta['width'],meta['height']),(2,2))
        self.assertEqual(bgra,bytes([0,0,255,255,0,255,0,255,255,0,0,255,0,255,255,255]))

    def test_alpha_and_path_escape(self):
        from PIL import Image
        output=io.BytesIO();Image.new('RGBA',(1,1),(0,0,0,0)).save(output,format='PNG')
        with self.assertRaises(ValueError):texture(output.getvalue())
        with tempfile.TemporaryDirectory() as directory:
            for name in ('../outside.bmp','C:/Windows/not-an-image.bmp','missing.bmp'):
                with self.subTest(name=name),self.assertRaises(ValueError):resolve_image(directory,name)

    def test_neutral_module_has_no_backend_import(self):
        import ast
        tree=ast.parse((ROOT/'tools/scene_bridge/scene_bundle.py').read_text())
        modules=[n.module or '' for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
        self.assertFalse(any('remix_runtime' in n or 'pxr' in n for n in modules))
        # Existing captured-format validator is reused,not a renderer dependency.
        self.assertIn('live_scene',modules)

    def test_prepare_keeps_capture_session_and_original_provenance(self):
        import numpy as np
        from PIL import Image
        base=ROOT/'artifacts/readme-validation-temp';base.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as directory:
            folder=Path(directory);source=folder/'LIVE-SCENE-001-asset-1.bin'
            source.write_bytes(b'capture');source.with_suffix('.json').write_bytes(b'{}')
            session='Local\\SFCBridge_'+'a'*32
            metadata=folder/'run-metadata.json';metadata.write_text(json.dumps(dict(live_channel=session)))
            points=[(-.5,-.5,-2),(.5,-.5,-2),(0,.5,-2)]
            model=np.eye(4);projection=np.array([[.5625,0,0,0],[0,1,0,0],[0,0,-1.01,-.1],[0,0,-1,0]])
            vp=np.array([[960,0,0,960],[0,-540,0,540],[0,0,1,0],[0,0,0,1]])
            def words(matrix,affine=False):return list(struct.unpack('<16I',struct.pack('<16f',*matrix.flat)))+[256 if affine else 0]
            row=[0]*96;row[1]=7;row[2]=3;row[4:8]=[1,9,11,1];row[48]=1
            row[8:25]=words(model,True);row[25:42]=words(vp@projection@model)
            row[49:66]=words(model,True);row[66:83]=words(projection)
            row[83:89]=list(struct.unpack('<6I',struct.pack('<6f',0,0,1920,1080,960,540)))
            (folder/'LIVE-SCENE-001-updates.jsonl').write_text(json.dumps(row)+'\n')
            header=[0]*64;header[4]=7;header[6]=3;header[10]=9;header[12]=11
            mesh=dict(header=header,points=points,used_points=points,corners=[(i,(0,0,1),uv) for i,uv in enumerate(((0,1),(1,1),(.5,0)))],
                groups=[dict(group=5,flags=1,primary=17)],polygons=[(5,0)],geometry_sha256='b'*64,
                refs=dict(resources=[dict(id=17,filename='image.bmp')],model_filename='fixture.mod'))
            Image.new('RGB',(2,2),(123,45,67)).save(folder/'image.bmp')
            with patch('scene_bundle.decode_mesh',return_value=mesh):manifest=prepare(source,folder/'out',folder)
            self.assertEqual(manifest['source_session'],session)
            self.assertEqual(manifest['source_metadata_sha256'],hashlib.sha256(metadata.read_bytes()).hexdigest())
            self.assertEqual(manifest['textures'][0]['original_sha256'],hashlib.sha256((folder/'image.bmp').read_bytes()).hexdigest())
            self.assertEqual(read_replay(folder/'out/scene.bin')['vertices'][0][-2:],(0,1))
            with patch('scene_bundle.decode_mesh',return_value=mesh),self.assertRaises(ValueError):prepare(source,folder/'out',folder)
            metadata.write_text('{}')
            with patch('scene_bundle.decode_mesh',return_value=mesh),self.assertRaises(ValueError):prepare(source,folder/'bad-session',folder)


if __name__=='__main__':unittest.main()

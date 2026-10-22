import pathlib
import io
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/d3d9_proof'))
import material_binding as binding


class NormalMaterialBinding(unittest.TestCase):
    values=[.4,5,.2,.5,1,.9,0,1,0,.4]

    def test_generated_dds_roundtrip_and_unchanged_encoding_offline(self):
        # Full decode deliberately lives only in this small offline regression.
        image=Image.new('RGBA',(3,2))
        image.putdata([(1,2,3,4),(255,0,17,128),(0,255,31,255),
                       (19,23,29,0),(41,43,47,83),(101,103,107,109)])
        reference=io.BytesIO();image.save(reference,format='DDS')
        data=binding.encode_generated_dds(image)
        self.assertEqual(data,reference.getvalue())
        with Image.open(io.BytesIO(data)) as decoded:
            self.assertEqual(decoded.convert('RGBA').tobytes(),image.tobytes())

    def test_runtime_encoding_does_not_reopen_or_decode(self):
        with patch.object(Image,'open',side_effect=AssertionError('Runtime readback')):
            binding.encode_generated_dds(Image.new('RGBA',(2,3)))

    def test_remix_derivative_origin_only_and_all_channels_preserved(self):
        image=Image.new('RGBA',(2,3))
        image.putdata([(1,2,3,4),(5,6,7,8),(9,10,11,12),(13,14,15,16),(17,18,19,20),(21,22,23,24)])
        before=image.tobytes()
        raw=binding.encode_remix_material_dds(image)
        with Image.open(io.BytesIO(raw)) as decoded:
            self.assertEqual(decoded.convert('RGBA').tobytes(),image.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes())
        self.assertEqual(image.tobytes(),before)
        with patch.object(Image,'open',side_effect=AssertionError('Runtime decode')):
            binding.encode_remix_material_dds(image)

    def test_generated_dds_rejects_wrong_sizes_and_modes(self):
        for size in ((0,1),(4097,1),(1,4097)):
            with self.assertRaises(ValueError):binding.validate_generated_dds(b'',size)
        with self.assertRaises(ValueError):binding.encode_generated_dds(Image.new('RGB',(1,1)))
        data=binding.encode_generated_dds(Image.new('RGBA',(2,3)))
        for bad in (b'',data[:127],data[:-1],data+b'\0'):
            with self.assertRaises(ValueError):binding.validate_generated_dds(bad,(2,3))
        with self.assertRaises(ValueError):binding.validate_generated_dds(data,(3,2))

    def test_generated_dds_rejects_unsupported_headers(self):
        data=binding.encode_generated_dds(Image.new('RGBA',(2,3)))
        for index in range(32):
            bad=bytearray(data);value=struct.unpack_from('<I',bad,index*4)[0]
            struct.pack_into('<I',bad,index*4,value^1)
            with self.subTest(header_word=index),self.assertRaises(ValueError):
                binding.validate_generated_dds(bad,(2,3))

    def test_original_maps_bound_separately(self):
        text=binding.shader('0123456789ABCDEF',dict(color='textures/a.dds',roughness='textures/b.dds',emission='textures/c.dds'),self.values)
        self.assertIn('mat_0123456789ABCDEF',text)
        self.assertIn('inputs:diffuse_texture = @textures/a.dds@',text)
        self.assertIn('inputs:reflectionroughness_texture = @textures/b.dds@',text)
        self.assertIn('inputs:emissive_mask_texture = @textures/c.dds@',text)
        self.assertIn('inputs:emissive_intensity = 5',text)

    def test_no_emission_is_explicit(self):
        text=binding.shader('0123456789ABCDEF',dict(color='textures/a.dds'),self.values)
        self.assertIn('inputs:enable_emission = false',text)
        self.assertNotIn('inputs:emissive_mask_texture',text)

    def test_no_geometry_in_material_layer(self):
        text=binding.shader('0123456789ABCDEF',dict(color='textures/a.dds'),self.values)
        self.assertNotIn('def Mesh',text)
        self.assertNotIn('xformOp',text)

    def test_rejects_bad_identity(self):
        for identity in ('1','0'*15+'G','0'*15+'\n'):
            with self.assertRaises(ValueError):binding.shader(identity,dict(color='textures/a.dds'),self.values)

    def test_rejects_injected_paths(self):
        for path in ('../a.dds','C:/a.dds','a@.dds','a".dds'):
            with self.assertRaises(ValueError):binding.shader('0'*16,dict(color=path),self.values)

    @unittest.skipUnless(binding.HASHER.exists(),'native pinned hash helper not built')
    def test_native_identity_and_invalid_packet(self):
        with tempfile.TemporaryDirectory() as folder:
            p=pathlib.Path(folder)/'texture.bin'
            p.write_bytes(struct.pack('<4I',0x31544653,64,1,256)+bytes(256))
            def run():return subprocess.run([str(binding.HASHER),str(p)],capture_output=True,text=True,timeout=5)
            first=run();self.assertEqual(first.returncode,0)
            self.assertRegex(first.stdout.strip(),r'^[0-9a-f]{1,16}$')
            p.write_bytes(p.read_bytes()[:-1]+b'\x01');self.assertNotEqual(first.stdout,run().stdout)
            p.write_bytes(p.read_bytes()[:-1]);self.assertNotEqual(run().returncode,0)

    @unittest.skipUnless(binding.HASHER.exists(),'native pinned hash helper not built')
    def test_native_batch_matches_single_file(self):
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder);expected=[]
            for i in range(3):
                p=root/f'texture-{i}.bin';p.write_bytes(struct.pack('<4I',0x31544653,8,1,32)+bytes([i])*32)
                expected.append(subprocess.check_output([str(binding.HASHER),str(p)],text=True,timeout=5).strip())
            result=subprocess.run([str(binding.HASHER),'--batch',folder,'3'],capture_output=True,text=True,timeout=5)
            self.assertEqual(result.returncode,0);self.assertEqual(result.stdout.splitlines(),expected)
            bad=subprocess.run([str(binding.HASHER),'--batch',folder,'257'],capture_output=True,timeout=5)
            self.assertNotEqual(bad.returncode,0)


if __name__=='__main__':unittest.main()

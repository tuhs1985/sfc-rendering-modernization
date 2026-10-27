import pathlib
import io
import struct
import subprocess
import sys
import tempfile
import unittest
import json
import hashlib
from types import SimpleNamespace
from unittest.mock import patch
from PIL import Image

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/d3d9_proof'))
import material_binding as binding


class NormalMaterialBinding(unittest.TestCase):
    values=[.4,5,.2,.5,1,.9,0,1,0,.4]

    def fixture(self,root,folder,*,secondary_change=False):
        root.mkdir(exist_ok=True);folder.mkdir()
        for name,color in [('primary',(80,120,200,255)),('secondary',(200,80,20,255)),('other',(20,40,60,255))]:
            Image.new('RGBA',(3,2),color).convert('RGB').save(root/f'{name}.bmp')
        packet=root/'capture.bin';packet.write_bytes(b'validated upstream geometry')
        refs={'textures_enabled':1,'resources':[{'id':i,'filename':f'{name}.bmp'} for i,name in enumerate(('primary','secondary','other'),1)],
              'groups':[{'group':i,'primary':1,'secondary':3 if secondary_change and i else 2,'flags':0x21} for i in range(2)]}
        packet.with_suffix('.json').write_text(json.dumps(refs))
        meta,bgra=binding.texture((root/'primary.bmp').read_bytes())
        (folder/'texture-0.bin').write_bytes(struct.pack('<4I',0x31544653,3,2,len(bgra))+bgra)
        sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
        scene={'source_packet':'capture.bin','source_packet_sha256':sha(packet),'source_references_sha256':sha(packet.with_suffix('.json')),
               'textures':[{'original_sha256':sha(root/'primary.bmp')}],'groups':[[0,0,0,3],[1,0,3,3]]}
        (folder/'scene.json').write_text(json.dumps(scene))

    def test_performance_reuses_inputs_and_derivatives_with_exact_test_mode_output(self):
        config=(ROOT/'tools/remix_runtime/config/rendering.toml').read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            root=pathlib.Path(temp);a=root/'a';b=root/'b'
            self.fixture(root,a);self.fixture(root,b)
            with patch.object(binding,'ROOT',root),patch.object(binding.subprocess,'run',return_value=SimpleNamespace(stdout='1\n')):
                with patch.object(binding,'encode_remix_material_dds',wraps=binding.encode_remix_material_dds) as encode:
                    fast=binding.prepare(a,root,config,evidence_mode='performance')
                    self.assertEqual(encode.call_count,3)
                with patch.object(binding,'encode_remix_material_dds',wraps=binding.encode_remix_material_dds) as encode:
                    checked=binding.prepare(b,root,config,evidence_mode='test')
                    self.assertEqual(encode.call_count,6)
            for key in ('mod_sha256','images','groups','image_bytes'):self.assertEqual(fast[key],checked[key])
            self.assertFalse(fast['source_recomparison']);self.assertTrue(checked['source_recomparison'])

    def test_test_mode_detects_changed_source_but_performance_trusts_upstream(self):
        config=(ROOT/'tools/remix_runtime/config/rendering.toml').read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            root=pathlib.Path(temp);a=root/'a';b=root/'b';self.fixture(root,a);self.fixture(root,b)
            (root/'capture.bin').write_bytes(b'changed after upstream preparation')
            with patch.object(binding,'ROOT',root),patch.object(binding.subprocess,'run',return_value=SimpleNamespace(stdout='1\n')):
                with self.assertRaisesRegex(ValueError,'association changed'):binding.prepare(b,root,config,evidence_mode='test')
                binding.prepare(a,root,config,evidence_mode='performance')

    def test_performance_preserves_conflicting_secondary_identity_rejection(self):
        config=(ROOT/'tools/remix_runtime/config/rendering.toml').read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            root=pathlib.Path(temp);folder=root/'a';self.fixture(root,folder,secondary_change=True)
            with patch.object(binding,'ROOT',root),patch.object(binding.subprocess,'run',return_value=SimpleNamespace(stdout='1\n')):
                with self.assertRaisesRegex(ValueError,'conflicting image pairs'):binding.prepare(folder,root,config,evidence_mode='performance')

    def test_small_decode_cache_eviction_preserves_output(self):
        config=(ROOT/'tools/remix_runtime/config/rendering.toml').read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            root=pathlib.Path(temp);a=root/'a';b=root/'b';self.fixture(root,a);self.fixture(root,b)
            with patch.object(binding,'ROOT',root),patch.object(binding.subprocess,'run',return_value=SimpleNamespace(stdout='1\n')):
                normal=binding.prepare(a,root,config,evidence_mode='performance')
                with patch.object(binding,'DECODE_CACHE_BYTES',24):small=binding.prepare(b,root,config,evidence_mode='performance')
            self.assertEqual(normal['images'],small['images']);self.assertEqual(normal['mod_sha256'],small['mod_sha256'])

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

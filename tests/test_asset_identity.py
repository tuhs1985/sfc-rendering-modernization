import pathlib
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools/d3d9_proof'),str(ROOT/'tools/scene_bridge')]
from mesh_checksum import asset_identity,texture_identity
from multi_scene import prepared_packet,file_packet,fnv


class NativeAssetIdentityTests(unittest.TestCase):
    def test_catalog_hash_matches_existing_contract_including_nuls(self):
        for raw in (b'x',b'\0'*256,bytes(range(256))*256):
            self.assertEqual(asset_identity(raw),fnv(raw))
        for raw in (b'',bytearray(b'x'),None):
            with self.assertRaises(ValueError):asset_identity(raw)

    def test_texture_hash_matches_pinned_existing_helper(self):
        helper=ROOT/'artifacts/d3d9-proof/material-bin/texture_hash.exe'
        with tempfile.TemporaryDirectory() as temp:
            for width,height in ((1,1),(3,2),(64,64)):
                raw=bytes((i%251 for i in range(width*height*4)))
                path=pathlib.Path(temp)/'texture.bin';path.write_bytes(struct.pack('<4I',0x31544653,width,height,len(raw))+raw)
                expected=int(subprocess.check_output([str(helper),str(path)],text=True,timeout=5).strip(),16)
                self.assertEqual(texture_identity(raw,width,height),expected)
        for raw,w,h in ((b'',1,1),(bytes(4),1.0,1),(bytes(4),0,1),(bytes(4),4097,1)):
            with self.assertRaises(ValueError):texture_identity(raw,w,h)

    def test_prepared_catalog_byte_exact_against_native_file_helper(self):
        # Original native utility remains the independent offline oracle.
        with tempfile.TemporaryDirectory(dir=ROOT/'artifacts/render-survey/test-temp') as temp:
            folder=pathlib.Path(temp);replay=b'scene fixture\0';images=[]
            (folder/'scene.bin').write_bytes(replay)
            for i in range(2):
                raw=struct.pack('<4I',0x31544653,3,2,24)+bytes([i])*24
                images.append(raw);(folder/f'texture-{i}.bin').write_bytes(raw)
            row=[0]*96
            for i in (1,5,6,7):row[i]=i
            combined=14695981039346656037
            for raw in images:combined=((combined^asset_identity(raw))*1099511628211)&0xffffffffffffffff
            fields=[len(replay),sum(map(len,images)),asset_identity(replay),combined]
            self.assertEqual(prepared_packet(1,1,row,'ab'*32,fields),file_packet(1,1,row,'ab'*32,folder,2))
            for bad in ([0,*fields[1:]],[2*1024*1024+1,*fields[1:]],[1,128*1024*1024+1,1,1]):
                with self.assertRaises(ValueError):prepared_packet(1,1,row,'ab'*32,bad)


if __name__=='__main__':unittest.main()

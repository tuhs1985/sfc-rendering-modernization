import ctypes as C
import hashlib
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import os
import subprocess
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools/remix_runtime'),str(ROOT/'tools/d3d9_proof'),str(ROOT/'tools/remix_ingest')]
import environment_resources as env

class Channel:
    name='Local\\SFCBridge_'+'a'*32
    def __init__(self):self.buffer=C.create_string_buffer(65536);self.view=C.addressof(self.buffer)
    def read(self,o,n):return C.string_at(self.view+o,n)
    def write(self,o,b):C.memmove(self.view+o,b,len(b))

class EnvironmentTests(unittest.TestCase):
    def test_actual_config_packet_and_immutable_publication(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);c=Channel();report=env.publish(c,123,root,cache=root/'cache')
            self.assertEqual(c.read(env.OFFSET,8),struct.pack('<2I',1,0))
            raw=c.read(env.OFFSET+8,env.PACKET.size);p=env.PACKET.unpack(raw)
            self.assertEqual(p[:4],(0x31564e45,1,1912,123));self.assertEqual(p[4:8],(0xaaaaaaaa,)*4)
            self.assertEqual(p[10],hashlib.sha256((ROOT/'tools/remix_runtime/config/lights.toml').read_bytes()).digest())
            self.assertTrue(report['project_dome_prepared']);self.assertEqual(len(list((root/'cache').glob('*.dds'))),1)
            with self.assertRaises(ValueError):env.publish(c,123,root,cache=root/'cache')
            self.assertEqual(c.read(env.OFFSET+8,env.PACKET.size),raw)
    def test_cache_reuse_preserves_bytes_and_timestamp(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);raw=b'DDS test bytes';source=root/(hashlib.sha256(raw).hexdigest()+'.dds');source.write_bytes(raw)
            target=env.cache_image(source,root/'cache');stamp=target.stat().st_mtime_ns
            self.assertEqual(env.cache_image(source,root/'cache'),target)
            self.assertEqual(target.read_bytes(),raw);self.assertEqual(target.stat().st_mtime_ns,stamp)
            target.write_bytes(b'corrupt')
            with self.assertRaises(ValueError):env.cache_image(source,root/'cache')
            self.assertEqual(target.read_bytes(),b'corrupt')
    def test_failed_preparation_does_not_publish(self):
        with tempfile.TemporaryDirectory() as temp:
            c=Channel()
            with patch.object(env,'cache_image',side_effect=ValueError('cache unavailable')):
                with self.assertRaises(ValueError):env.publish(c,123,Path(temp),cache=Path(temp)/'cache')
            self.assertEqual(c.read(env.OFFSET,env.STORE_BYTES),bytes(env.STORE_BYTES))
    def test_packet_rejects_bad_identity_and_shapes(self):
        with tempfile.TemporaryDirectory() as temp:
            c=Channel();root=Path(temp);env.publish(c,123,root,cache=root/'cache')
            p=env.PACKET.unpack(c.read(env.OFFSET+8,env.PACKET.size));shapes=p[-2]
            for session,pid,producer in [('bad',123,1),(c.name,0,1),(c.name,123,0)]:
                with self.assertRaises(ValueError):env.encode(session,pid,producer,b'config',shapes,root)
            broken=bytearray(shapes);broken[-1]^=1
            with self.assertRaises(ValueError):env.encode(c.name,123,1,b'config',broken,root)
    def test_non_dome_configuration_stays_non_dome(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);config=root/'lights.toml'
            original=(ROOT/'tools/remix_runtime/config/lights.toml').read_text()
            self.assertIn('type = "dome"',original)
            config.write_text(original.replace('type = "dome"','type = "directional"'))
            c=Channel();report=env.publish(c,123,root,config,root/'cache')
            self.assertFalse(report['project_dome_prepared'])
            self.assertEqual(list((root/'cache').glob('*.dds')),[])
    def test_cache_bound_and_content_filename(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/'bad.dds';source.write_bytes(b'bytes')
            with self.assertRaises(ValueError):env.cache_image(source,root/'cache')
            source=root/(hashlib.sha256(b'bytes').hexdigest()+'.dds');source.write_bytes(b'bytes')
            with patch.object(env,'LIMIT',4):
                with self.assertRaises(ValueError):env.cache_image(source,root/'cache')

class EnvironmentNativeTests(unittest.TestCase):
    def run_probe(self,mode,mutate=None):
        from live_scene import SceneChannel
        from warm_start import initialize,cancel
        exe=ROOT/'artifacts/player-replacement/environment-tests/probe.exe'
        if not exe.exists():self.skipTest('Build environment preparation probe first')
        with tempfile.TemporaryDirectory() as temp:
            c=SceneChannel(create=True)
            try:
                process=subprocess.Popen([str(exe),c.name,mode],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
                try:
                    initialize(c,process.pid);env.publish(c,process.pid,Path(temp),cache=Path(temp)/'cache')
                    if mutate:mutate(c,cancel)
                    output=process.communicate('\n',timeout=20)[0]
                    self.assertEqual(process.returncode,0,output)
                    return output
                finally:
                    if process.poll() is None:process.kill();process.wait(timeout=5)
            finally:c.close()
    def test_actual_packet_receipt_and_untransferred_retirement(self):
        self.assertIn('result=accepted creates=1 destroys=1 waits=1',self.run_probe('normal'))
    def test_single_transfer_and_final_cleanup(self):
        self.assertIn('result=accepted creates=1 destroys=1 waits=1',self.run_probe('transfer'))
    def test_cancel_before_api_work(self):
        self.assertIn('result=cancelled creates=0 destroys=0 waits=0',self.run_probe('normal',lambda c,cancel:cancel(c)))
    def test_cancel_during_preparation_retires_resource(self):
        self.assertIn('result=cancelled creates=1 destroys=1 waits=1',self.run_probe('cancel-wait'))
    def test_corrupt_packet_never_creates_light(self):
        def corrupt(c,cancel):
            value=bytearray(c.read(env.OFFSET+8,env.PACKET.size));value[-1]^=1;c.write(env.OFFSET+8,bytes(value))
        self.assertIn('result=rejected creates=0 destroys=0 waits=0',self.run_probe('normal',corrupt))
    def test_wrong_session_never_creates_light(self):
        from owner_rebind import fnv
        def corrupt(c,cancel):
            value=bytearray(c.read(env.OFFSET+8,env.PACKET.size));value[16]^=1;value[-8:]=struct.pack('<Q',fnv(value[:-8]));c.write(env.OFFSET+8,bytes(value))
        self.assertIn('result=rejected creates=0 destroys=0 waits=0',self.run_probe('normal',corrupt))
    def test_absent_producer_cancels_before_api_work(self):
        from owner_rebind import fnv
        from warm_start import OFFSET
        def orphan(c,cancel):
            c.write(OFFSET+32,struct.pack('<I',0xfffffffc))
            value=bytearray(c.read(env.OFFSET+8,env.PACKET.size));struct.pack_into('<I',value,32,0xfffffffc)
            value[-8:]=struct.pack('<Q',fnv(value[:-8]));c.write(env.OFFSET+8,bytes(value))
        self.assertIn('result=cancelled creates=0 destroys=0 waits=0',self.run_probe('normal',orphan))
if __name__=='__main__':unittest.main()

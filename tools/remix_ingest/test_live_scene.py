import json
from pathlib import Path
import struct
import subprocess
import tempfile
import time
import unittest
from PIL import Image
from live_scene import SceneChannel,SceneConsumer,decode_mesh,qualify_mesh,ImageStore,DATA,STRIDE
from replay_live_scene import asset_variant,observation

ROOT=Path(__file__).resolve().parents[2]
CAPTURE=ROOT/'artifacts/m1/runs/20261016-215022-enabled'


def packet_fixture():
    h=[0]*64;h[:14]=[0x314d4653,1,0,0,1,1,1,34,1,2,3,4,5,0x42e55d]
    h[16:20]=[3,1,3,1]
    positions=struct.pack('<9f',0,0,0,1,0,0,0,1,0)
    poly=struct.pack('<9I',3,0,0,0,0x3f800000,0,0,0,0)
    corners=b''.join(struct.pack('<I5fI',i,0,0,1,float(i==1),float(i==2),0) for i in range(3))
    source=struct.pack('<10I',0,1,0,0,0,0,7,0,0,0)
    body=positions+poly+corners+source;h[2]=256+len(body)
    packet=bytearray(struct.pack('<64I',*h)+body);value=2166136261
    for byte in packet:value=((value^byte)*16777619)&0xffffffff
    struct.pack_into('<I',packet,12,value)
    refs=dict(status=1,packet_fnv1a=value,owner_epoch=1,frame=1,model=3,source=5,textures_enabled=1,
        model_filename='Assets/Models/test/test.mod',groups=[dict(group=0,flags=1,primary=7,secondary=0,primary_name_offset=0,secondary_name_offset=0)],
        resources=[dict(id=7,filename='ship.bmp')])
    return bytes(packet),json.dumps(refs).encode()


class SceneTests(unittest.TestCase):
    def test_mesh_arrays_and_content_without_template(self):
        packet,refs=packet_fixture();d=decode_mesh(packet,refs)
        self.assertEqual(d['points'][1],(1,0,0));self.assertEqual(d['corners'][2][2],(0,1))
        second,ref2,h=asset_variant(packet,refs,2,1)
        self.assertNotEqual(decode_mesh(second,ref2)['geometry_sha256'],d['geometry_sha256'])
        same,ref3,h=asset_variant(packet,refs,3)
        self.assertEqual(decode_mesh(same,ref3)['geometry_sha256'],d['geometry_sha256'])
    def test_bad_packet_association_and_bounds(self):
        packet,refs=packet_fixture()
        for data in (packet[:-1],b'bad',packet[:260]+bytes([packet[260]^1])+packet[261:]):
            with self.assertRaises(ValueError):decode_mesh(data,refs)
        r=json.loads(refs);r['model']=999
        with self.assertRaises(ValueError):decode_mesh(packet,json.dumps(r).encode())
    def test_original_images_and_group_assignment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);Image.new('RGB',(4,4),(20,80,40)).save(root/'ship.bmp')
            store=ImageStore(root,root/'output');packet,refs=packet_fixture();data=qualify_mesh(packet,refs,store)
            self.assertEqual(data['assignments'][0]['primary']['width'],4)
            with Image.open(data['assignments'][0]['primary']['dds']) as converted:
                self.assertEqual(converted.convert('RGB').getpixel((0,0)),(20,80,40))
            first=data['asset_sha256'];other,rr,_=asset_variant(packet,refs,3)
            self.assertEqual(qualify_mesh(other,rr,store)['asset_sha256'],first)
            self.assertEqual(len(store.images),1)
            with self.assertRaises(ValueError):store.load('../missing.bmp')
            with self.assertRaises(ValueError):store.load('missing.bmp')
            Image.new('RGB',(4097,1)).save(root/'wide.bmp')
            with self.assertRaises(ValueError):store.load('wide.bmp')
            store.bytes=128*1024*1024;Image.new('RGB',(1,1)).save(root/'other.bmp')
            with self.assertRaises(ValueError):store.load('other.bmp')
    def test_multi_owner_common_origin_lifetime_and_revision(self):
        packet,refs=packet_fixture();assets={};rows=[]
        for i in range(2):
            p,r,h=asset_variant(packet,refs,i+1,i);assets[i+1]=decode_mesh(p,r);rows.append(observation(h,i,i+1,1,0))
        c=SceneConsumer();m0=c.update(rows[0],assets,0);m1=c.update(rows[1],assets,0)
        self.assertEqual(m0[3][0],0);self.assertEqual(m1[3][0],5)
        self.assertTrue(c.fresh(1,.5));self.assertFalse(c.fresh(1,1.))
        retired=rows[0].copy();retired[0]=2;retired[4]=2;c.update(retired,assets,.5)
        stale=rows[0].copy();stale[0]=3;self.assertIsNone(c.update(stale,assets,.6))
        bad=rows[1].copy();bad[0]=2;bad[7]=1;self.assertIsNone(c.update(bad,assets,.7))
        fresh,rr,h=asset_variant(packet,refs,3);assets[3]=decode_mesh(fresh,rr)
        reused=observation(h,0,3,4,5);self.assertIsNotNone(c.update(reused,assets,.8))
        self.assertIn((0,1),c.retired);self.assertEqual(c.origin,(0,0,0))
    def test_transport_ack_torn_stale_and_protocol(self):
        creator=SceneChannel(create=True)
        try:
            receiver=SceneChannel(creator.name)
            try:
                packet,refs=packet_fixture();creator.write(DATA,packet+refs)
                creator.write(256,struct.pack('<6I',1,0,len(packet),len(refs),1,1))
                self.assertEqual(receiver.asset_transfer(0)[3],packet)
                receiver.acknowledge(0,1);self.assertIsNone(receiver.asset_transfer(0))
                with self.assertRaises(ValueError):receiver.acknowledge(0,2)
                r=observation(decode_mesh(packet,refs)['header'],0,1,1,1)
                creator.write(4096,struct.pack('<I',1));creator.write(4100,struct.pack('<96I',*r))
                self.assertIsNone(receiver.sample_owner(0))
                creator.write(4096,struct.pack('<I',2));self.assertEqual(receiver.sample_owner(0)[7],1)
            finally:receiver.close()
            from live_bridge import Channel
            with self.assertRaises(ValueError):Channel(creator.name)
        finally:creator.close()
    def test_actual_native_worker_and_acknowledgements(self):
        binary=ROOT/'artifacts/m1/bin/m1_live_scene_tests.exe'
        self.assertTrue(binary.exists(),'Build native scene tests first')
        with tempfile.TemporaryDirectory() as tmp:
            channel=SceneChannel(create=True)
            try:
                child=subprocess.Popen([str(binary),channel.name,tmp],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                revisions=set();deadline=time.monotonic()+10
                while child.poll() is None and time.monotonic()<deadline:
                    for slot in range(4):
                        transfer=channel.asset_transfer(slot)
                        if transfer:
                            gen,revision,owner,packet,refs=transfer
                            self.assertEqual(decode_mesh(packet,refs)['header'][4],owner)
                            revisions.add(revision);channel.acknowledge(slot,gen)
                    time.sleep(.005)
                if child.poll() is None:child.kill();self.fail('Offline native test exceeded10s')
                output=child.communicate()[0].decode(errors='replace');self.assertEqual(child.returncode,0,output)
                self.assertGreaterEqual(len(revisions),4)
                summary=json.loads((Path(tmp)/'LIVE-SCENE-001-worker.json').read_text())
                self.assertTrue(summary['stopped']);self.assertFalse(summary['io_failed'])
                self.assertEqual(summary['capture_failures'],0)
            finally:channel.close()
    def test_empty_preview_preparation_no_old_job(self):
        from run_mesh_preview import prepare
        with tempfile.TemporaryDirectory(prefix='sfcFresh',dir='C:/Project/RemixJobs') as tmp:
            work,source,command=prepare(Path(tmp)/'absent','C:/Project/RTXRemix',tmp,textures=True,fresh=True)
            config=json.loads((work/'preview-config.json').read_text())
            self.assertEqual(config['expected_triangles'],0);self.assertTrue(config['fresh_scene'])
            self.assertEqual(config['dependency_sha256'],{});self.assertNotIn('kff',source.read_text())
    def test_native_disconnected_receiver_bounded_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            channel=SceneChannel(create=True)
            try:
                child=subprocess.run([str(ROOT/'artifacts/m1/bin/m1_live_scene_tests.exe'),channel.name,tmp],
                    stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=10)
                self.assertEqual(child.returncode,0,child.stdout.decode(errors='replace'))
                summary=json.loads((Path(tmp)/'LIVE-SCENE-001-worker.json').read_text())
                self.assertEqual(summary['transfers'],4)
                self.assertEqual(summary['unsent_assets'],4)
                self.assertTrue(summary['stopped']);self.assertFalse(summary['io_failed'])
            finally:channel.close()


if __name__=='__main__':unittest.main()

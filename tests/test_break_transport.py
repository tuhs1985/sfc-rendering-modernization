"""Indexed debris admission and actual native shared-memory delivery."""
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from contextlib import nullcontext

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools/remix_ingest'),str(ROOT/'tools/scene_bridge'),str(ROOT/'tools/d3d9_proof')]
from live_scene import SceneChannel,decode_mesh
from break_scene import decode_runtime_mesh
from test_live_scene import packet_fixture


def fixture():
    packet,refs=packet_fixture();packet=bytearray(packet);refs=json.loads(refs)
    for index,value in ((4,0x80000001),(13,0x42ea92),(14,0x1000),(20,1)):
        struct.pack_into('<I',packet,index*4,value)
    struct.pack_into('<I',packet,12,0);checksum=2166136261
    for byte in packet:checksum=((checksum^byte)*16777619)&0xffffffff
    struct.pack_into('<I',packet,12,checksum)
    refs.update(packet_fnv1a=checksum,owner_epoch=0x80000001,model_filename='assets/models/test/test_brk.mod',
                break_piece=dict(schema='sfc.break.piece.v1',owner_epoch=0x80000001,parent_owner_epoch=7,
                                 index=0,piece_count=2,first=0,count=1,total=2,primary_base=0x1000))
    return bytes(packet),refs


class BreakTransportTests(unittest.TestCase):
    def test_actual_receiver_checks_break_mode_before_acknowledging(self):
        from present_calibration import Receiver
        packet,refs=fixture();raw=json.dumps(refs).encode()
        for enabled in (False,True):
            with self.subTest(enabled=enabled):
                receiver=Receiver(break_models=enabled);channel=receiver.channel
                try:
                    channel.write(65536,packet+raw)
                    channel.write(256,struct.pack('<6I',1,0,len(packet),len(raw),refs['owner_epoch'],1))
                    if not enabled:
                        with self.assertRaisesRegex(ValueError,'semantic origin'):receiver.drain()
                        self.assertEqual(struct.unpack('<I',channel.read(260,4))[0],0)
                        self.assertFalse(receiver.revisions)
                    else:
                        receiver.drain()
                        self.assertEqual(struct.unpack('<I',channel.read(260,4))[0],1)
                        self.assertEqual(receiver.assets[1]['source_kind'],'break_piece')
                        bad=json.loads(raw);bad['break_piece']['parent_owner_epoch']=0
                        broken=json.dumps(bad).encode();channel.write(65536,packet+broken)
                        channel.write(256,struct.pack('<6I',2,1,len(packet),len(broken),refs['owner_epoch'],2))
                        with self.assertRaisesRegex(ValueError,'partition identity'):receiver.drain()
                        self.assertEqual(struct.unpack('<I',channel.read(260,4))[0],1)
                        self.assertNotIn(2,receiver.revisions)
                finally:receiver.close()

    def test_actual_parallel_decoder_obeys_break_mode_and_identity(self):
        from parallel_assets import Pipeline
        packet,refs=fixture()
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);gate=folder/'gate';gate.mkdir()
            source=gate/'LIVE-SCENE-001-asset-1.bin'
            source.write_bytes(packet);source.with_suffix('.json').write_text(json.dumps(refs))
            row=[0]*96;row[1]=refs['owner_epoch'];row[5]=refs['model'];row[6]=refs['source'];row[7]=1
            pipeline=Pipeline.__new__(Pipeline);pipeline.relay=SimpleNamespace(folder=folder,break_models=True)
            result=pipeline.decode({'row':row})
            self.assertEqual(result[3]['source_kind'],'break_piece')
            self.assertEqual(result[1],packet)
            self.assertEqual(result[3]['piece']['parent_owner_epoch'],7)
            for enabled in (False,None):
                pipeline.relay=SimpleNamespace(folder=folder,**({'break_models':enabled} if enabled is not None else {}))
                with self.assertRaisesRegex(ValueError,'semantic origin'):pipeline.decode({'row':row})
            pipeline.relay.break_models=True
            changed=dict(refs);changed.pop('break_piece')
            source.with_suffix('.json').write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError,'partition evidence'):pipeline.decode({'row':row})
            source.with_suffix('.json').write_text(json.dumps(refs))
            row[1]+=1
            with self.assertRaisesRegex(ValueError,'owner identity'):pipeline.decode({'row':row})
            intact,raw=packet_fixture();refs=json.loads(raw);source.write_bytes(intact)
            source.with_suffix('.json').write_bytes(raw)
            row[1]=refs['owner_epoch'];row[5]=refs['model'];row[6]=refs['source']
            for enabled in (False,True):
                pipeline.relay.break_models=enabled
                self.assertNotIn('source_kind',pipeline.decode({'row':row})[3])

    def test_parallel_submit_to_base_and_enhancements_uses_real_decoder(self):
        from PIL import Image
        from parallel_assets import Pipeline
        from replay_live_scene import observation
        from present_calibration import Receiver
        parent=ROOT/'artifacts/test-temp';parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as tmp:
            folder=Path(tmp);gate=folder/'gate';gate.mkdir()
            (gate/'run-metadata.json').write_text(json.dumps({'live_channel':'Local\\SFCBridge_'+'1'*32}))
            Image.new('RGB',(2,2),(80,120,160)).save(folder/'ship.bmp')
            relay=SimpleNamespace(folder=folder,root=folder,break_models=True,damage_textures=False,
                material_config=(ROOT/'tools/remix_runtime/config/rendering.toml').read_bytes(),
                output_reservations=SimpleNamespace(asset=lambda *_:nullcontext()))
            pipeline=Pipeline(relay);receiver=Receiver(break_models=True)
            receiver.retain_assets=False # Match actual multiship performance mode.
            try:
                debris,debris_refs=fixture()
                for revision,(packet,refs) in enumerate((packet_fixture(),(debris,json.dumps(debris_refs).encode())),1):
                    source=gate/f'LIVE-SCENE-001-asset-{revision}.bin'
                    source.write_bytes(packet);source.with_suffix('.json').write_bytes(refs)
                    header=struct.unpack_from('<64I',packet)
                    receiver.channel.write(65536,packet+refs)
                    receiver.channel.write(256,struct.pack('<6I',revision,revision-1,len(packet),len(refs),header[4],revision))
                    receiver.drain()
                    self.assertEqual(struct.unpack('<I',receiver.channel.read(260,4))[0],revision)
                    row=observation(struct.unpack_from('<64I',packet),revision-1,revision,1,0)
                    pipeline.submit(revision,row)
                until=time.monotonic()+10
                while not pipeline.settled((1,2)) and time.monotonic()<until:
                    pipeline.pump();time.sleep(.002)
                self.assertEqual([pipeline.jobs[i]['phase'] for i in (1,2)],['ready','ready'],pipeline.report())
                for identity in (1,2):
                    job=pipeline.jobs[identity]
                    self.assertTrue(job['basic_ready'])
                    self.assertEqual(len(job['material_done']),1)
                    self.assertTrue((job['output']/'scene.json').is_file())
                    self.assertTrue(any(kind=='basic' and value['id']==identity for kind,value in pipeline.events))
                manifest=pipeline.jobs[2]['manifest']
                self.assertEqual(manifest['source_kind'],'break_piece')
                self.assertEqual(manifest['piece']['parent_owner_epoch'],7)
                self.assertEqual(len(receiver.revisions),2)
                self.assertFalse(receiver.assets)
            finally:pipeline.close();receiver.close()

    def test_mixed_damage_policy_keeps_debris_base_and_intact_validation(self):
        from PIL import Image
        from parallel_assets import Pipeline,load_image,read_image
        from scene_bundle import geometry_parts
        packet,refs=fixture();raw=json.dumps(refs).encode()
        mesh=decode_runtime_mesh(packet,raw,allow_break=True)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);output=root/'output';output.mkdir()
            Image.new('RGB',(2,2),(100,120,140)).save(root/'ship.bmp')
            relay=SimpleNamespace(root=root,damage_textures=True,
                material_config=(ROOT/'tools/remix_runtime/config/rendering.toml').read_bytes())
            pipeline=Pipeline(relay)
            try:
                key=('geometry',1);pipeline.graph.tasks[key]={'value':geometry_parts(mesh),'state':'done'}
                job=dict(id=1,row=[0]*96,capture=(root/'source.bin',packet,raw,mesh),
                         images={'ship.bmp':load_image(root,'ship.bmp',read_image(root,'ship.bmp'))},
                         primary=['ship.bmp'],geometry_key=key,output=output)
                with patch('scene_bundle.prepare',return_value={'catalog_identity':{},'conventions':{}}) as prepare,patch('multi_scene.prepared_packet',return_value=b'packet'):
                    pipeline._basic(job)
                    self.assertIsNone(prepare.call_args.kwargs['damage_uv'])
                    mesh.pop('source_kind')
                    with self.assertRaisesRegex(ValueError,'damage mapping bounds missing'):pipeline._basic(job)
            finally:pipeline.close()

    def test_default_path_stays_closed(self):
        packet,refs=fixture();raw=json.dumps(refs).encode()
        with self.assertRaises(ValueError):decode_runtime_mesh(packet,raw)
        with self.assertRaises(ValueError):decode_mesh(packet,raw)
        data=decode_runtime_mesh(packet,raw,allow_break=True)
        self.assertEqual(data['piece']['parent_owner_epoch'],7)
        self.assertEqual(data['points'][1],(1,0,0))

    def test_partition_or_epoch_mismatch_rejected(self):
        packet,refs=fixture()
        for key,value in [('owner_epoch',0x80000002),('parent_owner_epoch',0),('index',2),
                          ('count',2),('first',2),('primary_base',0x2000),('total',8193)]:
            with self.subTest(key=key):
                changed=json.loads(json.dumps(refs));changed['break_piece'][key]=value
                with self.assertRaises(ValueError):decode_runtime_mesh(packet,json.dumps(changed).encode(),allow_break=True)
        refs.pop('break_piece')
        with self.assertRaises(ValueError):decode_runtime_mesh(packet,json.dumps(refs).encode(),allow_break=True)

    def test_native_worker_and_consumer(self):
        binary=ROOT/'artifacts/break-live/bin/break_scene_tests.exe'
        self.assertTrue(binary.is_file(),'Build focused native break fixture first')
        with tempfile.TemporaryDirectory() as tmp:
            from present_calibration import Receiver
            receiver=Receiver(break_models=True);channel=receiver.channel;child=None;pieces={}
            try:
                env={k:v for k,v in os.environ.items() if not k.startswith('SFC_')}
                child=subprocess.Popen([str(binary),channel.name,tmp],env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                deadline=time.monotonic()+10
                while child.poll() is None and time.monotonic()<deadline:
                    receiver.drain()
                    for revision,data in receiver.assets.items():
                        pieces[data['piece']['index']]=(data['header'][4],revision,data['piece']['count'])
                    time.sleep(.005)
                output=child.communicate(timeout=2)[0].decode(errors='replace')
                self.assertEqual(child.returncode,0,output)
                self.assertIn('Break scene transport/lifetime PASS',output)
                self.assertEqual(set(pieces),{0,1})
                self.assertNotEqual(pieces[0][0],pieces[1][0])
                self.assertEqual([pieces[i][2] for i in range(2)],[1,1])
                report=json.loads((Path(tmp)/'LIVE-SCENE-001-worker.json').read_text())
                self.assertTrue(report['stopped']);self.assertFalse(report['io_failed'])
                self.assertEqual(report['break_born'],3);self.assertEqual(report['break_retired'],1)
            finally:
                if child and child.poll() is None:child.kill();child.wait(timeout=3)
                if child and child.stdout:child.stdout.close()
                channel.close()


if __name__=='__main__':unittest.main()

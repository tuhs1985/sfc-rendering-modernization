import ctypes as C
from pathlib import Path
import struct
import sys
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_ingest'))
from live_owner_timing import Relay,OFFSET as LIVE_OFFSET
from owner_rebind import initialize,OFFSET,TARGET


class RecoveryRelayTests(unittest.TestCase):
    def exercise(self,ambiguous=False,signature=None,background=False):
        with tempfile.TemporaryDirectory() as raw:
            folder=Path(raw);(folder/'gate').mkdir()
            class Channel:
                name='Local\\SFCBridge_00000001000000020000000300000004'
                def __init__(self):self.memory=C.create_string_buffer(16*1024*1024);self.view=C.addressof(self.memory);self.rows=[]
                def write(self,offset,value):C.memmove(self.view+offset,value,len(value))
                def read(self,offset,size):return C.string_at(self.view+offset,size)
                def sample_owner(self,index):return self.rows[index] if index<len(self.rows) else None
            channel=Channel();initialize(channel,77);channel.write(OFFSET+104,struct.pack('<I',1));channel.write(LIVE_OFFSET+44,struct.pack('<I',100))
            old=[0]*96;old[1]=2;old[7]=2
            row=[0]*96;row[1]=4;row[2]=100;row[4]=1;row[5]=99;row[6]=98;row[7]=3;row[48]=1
            channel.rows=[row]
            if ambiguous:
                duplicate=row.copy();duplicate[1]=5;channel.rows.append(duplicate)
            for suffix in ('bin','json'):(folder/'gate'/f'LIVE-SCENE-001-asset-3.{suffix}').write_bytes(b'fixture')
            mesh=dict(header=[0]*64,refs=dict(model_filename='assets/models/fca/fca.mod'))
            mesh['header'][4]=4;mesh['header'][10]=99;mesh['header'][12]=98
            relay=Relay.__new__(Relay);relay.receiver=SimpleNamespace(channel=channel);relay.folder=folder
            relay.binding_generation=1;relay.binding_pending=None;relay.binding_events=[];relay.bound_row=old;relay.binding_requested_at=0
            relay.lights=SimpleNamespace(row=old,ready=True,last=99)
            def prepare_owner(value):relay.lights.row=list(value);relay.lights.ready=True;return True
            relay.lights.prepare_owner=prepare_owner
            relay.content_signature='a'*64;relay.content=SimpleNamespace(signature=lambda m:signature or 'a'*64)
            relay.mesh_cache={};relay.recovery_polled=0;relay.recovery_rejected=set();relay.selected_model='assets/models/fca/fca.mod'
            if background:
                # Actual Relay service ownership with a fresh decoded transfer;
                # any disk reread/decode in recovery is an explicit test failure.
                drains=[];relay.receiver.assets={3:mesh}
                relay.receiver.drain=lambda:drains.append(threading.get_ident())
                relay.service=None;relay.error=None;relay.pending=None
                relay.process=SimpleNamespace(poll=lambda:None);relay.additive=True;relay.offline_fixture=False
                relay.lights.poll=lambda:True
                with patch('live_scene.decode_mesh',side_effect=AssertionError('decoded packet reread')):
                    relay.start_service(77)
                    try:
                        limit=time.monotonic()+2
                        while relay.binding_generation!=2 and time.monotonic()<limit:
                            relay.poll(77);time.sleep(.002)
                        self.assertEqual(relay.binding_generation,2)
                        channel.write(OFFSET+104,struct.pack('<I',2))
                        while relay.bound_row[1]!=4 and time.monotonic()<limit:time.sleep(.002)
                        self.assertEqual(relay.bound_row[1],4);relay.check_service()
                    finally:relay.service.close()
                self.assertTrue(drains);self.assertEqual(len(set(drains)),1)
                self.assertNotEqual(drains[0],threading.get_ident());self.assertFalse(relay.service.thread.is_alive())
                return
            if ambiguous:
                second=dict(mesh,header=list(mesh['header']));second['header'][4]=5;relay.mesh_cache[(5,3)]=second
            with patch('live_scene.decode_mesh',return_value=mesh):relay.recover(77)
            if ambiguous or signature:
                self.assertEqual(relay.binding_generation,1);self.assertIsNone(relay.binding_pending)
                self.assertTrue(relay.recovery_rejected);return
            self.assertEqual(relay.binding_generation,2);self.assertEqual(relay.bound_row[1],2)
            self.assertEqual(TARGET.unpack(channel.read(OFFSET+64,40))[1:5],(4,3,99,98))
            channel.write(OFFSET+104,struct.pack('<I',2));relay.recover(77)
            self.assertEqual(relay.bound_row[1],4);self.assertEqual(relay.lights.row[1],4)
            self.assertTrue(relay.lights.ready);self.assertTrue(relay.binding_events[-1]['acknowledged'])

    def test_acknowledgement_before_light_retarget_no_asset_rebuild(self):self.exercise()
    def test_ambiguous_same_model_hides_instead_of_guessing(self):self.exercise(ambiguous=True)
    def test_changed_content_rejects_even_with_same_native_labels(self):self.exercise(signature='b'*64)
    def test_dedicated_recovery_uses_decoded_transfer_and_single_drain_owner(self):self.exercise(background=True)


if __name__=='__main__':unittest.main()

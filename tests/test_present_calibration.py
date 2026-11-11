from pathlib import Path
import struct
import tempfile
import unittest
import sys
from unittest.mock import Mock,patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
import present_calibration as pc
import scene_receiver

class CalibrationTests(unittest.TestCase):
    def test_actual_ninth_transfer_ack_and_owner_above_hundred(self):
        from test_live_scene import packet_fixture
        from scene_capacity import STATE_OFFSET
        mesh,refs=packet_fixture();receiver=pc.Receiver();channel=receiver.channel
        try:
            channel.write(256,struct.pack('<6I',1,0,len(mesh),len(refs),1,9))
            channel.write(65536,mesh+refs);receiver.drain()
            self.assertEqual(struct.unpack('<I',channel.read(260,4))[0],1)
            self.assertEqual(receiver.assets[9]['header'][4],1)
            row=[0]*96;row[1]=160;row[45]=159
            channel.write(STATE_OFFSET+159*512,struct.pack('<I',2)+struct.pack('<96I',*row))
            channel.write(128,struct.pack('<I',160))
            self.assertEqual(len(channel.owner_indices()),160)
            self.assertEqual(channel.sample_owner(159)[1],160)
        finally:receiver.close()

    def test_transport_receiver_accepts_ninth_and_large_fleet_revisions(self):
        channel=Mock();channel.asset_transfer.return_value=None
        with patch.object(scene_receiver,'SceneChannel',return_value=channel):receiver=pc.Receiver()
        for revision in (*range(1,161),pc.ASSETS):
            channel.asset_transfer.side_effect=lambda slot,r=revision: (r,r,r,b'mesh'+str(r).encode(),b'refs') if slot==0 else None
            header=[0]*5;header[4]=revision
            with patch.object(scene_receiver,'decode_mesh',return_value={'header':header}):receiver.drain()
            channel.acknowledge.assert_called_with(0,revision)
        self.assertEqual(len(receiver.revisions),161)
        channel.asset_transfer.side_effect=lambda slot:(1,pc.ASSETS+1,1,b'mesh',b'refs') if slot==0 else None
        with self.assertRaises(ValueError):receiver.drain()
        self.assertEqual(channel.acknowledge.call_count,161)

    def test_multiscene_receiver_keeps_identities_without_duplicate_decoded_assets(self):
        channel=Mock();channel.asset_transfer.side_effect=lambda slot:(1,9,1,b'mesh',b'refs') if slot==0 else None
        with patch.object(scene_receiver,'SceneChannel',return_value=channel):receiver=pc.Receiver()
        receiver.retain_assets=False
        with patch.object(scene_receiver,'decode_mesh',return_value={'header':[0,0,0,0,1]}):receiver.drain()
        self.assertIn(9,receiver.revisions);self.assertEqual(receiver.assets,{})
        channel.acknowledge.assert_called_once_with(0,1)

    def setUp(self):
        self.session='Local\\SFCBridge_'+'a'*32
        self.s=[0x31504353,1,pc.SIZE,40,41,2,9,9,123,456]+[0]*6
        self.h=[0x314c4143,1,pc.SIZE-128,9]+[0xaaaaaaaa]*4+[1,0,0,0]
        self.rows=[[0]*96 for _ in range(32)]
        self.rows[0][1:8]=[7,9,10,1,99,98,1];self.rows[0][47:49]=[456,1]
        self.depth=dict(qpc=40,present_frame=41,resource_epoch=2)
    def read(self):
        raw=struct.pack('<16Q12I',*self.s,*self.h)+b''.join(struct.pack('<96I',*r) for r in self.rows)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'semantic-0.bin';p.write_bytes(raw)
            return pc.read_semantic(p,self.depth,self.session,123)
    def test_valid(self):self.assertEqual(self.read()['owners'][0][1],7)
    def test_wrong_gpu_pair(self):
        self.s[4]+=1
        with self.assertRaises(ValueError):self.read()
    def test_stale_semantic(self):
        self.rows[0][2]-=1
        with self.assertRaises(ValueError):self.read()
    def test_wrong_thread(self):
        self.rows[0][47]+=1
        with self.assertRaises(ValueError):self.read()
    def test_session(self):
        self.h[4]=0
        with self.assertRaises(ValueError):self.read()
    def test_reserved(self):
        self.s[-1]=1
        with self.assertRaises(ValueError):self.read()
    def test_ambiguous(self):
        self.rows[0][4]=3
        with self.assertRaises(ValueError):self.read()
    def test_nonfinite(self):
        self.rows[0][8]=0x7f800000
        with self.assertRaises(ValueError):self.read()
    def test_duplicate_owner(self):
        self.rows[1]=self.rows[0].copy();self.rows[1][45]=1;self.h[8]=2
        with self.assertRaises(ValueError):self.read()

if __name__=='__main__':unittest.main()

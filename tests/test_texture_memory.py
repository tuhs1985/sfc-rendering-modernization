import os
import struct
import sys
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools/remix_runtime'),str(ROOT/'tools/remix_ingest'),str(ROOT/'tools/d3d9_proof')]
from texture_memory import Pool,Mapping,HEADER,name
from multi_scene import asset_packet


class TextureMemoryTests(unittest.TestCase):
    def setUp(self):
        self.session='Local\\SFCBridge_'+uuid.uuid4().hex;self.pool=Pool(self.session)
        self.addCleanup(self.pool.close)
        self.images=[struct.pack('<4I',0x31544653,3,2,24)+bytes(range(24)),struct.pack('<4I',0x31544653,1,1,4)+b'\x00\xff\x80\xff']
        row=[0]*96
        for i in (1,5,6,7):row[i]=i
        self.packet=asset_packet(1,1,row,'ab'*32,b'geometry',self.images)

    def publish(self):
        self.assertTrue(self.pool.reserve(1,list(map(len,self.images)),8))
        self.pool.write_geometry(1,b'geometry')
        for i,image in enumerate(self.images):self.pool.write(1,i,image)
        self.pool.seal(1,self.packet)

    def test_exact_pixels_and_no_reuse(self):
        self.publish();entry=self.pool.entries[1]
        for i,image in enumerate(self.images):
            offset,length=entry['table'][i]
            self.assertEqual(entry['mapping'].read(offset,length),image)
        with self.assertRaises(ValueError):self.pool.write(1,0,self.images[0])
        other=Mapping.__new__(Mapping);other.size=entry['mapping'].size
        with self.assertRaises(ValueError):Mapping.__init__(other,name(self.session,1),create=True)

    def test_incomplete_and_wrong_identity(self):
        self.pool.reserve(1,list(map(len,self.images)),8)
        with self.assertRaises(ValueError):self.pool.seal(1,self.packet)
        with self.assertRaises(ValueError):self.pool.write(1,0,b'wrong')

    def test_capacity_postpones_and_ack_releases(self):
        with patch('texture_memory.BUDGET',HEADER+8+sum(map(len,self.images))):
            self.publish();self.assertFalse(self.pool.reserve(2,list(map(len,self.images)),8))
            with patch('multi_scene.acknowledgement',return_value=0):self.pool.reclaim(None)
            self.assertEqual(len(self.pool.entries),1)
            with patch('multi_scene.acknowledgement',return_value=1):self.pool.reclaim(None)
            self.assertEqual(self.pool.bytes,0);self.assertTrue(self.pool.reserve(2,list(map(len,self.images)),8))

    def test_geometry_required_and_immutable(self):
        self.pool.reserve(1,list(map(len,self.images)),8)
        for i,image in enumerate(self.images):self.pool.write(1,i,image)
        with self.assertRaises(ValueError):self.pool.seal(1,self.packet)
        with self.assertRaises(ValueError):self.pool.write_geometry(1,b'bad')
        self.pool.write_geometry(1,b'geometry');self.pool.seal(1,self.packet)
        self.assertEqual(self.pool.entries[1]['mapping'].read(HEADER,8),b'geometry')
        with self.assertRaises(ValueError):self.pool.write_geometry(1,b'geometry')

    def test_session_and_owner_slots_differ(self):
        self.assertNotEqual(name(self.session,1),name(self.session,2))
        self.assertNotEqual(name(self.session,1),name('Local\\SFCBridge_'+uuid.uuid4().hex,1))
        for lengths in ([],[16],[128*1024*1024],[20]*257):
            with self.assertRaises(ValueError):self.pool.reserve(1,lengths)


if __name__=='__main__':unittest.main()

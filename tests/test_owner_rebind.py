import copy
import ctypes
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
sys.path[:0]=[str(Path(__file__).resolve().parents[1]/'tools/d3d9_proof'),str(Path(__file__).resolve().parents[1]/'tools/scene_bridge')]
from owner_rebind import Content,choose,initialize,request,acknowledged,OFFSET,TARGET,fnv


class RebindTests(unittest.TestCase):
    def test_mailbox_layout_checksum_and_ack(self):
        class Channel:
            name='Local\\SFCBridge_00000001000000020000000300000004'
            def __init__(self):self.memory=ctypes.create_string_buffer(16*1024*1024);self.view=ctypes.addressof(self.memory)
            def write(self,offset,raw):ctypes.memmove(self.view+offset,raw,len(raw))
            def read(self,offset,size):return ctypes.string_at(self.view+offset,size)
        channel=Channel();initialize(channel,77)
        row=[0]*96;row[1]=4;row[4]=1;row[5]=99;row[6]=98;row[7]=3
        request(channel,2,row,123)
        self.assertEqual(struct.unpack('<I',channel.read(OFFSET+32,4))[0],4)
        raw=channel.read(OFFSET+64,40);self.assertEqual(TARGET.unpack(raw),(2,4,3,99,98,0,123,fnv(raw[:-8])))
        channel.write(OFFSET+104,struct.pack('<I',2));self.assertEqual(acknowledged(channel),2)
        with self.assertRaises(ValueError):request(channel,65,row,123)

    def test_new_epoch_pointer_reuse_and_ambiguous_content(self):
        row=[0]*96;row[1]=4;row[7]=3
        mesh=dict(refs=dict(model_filename='assets/models/fca/fca.mod'),content='a')
        class Signature:
            def signature(self,m):return m['content']
        self.assertEqual(choose([(row,mesh)],mesh['refs']['model_filename'],Signature(),'a'),(row,mesh))
        wrong=copy.deepcopy(mesh);wrong['content']='b'
        self.assertIsNone(choose([(row,wrong)],mesh['refs']['model_filename'],Signature(),'a'))
        self.assertIsNone(choose([(row,mesh),(row.copy(),mesh)],mesh['refs']['model_filename'],Signature(),'a'))
        self.assertIsNone(choose([],mesh['refs']['model_filename'],Signature(),'a'))

    def test_resource_ids_not_identity_but_image_content_is(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);(root/'one.bmp').write_bytes(b'original image bytes')
            content=Content(root)
            mesh=dict(geometry_sha256='abc',header=[0]*64,groups=[dict(group=1,flags=1,primary=12,secondary=0)],
                      refs=dict(resources=[dict(id=12,filename='one.bmp')],secondary_role='unproven'))
            first=content.signature(mesh);other=copy.deepcopy(mesh);other['groups'][0]['primary']=99;other['refs']['resources'][0]['id']=99
            self.assertEqual(first,content.signature(other))
            (root/'one.bmp').write_bytes(b'different image bytes')
            self.assertNotEqual(first,content.signature(other))


if __name__=='__main__':unittest.main()

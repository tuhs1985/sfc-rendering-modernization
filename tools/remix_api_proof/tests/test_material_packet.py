from pathlib import Path
import copy
import struct
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from material_packet import encode,checksum,ROW,MAGIC

class MaterialPacketTests(unittest.TestCase):
    def data(self,root):
        name='a'*64+'.dds'
        path=Path(root)/'rtx-remix/mods/sfc-policy/textures'/name
        path.parent.mkdir(parents=True);path.write_bytes(b'DDS '+bytes(124))
        report=dict(values=[.4,5,.2,.5,1,.9,0,1,0,.4],groups=[dict(group=3,ordinary_texture=0,
            remix_hash='1234567890ABCDEF',images=dict(color='textures/'+name,emission='textures/'+name,roughness='textures/'+name))])
        return report,dict(groups=[[3,0,0,3]]),path

    def test_exact_layout_checksum_and_original_preserved(self):
        with tempfile.TemporaryDirectory() as root:
            report,scene,path=self.data(root);before=path.read_bytes();original=copy.deepcopy(report)
            raw=encode(report,scene,root)
            self.assertEqual(len(raw),320)
            self.assertEqual(struct.unpack_from('<4I',raw),(MAGIC,1,1,256))
            row=ROW.unpack_from(raw,56)
            self.assertEqual(row[:3],(3,0,0x1234567890abcdef))
            self.assertEqual(row[3].rstrip(b'\0'),path.name.encode())
            self.assertEqual(struct.unpack_from('<Q',raw,len(raw)-8)[0],checksum(raw[:-8]))
            self.assertEqual(report,original);self.assertEqual(path.read_bytes(),before)

    def test_group_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            report,scene,_=self.data(root);scene['groups'][0][0]=4
            with self.assertRaisesRegex(ValueError,'identity'):encode(report,scene,root)

    def test_nonfinite_or_missing_primary_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            report,scene,_=self.data(root);report['values'][0]=float('nan')
            with self.assertRaisesRegex(ValueError,'scalars'):encode(report,scene,root)
            report['values'][0]=.4;report['groups'][0]['images'].pop('color')
            with self.assertRaisesRegex(ValueError,'primary'):encode(report,scene,root)

    def test_missing_or_unsafe_image_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            report,scene,path=self.data(root);report['groups'][0]['images']['color']='../texture.dds'
            with self.assertRaisesRegex(ValueError,'Unsafe'):encode(report,scene,root)
            report['groups'][0]['images']['color']='textures/'+path.name;path.unlink()
            with self.assertRaisesRegex(ValueError,'Missing'):encode(report,scene,root)

    def test_optional_roles_remain_empty(self):
        with tempfile.TemporaryDirectory() as root:
            report,scene,_=self.data(root);report['values'][4]=0
            report['groups'][0]['images']={k:v for k,v in report['groups'][0]['images'].items() if k=='color'}
            row=ROW.unpack_from(encode(report,scene,root),56)
            self.assertEqual(row[4],bytes(80));self.assertEqual(row[5],bytes(80))

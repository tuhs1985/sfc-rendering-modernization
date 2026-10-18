from pathlib import Path
import struct
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
from ship_image_snapshot import HEADER,KEY,decode,convert
from PIL import Image

def sample():
    header=HEADER.pack(0x31495353,1,256,4,42,2,2,87,99,1000,999,1000,1,1,200,30,1200,630)
    key=KEY.pack(1,2,3,4,2,3,12,29,1,2,2,2,200,30,1000,600,1,1,b'a'*32,1,2,3,4,42,0,2,0,1,0)
    return header+key+struct.pack('<4I',0,0x1000,0x2000,0)+bytes([0,0,255,255,0,255,0,255,255,0,0,255,0,255,255,0])

class ShipImageSnapshotTests(unittest.TestCase):
    def test_exact_rgba_and_provenance(self):
        raw=sample();meta,_=decode(raw)
        self.assertEqual(meta['owner_epoch'],2);self.assertEqual(meta['source_frame'],12)
        self.assertEqual(meta['display_rect'],[200,30,1200,630]);self.assertEqual(meta['nonzero_alpha_pixels'],3)
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);(folder/'prepared-ship-image.sfcimg').write_bytes(raw);convert(folder)
            with Image.open(folder/'prepared-ship-image.png') as image:
                self.assertEqual(image.tobytes(),bytes([255,0,0,255,0,255,0,255,0,0,255,255,255,255,0,0]))
            with self.assertRaisesRegex(ValueError,'overwrite'):convert(folder)
    def test_partial_or_invalid_records_rejected(self):
        for offset,value in ((0,0),(12,5),(28,0),(216,99)):
            raw=bytearray(sample());struct.pack_into('<I',raw,offset,value)
            with self.assertRaises(ValueError):decode(raw)
        with self.assertRaises(ValueError):decode(sample()[:-1])
    def test_old_source_rejected(self):
        raw=bytearray(sample());struct.pack_into('<Q',raw,40,2000)
        with self.assertRaisesRegex(ValueError,'age'):decode(raw)
    def test_snapshot_hook_does_not_read_back_or_write(self):
        source=(Path(__file__).resolve().parents[1]/'tools/remix_runtime/ship_image_snapshot.h').read_text()
        for forbidden in ('->Map(', 'Sleep(', 'WaitForSingleObject(', 'ofstream','WriteFile('):self.assertNotIn(forbidden,source)
        self.assertIn('D3D11_ASYNC_GETDATA_DONOTFLUSH',source)
        self.assertIn('context->CopyResource(target.Get(),texture)',source)
        self.assertIn('h.pid==GetCurrentProcessId()&&return_path::read(h.status)!=Off)return',source)
        self.assertIn('if(submitted&&return_path::read(h.status)==Copying)',source)

"""Offline bounds/fail-closed checks for static effects verification."""
import sys
from pathlib import Path
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import verify_effect_resource_path as anchors

class AnchorTests(unittest.TestCase):
    def image(self):
        image=anchors.Image.__new__(anchors.Image)
        image.base=0x400000;image.data=b'0123456789ABCDEF'
        image.meta={'sections':[{'rva':0x1000,'raw_offset':4,'raw_size':8}]}
        return image

    def test_reads_explicit_file_backed_section(self):
        self.assertEqual(self.image().read(0x401002,4),b'6789')

    def test_rejects_cross_section_and_unmapped(self):
        for address,size in ((0x401007,2),(0x401008,1),(0x400FFF,1)):
            with self.assertRaisesRegex(ValueError,'file-backed'):self.image().read(address,size)

    def test_read_bound(self):
        for size in (0,-1,257):
            with self.assertRaisesRegex(ValueError,'read bound'):self.image().read(0x401000,size)

    def test_wrong_anchor_fails_closed(self):
        with patch.object(anchors,'Image') as image:
            image.return_value.read.side_effect=lambda address,size:b'\0'*size
            with self.assertRaisesRegex(ValueError,'Anchor mismatch'):anchors.verify(Path('unused'))

if __name__=='__main__':unittest.main()

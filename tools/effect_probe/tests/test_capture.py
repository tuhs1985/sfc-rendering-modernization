import ctypes as C
import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('effect_capture_test',Path(__file__).resolve().parents[1]/'capture.py')
capture=importlib.util.module_from_spec(spec);spec.loader.exec_module(capture)

class CaptureTests(unittest.TestCase):
    def sample(self):
        name=b'assets/textures/fx0.bmp\0'.ljust(256,b'\0')
        rows=[(64,111,0,[1,0]),(66,111,222,[1,100,0,1]),(69,111,222,[1,100,1,7,4,1,1]),
              (71,111,222,[1,100,1,333,444,555,666]),(70,111,222,[1,100,1,4,0,1])]
        rows += [(72,111,222,[4,1,i,*struct.unpack('<8Q',name[i*64:(i+1)*64])]) for i in range(4)]
        return rows+[(67,111,222,[1,100,123]),(75,0,0,[0,0]),(76,0,0,[0,0,1,1,0])]

    def report(self,rows=None,drop=0,mutate=None):
        rows=self.sample() if rows is None else rows
        h=capture.Header();h.magic=capture.MAGIC;h.version=1;h.recordBytes=h.headerBytes=128
        h.hardBytes=capture.HARD;h.durationMs=90000;h.frequency=10_000_000;h.status=3;h.reason=3;h.written=len(rows);h.fileBytes=128*(len(rows)+1);h.dropped=drop
        data=bytes(h)+b''.join(capture.RECORD.pack(i,100+i,kind,1,obj,manager,*args,*([0]*(11-len(args)))) for i,(kind,obj,manager,args) in enumerate(rows,1))
        if mutate:data=mutate(data)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'test.bin';path.write_bytes(data);return capture.analyze(path)

    def test_fresh_instance_resource_join(self):
        r=self.report();self.assertEqual(r['qualified_native_polygons'],1);self.assertFalse(r['issues'])
        self.assertEqual(r['assignments'][0]['filename'],'assets/textures/fx0.bmp')

    def test_wrong_owner_epoch_and_manager_rejected(self):
        for field,value in ((0,2),(3,999)):
            rows=self.sample();kind,obj,m,args=rows[4]
            if field==0:args[0]=value
            else:m=value
            rows[4]=(kind,obj,m,args)
            r=self.report(rows);self.assertEqual(r['qualified_native_polygons'],0);self.assertIn('unqualified_polygon',r['issues'])

    def test_retired_pointer_cannot_restore_old_epoch(self):
        rows=self.sample();rows.insert(1,(65,111,0,[1]));rows.insert(2,(64,111,0,[2,0]))
        self.assertEqual(self.report(rows)['qualified_native_polygons'],0)

    def test_record_loss_remains_partial(self):
        r=self.report(drop=3);self.assertEqual(r['result'],'PARTIAL');self.assertEqual(r['issues']['record_loss'],3)

    def test_bad_header_alignment_sequence_rejected(self):
        for mutate in (lambda d:b'\0'*4+d[4:],lambda d:d+b'X',lambda d:d[:256]+b'\0'*8+d[264:]):
            with self.assertRaises(ValueError):self.report(mutate=mutate)

    def test_missing_filename_cleanup_or_identity_unknown_not_success(self):
        rows=[r for r in self.sample() if r[0]!=72];r=self.report(rows)
        self.assertEqual(r['qualified_native_polygons'],0)
        rows=[r for r in self.sample() if r[0]!=75];self.assertIn('cleanup_unconfirmed',self.report(rows)['issues'])
        rows=self.sample();rows[-1]=(76,0,0,[0,0,1,1,1]);self.assertIn('native_fault_or_identity_uncertainty',self.report(rows)['issues'])

if __name__=='__main__':unittest.main()

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

    def report(self,rows=None,drop=0,mutate=None,allow_unfinalized=False,reader=None):
        rows=self.sample() if rows is None else rows
        h=capture.Header();h.magic=capture.MAGIC;h.version=1;h.recordBytes=h.headerBytes=128
        h.hardBytes=capture.HARD;h.durationMs=90000;h.frequency=10_000_000;h.status=3;h.reason=3;h.written=len(rows);h.fileBytes=128*(len(rows)+1);h.dropped=drop
        data=bytes(h)+b''.join(capture.RECORD.pack(i,100+i,kind,1,obj,manager,*args,*([0]*(11-len(args)))) for i,(kind,obj,manager,args) in enumerate(rows,1))
        if mutate:data=mutate(data)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'test.bin';path.write_bytes(data)
            if reader:return reader(path)
            return capture.analyze(path,allow_unfinalized=allow_unfinalized)

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

    def test_unfinalized_trace_requires_explicit_recovery_and_stays_partial(self):
        def unfinished(data):
            h=capture.Header.from_buffer_copy(data[:128])
            h.status=1;h.written=0;h.fileBytes=0;h.reason=0
            return bytes(h)+data[128:]
        rows=self.sample()[:-2]
        with self.assertRaisesRegex(ValueError,'Effect final file size'):
            self.report(rows,mutate=unfinished)
        report=self.report(rows,mutate=unfinished,allow_unfinalized=True)
        self.assertEqual(report['records'],len(rows))
        self.assertEqual(report['qualified_native_polygons'],1)
        self.assertEqual(report['result'],'PARTIAL')
        self.assertEqual(report['issues'],{'unfinalized_trace':1,'cleanup_unconfirmed':1})

    def test_bad_header_alignment_sequence_rejected(self):
        for mutate in (lambda d:b'\0'*4+d[4:],lambda d:d+b'X',lambda d:d[:256]+b'\0'*8+d[264:]):
            with self.assertRaises(ValueError):self.report(mutate=mutate)

    def test_missing_filename_cleanup_or_identity_unknown_not_success(self):
        rows=[r for r in self.sample() if r[0]!=72];r=self.report(rows)
        self.assertEqual(r['qualified_native_polygons'],0)
        rows=[r for r in self.sample() if r[0]!=75];self.assertIn('cleanup_unconfirmed',self.report(rows)['issues'])
        rows=self.sample();rows[-1]=(76,0,0,[0,0,1,1,1]);self.assertIn('native_fault_or_identity_uncertainty',self.report(rows)['issues'])

    def test_native_draw_requires_bound_texture_and_matching_vertex_bytes(self):
        def draw_rows(texture=666, conflicting_vertex=False):
            rows=self.sample()
            rows[9:9]=[(77,111,222,[1,100,i]+[0]*8) for i in range(4)]
            rows.insert(13,(78,111,222,[1,100,1,1,3,1]))
            tail=[
                (79,[1,100,1,1,0,6,4]),
                (82,[1,100,2,1,4,2,4]),
                (83,[1,100,2,2,0,texture,0,1234,0,1]),
                (84,[1,100,2,1,1]),
            ]
            for kind,selectors in ((0,capture.RENDER_STATES),(1,capture.TEXTURE_STATES)):
                tail[3:3]=[(83,[1,100,2,kind,selector,1,0]) for selector in selectors]
            for i,index in enumerate((0,1,2,0,2,3)):
                x=float(index)+(1.0 if conflicting_vertex and i==3 else 0.0)
                packed=struct.unpack('<4Q',struct.pack('<4f2I2f',x,1,0.5,1,0xFFFFFFFF,0,0.75,0.5))
                tail[1:1]=[(80,[1,100,2,i,*packed]),(81,[1,100,2,i,index])]
            rows[-2:-2]=[(kind,111,222,args) for kind,args in tail]
            return rows
        draw=self.report(draw_rows(),reader=capture.read_native_draw)
        self.assertEqual(draw['indices'],[0,1,2,0,2,3])
        self.assertEqual(draw['vertices'][3]['screen_xy'],[3.0,1.0])
        self.assertEqual(draw['texture']['filename'],'assets/textures/fx0.bmp')
        with self.assertRaisesRegex(ValueError,'texture binding'):
            self.report(draw_rows(texture=667),reader=capture.read_native_draw)
        with self.assertRaisesRegex(ValueError,'Conflicting native vertex'):
            self.report(draw_rows(conflicting_vertex=True),reader=capture.read_native_draw)

if __name__=='__main__':unittest.main()

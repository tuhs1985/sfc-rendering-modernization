import struct,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from inventory_render_types import category,inventory,hierarchy,disassembly_rows,instructions,graph,asset_acquisitions,binding_candidates

class Tiny:
    def __init__(self):
        self.base=0;self.data=bytearray(0x4000)
        self.meta={'sections':[{'rva':0x1000,'raw_offset':0x1000,'raw_size':0x1000,'characteristics':'0x40000040'},
                               {'rva':0x3000,'raw_offset':0x3000,'raw_size':0x1000,'characteristics':'0x60000020'}]}
        self.words(0x1100,[0x1080,0]);self.put(0x1108,b'.?AVtFx_Test@@\0')
        self.words(0x1200,[0,0,0,0x1100,0x1300]);self.words(0x1300,[0,0,1,0x1400])
        self.words(0x1400,[0x1500]);self.words(0x1500,[0x1100]);self.words(0x1600,[0x1200,0x3000,0x3010,0])
        self.put(0x1800,b'assets/textures/test.bmp\0')
    def put(self,va,data):self.data[va:va+len(data)]=data
    def words(self,va,values):self.put(va,struct.pack('<'+'I'*len(values),*values))
    def read(self,va,size):
        if not 0<size<=256 or not 0<=va<=len(self.data)-size:raise ValueError('Read bound')
        return bytes(self.data[va:va+size])

class InventoryTests(unittest.TestCase):
    def test_scope_excludes_accidental_light_substrings(self):
        self.assertEqual(category('.?AVtFx_Organian@@'),'effects')
        self.assertEqual(category('.?AVtLightPhaser_Creator@@'),'light_creator')
        self.assertIsNone(category('.?AVLightGetCertOp@WONAPI@@'))
        self.assertIsNone(category('.?AVtShipFlightPath@@'))
    def test_namespace_camera(self):
        self.assertEqual(category('.?AVtCamera@tState_Namespace_Tactical@@'),'tactical_camera')
        self.assertIsNone(category('.?AVtCamera@Unrelated@@'))
    def test_structurally_qualified_rtti(self):
        r=inventory(Tiny());self.assertEqual(len(r),1)
        self.assertEqual(r[0]['vtables'][0]['address'],0x1604)
        self.assertEqual(r[0]['vtables'][0]['methods'],[{'slot':0,'target':0x3000},{'slot':4,'target':0x3010}])
    def test_bad_hierarchy_does_not_create_vtable(self):
        im=Tiny();im.words(0x1300,[1,0,1,0x1400])
        self.assertEqual(inventory(im)[0]['vtables'],[])
    def test_self_descriptor_mismatch(self):
        im=Tiny()
        with self.assertRaises(ValueError):hierarchy(im,0x1300,0x1110)
    def test_methods_must_be_executable(self):
        im=Tiny();im.words(0x1604,[0x1800])
        self.assertEqual(inventory(im)[0]['vtables'],[])
    def test_dumpbin_wrapped_bytes_are_one_instruction(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'dump.txt';p.write_text('  00003000: F6 05 00 18 00 00  test byte ptr ds:[00001800h],1\n            01\n  00003007: C3  ret\n')
            rows=list(disassembly_rows(p));self.assertEqual(len(rows[0][1]),7);self.assertEqual(rows[1][0],0x3007)
    def test_disassembly_bytes_checked_against_image(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'dump.txt';p.write_text('  00003000: C3  ret\n')
            with self.assertRaises(ValueError):instructions(Tiny(),p,0x3000,0x3010,set())
    def test_fallthrough_accounts_for_continuation(self):
        im=Tiny();im.put(0x3000,bytes.fromhex('F6 05 00 18 00 00 01 C3'))
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'dump.txt';p.write_text('  00003000: F6 05 00 18 00 00  test byte ptr ds:[00001800h],1\n            01\n  00003007: C3  ret\n')
            code,_,_=instructions(im,p,0x3000,0x3010,set());g=graph(im,code,0x3000,0x3000,0x3010)
            self.assertEqual(g['limitations'],[]);self.assertEqual(g['instruction_count'],2)
    def test_indirect_jump_is_not_guessed(self):
        g=graph(Tiny(),{0x3000:(b'\xff\xe0','jmp','eax')},0x3000,0x3000,0x3100)
        self.assertIn('INDIRECT_JUMP:00003000',g['limitations'])
    def test_direct_follow_depth_is_explicit(self):
        code={0x3000:(b'\xe8\x0b\0\0\0','call','00003010'),0x3005:(b'\xc3','ret',''),0x3010:(b'\xc3','ret','')}
        g=graph(Tiny(),code,0x3000,0x3000,0x3100,max_depth=0)
        self.assertIn('CALL_DEPTH_LIMIT:00003010',g['limitations']);self.assertEqual(g['functions'],[0x3000])
    def acquire_code(self):
        return {0x3000:(b'a','mov','ecx,dword ptr ds:[008CC620h]'),0x3001:(b'a','push','001800h'),0x3002:(b'a','call','dword ptr [eax+8]'),0x3003:(b'a','mov','dword ptr ds:[00001900h],eax')}
    def test_literal_acquire_store_chain(self):
        r=asset_acquisitions(Tiny(),self.acquire_code());self.assertEqual(r[0]['filename'],'assets/textures/test.bmp');self.assertEqual(r[0]['result_slot'],0x1900)
    def test_intervening_call_not_false_literal_argument(self):
        code=self.acquire_code();code[0x3001]=(b'a','push','001800h');code[0x3002]=(b'a','call','00003050');code[0x3003]=(b'a','call','dword ptr [eax+8]')
        self.assertEqual(asset_acquisitions(Tiny(),code),[])
    def test_variable_last_argument_not_false_literal(self):
        code=self.acquire_code();code[0x3002]=(b'a','push','eax');code[0x3003]=(b'a','call','dword ptr [eax+8]')
        self.assertEqual(asset_acquisitions(Tiny(),code),[])
    def test_indexed_binding_does_not_claim_first_image_only(self):
        code={0x3000:(b'a','push','dword ptr [ecx*4+00001900h]'),0x3001:(b'a','call','dword ptr [eax+00000134h]')}
        g={'indirect_calls':[{'slot':0x134,'site':0x3001}]};assets=[{'result_slot':0x1900,'filename':'red'},{'result_slot':0x1904,'filename':'green'}]
        r=binding_candidates(code,g,assets)[0];self.assertTrue(r['indexed']);self.assertFalse(r['index_range_proven']);self.assertEqual(len(r['static_acquisitions']),2)

if __name__=='__main__':unittest.main()

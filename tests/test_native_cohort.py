import struct,sys,unittest,json,hashlib,tempfile
from unittest.mock import patch
from contextlib import contextmanager
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
import native_cohort as n
ROOT=Path(__file__).resolve().parents[1]
for directory in ('d3d9_proof','scene_bridge','remix_ingest'):sys.path.insert(0,str(ROOT/'tools'/directory))

class CohortTests(unittest.TestCase):
    def raw(self):
        b=bytearray(n.SIZE);struct.pack_into('<16I',b,0,n.MAGIC,2,n.SIZE,42,1,2,3,4,200,400,5,0,0,0,0,0)
        struct.pack_into('<8I',b,n.OWNER_BASE,7,3,11,12,100,200,2,99)
        struct.pack_into('<8I',b,n.OWNER_BASE+32,8,4,11,12,100,200,3,99)
        return b
    def test_distinct_owners_shared_geometry(self):
        r=n.decode(self.raw());self.assertEqual(len(r['owners']),2);self.assertEqual(r['owners'][0]['model'],r['owners'][1]['model']);self.assertNotEqual(r['owners'][0]['owner'],r['owners'][1]['owner'])
    def test_malformed(self):
        with self.assertRaises(ValueError):n.decode(self.raw()[:-1])
        b=self.raw();b[0]=0
        with self.assertRaises(ValueError):n.decode(b)
    def test_scope_and_counts(self):
        r=n.decode(self.raw());self.assertEqual(r['session'],[1,2,3,4]);self.assertEqual(r['inserted'],200);self.assertEqual(r['suppressed'],400)

    @contextmanager
    def qualification(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);config=root/'tools/remix_runtime/config';config.mkdir(parents=True)
            for name in ('lights','rendering'):(config/(name+'.toml')).write_bytes((ROOT/f'tools/remix_runtime/config/{name}.toml').read_bytes())
            (root/'code.bin').write_bytes(b'qualified code')
            files={'code.bin':hashlib.sha256(b'qualified code').hexdigest().upper(),**{name:'historical appearance' for name in n.EDITABLE_VISUALS}}
            receipt=root/'qualification.json';receipt.write_text(json.dumps(dict(result='NATIVE_COHORT_PREPARED',policies=['Strict'],files=files)))
            with patch.object(n,'ROOT',root),patch.object(n,'RECEIPT',receipt),patch('async_material_checkout.backend_inputs',return_value={}),patch('async_material_checkout.receipt',side_effect=lambda value:value):yield root

    def test_edited_valid_visuals_do_not_invalidate_code_qualification(self):
        with self.qualification() as root:
            path=root/'tools/remix_runtime/config/lights.toml';path.write_text(path.read_text()+'\n# Edited between runs\n')
            q=n.require_qualification('Strict');self.assertEqual(q['active_visual_inputs']['tools/remix_runtime/config/lights.toml'],hashlib.sha256(path.read_bytes()).hexdigest().upper())

    def test_code_changes_still_reject(self):
        with self.qualification() as root:
            (root/'code.bin').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'Native cohort inputs changed'):n.require_qualification('Strict')

    def test_invalid_light_and_material_controls_reject(self):
        with self.qualification() as root:
            (root/'tools/remix_runtime/config/lights.toml').write_text('schema_version=99\n')
            with self.assertRaises(ValueError):n.require_qualification('Strict')
        with self.qualification() as root:
            (root/'tools/remix_runtime/config/rendering.toml').write_text('[material]\nroughness=99\n')
            with self.assertRaises(ValueError):n.require_qualification('Strict')

if __name__=='__main__':unittest.main()

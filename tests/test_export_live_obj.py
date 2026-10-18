import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
import export_live_obj as target
import test_texture_delivery_audit as fixtures

class LiveObjTests(unittest.TestCase):
    def setUp(self):
        fixtures.TextureDeliveryAuditTests.setUp(self)
        root=self.folder.parents[3];fresh=json.loads((self.folder/'fresh-asset.json').read_text())
        fresh.update(packet_sha256=hashlib.sha256((self.folder/'asset.bin').read_bytes()).hexdigest(),model_name='label_only.mod')
        (self.folder/'fresh-asset.json').write_text(json.dumps(fresh))
        patch=mock.patch.object(target,'ROOT',root);patch.start();self.addCleanup(patch.stop)
        self.out=root/'export'
    def test_export_without_installed_mod_and_exact_readback(self):
        self.assertFalse(any(Path(self.temp.name).rglob('*.mod')))
        target.export(self.folder,self.out);result=target.verify(self.folder,self.out)
        self.assertEqual(result['result'],'LIVE_CAPTURE_OBJ_READBACK_PASS');self.assertEqual(result['triangles'],1)
    def test_no_overwrite(self):
        target.export(self.folder,self.out)
        with self.assertRaisesRegex(ValueError,'overwrite'):target.export(self.folder,self.out)
    def test_modified_uv_rejected(self):
        target.export(self.folder,self.out);path=self.out/'ship.obj'
        lines=path.read_text().splitlines();index=next(i for i,line in enumerate(lines) if line.startswith('vt '))
        lines[index]='vt .123 .456';path.write_text('\n'.join(lines)+'\n')
        with self.assertRaisesRegex(ValueError,'UV changed'):target.verify(self.folder,self.out)

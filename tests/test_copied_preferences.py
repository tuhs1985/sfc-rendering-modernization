import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
from copied_preferences import protected_ini_sha256,prepared_ini_signature,changed_protected_files

BASE=b'[Network]\r\nPlayerName=before\r\nSessionName=OrionPirates\r\n[3D]\r\nWidth=1920\r\n'
class CopiedPreferencesTests(unittest.TestCase):
    def changes(self,raw,extra=None):
        before={'sfc.ini':'original','dxgi.dll':'pinned'}
        after={'sfc.ini':'changed','dxgi.dll':'pinned',**(extra or {})}
        return changed_protected_files(before,after,raw,protected_ini_sha256(BASE))

    def test_player_name_changes_preserved(self):
        self.assertEqual(self.changes(BASE.replace(b'before',b'new player')),[])

    def test_graphics_and_other_network_settings_stay_protected(self):
        for raw in (BASE.replace(b'1920',b'800'),BASE.replace(b'OrionPirates',b'changed')):
            with self.subTest(raw=raw):self.assertEqual(self.changes(raw),['sfc.ini'])

    def test_same_key_in_other_section_remains_protected(self):
        raw=BASE+b'PlayerName=other\r\n'
        self.assertEqual(self.changes(raw),['sfc.ini'])

    def test_duplicate_allowed_key_is_rejected(self):
        with self.assertRaises(ValueError):protected_ini_sha256(BASE.replace(b'[3D]',b'PlayerName=duplicate\r\n[3D]'))

    def test_proxy_changes_are_never_ignored(self):
        self.assertEqual(self.changes(BASE,{'dxgi.dll':'wrong'}),['dxgi.dll'])

    def test_reference_requires_exact_prepared_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'reference.ini';p.write_bytes(BASE)
            self.assertEqual(prepared_ini_signature(p,hashlib.sha256(BASE).hexdigest()),protected_ini_sha256(BASE))
            with self.assertRaises(ValueError):prepared_ini_signature(p,'0'*64)

    def test_session_signature_survives_another_name_change(self):
        start=BASE.replace(b'before',b'first');end=BASE.replace(b'before',b'second')
        self.assertEqual(changed_protected_files({'sfc.ini':'first'},{'sfc.ini':'second'},end,protected_ini_sha256(start)),[])

    def test_missing_signature_does_not_weaken_legacy_recovery(self):
        self.assertEqual(changed_protected_files({'sfc.ini':'first'},{'sfc.ini':'second'},BASE,None),['sfc.ini'])

if __name__=='__main__':unittest.main()

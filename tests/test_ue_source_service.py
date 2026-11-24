"""Read-only UE parent policy; no game or graphics device required."""
import importlib.util
from pathlib import Path
import struct
import sys
from types import SimpleNamespace as NS
import unittest
ROOT=Path(__file__).resolve().parents[1]
for part in ('src/rendering/ue','src/transport','src/assets','src/runtime','src/session'):
    sys.path.insert(0,str(ROOT/part))
from source_reader import SourceReader


class SourceServiceTests(unittest.TestCase):
    def test_unattached_source_is_passive_not_wrong_pid(self):
        import multi_scene as wire
        session='Local\\SFCBridge_'+'a'*32
        header=struct.pack('<16I',wire.MAGIC,3,wire.STORE_BYTES,0,*([0xaaaaaaaa]*4),*([0]*8))
        receiver=NS(retain_assets=False,name=session,channel=NS(read=lambda offset,size:header))
        self.assertIsNone(SourceReader(receiver,ROOT,42).snapshot())

    def test_environment_is_explicitly_non_inserting(self):
        from source_service import source_environment
        env=source_environment({'PATH':'retained','SFC_NATIVE_INSERTION_GATE':'1','SFC_D3D9_GAME_OUTPUT':'1','SFC_REPLACEMENT_FIXTURE_FAULTS':'1'},'return','source','game')
        self.assertEqual(env['PATH'],'retained')
        for key in ('SFC_NATIVE_INSERTION_GATE','SFC_D3D9_PLAYER_REPLACEMENT','SFC_NATIVE_INSERTION_ALL_SHIPS','SFC_D3D9_GAME_OUTPUT'):
            self.assertNotEqual(env.get(key),'1')
        self.assertNotIn('SFC_REPLACEMENT_FIXTURE_FAULTS',env)
        self.assertEqual(env['SFC_PERSISTENT_SCENE'],'1');self.assertEqual(env['SFC_D3D9_MULTISCENE'],'1')

    def test_new_observation_reuses_only_qualified_recovery(self):
        from session_recovery import supported_transaction
        self.assertFalse(supported_transaction({'probe':'UE-SOURCE-001'}))
        self.assertTrue(supported_transaction({'probe':'UE-SOURCE-001','full_support_qualification':{'ue_read_only':True}}))
        self.assertFalse(supported_transaction({'probe':'UE-SOURCE-UNKNOWN','full_support_qualification':{'ue_read_only':True}}))


if __name__=='__main__':unittest.main()

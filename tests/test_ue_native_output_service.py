"""Unique player selection and immutable additive startup environment."""
import sys,unittest
from pathlib import Path
from types import SimpleNamespace as NS
ROOT=Path(__file__).resolve().parents[1]
for part in ("src/rendering/ue","src/transport","src/assets","src/runtime","src/session"):
    sys.path.insert(0,str(ROOT/part))
from native_output_service import choose_player,additive_environment,AdditiveSourceService

def reader():
    return NS(revisions={1:("enemy",7,10,20),2:("player",3,11,21),3:("player",4,12,22)},
              assets={"enemy":NS(model="assets/models/kff/kff.mod"),"player":NS(model="assets/models/fca/fca.mod")})
def row(owner,revision):
    r=[0]*96;r[1]=owner;r[7]=revision;return r

class OutputServiceTests(unittest.TestCase):
    def test_enemy_first_never_selects_enemy(self):
        self.assertEqual(choose_player(reader(),[row(7,1),row(3,2)],"assets/models/fca/fca.mod")[1],3)
    def test_missing_player_waits(self):
        self.assertIsNone(choose_player(reader(),[row(7,1)],"assets/models/fca/fca.mod"))
    def test_two_same_model_owners_are_ambiguous(self):
        with self.assertRaises(ValueError):choose_player(reader(),[row(3,2),row(4,3)],"assets/models/fca/fca.mod")
    def test_environment_cannot_suppress_or_guess_timing(self):
        original={"PATH":"kept","SFC_D3D9_PLAYER_REPLACEMENT":"1","SFC_NATIVE_INSERTION_ALL_SHIPS":"1"}
        env=additive_environment(original)
        self.assertEqual(original["SFC_D3D9_PLAYER_REPLACEMENT"],"1")
        for k in ("SFC_NATIVE_INSERTION_GATE","SFC_NATIVE_INSERTION_ADDITIVE","SFC_D3D9_GAME_OUTPUT","SFC_NATIVE_RESOLUTION","SFC_D3D9_SYNC_BUFFER"):
            self.assertEqual(env[k],"1")
        self.assertEqual(env["SFC_D3D9_PLAYER_REPLACEMENT"],"0");self.assertEqual(env["SFC_NATIVE_INSERTION_ALL_SHIPS"],"0")
        self.assertEqual(env["SFC_NATIVE_INSERTION_POLICY"],"ExtraFrame")
    def test_additive_recovery_requires_qualification(self):
        from session_recovery import supported_transaction
        self.assertFalse(supported_transaction({'probe':'UE-ADDITIVE-001'}))
        self.assertTrue(supported_transaction({'probe':'UE-ADDITIVE-001','full_support_qualification':{'ue_additive':True}}))
        self.assertFalse(supported_transaction({'probe':'UE-ADDITIVE-UNKNOWN','full_support_qualification':{'ue_additive':True}}))
    def test_retired_player_cannot_rebind_to_new_same_model_owner(self):
        service=AdditiveSourceService.__new__(AdditiveSourceService)
        service.reader=reader();service.player_model="assets/models/fca/fca.mod";service.player=(3,2)
        self.assertIsNone(service.choose_anchor([row(4,3)]))
        self.assertEqual(service.player,(3,2))

if __name__=="__main__":unittest.main()

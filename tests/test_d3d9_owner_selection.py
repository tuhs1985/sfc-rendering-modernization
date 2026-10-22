from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/d3d9_proof'))
from owner_selection import choose,selected_model,camera_left_offset

def candidate(owner,model):
    row=[0]*96;row[1]=owner;row[7]=owner
    return row,{'refs':{'model_filename':model}}

class OwnerSelectionTests(unittest.TestCase):
    def test_gap_reduced_one_third_without_depth_or_scale_change(self):
        self.assertEqual(camera_left_offset(24),[-24,0,0])
        self.assertEqual(camera_left_offset(24)[0]/(-1.5*24),2/3)
        for span in (0,-1,500001,float('nan'),float('inf')):
            with self.assertRaises(ValueError):camera_left_offset(span)
    def test_enemy_first_does_not_win(self):
        enemy=candidate(1,'assets/models/kff/kff.mod');player=candidate(2,'assets/models/fca/fca.mod')
        self.assertEqual(choose([enemy,player],selected_model())[0][1],2)
    def test_missing_player_never_falls_back(self):
        self.assertIsNone(choose([candidate(1,'assets/models/kff/kff.mod')],selected_model()))
    def test_same_model_owners_are_ambiguous(self):
        with self.assertRaisesRegex(ValueError,'Multiple owners'):
            choose([candidate(1,selected_model()),candidate(2,selected_model())],selected_model())
    def test_config_rejects_unknown_keys_and_paths(self):
        for raw in (b'selected_model="../fca.mod"',b'selected_model="assets/models/fca/fca.mod"\nfirst_owner=true'):
            with self.assertRaises(ValueError):selected_model(raw)

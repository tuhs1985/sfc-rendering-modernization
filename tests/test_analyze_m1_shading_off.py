import copy
import unittest
from tools.m1_component.analyze_m1_shading_off import analyze


def fixture():
    phases = [{"phase": i, "observed": 100, "eligible": int(i == 3),
               "applied": int(i in (1, 3)), "released": int(i in (1, 3))} for i in range(5)]
    samples = [{"elapsed_ms": elapsed, "phase": phase, "owner": 1,
                "ship": "0x1000", "visual": "0x2000", "model0": "0x3000", "source": "0x4000",
                "effective": "0x5000" if phase in (1, 3) else "0x0", "flags": 0x27,
                "effective_flags": 0x21 if phase == 3 else 0x27, "lit_entries": 1,
                "manager_mode": 0,
                "applied": int(phase in (1, 3)), "restore": int(phase in (1, 3))}
               for phase, elapsed in enumerate((1000, 6000, 9000, 20000, 59000))]
    return {"shading_off": {"enabled": True, "phases": phases, "samples": samples},
            "visual_tint": {"enabled": False, "target_owner_id": 1, "thread_mismatch": 0,
                            "rejected": 0, "restore_failed": 0, "active_scopes": 0,
                            "applied": 2, "restored": 2, "renderer_replaced": 0},
            "geometry_hook_enabled": False, "hooks_restored": True, "gate_activated": True,
            "rejected_semantics": 0, "owner_overflow": 0, "thread_overflow": 0}


class ShadingAnalysisTests(unittest.TestCase):
    def test_mechanism_does_not_claim_visual_or_trl4_pass(self):
        result = analyze(fixture())
        self.assertEqual(result["status"], "MECHANISM_COHERENT_VISUAL_REVIEW_PENDING")
        self.assertEqual(result["formal_m1"], "CONTINUES")

    def test_already_unlit_is_no_op(self):
        data = fixture()
        data["shading_off"]["phases"][3].update(eligible=0, applied=0, released=0)
        data["shading_off"]["samples"][3].update(applied=0, restore=0, effective="0x0",
                                                  flags=0x21, effective_flags=0x21, lit_entries=0)
        data["visual_tint"].update(applied=1, restored=1)
        self.assertEqual(analyze(data)["status"], "NO_OP_LIGHTING_INELIGIBLE")

    def test_manager_mode_three_is_no_op(self):
        data = fixture()
        data["shading_off"]["phases"][3].update(eligible=0, applied=0, released=0)
        data["shading_off"]["samples"][3].update(applied=0, restore=0, effective="0x0",
                                                  effective_flags=0x27, manager_mode=3)
        data["visual_tint"].update(applied=1, restored=1)
        self.assertEqual(analyze(data)["status"], "NO_OP_LIGHTING_INELIGIBLE")

    def test_missing_post_restore_observation(self):
        data = fixture()
        data["shading_off"]["samples"].pop()
        self.assertTrue(analyze(data)["issues"])

    def test_cross_association_and_wrong_mask(self):
        data = fixture()
        data["shading_off"]["samples"][3].update(owner=2, effective_flags=0)
        self.assertEqual(len(analyze(data)["issues"]), 2)

    def test_cleanup_failure(self):
        data = fixture()
        data["visual_tint"]["active_scopes"] = 1
        data["hooks_restored"] = False
        self.assertTrue(analyze(data)["issues"])

    def test_malformed_bounds_and_timing(self):
        data = fixture()
        data["shading_off"]["samples"] = copy.deepcopy(data["shading_off"]["samples"]) * 20
        with self.assertRaises(ValueError):
            analyze(data)
        data = fixture()
        data["shading_off"]["samples"][3]["elapsed_ms"] = 59000
        self.assertTrue(analyze(data)["issues"])


if __name__ == "__main__":
    unittest.main()

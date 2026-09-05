import csv
import json
import tempfile
import unittest
from pathlib import Path

from tools.m1_component.analyze_m1_log import analyze_run, write_outputs


class AnalyzeM1LogTests(unittest.TestCase):
    def test_confirms_bounded_one_owner_chain(self):
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = Path(temporary)
            summary = {
                "schema": "m1.semantic.v1",
                "component_version": "0.1",
                "hooks_restored": True,
                "gate_activated": True,
                "detailed_saturated": True,
                "detailed_events": 4,
                "frames_observed": 120,
                "event_log_bytes": 1200,
                "log_truncated": False,
                "counts": {},
                "correlated_geometry": 1,
                "uncorrelated_geometry": 0,
                "known_exception_00509843": 0,
                "rejected_semantics": 0,
                "owner_overflow": 0,
                "thread_overflow": 0,
                "limits": {
                    "max_frames": 120,
                    "max_events": 10000,
                    "max_owners": 8,
                    "warning_bytes": 16777216,
                    "hard_bytes": 33554432,
                },
            }
            (run_dir / "M1-A-summary.json").write_text(json.dumps(summary))
            (run_dir / "controller.stdout.txt").write_text(
                "component_state=removed\nhook_bytes_restored=true\n"
            )
            fields = [
                "schema", "component_version", "elapsed_ms", "sequence", "frame",
                "event", "thread", "origin", "return_address", "ecx", "ebx",
                "esi", "arg1", "arg2", "arg3", "arg4", "owner_id", "ship",
                "visual", "model0", "manager", "source", "ship_vtable",
                "visual_vtable", "model0_vtable", "lod_count", "lod_override",
                "lod_selected", "selected_child", "correlated",
            ]
            base = {field: "0" for field in fields}
            rows = []
            for sequence, event in enumerate(
                ("ship_owner", "visual_model", "model0", "geometry_submit"), 1
            ):
                row = dict(base)
                row.update(
                    sequence=str(sequence), event=event, owner_id="1",
                    ship="0x10000000", visual="0x20000000",
                    model0="0x30000000" if event in {"model0", "geometry_submit"} else "0",
                    source="0x40000000", correlated="1" if event == "geometry_submit" else "0",
                )
                if event in {"ship_owner", "visual_model"}:
                    row["ship_vtable"] = "0x00796F0C"
                    row["visual_vtable"] = "0x007985A4"
                if event == "model0":
                    row["model0_vtable"] = "0x007983E8"
                rows.append(row)
            with (run_dir / "M1-A-events.csv").open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)

            result = analyze_run(run_dir)
            self.assertEqual(result["result"], "ONE_OWNER_INTEGRATION_CONFIRMED")
            self.assertEqual(result["distinct_owner_epochs"], 1)
            outputs = write_outputs(run_dir, result)
            self.assertTrue(all(path.exists() for path in outputs))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
ANALYZER = REPOSITORY_ROOT / "tools" / "m0_probe" / "analyze_probe_log.py"
HEADER = [
    "kind",
    "elapsed_ms",
    "sequence_or_event",
    "event_or_detail",
    "hit",
    "thread",
    "eip",
    "eax",
    "ebx",
    "ecx",
    "edx",
    "esi",
    "edi",
    "esp",
    "ebp",
    "return_or_stack0",
    "data1",
    "data2",
    "data3",
    "data4",
    "data5",
    "data6",
]


def sample(event: str, sequence: int, **fields: str) -> list[str]:
    row = {name: "0x00000000" for name in HEADER}
    row.update(
        kind="SAMPLE",
        elapsed_ms=str(sequence * 10),
        sequence_or_event=str(sequence),
        event_or_detail=event,
        hit="1",
        thread="1234",
    )
    row.update(fields)
    return [row[name] for name in HEADER]


class AnalyzeProbeLogTests(unittest.TestCase):
    def test_semantic_profile_summary_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            run_directory = Path(temporary_directory)
            log_path = run_directory / "input.csv"
            with log_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(HEADER)
                writer.writerow(["META", "0", "probe", "M0-RT-TEST"])
                writer.writerows(
                    [
                        sample(
                            "visual_model_render",
                            1,
                            ebx="0x11111111",
                            ecx="0x22222222",
                            data1="0x007985A4",
                            data2="0x33333333",
                        ),
                        sample(
                            "visual_to_model_call",
                            2,
                            esi="0x22222222",
                            ecx="0x44444444",
                            edi="0x55555555",
                            data2="0x33333333",
                            data5="0x007983E8",
                            data6="0x007985A4",
                        ),
                        sample(
                            "geometry_submit",
                            3,
                            return_or_stack0="0x006AC503",
                            data1="0x00000003",
                            data2="0x00000000",
                            data3="0x000000B1",
                            data4="0x00000001",
                        ),
                        sample("batch_flush", 4, data5="0x55555555"),
                        sample("scene_begin", 5, data1="0x66666666"),
                        sample(
                            "draw_indexed_call",
                            6,
                            data2="0x66666666",
                            data4="213",
                            data6="213",
                        ),
                    ]
                )

            completed = subprocess.run(
                [sys.executable, str(ANALYZER), str(log_path)],
                cwd=REPOSITORY_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)

            summary_path = run_directory / "M0-RT-TEST-summary.json"
            evidence_path = run_directory / "M0-RT-TEST-evidence.md"
            self.assertTrue(summary_path.is_file())
            self.assertTrue(evidence_path.is_file())
            self.assertFalse((run_directory / "input-summary.json").exists())

            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(summary["probe"], "M0-RT-TEST")
            self.assertEqual(summary["sample_count"], 6)
            self.assertEqual(summary["event_counts"]["geometry_submit"], 1)
            self.assertEqual(
                summary["device_pointer_intersection"], ["0x66666666"]
            )
            self.assertEqual(
                summary["geometry_callers"],
                [{"return_address": "0x006AC503", "hits": 1}],
            )
            self.assertEqual(
                summary["top_geometry_argument_shapes"][0],
                {
                    "arguments": [
                        "0x00000003",
                        "0x00000000",
                        "0x000000B1",
                        "0x00000001",
                    ],
                    "hits": 1,
                },
            )
            self.assertEqual(
                summary["top_draw_shapes_vertex_index_count"][0],
                {"vertex_count": 213, "index_count": 213, "hits": 1},
            )
            self.assertEqual(
                summary["ship_to_visual_model_identities"][0],
                {
                    "ship_owner": "0x11111111",
                    "visual_model": "0x22222222",
                    "visual_vtable": "0x007985A4",
                    "model_source": "0x33333333",
                    "hits": 1,
                },
            )
            self.assertEqual(
                summary["visual_to_model0_identities"][0],
                {
                    "visual_model": "0x22222222",
                    "model0_owner": "0x44444444",
                    "manager": "0x55555555",
                    "model_source": "0x33333333",
                    "model0_vtable": "0x007983E8",
                    "visual_vtable": "0x007985A4",
                    "hits": 1,
                },
            )

            evidence = evidence_path.read_text(encoding="utf-8")
            self.assertIn("# M0-RT-TEST Generated Evidence Packet", evidence)
            self.assertIn("## Ship owner to visual-model identities", evidence)
            self.assertIn("ship 0x11111111 -> visual 0x22222222", evidence)
            self.assertIn("visual 0x22222222 -> Model0 0x44444444", evidence)


if __name__ == "__main__":
    unittest.main()

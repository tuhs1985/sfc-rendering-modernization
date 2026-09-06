#!/usr/bin/env python3
"""Summarize bounded M1 semantic pass-through evidence."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


EXPECTED = {
    "ship": "0x00796F0C",
    "visual": "0x007985A4",
    "model0": "0x007983E8",
}


def _is_zero(value: str) -> bool:
    return not value or int(value, 0) == 0


def analyze_run(run_dir: Path) -> dict:
    summary_path = run_dir / "M1-A-summary.json"
    events_path = run_dir / "M1-A-events.csv"
    controller_path = run_dir / "controller.stdout.txt"
    summary = json.loads(summary_path.read_text(encoding="utf-8-sig"))
    with events_path.open(newline="", encoding="utf-8-sig") as handle:
        events = list(csv.DictReader(handle))
    controller = (
        controller_path.read_text(encoding="utf-8-sig")
        if controller_path.exists()
        else ""
    )

    event_counts = Counter(row["event"] for row in events)
    owner_events: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        owner_id = int(row.get("owner_id", "0") or 0)
        if owner_id:
            owner_events[owner_id].append(row)

    owner_chains = []
    for owner_id, rows in sorted(owner_events.items()):
        ships = {row["ship"] for row in rows if not _is_zero(row["ship"])}
        visuals = {row["visual"] for row in rows if not _is_zero(row["visual"])}
        models = {row["model0"] for row in rows if not _is_zero(row["model0"])}
        sources = {row["source"] for row in rows if not _is_zero(row["source"])}
        owner_chains.append(
            {
                "owner_id": owner_id,
                "ships": sorted(ships),
                "visuals": sorted(visuals),
                "models": sorted(models),
                "sources": sorted(sources),
                "events": len(rows),
                "first_frame": min(int(row["frame"]) for row in rows),
                "last_frame": max(int(row["frame"]) for row in rows),
                "retired": any(row["event"] == "owner_retired" for row in rows),
                "correlated_geometry": sum(
                    row["event"] == "geometry_submit" and row["correlated"] == "1"
                    for row in rows
                ),
            }
        )

    vtable_mismatches = []
    for row in events:
        if row["event"] in {"ship_owner", "visual_model"}:
            if not _is_zero(row["ship_vtable"]) and row["ship_vtable"] != EXPECTED["ship"]:
                vtable_mismatches.append(row["sequence"])
            if not _is_zero(row["visual_vtable"]) and row["visual_vtable"] != EXPECTED["visual"]:
                vtable_mismatches.append(row["sequence"])
        if row["event"] == "model0":
            if not _is_zero(row["model0_vtable"]) and row["model0_vtable"] != EXPECTED["model0"]:
                vtable_mismatches.append(row["sequence"])

    bounds = summary["limits"]
    bounded = (
        summary["detailed_events"] <= bounds["max_events"] <= 100000
        and summary["event_log_bytes"] <= bounds["hard_bytes"] <= 32 * 1024 * 1024
        and bounds["max_frames"] <= 6000
        and bounds["max_owners"] <= 8
        and not summary["log_truncated"]
    )
    controller_restored = "hook_bytes_restored=true" in controller
    has_one_chain = any(
        chain["ships"] and chain["visuals"] and chain["models"]
        and chain["correlated_geometry"]
        for chain in owner_chains
    )
    one_owner_confirmed = (
        summary["hooks_restored"]
        and controller_restored
        and summary["gate_activated"]
        and has_one_chain
        and not vtable_mismatches
        and not summary["owner_overflow"]
        and not summary["thread_overflow"]
        and bounded
    )

    ship_epochs: dict[str, set[int]] = defaultdict(set)
    for chain in owner_chains:
        for ship in chain["ships"]:
            ship_epochs[ship].add(chain["owner_id"])
    reappeared_ships = sorted(
        ship for ship, epochs in ship_epochs.items() if len(epochs) > 1
    )
    coherent_chains = all(
        len(chain["ships"]) <= 1 and len(chain["visuals"]) <= 1
        and len(chain["models"]) <= 1 and len(chain["sources"]) <= 1
        for chain in owner_chains
    )
    lifetime_confirmed = (
        one_owner_confirmed
        and summary["frames_observed"] > 2
        and event_counts["owner_retired"] > 0
        and bool(reappeared_ships)
        and coherent_chains
    )

    return {
        "schema": summary["schema"],
        "component_version": summary["component_version"],
        "result": (
            "MULTI_FRAME_LIFETIME_CONFIRMED"
            if lifetime_confirmed else "ONE_OWNER_INTEGRATION_CONFIRMED"
            if one_owner_confirmed
            else "PARTIAL_OR_REVIEW_REQUIRED"
        ),
        "event_counts": dict(sorted(event_counts.items())),
        "owner_chains": owner_chains,
        "distinct_owner_epochs": len(owner_chains),
        "retirement_events": event_counts["owner_retired"],
        "reappeared_ship_pointers": reappeared_ships,
        "coherent_owner_chains": coherent_chains,
        "correlated_geometry": summary["correlated_geometry"],
        "uncorrelated_geometry": summary["uncorrelated_geometry"],
        "sampled_correlated_geometry": summary.get(
            "sampled_correlated_geometry", event_counts["geometry_submit"]
        ),
        "sampled_uncorrelated_geometry": summary.get(
            "sampled_uncorrelated_geometry", 0
        ),
        "known_exception_00509843": summary["known_exception_00509843"],
        "rejected_semantics": summary["rejected_semantics"],
        "vtable_mismatch_sequences": sorted(set(vtable_mismatches)),
        "bounded": bounded,
        "hooks_restored_by_component": summary["hooks_restored"],
        "hooks_restored_by_controller": controller_restored,
        "raw_summary": summary,
    }


def write_outputs(run_dir: Path, result: dict) -> tuple[Path, Path]:
    json_path = run_dir / "M1-A-analysis.json"
    markdown_path = run_dir / "M1-A-evidence.md"
    json_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# M1 Increment A Generated Evidence Packet",
        "",
        f"- Analyzer result: **{result['result']}**",
        f"- Schema/component: `{result['schema']}` / `{result['component_version']}`",
        f"- Distinct owner epochs: {result['distinct_owner_epochs']}",
        f"- Correlated geometry events: {result['correlated_geometry']}",
        f"- Uncorrelated geometry events: {result['uncorrelated_geometry']}",
        f"- Retained correlated/uncorrelated geometry samples: "
        f"{result['sampled_correlated_geometry']} / "
        f"{result['sampled_uncorrelated_geometry']}",
        f"- Known `0x00509843` exceptions: {result['known_exception_00509843']}",
        f"- Bounded output: {result['bounded']}",
        f"- Component/controller restoration: {result['hooks_restored_by_component']} / "
        f"{result['hooks_restored_by_controller']}",
        "",
        "## Owner chains",
        "",
    ]
    for chain in result["owner_chains"]:
        lines.append(
            f"- owner {chain['owner_id']}: ship {', '.join(chain['ships']) or 'none'}; "
            f"visual {', '.join(chain['visuals']) or 'none'}; "
            f"Model0 {', '.join(chain['models']) or 'none'}; "
            f"source {', '.join(chain['sources']) or 'none'}; "
            f"frames {chain['first_frame']}-{chain['last_frame']}; "
            f"retired {chain['retired']}; "
            f"correlated geometry samples {chain['correlated_geometry']}"
        )
    lines += [
        "",
        "## Review notes",
        "",
        f"- Retirement events: {result['retirement_events']}",
        f"- Reappeared ship pointers: "
        f"{result['reappeared_ship_pointers'] or 'none'}",
        f"- Coherent owner chains: {result['coherent_owner_chains']}",
        f"- Rejected semantic samples: {result['rejected_semantics']}",
        f"- Vtable mismatch sequences: {result['vtable_mismatch_sequences'] or 'none'}",
        "",
        "This packet is generated evidence. Codex must review the raw bounded",
        "sequence, visible game behavior, exact client hashes, and probe definition",
        "before promoting any integration conclusion to CONFIRMED.",
    ]
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, markdown_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    result = analyze_run(args.run_dir)
    for path in write_outputs(args.run_dir, result):
        print(path)


if __name__ == "__main__":
    main()

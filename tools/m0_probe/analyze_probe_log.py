#!/usr/bin/env python3
"""Summarize an M0-RT-001 CSV log into a bounded evidence packet."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def parse_int(value: str) -> int:
    return int(value, 0) if value else 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=Path)
    args = parser.parse_args()

    samples = []
    meta = []
    with args.log.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        for row in reader:
            if not row:
                continue
            if row[0] == "META":
                meta.append(row)
            elif row[0] == "SAMPLE":
                samples.append(dict(zip(header, row)))

    counts = Counter(row["event_or_detail"] for row in samples)
    identities: dict[str, set[int]] = defaultdict(set)
    for row in samples:
        identities[row["event_or_detail"]].add(parse_int(row["ecx"]))

    ordered = [row["event_or_detail"] for row in samples]
    transitions = Counter(zip(ordered, ordered[1:]))
    draw_rows = [row for row in samples if row["event_or_detail"] == "draw_indexed_call"]
    draw_shapes = Counter(
        (parse_int(row["data4"]), parse_int(row["data6"])) for row in draw_rows
    )
    batch_rows = [row for row in samples if row["event_or_detail"] == "batch_flush"]
    geometry_rows = [
        row for row in samples if row["event_or_detail"] == "geometry_submit"
    ]
    geometry_callers = Counter(row["return_or_stack0"] for row in geometry_rows)
    geometry_shapes = Counter(
        tuple(parse_int(row[f"data{i}"]) for i in range(1, 5))
        for row in geometry_rows
    )
    visual_links = Counter(
        (
            row["esi"],
            row["ecx"],
            row["edi"],
            row["data2"],
            row["data5"],
            row["data6"],
        )
        for row in samples
        if row["event_or_detail"] == "visual_to_model_call"
    )
    ship_visuals = Counter(
        (row["ebx"], row["ecx"], row["data1"], row["data2"])
        for row in samples
        if row["event_or_detail"] == "visual_model_render"
    )
    batch_owners = {parse_int(row["data5"]) for row in batch_rows if parse_int(row["data5"])}
    devices = {
        parse_int(row["data1"])
        for row in samples
        if row["event_or_detail"] in {"scene_begin", "scene_end", "engine_present"}
        and parse_int(row["data1"])
    }
    draw_devices = {parse_int(row["data2"]) for row in draw_rows if parse_int(row["data2"])}

    probe_id = next(
        (row[3] for row in meta if len(row) > 3 and row[2] == "probe"),
        args.log.stem,
    )
    summary = {
        "probe": probe_id,
        "sample_count": len(samples),
        "event_counts": dict(sorted(counts.items())),
        "unique_ecx_by_event": {
            key: len(values) for key, values in sorted(identities.items())
        },
        "scene_device_pointers": [f"0x{x:08X}" for x in sorted(devices)],
        "draw_device_pointers": [f"0x{x:08X}" for x in sorted(draw_devices)],
        "device_pointer_intersection": [
            f"0x{x:08X}" for x in sorted(devices & draw_devices)
        ],
        "batch_owner_pointers": [f"0x{x:08X}" for x in sorted(batch_owners)],
        "geometry_callers": [
            {"return_address": address, "hits": count}
            for address, count in geometry_callers.most_common()
        ],
        "top_geometry_argument_shapes": [
            {
                "arguments": [f"0x{x:08X}" for x in shape],
                "hits": count,
            }
            for shape, count in geometry_shapes.most_common(20)
        ],
        "ship_to_visual_model_identities": [
            {
                "ship_owner": item[0],
                "visual_model": item[1],
                "visual_vtable": item[2],
                "model_source": item[3],
                "hits": count,
            }
            for item, count in ship_visuals.most_common()
        ],
        "visual_to_model0_identities": [
            {
                "visual_model": item[0],
                "model0_owner": item[1],
                "manager": item[2],
                "model_source": item[3],
                "model0_vtable": item[4],
                "visual_vtable": item[5],
                "hits": count,
            }
            for item, count in visual_links.most_common()
        ],
        "top_draw_shapes_vertex_index_count": [
            {"vertex_count": shape[0], "index_count": shape[1], "hits": count}
            for shape, count in draw_shapes.most_common(20)
        ],
        "top_transitions": [
            {"from": pair[0], "to": pair[1], "hits": count}
            for pair, count in transitions.most_common(20)
        ],
        "meta": meta,
    }

    output_json = args.log.with_name(f"{probe_id}-summary.json")
    output_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        f"# {probe_id} Generated Evidence Packet",
        "",
        f"- Samples: {len(samples)}",
        f"- Scene Device3 pointers: {', '.join(summary['scene_device_pointers']) or 'none'}",
        f"- Indexed-draw device pointers: {', '.join(summary['draw_device_pointers']) or 'none'}",
        f"- Matching scene/draw device pointers: {', '.join(summary['device_pointer_intersection']) or 'none'}",
        f"- Candidate batch owners: {', '.join(summary['batch_owner_pointers']) or 'none'}",
        "",
        "## Event counts",
        "",
    ]
    lines.extend(f"- {name}: {count}" for name, count in sorted(counts.items()))
    lines += ["", "## Most common indexed draw shapes", ""]
    lines.extend(
        f"- vertices {item['vertex_count']}, indices {item['index_count']}: {item['hits']} hits"
        for item in summary["top_draw_shapes_vertex_index_count"]
    )
    lines += ["", "## Most common observed transitions", ""]
    lines.extend(
        f"- {item['from']} -> {item['to']}: {item['hits']}"
        for item in summary["top_transitions"]
    )
    lines += ["", "## Geometry submission callers", ""]
    lines.extend(
        f"- {item['return_address']}: {item['hits']} hits"
        for item in summary["geometry_callers"]
    )
    lines += ["", "## Most common geometry argument shapes", ""]
    lines.extend(
        f"- {', '.join(item['arguments'])}: {item['hits']} hits"
        for item in summary["top_geometry_argument_shapes"]
    )
    lines += ["", "## Ship owner to visual-model identities", ""]
    lines.extend(
        f"- ship {item['ship_owner']} -> visual {item['visual_model']} "
        f"(vtable {item['visual_vtable']}, source {item['model_source']}): "
        f"{item['hits']} hits"
        for item in summary["ship_to_visual_model_identities"]
    )
    lines += ["", "## Visual-model to Model0 identities", ""]
    lines.extend(
        f"- visual {item['visual_model']} -> Model0 {item['model0_owner']} "
        f"(manager {item['manager']}, source {item['model_source']}, "
        f"vtables {item['visual_vtable']} / {item['model0_vtable']}): "
        f"{item['hits']} hits"
        for item in summary["visual_to_model0_identities"]
    )
    lines += [
        "",
        "This packet is generated evidence. Critical conclusions require review",
        "against the exact event sequence and static address map.",
    ]
    output_md = args.log.with_name(f"{probe_id}-evidence.md")
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(output_md)


if __name__ == "__main__":
    main()

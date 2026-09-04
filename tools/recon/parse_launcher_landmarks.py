#!/usr/bin/env python3
"""Extract compiled launcher service-redirection templates as landmark evidence.

The launcher stores text templates such as ``&H2C4E04 = %http%``.  These are
useful community landmarks, but unlike the SFC Editor definitions they do not
carry a target-executable hash or original/replacement bytes.  This helper
therefore emits them into a separate catalog with deliberately limited claims.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
from pathlib import Path


LANDMARK_RE = re.compile(rb"&H([0-9A-Fa-f]+)\s*=\s*%(gamespy|http)%")

# Target association comes from the surrounding launcher template blocks.  It
# is intentionally explicit and reviewable instead of pretending the compiled
# resource format provides stronger metadata than it does.
TARGETS = {
    0x46814C: ("StarFleet2.exe", "SFC2 EAW client template"),
    0x4684E8: ("StarFleet2.exe", "SFC2 EAW client template"),
    0x468F20: ("StarFleet2.exe", "SFC2 EAW client template"),
    0x46919C: ("StarFleet2.exe", "SFC2 EAW client template"),
    0x469E64: ("StarFleet2.exe", "SFC2 EAW client template"),
    0x2C31D8: ("ServerPlatform.exe", "SFC2 EAW server template"),
    0x2C3218: ("ServerPlatform.exe", "SFC2 EAW server template"),
    0x2C33C4: ("ServerPlatform.exe", "SFC2 EAW server template"),
    0x2C4D38: ("ServerPlatform.exe", "SFC2 OP server template"),
    0x2C4D78: ("ServerPlatform.exe", "SFC2 OP server template"),
    0x2C4E04: ("ServerPlatform.exe", "SFC2 OP server template"),
    0x2C5054: ("ServerPlatform.exe", "SFC2 OP server template"),
    0x2C512C: ("ServerPlatform.exe", "SFC2 OP server template"),
    0x28FEF0: ("ServerPlatform.exe", "SFC3 server template"),
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("launcher", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    data = args.launcher.read_bytes()
    launcher_sha256 = hashlib.sha256(data).hexdigest().upper()
    rows = []
    for match in LANDMARK_RE.finditer(data):
        offset = int(match.group(1), 16)
        target, block = TARGETS.get(offset, ("unknown", "unclassified template"))
        token = match.group(2).decode("ascii").lower()
        rows.append({
            "launcher": args.launcher.name,
            "launcher_sha256": launcher_sha256,
            "launcher_string_file_offset": f"0x{match.start():08X}",
            "target_executable": target,
            "target_build": "not encoded in template",
            "target_file_offset": f"0x{offset:08X}",
            "target_virtual_address": "unknown",
            "original_bytes": "unknown",
            "replacement_bytes": "runtime text substitution; exact bytes unknown",
            "reported_effect": f"replace embedded service endpoint with %{token}% value",
            "probable_subsystem": "network/GameSpy" if token == "gamespy" else "network/MOTD HTTP",
            "confidence": "STRONG HYPOTHESIS",
            "source_context": block,
            "notes": "Target association is based on the surrounding compiled launcher template; no target hash is stored beside this string.",
        })

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} launcher landmarks to {args.output}")


if __name__ == "__main__":
    main()

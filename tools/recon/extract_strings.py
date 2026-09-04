#!/usr/bin/env python3
"""Extract printable ASCII and UTF-16LE strings from binary files read-only."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--min-length", type=int, default=5)
    parser.add_argument("--match", help="case-insensitive regular expression filter")
    args = parser.parse_args()

    data = args.path.read_bytes()
    minimum = max(args.min_length, 1)
    ascii_re = re.compile(rb"[\x20-\x7e]{%d,}" % minimum)
    utf16_re = re.compile(rb"(?:[\x20-\x7e]\x00){%d,}" % minimum)
    match = re.compile(args.match, re.IGNORECASE) if args.match else None
    found: set[tuple[int, str, str]] = set()

    for encoding, pattern in (("ascii", ascii_re), ("utf-16le", utf16_re)):
        for item in pattern.finditer(data):
            value = item.group().decode(encoding, errors="replace")
            if match is None or match.search(value):
                found.add((item.start(), encoding, value))

    for offset, encoding, value in sorted(found):
        print(f"0x{offset:08x}\t{encoding}\t{value}")


if __name__ == "__main__":
    main()

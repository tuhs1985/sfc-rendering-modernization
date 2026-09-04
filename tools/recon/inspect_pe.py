#!/usr/bin/env python3
"""Read-only, dependency-free PE metadata/import/export/string inspector."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import struct
from pathlib import Path


def u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def c_string(data: bytes, offset: int) -> str:
    end = data.find(b"\0", offset)
    if end < 0:
        end = len(data)
    return data[offset:end].decode("ascii", errors="replace")


def inspect(path: Path) -> dict:
    data = path.read_bytes()
    if data[:2] != b"MZ":
        raise ValueError("not an MZ executable")
    pe = u32(data, 0x3C)
    if data[pe:pe + 4] != b"PE\0\0":
        raise ValueError("missing PE signature")

    coff = pe + 4
    machine, section_count, timestamp = struct.unpack_from("<HHI", data, coff)
    optional_size = u16(data, coff + 16)
    characteristics = u16(data, coff + 18)
    optional = coff + 20
    magic = u16(data, optional)
    is_64 = magic == 0x20B
    if magic not in (0x10B, 0x20B):
        raise ValueError(f"unknown optional-header magic 0x{magic:04x}")

    image_base = struct.unpack_from("<Q" if is_64 else "<I", data, optional + (24 if is_64 else 28))[0]
    entry_rva = u32(data, optional + 16)
    subsystem = u16(data, optional + (68 if is_64 else 68))
    data_dirs = optional + (112 if is_64 else 96)
    export_rva, export_size = struct.unpack_from("<II", data, data_dirs)
    import_rva, import_size = struct.unpack_from("<II", data, data_dirs + 8)

    sections = []
    sec = optional + optional_size
    for index in range(section_count):
        off = sec + index * 40
        name = data[off:off + 8].split(b"\0", 1)[0].decode("ascii", errors="replace")
        virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from("<IIII", data, off + 8)
        flags = u32(data, off + 36)
        sections.append({
            "name": name,
            "rva": virtual_address,
            "virtual_size": virtual_size,
            "raw_offset": raw_offset,
            "raw_size": raw_size,
            "characteristics": f"0x{flags:08x}",
        })

    def rva_to_offset(rva: int) -> int:
        for section in sections:
            start = section["rva"]
            span = max(section["virtual_size"], section["raw_size"])
            if start <= rva < start + span:
                return section["raw_offset"] + rva - start
        if rva < sec:
            return rva
        raise ValueError(f"RVA 0x{rva:x} does not map to a section")

    imports = []
    if import_rva:
        pos = rva_to_offset(import_rva)
        thunk_size = 8 if is_64 else 4
        ordinal_mask = 1 << (63 if is_64 else 31)
        unpack_thunk = "<Q" if is_64 else "<I"
        while pos + 20 <= len(data):
            original, _, _, name_rva, first_thunk = struct.unpack_from("<IIIII", data, pos)
            if not any((original, name_rva, first_thunk)):
                break
            dll = c_string(data, rva_to_offset(name_rva))
            thunk_rva = original or first_thunk
            thunk_pos = rva_to_offset(thunk_rva)
            symbols = []
            iat = []
            symbol_index = 0
            while thunk_pos + thunk_size <= len(data):
                value = struct.unpack_from(unpack_thunk, data, thunk_pos)[0]
                if not value:
                    break
                if value & ordinal_mask:
                    symbol = f"ordinal:{value & 0xffff}"
                else:
                    hint_name = rva_to_offset(value)
                    symbol = c_string(data, hint_name + 2)
                symbols.append(symbol)
                iat_rva = first_thunk + symbol_index * thunk_size
                iat.append({
                    "symbol": symbol,
                    "rva": f"0x{iat_rva:x}",
                    "va": f"0x{image_base + iat_rva:x}",
                })
                symbol_index += 1
                thunk_pos += thunk_size
            imports.append({"dll": dll, "symbols": symbols, "iat": iat})
            pos += 20

    exports = []
    if export_rva:
        pos = rva_to_offset(export_rva)
        _, _, _, _, _, base, function_count, name_count, _, names_rva, ordinals_rva = struct.unpack_from(
            "<IIHHIIIIIII", data, pos
        )
        names_pos = rva_to_offset(names_rva)
        ordinals_pos = rva_to_offset(ordinals_rva)
        for index in range(name_count):
            name_rva = u32(data, names_pos + index * 4)
            ordinal = u16(data, ordinals_pos + index * 2) + base
            exports.append({"name": c_string(data, rva_to_offset(name_rva)), "ordinal": ordinal})

    return {
        "path": str(path),
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "machine": {0x14C: "x86", 0x8664: "x64"}.get(machine, f"0x{machine:04x}"),
        "timestamp_utc": dt.datetime.fromtimestamp(timestamp, tz=dt.timezone.utc).isoformat(),
        "image_base": f"0x{image_base:x}",
        "entry_rva": f"0x{entry_rva:x}",
        "subsystem": {2: "windows-gui", 3: "windows-console"}.get(subsystem, str(subsystem)),
        "characteristics": f"0x{characteristics:04x}",
        "directory_rvas": {
            "exports": f"0x{export_rva:x}", "exports_size": export_size,
            "imports": f"0x{import_rva:x}", "imports_size": import_size,
        },
        "sections": sections,
        "imports": imports,
        "exports": exports,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--summary", action="store_true", help="omit symbols and section details")
    args = parser.parse_args()
    results = []
    for path in args.paths:
        try:
            item = inspect(path)
            if args.summary:
                item["import_dlls"] = [entry["dll"] for entry in item.pop("imports")]
                item["export_count"] = len(item.pop("exports"))
                item.pop("sections")
            results.append(item)
        except Exception as exc:  # Keep a batch inspection useful if one file is malformed.
            results.append({"path": str(path), "error": str(exc)})
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Normalize d4v1ks SFC editor definitions into a reproducible landmark catalog."""
from __future__ import annotations

import argparse, csv, hashlib, json, re, struct
from pathlib import Path
from inspect_pe import inspect

TYPE_SIZES = {"b":1,"ub":1,"c":1,"op":1,"s":2,"us":2,"u":2,
              "i":4,"ui":4,"f":4,"l":8,"ul":8,"d":8}
FORMATS = {"b":"b","ub":"B","c":"B","op":"B","s":"h","us":"H","u":"H",
           "i":"i","ui":"I","f":"f","l":"q","ul":"Q","d":"d"}
SUBSYSTEMS = {
    "AMD":"weapons/anti-missile defense","Cloak":"cloak/combat resolution",
    "DAC":"damage allocation","Disr":"weapons/disruptor",
    "DisH":"weapons/heavy disruptor","ESG":"weapons/ESG",
    "Fus":"weapons/fusion","Hell":"weapons/hellbore","Maul":"weapons/mauler",
    "Mine":"mines","Misc":"mixed gameplay/camera","Miss":"weapons/missiles",
    "Move":"movement","Phas":"weapons/phasers","Phot":"weapons/photons",
    "Plas":"weapons/plasma","Plas Range":"weapons/plasma","PPD":"weapons/PPD",
    "Ray":"weapons/ray","Scan":"scanner","Sens":"sensors","Shield":"shields",
    "Shut":"shuttles","Speed":"movement/speed","Trac":"tractor",
    "Trans":"transporters/marine combat","Year":"era/content gating",
    "Gamespy":"network/GameSpy","Server/GameSpy":"network/GameSpy"}
LINE_RE = re.compile(
    r"^\s*(?P<comment>//\s*)?(?P<offset>[0-9A-Fa-f]+)\s*:\s*"
    r"(?P<shape>(?:(?:\d+)x)?(?:\d+)?)(?P<type>ub|us|ui|ul|op|b|c|s|u|i|f|l|d)"
    r"(?:\s+(?P<base>2|8|10|16))?(?:\s+(?P<restricted>[Rr]))?"
    r"(?:\s*//\s*(?P<description>.*?))?(?:\s*//\s*(?P<tooltip>.*))?$", re.IGNORECASE)

def section_for_offset(pe, offset):
    image_base = int(pe["image_base"], 16)
    for section in pe["sections"]:
        start = section["raw_offset"]
        if start <= offset < start + section["raw_size"]:
            rva = section["rva"] + offset - start
            return section["name"], rva, image_base + rva
    return None

def dimensions(shape):
    if not shape: return 1, 1
    if "x" in shape:
        rows, columns = shape.split("x")
        return int(rows), int(columns)
    return 1, int(shape)

def decode_values(blob, type_name, base):
    size = TYPE_SIZES[type_name]
    values = [struct.unpack_from("<" + FORMATS[type_name], blob, pos)[0]
              for pos in range(0, len(blob), size)]
    if type_name in {"f","d"}: return "; ".join(f"{v:.9g}" for v in values)
    if type_name in {"c","u"}:
        return blob.decode("utf-8" if type_name == "c" else "utf-16le",
                           errors="replace").rstrip("\0")
    if base == 16 or type_name == "op":
        return "; ".join(f"0x{int(v):X}" for v in values)
    if base == 2: return "; ".join(bin(int(v)) for v in values)
    if base == 8: return "; ".join(oct(int(v)) for v in values)
    return "; ".join(str(v) for v in values)

def parse_definition(definition, executable, version, expected_md5, label):
    data, pe = executable.read_bytes(), inspect(executable)
    actual_md5 = hashlib.md5(data).hexdigest().upper()
    exact_match, rows, tab = actual_md5 == expected_md5.upper(), [], "Uncategorized"
    for line_number, raw in enumerate(definition.read_text(errors="replace").splitlines(), 1):
        tab_match = re.match(r"^\s*[Tt]ab\s+(.+?)\s*$", raw)
        if tab_match and not raw.lstrip().startswith(("*","//")):
            tab = tab_match.group(1); continue
        match = LINE_RE.match(raw)
        if not match: continue
        offset = int(match.group("offset"), 16)
        row_count, column_count = dimensions(match.group("shape"))
        type_name = match.group("type").lower()
        byte_count = row_count * column_count * TYPE_SIZES[type_name]
        location, observed = section_for_offset(pe, offset), data[offset:offset+byte_count]
        base = int(match.group("base") or 10)
        if location:
            section, rva, va = location
            rva_hex, va_hex = f"0x{rva:08X}", f"0x{va:08X}"
        else:
            section, rva_hex, va_hex = "unmapped", "", ""
        notes = []
        if not exact_match: notes.append("definition MD5 does not match inspected executable")
        if section == "unmapped": notes.append("file offset is not mapped by a PE section")
        rows.append({
            "landmark_id":f"{label}-{offset:08X}","executable":label,"version":version,
            "expected_md5":expected_md5.upper(),"observed_md5":actual_md5,
            "build_match":str(exact_match).lower(),
            "status":"commented-candidate" if match.group("comment") else "active",
            "source":str(definition).replace("\\","/"),"source_line":line_number,
            "category":tab,"file_offset":f"0x{offset:08X}","rva":rva_hex,
            "virtual_address":va_hex,"section":section,
            "type_spec":f"{row_count}x{column_count} {type_name}","byte_count":byte_count,
            "original_bytes":observed.hex(" ").upper() if exact_match else "",
            "replacement_bytes":"","observed_build_bytes":observed.hex(" ").upper(),
            "observed_value":decode_values(observed,type_name,base) if len(observed)==byte_count else "",
            "reported_effect":(match.group("description") or "").strip(),
            "tooltip_or_reported_default":(match.group("tooltip") or "").strip(),
            "probable_subsystem":SUBSYSTEMS.get(tab,tab.lower()),
            "confidence":"CONFIRMED" if exact_match else "STRONG HYPOTHESIS",
            "notes":"; ".join(notes)})
    return rows

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=Path.cwd())
    parser.add_argument("--csv",type=Path,required=True)
    parser.add_argument("--json",type=Path,required=True)
    args, root = parser.parse_args(), Path.cwd()
    root = args.root.resolve()
    definitions = [
        (root/"Game Assets/D4v1ks/SFC_Editor/StarFleetOP.txt",
         root/"Game Assets/StarFleetOP.exe","2.5.6.4",
         "2BE8F713F81B1C68D50EAD6088C32886","StarFleetOP.exe"),
        (root/"Game Assets/D4v1ks/SFC_Editor/ServerPlatform.txt",
         root/"Game Assets/ServerPlatform.exe","2.5.6.4",
         "F9EFDB2CDB948DA98DB0561732C1C581","ServerPlatform.exe")]
    rows = []
    for values in definitions: rows.extend(parse_definition(*values))
    args.csv.parent.mkdir(parents=True,exist_ok=True)
    with args.csv.open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    args.json.write_text(json.dumps(rows,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"rows":len(rows),
        "by_executable":{v:sum(r["executable"]==v for r in rows) for v in sorted({r["executable"] for r in rows})},
        "by_status":{v:sum(r["status"]==v for r in rows) for v in sorted({r["status"] for r in rows})}},indent=2))

if __name__ == "__main__": main()

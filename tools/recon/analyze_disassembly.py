#!/usr/bin/env python3
"""Correlate dumpbin disassembly, community landmarks, imports, and string anchors."""
from __future__ import annotations

import argparse, bisect, csv, json, re
from collections import defaultdict
from pathlib import Path
from inspect_pe import inspect

INSN_RE = re.compile(r"^\s*([0-9A-F]{8}):\s+(?:(?:[0-9A-F]{2})\s+)+(.+?)\s*$")
DIRECT_CALL_RE = re.compile(r"\bcall\s+([0-9A-F]{8})\b", re.I)
ABS_RE = re.compile(r"\b([0-9A-F]{6,8})h\b", re.I)
ANCHOR_RULES = [
 ("graphics", re.compile(r"DirectDraw|Direct3D|tDDSurfMgr|tD3DMgr|tD3DView|tDDSurface|"
                         r"ZBuffer|QSDRIVERS|back buffer|front surface|SwapBuffers|CopyToFront",re.I)),
 ("model_material", re.compile(r"assets[/\\](?:models|textures)|Model has a format|"
                               r"material|luminance texture|hardpoint",re.I)),
 ("scene_camera", re.compile(r"viewport|camera|Hud3D|scene",re.I)),
 ("sprite_effect", re.compile(r"sprite|weapon effect|explosion",re.I))]
GRAPHICS_IMPORTS = {"DirectDrawCreate","DirectDrawCreateClipper","DirectDrawEnumerateA",
 "ChangeDisplaySettingsA","EnumDisplaySettingsA","BitBlt","StretchBlt",
 "CreateDIBSection","GetDIBColorTable","SetDIBColorTable","GetDeviceCaps"}

def write_csv(path, rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows: return
    with path.open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)

def parse_disassembly(path):
    instructions=[]
    for raw in path.read_text(errors="replace").splitlines():
        match=INSN_RE.match(raw)
        if match: instructions.append((int(match.group(1),16),match.group(2)))
    return instructions

def raw_to_va(pe, offset):
    base=int(pe["image_base"],16)
    for section in pe["sections"]:
        start=section["raw_offset"]
        if start<=offset<start+section["raw_size"]:
            return base+section["rva"]+offset-start
    return None

def string_anchors(binary, pe):
    data=binary.read_bytes(); anchors=[]
    for match in re.finditer(rb"[\x20-\x7e]{5,}",data):
        value=match.group().decode("ascii",errors="replace")
        category=next((name for name,rule in ANCHOR_RULES if rule.search(value)),None)
        if category:
            va=raw_to_va(pe,match.start())
            if va: anchors.append((va,match.start(),category,value))
    return anchors

def function_name(row):
    text=" ".join([row["string_anchors"],row["imported_apis"]]).lower()
    if "swapbuffers" in text or "copytofront" in text: return "candidate_frame_present"
    if "minitd3ddevice" in text: return "candidate_D3D_device_initialization"
    if "minitinterfaces" in text or "directdrawcreate" in text: return "candidate_DirectDraw_initialization"
    if "menumdispmodes" in text or "enumdisplaysettings" in text: return "candidate_display_mode_enumeration"
    if "minitbuffers" in text or "front surface" in text or "back buffer" in text:
        return "candidate_surface_buffer_initialization"
    if "model_material" in text: return "candidate_model_material_handling"
    if "scene_camera" in text: return "candidate_scene_camera_handling"
    if "sprite_effect" in text: return "candidate_sprite_effect_handling"
    categories=row["landmark_categories"]
    return "candidate_"+re.sub(r"[^a-z0-9]+","_",categories.lower()).strip("_") if categories else "candidate_unknown"

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--binary",type=Path,required=True)
    parser.add_argument("--disassembly",type=Path,required=True)
    parser.add_argument("--landmarks",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    pe=inspect(args.binary); base=int(pe["image_base"],16)
    text=next(s for s in pe["sections"] if s["name"]==".text")
    text_start,text_end=base+text["rva"],base+text["rva"]+text["virtual_size"]
    insns=parse_disassembly(args.disassembly); addresses=[a for a,_ in insns]
    direct_calls=defaultdict(list); starts={int(pe["entry_rva"],16)+base}
    for address,op in insns:
        match=DIRECT_CALL_RE.search(op)
        if match:
            target=int(match.group(1),16); direct_calls[target].append(address)
            if text_start<=target<text_end: starts.add(target)
    for index in range(len(insns)-1):
        if insns[index][1].strip().lower()=="push        ebp" and re.match(
                r"mov\s+ebp,esp",insns[index+1][1].strip(),re.I):
            starts.add(insns[index][0])
    starts=sorted(starts)
    iat={}
    for library in pe["imports"]:
        for item in library["iat"]:
            iat[int(item["va"],16)]=library["dll"]+"!"+item["symbol"]
    refs=defaultdict(list); import_refs=defaultdict(list)
    for address,op in insns:
        for token in ABS_RE.findall(op):
            value=int(token,16); refs[value].append(address)
            if value in iat: import_refs[iat[value]].append(address)
    def containing(address):
        pos=bisect.bisect_right(starts,address)-1
        return starts[pos] if pos>=0 else None
    def instruction_at_or_before(address):
        pos=bisect.bisect_right(addresses,address)-1
        return addresses[pos] if pos>=0 else None
    def end_for(start):
        pos=bisect.bisect_right(starts,start)
        return starts[pos]-1 if pos<len(starts) else text_end-1
    landmarks=list(csv.DictReader(args.landmarks.open(encoding="utf-8")))
    correlations=[]; function_landmarks=defaultdict(list)
    for landmark in landmarks:
        if landmark["executable"]!="StarFleetOP.exe" or landmark["section"]!=".text": continue
        va=int(landmark["virtual_address"],16)
        instruction=instruction_at_or_before(va); function=containing(va)
        function_landmarks[function].append(landmark)
        correlations.append({
          "landmark_id":landmark["landmark_id"],"category":landmark["category"],
          "file_offset":landmark["file_offset"],"virtual_address":landmark["virtual_address"],
          "instruction_address":f"0x{instruction:08X}" if instruction else "",
          "function_start":f"0x{function:08X}" if function else "",
          "function_end_estimate":f"0x{end_for(function):08X}" if function else "",
          "reported_effect":landmark["reported_effect"],
          "boundary_confidence":"STRONG HYPOTHESIS",
          "notes":"function bounds inferred from direct-call targets and conventional EBP prologues"})
    anchor_rows=[]; function_anchors=defaultdict(list)
    for va,offset,category,value in string_anchors(args.binary,pe):
        for xref in refs.get(va,[]):
            function=containing(xref); function_anchors[function].append((category,value,va,xref))
            anchor_rows.append({"category":category,"string":value,
              "string_file_offset":f"0x{offset:08X}","string_va":f"0x{va:08X}",
              "xref_address":f"0x{xref:08X}","function_start":f"0x{function:08X}" if function else "",
              "evidence":"CONFIRMED direct absolute reference"})
    function_imports=defaultdict(set)
    for api,xrefs in import_refs.items():
        if api.split("!",1)[1] not in GRAPHICS_IMPORTS: continue
        for xref in xrefs: function_imports[containing(xref)].add(api)
    selected={f for f in function_landmarks if f}|{f for f in function_anchors if f}|{f for f in function_imports if f}
    function_rows=[]
    for start in sorted(selected):
        end=end_for(start); first=bisect.bisect_left(addresses,start); last=bisect.bisect_right(addresses,end)
        callees=[]; data_refs=set()
        for address,op in insns[first:last]:
            match=DIRECT_CALL_RE.search(op)
            if match: callees.append(int(match.group(1),16))
            for token in ABS_RE.findall(op):
                value=int(token,16)
                if not text_start<=value<text_end and base<=value<base+0x900000:
                    data_refs.add(value)
        cats=sorted({x["category"] for x in function_landmarks.get(start,[])})
        anchors=sorted({f"{x[0]}:{x[1]}" for x in function_anchors.get(start,[])})
        row={"function_start":f"0x{start:08X}","function_end_estimate":f"0x{end:08X}",
             "proposed_name":"","boundary_basis":"direct-call target and/or EBP prologue",
             "boundary_confidence":"STRONG HYPOTHESIS",
             "landmark_count":len(function_landmarks.get(start,[])),
             "landmark_categories":"; ".join(cats),
             "string_anchors":"; ".join(anchors),
             "callers":"; ".join(f"0x{x:08X}" for x in sorted(direct_calls.get(start,[]))),
             "callees":"; ".join(f"0x{x:08X}" for x in sorted(set(callees))),
             "imported_apis":"; ".join(sorted(function_imports.get(start,set()))),
             "referenced_globals":"; ".join(f"0x{x:08X}" for x in sorted(data_refs)[:40]),
             "notes":"name is analytic shorthand, not an original symbol"}
        row["proposed_name"]=function_name(row); function_rows.append(row)
    out=args.output_dir; out.mkdir(parents=True,exist_ok=True)
    write_csv(out/"landmark-function-correlations.csv",correlations)
    write_csv(out/"string-anchor-xrefs.csv",anchor_rows)
    write_csv(out/"function-map.csv",function_rows)
    summary={"instructions":len(insns),"function_start_candidates":len(starts),
      "text_landmarks":len(correlations),"functions_with_landmarks":len(function_landmarks),
      "string_anchor_xrefs":len(anchor_rows),"functions_with_anchor_xrefs":len(function_anchors),
      "graphics_import_xrefs":sum(len(v) for v in function_imports.values()),
      "selected_functions":len(function_rows)}
    (out/"analysis-summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2))

if __name__=="__main__": main()

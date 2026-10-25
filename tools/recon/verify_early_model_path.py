"""Read-only, pinned early model-request/completion path; no hook or asset reads."""
import argparse
import collections
import csv
import hashlib
import io
import json
from pathlib import Path

from inventory_render_types import disassembly_rows, direct
from verify_effect_resource_path import Image

RANGES = (
    (0x00409793, 0x0040A565),
    (0x00413A8D, 0x00413AC3), (0x004156F9, 0x004157ED),
    (0x0042E26B, 0x0042E4B2), (0x0042E650, 0x0042E6D0),
    (0x0042F121, 0x0042F187), (0x0042F39A, 0x0042F3E9),
    (0x0042F51A, 0x0042F806), (0x0042F858, 0x0042F8FC),
    (0x0042FBD4, 0x0042FC18), (0x0042FEF9, 0x00430367),
    (0x004304E4, 0x004304EF), (0x00435632, 0x00435636),
)
ANCHORS = {
    0x004097BE: ('call', '004146A7'),
    0x004097F5: ('mov', 'esi,dword ptr [ebp+8]'),
    0x0040A54C: ('cmp', 'byte ptr [ebp+10h],0'),
    0x0040A550: ('je', '0040A562'),
    0x0040A555: ('lea', 'eax,[esi+38h]'),
    0x0040A55B: ('call', '004156F9'),
    0x0041574E: ('call', '0042F39A'),
    0x00415757: ('call', '00413A8D'),
    0x00413A96: ('mov', 'dword ptr [esi+00000088h],ecx'),
    0x0041579D: ('call', '0042F39A'),
    0x0042F3D7: ('call', '004304E4'),
    0x004304E8: ('call', '0042F51A'),
    0x0042F543: ('mov', 'esi,dword ptr ds:[008F5974h]'),
    0x0042F552: ('call', 'dword ptr [eax+10h]'),
    0x00435632: ('lea', 'eax,[ecx+14h]'),
    0x0042F556: ('call', '007383A0'),
    0x0042F56A: ('call', 'dword ptr [eax+8]'),
    0x0042F56D: ('mov', 'eax,esi'),
    0x0042F5C3: ('call', '0042F858'),
    0x0042F877: ('mov', 'dword ptr ds:[008F5974h],eax'),
    0x0042F8CA: ('mov', 'dword ptr [eax+00000154h],edx'),
    0x0042F8D0: ('mov', 'dword ptr [eax+00000158h],edx'),
    0x0042F5D7: ('call', '0042FEF9'),
    0x0042F5DC: ('test', 'al,al'),
    0x0042F5DE: ('jne', '0042F5F9'),
    0x0042F5E6: ('call', 'dword ptr [eax]'),
    0x004300D7: ('call', '004301E9'),
    0x004300E7: ('call', '004301BD'),
    0x0043010E: ('call', '0042F121'),
    0x00430113: ('mov', 'dword ptr [esi+ebx*4+00000160h],eax'),
    0x0042F165: ('call', 'dword ptr [eax+4]'),
    0x0042E2B0: ('mov', 'dword ptr [edi+0Ch],eax'),
    0x0042E2C6: ('mov', 'dword ptr [edi+14h],eax'),
    0x0042E49E: ('mov', 'al,1'),
    0x0043014D: ('call', '007364C0'),
    0x00430156: ('call', '00430367'),
    0x0043015B: ('mov', 'al,1'),
    0x0042F62F: ('call', '0042F806'),
    0x0042F641: ('call', '0042F756'),
    0x0042F647: ('mov', 'dword ptr [esi+14h],eax'),
    0x0042F65F: ('test', 'byte ptr [esi],20h'),
    0x0042F685: ('call', '0042F756'),
    0x0042F68B: ('mov', 'dword ptr [esi+1Ch],eax'),
    0x0042F7EE: ('call', 'dword ptr [eax+8]'),
    0x0042F74C: ('call', 'dword ptr [eax+38h]'),
    0x0042FC03: ('call', 'dword ptr [eax+14h]'),
    0x0042E689: ('mov', 'dword ptr [esi+0Ch],eax'),
    0x0042E68C: ('mov', 'dword ptr [esi+20h],ecx'),
    0x0042F74F: ('mov', 'eax,edi'),
}


def qualify_rows(image, rows):
    selected = {}
    factory_calls = []
    for va, raw, op, args in rows:
        relevant = any(a <= va < z for a, z in RANGES)
        factory_call = op == 'call' and direct(args) == 0x0042F39A
        if not relevant and not factory_call:
            continue
        if not 1 <= len(raw) <= 15 or image.read(va, len(raw)) != raw:
            raise ValueError(f'Disassembly/PE mismatch: {va:08X}')
        if relevant:
            if va in selected:
                raise ValueError('Duplicate instruction')
            selected[va] = (op, args)
            if len(selected) > 4096:
                raise ValueError('Narrow instruction bound')
        if factory_call:
            factory_calls.append(va)
            if len(factory_calls) > 128:
                raise ValueError('Factory caller bound')
    for va, expected in ANCHORS.items():
        if selected.get(va) != expected:
            raise ValueError(f'Expected path instruction missing/changed: {va:08X}')
    return selected, factory_calls


def historical_trace(path, expected_md5):
    raw = path.read_bytes() if path.stat().st_size <= 8 * 1024**2 else None
    if raw is None:
        raise ValueError('Historical trace8MiB bound')
    metadata = {}
    events = collections.defaultdict(list)
    last_sequence = 0
    for i, row in enumerate(csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))):
        if i >= 100000:
            raise ValueError('Historical row bound')
        if row['kind'] == 'META':
            key = row['sequence_or_event']
            value = row['event_or_detail']
            if key in ('target_md5', 'image_base') and key in metadata and metadata[key] != value:
                raise ValueError('Conflicting historical metadata')
            if key in ('target_md5', 'image_base'):
                metadata[key] = value
        if row['kind'] != 'SAMPLE':
            continue
        seq = int(row['sequence_or_event'])
        if seq <= last_sequence:
            raise ValueError('Historical sequence invalid')
        last_sequence = seq
        event = row['event_or_detail']
        if event not in ('model_parse', 'geometry_submit', 'draw_indexed_call'):
            continue
        elapsed = int(row['elapsed_ms'])
        if elapsed < 0:
            raise ValueError('Historical time invalid')
        if event == 'model_parse' and (row['eip'] != '0x0042FEF9' or row['return_or_stack0'] != '0x0042F5DC'):
            raise ValueError('Historical parser origin mismatch')
        events[event].append(elapsed)
    if metadata.get('target_md5', '').upper() != expected_md5.upper() or metadata.get('image_base') != '0x00400000':
        raise ValueError('Historical client identity mismatch')
    summary = {k: dict(count=len(v), first_ms=min(v), last_ms=max(v)) for k, v in events.items() if v}
    return dict(path=path.as_posix(), sha256=hashlib.sha256(raw).hexdigest().upper(),
                events=summary, interpretation='Parser ENTRY precedes some generic drawing; no named asset, parser completion, tactical gate or reliable free-preparation interval measured. Breakpoint instrumentation affects timing.')


def build(client, disassembly, traces):
    image = Image(client)
    if disassembly.stat().st_size > 128 * 1024**2:
        raise ValueError('Disassembly128MiB bound')
    selected, callers = qualify_rows(image, disassembly_rows(disassembly))
    vtables = ((0x007985A4 + 0x10, 0x00435632), (0x007985A4 + 8, 0x0042F2E6),
               (0x007985A4 + 0x38, 0x0042FBD4), (0x007983E8 + 4, 0x0042E26B),
               (0x007983E8 + 0x14, 0x0042E650))
    for address, target in vtables:
        if int.from_bytes(image.read(address, 4), 'little') != target:
            raise ValueError('Vtable path mismatch')
    broken_suffix = image.read(0x0083CBAC, 9)
    if broken_suffix != b'_BRK.mod\0':
        raise ValueError('Secondary model suffix mismatch')
    return dict(probe='EARLY-MODEL-AVAILABILITY-001', scope='STATIC_AND_EXISTING_EVIDENCE_ONLY',
                client_sha256=hashlib.sha256(image.data).hexdigest().upper(),
                disassembly_sha256=hashlib.sha256(disassembly.read_bytes()).hexdigest().upper(),
                instruction_count=len(selected), checked_anchors=[dict(address=f'0x{va:08X}', opcode=op, operand=args) for va, (op, args) in ANCHORS.items()],
                direct_factory_call_sites=[f'0x{x:08X}' for x in callers],
                checked_vtable_targets=[dict(address=f'0x{a:08X}', target=f'0x{t:08X}') for a, t in vtables],
                secondary_model_suffix='_BRK.mod',
                existing_traces=[historical_trace(p, hashlib.md5(image.data).hexdigest()) for p in traces],
                conclusions=dict(early_filename='CONFIRMED: ship creation path passes definition+38 to004156F9, then0042F39A',
                    parse_before_draw='CONFIRMED code order; historical parser entry samples also precede generic draws',
                    safe_candidate='AFTER0042F51A returns nonzero, post texture acquisition and optional geometry scale; structurally qualify and join owner attachment',
                    cache_warning='0042F858 publishes into008F5974 BEFORE initialization/parser; presence is not completion',
                    timing='UNPROVED: no contemporary named-asset readiness-to-first-visible interval',
                    roster='UNPROVED: no complete mission roster/preselection notification recovered'),
                limits=dict(output_bytes=256*1024, selected_instructions=4096, factory_calls=128, trace_bytes=8*1024**2, trace_rows=100000),
                exclusions=['No runtime hook/ABI qualification','No game/renderer launch','No geometry/image payload or asset-file extraction','No changes to normal loading/capture/backend','No new performance claim'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client', type=Path, default=Path(r'C:\Project\SFC-Remix-Return-Test\StarFleetOP.exe'))
    parser.add_argument('--disassembly', type=Path, default=Path('artifacts/pre-m0/raw/StarFleetOP-2.5.6.4.dumpbin-disasm.txt'))
    parser.add_argument('--historical-trace', type=Path, action='append', default=[])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = build(args.client, args.disassembly, args.historical_trace)
    output = json.dumps(report, indent=2)
    if len(output.encode('utf-8')) > report['limits']['output_bytes']:
        raise ValueError('Report256KiB bound')
    with args.output.open('x', encoding='utf-8') as f:
        f.write(output)
    print(json.dumps({k: report[k] for k in ('scope', 'instruction_count', 'conclusions')}, indent=2))

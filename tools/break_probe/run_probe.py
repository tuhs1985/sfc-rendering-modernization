"""Observe one break-model transition in the controlled game copy."""
import argparse
import collections
import ctypes
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/early_model_probe'))
from capture import HARD, MAGIC, RECORD, Header, digest
from run_probe import BIN, TEST, CLIENT, budget, preflight, run

PROBE = 'BREAK-PIECE-001'
COMPONENT = ROOT / 'artifacts/render-survey/break-probe/bin/break_component.dll'


def locks():
    sources = ROOT / 'tools/early_model_probe'
    paths = [sources / name for name in (
        'build.ps1', 'early_component.cpp', 'early_core.h', 'early_native.h',
        'early_runtime.h', 'run_probe.py', 'capture.py', 'supervision.py',
    )]
    paths += [Path(__file__), Path(__file__).with_name('break_hooks.inl'), COMPONENT,
              ROOT / 'tools/scene_bridge/break_piece.h',
              ROOT / 'tools/scene_bridge/break_pose.h',
              ROOT / 'tools/m1_component/m1_mesh_export.h',
              ROOT / 'tools/m1_component/m1_texture_references.h',
              BIN / 'return_host.exe', BIN / 'return_launcher.exe']
    return {p.relative_to(ROOT).as_posix(): digest(p) for p in paths}


def analyze(path):
    raw = path.read_bytes()
    if not 128 <= len(raw) <= HARD or (len(raw) - 128) % RECORD.size:
        raise ValueError('Break trace length')
    h = Header.from_buffer_copy(raw[:128])
    incomplete = h.status in (1, 2) and not h.endQpc
    if ((h.magic, h.version, h.recordBytes, h.headerBytes) != (MAGIC, 1, RECORD.size, 128)
            or h.hardBytes != HARD or not h.frequency
            or (not incomplete and (h.fileBytes != len(raw)
                                   or h.written != (len(raw) - 128) // RECORD.size))):
        raise ValueError('Break trace envelope')
    issues = collections.Counter()
    loads, visuals, pieces = {}, {}, {}
    handoff = stop = None
    geometry = []
    for seq, row in enumerate(RECORD.iter_unpack(memoryview(raw)[128:]), 1):
        sequence, qpc, token, _ = row[:4]
        kind, _, owner, visual, child, flags, depth, caller = row[4:12]
        a = row[12:52]
        if (sequence != seq or qpc < h.startQpc or (not incomplete and qpc > h.endQpc)
                or kind not in (*range(80, 95), *range(110, 119))
                or flags & ~511 or depth > 8 or any(row[53:])):
            raise ValueError('Break record layout')
        if kind == 82:
            loads[token] = row[52].split(b'\0', 1)[0].decode('ascii')
        elif kind == 83 and visual and a[1]:
            visuals[visual, a[1]] = loads.get(token, '')
        elif kind == 110:
            if handoff or not owner or not visual or not a[0] or caller != 0x416754:
                raise ValueError('Break handoff identity')
            handoff = dict(owner=owner, visual=visual, owner_epoch=a[0], asset_epoch=a[1],
                           model=visuals.get((visual, a[1]), ''), qpc=qpc)
        elif kind in (111, 112, 113):
            if (not handoff or not child or (owner, visual, a[0]) !=
                    (handoff['owner'], handoff['visual'], handoff['owner_epoch'])):
                raise ValueError('Break record is outside selected handoff')
            if kind == 111:
                if child in pieces or caller != 0x41BAFB or len(pieces) == 128:
                    raise ValueError('Break child identity or capacity')
                pieces[child] = dict(child=child, index=a[1], mode=a[2], qpc=qpc, draws=[])
            elif kind == 112:
                piece = pieces.get(child)
                if (not piece or caller != 0x41B9FE or (a[1], a[2]) != (piece['index'], piece['mode'])
                        or a[3] != len(piece['draws']) + 1 or a[3] > 8):
                    raise ValueError('Indexed draw does not match its child')
                piece['draws'].append(dict(qpc=qpc, supplied=a[4:21], composed=a[21:38]))
            else:
                piece = pieces.get(child)
                if not piece or a[1] != piece['index'] or a[2] >= 4:
                    raise ValueError('Geometry snapshot identity')
                geometry.append(dict(child=child, index=a[1], slot=a[2], mesh_status=a[3],
                                     references_status=a[4], first=a[5], count=a[6],
                                     piece_count=a[7]))
                if a[3:5] != (1, 1):
                    issues['geometry_capture_failed'] += 1
                elif not all(path.with_name(f'break-piece-{a[2]}.{extension}').is_file()
                             for extension in ('bin', 'json')):
                    issues['geometry_files_missing'] += 1
        elif kind in (114, 115, 116, 117, 118):
            piece = pieces.get(child)
            if (not piece or not handoff or owner != handoff['owner']
                    or visual != handoff['visual']):
                raise ValueError('Break lifetime/state identity')
            if kind == 118:
                if ((a[0], a[1]) != (handoff['owner_epoch'], piece['index'])
                        or not 1 <= a[2] <= len(piece['draws'])):
                    raise ValueError('Break predicted-pose identity')
                piece.setdefault('predicted_poses', []).append(
                    dict(sample=a[2], qpc=qpc, matched=bool(a[3]), words=a[4:20]))
                if a[3] != 1:
                    issues['simulation_pose_mismatch'] += 1
            elif kind == 117:
                if not 1 <= token <= len(piece['draws']):
                    raise ValueError('Break camera/pose pair')
                piece.setdefault('cameras', []).append(dict(sample=token, qpc=qpc, words=a))
            else:
                if (a[0], a[1]) != (handoff['owner_epoch'], piece['index']):
                    raise ValueError('Break simulation identity')
                if kind == 116:
                    piece['retired_qpc'] = qpc
                else:
                    key = 'draw_states' if kind == 114 else 'updates'
                    piece.setdefault(key, []).append(dict(sample=a[3], qpc=qpc, words=a[4:31]))
        elif kind == 93 and any(a[:3]):
            issues['observer_uncertain'] += 1
        elif kind == 94:
            stop = a[:4]
        if kind >= 110 and flags & 255:
            issues['flagged_break_record'] += 1
    if h.status != 3 or h.error or stop not in ((0, 0, 13, 0), (0, 0, 14, 0), (0, 0, 16, 0)):
        issues['cleanup_unconfirmed'] += 1
    if h.dropped:
        issues['dropped_records'] = h.dropped
    if not handoff:
        issues['handoff_missing'] += 1
    elif not handoff['model'].lower().endswith('_brk.mod'):
        issues['break_filename_unresolved'] += 1
    if not any(len({d['supplied'] for d in p['draws']}) > 1 for p in pieces.values()):
        issues['changing_piece_pose_missing'] += 1
    return dict(result='PARTIAL' if issues else 'INDEXED_BREAK_DRAWS_OBSERVED',
                issues=dict(issues), handoff=handoff, pieces=list(pieces.values()),
                geometry=geometry, finalized=not incomplete,
                qpc_frequency=h.frequency, restored=stop, sha256=digest(path))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    preflight()
    budget()
    if digest(TEST / 'StarFleetOP.exe') != CLIENT:
        raise ValueError('Unexpected copied client for break-piece hooks')
    locks()
    if not args.execute:
        print('Break observer preflight PASS. No game or renderer started.')
        return
    if not ctypes.WinDLL('shell32').IsUserAnAdmin():
        raise ValueError('Run from the established Administrator PowerShell')
    _, result = run(component=COMPONENT, output_name='break.bin', analyze_trace=analyze,
                    probe=PROBE, qualification_locks=locks, run_prefix='break-',
                    instructions='Use a two-ship skirmish without fighters. Destroy one ship in view, '
                                 'keep the debris in view briefly, then exit at the two-beep request.')
    report = result['report']
    print(report['result'], report['issues'], flush=True)


if __name__ == '__main__':
    main()

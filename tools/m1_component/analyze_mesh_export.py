"""Bounded, pointer-independent reader for sfc.mesh.v1. No renderer or asset writes."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import struct

FILE_LIMIT = 2 * 1024 * 1024


def fnv(data):
    value = 2166136261
    for byte in data:
        value = ((value ^ byte) * 16777619) & 0xFFFFFFFF
    return value


def analyze(path, receipt=None):
    path = Path(path)
    if path.stat().st_size > FILE_LIMIT:
        raise ValueError('Packet exceeds 2 MiB')
    with path.open('rb') as stream:
        data = stream.read(FILE_LIMIT + 1)
    if len(data) > FILE_LIMIT or len(data) < 256:
        raise ValueError('Invalid bounded packet length')
    h = struct.unpack_from('<64I', data)
    nv, np, nc, ns = h[16:20]
    if h[0:2] != (0x314D4653, 1):
        raise ValueError('Unsupported mesh schema')
    if not (1 <= nv <= 65536 and 1 <= np <= 512 and np * 3 <= nc <= 4096 and 1 <= ns <= 256):
        raise ValueError('Counts out of bounds')
    if len(data) != h[2] or len(data) != 256 + nv * 12 + np * 36 + nc * 28 + ns * 40:
        raise ValueError('Incomplete packet, trailing bytes or inconsistent lengths')
    hashed = bytearray(data)
    hashed[12:16] = b'\0' * 4
    if fnv(hashed) != h[3]:
        raise ValueError('Packet checksum mismatch')
    capture_ms = None
    if receipt is not None:
        with Path(receipt).open('rb') as stream:
            raw_receipt = stream.read(65537)
        if len(raw_receipt) > 65536:
            raise ValueError('Receipt exceeds 64 KiB')
        record = json.loads(raw_receipt)
        if not isinstance(record, dict) or type(record.get('attempts')) is not int:
            raise ValueError('Malformed receipt')
        if (record.get('schema') != 'sfc.mesh.receipt.v1' or record.get('status') != 1 or
            record.get('complete') is not True or record.get('hooks_restored') is not True or
            record.get('file_write_ok') is not True or not 1 <= record.get('attempts', 0) <= 2 or
            record.get('owner_epoch') != h[4] or record.get('packet_bytes') != h[2] or record.get('packet_fnv1a') != h[3]):
            raise ValueError('Receipt does not corroborate successful capture and cleanup')
        frequency = record.get('capture_qpc_frequency', 0)
        ticks = record.get('capture_qpc_ticks', [])
        if type(frequency) is int and frequency > 0 and isinstance(ticks, list) and len(ticks) == 2 and all(type(t) is int and t >= 0 for t in ticks):
            capture_ms = [t * 1000 / frequency for t in ticks[:record['attempts']]]
    if not h[4] or not h[5] or not all(h[8:13]) or h[7] > 90000 or h[13] != 0x0042E55D:
        raise ValueError('Missing semantic identity or wrong capture path')
    if not 1 <= h[20] <= 64 or h[23] >= h[20]:
        raise ValueError('Invalid selected child')
    selected = h[21] if h[21] != 0xFFFFFFFF else (h[22] if h[20] > 1 else 0)
    if h[23] != selected:
        raise ValueError('Selected child contradicts LOD selection evidence')
    offset = 256
    positions = [struct.unpack_from('<3f', data, offset + i * 12) for i in range(nv)]
    offset += nv * 12
    polygons = [struct.unpack_from('<9I', data, offset + i * 36) for i in range(np)]
    offset += np * 36
    corners = [data[offset + i * 28:offset + (i + 1) * 28] for i in range(nc)]
    offset += nc * 28
    sources = [struct.unpack_from('<10I', data, offset + i * 40) for i in range(ns)]
    source_ids = {s[0] for s in sources}
    if len(source_ids) != ns or any(s >= 256 for s in source_ids):
        raise ValueError('Duplicate or invalid source groups')
    used, histogram, groups = set(), Counter(), Counter()
    normal_lengths, uv_values, alignments = [], [], []
    degenerate = zero_normals = cursor = 0
    referenced_sources = set()
    for poly in polygons:
        count, group, start = poly[0], poly[1], poly[6]
        if not 3 <= count <= 8 or start != cursor or start + count > nc or group not in source_ids:
            raise ValueError('Invalid polygon topology or source association')
        referenced_sources.add(group)
        histogram[count] += 1
        groups[group] += 1
        vertex_indices = []
        for raw in corners[start:start + count]:
            index = struct.unpack_from('<H', raw)[0]
            normal = struct.unpack_from('<3f', raw, 4)
            uv = struct.unpack_from('<2f', raw, 16)
            if index >= nv or not all(math.isfinite(x) for x in (*normal, *uv, *positions[index])):
                raise ValueError('Invalid position index or nonfinite referenced attributes')
            length = math.sqrt(sum(x * x for x in normal))
            normal_lengths.append(length)
            zero_normals += length == 0
            uv_values.append(uv)
            used.add(index)
            vertex_indices.append(index)
        if count == 3:
            a, b, c = (positions[i] for i in vertex_indices)
            ab, ac = ([b[i] - a[i] for i in range(3)], [c[i] - a[i] for i in range(3)])
            cross = (ab[1]*ac[2]-ab[2]*ac[1], ab[2]*ac[0]-ab[0]*ac[2], ab[0]*ac[1]-ab[1]*ac[0])
            length = math.sqrt(sum(x*x for x in cross))
            degenerate += length == 0
            face = struct.unpack('<3f', struct.pack('<3I', *poly[2:5]))
            face_length = math.sqrt(sum(x*x for x in face)) if all(math.isfinite(x) for x in face) else 0
            if length and face_length:
                alignments.append(sum(cross[i]*face[i] for i in range(3))/(length*face_length))
        cursor += count
    if cursor != nc or referenced_sources != source_ids:
        raise ValueError('Unaccounted corners or source records')
    points = [positions[i] for i in used]
    findings = []
    if any(n != 3 for n in histogram):
        findings.append('Nontriangle topology preserved raw; conversion not qualified')
    if degenerate:
        findings.append('Degenerate triangles present; no repair performed')
    if zero_normals:
        findings.append('Zero corner vectors present; no repair performed')
    return {
        'schema': 'sfc.mesh.analysis.v1', 'packet_sha256': hashlib.sha256(data).hexdigest(),
        'packet_bytes': len(data), 'complete_selected_primary_mesh': True,
        'capture_attempt_ms': capture_ms,
        'owner_epoch': h[4], 'thread': h[5], 'frame': h[6], 'elapsed_ms': h[7],
        'provenance': dict(zip(('ship', 'visual', 'model', 'manager', 'source'), h[8:13])),
        'selected_child': h[23], 'vertices': nv, 'referenced_positions': len(used),
        'unused_positions': nv - len(used), 'polygons': np, 'corners': nc,
        'polygon_corner_histogram': dict(histogram), 'source_polygon_counts': dict(groups),
        'bbox': {'min': [min(p[i] for p in points) for i in range(3)],
                 'max': [max(p[i] for p in points) for i in range(3)]},
        'uv_min': [min(p[i] for p in uv_values) for i in range(2)],
        'uv_max': [max(p[i] for p in uv_values) for i in range(2)],
        'normal_length_range': [min(normal_lengths), max(normal_lengths)],
        'nonunit_corner_vectors': sum(abs(x - 1) > 1e-4 for x in normal_lengths),
        'zero_corner_vectors': zero_normals, 'degenerate_triangles': degenerate,
        'face_geometric_alignment_range': [min(alignments), max(alignments)] if alignments else None,
        'findings': findings,
        'limits': ['Not all physical-ship passes or LODs', 'UV numeric interpretation not visually qualified',
                   'Source groups are not recovered textures/materials', 'Raw transforms not external camera/world contract'],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packet', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    try:
        result = analyze(args.packet, args.receipt)
    except (ValueError, OSError, struct.error) as exc:
        parser.exit(1, f'Mesh validation failed: {exc}\n')
    text = json.dumps(result, indent=2, allow_nan=False) + '\n'
    if len(text.encode()) > 65536:
        parser.exit(1, 'Analysis summary exceeds 64 KiB\n')
    if args.output:
        if args.output.resolve() in {p.resolve() for p in (args.packet, args.receipt) if p is not None}:
            parser.exit(1, 'Output must not overwrite evidence\n')
        args.output.write_text(text, encoding='utf-8')
    else:
        print(text, end='')


if __name__ == '__main__':
    main()

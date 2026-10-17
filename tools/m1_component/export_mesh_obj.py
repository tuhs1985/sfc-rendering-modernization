"""Convert a validated selected-primary packet into an isolated Remix-ingest OBJ.

No native game writes, renderer connection, texture recovery or inferred axes.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import struct

from analyze_mesh_export import analyze, FILE_LIMIT

OBJ_LIMIT = 2 * 1024 * 1024
SIDECAR_LIMIT = 65536


def export_obj(packet, output, receipt=None):
    packet, output = Path(packet), Path(output)
    receipt = Path(receipt) if receipt is not None else None
    analysis = analyze(packet, receipt)
    if any(int(n) != 3 for n in analysis['polygon_corner_histogram']):
        raise ValueError('Nontriangle conversion not qualified; original packet retained')
    if analysis['zero_corner_vectors'] or analysis['degenerate_triangles']:
        raise ValueError('Zero vectors or degenerate triangles require adjudication; no repair performed')
    with packet.open('rb') as stream:
        raw = stream.read(FILE_LIMIT + 1)
    if len(raw) > FILE_LIMIT or hashlib.sha256(raw).hexdigest() != analysis['packet_sha256']:
        raise ValueError('Packet changed after validation')
    if output.suffix.lower() != '.obj' or not re.fullmatch(r'[A-Za-z0-9_-]+', output.stem):
        raise ValueError('Use an ASCII letter/digit/underscore/hyphen OBJ basename')
    material = output.with_suffix('.mtl')
    manifest_path = output.with_suffix('.obj-manifest.json')
    targets = (output, material, manifest_path)
    protected = {p.resolve() for p in (packet, receipt) if p is not None}
    if any(p.resolve() in protected or p.exists() for p in targets):
        raise ValueError('Refusing to overwrite evidence or existing derived outputs')
    header = struct.unpack_from('<64I', raw)
    nv, np, nc = header[16:19]
    polygon_offset = 256 + nv * 12
    corner_offset = polygon_offset + np * 36
    lines = ['# Derived from sfc.mesh.v1; NOT a faithful textured SFC scene',
             f'# Packet SHA256 {analysis["packet_sha256"]}',
             '# Native position coordinates/order/UVs; normals normalized in this derived copy only',
             '# No world/camera transform, handedness, unit or winding conversion',
             f'mtllib {material.name}',
             f'o owner_{header[4]}_child_{header[23]}']
    # One independent OBJ vertex/UV/normal per native polygon corner. No welding.
    for c in range(nc):
        corner = corner_offset + c * 28
        index = struct.unpack_from('<H', raw, corner)[0]
        position = struct.unpack_from('<3f', raw, 256 + index * 12)
        normal = struct.unpack_from('<3f', raw, corner + 4)
        uv = struct.unpack_from('<2f', raw, corner + 16)
        length = math.sqrt(sum(x*x for x in normal))
        for prefix, values in (('v', position), ('vt', uv), ('vn', [x/length for x in normal])):
            lines.append(prefix + ' ' + ' '.join(format(x, '.9g') for x in values))
    mapping, last_group = [], None
    for p in range(np):
        poly = struct.unpack_from('<9I', raw, polygon_offset + p * 36)
        group, start = poly[1], poly[6]
        if group != last_group:
            lines += [f'g source_{group:03d}', f'usemtl source_{group:03d}']
            last_group = group
        lines.append('f ' + ' '.join(f'{i}/{i}/{i}' for i in range(start+1, start+4)))
        mapping.append([p, group, p + 1, start])
    obj = ('\n'.join(lines) + '\n').encode('ascii')
    materials = ['# Diagnostic neutral materials; labels are source groups, NOT recovered SFC materials']
    for group in sorted(int(s) for s in analysis['source_polygon_counts']):
        materials += [f'newmtl source_{group:03d}', 'Ka 0 0 0', 'Kd 0.7 0.7 0.7', 'Ks 0 0 0', 'd 1', 'illum 1', '']
    mtl = ('\n'.join(materials) + '\n').encode('ascii')
    manifest = {
        'schema': 'sfc.mesh.obj.v1', 'packet_sha256': analysis['packet_sha256'],
        'cleanup_receipt_validated': receipt is not None,
        'owner_epoch': header[4], 'provenance': analysis['provenance'], 'selected_child': header[23],
        'vertices': nc, 'texture_coordinates': nc, 'normals': nc, 'triangles': np,
        'obj': {'name': output.name, 'bytes': len(obj), 'sha256': hashlib.sha256(obj).hexdigest()},
        'mtl': {'name': material.name, 'bytes': len(mtl), 'sha256': hashlib.sha256(mtl).hexdigest()},
        'polygon_mapping_columns': ['native_polygon_ordinal', 'source_group', 'obj_face_ordinal_1based', 'first_native_corner_ordinal'],
        'polygon_mapping': mapping,
        'policy': {'corner_expansion': 'no_welding', 'positions_uvs_order': 'unchanged',
                   'normals': 'normalized_derived_copy_raw_packet_unchanged',
                   'materials': 'neutral_diagnostic_source_labels_not_recovered',
                   'transforms_axes_units': 'not_converted_or_applied'},
        'consumer_status': 'REMIX_NOT_TESTED',
    }
    manifest_bytes = (json.dumps(manifest, separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')
    if len(obj) > OBJ_LIMIT or len(mtl) > SIDECAR_LIMIT or len(manifest_bytes) > SIDECAR_LIMIT:
        raise ValueError('Derived OBJ/sidecar size limit exceeded before writing')
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation, manifest last = complete derivative set. On I/O failure,
    # preserve owned partials for diagnosis; never delete/overwrite other evidence.
    for path, data in ((output, obj), (material, mtl), (manifest_path, manifest_bytes)):
        with path.open('xb') as stream:
            stream.write(data)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packet', type=Path)
    parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = export_obj(args.packet, args.output, args.receipt)
    except (ValueError, OSError, struct.error) as exc:
        parser.exit(1, f'OBJ export failed: {exc}\n')
    print(f'OBJ prepared: {args.output} ({result["triangles"]} triangles). Remix import NOT TESTED.')


if __name__ == '__main__':
    main()

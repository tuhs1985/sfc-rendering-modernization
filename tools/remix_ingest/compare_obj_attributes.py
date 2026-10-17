"""Compare derived OBJ corner attributes to bounded Kit inspection, without repair."""
import argparse
import json
import math
from pathlib import Path
from run_remix_ingest import write_json


def ordered_key(group, corners):
    values = [tuple(float(v) for v in corner) for corner in corners]
    if len(values) != 3 or any(len(c) != 8 for c in values) or not all(math.isfinite(v) for c in values for v in c):
        raise ValueError('Invalid triangle attributes')
    return group, tuple(values)


def compare(obj, geometry):
    positions, normals, uvs, expected = [], [], [], []
    group = None
    for line in obj.splitlines():
        fields = line.split()
        if not fields:
            continue
        name, values = fields[0], fields[1:]
        if name in ('v', 'vn', 'vt'):
            {'v': positions, 'vn': normals, 'vt': uvs}[name].append(tuple(map(float, values)))
        elif name == 'usemtl':
            group = values[0]
        elif name == 'f':
            corners = []
            for value in values:
                p, t, n = (int(x)-1 for x in value.split('/'))
                if min(p, t, n) < 0:
                    raise ValueError('Only positive OBJ indices admitted')
                corners.append(positions[p]+uvs[t]+normals[n])
            expected.append(ordered_key(group, corners))
    observed = []
    for mesh in geometry['meshes']:
        indices = mesh['indices']
        if mesh['normal_interpolation'] != 'faceVarying' or mesh['uv_interpolation'] != 'faceVarying':
            raise ValueError('Attribute interpolation requires separate adjudication')
        if any(n != 3 for n in mesh['counts']) or sum(mesh['counts']) != len(indices):
            raise ValueError('Invalid inspected topology')
        if len(mesh['normals']) != len(indices) or len(mesh['uv']) != len(indices):
            raise ValueError('Incomplete corner attributes')
        group = str(mesh['material']).rsplit('/', 1)[-1]
        for start in range(0, len(indices), 3):
            corners = [tuple(mesh['points'][indices[i]])+tuple(mesh['uv'][i])+tuple(mesh['normals'][i])
                       for i in range(start, start+3)]
            observed.append(ordered_key(group, corners))
    if max(len(expected), len(observed)) > 512:
        raise ValueError('Comparison exceeds captured triangle limit')
    # Decimal binning can disagree across a rounding boundary for identical
    # float32 values. Compare numeric deltas instead, never mutate either input.
    remaining = list(observed)
    matched, maximum = 0, [0.0]*8
    for group, corners in expected:
        best = None
        for index, (other_group, other_corners) in enumerate(remaining):
            if other_group != group:
                continue
            for shift in range(3):
                delta = [max(abs(corners[i][j]-other_corners[(i+shift)%3][j]) for i in range(3)) for j in range(8)]
                if max(delta) <= 1e-6 and (best is None or max(delta) < best[0]):
                    best = (max(delta), index, delta)
        if best is not None:
            matched += 1
            remaining.pop(best[1])
            maximum = [max(a,b) for a,b in zip(maximum,best[2])]
    return {'schema': 'sfc.remix.corner-comparison.v1', 'match': matched == len(expected) == len(observed),
            'expected_triangles': len(expected), 'observed_triangles': len(observed),
            'missing': len(expected)-matched, 'extra': len(remaining), 'absolute_tolerance': 1e-6,
            'max_position_delta': max(maximum[:3]), 'max_uv_delta': max(maximum[3:5]),
            'max_normal_delta': max(maximum[5:]),
            'scope': 'local position + UV + derived unit normal + source-group binding; cyclic order, absolute numeric tolerance, no repair',
            'not_qualified': 'raw vector meaning, world transform/units, actual materials/textures, recognizable preview'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('obj', type=Path)
    parser.add_argument('geometry', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if any(p.stat().st_size > 2*1024*1024 for p in (args.obj, args.geometry)):
        raise ValueError('Input exceeds 2 MiB')
    result = compare(args.obj.read_text(), json.loads(args.geometry.read_text()))
    write_json(args.output, result)
    print(json.dumps(result))
    return 0 if result['match'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

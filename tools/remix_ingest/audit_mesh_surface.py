"""Read-only geometry diagnostic. Reports conventions, never repairs a mesh."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path


def sub(a, b): return tuple(x-y for x, y in zip(a, b))
def dot(a, b): return sum(x*y for x, y in zip(a, b))
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def audit(data):
    meshes = data['meshes']
    if not 1 <= len(meshes) <= 16:
        raise ValueError('Mesh bound exceeded')
    edges, directions, totals, rows = Counter(), Counter(), Counter(), []
    for mesh in meshes:
        points, indices, normals = mesh['points'], mesh['indices'], mesh['normals']
        if (len(points) > 8192 or len(indices) > 1536 or len(indices) % 3
                or mesh['normal_interpolation'] != 'faceVarying' or len(normals) != len(indices)
                or any(c != 3 for c in mesh['counts']) or sum(mesh['counts']) != len(indices)):
            raise ValueError('Unqualified topology/normal interpolation')
        if any(not math.isfinite(v) for p in points+normals for v in p):
            raise ValueError('Nonfinite geometry')
        cosines = []
        for i in range(0, len(indices), 3):
            if any(type(j) is not int or not 0 <= j < len(points) for j in indices[i:i+3]):
                raise ValueError('Bad index')
            p = [points[j] for j in indices[i:i+3]]
            face = cross(sub(p[1], p[0]), sub(p[2], p[0]))
            if mesh['orientation'] not in ('leftHanded', 'rightHanded'):
                raise ValueError('Unknown facing convention')
            if mesh['orientation'] == 'leftHanded':
                face = tuple(-v for v in face)
            avg = tuple(sum(n[k] for n in normals[i:i+3])/3 for k in range(3))
            denominator = math.sqrt(dot(face, face)*dot(avg, avg))
            if denominator == 0:
                totals['degenerate_or_zero_average'] += 1
            else:
                cosine = dot(face, avg)/denominator
                cosines.append(cosine)
                totals['opposed' if cosine < -.1 else 'aligned' if cosine > .1 else 'near_perpendicular'] += 1
            # Quantization for adjacency analysis only; no vertex welding/output.
            quantized = [tuple(round(v, 6) for v in point) for point in p]
            for a, b in zip(quantized, quantized[1:]+quantized[:1]):
                edges[tuple(sorted((a, b)))] += 1
                directions[(a, b)] += 1
            totals['triangles'] += 1
            if totals['triangles'] > 512:
                raise ValueError('Selected mesh triangle bound exceeded')
        rows.append({'mesh': mesh['path'], 'orientation': mesh['orientation'],
                     'triangles': len(indices)//3, 'opposed': sum(c < -.1 for c in cosines),
                     'aligned': sum(c > .1 for c in cosines),
                     'cos_min': min(cosines) if cosines else None, 'cos_max': max(cosines) if cosines else None})
    return {'schema': 'sfc.surface-audit.v1', 'totals': dict(totals), 'meshes': rows,
            'edge_use_counts': dict(Counter(edges.values())),
            'same_direction_shared_edges': sum(1 for (a, b), n in edges.items() if n == 2
                                               and (directions[(a, b)] == 2 or directions[(b, a)] == 2)),
            'adjacency_quantization': 'local coordinates rounded to 6 decimals; diagnostic only',
            'interpretation': 'Normal/winding opposition is not proof which convention should be changed.',
            'source_edits': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('geometry', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.geometry.stat().st_size > 2*1024*1024:
        raise ValueError('Geometry inspection exceeds 2 MiB')
    raw = args.geometry.read_bytes()
    result = audit(json.loads(raw))
    result['input_sha256'] = hashlib.sha256(raw).hexdigest()
    encoded = (json.dumps(result, indent=2, allow_nan=False)+'\n').encode()
    if len(encoded) > 65536:
        raise ValueError('Audit report exceeds 64 KiB')
    with args.output.open('xb') as stream:
        stream.write(encoded)
    print(json.dumps(result['totals']))


if __name__ == '__main__': main()

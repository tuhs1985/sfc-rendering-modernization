"""Compare actual Blender importer/control output with retained renderer inputs."""
from collections import Counter
from pathlib import Path
import argparse
import hashlib
import json
import struct

import numpy as np
from PIL import Image
from audit_texture_delivery import audit


def corners(path):
    with Image.open(path) as image:
        rgb = np.asarray(image.convert('RGB'))
    h, w = rgb.shape[:2]
    return [rgb[int(h*y), int(w*x)].tolist()
            for x, y in ((.25, .25), (.75, .25), (.25, .75), (.75, .75))]


def label(samples):
    result = []
    for rgb in samples:
        r, g, b = rgb
        result.append('yellow' if min(r, g) > b*2 else ('red', 'green', 'blue')[int(np.argmax(rgb))])
    return result


def imported_uvs(obj, imported):
    positions, uv, expected = [], [], []
    material = None
    for line in Path(obj).read_text().splitlines():
        fields = line.split()
        if not fields:
            continue
        if fields[0] == 'v':
            positions.append(tuple(map(float, fields[1:])))
        elif fields[0] == 'vt':
            uv.append(tuple(map(float, fields[1:])))
        elif fields[0] == 'usemtl':
            material = fields[1]
        elif fields[0] == 'f':
            for vertex in fields[1:]:
                i, t, *_ = map(int, vertex.split('/'))
                expected.append((material, positions[i-1], uv[t-1]))
    def key(row):
        name, xyz, st = row
        # Actual imported local arrays retain OBJ coordinates. Keep float32
        # bits exact, including UVs, to catch a silent 1-v or swapped assignment.
        return name, struct.pack('<3f', *xyz), struct.pack('<2f', *st)
    if Counter(map(key, expected)) != Counter(map(key, imported)):
        raise ValueError('Blender importer changed corner position/material/UV association')
    return len(expected)


def analyze(control, obj, old_run, current_run, remix_control):
    control, obj = Path(control), Path(obj)
    count = imported_uvs(obj, json.loads((control/'imported-corners.json').read_text()))
    before, after = corners(control/'corners.png'), corners(control/'blender-quad.png')
    raw = (Path(remix_control)/'emission-off.bgra').read_bytes()
    if len(raw) != 256*256*4:
        raise ValueError('Retained Remix control size')
    rgb = np.frombuffer(raw, dtype='u1').reshape(256, 256, 4)[:, :, [2, 1, 0]]
    samples = [np.median(rgb[y-3:y+4, x-3:x+4], axis=(0, 1)).tolist()
               for x, y in ((98,98), (158,98), (98,158), (158,158))]
    if label(before) != ['red','green','blue','yellow']:
        raise ValueError('Asymmetric input is not as documented')
    if label(after) != ['blue','yellow','red','green'] or label(samples) != label(before):
        raise ValueError('Convention comparison did not confirm expected relationship')
    old, current = audit(old_run), audit(current_run)
    a, b = (Path(old_run)/'live-mesh.bin').read_bytes(), (Path(current_run)/'live-mesh.bin').read_bytes()
    if a != b:
        raise ValueError('Current ship mesh differs from the Blender-export source')
    return dict(result='UV_ORIGIN_DIFFERENCE_CONFIRMED', blender=json.loads((control/'result.json').read_text())['blender'],
                imported_corners=count, old_audit=old, current_audit=current,
                same_native_mesh_sha256=hashlib.sha256(a).hexdigest(),
                source_image_corners=label(before), blender_render_corners=label(after),
                remix_render_corners=label(samples),
                first_difference='Same numeric V addresses opposite image row origins: Blender bottom-left versus Remix/DDS top-left',
                candidate_adapter='Remix-only v = 1 - captured_v, or equivalent image row conversion, never both',
                limitations=['No production correction applied','Native SFC parity still requires matched visual check',
                             'Retained Remix control completed readback but shutdown was PARTIAL'])


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    for name in ('control','obj','old_run','current_run','remix_control'):
        p.add_argument(name, type=Path)
    args = p.parse_args()
    print(json.dumps(analyze(**vars(args)), indent=2))

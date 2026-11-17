"""Prepare and verify the standalone D3D9 replay of one captured main drone quad."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess
import sys

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'effect_probe'))
from capture import read_native_draw


EXTENT = 48
ATLAS_SHA256 = 'd12dd3b782d99772914b81fea810927339e8b62420b323c727b2505b4b84e915'
RENDER = dict(z_enable=1, z_write_enable=0, alpha_test_enable=0, src_blend=2,
              dest_blend=2, cull_mode=1, z_func=4, alpha_ref=0, alpha_func=8,
              alpha_blend_enable=1, color_key_enable=0)
TEXTURE = dict(color_op=4, color_arg1=2, color_arg2=0, alpha_op=2, alpha_arg1=2,
               alpha_arg2=1, address_u=1, address_v=1, mag_filter=2, min_filter=2, mip_filter=1)


def replay(trace, bitmap, executable, output):
    draw = read_native_draw(trace)
    if (draw['texture']['filename'].lower() != 'assets/textures/fx0.bmp' or
        draw['render_state'] != RENDER or draw['texture_stage_0'] != TEXTURE or
        draw['indices'] != [0, 1, 2, 0, 2, 3]):
        raise ValueError('Draw does not match the qualified main-quad replay state')
    atlas_hash = hashlib.sha256(bitmap.read_bytes()).hexdigest()
    if atlas_hash != ATLAS_SHA256:
        raise ValueError('Unexpected fx0.bmp content')
    with Image.open(bitmap) as image:
        atlas = image.convert('RGB')
    vertices = draw['vertices']
    if ([v['batch_index'] for v in vertices] != list(range(4)) or
        len({v['rhw'] for v in vertices}) != 1 or
        any(not 0.95 < v['depth'] < 0.99 or v['diffuse_argb'] != 0xffffffff or v['specular_argb'] for v in vertices)):
        raise ValueError('Unsupported captured vertices for this replay')
    a, b, c, d = vertices
    left, bottom = a['screen_xy']
    right, top = c['screen_xy']
    if (b['screen_xy'][0] != right or abs(b['screen_xy'][1] - bottom) > 1 / 1024 or
        d['screen_xy'] != [left, top]):
        raise ValueError('Expected an axis-aligned main quad')
    x0, y0 = math.floor(left) - 8, math.floor(top) - 8
    u0, v0 = a['uv']
    u1, v1 = c['uv']
    if not (0 < right - left < 32 and 0 < bottom - top < 32 and
            b['uv'] == [u1, v0] and d['uv'] == [u0, v1]):
        raise ValueError('Quad bounds or atlas interpolation do not match the replay fixture')
    output.mkdir(parents=True)
    with (output / 'input.bin').open('xb') as packet:
        for vertex in vertices:
            x, y = vertex['screen_xy']
            packet.write(struct.pack('<4f2I2f', x - x0, y - y0, vertex['depth'], vertex['rhw'],
                                     vertex['diffuse_argb'], vertex['specular_argb'], *vertex['uv']))
        packet.write(struct.pack('<6H', *draw['indices']))
        packet.write(atlas.tobytes('raw', 'BGRX'))
    subprocess.run([str(executable.resolve()), str(output.resolve())], check=True, timeout=40)

    images = {}
    for name in ('raw-v', 'inverted-v', 'destination', 'occluded', 'two-depths'):
        raw = (output / (name + '.bgra')).read_bytes()
        if len(raw) != EXTENT * EXTENT * 4:
            raise ValueError('D3D9 readback length mismatch')
        images[name] = Image.frombytes('RGBA', (EXTENT, EXTENT), raw, 'raw', 'BGRA').convert('RGB')
        images[name].save(output / (name + '.png'))
    background = (0x17, 0x2b, 0x3d)
    errors = {'raw-v': 0, 'inverted-v': 0}
    differences = 0
    for y in range(EXTENT):
        for x in range(EXTENT):
            sx, sy = x + x0, y + y0
            raw, flipped, added, occluded, twice = (im.getpixel((x, y)) for im in images.values())
            expected = tuple(min(255, base + value) for base, value in zip(background, flipped))
            if added != expected or occluded != background or twice != tuple(min(255, value * 2) for value in flipped):
                raise ValueError(f'Additive blend or depth control disagrees at {sx},{sy}')
            differences += raw != flipped
            if not (left <= sx < right and top <= sy < bottom):
                if any((*raw, *flipped)):
                    raise ValueError(f'Color outside the captured footprint at {sx},{sy}')
                continue
            u = u0 + (sx - left) / (right - left) * (u1 - u0)
            v = v1 + (sy - top) / (bottom - top) * (v0 - v1)
            for name, row, color in (('raw-v', v, raw), ('inverted-v', 1 - v, flipped)):
                px, py = u * atlas.width - 0.5, row * atlas.height - 0.5
                ix, iy = math.floor(px), math.floor(py)
                fx, fy = px - ix, py - iy
                neighbors = [atlas.getpixel(((ix + dx) % atlas.width, (iy + dy) % atlas.height))
                             for dy in (0, 1) for dx in (0, 1)]
                weights = ((1-fx)*(1-fy), fx*(1-fy), (1-fx)*fy, fx*fy)
                error = max(abs(value - sum(rgb[channel] * weight for rgb, weight in zip(neighbors, weights)))
                            for channel, value in enumerate(color))
                errors[name] = max(errors[name], error)
    if differences < 100 or max(errors.values()) > 4:
        raise ValueError(f'Replay orientation or screen samples disagree: differences={differences}, errors={errors}')
    report = dict(trace_sha256=draw['trace_sha256'], atlas_sha256=atlas_hash,
                  native_scene_ordinal=draw['native_scene_ordinal'], screen_origin=[x0, y0],
                  differing_rgb_pixels=differences, max_rgb_error_vs_cpu=errors,
                  additive_blend=True, depth_test=True, depth_writes_disabled=True,
                  assumptions='D3D9 HAL, non-MSAA RGB8 targets, isolated fixture; no native pixel reference')
    (output / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('trace', 'bitmap', 'executable', 'output'):
        parser.add_argument(key, type=Path)
    args = parser.parse_args()
    replay(args.trace, args.bitmap, args.executable, args.output)

"""Compare packaged UE pixels with a separate source-space software rasterizer."""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


def reference(scene, folder, frame_index=0, *, include_depth=False):
    frame = scene['frames'][frame_index]
    width, height = map(int, frame['viewport'][2:])
    positions = np.array(scene['positions'])
    transform = np.array(frame['projection']) @ np.array(frame['view']) @ np.array(frame['model'])
    clip = np.c_[positions, np.ones(len(positions))] @ transform.T
    ndc = clip[:, :3] / clip[:, 3, None]
    xy = (ndc[:, :2] * [1, -1] + 1) * [width / 2, height / 2]
    result = np.zeros((height, width, 3), dtype=np.uint8)
    depth = np.full((height, width), np.inf)
    interior = np.zeros((height, width), dtype=bool)
    corners = scene['corners']
    for group in scene['groups']:
        image = scene['images'][group['primary']['filename']]
        texture = np.frombuffer((folder / image['file']).read_bytes(), dtype=np.uint8)
        texture = texture.reshape(image['height'], image['width'], 4)[:, :, [2, 1, 0]]
        start, count = group['first_index'], group['index_count']
        for offset in range(start, start + count, 3):
            triangle = [corners[i] for i in scene['indices'][offset:offset + 3]]
            ids = [corner[0] for corner in triangle]
            if np.any(clip[ids, 3] <= 0):
                raise ValueError('Reference fixture crosses camera plane')
            points = xy[ids]
            low = np.maximum(0, np.floor(points.min(0)).astype(int))
            high = np.minimum([width - 1, height - 1], np.ceil(points.max(0)).astype(int))
            if np.any(high < low):
                continue
            x, y = np.meshgrid(np.arange(low[0], high[0] + 1) + .5,
                               np.arange(low[1], high[1] + 1) + .5)
            a, b, c = points
            denominator = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
            if abs(denominator) < 1e-10:
                continue
            u = ((b[1] - c[1]) * (x - c[0]) + (c[0] - b[0]) * (y - c[1])) / denominator
            v = ((c[1] - a[1]) * (x - c[0]) + (a[0] - c[0]) * (y - c[1])) / denominator
            weights = np.stack([u, v, 1 - u - v], axis=-1)
            z = weights @ ndc[ids, 2]
            area = np.s_[low[1]:high[1] + 1, low[0]:high[0] + 1]
            selected = (weights.min(-1) >= 0) & (z < depth[area])
            corrected = weights / clip[ids, 3]
            uv = (corrected @ np.array([corner[2] for corner in triangle])) / corrected.sum(-1)[..., None]
            texels = np.floor(uv * [image['width'], image['height']]).astype(int)
            colour = texture[texels[..., 1] % image['height'], texels[..., 0] % image['width']]
            result[area][selected] = colour[selected]
            depth[area][selected] = z[selected]
            interior[area][selected] = weights.min(-1)[selected] > .05
    if include_depth:
        return result, np.isfinite(depth), interior, depth
    return result, np.isfinite(depth), interior


def verify(scene_file, rendered, output, frame_index=0):
    scene = json.loads(scene_file.read_text(encoding='utf-8'))
    expected, coverage, interior = reference(scene, scene_file.parent, frame_index)
    actual = np.array(Image.open(rendered).convert('RGB'))
    if actual.shape != expected.shape:
        raise ValueError('Rendered dimensions differ from captured viewport')
    selected = interior & (expected.max(-1) > 8)
    differences = np.abs(actual.astype(int) - expected.astype(int)).max(-1)
    count = int(selected.sum())
    if not count:
        raise ValueError('No source interior pixels available for comparison')
    report = dict(compared_pixels=count, source_coverage_pixels=int(coverage.sum()),
                  within_three_levels=float((differences[selected] <= 3).mean()),
                  mean_max_channel_error=float(differences[selected].mean()),
                  rendered_nonblack_pixels=int((actual.max(-1) > 8).sum()))
    Image.fromarray(expected).save(output / 'reference.png')
    Image.fromarray(np.clip(np.abs(actual.astype(int) - expected.astype(int)) * 4, 0, 255).astype('uint8')).save(output / 'difference.png')
    (output / 'pixel-comparison.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scene', type=Path)
    parser.add_argument('rendered', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--frame-index', type=int, default=0)
    args = parser.parse_args()
    print(json.dumps(verify(args.scene, args.rendered, args.output, args.frame_index)))

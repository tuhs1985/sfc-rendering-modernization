"""Bounded, read-only original BMP -> copied BMP/PNG -> Remix DDS pixel audit."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

from PIL import Image, ImageChops, ImageStat

MAX_FILE = 128*1024*1024


def load(path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size > MAX_FILE:
        raise ValueError('Missing or oversized comparison image')
    raw = path.read_bytes()
    with Image.open(path) as image:
        if not 1 <= image.width <= 4096 or not 1 <= image.height <= 4096:
            raise ValueError('Image exceeds qualified dimensions')
        image.load()
        info = dict(path=str(path), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                    width=image.width, height=image.height, format=image.format, mode=image.mode)
        if raw.startswith(b'DDS '):
            info['mipmap_count'] = struct.unpack_from('<I', raw, 28)[0]
            info['fourcc'] = raw[84:88].decode('ascii', errors='replace')
            if raw[84:88] == b'DX10':
                info['dxgi_format'] = struct.unpack_from('<I', raw, 128)[0]
        return image.convert('RGBA'), info


def difference(original, derived):
    if original.size != derived.size:
        raise ValueError('Resolution changed; no resizing permitted during comparison')
    diff = ImageChops.difference(original.convert('RGB'), derived.convert('RGB'))
    stat = ImageStat.Stat(diff)
    changed = sum(any(rgb) for rgb in zip(*(iter(diff.tobytes()),)*3))
    rmse = math.sqrt(sum(x*x for x in stat.rms)/3)
    return dict(exact_rgb=not any(stat.sum), changed_rgb_pixels=changed,
                total_pixels=original.width*original.height,
                mean_absolute_error_rgb=stat.mean,
                maximum_absolute_error_rgb=[hi for lo, hi in diff.getextrema()],
                rmse_rgb=rmse, psnr_db=None if rmse == 0 else 20*math.log10(255/rmse),
                alpha_exact=original.getchannel('A').tobytes() == derived.getchannel('A').tobytes())


def compare(capture, ingestion, preview):
    capture, ingestion, preview = map(Path, (capture, ingestion, preview))
    manifest_path = capture/'textured/association-manifest.json'
    if manifest_path.stat().st_size > 512*1024:
        raise ValueError('Manifest exceeds limit')
    manifest = json.loads(manifest_path.read_text())
    if not 1 <= len(manifest['images']) <= 10:
        raise ValueError('Image count exceeds envelope')
    report = dict(schema='sfc.texture.pixel-comparison.v1', images=[],
                  comparison='decoded RGBA at base resolution; no resizing, flips, repairs or colour correction applied',
                  not_proven='UV placement on geometry, runtime sampling/LOD, lighting, secondary image role')
    primary = {g['primary'] for g in manifest['groups']}
    for resource in manifest['images']:
        original, original_info = load(resource['original_path'])
        if original_info['sha256'] != resource['original_sha256']:
            raise ValueError('Original no longer matches capture manifest')
        row = dict(id=resource['id'], original=original_info, primary=resource['id'] in primary, comparisons=[])
        paths = [('copied_original', capture/'textured'/resource['original_copy'], 'original_sha256'),
                 ('derived_png', capture/'textured'/resource['derived'], 'derived_sha256'),
                 ('ingestion_png', ingestion/'input'/resource['derived'], 'derived_sha256')]
        if row['primary']:
            name = f'resource_{resource["id"]:04d}.a.rtex.dds'
            paths += [('ingested_dds', ingestion/'output/textures'/name, None),
                      ('preview_dds', preview/'textures'/name, None)]
        for stage, path, expected_hash in paths:
            image, info = load(path)
            if expected_hash and info['sha256'] != resource[expected_hash]:
                raise ValueError('Captured/staged image hash changed')
            result = difference(original, image)
            if stage == 'ingested_dds':
                # Diagnostic alternative scores only; never transform an output image.
                result['orientation_rmse'] = {
                    'unchanged': result['rmse_rgb'],
                    'vertical_flip': difference(original, image.transpose(Image.Transpose.FLIP_TOP_BOTTOM))['rmse_rgb'],
                    'horizontal_flip': difference(original, image.transpose(Image.Transpose.FLIP_LEFT_RIGHT))['rmse_rgb']}
            row['comparisons'].append(dict(stage=stage, image=info, **result))
        if row['primary'] and row['comparisons'][-1]['image']['sha256'] != row['comparisons'][-2]['image']['sha256']:
            raise ValueError('Preview DDS differs from ingestion output')
        report['images'].append(row)
    report['original_copy_and_png_exact'] = all(c['exact_rgb'] and c['alpha_exact']
        for r in report['images'] for c in r['comparisons'] if c['stage'] in ('copied_original','derived_png','ingestion_png'))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture', type=Path)
    parser.add_argument('ingestion', type=Path)
    parser.add_argument('preview', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = compare(args.capture, args.ingestion, args.preview)
    data = (json.dumps(result, indent=2, allow_nan=False)+'\n').encode()
    if len(data) > 65536:
        raise ValueError('Comparison report exceeds 64 KiB')
    with args.output.open('xb') as stream:
        stream.write(data)
    print(json.dumps({'original_copy_and_png_exact': result['original_copy_and_png_exact'],
                      'images': len(result['images']), 'output': str(args.output)}))
    return 0 if result['original_copy_and_png_exact'] else 2


if __name__ == '__main__':
    raise SystemExit(main())

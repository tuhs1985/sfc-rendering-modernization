"""Stage a local UE proof project and checked SFC capture; original assets stay local."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/asset_diagnostics'))
from inspect_scene import read_scene
from scene_bundle import resolve_image, texture


def prepare(replay, game, output):
    scene = read_scene(replay, ROOT, game_root=game)
    output = output.resolve()
    if not output.is_relative_to((ROOT / 'artifacts/ue5-proof').resolve()) or output.exists():
        raise ValueError('Use a new directory under artifacts/ue5-proof')
    output.mkdir(parents=True)
    shutil.copytree(ROOT / 'src/ue5_proof', output / 'project')
    evidence = output / 'input'
    evidence.mkdir()
    images = {}
    for group in scene['groups']:
        primary = group['primary']
        name = primary['filename']
        if name in images:
            continue
        raw = resolve_image(game, name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != primary['original_sha256']:
            raise ValueError('Original image changed after inspection')
        metadata, pixels = texture(raw)
        if hashlib.sha256(pixels).hexdigest() != primary['source_bgra_sha256']:
            raise ValueError('Decoded image differs from inspected source')
        filename = f'texture-{len(images)}.bgra'
        (evidence / filename).write_bytes(pixels)
        images[name] = dict(file=filename, width=metadata['width'], height=metadata['height'],
                            sha256=hashlib.sha256(pixels).hexdigest(),
                            original_sha256=primary['original_sha256'])
    scene['images'] = images
    scene['proof_schema'] = 'sfc.ue5.offline-proof.v1'
    (evidence / 'scene.json').write_text(json.dumps(scene), encoding='utf-8')
    print(json.dumps(dict(project=str(output/'project/SFCSceneProof.uproject'),
                          input=str(evidence/'scene.json'), model=scene['asset']['model'],
                          corners=len(scene['corners']), images=len(images))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('replay', type=Path)
    parser.add_argument('game', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    prepare(args.replay, args.game, args.output)

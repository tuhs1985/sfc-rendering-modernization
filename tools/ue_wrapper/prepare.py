"""Prepare only checked source inputs; never copy a game or the old UE project."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/asset_diagnostics'))
from inspect_scene import read_scene
from scene_bundle import resolve_image, texture


def prepare(replay, game, output):
    output = output.resolve()
    if not output.is_relative_to((ROOT / 'artifacts/ue-foundation/inputs').resolve()) or output.exists():
        raise ValueError('Use a new fixture directory under artifacts/ue-foundation/inputs')
    scene = read_scene(replay, ROOT, game_root=game)
    images = {}
    output.mkdir(parents=True)
    for group in scene['groups']:
        association = group['primary']
        name = association['filename']
        if name in images:
            continue
        raw = resolve_image(game, name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != association['original_sha256']:
            raise ValueError('Original fixture image changed')
        metadata, decoded = texture(raw)
        decoded_hash = hashlib.sha256(decoded).hexdigest()
        if decoded_hash != association['source_bgra_sha256']:
            raise ValueError('Decoded fixture image changed')
        file = f'texture-{len(images)}.bgra'
        (output / file).write_bytes(decoded)
        images[name] = dict(file=file, width=metadata['width'], height=metadata['height'],
                            sha256=decoded_hash, original_sha256=association['original_sha256'])
    scene.update(images=images, proof_schema='sfc.ue5.offline-proof.v1')
    path = output / 'scene.json'
    path.write_text(json.dumps(scene), encoding='utf-8')
    return path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('replay', type=Path)
    parser.add_argument('game', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    print(prepare(args.replay, args.game, args.output))

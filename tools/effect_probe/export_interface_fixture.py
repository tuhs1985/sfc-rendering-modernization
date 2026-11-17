"""Encode a saved native draw for the standalone retained-frame interface test."""
import argparse
from pathlib import Path
import struct

from capture import RENDER_STATES, TEXTURE_STATES, read_native_draw


def fixture_bytes(draw):
    vertices = draw['vertices']
    indices = draw['indices']
    texture = draw['texture']['filename'].encode('ascii')
    if not 3 <= len(vertices) <= 16 or not 3 <= len(indices) <= 42 or not 0 < len(texture) < 256:
        raise ValueError('Native interface fixture bounds')
    # Frame key and checksum are populated by the fixture after acquiring a
    # normal retained frame. The saved draw supplies its own trace provenance.
    header = struct.pack(
        '<8I2Q32s2Q6I256s',
        0x31544645, 1, 1216, 0, 0, 0, 0, 0, 0, 0,
        bytes.fromhex(draw['trace_sha256']), draw['flush_order'], draw['engine_present_ordinal'],
        draw['owner_epoch'], draw['texture']['run_local_resource_id'],
        draw['first_batch_index'], len(vertices), len(indices), 0, texture,
    )
    states = struct.pack(
        '<22I',
        *(draw['render_state'][name] for name in RENDER_STATES.values()),
        *(draw['texture_stage_0'][name] for name in TEXTURE_STATES.values()),
    )
    packed = b''.join(
        struct.pack('<I4f2I2f', v['batch_index'], *v['screen_xy'], v['depth'], v['rhw'],
                    v['diffuse_argb'], v['specular_argb'], *v['uv'])
        for v in vertices
    )
    return header + states + packed.ljust(576, b'\0') + struct.pack('<42IQ', *indices, *([0] * (42 - len(indices))), 0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('trace', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    with args.output.open('xb') as output:
        output.write(fixture_bytes(read_native_draw(args.trace)))

"""Read-only qualification inputs for player-mesh suppression; never launches SFC.

Extracts two small instruction ranges from the pinned client into ignored test
artifacts. The executable and its disassembly remain local, not repository data.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from verify_effect_resource_path import Image, CLIENT

RANGES = {'wrapper': (0x006AC5A0, 0x006AC757),
          'prepare': (0x006ABFC0, 0x006AC596)}
ANCHORS = {
    0x006AC5A0: '83 EC 08 53 56',
    0x006AC600: 'FF 92 80 01 00 00',
    0x006AC631: 'FF 90 80 01 00 00',
    0x006AC66C: 'FF 90 80 01 00 00',
    0x006AC69F: 'FF 90 80 01 00 00',
    0x006AC6D0: 'FF 90 80 01 00 00',
    0x006AC719: 'FF 92 80 01 00 00',
    0x006AC754: 'C2 0C 00',
    0x006ABFFD: '8B 84 24 90 00 00 00',
    0x006AC004: '85 C0 0F 8E 55 05 00 00',
    0x006AC00C: '8B 8C 24 94 00 00 00',
    0x006AC561: '8A 4C 24 44',
    0x006AC57E: 'B0 01 5F 81 C4 84 00 00 00 C2 10 00',
}


def extract(client, output):
    image = Image(client)  # Entire accepted executable hash checked first.
    output.mkdir(parents=True, exist_ok=True)
    checks = []
    for address, text in ANCHORS.items():
        expected = bytes.fromhex(text)
        if image.read(address, len(expected)) != expected:
            raise ValueError(f'Instruction anchor mismatch {address:08X}')
        checks.append(f'{address:08X}')
    target = struct.unpack('<I', image.read(0x007B8D4C + 0x180, 4))[0]
    if target != RANGES['prepare'][0]:
        raise ValueError('Qualified manager polygon slot changed')
    files = {}
    for name, (start, end) in RANGES.items():
        raw = b''.join(image.read(at, min(256, end-at))
                       for at in range(start, end, 256))
        (output / (name+'.bin')).write_bytes(raw)
        files[name] = dict(start=hex(start), end_exclusive=hex(end),
                           bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    result = dict(client_sha256=CLIENT, checks=checks, files=files,
                  manager_vtable='0x007B8D4C', polygon_slot='0x180',
                  result='STATIC_ANCHORS_VERIFIED_NATIVE_EXECUTION_PENDING',
                  limitation='No game hooks or suppression enabled; state methods stubbed in isolated native test')
    (output/'inputs.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--client', type=Path, default=Path(r'C:\Project\SFC-Remix-Return-Test\StarFleetOP.exe'))
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(extract(a.client, a.output), indent=2))

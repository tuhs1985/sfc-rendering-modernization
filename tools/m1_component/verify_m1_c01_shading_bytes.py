"""Read-only exact-build check of adjudicated shading-control byte prefixes."""

import argparse
import hashlib
import json
import struct
from pathlib import Path

from prepare_m1_c01_packet import CLIENT_SHA256

# These are evidence anchors, not a patch list. No process or executable writes.
ANCHORS = {
    0x006AC0E0: '8B 0B',           # source flag DWORD
    0x006AC16C: '8B 87 CC 1E 00 00',
    0x006AC177: '83 E1 F9',       # mode 3 clears both lighting bits
    0x006AC181: 'F6 C1 02',       # mode 4 tests bit 2 before promoting bit 4
    0x006AC186: '0B C8',
    0x006AC18C: 'F6 C1 04',       # polygon lighting branch
    0x006AC18F: '0F 84 E8 00 00 00',
    0x006AC1D0: 'E8 BB D5 FF FF', # polygon response call 006A9790
    0x006AC28B: '83 E0 02',       # vertex lighting selector
    0x006AC2F8: '0F 84 D8 00 00 00',
    0x006AC32E: 'E8 5D D4 FF FF', # vertex response call 006A9790
    0x006AC3D6: '8B 54 24 28',    # unlit RGB copy
    0x0069B250: '8B 44 24 04',    # vector dot helper entry
    0x0069B254: 'D9 40 08',
    0x0069B257: 'D8 49 08',
    # Narrow C-01 corner/transform qualification anchors (not hook sites).
    0x006AC042: '8B 4E 18',       # polygon corner-list pointer
    0x006AC3FA: '83 C2 1C',       # next corner, 28-byte stride
    0x006AC2C9: '8D 8F B0 06 00 00', # composed position matrix
    0x006A97FD: '8B 4C 24 68',   # third lighting argument (vector)
    0x006AA55D: '8D BB F4 06 00 00', # original object transform copy
    0x006AA570: 'F3 A5',         # preceding count 17 DWORDs
    0x006AA581: '8D 8B B0 06 00 00',
    0x006AA61A: '8D B3 88 07 00 00', # original light-slot base
    0x0069CBC0: '83 EC 0C',      # subtract translation / transposed linear map
    0x0069CC40: 'A1 58 40 C7 00', # vector map / runtime dispatch
    0x0069CA30: 'A1 F0 9F C6 00', # position map / runtime dispatch
    0x007B8E30: '50 A5 6A 00',   # manager vtable+E4 -> 006AA550
    0x007B8DE0: '90 F1 69 00',   # manager vtable+94 -> 0069F190
    0x00416323: 'FF 92 E4 00 00 00', # ship transform handoff to manager
    # Isolated polygon-list handoff feasibility, not approved hook/patch sites.
    0x00798424: '52 EB 42 00',   # Model0 vtable+3C lazy secondary-list builder
    0x0042EB94: '89 46 18',      # builder writes Model0+18
    0x0042E551: 'FF 77 14',      # primary list argument from Model0+14
    0x0042E618: 'FF 77 18',      # secondary list argument from Model0+18
    0x007B8E8C: 'A0 C5 6A 00',   # manager+140 wrapper, NOT directly ABFC0
    0x006AC5A0: '83 EC 08 53 56', # list wrapper prologue
    0x006AC2B4: 'F6 06 01',      # prepared position cache test
    0x006AC310: '8B 44 24 1C',   # lighting reads current corner each iteration
    0x007B8ECC: 'C0 BF 6A 00',   # manager+180 -> polygon preparation
    0x007B8ED0: '10 B4 6A 00',   # manager+184 -> generic accumulation
    0x006AB5EC: 'F3 A5',         # eight DWORD numeric output copy
    0x006A9A6D: 'D9 18',         # response output into caller-supplied float triple
    0x006ABFC0: '81 EC 84 00 00 00', # optional private-copy receipt hook: whole instruction
}


def verify(client):
    if client.stat().st_size > 64 * 1024 * 1024:
        raise ValueError('Client input exceeds 64 MiB')
    data = client.read_bytes()
    sha = hashlib.sha256(data).hexdigest().upper()
    if sha != CLIENT_SHA256:
        raise ValueError('Unsupported client hash')
    pe = struct.unpack_from('<I', data, 0x3C)[0]
    if data[pe:pe + 4] != b'PE\0\0':
        raise ValueError('Invalid PE signature')
    machine, count = struct.unpack_from('<HH', data, pe + 4)
    optional_size = struct.unpack_from('<H', data, pe + 20)[0]
    optional = pe + 24
    if machine != 0x14C or struct.unpack_from('<H', data, optional)[0] != 0x10B:
        raise ValueError('Expected x86 PE32')
    base = struct.unpack_from('<I', data, optional + 28)[0]
    sections = []
    for index in range(count):
        offset = optional + optional_size + index * 40
        virtual_size, rva, raw_size, raw_offset = struct.unpack_from('<IIII', data, offset + 8)
        sections.append((rva, raw_size, raw_offset))
    results = []
    for address, text in ANCHORS.items():
        expected = bytes.fromhex(text)
        relative = address - base
        section = next((s for s in sections
                        if s[0] <= relative and relative + len(expected) <= s[0] + s[1]), None)
        if section is None:
            raise ValueError(f'Address not file-backed: {address:08X}')
        offset = section[2] + relative - section[0]
        observed = data[offset:offset + len(expected)]
        if observed != expected:
            raise ValueError(f'Static anchor mismatch at {address:08X}')
        results.append({'va': f'0x{address:08X}', 'file_offset': offset,
                        'bytes': observed.hex(' ').upper()})
    return {'client_sha256': sha, 'anchors': results,
            'result': 'STATIC_PREFIXES_MATCH',
            'limitation': 'Byte corroboration only; not runtime semantics or safe intervention proof.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('client', type=Path)
    print(json.dumps(verify(parser.parse_args().client), indent=2))

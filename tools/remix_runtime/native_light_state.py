"""Decode renderer-neutral native bank snapshots; no guessed physical lights."""
import math
import struct

SIZE = 6156
HEADER = struct.Struct('<16I')


def floats(words):
    return struct.unpack('<%df'%len(words), struct.pack('<%dI'%len(words), *words))


def decode(raw):
    if len(raw) != SIZE:
        raise ValueError('Native light snapshot size')
    h = HEADER.unpack_from(raw)
    if h[:3] != (0x54494c4e, 1, SIZE) or not h[3] or not any(h[4:8]) or not all(h[i] for i in (8,9,11,12,13,14)) or h[15]:
        raise ValueError('Native light snapshot identity/version')
    supplied = struct.unpack_from('<17I', raw, 64)
    view = struct.unpack_from('<17I', raw, 132)
    words = struct.unpack_from('<1024I', raw, 200)
    enables = list(raw[4296:4360])
    points = struct.unpack_from('<192I', raw, 4360)
    directions = struct.unpack_from('<192I', raw, 5128)
    reciprocal = struct.unpack_from('<64I', raw, 5896)
    gate = struct.unpack_from('<I', raw, 6152)[0]
    # First disabled terminates native response;later enabled slots still retained.
    prefix = next((i for i, enabled in enumerate(enables) if not enabled), 64)
    slots = []
    for i in range(64):
        record = list(words[i*16:i*16+16])
        consumed = bool(gate and i < prefix)
        kind = {0:'directional_like', 1:'point_like', 5:'special_positional_unknown'}.get(record[0], 'unqualified')
        used = floats(record[1:11])
        local = floats(points[i*3:i*3+3])+floats(directions[i*3:i*3+3])
        finite = all(math.isfinite(v) for v in used+local)
        slots.append(dict(slot=i, native_type=record[0], enabled_byte=enables[i],
            consumed_by_native_response=consumed, interpretation=kind,
            numeric_status='FINITE' if finite else 'NONFINITE_NOT_USABLE',
            raw_words=record,
            # Never emit NaN into JSON. Keep original words for invalid/unused data.
            values=dict(direction_input=list(used[:3]),position_input=list(used[3:6]),
                contribution_channels=list(used[6:9]),type_dependent_scalar=used[9],
                local_point=list(local[:3]),local_direction=list(local[3:]),
                reciprocal_word=reciprocal[i]) if finite else None))
    return dict(schema='sfc.native-light-snapshot.v1',session_words=list(h[4:8]),
        sequence=h[3],owner_epoch=h[8],frame=h[9],elapsed_ms=h[10],
        manager_process_local=h[11],model_process_local=h[12],source_process_local=h[13],thread=h[14],
        supplied_raw_words=list(supplied),view_raw_words=list(view),
        global_gate_raw=gate,consumed_prefix=prefix,slots=slots,
        limitation='Raw native state only;no sun/weapon classification,world-space conversion,photometric units or Remix eligibility inferred')

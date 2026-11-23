"""Renderer-independent view of the existing source transport.

The receiver owns packet validation and acknowledgements. This facade keeps
source geometry, original images and coherent frame identities for a UE consumer.
It performs no Remix coordinate or material conversions.
"""
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[3]
for part in ('src/assets', 'src/transport', 'tools/remix_ingest', 'tools/m1_component'):
    sys.path.insert(0, str(ROOT / part))

from scene_bundle import resolve_image, texture
from analyze_live_camera import native_matrix
from multi_scene import frame_snapshot, FRAME_BYTES, OFFSET, MAGIC, STORE_BYTES


@dataclass(frozen=True)
class Image:
    filename: str
    original_sha256: str
    decoded_sha256: str
    width: int
    height: int
    bgra: bytes


@dataclass(frozen=True)
class Asset:
    content: str
    model: str
    positions: tuple
    corners: tuple
    polygons: tuple
    groups: tuple


class SourceReader:
    def __init__(self, receiver, game_root, source_pid):
        if not source_pid:
            raise ValueError('Explicit source process required')
        if receiver.retain_assets:
            raise ValueError('Source reader requires ownership of decoded assets')
        self.receiver = receiver
        self.game_root = Path(game_root)
        self.source_pid = source_pid
        self.session = receiver.name
        self.session_words = tuple(int(self.session[-32:][i:i+8],16) for i in range(0,32,8))
        self.images = {}
        self.assets = {}
        self.revisions = {}
        self.image_bytes = 0
        self.asset_bytes = 0
        self.last_sequence = 0
        self.retired_epochs = {}

    def _image(self, filename):
        if filename in self.images:
            return self.images[filename]
        path = resolve_image(self.game_root, filename)
        with path.open('rb') as stream:
            raw = stream.read(128 * 1024 * 1024 + 1)
        if len(raw) > 128 * 1024 * 1024:
            raise ValueError('Original image byte budget')
        description, decoded = texture(raw)
        if self.image_bytes + len(decoded) > 128 * 1024 * 1024:
            raise ValueError('Decoded image byte budget')
        if self.asset_bytes + self.image_bytes + len(decoded) > 256 * 1024 * 1024:
            raise ValueError('Retained source memory budget')
        image = Image(filename, hashlib.sha256(raw).hexdigest(),
                      hashlib.sha256(decoded).hexdigest(),
                      description['width'], description['height'], decoded)
        self.images[filename] = image
        self.image_bytes += len(decoded)
        return image

    def admit(self):
        for revision, mesh in self.receiver.drain(collect=True):
            if revision in self.revisions:
                continue
            resources = {item['id']: item['filename'] for item in mesh['refs']['resources']}
            groups = []
            for group in mesh['groups']:
                primary = resources.get(group['primary'])
                secondary = resources.get(group['secondary']) if group['secondary'] else None
                if primary is None or (group['secondary'] and secondary is None):
                    raise ValueError('Unresolved fresh image association')
                first = self._image(primary)
                second = self._image(secondary) if secondary else None
                groups.append((group['group'], group['flags'], first.filename,
                               first.original_sha256, second.filename if second else None,
                               second.original_sha256 if second else None,
                               mesh['refs'].get('secondary_role')))
            binding = json.dumps(groups, separators=(',', ':')).encode()
            identity = hashlib.sha256(bytes.fromhex(mesh['geometry_sha256']) + binding).hexdigest()
            if identity not in self.assets:
                if self.asset_bytes + mesh['memory_bytes'] + self.image_bytes > 256 * 1024 * 1024:
                    raise ValueError('Retained source asset budget')
                self.assets[identity] = Asset(identity, mesh['refs']['model_filename'],
                    tuple(mesh['points']), tuple(mesh['corners']),
                    tuple(mesh['polygons']), tuple(groups))
                self.asset_bytes += mesh['memory_bytes']
            self.revisions[revision] = (identity, mesh['header'][4],
                                        mesh['header'][10], mesh['header'][12])

    def snapshot(self):
        if self.receiver.name != self.session:
            raise ValueError('Source session changed')
        header = struct.unpack('<16I', self.receiver.channel.read(OFFSET,64))
        if header[0] == 0:
            return None
        if header[:3] != (MAGIC,3,STORE_BYTES):
            raise ValueError('Source layout changed')
        if header[3] != self.source_pid or header[8] or header[4:8] != self.session_words:
            raise ValueError('Source process stopped or changed')
        # The existing transport validates the sealed frame and checksum.
        snapshot = frame_snapshot(self.receiver.channel)
        if snapshot is None:
            return None
        number, _, raw = snapshot
        if len(raw) != FRAME_BYTES:
            raise ValueError('Source frame layout changed')
        sequence, offered, frame, anchor, revision, count = struct.unpack_from('<QQ4I', raw)
        if sequence <= self.last_sequence:
            return None
        instances = []
        retirements = []
        for index in self.receiver.channel.owner_indices():
            row = self.receiver.channel.sample_owner(index)
            if row and row[4] == 2 and row[1] and row[2] <= frame and row[1] not in self.retired_epochs:
                self.retired_epochs[row[1]] = row[2]
                retirements.append(dict(session=self.session, owner_epoch=row[1], revision=row[7],
                                        source_frame=row[2]))
        camera = None
        seen = set()
        anchor_seen = False
        for index in range(count):
            row = struct.unpack_from('<96I', raw, 32 + index * 384)
            if row[2] != frame or row[4] != 1 or not row[48] or row[1] in seen:
                raise ValueError('Incoherent source owner')
            seen.add(row[1])
            if row[1] == anchor:
                if row[7] != revision or (row[94] | (row[95] << 32)) != sequence:
                    raise ValueError('Source anchor sequence mismatch')
                anchor_seen = True
            if row[1] in self.retired_epochs:
                if row[2] <= self.retired_epochs[row[1]]:
                    continue
                raise ValueError('Retired owner epoch reappeared')
            if row[7] not in self.revisions:
                continue
            content, owner, model, source = self.revisions[row[7]]
            if (row[1], row[5], row[6]) != (owner, model, source):
                raise ValueError('Cross-associated source asset')
            if any(row[42:45]):
                continue
            current_camera = (native_matrix(row[49:66]), native_matrix(row[66:83]),
                              struct.unpack('<6f', struct.pack('<6I', *row[83:89])))
            x, y, width, height, half_width, half_height = current_camera[2]
            if (not all(math.isfinite(v) for v in current_camera[2]) or min(x, y) < 0
                    or not 1 <= width <= 4096 or not 1 <= height <= 4096
                    or abs(width-2*half_width) > .001 or abs(height-2*half_height) > .001):
                raise ValueError('Invalid source viewport')
            if camera is not None and current_camera != camera:
                raise ValueError('Source cohort camera changed within frame')
            camera = current_camera
            instances.append(dict(session=self.session, owner_epoch=owner, revision=row[7],
                                  asset=content, model=native_matrix(row[8:25]),
                                  owner_sequence=row[94] | (row[95] << 32)))
        if not anchor_seen:
            raise ValueError('Source anchor missing')
        self.last_sequence = sequence
        return dict(session=self.session, source_pid=self.source_pid, frame=number,
                    sequence=sequence, offered=offered, camera=camera, instances=instances,
                    cohort_hash=struct.unpack_from('<Q',raw,len(raw)-8)[0], retirements=retirements)

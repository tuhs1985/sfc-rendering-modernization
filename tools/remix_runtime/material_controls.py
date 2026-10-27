"""Worker-only, last-good material configuration for the Remix backend."""
from pathlib import Path
import hashlib
import math
import struct
import tomllib
from rendering_config import DEFAULT,section,scoped
def fnv(raw):
    value=14695981039346656037
    for byte in raw:value=((value^byte)*1099511628211)&0xffffffffffffffff
    return value

DEFAULTS=dict(roughness=1.0,illumination_strength=1.0,metallic=0.0,anisotropy=0.0)
MAP_DEFAULTS=dict(roughness_map_enabled=False,roughness_map_strength=0.5,
    roughness_map_black=0.0,roughness_map_white=1.0,
    roughness_map_invert=False,roughness_map_gamma=1.0)

def encode(raw):
    if len(raw)>16384:raise ValueError('Material config16KiB limit')
    row=section(raw,'material')
    if isinstance(row,dict) and 'emissive_intensity' in row:
        if 'illumination_strength' in row:raise ValueError('Use emissive_intensity only;duplicate legacy illumination_strength')
        row=dict(row);row['illumination_strength']=row.pop('emissive_intensity')
    if not isinstance(row,dict) or set(row)-(set(DEFAULTS)|set(MAP_DEFAULTS)):raise ValueError('Unknown material setting')
    values=DEFAULTS|MAP_DEFAULTS|row
    def number(value,low,high):
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not low<=value<=high:
            raise ValueError('Material value outside documented range')
        return float(value)
    floats=[number(values['roughness'],0,1),number(values['illumination_strength'],0,100),
            number(values['metallic'],0,1),number(values['anisotropy'],-1,1)]
    for key in ('roughness_map_enabled','roughness_map_invert'):
        if type(values[key]) is not bool:raise ValueError('Roughness map flags must be boolean')
    floats.extend([float(values['roughness_map_enabled']),number(values['roughness_map_strength'],0,1),
        number(values['roughness_map_black'],0,1),number(values['roughness_map_white'],0,1),
        float(values['roughness_map_invert']),number(values['roughness_map_gamma'],0.25,4)])
    if floats[7]<=floats[6]:raise ValueError('Roughness map white must exceed black')
    body=struct.pack('<2I10f',0x3143544d,2,*floats)
    rounded=struct.unpack('<2I10f',body)
    if rounded[9]<=rounded[8]:raise ValueError('Roughness map levels indistinguishable in transport')
    return body+struct.pack('<Q',fnv(body))

class Relay:
    def __init__(self,folder,path=DEFAULT):
        self.folder=Path(folder);self.path=Path(path);self.digest=None
        self.accepted=0;self.rejected=0;self.messages=0
        self.pending_revision=None;self.active_revision=0;self.reclaimed_bytes=0;self.known_revision=None
        self.adopt_published()
    def adopt_published(self):
        # Asset preparation can publish after this long-lived relay was created.
        # Adopt that outstanding packet before any collection, not just at init.
        try:
            with (self.folder/'material-controls.bin').open('rb') as stream:raw=stream.read(57)
            if len(raw)==56 and struct.unpack_from('<2I',raw)==(0x3143544d,2) and struct.unpack_from('<Q',raw,48)[0]==fnv(raw[:48]):
                revision=struct.unpack_from('<Q',raw,48)[0]
                if revision!=self.known_revision:self.pending_revision=revision;self.known_revision=revision
        except OSError:pass
    def poll(self):
        from roughness_maps import receipt,collect
        self.adopt_published()
        if self.pending_revision is not None:
            ack=receipt(self.folder)
            # One outstanding revision: missing/stale receipts never permit reuse.
            if ack is None or ack[0]!=self.pending_revision:return
            self.active_revision=ack[1];self.pending_revision=None
            self.reclaimed_bytes+=collect(self.folder,{self.active_revision})
            if ack[2]==2 and self.messages<100:
                print('MATERIAL HOST_REJECTED retaining active material',flush=True);self.messages+=1
        self.reclaimed_bytes+=collect(self.folder,{self.active_revision})
        try:
            if self.path.stat().st_size>16384:raise ValueError('Material config16KiB limit')
            raw=scoped(self.path.read_bytes(),'material');digest=hashlib.sha256(raw).hexdigest()
            if digest==self.digest:return
            if self.accepted>=256:raise ValueError('Material revision256/session limit;restart to continue')
            packet=encode(raw)
            # Finish derivative creation before publishing its immutable revision.
            # Worker only; never file access/decoding inside SFC's callback.
            from roughness_maps import prepare
            prepare(self.folder,packet)
            pending=self.folder/'material-controls.pending';pending.write_bytes(packet)
            pending.replace(self.folder/'material-controls.bin')
            self.pending_revision=struct.unpack_from('<Q',packet,48)[0]
            self.known_revision=self.pending_revision
            self.digest=digest;self.accepted+=1
            (self.folder/'materials-config-accepted.toml').write_bytes(raw)
            if self.accepted<=16:(self.folder/f'materials-config-{self.accepted:04d}.toml').write_bytes(raw)
            if self.messages<100:print(f'MATERIAL CONFIG_ACCEPTED revision={self.accepted}',flush=True);self.messages+=1
        except (ValueError,OSError) as exc:
            # Failed preparation was never published; only active files survive.
            if self.pending_revision is None:self.reclaimed_bytes+=collect(self.folder,{self.active_revision})
            self.rejected+=1
            if self.messages<100:print('MATERIAL CONFIG_REJECTED keeping last good: '+str(exc),flush=True);self.messages+=1

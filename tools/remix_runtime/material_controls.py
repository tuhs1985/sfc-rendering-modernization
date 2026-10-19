"""Worker-only, last-good material configuration for the Remix backend."""
from pathlib import Path
import hashlib
import math
import struct
import tomllib
def fnv(raw):
    value=14695981039346656037
    for byte in raw:value=((value^byte)*1099511628211)&0xffffffffffffffff
    return value

DEFAULT=Path(__file__).parent/'config/materials.toml'
DEFAULTS=dict(roughness=1.0,illumination_strength=1.0,metallic=0.0,anisotropy=0.0)

def encode(raw):
    if len(raw)>16384:raise ValueError('Material config16KiB limit')
    data=tomllib.loads(raw.decode('utf-8'))
    if set(data)-{'material'}:raise ValueError('Unknown material section')
    row=data.get('material',{})
    if not isinstance(row,dict) or set(row)-set(DEFAULTS):raise ValueError('Unknown material setting')
    values=DEFAULTS|row
    def number(value,low,high):
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not low<=value<=high:
            raise ValueError('Material value outside documented range')
        return float(value)
    floats=[number(values['roughness'],0,1),number(values['illumination_strength'],0,100),
            number(values['metallic'],0,1),number(values['anisotropy'],-1,1)]
    # SDK colour constants are texture-absent fallbacks,NOT texture multipliers.
    floats.extend([1.0]*6)  # reserved neutral fallback colours,not user controls
    body=struct.pack('<2I10f',0x3143544d,1,*floats)
    return body+struct.pack('<Q',fnv(body))

class Relay:
    def __init__(self,folder,path=DEFAULT):
        self.folder=Path(folder);self.path=Path(path);self.digest=None
        self.accepted=0;self.rejected=0;self.messages=0
    def poll(self):
        try:
            if self.path.stat().st_size>16384:raise ValueError('Material config16KiB limit')
            raw=self.path.read_bytes();digest=hashlib.sha256(raw).hexdigest()
            if digest==self.digest:return
            if self.accepted>=256:raise ValueError('Material revision256/session limit;restart to continue')
            packet=encode(raw)
            pending=self.folder/'material-controls.pending';pending.write_bytes(packet)
            pending.replace(self.folder/'material-controls.bin')
            self.digest=digest;self.accepted+=1
            (self.folder/'materials-config-accepted.toml').write_bytes(raw)
            if self.accepted<=16:(self.folder/f'materials-config-{self.accepted:04d}.toml').write_bytes(raw)
            if self.messages<100:print(f'MATERIAL CONFIG_ACCEPTED revision={self.accepted}',flush=True);self.messages+=1
        except (ValueError,OSError) as exc:
            self.rejected+=1
            if self.messages<100:print('MATERIAL CONFIG_REJECTED keeping last good: '+str(exc),flush=True);self.messages+=1

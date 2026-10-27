"""Bounded worker-only image settings; no native SFC writes or callback IO."""
from pathlib import Path
import hashlib
import math
import struct
import tomllib
from material_controls import fnv
from rendering_config import DEFAULT,parse,scoped

DEFAULTS=dict(enabled=False,tone_mapping='local',automatic_exposure=True,
              brightness=50,exposure_ev=0.,contrast=1.,gamma=1.,saturation=1.)
NATIVE_DEFAULT=None  # Native [remix] controls now live in the same profile.
REMIX_DEFAULTS={'rtx.bloom.enable':True,'rtx.bloom.steps':5,
                'rtx.bloom.burnIntensity':1.,
                'rtx.bloom.luminanceThreshold':.25}

def encode(raw,native_raw=None):
    if len(raw)>16384:raise ValueError('Image config16KiB limit')
    data=parse(raw)
    row=data.get('image',{})
    if not isinstance(row,dict) or set(row)-set(DEFAULTS):raise ValueError('Unknown image setting')
    v=DEFAULTS|row
    if type(v['enabled']) is not bool or type(v['automatic_exposure']) is not bool:raise ValueError('Image boolean required')
    if v['tone_mapping'] not in ('local','global'):raise ValueError('Image tone_mapping local/global required')
    if type(v['brightness']) is not int or not 0<=v['brightness']<=100:raise ValueError('Image brightness integer0..100')
    def number(key,lo,hi):
        x=v[key]
        if isinstance(x,bool) or not isinstance(x,(int,float)) or not lo<=x<=hi or not math.isfinite(x):raise ValueError('Image value outside documented range: '+key)
        return float(x)
    values=[number('exposure_ev',-4,4),number('contrast',0,2),number('gamma',.25,4),number('saturation',0,2)]
    body=struct.pack('<6I4f',0x31474d49,1,v['enabled'],int(v['tone_mapping']=='local'),v['automatic_exposure'],v['brightness'],*values)
    if native_raw is None and 'remix' in data:native_raw=raw
    if native_raw is not None:
        if len(native_raw)>16384:raise ValueError('Post-processing config16KiB limit')
        data=parse(native_raw)
        native=data.get('remix',{})
        if not isinstance(native,dict) or set(native)-set(REMIX_DEFAULTS):raise ValueError('Unknown native Remix setting')
        native=REMIX_DEFAULTS|native
        if type(native['rtx.bloom.enable']) is not bool:raise ValueError('rtx.bloom.enable requires boolean')
        steps=native['rtx.bloom.steps']
        if type(steps) is not int or not 1<=steps<=8:raise ValueError('rtx.bloom.steps requires integer1..8')
        # Finite representable nonnegative native floats, not invented artistic
        # ranges. Names/values pass directly to SetConfigVariable without mixing.
        floats=[]
        for key in ('rtx.bloom.burnIntensity','rtx.bloom.luminanceThreshold'):
            x=native[key]
            if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or not 0<=x<=3.4028234663852886e38:
                raise ValueError('Native Remix nonnegative finite float required: '+key)
            floats.append(float(x))
        body=struct.pack('<I',0x31474d49)+struct.pack('<I',2)+body[8:]+struct.pack('<2I2f',native['rtx.bloom.enable'],steps,*floats)
    return body+struct.pack('<Q',fnv(body))

def encode_current(raw):
    return encode(raw)

class Relay:
    def __init__(self,folder,path=DEFAULT,native_path=NATIVE_DEFAULT):
        self.folder=Path(folder);self.path=Path(path);self.digest=None
        self.native_path=Path(native_path) if native_path is not None else None
        self.accepted=0;self.rejected=0;self.messages=0;self.last_poll=-1.
    def poll(self):
        import time
        now=time.monotonic()
        if now-self.last_poll<.5:return
        self.last_poll=now
        try:
            if self.path.stat().st_size>16384:raise ValueError('Image config16KiB limit')
            raw=scoped(self.path.read_bytes(),'image','remix');native_raw=None
            if self.native_path is not None:
                if self.native_path.stat().st_size>16384:raise ValueError('Post-processing config16KiB limit')
                native_raw=self.native_path.read_bytes()
            digest=hashlib.sha256(raw+b'\0'+(native_raw or b'')).hexdigest()
            if digest==self.digest:return
            if self.accepted>=256:raise ValueError('Image revision256/session limit;restart to continue')
            packet=encode(raw,native_raw)
            pending=self.folder/'image-controls.pending';pending.write_bytes(packet)
            pending.replace(self.folder/'image-controls.bin')
            self.digest=digest;self.accepted+=1
            (self.folder/'image-config-accepted.toml').write_bytes(raw)
            if native_raw is not None:(self.folder/'post_processing-config-accepted.toml').write_bytes(native_raw)
            if self.accepted<=16:(self.folder/f'image-config-{self.accepted:04d}.toml').write_bytes(raw)
            if self.messages<100:print(f'IMAGE CONFIG_ACCEPTED revision={self.accepted}',flush=True);self.messages+=1
        except (OSError,ValueError) as exc:
            self.rejected+=1
            if self.messages<100:print('IMAGE CONFIG_REJECTED keeping last good: '+str(exc),flush=True);self.messages+=1

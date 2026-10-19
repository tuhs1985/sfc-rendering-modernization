"""Separate bounded quality relay; no image/light/material file writes."""
from pathlib import Path
import math
import struct
import tomllib
from image_controls import Relay as ImageRelay
from material_controls import fnv

DEFAULT=Path(__file__).parent/'config/quality.toml'
DEFAULTS=dict(enabled=False,texture_filtering='anisotropic',max_anisotropy=8,
              mip_bias=0.,anti_aliasing='off',denoising=True,supersampling=1.)

def encode(raw):
    if len(raw)>16384:raise ValueError('Quality config16KiB limit')
    data=tomllib.loads(raw.decode('utf-8'))
    if set(data)-{'quality'}:raise ValueError('Unknown quality section')
    row=data.get('quality',{})
    if not isinstance(row,dict) or set(row)-set(DEFAULTS):raise ValueError('Unknown quality setting')
    v=DEFAULTS|row
    if type(v['enabled']) is not bool or type(v['denoising']) is not bool:raise ValueError('Quality boolean required')
    if v['texture_filtering'] not in ('trilinear','anisotropic'):raise ValueError('Unknown texture filtering')
    if v['anti_aliasing'] not in ('off','temporal'):raise ValueError('AA off/temporal required;not MSAA/DLSS')
    if type(v['max_anisotropy']) is not int or v['max_anisotropy'] not in (1,2,4,8,16):raise ValueError('Anisotropy1/2/4/8/16 required')
    bias=v['mip_bias'];scale=v['supersampling']
    if isinstance(bias,bool) or not isinstance(bias,(float,int)) or not -1<=bias<=1 or not math.isfinite(bias):raise ValueError('Mip bias outside-1..1')
    if isinstance(scale,bool) or not isinstance(scale,(float,int)) or scale!=1:raise ValueError('Supersampling>1not qualified:SDK output copy uses nearest sampling;requires real resolve')
    body=struct.pack('<8I2f',0x31544c51,1,v['enabled'],int(v['texture_filtering']=='anisotropic'),v['max_anisotropy'],3 if v['anti_aliasing']=='temporal' else 0,v['denoising'],0,bias,scale)
    return body+struct.pack('<Q',fnv(body))

class Relay(ImageRelay):
    # Same bounded/atomic last-good behavior; distinct parser,filenames and log tag.
    def __init__(self,folder,path=DEFAULT):super().__init__(folder,path)
    def poll(self):
        import time
        import hashlib
        now=time.monotonic()
        if now-self.last_poll<.5:return
        self.last_poll=now
        try:
            if self.path.stat().st_size>16384:raise ValueError('Quality config16KiB limit')
            raw=self.path.read_bytes();digest=hashlib.sha256(raw).hexdigest()
            if digest==self.digest:return
            if self.accepted>=256:raise ValueError('Quality revision256/session limit')
            packet=encode(raw);pending=self.folder/'quality-controls.pending';pending.write_bytes(packet);pending.replace(self.folder/'quality-controls.bin')
            self.digest=digest;self.accepted+=1
            (self.folder/'quality-config-accepted.toml').write_bytes(raw)
            if self.accepted<=16:(self.folder/f'quality-config-{self.accepted:04d}.toml').write_bytes(raw)
            if self.messages<100:print(f'QUALITY CONFIG_ACCEPTED revision={self.accepted}',flush=True);self.messages+=1
        except (OSError,ValueError) as exc:
            self.rejected+=1
            if self.messages<100:print('QUALITY CONFIG_REJECTED keeping last good: '+str(exc),flush=True);self.messages+=1

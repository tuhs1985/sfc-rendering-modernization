"""Backend-local API sidecar from the accepted material manifest; no image edits."""
import hashlib
import json
import math
from pathlib import Path
import re
import struct

MAGIC=0x314d5041
ROW=struct.Struct('<2IQ80s80s80s')
def checksum(raw):
    value=14695981039346656037
    for byte in raw:value=((value^byte)*1099511628211)&0xffffffffffffffff
    return value

def encode(report,scene,folder):
    folder=Path(folder)
    values=report['values']
    if len(values)!=10 or not all(math.isfinite(x) for x in values):raise ValueError('Material scalars')
    groups=report['groups']
    if not 1<=len(groups)<=256 or len(groups)!=len(scene['groups']):raise ValueError('Material groups')
    raw=struct.pack('<4I10f',MAGIC,1,len(groups),ROW.size,*values)
    for item,group in zip(groups,scene['groups']):
        identity,index,_,_=group
        if (identity,index)!=(item['group'],item['ordinary_texture']):raise ValueError('Group/image identity')
        names=[]
        for role in ('color','emission','roughness'):
            relative=item['images'].get(role,'')
            if not relative:
                if role=='color':raise ValueError('Missing primary image')
                names.append(b'');continue
            if not re.fullmatch(r'textures/[0-9a-f]{64}\.dds',relative):raise ValueError('Unsafe API image path')
            path=folder/'rtx-remix/mods/sfc-policy'/relative
            path.resolve().relative_to(folder.resolve())
            if path.is_symlink() or not path.is_file() or path.stat().st_size>128*1024*1024:raise ValueError('Missing/bounded API image')
            # The filename is already the accepted content hash, not an old resource ID.
            names.append(path.name.encode('ascii'))
        raw+=ROW.pack(identity,index,int(item['remix_hash'],16),*names)
    return raw+struct.pack('<Q',checksum(raw))

def prepare(folder,*,emission_off=False):
    folder=Path(folder)
    report=json.loads((folder/'material-binding.json').read_text())
    if emission_off:
        report=dict(report,values=list(report['values']))
        report['values'][1]=0
    scene=json.loads((folder/'scene.json').read_text())
    raw=encode(report,scene,folder)
    (folder/'api-materials.bin').write_bytes(raw)
    return dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),groups=len(report['groups']),
                material_config_sha256=report['config_sha256'],images_unchanged=True,
                diagnostic_emission_off=emission_off,effective_values=report['values'])

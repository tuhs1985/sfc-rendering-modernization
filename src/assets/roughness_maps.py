"""Bounded worker-only artistic roughness derivatives; not recovered SFC data."""
from pathlib import Path
import hashlib
import io
import json
import re
import struct
import numpy as np
from PIL import Image

LIMIT=128*1024*1024

def collect(folder,keep):
    """Delete ONLY session-generated, unreferenced DDS revisions after host receipt."""
    folder=Path(folder).resolve();directory=folder/'textures'
    if not directory.exists():return 0
    if directory.is_symlink() or directory.resolve().parent!=folder:raise ValueError('Unsafe roughness cache directory')
    removed=0
    for path in directory.iterdir():
        match=re.fullmatch(r'roughness-[0-9a-f]{64}-([0-9a-f]{16})\.(dds|pending)',path.name)
        if not match or int(match[1],16) in keep:continue
        if path.is_symlink() or not path.is_file():raise ValueError('Unsafe roughness cache entry')
        size=path.stat().st_size
        try:path.unlink()
        except OSError:continue # Busy file stays protected by budget; retry later.
        removed+=size
    return removed

def receipt(folder):
    from material_controls import fnv
    try:raw=(Path(folder)/'material-receipt.bin').read_bytes()
    except OSError:return None
    if len(raw)!=40:return None
    magic,version,processed,active,status,reserved,checksum=struct.unpack('<IIQQIIQ',raw)
    if magic!=0x314b414d or version!=1 or status not in (1,2) or reserved or checksum!=fnv(raw[:32]):return None
    if status==1 and active!=processed:return None
    return processed,active,status

def pixels(image,base,strength,black,white,invert,gamma):
    rgb=image.convert('RGB');out=np.empty((image.height,image.width),dtype=np.uint8)
    # Bounded strips avoid multiple full4096-square floating-point images.
    for y in range(0,image.height,128):
        strip=np.asarray(rgb.crop((0,y,image.width,min(y+128,image.height))),dtype=np.float32)/255.0
        level=np.clip((strip@np.array([.2126,.7152,.0722],dtype=np.float32)-black)/(white-black),0,1)
        level=level**(1.0/gamma)
        if invert:level=1-level
        out[y:y+len(level)]=np.floor(np.clip(base*(1-strength)+level*strength,0,1)*255+.5).astype(np.uint8)
    return Image.fromarray(out).convert('RGBA')

def prepare(folder,packet):
    from material_controls import fnv
    if len(packet)!=56:raise ValueError('Roughness material packet size')
    magic,version,*values=struct.unpack('<2I10fQ',packet)
    revision=values.pop()
    if magic!=0x3143544d or version!=2 or revision!=fnv(packet[:48]):raise ValueError('Roughness packet integrity')
    if not values[4]:return
    folder=Path(folder);table=(folder/'live-materials.bin').read_bytes()
    if len(table)<40 or len(table)>2*1024*1024:raise ValueError('Roughness association size')
    h=struct.unpack_from('<8IQ',table)
    if h[0]!=0x31585453 or h[1]!=1 or not 0<h[2]<=256 or h[6]!=len(table)-40 or h[8]!=fnv(table[40:]) or h[2]*80>len(table)-40:
        raise ValueError('Roughness association integrity')
    texture_dir=folder/'textures'
    total=sum(p.stat().st_size for p in texture_dir.iterdir() if p.is_file())
    rows=[]
    for i in range(h[2]):
        _,raw=struct.unpack_from('<Q72s',table,40+i*80)
        if raw[68:]!=bytes(4):raise ValueError('Roughness source padding')
        name=raw[:68].decode('ascii')
        if not re.fullmatch(r'[0-9a-f]{64}\.dds',name):raise ValueError('Roughness source filename')
        source=texture_dir/name
        if source.stat().st_size>LIMIT:raise ValueError('Roughness source byte cap')
        target=texture_dir/f'roughness-{name[:64]}-{revision:016x}.dds'
        with Image.open(source) as image:
            if not 0<image.width<=4096 or not 0<image.height<=4096:raise ValueError('Roughness dimension cap')
            dimensions=list(image.size)
            if not target.exists():
                derived=pixels(image,values[0],values[5],values[6],values[7],bool(values[8]),values[9])
                buffer=io.BytesIO();derived.save(buffer,format='DDS');output=buffer.getvalue()
                if total+len(output)>LIMIT:raise ValueError(f'Generated-image cache budget exceeded (not system RAM): {total+len(output):,} bytes needed; {LIMIT:,} byte limit; current/in-flight images protected; keep last good')
                pending=target.with_suffix('.pending');pending.write_bytes(output);pending.replace(target)
                total+=len(output)
        rows.append(dict(source=name,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
            derived=target.name,derived_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),dimensions=dimensions))
    manifest=dict(version=1,material_revision=f'{revision:016x}',classification='ARTISTIC_APPROXIMATION_NOT_NATIVE_MATERIAL',
        formula='round(255*((1-strength)*roughness+strength*levels(encoded Rec709 luminance)^(1/gamma))); optional inversion after levels/gamma',
        images=rows,total_image_bytes=total,warning=total>=64*1024*1024)
    # Bounded latest provenance; derivatives immutable and session-capped.
    pending=folder/'roughness-manifest.pending';pending.write_text(json.dumps(manifest,indent=2));pending.replace(folder/'roughness-manifest.json')

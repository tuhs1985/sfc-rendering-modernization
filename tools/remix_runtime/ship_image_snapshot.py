"""Decode a one-shot exact prepared BGRA ship layer; no colour/orientation edit."""
from pathlib import Path
import hashlib
import json
import math
import struct
from PIL import Image

HEADER=struct.Struct('<8I4Q2I4f')
KEY=struct.Struct('<8I2Q8I32s6II3f')
MAX_BYTES=256+1920*1080*4

def decode(raw):
    if not 256<=len(raw)<=MAX_BYTES:raise ValueError('Snapshot byte bound')
    h=HEADER.unpack_from(raw);k=KEY.unpack_from(raw,88);error,model,source,lod=struct.unpack_from('<4I',raw,240)
    magic,version,size,status,pid,w,height,fmt,handle,captured,observed,freq,sequence,flags,*rect=h
    if (magic,version,size,status,fmt)!=(0x31495353,1,256,4,87) or error or flags!=1:raise ValueError('Snapshot schema/status')
    if not(0<w<=1920 and 0<height<=1080) or len(raw)!=256+w*height*4:raise ValueError('Snapshot dimensions/length')
    if not pid or not model or not source or not freq or not sequence or not handle or captured<observed or (captured-observed)*1000>100*freq:raise ValueError('Snapshot provenance/age')
    if not all(math.isfinite(x) for x in rect) or not(0<=rect[0]<rect[2]<=1920 and 0<=rect[1]<rect[3]<=1080):raise ValueError('Snapshot display rectangle')
    if k[23]!=pid or k[10:12]!=(w,height) or not all(k[i] for i in (4,5,6,7,8,9)) or k[24] or k[25]!=2 or not any(k[:4]) or not any(k[19:23]) or not any(k[18]):raise ValueError('Snapshot owner/key')
    if rect!=[float(k[12]),float(k[13]),float(k[12]+k[14]),float(k[13]+k[15])] or not all(math.isfinite(x) and abs(x)<=1e6 for x in k[26:29]):raise ValueError('Snapshot viewport/offset')
    meta=dict(schema='sfc.prepared-ship-image.v1',pid=pid,owner_epoch=k[4],revision=k[5],source_frame=k[6],object_id=k[7],
              pose_hash=k[8],camera_hash=k[9],asset_sha256=k[18].hex(),sequence=sequence,model=model,source=source,lod=lod,
              return_session_words=list(k[:4]),semantic_session_words=list(k[19:23]),
              width=w,height=height,source_format='BGRA8_UNORM',display_rect=rect,source_viewport=list(k[12:16]),
              source_observed_qpc=observed,capture_qpc=captured,qpc_frequency=freq,source_request_age_ms=(captured-observed)*1000/freq,
              stage='Exact private prepared ship layer before late ReShade AddImage;not raw pre-mask Remix output or final SFC framebuffer',
              add_image_enqueued=True,uv_display=[0,0,1,1],conversion='Lossless BGRA-to-RGBA channel order only;no flip,resize,gamma or exposure change',
              raw_sha256=hashlib.sha256(raw).hexdigest(),pixels_sha256=hashlib.sha256(raw[256:]).hexdigest())
    meta['nonzero_alpha_pixels']=sum(x!=0 for x in raw[259::4])
    return meta,raw[256:]

def convert(folder):
    folder=Path(folder);path=folder/'prepared-ship-image.sfcimg'
    with path.open('rb') as f:raw=f.read(MAX_BYTES+1)
    meta,pixels=decode(raw);png=folder/'prepared-ship-image.png';sidecar=folder/'prepared-ship-image.json'
    if png.exists() or sidecar.exists():raise ValueError('Refusing snapshot conversion overwrite')
    current=sum(p.stat().st_size for p in folder.rglob('*') if p.is_file() and 'textures' not in p.relative_to(folder).parts)
    if current+len(pixels)+65536>32*1024*1024:raise ValueError('Snapshot PNG would exceed non-image evidence cap')
    image=Image.frombytes('RGBA',(meta['width'],meta['height']),pixels,'raw','BGRA');image.save(png)
    with Image.open(png) as check:
        if check.tobytes()!=image.tobytes():raise ValueError('Snapshot PNG readback mismatch')
    meta['png_sha256']=hashlib.sha256(png.read_bytes()).hexdigest();sidecar.write_text(json.dumps(meta,indent=2));return meta

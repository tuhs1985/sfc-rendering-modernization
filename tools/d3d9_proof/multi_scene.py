"""Version1 bounded tracked-set/catalog wire. Worker-side only; no SFC calls."""
import ctypes as C
import struct
import subprocess
from pathlib import Path
import math
import tomllib
from owner_rebind import fnv

OFFSET=15*1024*1024-128*1024
MAGIC=0x31534d53
OWNERS,ASSETS,FRAMES=32,64,8
FRAME_BYTES,FRAME_SLOT,ASSET_SLOT=12328,12352,128
ASSET_BASE=64+FRAMES*FRAME_SLOT
STORE_BYTES=ASSET_BASE+ASSETS*ASSET_SLOT
ASSET=struct.Struct('<8I32s3Q')
CONFIG=Path(__file__).with_name('multi_ship.toml')


def camera_offset(raw=None):
    raw=CONFIG.read_bytes() if raw is None else raw
    if len(raw)>4096:raise ValueError('Multi-ship placement4KiB cap')
    data=tomllib.loads(raw.decode('utf-8'))
    if set(data)!={'camera_left_distance'}:raise ValueError('Multi-ship placement keys')
    distance=data['camera_left_distance']
    if type(distance) not in (int,float) or not math.isfinite(distance) or not 0<=distance<=1e6:
        raise ValueError('Multi-ship placement distance0..1000000')
    return [-float(distance),0,0]


def initialize(channel):
    words=[int(channel.name[-32:][i:i+8],16) for i in range(0,32,8)]
    channel.write(OFFSET,struct.pack('<16I',MAGIC,1,STORE_BYTES,0,*words,*([0]*8))+bytes(STORE_BYTES-64))


def asset_packet(identity,path_id,row,signature,replay,textures):
    if not 1<=identity<=ASSETS or not 1<=path_id<=ASSETS or any(not row[i] for i in (1,5,6,7)):
        raise ValueError('Multi-scene catalog identity')
    if not 0<len(replay)<=2*1024*1024 or sum(map(len,textures))>128*1024*1024:
        raise ValueError('Multi-scene catalog byte limits')
    content=bytes.fromhex(signature)
    if len(content)!=32 or not any(content):raise ValueError('Multi-scene content identity')
    image_hash=14695981039346656037
    for raw in textures:image_hash=((image_hash^fnv(raw))*1099511628211)&0xffffffffffffffff
    raw=ASSET.pack(identity,path_id,row[1],row[7],row[5],row[6],len(replay),sum(map(len,textures)),content,fnv(replay),image_hash,0)
    return raw[:-8]+struct.pack('<Q',fnv(raw[:-8]))


def publish(channel,identity,raw):
    if len(raw)!=ASSET.size or ASSET.unpack(raw)[0]!=identity or fnv(raw[:-8])!=ASSET.unpack(raw)[-1]:
        raise ValueError('Multi-scene catalog packet/checksum')
    base=OFFSET+ASSET_BASE+(identity-1)*ASSET_SLOT
    if channel.read(base,8)!=bytes(8):raise ValueError('Catalog entries immutable;never overwrite a consumed slot')
    C.c_int32.from_address(channel.view+base).value=1
    channel.write(base+8,raw)
    C.c_int32.from_address(channel.view+base).value=2


def file_packet(identity,path_id,row,signature,folder,image_count):
    if not 1<=identity<=ASSETS or not 1<=path_id<=ASSETS or any(not row[i] for i in (1,5,6,7)):
        raise ValueError('Multi-scene catalog identity')
    folder=Path(folder).resolve();root=Path(__file__).resolve().parents[2]
    folder.relative_to(root/'artifacts')
    content=bytes.fromhex(signature)
    if len(content)!=32 or not any(content) or not 1<=image_count<=256:raise ValueError('Multi-scene content/image count')
    helper=root/'artifacts/d3d9-proof/multiship-tests/asset_hash.exe'
    result=subprocess.run([str(helper),str(folder),str(image_count)],capture_output=True,text=True,timeout=10,check=True,
                          creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    fields=[int(x) for x in result.stdout.split()]
    if len(fields)!=4:raise ValueError('Native hash receipt layout')
    geometry,images,replay_hash,image_hash=fields
    if not 0<geometry<=2*1024*1024 or not 0<images<=128*1024*1024 or not replay_hash or not image_hash:
        raise ValueError('Native hash byte bounds')
    raw=ASSET.pack(identity,path_id,row[1],row[7],row[5],row[6],geometry,images,content,replay_hash,image_hash,0)
    return raw[:-8]+struct.pack('<Q',fnv(raw[:-8]))


def acknowledgement(channel,identity):
    return struct.unpack('<i',channel.read(OFFSET+ASSET_BASE+(identity-1)*ASSET_SLOT+4,4))[0]


def summary(channel):
    h=struct.unpack('<16I',channel.read(OFFSET,64))
    if h[:3]!=(MAGIC,1,STORE_BYTES):raise ValueError('Multi-scene final layout')
    return dict(pid=h[3],stopped=bool(h[8]),last_frame=h[9],published=h[10],dropped=h[11],invalid=h[12],
                asset_ready=h[13],asset_rejected=h[14],closed_frame=h[15])


def frame_snapshot(channel,minimum=0):
    frame=struct.unpack('<I',channel.read(OFFSET+36,4))[0]
    if not frame or frame<minimum:return None
    base=OFFSET+64+(frame%FRAMES)*FRAME_SLOT
    guard=channel.read(base,4)
    if not struct.unpack('<I',guard)[0] or struct.unpack('<I',guard)[0]&1:return None
    raw=channel.read(base+8,FRAME_BYTES)
    if channel.read(base,4)!=guard:return None
    sequence,offered,number,anchor,revision,count=struct.unpack_from('<QQ4I',raw)
    if not sequence or not offered or number!=frame or not anchor or not revision or not 1<=count<=OWNERS:
        return None
    if fnv(raw[:-8])!=struct.unpack_from('<Q',raw,FRAME_BYTES-8)[0]:return None
    identities=tuple(struct.unpack_from('<96I',raw,32+i*384)[j] for i in range(count) for j in (1,5,6,7))
    return frame,identities,raw

"""Remix environment preparation metadata;published once before host launch.

Uses spare metadata space in the existing current-user scene mapping. No game
attachment, asset identity or rendering callback is needed to prepare a dome.
"""
import hashlib
import os
from pathlib import Path
import struct
import tomllib
import uuid

ROOT=Path(__file__).resolve().parents[2]
import sys
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
from runtime_context import CONTEXT
CACHE=CONTEXT.artifact('d3d9-proof/environment-cache')
OFFSET=8192
PACKET=struct.Struct('<10I32s1024s808sQ')
STORE_BYTES=8+PACKET.size
LIMIT=128*1024*1024
assert STORE_BYTES==1920 and OFFSET+STORE_BYTES<32768

def cache_image(source,cache=CACHE):
    source=Path(source);cache=Path(cache)
    if source.is_symlink() or source.stat().st_size>LIMIT:raise ValueError('Environment source bound/link')
    raw=source.read_bytes();digest=hashlib.sha256(raw).hexdigest()
    if source.name!=digest+'.dds':raise ValueError('Environment content identity')
    cache.mkdir(parents=True,exist_ok=True)
    if cache.is_symlink():raise ValueError('Environment cache link')
    target=cache/source.name
    if target.exists():
        if target.is_symlink() or target.stat().st_size!=len(raw) or hashlib.sha256(target.read_bytes()).hexdigest()!=digest:
            raise ValueError('Environment cache content mismatch;not overwritten')
        return target
    files=list(cache.glob('*.dds'))
    if len(files)>=256 or sum(p.stat().st_size for p in files)+len(raw)>LIMIT:raise ValueError('Environment cache128MiB/256resource bound')
    temporary=cache/(source.name+'.'+uuid.uuid4().hex+'.pending')
    try:
        temporary.write_bytes(raw)
        try:temporary.rename(target) # Windows exclusive atomic publication;never replace a resident file.
        except FileExistsError:
            if target.read_bytes()!=raw:raise ValueError('Concurrent environment cache content mismatch')
    finally:
        if temporary.exists():temporary.unlink()
    return target

def encode(session,pid,producer,config,shapes,cache):
    import re
    from owner_rebind import fnv
    if not re.fullmatch(r'Local\\SFCBridge_[0-9a-f]{32}',session) or not 0<pid<=0xffffffff or not 0<producer<=0xffffffff:
        raise ValueError('Prepared environment session/process')
    if not config or len(config)>65536 or len(shapes)!=808:raise ValueError('Prepared environment config/shape bounds')
    if struct.unpack_from('<4I',shapes)!=(0x50414853,2,808,3) or struct.unpack_from('<Q',shapes,16)[0]!=1 or fnv(shapes[:-8])!=struct.unpack_from('<Q',shapes,800)[0]:
        raise ValueError('Prepared environment shape integrity')
    cache=Path(cache).resolve();text=str(cache)
    if not cache.is_absolute() or '\x00' in text or len(text.encode('utf-16-le'))>1022:raise ValueError('Environment cache path bound')
    words=[int(session[-32:][i:i+8],16) for i in range(0,32,8)]
    slot,kind,ship,enabled=struct.unpack_from('<4I',shapes,32+2*256)
    if slot!=2:raise ValueError('Prepared environment project slot')
    flags=int(kind==1 and enabled==1)
    raw=PACKET.pack(0x31564e45,1,PACKET.size,pid,*words,producer,flags,
        hashlib.sha256(config).digest(),text.encode('utf-16-le').ljust(1024,b'\0'),shapes,0)
    return raw[:-8]+struct.pack('<Q',fnv(raw[:-8]))

def publish(channel,pid,folder,config_path=None,cache=None):
    from light_controls import validate
    from live_lights import REGISTRY
    from light_shapes import build
    config_path=Path(config_path or CONTEXT.setting('lights.toml'))
    cache=Path(cache or CACHE).resolve();folder=Path(folder)
    if channel.read(OFFSET,STORE_BYTES)!=bytes(STORE_BYTES):raise ValueError('Prepared environment already published')
    raw=config_path.read_bytes()
    if len(raw)>65536:raise ValueError('Light config64KiB cap')
    controls={row['id']:row for row in validate(tomllib.loads(raw.decode('utf-8')),REGISTRY)}
    shapes,manifest=build(controls,1,folder,config_path.parent)
    cache.mkdir(parents=True,exist_ok=True)
    for row in manifest:
        if row['prepared_environment']:cache_image(folder/'textures'/row['prepared_environment'],cache)
    packet=encode(channel.name,pid,os.getpid(),raw,shapes,cache)
    channel.write(OFFSET+8,packet)
    channel.write(OFFSET,struct.pack('<I',1)) # Single immutable producer;aligned release on supported Windows.
    return dict(version=1,offset=OFFSET,bytes=STORE_BYTES,config_sha256=hashlib.sha256(raw).hexdigest(),
        cache=str(cache),project_dome_prepared=bool(PACKET.unpack(packet)[9]),
        scope='Configured project dome only;native observations and asset activation remain separate')

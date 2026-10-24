"""Bounded session request for an offline public-API texture-cache experiment."""
import json
from pathlib import Path
import re
import struct
from owner_rebind import fnv

HEADER=struct.Struct('<8I')
CAPACITY=1024
STRIDE=256
PATTERN=r'assets/[1-9][0-9]*/rtx-remix/mods/sfc-policy/textures/[0-9a-f]{64}\.dds'


def packet(gpu,layers,pid,session):
    gpu=Path(gpu).resolve();root=gpu/'rtx-remix/mods/sfc-policy'
    if not re.fullmatch(r'Local\\SFCBridge_[0-9a-f]{32}',session) or not 0<pid<=0xffffffff:
        raise ValueError('Prefetch session/process')
    if not 1<=len(layers)<=64:raise ValueError('Prefetch layer bound')
    paths=set()
    for layer in layers:
        stage=(root/layer).resolve();stage.relative_to(gpu)
        report=stage.parents[3]/'material-binding.json'
        if report.stat().st_size>1024*1024:raise ValueError('Prefetch manifest bound')
        for name in json.loads(report.read_text())['images']:
            target=(stage.parent/name).resolve();path=target.relative_to(gpu).as_posix()
            if not re.fullmatch(PATTERN,path) or not target.is_file():raise ValueError('Prefetch generated image path')
            paths.add(path)
    if not 1<=len(paths)<=CAPACITY:raise ValueError('Prefetch texture count')
    words=[int(session[-32:][i:i+8],16) for i in range(0,32,8)]
    data=HEADER.pack(0x31504654,1,pid,len(paths),*words)
    for path in sorted(paths):
        raw=path.encode('ascii')
        if len(raw)>=STRIDE:raise ValueError('Prefetch path length')
        data+=raw+b'\0'*(STRIDE-len(raw))
    return data+struct.pack('<Q',fnv(data))

"""Bounded one-frame presentation evidence;not motion prediction or stale hold."""
import hashlib
import struct
from pathlib import Path

OFFSET=11*1024*1024+128*1024+4096
CAPACITY=8192
HEADER=struct.Struct('<16I')
RECORD=struct.Struct('<8I5Q')
STORE_BYTES=HEADER.size+CAPACITY*RECORD.size
MAGIC=0x31424653

def decode(raw,session,pid):
    if not HEADER.size<=len(raw)<=STORE_BYTES:raise ValueError('Buffered audit byte cap')
    h=HEADER.unpack_from(raw);words=tuple(int(session[-32:][i:i+8],16) for i in range(0,32,8))
    if h[:4]!=(MAGIC,1,STORE_BYTES,pid) or h[4:8]!=words or h[8]>CAPACITY or any(h[12:]) or len(raw)!=HEADER.size+h[8]*RECORD.size:
        raise ValueError('Buffered audit session/process/layout')
    counts={str(n):0 for n in (1,2,3,4)};owners={};instances={};last=0;observed_max=0
    for r in RECORD.iter_unpack(raw[HEADER.size:]):
        current,scene,output,status,owner,revision,age,reserved,sequence,returned,expected_hash,returned_hash,qpc=r
        if not current or not qpc or qpc<last or reserved or status not in (1,2,3,4):raise ValueError('Buffered audit malformed')
        last=qpc;counts[str(status)]+=1
        observed_max=max(observed_max,age)
        if status in (1,2):
            if not scene or scene+1!=current or not owner or not revision or not sequence or not expected_hash or not 0<=age<=50000:raise ValueError('Buffered scene not adjacent/bounded')
        if status==1:
            if output!=scene or returned!=sequence or returned_hash!=expected_hash:raise ValueError('Buffered mixed-frame image')
            owners[str(owner)]=owners.get(str(owner),0)+1
            key=f'{owner}:{revision}';instances[key]=instances.get(key,0)+1
        elif output or returned or returned_hash:raise ValueError('False buffered output provenance')
    if h[10]!=observed_max:raise ValueError('Buffered age counter mismatch')
    return dict(probe='D3D9-SYNC-BUFFER-001',records=h[8],dropped=h[9],max_age_us=h[10],failed=h[11],statuses=counts,
        paired=counts['1'],without_ship=counts['2'],warmup=counts['3'],reset=counts['4'],owners=owners,instances=instances,
        sha256=hashlib.sha256(raw).hexdigest(),scope='Complete pre-effects game frame including native HUD and matching ship/depth delayed together by one adjacent game frame;not physical input latency')

def save(channel,folder,pid):
    head=channel.read(OFFSET,HEADER.size);h=HEADER.unpack(head)
    if h[8]>CAPACITY:raise ValueError('Buffered audit record cap')
    raw=channel.read(OFFSET,HEADER.size+h[8]*RECORD.size)
    if channel.read(OFFSET,HEADER.size)!=head:raise ValueError('Buffered audit still changing')
    report=decode(raw,channel.name,pid);(Path(folder)/'D3D9-SYNC-BUFFER-001.bin').write_bytes(raw);return report

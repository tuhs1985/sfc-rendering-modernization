"""Fresh content qualification and bounded worker-control mailbox, no asset rebuild."""
import ctypes as C
import struct

from asset_content import Content

OFFSET=11*1024*1024+112*1024
TARGET=struct.Struct('<6I2Q')
MAGIC=0x3142524f


def fnv(raw):
    value=14695981039346656037
    for byte in raw:value=((value^byte)*1099511628211)&0xffffffffffffffff
    return value


def initialize(channel,pid):
    words=[int(channel.name[-32:][i:i+8],16) for i in range(0,32,8)]
    channel.write(OFFSET,struct.pack('<8I',MAGIC,1,128,*words,pid)+bytes(96))


def request(channel,generation,row,cookie):
    if not 1<=generation<=0x3fffffff or not all(row[i] for i in (1,5,6,7)) or row[4]!=1 or not cookie:
        raise ValueError('Invalid rebind request')
    raw=TARGET.pack(generation,row[1],row[7],row[5],row[6],0,cookie,0)
    raw=raw[:-8]+struct.pack('<Q',fnv(raw[:-8]))
    # One Python producer, aligned stores; worker snapshots with acquire barriers.
    C.c_int32.from_address(channel.view+OFFSET+32).value=generation*2-1
    channel.write(OFFSET+64,raw)
    C.c_int32.from_address(channel.view+OFFSET+32).value=generation*2


def acknowledged(channel):return struct.unpack('<I',channel.read(OFFSET+104,4))[0]




def choose(candidates,selected_model,content,expected):
    # Unique known fixture only; ambiguity never silently picks an identical enemy.
    matches=[(r,m) for r,m in candidates if m['refs']['model_filename'].replace('\\','/').lower()==selected_model]
    if len(matches)!=1:return None
    row,mesh=matches[0]
    return (row,mesh) if content.signature(mesh)==expected else None

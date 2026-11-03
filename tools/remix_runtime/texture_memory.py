"""Immutable, current-user texture delivery. No renderer-side texture-file opens.

Mappings stay owned until catalog acknowledgement; the consumer owns its copied
upload vectors afterwards. Capacity pressure postpones preparation, never SFC.
"""
import ctypes as C
import re
import struct
from live_bridge import Channel
from scene_capacity import ASSETS

HEADER=2176
LIMIT=128*1024*1024
BUDGET=256*1024*1024+4*HEADER
ASSET=struct.Struct('<8I32s3Q')


def name(session,identity):
    if not re.fullmatch(r'Local\\SFCBridge_[a-f0-9]{32}',session) or not 1<=identity<=ASSETS:
        raise ValueError('Texture session/asset identity')
    words=[int(session[-32:][i:i+8],16) for i in range(0,32,8)]
    words[0]^=0x54585431;words[3]^=identity
    return 'Local\\SFCTextures_'+''.join(f'{w:08x}' for w in words)


class Mapping(Channel):
    version=2
    name_pattern=re.compile(r'Local\\SFCTextures_[a-f0-9]{32}\Z')


class Pool:
    def __init__(self,session):
        self.session=session;self.entries={};self.bytes=0;self.peak=0;self.created=0;self.acknowledged=0;self.closed=False

    def reserve(self,identity,lengths,geometry_bytes=0):
        if self.closed:raise ValueError('Texture pool closed')
        if identity in self.entries:return True
        if not 1<=len(lengths)<=256 or any(not 16<n<=64*1024*1024+16 for n in lengths) or sum(lengths)>LIMIT:
            raise ValueError('Texture payload bounds')
        if not 0<geometry_bytes<=2*1024*1024:raise ValueError('Geometry payload bounds')
        size=HEADER+geometry_bytes+sum(lengths)
        if self.bytes+size>BUDGET:return False
        mapping=Mapping.__new__(Mapping);mapping.size=size
        Mapping.__init__(mapping,name(self.session,identity),create=True)
        offset=HEADER+geometry_bytes;table=[]
        for length in lengths:table.append((offset,length));offset+=length
        mapping.write(128,b''.join(struct.pack('<2I',*v) for v in table))
        self.entries[identity]=dict(mapping=mapping,table=table,written=set(),sealed=False,geometry_bytes=geometry_bytes,geometry_written=False)
        self.bytes+=size;self.peak=max(self.peak,self.bytes)
        self.created+=1
        return True

    def write(self,identity,index,payload):
        entry=self.entries[identity]
        if entry['sealed'] or not 0<=index<len(entry['table']) or index in entry['written']:raise ValueError('Immutable texture slot')
        offset,length=entry['table'][index]
        if len(payload)!=length:raise ValueError('Texture length changed')
        entry['mapping'].write(offset,payload);entry['written'].add(index)

    def write_geometry(self,identity,payload):
        entry=self.entries[identity]
        if entry['sealed'] or entry['geometry_written'] or len(payload)!=entry['geometry_bytes']:raise ValueError('Immutable geometry slot/length')
        entry['mapping'].write(HEADER,payload);entry['geometry_written']=True

    def seal(self,identity,packet):
        entry=self.entries[identity]
        if entry['sealed'] or not entry['geometry_written'] or len(entry['written'])!=len(entry['table']) or len(packet)!=ASSET.size or ASSET.unpack(packet)[0]!=identity or ASSET.unpack(packet)[6]!=entry['geometry_bytes']:
            raise ValueError('Incomplete texture publication')
        entry['mapping'].write(32,packet)
        entry['mapping'].write(120,struct.pack('<I',len(entry['table'])))
        C.c_int32.from_address(entry['mapping'].view+124).value=1
        entry['sealed']=True

    def release(self,identity):
        entry=self.entries.pop(identity,None)
        if entry:self.bytes-=entry['mapping'].size;entry['mapping'].close()

    def reclaim(self,channel):
        from multi_scene import acknowledgement
        for identity,entry in list(self.entries.items()):
            if entry['sealed'] and acknowledgement(channel,identity):self.acknowledged+=1;self.release(identity)

    def close(self):
        self.closed=True
        for identity in list(self.entries):self.release(identity)

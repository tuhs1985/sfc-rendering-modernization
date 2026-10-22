"""Fresh content qualification and bounded worker-control mailbox, no asset rebuild."""
import ctypes as C
import hashlib
import json
from pathlib import Path
import struct

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
    if not 1<=generation<=64 or not all(row[i] for i in (1,5,6,7)) or row[4]!=1 or not cookie:
        raise ValueError('Invalid rebind request')
    raw=TARGET.pack(generation,row[1],row[7],row[5],row[6],0,cookie,0)
    raw=raw[:-8]+struct.pack('<Q',fnv(raw[:-8]))
    # One Python producer, aligned stores; worker snapshots with acquire barriers.
    C.c_int32.from_address(channel.view+OFFSET+32).value=generation*2-1
    channel.write(OFFSET+64,raw)
    C.c_int32.from_address(channel.view+OFFSET+32).value=generation*2


def acknowledged(channel):return struct.unpack('<I',channel.read(OFFSET+104,4))[0]


class Content:
    def __init__(self,root):self.root=Path(root).resolve();self.images={};self.signatures={}

    def image(self,filename):
        from scene_bundle import resolve_image
        path=resolve_image(self.root,filename);stat=path.stat()
        stamp=(stat.st_size,stat.st_mtime_ns,stat.st_ctime_ns,stat.st_ino)
        cached=self.images.get(path)
        if not cached or cached[0]!=stamp:
            cached=(stamp,hashlib.sha256(path.read_bytes()).hexdigest());self.images[path]=cached
        return cached[1]

    def signature(self,mesh):
        cached=self.signatures.get(mesh.get('packet_sha256'))
        if cached:return cached
        refs=mesh['refs'];resources={r['id']:r for r in refs['resources']}
        groups=[]
        for g in mesh['groups']:
            images=[]
            for key in ('primary','secondary'):
                if key=='secondary' and not g[key]:images.append(None);continue
                resource=resources.get(g[key])
                if not resource:raise ValueError('Unresolved rebind image')
                images.append(self.image(resource['filename']))
            groups.append([g['group'],g['flags'],*images])
        # Captured geometry+LOD+group image CONTENT, not resource IDs or pointers.
        value=[mesh['geometry_sha256'],list(mesh['header'][20:23]),groups,refs.get('secondary_role')]
        result=hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        if mesh.get('packet_sha256'):self.signatures[mesh['packet_sha256']]=result
        return result


def choose(candidates,selected_model,content,expected):
    # Unique known fixture only; ambiguity never silently picks an identical enemy.
    matches=[(r,m) for r,m in candidates if m['refs']['model_filename'].replace('\\','/').lower()==selected_model]
    if len(matches)!=1:return None
    row,mesh=matches[0]
    return (row,mesh) if content.signature(mesh)==expected else None

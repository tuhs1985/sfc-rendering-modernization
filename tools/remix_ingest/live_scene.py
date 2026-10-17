"""Protocol3 fresh scene transport/validation. No template import or native dereference."""
import ctypes
import hashlib
import io
import json
import math
from pathlib import Path
import struct
import time
from live_bridge import Channel, affine

SIZE=16*1024*1024
STRIDE=2*1024*1024
DATA=65536
OWNERS=32
ASSETS=64
IMAGE_LIMIT=128*1024*1024
MEMORY_LIMIT=256*1024*1024


class SceneChannel(Channel):
    size=SIZE
    version=3
    receiver_write=True  # explicit current-user-only acknowledgements

    def sample_owner(self,index):
        if not 0<=index<32:raise ValueError('Owner index')
        offset=4096+index*512
        guard=self.read(offset,4);value=struct.unpack('<I',guard)[0]
        if not value or value&1:return None
        row=struct.unpack('<96I',self.read(offset+4,384))
        return row if self.read(offset,4)==guard and row[45]==index else None

    def asset_transfer(self,index):
        if not 0<=index<4:raise ValueError('Transfer slot')
        offset=256+index*64
        desc=self.read(offset,24);generation,ack,nmesh,nrefs,owner,revision=struct.unpack('<6I',desc)
        if not generation or generation==ack:return None
        if generation<ack or not 256<=nmesh<STRIDE or not 1<=nrefs<=256*1024 or nmesh+nrefs>STRIDE or not 1<=revision<=64 or not owner:
            raise ValueError('Transfer bounds/generation')
        payload=self.read(DATA+index*STRIDE,nmesh+nrefs)
        if self.read(offset,24)!=desc:return None
        return generation,revision,owner,payload[:nmesh],payload[nmesh:]

    def acknowledge(self,index,generation):
        if not 0<=index<4 or struct.unpack('<I',self.read(256+index*64,4))[0]!=generation:
            raise ValueError('Stale acknowledgement')
        # Aligned release store on Windows/x86, only after payload is consumed.
        ctypes.c_uint32.from_address(self.view+260+index*64).value=generation


def decode_mesh(packet,references):
    if not 256<=len(packet)<=STRIDE or len(references)>256*1024:raise ValueError('Packet byte bound')
    h=struct.unpack_from('<64I',packet);nv,np,nc,ng=h[16:20]
    if h[:2]!=(0x314d4653,1) or h[2]!=len(packet):raise ValueError('Mesh header')
    if not h[4] or h[13]!=0x0042E55D or any(h[24:27]):raise ValueError('Unsupported semantic origin/math dispatch')
    if not(1<=nv<=65536 and 1<=np<=8192 and np*3==nc<=32768 and 1<=ng<=256):raise ValueError('Mesh count/triangles')
    if len(packet)!=256+nv*12+np*36+nc*28+ng*40:raise ValueError('Mesh length')
    value=2166136261
    for i,byte in enumerate(packet):value=((value^(0 if 12<=i<16 else byte))*16777619)&0xffffffff
    if value!=h[3]:raise ValueError('Mesh checksum')
    points=[struct.unpack_from('<3f',packet,256+i*12) for i in range(nv)]
    if not all(math.isfinite(x) for p in points for x in p):raise ValueError('Nonfinite positions')
    poly_offset=256+nv*12;corner_offset=poly_offset+np*36;source_offset=corner_offset+nc*28
    groups=[]
    for i in range(ng):
        s=struct.unpack_from('<10I',packet,source_offset+i*40)
        groups.append(dict(group=s[0],flags=s[1],primary=s[6],secondary=s[8],primary_name_offset=s[7],secondary_name_offset=s[9]))
    if len({g['group'] for g in groups})!=ng:raise ValueError('Duplicate groups')
    bygroup={g['group']:g for g in groups};polys=[];used=[]
    for i in range(np):
        p=struct.unpack_from('<9I',packet,poly_offset+i*36)
        if p[0]!=3 or p[1] not in bygroup or p[6]!=i*3:raise ValueError('Polygon bounds/order')
        if not all(math.isfinite(x) for x in struct.unpack('<3f',struct.pack('<3I',*p[2:5]))):raise ValueError('Nonfinite face')
        polys.append((p[1],p[6]))
    corners=[]
    for i in range(nc):
        raw=struct.unpack_from('<7I',packet,corner_offset+i*28);index=raw[0]&65535
        normal=struct.unpack('<3f',struct.pack('<3I',*raw[1:4]));uv=struct.unpack('<2f',struct.pack('<2I',*raw[4:6]))
        if index>=nv or not all(math.isfinite(x) for x in (*normal,*uv)):raise ValueError('Corner bounds/finite')
        corners.append((index,normal,uv));used.append(index)
    refs=json.loads(references)
    if (refs.get('status')!=1 or refs.get('packet_fnv1a')!=h[3] or refs.get('owner_epoch')!=h[4] or
        refs.get('model')!=h[10] or refs.get('source')!=h[12] or refs.get('frame')!=h[6] or refs.get('groups')!=groups):
        raise ValueError('Same-epoch resource associations')
    resources=refs.get('resources',[])
    if len(resources)>256 or len({r['id'] for r in resources})!=len(resources):raise ValueError('Resource bounds')
    # Hash only portable rendered content, never native labels/transforms/resource IDs.
    content=bytearray(packet[256:poly_offset])
    for i,(group,start) in enumerate(polys):
        p=struct.unpack_from('<9I',packet,poly_offset+i*36);content+=struct.pack('<6I',*p[:5],start)
    for index,n,uv in corners:content+=struct.pack('<I5f',index,*n,*uv)
    return dict(header=h,points=points,corners=corners,polygons=polys,groups=groups,refs=refs,
        used_points=[points[used[i]] for i in (0,len(used)//2,len(used)-1)],
        geometry_sha256=hashlib.sha256(content).hexdigest(),packet_sha256=hashlib.sha256(packet).hexdigest(),
        memory_bytes=nv*160+nc*256+np*80+ng*2048)


class ImageStore:
    """Worker-only immutable original+PNG copies with decoded/mipmap accounting."""
    def __init__(self,game_root,output):
        self.root=Path(game_root).resolve();self.output=Path(output);self.output.mkdir(exist_ok=True)
        self.images={};self.bytes=0;self.memory=0

    def load(self,filename):
        from PIL import Image
        name=filename.replace('\\','/');candidate=self.root/name;path=candidate.resolve()
        if not name or not path.is_relative_to(self.root) or any(p.is_symlink() for p in [candidate,*candidate.parents] if p!=self.root):raise ValueError('Unsafe image path')
        if not path.is_file() or path.stat().st_size>16*1024*1024:raise ValueError('Image file bound')
        raw=path.read_bytes();digest=hashlib.sha256(raw).hexdigest()
        if digest in self.images:return self.images[digest]
        if len(self.images)>=256:raise ValueError('Unique image cap')
        with Image.open(io.BytesIO(raw)) as image:
            if not 1<=image.width<=4096 or not 1<=image.height<=4096:raise ValueError('Image dimension bound')
            image.load();rgba=image.convert('RGBA');encoded=io.BytesIO();rgba.save(encoded,format='PNG');png=encoded.getvalue()
            encoded=io.BytesIO();rgba.save(encoded,format='DDS');dds=encoded.getvalue()
            memory=rgba.width*rgba.height*4*2  # decoded+GPU/mips conservative reservation
            if self.bytes+len(raw)+len(png)+len(dds)>IMAGE_LIMIT or self.memory+memory>MEMORY_LIMIT:raise ValueError('Image output/memory cap')
            with Image.open(io.BytesIO(png)) as check:
                if check.convert('RGBA').tobytes()!=rgba.tobytes():raise ValueError('PNG pixel mismatch')
            with Image.open(io.BytesIO(dds)) as check:
                if check.convert('RGBA').tobytes()!=rgba.tobytes():raise ValueError('DDS pixel mismatch')
            row=dict(sha256=digest,filename=name,format=image.format,width=image.width,height=image.height,
                alpha=rgba.getextrema()[3]!=(255,255),png=(self.output/(digest+'.png')).as_posix(),
                png_sha256=hashlib.sha256(png).hexdigest(),dds=(self.output/(digest+'.dds')).as_posix(),
                dds_sha256=hashlib.sha256(dds).hexdigest(),memory_bytes=memory)
        (self.output/(digest+'.original')).write_bytes(raw);Path(row['png']).write_bytes(png)
        Path(row['dds']).write_bytes(dds)
        self.bytes+=len(raw)+len(png)+len(dds);self.memory+=memory;self.images[digest]=row;return row


def qualify_mesh(packet,refs,images):
    data=decode_mesh(packet,refs);resources={r['id']:r for r in data['refs']['resources']};assignments=[];issues=[]
    for group in data['groups']:
        row=dict(group=group['group'],flags=group['flags'],primary=None,secondary=None)
        if data['refs'].get('textures_enabled')!=1:raise ValueError('Texture-disabled path not qualified')
        if group['flags']&1:
            if not group['primary'] or group['primary'] not in resources:raise ValueError('Unresolved primary image')
            row['primary']=images.load(resources[group['primary']]['filename'])
            if row['primary']['alpha']:issues.append(f"group {group['group']}: alpha image retained, native blend/alpha-test mapping unqualified")
        else:issues.append(f"group {group['group']}: untextured flag path not visually qualified")
        if group['flags']&0x20 and group['secondary']:
            if group['secondary'] not in resources:raise ValueError('Unresolved secondary association')
            row['secondary']=images.load(resources[group['secondary']]['filename'])
            issues.append(f"group {group['group']}: secondary role not applied; primary-only provisional material")
        assignments.append(row)
    identity=dict(geometry=data['geometry_sha256'],groups=[(x['group'],x['flags'],
        x['primary']['sha256'] if x['primary'] else None,x['secondary']['sha256'] if x['secondary'] else None) for x in assignments])
    data.update(assignments=assignments,issues=issues,asset_sha256=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest())
    return data


class SceneConsumer:
    def __init__(self):self.last={};self.retired=set();self.origin=None;self.seen={};self.revisions={};self.owners={};self.rejected=0
    def update(self,r,assets,now=None):
        now=time.monotonic() if now is None else now
        if r is None:return None
        if len(r)!=96 or not all(type(x)is int and 0<=x<=0xffffffff for x in r):self.rejected+=1;return None
        slot,owner=r[45],r[1]
        if not 0<=slot<32 or not owner:self.rejected+=1;return None
        if r[0]<=self.last.get(slot,0):return None
        self.last[slot]=r[0]
        key=(slot,owner)
        previous=self.owners.get(slot)
        if previous is not None and previous!=owner:
            if owner<previous:self.rejected+=1;return None
            self.retired.add((slot,previous));self.seen.pop(slot,None)
        self.owners[slot]=owner
        if r[4]==2:self.retired.add(key);self.seen.pop(slot,None);return None
        asset=assets.get(r[7])
        if (r[4]!=1 or key in self.retired or not asset or asset['header'][4]!=owner or
            tuple(asset['header'][i] for i in (10,12))!=(r[5],r[6]) or r[7]<self.revisions.get(slot,0) or any(r[42:45])):
            self.seen.pop(slot,None);self.rejected+=1;return None
        try:matrix,t=affine(r[8:25],self.origin)
        except ValueError:self.seen.pop(slot,None);self.rejected+=1;return None
        if self.origin is None:self.origin=t
        self.revisions[slot]=r[7];self.seen[slot]=(owner,now);return matrix
    def fresh(self,slot,now=None):
        now=time.monotonic() if now is None else now
        return slot in self.seen and now-self.seen[slot][1]<1

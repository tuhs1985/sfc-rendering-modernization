"""Development template comparison and preview consumer."""
import hashlib
import json
from pathlib import Path
import struct
import time

from live_bridge import STRIDE, affine


def mesh_content(data):
    """Compare all used geometry/UV/normal/group bits, excluding native pointers/IDs."""
    if len(data)<256 or len(data)>STRIDE:raise ValueError('Mesh bounds')
    h=struct.unpack_from('<64I',data)
    nv,np,nc,ns=h[16:20]
    if h[:2]!=(0x314d4653,1) or (nv,np,nc,ns)!=(254,452,1356,5):raise ValueError('Unsupported mesh')
    if len(data)!=h[2] or len(data)!=256+nv*12+np*36+nc*28+ns*40:raise ValueError('Incomplete mesh')
    check=bytearray(data);check[12:16]=b'\0'*4
    value=2166136261
    for byte in check:value=((value^byte)*16777619)&0xffffffff
    if value!=h[3]:raise ValueError('Mesh checksum')
    content=bytearray(data[256:256+nv*12]);polys=256+nv*12;corners=polys+np*36
    for i in range(np):
        row=struct.unpack_from('<9I',data,polys+i*36)
        if row[0]!=3 or row[1]>=5 or row[6]+3>nc:raise ValueError('Polygon bounds')
        content+=struct.pack('<6I',*row[:5],row[6])
    for i in range(nc):
        row=struct.unpack_from('<7I',data,corners+i*28)
        if row[0]&65535>=nv:raise ValueError('Vertex bounds')
        content+=struct.pack('<6I',row[0]&65535,*row[1:6])
    return hashlib.sha256(content).hexdigest(),h


def qualify(packet, references, template_capture, game_root):
    signature,h=mesh_content(packet)
    template_capture=Path(template_capture)
    expected,_=mesh_content((template_capture/'MESH-EXPORT-001.bin').read_bytes())
    refs=json.loads(references)
    if (signature!=expected or refs.get('status')!=1 or refs.get('packet_fnv1a')!=h[3]
        or refs.get('owner_epoch')!=h[4] or refs.get('model')!=h[10] or refs.get('source')!=h[12]
        or refs.get('frame')!=h[6] or refs.get('textures_enabled')!=1
        or refs.get('model_filename','').replace('\\','/').lower()!='assets/models/kff/kff.mod'):
        raise ValueError('Asset content or same-epoch identity mismatch')
    source_offset=256+h[16]*12+h[17]*36+h[18]*28
    actual=[]
    for i in range(h[19]):
        s=struct.unpack_from('<10I',packet,source_offset+i*40)
        actual.append({'group':s[0],'flags':s[1],'primary':s[6],'secondary':s[8],
                       'primary_name_offset':s[7],'secondary_name_offset':s[9]})
    if refs.get('groups')!=actual:raise ValueError('Packet/reference group mismatch')
    manifest=json.loads((template_capture/'textured/association-manifest.json').read_text())
    if len(refs.get('groups',[]))!=5 or len(refs.get('resources',[]))!=10:raise ValueError('Five pairs required')
    current={r['id']:r for r in refs['resources']};old={r['id']:r for r in manifest['images']}
    if len(current)!=10:raise ValueError('Duplicate resources')
    root=Path(game_root).resolve();total=0
    for g,t in zip(refs['groups'],manifest['groups']):
        if g['group']!=t['group'] or g['flags']!=t['flags']:raise ValueError('Group mismatch')
        for role in ('primary','secondary'):
            r,e=current[g[role]],old[t[role]]
            name=r['filename'].replace('\\','/')
            if name.lower()!=e['filename'].replace('\\','/').lower():raise ValueError('Image pairing mismatch')
            candidate=root/name;path=candidate.resolve()
            if not path.is_relative_to(root) or candidate.is_symlink():raise ValueError('Unsafe asset path')
            total+=path.stat().st_size
            if total>128*1024*1024 or path.stat().st_size>16*1024*1024:raise ValueError('Image byte cap')
            if hashlib.sha256(path.read_bytes()).hexdigest()!=e['original_sha256']:raise ValueError('Image hash mismatch')
    return {'owner':h[4],'model':h[10],'source':h[12],'signature':signature,'model_name':'kff.mod',
            'check_points':[list(struct.unpack_from('<3f',packet,256+i*12)) for i in (0,h[16]//2,h[16]-1)],
            'packet_sha256':hashlib.sha256(packet).hexdigest(),'references_sha256':hashlib.sha256(references).hexdigest()}


class Consumer:
    def __init__(self):
        self.last=0;self.epoch=None;self.origin=None;self.seen=None;self.visible=False;self.retired=set()
        self.accepted=0;self.rejected=0

    def update(self, record, assets, now=None):
        now=time.monotonic() if now is None else now
        if record is not None and (len(record)!=48 or any(type(x) is not int or not 0<=x<=0xffffffff for x in record)):
            self.rejected+=1;return None
        if record is None or record[0]<=self.last:return None
        self.last=record[0]
        owner,slot=record[1],record[45]
        if record[4]==2:
            self.retired.add((slot,owner));self.visible=False;return None
        asset=assets.get(slot)
        if (record[4]!=1 or (slot,owner) in self.retired or not asset or owner!=asset['owner']
                or record[5]!=asset['model'] or record[6]!=asset['source'] or any(record[42:45])):
            self.rejected+=1;self.visible=False;return None
        epoch=(slot,owner)
        if self.epoch is not None and epoch<self.epoch:
            self.rejected+=1;self.visible=False;return None
        try:matrix,t=affine(record[8:25],None if epoch!=self.epoch else self.origin)
        except ValueError:self.rejected+=1;return None
        if epoch!=self.epoch:self.origin=t
        self.epoch=epoch;self.seen=now;self.visible=True;self.accepted+=1
        return matrix

    def fresh(self, now=None):
        now=time.monotonic() if now is None else now
        if self.seen is None or now-self.seen>=1:self.visible=False
        return self.visible

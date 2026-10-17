"""Bounded Windows live channel, content qualification and explicit affine conversion.

No game pointers are dereferenced here. Importable without Kit for transport tests.
"""
import ctypes as C
from ctypes import wintypes as W
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import time
import uuid

SIZE = 2*1024*1024
STRIDE = 512*1024
MAGIC = 0x31424C53
WORDS = 96
NAME = re.compile(r'Local\\SFCBridge_[a-f0-9]{32}\Z')


class Channel:
    size=SIZE
    version=2
    receiver_write=False
    def __init__(self, name=None, create=False):
        self.name = name or 'Local\\SFCBridge_'+uuid.uuid4().hex
        if not NAME.fullmatch(self.name):
            raise ValueError('Invalid explicit session name')
        self.handle = self.view = None
        self.k = C.WinDLL('kernel32', use_last_error=True)
        k = self.k
        k.CreateFileMappingW.argtypes = [W.HANDLE, C.c_void_p, W.DWORD, W.DWORD, W.DWORD, W.LPCWSTR]
        k.CreateFileMappingW.restype = W.HANDLE
        k.OpenFileMappingW.argtypes = [W.DWORD, W.BOOL, W.LPCWSTR]; k.OpenFileMappingW.restype = W.HANDLE
        k.MapViewOfFile.argtypes = [W.HANDLE,W.DWORD,W.DWORD,W.DWORD,C.c_size_t]; k.MapViewOfFile.restype = C.c_void_p
        k.UnmapViewOfFile.argtypes = [C.c_void_p]; k.CloseHandle.argtypes = [W.HANDLE]
        k.LocalFree.argtypes = [C.c_void_p]
        if create:
            self._create()
        else:
            self.handle = k.OpenFileMappingW(6 if self.receiver_write else 4, False, self.name)
        if not self.handle:
            raise C.WinError(C.get_last_error())
        self.writable = create or self.receiver_write
        self.view = k.MapViewOfFile(self.handle, 6 if self.writable else 4, 0, 0, self.size)
        if not self.view:
            self.close(); raise C.WinError(C.get_last_error())
        if create:
            words = [MAGIC,self.version,self.size,0]+[int(self.name[-32:][i:i+8],16) for i in range(0,32,8)]
            self.write(0, struct.pack('<8I',*words))
        try:self.validate()
        except Exception:self.close();raise

    def _create(self):
        a=C.WinDLL('advapi32',use_last_error=True); token=W.HANDLE(); needed=W.DWORD()
        a.OpenProcessToken.argtypes=[W.HANDLE,W.DWORD,C.POINTER(W.HANDLE)]
        a.GetTokenInformation.argtypes=[W.HANDLE,C.c_int,C.c_void_p,W.DWORD,C.POINTER(W.DWORD)]
        a.ConvertSidToStringSidW.argtypes=[C.c_void_p,C.POINTER(W.LPWSTR)]
        a.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes=[W.LPCWSTR,W.DWORD,C.POINTER(C.c_void_p),C.c_void_p]
        self.k.GetCurrentProcess.restype=W.HANDLE
        if not a.OpenProcessToken(self.k.GetCurrentProcess(),8,C.byref(token)): raise C.WinError(C.get_last_error())
        sd=C.c_void_p(); sid_text=W.LPWSTR()
        try:
            a.GetTokenInformation(token,1,None,0,C.byref(needed))
            buf=C.create_string_buffer(needed.value)
            if not a.GetTokenInformation(token,1,buf,needed,C.byref(needed)): raise C.WinError(C.get_last_error())
            sid=C.c_void_p.from_buffer(buf).value
            if not a.ConvertSidToStringSidW(sid,C.byref(sid_text)): raise C.WinError(C.get_last_error())
            if not a.ConvertStringSecurityDescriptorToSecurityDescriptorW('D:P(A;;GA;;;'+sid_text.value+')',1,C.byref(sd),None):
                raise C.WinError(C.get_last_error())
            class SA(C.Structure):
                _fields_=[('length',W.DWORD),('descriptor',C.c_void_p),('inherit',W.BOOL)]
            sa=SA(C.sizeof(SA),sd,False)
            self.handle=self.k.CreateFileMappingW(W.HANDLE(-1),C.byref(sa),4,0,self.size,self.name)
            error=C.get_last_error()
            if self.handle and error==183:
                self.k.CloseHandle(self.handle);self.handle=None
                raise ValueError('Existing session must never be reused')
        finally:
            if sid_text:self.k.LocalFree(C.cast(sid_text,C.c_void_p))
            if sd:self.k.LocalFree(sd)
            self.k.CloseHandle(token)

    def read(self, offset, length):
        if not self.view or offset<0 or length<0 or offset+length>self.size: raise ValueError('Channel bounds')
        return C.string_at(self.view+offset,length)

    def write(self, offset, data):
        if not self.writable or offset<0 or offset+len(data)>self.size: raise ValueError('Channel write bounds')
        C.memmove(self.view+offset,data,len(data))

    def validate(self):
        h=struct.unpack('<8I',self.read(0,32))
        expected=tuple(int(self.name[-32:][i:i+8],16) for i in range(0,32,8))
        if h[:3]!=(MAGIC,self.version,self.size) or h[4:]!=expected: raise ValueError('Wrong session/protocol')
        return h[3]

    def sample(self):
        first=struct.unpack('<I',self.read(256,4))[0]
        if not first or first&1:return None
        data=self.read(260,WORDS*4)
        if self.read(256,4)!=struct.pack('<I',first):return None
        return struct.unpack('<96I',data)

    def asset(self, slot):
        if slot not in (0,1):raise ValueError('Asset epoch capacity')
        d=struct.unpack('<4I',self.read(128+slot*32,16))
        if d[0]!=1:return None
        if not 256<=d[1]<STRIDE or not 1<=d[2]<=8192 or d[1]+d[2]>STRIDE:raise ValueError('Asset bounds')
        data=self.read(4096+slot*STRIDE,d[1]+d[2])
        if self.read(128+slot*32,16)!=struct.pack('<4I',*d):return None
        return data[:d[1]],data[d[1]:],d[3]

    def close(self):
        if self.view:self.k.UnmapViewOfFile(self.view);self.view=None
        if self.handle:self.k.CloseHandle(self.handle);self.handle=None


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


def affine(words, origin=None):
    if len(words)!=17:raise ValueError('Native17-word transform required')
    f=struct.unpack('<16f',struct.pack('<16I',*words[:16]))
    if not all(math.isfinite(x) for x in f):raise ValueError('Nonfinite transform')
    # Only sampled rigid subset: reject scale/shear rather than silently repair it.
    for i in range(3):
        for j in range(3):
            if abs(sum(f[i*4+k]*f[j*4+k] for k in range(3))-(i==j))>1e-3:raise ValueError('Unsupported nonrigid transform')
    determinant=(f[0]*(f[5]*f[10]-f[6]*f[9])-f[1]*(f[4]*f[10]-f[6]*f[8])+f[2]*(f[4]*f[9]-f[5]*f[8]))
    if abs(determinant-1)>1e-3:raise ValueError('Unqualified reflected transform')
    t=(f[3],f[7],f[11]);o=t if origin is None else origin
    return ((f[0],f[4],f[8],0),(f[1],f[5],f[9],0),(f[2],f[6],f[10],0),
            (t[0]-o[0],t[1]-o[1],t[2]-o[2],1)),t


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

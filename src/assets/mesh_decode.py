"""Neutral SFC mesh packet decoding, shared by transport and preparation."""
import hashlib,json,math,struct
STRIDE=2*1024*1024

def decode_mesh(packet,references,*,checksum=None):
    return _decode_mesh(packet,references,checksum=checksum,origin=0x0042E55D)


def _decode_mesh(packet,references,*,checksum,origin):
    if not 256<=len(packet)<=STRIDE or len(references)>256*1024:raise ValueError('Packet byte bound')
    h=struct.unpack_from('<64I',packet);nv,np,nc,ng=h[16:20]
    if h[:2]!=(0x314d4653,1) or h[2]!=len(packet):raise ValueError('Mesh header')
    if not h[4] or h[13]!=origin or any(h[24:27]):raise ValueError('Unsupported semantic origin/math dispatch')
    if not(1<=nv<=65536 and 1<=np<=8192 and np*3==nc<=32768 and 1<=ng<=256):raise ValueError('Mesh count/triangles')
    if len(packet)!=256+nv*12+np*36+nc*28+ng*40:raise ValueError('Mesh length')
    if checksum is None:
        value=2166136261
        for i,byte in enumerate(packet):value=((value^(0 if 12<=i<16 else byte))*16777619)&0xffffffff
    else:value=checksum(packet)
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

"""Deterministic synthetic multi-owner rehearsal; never launches SFC."""
import json
import struct
import time
from live_camera import multiply
from live_scene import DATA,STRIDE


def asset_variant(packet,refs,owner,variant=0):
    data=bytearray(packet);h=list(struct.unpack_from('<64I',data));h[4]=owner;h[10]+=owner
    if variant:
        # Explicit synthetic second shape, not evidence of another captured SFC class.
        for i in range(h[16]):
            x=struct.unpack_from('<f',data,256+i*12)[0];struct.pack_into('<f',data,256+i*12,x*1.15)
    h[3]=0;struct.pack_into('<64I',data,0,*h);value=2166136261
    for byte in data:value=((value^byte)*16777619)&0xffffffff
    h[3]=value;struct.pack_into('<64I',data,0,*h)
    references=json.loads(refs);references.update(owner_epoch=owner,model=h[10],packet_fnv1a=value)
    return bytes(data),json.dumps(references).encode(),h


def observation(h,index,revision,sequence,step):
    import math
    a=step*.006;co,si=math.cos(a),math.sin(a)
    model=[[co,-si,0,index*5+step*.005],[si,co,0,0],[0,0,1,0],[0,0,0,1]]
    view=[[1,0,0,step*.002],[0,1,0,0],[0,0,1,-30],[0,0,0,1]]
    p=[[2,0,.12,0],[0,3.2,-.08,0],[0,0,-1.002002,-2.002002],[0,0,-1,0]]
    s=[[512,0,0,712],[0,-320,0,320],[0,0,1,0],[0,0,0,1]]
    def words(m,flag):return list(struct.unpack('<16I',struct.pack('<16f',*(v for row in m for v in row))))+[flag<<8]
    r=[0]*96;r[:8]=[sequence,h[4],step+1,step*34,1,h[10],h[12],revision]
    r[8:25]=words(model,1);r[25:42]=words(multiply(multiply(multiply(s,p),view),model),0)
    r[45]=index;r[48]=1;r[49:66]=words(view,1);r[66:83]=words(p,0)
    r[83:89]=struct.unpack('<6I',struct.pack('<6f',200,0,1024,640,512,320))
    return r


def replay_scene(channel,capture):
    packet=(capture/'LIVE-BRIDGE-001-asset-0.bin').read_bytes();refs=(capture/'LIVE-BRIDGE-001-asset-0.json').read_bytes()
    variants=[asset_variant(packet,refs,1),asset_variant(packet,refs,2,1),asset_variant(packet,refs,3)]
    for index,(mesh,reference,h) in enumerate(variants):
        channel.write(DATA+index*STRIDE,mesh+reference)
        channel.write(256+index*64,struct.pack('<6I',1,0,len(mesh),len(reference),h[4],index+1))
    channel.write(12,struct.pack('<I',1))
    def publish(index,r):
        offset=4096+index*512;channel.write(offset,struct.pack('<I',r[0]*2-1))
        channel.write(offset+4,struct.pack('<96I',*r));channel.write(offset,struct.pack('<I',r[0]*2))
    for step in range(180):
        for index,(_,_,h) in enumerate(variants):
            if index==2 and step<100:continue
            r=observation(h,index,index+1,step+1,step)
            if index==0 and step>=90:r[4]=2
            publish(index,r)
        time.sleep(.034)
    channel.write(12,struct.pack('<I',2))

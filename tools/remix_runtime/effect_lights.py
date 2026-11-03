"""Transient-light configuration. Native state drives lifetime,not cached scene lights."""
import ctypes as C
import struct
from light_controls import number,vector,scales
SOURCE_OFFSET=15*1024*1024+384*1024
CONFIG_OFFSET=SOURCE_OFFSET+32768
SOURCE_MAGIC=0x31464c53
CONFIG_MAGIC=0x31434c45
SOURCE_BYTES=16960
CONFIG_BYTES=1600

def controls(data):
    common=data.get('effects',{})
    allowed={'enabled','intensity_multiplier','color_multiplier','radius'}
    def read(r):
        if not isinstance(r,dict) or set(r)-allowed:raise ValueError('Unknown effect-light control')
        if type(r.get('enabled',True)) is not bool:raise ValueError('Effect enabled must be boolean')
        return dict(enabled=r.get('enabled',True),intensity_multiplier=number(r.get('intensity_multiplier',1),0,1000),
                    color_multiplier=vector(r.get('color_multiplier',[1,1,1]),0,16),radius=number(r.get('radius',1),1e-5,1e5))
    base=read(common);base['enabled']=bool(common) and base['enabled']
    overrides=data.get('effect_lights',[])
    if not isinstance(overrides,list) or len(overrides)>62:raise ValueError('Effect override bounds')
    rows=[dict(base) for _ in range(62)];seen=set()
    for item in overrides:
        if not isinstance(item,dict):raise ValueError('Effect override requires a table')
        slot=item.get('slot')
        if type(slot) is not int or not 2<=slot<64 or slot in seen:raise ValueError('Effect slot must be unique,2..63')
        seen.add(slot);row=read({**base,**{k:v for k,v in item.items() if k!='slot'}})
        row['enabled']=base['enabled'] and row['enabled'];rows[slot-2]=row
    conversion,master=scales(data)
    for row in rows:
        for value in row['color_multiplier']:number(value*row['intensity_multiplier']*conversion*master,0,1e6)
    return rows

def initialize(channel):
    session=[int(channel.name[-32:][i:i+8],16) for i in range(0,32,8)]
    for offset,magic,size in ((SOURCE_OFFSET,SOURCE_MAGIC,SOURCE_BYTES),(CONFIG_OFFSET,CONFIG_MAGIC,CONFIG_BYTES)):
        channel.write(offset,struct.pack('<8I',magic,1,size,*session,0)+bytes(size-32))

def publish(channel,data,generation):
    from live_lights import fnv
    rows=controls(data);conversion,master=scales(data);raw=struct.pack('<4I',CONFIG_MAGIC,1,1512,generation)
    for row in rows:
        gain=[row['intensity_multiplier']*v*conversion*master for v in row['color_multiplier']]
        raw+=struct.pack('<I4fI',int(row['enabled']),*gain,row['radius'],0)
    raw+=struct.pack('<Q',fnv(raw));assert len(raw)==1512
    cell=CONFIG_OFFSET+64;guard=C.c_uint32.from_address(channel.view+cell)
    guard.value+=1;channel.write(cell+8,struct.pack('<Q',generation)+raw);guard.value+=1
    C.c_uint32.from_address(channel.view+SOURCE_OFFSET+40).value=int(any(r['enabled'] for r in rows))
    return rows

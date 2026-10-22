"""Fixed current-user scene-map light cells. No per-frame files or timestamp refresh."""
import ctypes as C
import struct

RAW_OFFSET=15*1024*1024
ENCODED_OFFSET=RAW_OFFSET+256*1024
RAW_MAGIC=0x31524c53
ENCODED_MAGIC=0x31454c53
RAW_BYTES=198720
ENCODED_BYTES=1088
RAW_STRIDE=6208


def initialize(channel):
    words=[int(channel.name[-32:][i:i+8],16) for i in range(0,32,8)]
    for offset,magic,size in ((RAW_OFFSET,RAW_MAGIC,RAW_BYTES),(ENCODED_OFFSET,ENCODED_MAGIC,ENCODED_BYTES)):
        channel.write(offset,struct.pack('<8I',magic,1,size,*words,0)+bytes(size-32))


def valid_header(channel,offset,magic,size,pid=0):
    h=struct.unpack('<16I',channel.read(offset,64))
    session=tuple(int(channel.name[-32:][i:i+8],16) for i in range(0,32,8))
    return h[:3]==(magic,1,size) and h[3:7]==session and (not pid or h[7]==pid) and not h[8] and not any(h[10:])


def read_native(channel,owner,pid):
    if not valid_header(channel,RAW_OFFSET,RAW_MAGIC,RAW_BYTES,pid):return None
    offset=RAW_OFFSET+64+(owner%32)*RAW_STRIDE
    guard=channel.read(offset,4)
    if not struct.unpack('<I',guard)[0] or struct.unpack('<I',guard)[0]&1:return None
    raw=channel.read(offset+8,8+6156)
    if channel.read(offset,4)!=guard:return None
    tick=struct.unpack_from('<Q',raw)[0]
    if not tick or struct.unpack_from('<I',raw,8+32)[0]!=owner:return None
    return raw[8:],tick


def publish_encoded(channel,pid,packet,shapes,captured):
    if len(packet)!=200 or len(shapes)!=808 or not captured:raise ValueError('Shared light payload bounds')
    if not valid_header(channel,ENCODED_OFFSET,ENCODED_MAGIC,ENCODED_BYTES):raise ValueError('Shared light context')
    C.c_uint32.from_address(channel.view+ENCODED_OFFSET+28).value=pid
    cell=ENCODED_OFFSET+64
    guard=C.c_uint32.from_address(channel.view+cell)
    if guard.value&1:raise ValueError('Concurrent light publishers forbidden')
    guard.value+=1
    channel.write(cell+8,struct.pack('<Q',captured)+packet+shapes)
    guard.value+=1
    C.c_uint32.from_address(channel.view+ENCODED_OFFSET+36).value+=1

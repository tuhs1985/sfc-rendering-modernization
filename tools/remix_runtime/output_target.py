"""Bounded reader of the native target notice; never infers size from a mesh."""
import struct
from output_extent import requirements
from owner_rebind import fnv

OFFSET,SIZE,MAGIC,VERSION=4352,128,0x31544754,1
NOTICE=struct.Struct('<8IQ4IQ')
assert NOTICE.size==64


def read(channel,pid):
    before=struct.unpack('<i',channel.read(OFFSET,4))[0]
    if not before or before&1:return None
    raw=channel.read(OFFSET+64,64)
    after=struct.unpack('<i',channel.read(OFFSET,4))[0]
    if before!=after:return None
    values=NOTICE.unpack(raw)
    session=tuple(int(channel.name[-32:][i:i+8],16) for i in range(0,32,8))
    if (values[:4]!=(MAGIC,VERSION,64,pid) or values[4:8]!=session or
            not values[8] or not values[11] or not values[12] or fnv(raw[:-8])!=values[-1]):
        return None
    try:budget=requirements(values[9],values[10])
    except ValueError:return None
    return dict(budget,device_generation=values[11],target_generation=values[12],observed_qpc=values[8])

"""Protocol4 fresh scene transport/validation. No template import or native dereference."""
import ctypes
import hashlib
import io
import json
import math
from pathlib import Path
import struct
import time
from live_bridge import Channel, affine
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'remix_runtime'))
from scene_capacity import OWNERS,ASSETS,STATE_OFFSET,VERSION

SIZE=16*1024*1024
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src/assets'))
from mesh_decode import STRIDE,decode_mesh,_decode_mesh
DATA=65536
IMAGE_LIMIT=128*1024*1024
MEMORY_LIMIT=256*1024*1024


class SceneChannel(Channel):
    size=SIZE
    version=VERSION
    receiver_write=True  # explicit current-user-only acknowledgements

    def owner_indices(self):
        count=struct.unpack("<I",self.read(128,4))[0]
        if count>OWNERS:raise ValueError("Owner table high-water mark")
        return range(count)

    def sample_owner(self,index):
        if not 0<=index<OWNERS:raise ValueError('Owner index')
        offset=STATE_OFFSET+index*512
        guard=self.read(offset,4);value=struct.unpack('<I',guard)[0]
        if not value or value&1:return None
        row=struct.unpack('<96I',self.read(offset+4,384))
        return row if self.read(offset,4)==guard and row[45]==index else None

    def asset_transfer(self,index):
        if not 0<=index<4:raise ValueError('Transfer slot')
        offset=256+index*64
        desc=self.read(offset,24);generation,ack,nmesh,nrefs,owner,revision=struct.unpack('<6I',desc)
        if not generation or generation==ack:return None
        if generation<ack or not 256<=nmesh<STRIDE or not 1<=nrefs<=256*1024 or nmesh+nrefs>STRIDE or not 1<=revision<=ASSETS or not owner:
            raise ValueError('Transfer bounds/generation')
        payload=self.read(DATA+index*STRIDE,nmesh+nrefs)
        if self.read(offset,24)!=desc:return None
        return generation,revision,owner,payload[:nmesh],payload[nmesh:]

    def acknowledge(self,index,generation):
        if not 0<=index<4 or struct.unpack('<I',self.read(256+index*64,4))[0]!=generation:
            raise ValueError('Stale acknowledgement')
        # Aligned release store on Windows/x86, only after payload is consumed.
        ctypes.c_uint32.from_address(self.view+260+index*64).value=generation












def __getattr__(name):
    if name not in {'ImageStore','qualify_mesh','SceneConsumer'}:raise AttributeError(name)
    from scene_bundle import _development_review
    return getattr(_development_review(),name)

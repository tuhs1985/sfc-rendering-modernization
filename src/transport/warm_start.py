"""One immutable, session-bound activation of an already running native host."""
import struct
import math
import re
from owner_rebind import fnv

ACTIVATION=struct.Struct('<10I2Q32sfIQ')
def packet(env,session):
    if not re.fullmatch(r'Local\\SFCBridge_[0-9a-f]{32}',session):raise ValueError('Warm session identity')
    words=[int(session[-32:][i:i+8],16) for i in range(0,32,8)]
    fields=(0x31524157,1,ACTIVATION.size,int(env['SFC_D3D9_GAME_PID']),*words,
            int(env['SFC_D3D9_EXPECTED_MODEL']),int(env['SFC_D3D9_EXPECTED_SOURCE']),
            int(env['SFC_D3D9_INITIAL_ASSET_MASK'],16),int(env['SFC_D3D9_REBIND_COOKIE'],16),
            bytes.fromhex(env['SFC_D3D9_ASSET_SHA256']),float(env['SFC_D3D9_OFFSET_X']),0,0)
    raw=ACTIVATION.pack(*fields)
    if (not all(0<fields[i]<=0xffffffff for i in (3,8,9)) or not fields[10] or not fields[11]
            or not any(fields[12]) or not math.isfinite(fields[13]) or not -1e6<=fields[13]<=0):
        raise ValueError('Warm activation identity/extent')
    return raw[:-8]+struct.pack('<Q',fnv(raw[:-8]))

# First64KiB is transport metadata; payloads start at65536. No M1 bootstrap changes.
import ctypes as C
import os
OFFSET=4096
STORE_BYTES=256
HEADER=struct.Struct('<9I')

def _words(session):
    if not re.fullmatch(r'Local\\SFCBridge_[0-9a-f]{32}',session):raise ValueError('Warm session identity')
    return [int(session[-32:][i:i+8],16) for i in range(0,32,8)]

def _state(channel,value=None):
    cell=C.c_int32.from_address(channel.view+OFFSET+36)
    if value is not None:cell.value=value
    return cell.value

def initialize(channel,pid):
    if not 0<pid<=0xffffffff:raise ValueError('Warm game PID')
    if channel.read(OFFSET,STORE_BYTES)!=bytes(STORE_BYTES):raise ValueError('Startup cell already initialized')
    raw=HEADER.pack(0x31545353,1,STORE_BYTES,pid,*_words(channel.name),os.getpid())
    channel.write(OFFSET,raw+bytes(STORE_BYTES-len(raw)))

def _header(channel):
    h=HEADER.unpack(channel.read(OFFSET,HEADER.size))
    if h[:3]!=(0x31545353,1,STORE_BYTES) or not h[3] or tuple(h[4:8])!=tuple(_words(channel.name)) or h[8]!=os.getpid():
        raise ValueError('Startup cell session/creator/layout')
    return h

def ready(channel):
    _header(channel)
    flag=struct.unpack('<i',channel.read(OFFSET+44,4))[0]
    if flag in (0,-1):return None
    if flag!=1:raise ValueError('Startup readiness state')
    host=struct.unpack('<I',channel.read(OFFSET+40,4))[0]
    qpc=struct.unpack('<Q',channel.read(OFFSET+48,8))[0]
    if not host or not qpc:raise ValueError('Startup readiness identity')
    return qpc,host

def activate(channel,env,session):
    h=_header(channel)
    if session!=channel.name:raise ValueError('Startup explicit session mismatch')
    raw=packet(env,session)
    if ACTIVATION.unpack(raw)[3]!=h[3]:raise ValueError('Startup game identity mismatch')
    if _state(channel)!=0:raise ValueError('Warm renderer already activated/cancelled')
    # Single supervisor writer,aligned release stores on supported Windows x86/x64.
    _state(channel,1)
    channel.write(OFFSET+64,raw)
    qpc=C.c_int64()
    if not C.WinDLL('kernel32',use_last_error=True).QueryPerformanceCounter(C.byref(qpc)):raise C.WinError(C.get_last_error())
    channel.write(OFFSET+56,struct.pack('<Q',qpc.value))
    _state(channel,2)

def cancel(channel):
    _header(channel)
    _state(channel,4)

def snapshot(channel):
    h=_header(channel)
    state,host,flag=struct.unpack('<iIi',channel.read(OFFSET+36,12))
    ready_qpc,published=struct.unpack('<2Q',channel.read(OFFSET+48,16))
    accepted=struct.unpack('<Q',channel.read(OFFSET+168,8))[0]
    return dict(protocol='shared-startup-v1',state=state,game_pid=h[3],producer_pid=h[8],host_pid=host,ready=flag,
                ready_qpc=ready_qpc,published_qpc=published,accepted_qpc=accepted,
                scope='One-shot ticket and worker readiness only;not frame or material readiness')

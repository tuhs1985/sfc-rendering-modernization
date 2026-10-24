"""One immutable, session-bound activation of an already running native host."""
import struct
import math
import re
from pathlib import Path
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

def activate(folder,env,session):
    folder=Path(folder);target=folder/'renderer-activate.bin'
    if target.exists():raise ValueError('Warm renderer already activated')
    pending=target.with_suffix('.pending');pending.write_bytes(packet(env,session));pending.replace(target)

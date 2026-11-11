"""SFC's separate damage UV projection, built once on an asset worker.

Native 0042EB52..0042EE28; source coordinates/normals/UVs are never modified.
Image origin correction belongs to the renderer adapter, not this mapping.
"""
import math
import struct

def f32(f):return struct.unpack('<f',struct.pack('<f',f))[0]

def scale(upper,lower):
    if not all(math.isfinite(x) for x in (upper,lower)):raise ValueError('Damage mapping bounds nonfinite')
    # The native span is stored to float before the strict 7.5 comparison.
    span=f32(upper-lower)
    return f32(.15*.1875) if span>7.5 else .1875

def projected_uv(point,normal,factor):
    if len(point)!=3 or len(normal)!=3 or not all(math.isfinite(x) for x in (*point,*normal,factor)):
        raise ValueError('Damage mapping inputs nonfinite/layout')
    x,y,z=map(abs,normal)
    axes=(1,2) if x>y and x>z else (0,2) if y>x and y>z else (0,1)
    return tuple(f32(point[a]*factor+.5) for a in axes)

def corners(positions,polygons,source_corners,upper,lower):
    """Return a separate corner array; preserve raw index/normal/auxiliary words."""
    if not 0<len(positions)<=65536 or not 0<len(polygons)<=8192 or not 0<len(source_corners)<=32768:
        raise ValueError('Damage mapping counts')
    out=[list(row) for row in source_corners];factor=scale(upper,lower);expected=0
    for polygon in polygons:
        count,first,normal=polygon
        if count!=3 or first!=expected or first+count>len(out):raise ValueError('Damage mapping triangular corner coverage')
        for i in range(first,first+count):
            row=out[i]
            if len(row)!=7 or not 0<=row[0]&65535<len(positions):raise ValueError('Damage mapping corner index')
            uv=projected_uv(positions[row[0]&65535],normal,factor)
            row[4:6]=struct.unpack('<2I',struct.pack('<2f',*uv))
        expected+=count
    if expected!=len(out):raise ValueError('Damage mapping incomplete corners')
    return out

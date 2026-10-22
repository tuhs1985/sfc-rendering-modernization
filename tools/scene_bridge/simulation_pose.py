"""Scalar native getter arithmetic,independent of cached render submission."""
import math
import struct

def multiply(a,b):return [sum(a[i*4+k]*b[k*4+j] for k in range(4)) for i in range(4) for j in range(4)]
def rotation(axis,angle):
    a=(angle&8191)*2*math.pi/8192;c=math.cos(a);s=math.sin(a)
    r=[float(i//4==i%4) for i in range(16)]
    if axis==0:r[5]=r[10]=c;r[6]=-s;r[9]=s
    elif axis==1:r[0]=r[10]=c;r[2]=s;r[8]=-s
    else:r[0]=r[5]=c;r[1]=-s;r[4]=s
    return r
def pose(row):
    m=[float(i//4==i%4) for i in range(16)]
    for i,v in zip((3,7,11),row['base_position']):m[i]=v
    a=row['base_angles'];b=row['ship_angles_raw']
    for axis,angle in ((0,2048),(1,a[0]),(2,a[2]),(0,a[1]),(2,b[2]),(0,b[0])):
        m=multiply(m,rotation(axis,angle))
    extra=struct.unpack('<16f',struct.pack('<16I',*row['rotation_words'][:16]))
    m=multiply(m,extra)
    for i,v in zip((3,7,11),row['position']):m[i]+=v
    if not all(math.isfinite(v) for v in m):raise ValueError('Nonfinite simulation pose')
    return m

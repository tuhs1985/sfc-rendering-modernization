"""Mechanical reference fixture,clearly distinct from actual SFC asset evidence."""
import json
from pathlib import Path
import struct
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/scene_bridge'))
from scene_bundle import MAGIC,TEXTURE_MAGIC,FRAME


def prepare(folder):
    folder=Path(folder);folder.mkdir()
    # Asymmetric two-triangle plate with captured-style untransformed XYZ/N/UV.
    vertices=[(-1.,-.5,0,0,0,1,0,1),(1.,-.5,0,0,0,1,1,1),(-1.,.5,0,0,0,1,0,0),
              (-1.,.5,0,0,0,1,0,0),(1.,-.5,0,0,0,1,1,1),(1.,.5,0,0,0,1,1,0)]
    groups=[(7,0,0,3),(9,1,3,3)]
    for i,colors in enumerate(([(0,0,255),(0,255,0),(255,0,0),(0,255,255)],
                                [(255,0,255),(255,255,0),(255,128,0),(128,0,255)])):
        payload=b''.join(bytes([*c,255]) for c in colors)
        (folder/f'texture-{i}.bin').write_bytes(struct.pack('<4I',TEXTURE_MAGIC,2,2,16)+payload)
    view=np.eye(4);view[2,3]=-5
    projection=np.array([[.5625,0,0,0],[0,1,0,0],[0,0,-1.1,-1],[0,0,-1,0]])
    viewport=np.array([[960,0,0,960],[0,-540,0,540],[0,0,1,0],[0,0,0,1]])
    frames=[]
    for i in range(4):
        world=np.eye(4);v=view.copy()
        if i==1:world[0,3]=1
        if i==2:world[:2,:2]=[[0,-1],[1,0]]
        if i==3:v[0,3]=-.5
        frames.append(dict(owner=1,revision=1,frame=i+1,active=1,model=world.tolist(),view=v.tolist(),
            projection=projection.tolist(),viewport=[0,0,1920,1080],native_composed=(viewport@projection@v@world).tolist()))
    payload=struct.pack('<8I',MAGIC,1,6,6,2,len(frames),960,540)
    payload+=b''.join(struct.pack('<8f',*v) for v in vertices)+struct.pack('<6I',*range(6))
    payload+=b''.join(struct.pack('<4I',*g) for g in groups)
    for f in frames:payload+=FRAME.pack(f['owner'],f['revision'],f['frame'],f['active'],
        *np.asarray(f['model']).flat,*np.asarray(f['view']).flat,*np.asarray(f['projection']).flat,*f['viewport'])
    (folder/'scene.bin').write_bytes(payload)
    (folder/'scene.json').write_text(json.dumps(dict(schema='SFC-neutral-offline-scene-1',synthetic=True,
        frames=frames,groups=groups,purpose='known translation,rotation,camera and UV quadrants;NOT SFC runtime evidence'),indent=2))
    return folder

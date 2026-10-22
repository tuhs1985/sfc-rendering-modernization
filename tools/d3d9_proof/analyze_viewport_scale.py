"""Compare native composed projection with returned full-frustum placement."""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from run_offline import ROOT
from scene_bundle import native_matrix
from live_scene import decode_mesh


def compare(row,points):
    model,view,projection,composed=(np.asarray(native_matrix(row[i:i+17]),dtype=float) for i in (8,49,66,25))
    import struct
    x,y,w,h=struct.unpack('<4f',struct.pack('<4I',*row[83:87]))
    if not (w>0 and h>0 and x>=0 and y>=0 and x+w<=1920 and y+h<=1080):raise ValueError('Viewport bounds')
    p=np.column_stack((points,np.ones(len(points))))
    clip=p@(projection@view@model).T;native=p@composed.T
    valid=(clip[:,3]>1e-8)&(np.abs(native[:,3])>1e-8)
    if not valid.any():raise ValueError('No forward projected vertices')
    ndc=clip[valid,:2]/clip[valid,3,None]
    full=np.column_stack(((ndc[:,0]+1)*960,(1-ndc[:,1])*540))
    expected=native[valid,:2]/native[valid,3,None]
    mapped=full*np.array([w/1920,h/1080])+[x,y]
    span=np.max(np.ptp(np.asarray(points),axis=0));distance=1.5*span
    shifted=model.copy();shifted[:3,3]+=-distance*view[0,:3]
    offset_clip=p@(projection@view@shifted).T
    depth_error=float(np.max(np.abs(offset_clip[:,3]-clip[:,3])))
    return dict(vertices=int(valid.sum()),viewport=[x,y,w,h],
        max_corrected_projection_error_pixels=float(np.max(np.abs(mapped-expected))),
        max_old_placement_error_pixels=float(np.max(np.abs(full-expected))),
        old_relative_magnification=[1920/w,1080/h],
        max_camera_left_depth_change=depth_error)


def analyze(folder):
    folder=Path(folder).resolve();folder.relative_to(ROOT/'artifacts/remix-runtime/runs')
    manifest=json.loads((folder/'gpu/scene.json').read_text());source=ROOT/manifest['source_packet']
    mesh=decode_mesh(source.read_bytes(),source.with_suffix('.json').read_bytes())
    points=np.asarray([mesh['points'][i] for i in sorted({c[0] for c in mesh['corners']})])
    path=source.parent/'LIVE-SCENE-001-updates.jsonl'
    if path.stat().st_size>32*1024*1024:raise ValueError('State evidence cap')
    rows=[json.loads(line) for line in path.read_text().splitlines()]
    r=manifest['fresh_preparation_row'];rows=[a for a in rows if len(a)==96 and (a[1],a[7])==(r[1],r[7]) and a[4]==1 and a[48]==1 and not any(a[42:45])]
    if not rows:raise ValueError('No qualified source rows')
    sampled=[rows[i] for i in np.unique(np.linspace(0,len(rows)-1,min(64,len(rows)),dtype=int))]
    results=[compare(row,points) for row in sampled]
    error=max(x['max_corrected_projection_error_pixels'] for x in results)
    return dict(result='NATIVE_VIEWPORT_MAPPING_CORROBORATED' if error<=.25 else 'VIEWPORT_MAPPING_PARTIAL',
        source=str(folder.relative_to(ROOT)),qualified_rows=len(rows),sampled_rows=len(results),points=len(points),
        max_error_pixels=error,max_depth_change=max(x['max_camera_left_depth_change'] for x in results),
        first=results[0],scope='Captured native composed transform vs independent reconstructed projection;not an in-game silhouette screenshot comparison')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('folder',type=Path);args=parser.parse_args();print(json.dumps(analyze(args.folder),indent=2))

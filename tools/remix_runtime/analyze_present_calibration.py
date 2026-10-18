"""Offline same-submission projection/depth comparison; never suppresses SFC draws."""
import argparse
import json
import math
from pathlib import Path
import sys
import numpy as np
from PIL import Image
from depth_snapshot_analysis import ROOT,read_packet,digest
from present_calibration import analyze as verify_provenance
sys.path.insert(0,str(ROOT/'tools/remix_ingest'))
from live_scene import decode_mesh
from live_camera import camera_state
from analyze_live_camera import native_matrix

def native_depth_planes(projection):
    # Solve native z=-a+b/d against D3D A+B/d,without fitting captured pixels.
    a,b=projection[2][2:4]
    if not (math.isfinite(a) and math.isfinite(b) and a<-1 and b<0):raise ValueError('Unsupported native depth coefficients')
    near,far=b/a,b/(a+1)
    if not 0<near<far:raise ValueError('Invalid derived D3D planes')
    return near,far

def rasterize(vertices,shape):
    """Native screen XYZ triangles, sampled at source(2*x+.5,2*y+.5).

    No face reversal, fitting, cull guess, shader emulation or exact MSAA claim.
    Opaque,double-sided geometric candidate only. Near-crossing must be rejected.
    """
    h,w=shape;out=np.full((h,w),np.inf)
    vertices=np.asarray(vertices,dtype=float)
    if vertices.ndim!=2 or vertices.shape[1]!=3 or len(vertices)%3 or not np.isfinite(vertices).all():raise ValueError('Triangle projection input')
    for a,b,c in vertices.reshape(-1,3,3):
        lo=np.min([a,b,c],axis=0);hi=np.max([a,b,c],axis=0)
        xmin=max(0,int(math.ceil((lo[0]-.5)/2)));xmax=min(w-1,int(math.floor((hi[0]-.5)/2)))
        ymin=max(0,int(math.ceil((lo[1]-.5)/2)));ymax=min(h-1,int(math.floor((hi[1]-.5)/2)))
        if xmax<xmin or ymax<ymin:continue
        den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-12:continue
        yy,xx=np.mgrid[ymin:ymax+1,xmin:xmax+1];xx=xx*2+.5;yy=yy*2+.5
        wa=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
        wb=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;wc=1-wa-wb
        valid=(wa>=0)&(wb>=0)&(wc>=0)
        z=wa*a[2]+wb*b[2]+wc*c[2]
        region=out[ymin:ymax+1,xmin:xmax+1]
        np.minimum(region,np.where(valid,z,np.inf),out=region)
    return out

def interior(mask):
    result=mask.copy();result[[0,-1],:]=False;result[:,[0,-1]]=False
    result[1:-1,1:-1]&=mask[:-2,1:-1]&mask[2:,1:-1]&mask[1:-1,:-2]&mask[1:-1,2:]
    return result

def compare(predicted,depth,mask):
    expected=predicted[mask];low=depth[:,:,1][mask];high=depth[:,:,2][mask]
    if not len(expected):return {'pixels':0}
    # Compare against all-eight-sample interval, not a falsely exact sample0 ray.
    distance=np.maximum(np.maximum(low-expected,expected-high),0.)
    tolerance=2e-5
    return dict(pixels=len(expected),median_interval_error=float(np.median(distance)),
        p95_interval_error=float(np.quantile(distance,.95)),
        within_2e_5=int(np.count_nonzero(distance<=tolerance)),
        fraction_within_2e_5=float(np.mean(distance<=tolerance)),
        observed_closer=int(np.count_nonzero(high<expected-tolerance)),
        predicted_closer=int(np.count_nonzero(low>expected+tolerance)))

def analyze(folder,images=False):
    folder=Path(folder).resolve();folder.relative_to(ROOT/'artifacts/remix-runtime/runs')
    metadata=json.loads((folder/'manifest.json').read_text());result=json.loads((folder/'result.json').read_text())
    session=metadata['semantic_calibration']['scene_session'];pid=result['target_pid']
    provenance=verify_provenance(folder,session,pid)
    rows=[]
    for i,snapshot in enumerate(provenance['snapshots']):
        dp,depth,color=read_packet(folder/f'depth-{i}.bin');owners=[]
        if not dp['valid']:raise ValueError('Invalid native depth')
        if len(snapshot['associations'])>8:raise ValueError('Offline eight-owner comparison limit')
        overlay=color[::2,::2,:3].copy()
        for ordinal,association in enumerate(snapshot['associations']):
            record=association['record'];base=folder/'gate'/f"LIVE-SCENE-001-asset-{association['revision']}"
            data=decode_mesh(base.with_suffix('.bin').read_bytes(),base.with_suffix('.json').read_bytes())
            state=camera_state(record,[0,0,0],data['used_points'])
            points=np.asarray(data['points']);indices=[v[0] for v in data['corners']]
            # Explicit polygon corner ordinals;do not assume arbitrary packet order.
            ordered=[indices[start+j] for _,start in data['polygons'] for j in range(3)]
            vertices=points[ordered];c=np.asarray(state['native_composed'])
            clip=np.c_[vertices,np.ones(len(vertices))]@c.T
            if np.any(clip[:,3]<=0):raise ValueError('Near/behind camera clipping unqualified')
            projected=clip[:,:3]/clip[:,3,None]
            z=rasterize(projected,depth.shape[:2]);coverage=np.isfinite(z);core=interior(coverage)
            tests={'native_z':compare(z,depth,core),'half_z_plus_half':compare(.5*z+.5,depth,core)}
            near,far=native_depth_planes(native_matrix(record[66:83]))
            owner=dict(owner=record[1],asset_revision=record[7],model=data['refs']['model_filename'],
                packet_sha256=data['packet_sha256'],triangles=len(data['polygons']),
                viewport=state['viewport'],composition_error_pixels=state['native_composition_pixel_error'],
                projected_pixels=int(coverage.sum()),interior_pixels=int(core.sum()),depth_conventions=tests)
            owner['depth_conversion_arithmetic']={'existing_sdk_near':state['near']/100,
                'native_z_equivalent_d3d_near':near,'far':far,
                'status':'Derived from native coefficients only;SDK rendering with this conversion not exercised here'}
            owners.append(owner)
            edge=coverage&~core;overlay[edge]=[(255,40,40),(40,255,40)][ordinal%2]
        row=dict(engine_frame=snapshot['engine_frame'],present_frame=dp['present_frame'],qpc=dp['qpc'],owners=owners)
        if images:
            p=folder/f'calibration-{i}-projection.png';Image.fromarray(overlay).save(p)
            row['overlay']=dict(file=p.name,sha256=digest(p),bytes=p.stat().st_size)
        rows.append(row)
    report=dict(probe='REMIX-CALIBRATION-001',analysis_version=1,snapshots=rows,
        sampling='Candidate at original pixel center(2x+.5,2y+.5);one-grid-cell boundary removed;compare against8MSAA min/max interval,tolerance2e-5. Not exact per-sample coverage.',
        limitations=['Opaque double-sided geometric projection,not native culling/material/alpha emulation',
            'Other geometry may occlude;depth agreement alone does not prove ownership',
            'Both fixed depth conventions reported without fitted parameters',
            'No suppression,replacement,light capture or milestone completion'])
    (folder/'calibration.projection.json').write_text(json.dumps(report,indent=2))
    if sum(p.stat().st_size for pattern in ('depth-*.bin','depth-*.png','calibration-*.png') for p in folder.glob(pattern))>64*1024*1024:raise ValueError('Image64MiB budget')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run',type=Path);p.add_argument('--images',action='store_true');a=p.parse_args()
    print(json.dumps(analyze(a.run,a.images),indent=2))

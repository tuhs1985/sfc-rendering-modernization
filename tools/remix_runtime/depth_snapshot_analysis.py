"""Bounded offline depth/color verification. Never opens a game/GPU resource."""
from pathlib import Path
import argparse
import hashlib
import json
import struct
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
HEADER=struct.Struct('<96Q')
LIMIT=64*1024*1024
STAGES=('none','feature','compile_vs','compile_ps','create_vs','create_ps','deferred',
        'raster','depth_state','output_texture','output_view','staging_depth','source_view',
        'query','state_overflow','poll','timeout','map_depth','map_color','color_descriptor',
        'color_changed','staging_color','commands')

def digest(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest().upper()

def read_packet(path):
    path=Path(path)
    if not HEADER.size<=path.stat().st_size<=16_588_800+HEADER.size:raise ValueError('Snapshot file-size limit')
    with path.open('rb') as f:
        h=HEADER.unpack(f.read(HEADER.size))
        if h[:3]!=(0x44535031,1,768):raise ValueError('Snapshot wire version')
        dw,dh,cw,ch,sw,sh,samples,step=h[3:11]
        if not (0<sw<=1920 and 0<sh<=1080 and (cw,ch)==(sw,sh)
                and (dw,dh)==((sw+1)//2,(sh+1)//2) and (samples,step)==(8,2)):raise ValueError('Snapshot dimensions/samples')
        if h[14:16]!=(dw*dh*16,cw*ch*4) or path.stat().st_size!=768+h[14]+h[15]:raise ValueError('Snapshot byte/count mismatch')
        if h[16] not in (28,87) or not 1<=h[17]<=16 or any(h[18:32]):raise ValueError('Snapshot format/state count/reserved')
        if not all(h[n] for n in (11,12,13)):raise ValueError('Missing frame/time/epoch provenance')
        states=[h[32+i*4:36+i*4] for i in range(h[17])]
        if any(row[0]&~0x10101 or not 1<=row[1]<=8 or row[2]>255 or not row[3] for row in states):raise ValueError('Invalid depth-state observation')
        if any(h[32+h[17]*4:]):raise ValueError('Unused state rows not zero')
        depth=np.frombuffer(f.read(h[14]),dtype='<f4').reshape(dh,dw,4).copy()
        color=np.frombuffer(f.read(h[15]),dtype=np.uint8).reshape(ch,cw,4).copy()
    if h[16]==87:color=color[:,:,[2,1,0,3]]
    finite=np.isfinite(depth)
    invalid=int(np.count_nonzero(~finite));outside=int(np.count_nonzero(finite&((depth<0)|(depth>1))))
    order=int(np.count_nonzero(finite.all(axis=2)&((depth[:,:,1]>depth[:,:,0]+1e-6)|(depth[:,:,0]>depth[:,:,2]+1e-6)|(depth[:,:,3]<depth[:,:,1]-1e-6)|(depth[:,:,3]>depth[:,:,2]+1e-6))))
    row={'file':path.name,'sha256':digest(path),'bytes':path.stat().st_size,'source_size':[sw,sh],
         'depth_size':[dw,dh],'samples':samples,'sample_step':step,'qpc':h[11],'present_frame':h[12],
         'resource_epoch':h[13],'nonfinite_values':invalid,'out_of_range_values':outside,
         'color_alpha_range':[int(color[:,:,3].min()),int(color[:,:,3].max())],
         'sample_order_errors':order,'valid':not (invalid or outside or order),
         'native_depth_states':[{'flags':s[0],'compare_func':s[1],'stencil_ref':s[2],'draws':s[3]} for s in states]}
    return row,depth,color

def analyze_run(folder,images=False):
    folder=Path(folder);paths=sorted(folder.glob('depth-*.bin'))
    if len(paths)>3 or sum(p.stat().st_size for p in paths)>LIMIT:raise ValueError('Three-pair image budget')
    status=json.loads((folder/'depth-status.json').read_text())
    stage=status.get('failure_stage')
    if isinstance(stage,int):
        status['failure_stage_name']=STAGES[stage] if 0<=stage<len(STAGES) else 'unknown'
        status['failure_hresult_hex']=f"0x{status.get('failure_hresult',0):08X}"
    rows=[];previous=0;frames=0
    for p in paths:
        row,depth,color=read_packet(p)
        if row['qpc']<=previous or row['present_frame']<=frames:raise ValueError('Nonmonotonic snapshot provenance')
        previous=row['qpc'];frames=row['present_frame']
        if images:
            # Display derivatives ONLY: raw full-resolution color and all samples
            # are immutable. Color downsample documented to match depth grid.
            Image.fromarray(color[:,:,:3]).resize(tuple(row['depth_size']),Image.Resampling.NEAREST).save(p.with_name(p.stem+'-color.png'))
            for i,name in enumerate(('sample0','min','max','mean')):
                values=depth[:,:,i];valid=values[np.isfinite(values)]
                lo,hi=(float(valid.min()),float(valid.max())) if len(valid) else (0.,1.)
                row.setdefault('display_ranges',{})[name]=[lo,hi]
                scaled=np.nan_to_num((values-lo)/max(hi-lo,1e-12),nan=0.,posinf=1.,neginf=0.)
                Image.fromarray((np.clip(scaled,0,1)*255).astype(np.uint8)).save(p.with_name(p.stem+'-'+name+'.png'))
            image_size=sum(v.stat().st_size for pattern in ('depth-*.bin','depth-*.png') for v in folder.glob(pattern))
            if image_size>LIMIT:raise ValueError('Raw+derived image64MiB limit')
        rows.append(row)
    complete=(len(rows)==status.get('files')==status.get('issued')==3 and
              not any(status.get(n,True) for n in ('io_errors','gpu_failures','ambiguous','pending_abandoned')) and all(r['valid'] for r in rows))
    result={'probe':'REMIX-DEPTH-001','complete':complete,'status':status,'snapshots':rows,
            'interpretation':'Content awaits ship/camera comparison. No owner/occlusion qualification inferred.',
            'display_conversion':'Every-second source pixel; per-plane observed min/max contrast. Color RGB (raw alpha retained in packet),nearest downsample to depth grid. No linear distance conversion.'}
    (folder/'depth.analysis.json').write_text(json.dumps(result,indent=2))
    return result

def require_qualification():
    from prepare_full_reshade import source_hashes
    p=ROOT/'artifacts/remix-runtime/deps/depth-snapshot-qualification.json'
    q=json.loads(p.read_text())
    if q.get('result')!='OFFLINE_DEPTH_SNAPSHOT_PASS' or q.get('source_hashes')!=source_hashes():raise ValueError('Depth snapshot sources changed; offline requalification required')
    if q.get('addon_sha256')!=digest(ROOT/'artifacts/remix-runtime/return-bin/SFCRemixReturn.dll'):raise ValueError('Depth snapshot binary changed')
    if q.get('tested_feature_level')!=0xA100 or q.get('reader')!='ps_4_1':raise ValueError('Explicit SFC10_1-mode qualification required')
    return q

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run',type=Path);p.add_argument('--images',action='store_true');args=p.parse_args()
    print(json.dumps(analyze_run(args.run,args.images),indent=2))

"""Standalone bounded runtime output experiment. No game or Toolkit launch."""
from pathlib import Path
import argparse
import datetime as dt
import hashlib
import json
import math
import os
import struct
import subprocess as sp
import sys
import time
import zipfile
import numpy as np
from PIL import Image
from run_return_fixture import ROOT,DLL,ENV
sys.path.insert(0,str(ROOT/'tools/remix_ingest'))
from live_scene import decode_mesh
from live_camera import camera_state
from analyze_live_camera import native_matrix,inverse,project

SOURCE=ROOT/'artifacts/m1/runs/20261016-223535-enabled/LIVE-SCENE-001-asset-2.bin'
EXE=ROOT/'artifacts/remix-runtime/bin/output_probe.exe'
CORE_QUALIFIED=('owner_coverage_qualified','normalized_depth_qualified','background_sentinel_qualified','native_gpu_transfer_exact','native_shader_id_decode_exact')
QUALIFIED=CORE_QUALIFIED+('historical_camera_projection_qualified',)
def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest().upper()

def prepare_mesh(source,output):
    source=Path(source)
    if source.stat().st_size>2*1024*1024 or source.with_suffix('.json').stat().st_size>256*1024:raise ValueError('Input packet/reference cap')
    mesh=decode_mesh(source.read_bytes(),source.with_suffix('.json').read_bytes())
    points=mesh['points'];center=[(min(p[i] for p in points)+max(p[i] for p in points))/2 for i in range(3)]
    extent=max(max(p[i] for p in points)-min(p[i] for p in points) for i in range(3))
    if not math.isfinite(extent) or extent<=0:raise ValueError('Mesh extent')
    vertices=[(*points[i],*normal,*uv) for i,normal,uv in mesh['corners']]
    payload=struct.pack('<4I4f',0x53464347,1,len(vertices),len(vertices),*center,4/extent)
    payload+=b''.join(struct.pack('<8f',*v) for v in vertices)
    if len(payload)>2*1024*1024:raise ValueError('Native mesh payload cap')
    Path(output).write_bytes(payload)
    return {'source_packet':str(source.relative_to(ROOT)),'source_sha256':digest(source),
            'source_references_sha256':digest(source.with_suffix('.json')),'model_name':mesh['refs']['model_filename'],
            'geometry_sha256':mesh['geometry_sha256'],'corner_vertices':len(vertices),'triangles':len(vertices)//3,
            'groups':mesh['groups'],'fit_center':center,'instance_scale':4/extent,
            'conversion':'Positions/normals/UVs unchanged;corners duplicated;groups recorded but default opaque material only',
            'output_sha256':digest(output)}

def prepare_camera(source,folder):
    source=Path(source);mesh=decode_mesh(source.read_bytes(),source.with_suffix('.json').read_bytes())
    updates=source.parent/'LIVE-SCENE-001-updates.jsonl'
    if updates.stat().st_size>32*1024*1024:raise ValueError('Historical camera input cap')
    row=None;revision=int(source.stem.rsplit('-',1)[1])
    with updates.open() as f:
        for line_number,line in enumerate(f,1):
            if len(line)>8192:raise ValueError('Camera line bound')
            candidate=json.loads(line)
            if len(candidate)==96 and candidate[4]==1 and candidate[1]==mesh['header'][4] and candidate[2]>=mesh['header'][6] and candidate[7]==revision and candidate[5]==mesh['header'][10] and candidate[6]==mesh['header'][12]:row=candidate;break
    if row is None:raise ValueError('No same-revision historical camera/asset association')
    state=camera_state(row,[0,0,0],mesh['used_points']);view=native_matrix(row[49:66]);p=native_matrix(row[66:83]);v=inverse(view)
    if abs(p[0][2])+abs(p[1][2])>1e-6:raise ValueError('Parameterized SDK camera cannot represent off-axis projection')
    model=native_matrix(row[8:25]);params=[v[i][3] for i in range(3)]+[v[i][0] for i in range(3)]+[v[i][1] for i in range(3)]+[-v[i][2] for i in range(3)]
    params += [math.degrees(2*math.atan(1/p[1][1])),p[1][1]/p[0][0],state['near']/100,state['far']/100]
    payload=struct.pack('<4I28f',0x43414D31,1,row[2],row[1],*[x for r in model[:3] for x in r],*params)
    (folder/'coverage-camera.bin').write_bytes(payload)
    return {'source_updates':str(updates.relative_to(ROOT)),'source_sha256':digest(updates),'line':line_number,
            'owner_epoch':row[1],'frame':row[2],'asset_capture_frame':mesh['header'][6],'asset_revision':row[7],'viewport':state['viewport'],
            'native_composed':native_matrix(row[25:42]),'composition_error_pixels':state['native_composition_pixel_error'],
            'sdk_parameters':params,'output_sha256':digest(folder/'coverage-camera.bin'),
            'conversion':'Native RH view inverse:right=col0,up=col1,forward=-col2. SDK LH camera. Preserve native units/model;no fit on replay. Rigid same-revision asset may precede pose/camera frame;in-place deformation unqualified.'}

def prepare_calibration_camera(capture,folder,snapshot,owner,native_depth):
    from present_calibration import analyze as verify_capture
    from analyze_present_calibration import native_depth_planes
    capture=Path(capture).resolve();capture.relative_to(ROOT/'artifacts/remix-runtime/runs')
    meta=json.loads((capture/'manifest.json').read_text());result=json.loads((capture/'result.json').read_text())
    verified=verify_capture(capture,meta['semantic_calibration']['scene_session'],result['target_pid'])
    if snapshot not in (0,1,2):raise ValueError('Calibration snapshot0..2 required')
    rows=verified['snapshots'][snapshot]['associations'];matches=[a for a in rows if a['owner']==owner]
    if len(matches)!=1:raise ValueError('One exact qualified owner required')
    association=matches[0];row=association['record'];source=capture/'gate'/f"LIVE-SCENE-001-asset-{row[7]}.bin"
    from depth_snapshot_analysis import read_packet
    depth_pair=read_packet(capture/f'depth-{snapshot}.bin')[0]
    mesh=decode_mesh(source.read_bytes(),source.with_suffix('.json').read_bytes())
    state=camera_state(row,[0,0,0],mesh['used_points']);view=native_matrix(row[49:66]);p=native_matrix(row[66:83]);v=inverse(view)
    if abs(p[0][2])+abs(p[1][2])>1e-6:raise ValueError('Off-axis SDK projection unsupported')
    near,far=native_depth_planes(p)
    model=native_matrix(row[8:25]);params=[v[i][3] for i in range(3)]+[v[i][0] for i in range(3)]+[v[i][1] for i in range(3)]+[-v[i][2] for i in range(3)]
    params += [math.degrees(2*math.atan(1/p[1][1])),p[1][1]/p[0][0],near if native_depth else state['near']/100,far]
    payload=struct.pack('<4I28f',0x43414D31,1,row[2],row[1],*[x for r in model[:3] for x in r],*params)
    (folder/'coverage-camera.bin').write_bytes(payload)
    return source,dict(source_capture=str(capture.relative_to(ROOT)),source_snapshot=snapshot,
        source_semantic_sha256=digest(capture/f'semantic-{snapshot}.bin'),source_depth_sha256=digest(capture/f'depth-{snapshot}.bin'),
        owner_epoch=row[1],frame=row[2],present_frame=depth_pair['present_frame'],qpc=depth_pair['qpc'],asset_capture_frame=mesh['header'][6],
        asset_revision=row[7],viewport=state['viewport'],native_composed=native_matrix(row[25:42]),native_model=model,
        composition_error_pixels=state['native_composition_pixel_error'],sdk_parameters=params,
        depth_reference='native_z',native_depth_conversion=native_depth,output_sha256=digest(folder/'coverage-camera.bin'),
        conversion='Same captured native model/XY camera;only SDK near=b/a correction enabled or deliberately disabled as negative control. No fit/geometry/appearance change.')

def expected_replay(folder,manifest=None,resolution=(256,256)):
    rw,rh=resolution
    if not 1<=rw<=1920 or not 1<=rh<=1080:raise ValueError('Oracle resolution cap')
    if manifest is None:manifest=json.loads((folder/'manifest.json').read_text())
    camera=manifest['replay_camera']
    composed=np.array(camera.get('diagnostic_offset',{}).get('native_composed',camera['native_composed']))
    x0,y0,w,h=manifest['replay_camera']['viewport'];data=(folder/'coverage-mesh.bin').read_bytes();n=struct.unpack_from('<I',data,8)[0]
    vertices=np.frombuffer(data,dtype='<f4',offset=32).reshape(n,8)[:,:3]
    clip=np.c_[vertices,np.ones(n)]@composed.T
    if np.any(clip[:,3]<=0):raise ValueError('Replay near/behind-camera clipping unqualified')
    pos=clip[:,:3]/clip[:,3,None];pos[:,0]=(pos[:,0]-x0)*rw/w;pos[:,1]=(pos[:,1]-y0)*rh/h
    if manifest['replay_camera'].get('depth_reference')!='native_z':pos[:,2]=(pos[:,2]+1)*.5
    z=np.full((rh,rw),np.inf)
    for tri in pos.reshape(-1,3,3):
        xmin=max(0,int(np.floor(tri[:,0].min())));xmax=min(rw-1,int(np.ceil(tri[:,0].max())))
        ymin=max(0,int(np.floor(tri[:,1].min())));ymax=min(rh-1,int(np.ceil(tri[:,1].max())))
        if xmax<xmin or ymax<ymin:continue
        a,b,c=tri;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-10:continue
        yy,xx=np.mgrid[ymin:ymax+1,xmin:xmax+1];xx=xx+.5;yy=yy+.5
        wa=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
        wb=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;wc=1-wa-wb
        inside=(wa>=0)&(wb>=0)&(wc>=0);depth=wa*a[2]+wb*b[2]+wc*c[2]
        region=z[ymin:ymax+1,xmin:xmax+1];np.minimum(region,np.where(inside,depth,np.inf),out=region)
    return z

def diagnostic_offset(camera,folder):
    """Translate the instance in camera-right world space, not output pixels."""
    original=np.array(camera['native_composed'],dtype=float)
    model=np.array(camera['native_model'],dtype=float)
    raw=(folder/'coverage-mesh.bin').read_bytes();n=struct.unpack_from('<I',raw,8)[0]
    points=np.frombuffer(raw,dtype='<f4',offset=32).reshape(n,8)[:,:3]
    center=(points.min(axis=0)+points.max(axis=0))*.5
    clip=np.r_[center,1]@original.T
    x0,y0,w,h=camera['viewport']
    if clip[3]<=0:raise ValueError('Offset owner behind camera')
    relative=(clip[0]/clip[3]-x0)/w
    params=camera['sdk_parameters'];right=np.array(params[3:6],dtype=float)
    forward=np.array(params[9:12],dtype=float)
    world=(model@np.r_[center,1])[:3];distance=float(np.dot(world-np.array(params[:3]),forward))
    if distance<=0 or not math.isfinite(distance) or abs(np.linalg.norm(right)-1)>1e-3 or abs(np.linalg.norm(forward)-1)>1e-3 or abs(np.dot(right,forward))>1e-3:raise ValueError('Offset camera basis/depth')
    fraction=.20 if relative<.5 else -.20
    units=2*distance*math.tan(math.radians(params[12])*.5)*params[13]*fraction
    offset=np.array(right*units,dtype='<f4')
    if not np.isfinite(offset).all() or np.max(np.abs(offset))>1e6:raise ValueError('Offset bound')
    shifted=model.copy();shifted[:3,3]=np.asarray(model[:3,3]+offset,dtype='<f4')
    offset=np.asarray(shifted[:3,3]-model[:3,3],dtype='<f4')
    shifted[:3,3]=np.asarray(model[:3,3]+offset,dtype='<f4')
    composed=original@np.linalg.inv(model)@shifted
    projected=np.c_[points,np.ones(n)]@composed.T
    xy=projected[:,:2]/projected[:,3,None]
    if np.any(projected[:,3]<=0) or xy[:,0].min()<x0 or xy[:,0].max()>x0+w or xy[:,1].min()<y0 or xy[:,1].max()>y0+h:
        raise ValueError('Offset would clip ship; retain partial, do not fit or shrink')
    return dict(mode=1,world_translation=offset.tolist(),screen_fraction=fraction,
                native_composed=composed.tolist(),original_native_composed=original.tolist(),
                original_native_model=model.tolist(),rendered_native_model=shifted.tolist(),
                method='World translation along current camera right before Remix DrawInstance;original geometry/camera/pose unchanged')

def prepare_triplet_request(camera,source,folder):
    capture=ROOT/camera['source_capture'];report=json.loads((capture/'semantic.analysis.json').read_text())
    choices=[a for a in report['snapshots'][camera['source_snapshot']]['associations'] if a['owner']==camera['owner_epoch']]
    if len(choices)!=1:raise ValueError('Triplet source owner')
    r=choices[0]['record']
    def fnv(raw):
        h=14695981039346656037
        for byte in raw:h=((h^byte)*1099511628211)&0xffffffffffffffff
        return h
    meta=json.loads((capture/'manifest.json').read_text());result=json.loads((capture/'result.json').read_text())
    source_session=meta['semantic_calibration']['scene_session'][-32:]
    values=struct.pack('<8I2Q8I32s6I',0,0,0,0,r[1],r[7],r[2],29,
        fnv(struct.pack('<17I',*r[8:25])),fnv(struct.pack('<40I',*r[49:89])),
        256,256,*map(int,camera['viewport']),1,1,bytes.fromhex(digest(source)),
        *(int(source_session[i:i+8],16) for i in range(0,32,8)),result['target_pid'],0)
    offset=camera.get('diagnostic_offset',{})
    values+=struct.pack('<I3f',offset.get('mode',0),*offset.get('world_translation',[0,0,0]))
    if len(values)!=152:raise ValueError('Triplet key ABI')
    p=folder/'ship-return-request.bin';p.write_bytes(values)
    return dict(key_sha256=digest(p),owner_epoch=r[1],revision=r[7],engine_frame=r[2],object_picking_id=29,
        session='Assigned fresh GUID by producer;never borrowed from source run',asset_sha256=digest(source))

def analyze(folder):
    folder=Path(folder);rows=[]
    phases=6 if (folder/'coverage-5-depth.bin').exists() else 5
    for i in range(phases):
        planes={}
        for name in ('depth','picking','color'):
            p=folder/f'coverage-{i}-{name}.bin'
            if p.stat().st_size!=256*256*4:raise ValueError('Output plane size')
            planes[name]=np.fromfile(p,dtype='<u4').reshape(256,256)
        z=planes['depth'].view('<f4');pick=planes['picking'];pf=pick.view('<f4')
        expected=({7,11},{7,11},{11},{13,11},{23},{29})[i]
        possibilities={}
        for kind,a in (('raw_uint32',pick),('numeric_float32',pf)):
            counts={str(k):int(np.count_nonzero(a==k)) for k in (0,7,11,13,23,29)}
            # Freshness requires expected IDs and disappearance,not arbitrary
            # nonblack pixels or an API success code.
            valid=(all(counts[str(k)]>10 for k in expected) and all(counts[str(k)]==0 for k in {7,11,13,23,29}-expected)
                   and sum(counts.values())==256*256 and counts['0']>100)
            possibilities[kind]={'counts':counts,'valid':valid}
        modes=[k for k,v in possibilities.items() if v['valid']]
        mode=modes[0] if len(modes)==1 else None
        ids=pick if mode=='raw_uint32' else pf
        masks={};depth_models={}
        for owner in expected:
            mask=ids==owner if mode else np.zeros((256,256),dtype=bool)
            if mask.any():
                y,x=np.where(mask);values=z[mask];cx=float(x.mean());cy=float(y.mean())
                masks[str(owner)]={'pixels':len(x),'bbox':[int(x.min()),int(y.min()),int(x.max()),int(y.max())],
                                  'centroid':[cx,cy],'depth_range':[float(values.min()),float(values.max())],'depth_median':float(np.median(values))}
                if owner not in (23,29):
                    view_z=9 if owner==11 else (8 if i==1 else 6)
                    nx=(x+.5)/128-1;ny=1-(y+.5)/128;t=math.tan(math.radians(35))
                    radial=view_z*np.sqrt(1+(nx*t)**2+(ny*t)**2)
                    normalized=100/99.9-(.1*100/99.9)/view_z
                    depth_models[str(owner)]={k:float(np.median(np.abs(values-v))) for k,v in
                                             (('view_z',view_z),('ray_distance',radial),('d3d_normalized_z',normalized))}
        row={'phase':i,'frame':i*16+15,'expected_ids':sorted(expected),'picking_modes':possibilities,'qualified_id_mode':mode,
             'nonfinite_depth':int(np.count_nonzero(~np.isfinite(z))),
             'depth_range':[float(np.nanmin(z)),float(np.nanmax(z))],'owners':masks,'depth_model_errors':depth_models,
             'depth_background_median':float(np.median(z[ids==0])) if mode and np.any(ids==0) else None,
             'background_mismatches':int(np.count_nonzero(z[ids==0]!=-1234)) if mode else None,
             'owner_depth_out_of_range':int(np.count_nonzero((z[ids!=0]<0)|(z[ids!=0]>1))) if mode else None}
        rgba=np.frombuffer(planes['color'].tobytes(),dtype=np.uint8).reshape(256,256,4)
        Image.fromarray(rgba[:,:,[2,1,0]]).save(folder/f'coverage-{i}-color.png')
        if mode:Image.fromarray((np.isin(ids,list(expected))*255).astype(np.uint8)).save(folder/f'coverage-{i}-mask.png')
        rows.append(row)
    complete=all(r['qualified_id_mode'] and not r['nonfinite_depth'] for r in rows)
    normalized=bool(complete and all(row['owner_depth_out_of_range']==0 for row in rows) and all(err['d3d_normalized_z']<2e-5 for row in rows[:4] for err in row['depth_model_errors'].values()))
    background=bool(complete and all(row['background_mismatches']==0 for row in rows))
    logfile=folder/'stdout.log';text=logfile.read_text(errors='replace') if logfile.exists() else ''
    transfer={(int(line.split()[1].split('=')[1]),line.split()[2].split('=')[1]) for line in text.splitlines() if line.startswith('COVERAGE_NATIVE_GPU_EXACT ')}
    gpu=transfer=={(i,name) for i in range(phases) for name in ('depth','picking','color')}
    decoder={int(line.split('phase=')[1]) for line in text.splitlines() if line.startswith('COVERAGE_SHADER_ID_EXACT ')}
    result={'probe':'REMIX-COVERAGE-001','owner_coverage_qualified':bool(complete),'normalized_depth_qualified':normalized,
            'background_sentinel_qualified':background,'native_gpu_transfer_exact':gpu,'native_shader_id_decode_exact':decoder==set(range(phases)),
            'phases':rows,'note':'Controlled standalone normalized depth and opaque geometry coverage;not SFC frame correspondence or textured replacement.'}
    result['historical_camera_projection_qualified']=False
    result['same_frame_native_depth_projection_qualified']=False
    result['diagnostic_offset_projection_qualified']=False
    if phases==6:
        theoretical=expected_replay(folder);actual=np.fromfile(folder/'coverage-5-picking.bin',dtype='<u4').reshape(256,256)==29
        predicted=np.isfinite(theoretical);common=actual&predicted;union=actual|predicted
        rawdepth=np.fromfile(folder/'coverage-5-depth.bin',dtype='<f4').reshape(256,256)
        result['historical_camera_replay']={'source_frame':json.loads((folder/'manifest.json').read_text())['replay_camera']['frame'],
            'intersection_pixels':int(common.sum()),'union_pixels':int(union.sum()),'mask_iou':float(common.sum()/max(1,union.sum())),
            'depth_median_error':float(np.median(np.abs(rawdepth[common]-theoretical[common]))) if common.any() else None,
            'scope':'Replay vs independently projected native composed matrix;NOT same-frame SFC GPU depth calibration'}
        replay=result['historical_camera_replay']
        qualified=bool(common.sum()>10 and replay['mask_iou']>=.95 and replay['depth_median_error']<1e-5)
        source_camera=json.loads((folder/'manifest.json').read_text())['replay_camera']
        calibration=source_camera.get('depth_reference')=='native_z'
        if calibration:
            offset=bool(source_camera.get('diagnostic_offset'))
            replay['scope']=('World-offset Remix output vs independently shifted native composition;NOT original SFC GPU depth.' if offset else 'Actual Remix output vs native composed projection for contemporaneous SFC capture;different pixel grid from original native depth. No per-sample equality claim.')
            result['diagnostic_offset_projection_qualified' if offset else 'same_frame_native_depth_projection_qualified']=qualified
            result['calibration_camera_replay']=result.pop('historical_camera_replay')
        else:result['historical_camera_projection_qualified']=qualified
    (folder/'coverage.analysis.json').write_text(json.dumps(result,indent=2,allow_nan=False));return result

def main():
    parser=argparse.ArgumentParser();mode=parser.add_mutually_exclusive_group();mode.add_argument('--execute',action='store_true');mode.add_argument('--analyze',type=Path);mode.add_argument('--archive',type=Path,nargs='+')
    parser.add_argument('--calibration-run',type=Path);parser.add_argument('--snapshot',type=int,choices=(0,1,2),default=0)
    parser.add_argument('--owner',type=int,default=2);parser.add_argument('--native-depth',action='store_true')
    parser.add_argument('--triplet',action='store_true');parser.add_argument('--triplet-fault',choices=('slow','exit'))
    parser.add_argument('--diagnostic-offset',action='store_true',help='World-space offset of returned ship only;offline prerequisite')
    args=parser.parse_args()
    if args.native_depth and not args.calibration_run:parser.error('--native-depth requires --calibration-run')
    if args.triplet and not (args.native_depth and args.calibration_run):parser.error('--triplet requires corrected --native-depth and --calibration-run')
    if args.triplet_fault and not args.triplet:parser.error('--triplet-fault requires --triplet')
    if args.diagnostic_offset and not args.triplet:parser.error('--diagnostic-offset requires --triplet')
    if args.archive:
        print(json.dumps(archive(args.archive),indent=2));return
    if args.analyze:print(json.dumps(analyze(args.analyze),indent=2));return
    if not args.execute:print('Offline-only probe;use --execute to run owned SDK host,not SFC.');return
    executable=ROOT/'artifacts/remix-runtime/triplet-bin/output_probe.exe' if args.triplet else EXE
    if digest(DLL)!='F7C310821AA98BCDFDEC120330B0A89457B7C5EBA58D21464AF32639611C809F':raise ValueError('Pinned runtime mismatch')
    if digest(ROOT/'artifacts/remix-runtime/deps/include/remix/remix_c.h')!='E623E4956A76894EEEF02361334C7C0458D4EC8BF49F729EC9038C36128BBF47':raise ValueError('Pinned header mismatch')
    from broad_capture import storage_bytes,OVERALL
    if storage_bytes()+64*1024*1024>OVERALL:raise ValueError('Overall output allowance exhausted')
    folder=ROOT/'artifacts/remix-runtime/runs'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f-coverage');folder.mkdir()
    source=SOURCE
    if args.calibration_run:source,camera=prepare_calibration_camera(args.calibration_run,folder,args.snapshot,args.owner,args.native_depth)
    else:camera=prepare_camera(source,folder)
    manifest={'probe':'REMIX-COVERAGE-001','mesh':prepare_mesh(source,folder/'coverage-mesh.bin'),'replay_camera':camera,
              'runtime_sha256':digest(DLL),'exe_sha256':digest(executable),'limits':{'seconds':120,'bytes':32*1024*1024,'frames':96,'output_surfaces':4},
              'environment':ENV,'sfc_launched':False,'camera':{'forward':[0,0,1],'fovY':70,'aspect':1,'near':.1,'far':100}}
    if args.diagnostic_offset:camera['diagnostic_offset']=diagnostic_offset(camera,folder)
    if args.triplet:
        manifest['probe']='REMIX-OFFSET-001' if args.diagnostic_offset else 'REMIX-TRIPLET-001'
        manifest['triplet']=prepare_triplet_request(camera,source,folder)
        manifest['triplet'].update(wire_version=3,wire_bytes=496,key_bytes=152,fault=args.triplet_fault,
            consumer_sha256=digest(executable.with_name('ship_triplet_consumer_x86.exe')),
            compositor_source_sha256=digest(Path(__file__).with_name('ship_triplet_compositor.h')))
    (folder/'manifest.json').write_text(json.dumps(manifest,indent=2));error=None;probe=None;start=time.monotonic();warned=False;report=None
    try:
        with (folder/'stdout.log').open('wb') as out,(folder/'stderr.log').open('wb') as err:
            env={**os.environ,**ENV,'DXVK_LOG_PATH':str(folder)};env.pop('SFC_RETURN_TRIPLET',None);env.pop('SFC_TRIPLET_FAULT',None)
            if args.triplet:env['SFC_RETURN_TRIPLET']='1'
            if args.triplet_fault:env['SFC_TRIPLET_FAULT']=args.triplet_fault
            probe=sp.Popen([str(executable),str(DLL),'coverage'],cwd=folder,env=env,stdout=out,stderr=err,creationflags=sp.CREATE_NO_WINDOW)
            while probe.poll() is None:
                total=sum(p.stat().st_size for p in folder.rglob('*') if p.is_file())
                if total>16*1024*1024 and not warned:print('Output warning16MiB',flush=True);warned=True
                if total>32*1024*1024 or time.monotonic()-start>120:raise RuntimeError('Owned probe time/output cap')
                time.sleep(.1)
            if probe.returncode:raise RuntimeError('Owned runtime probe failed;see stage log')
        report=analyze(folder)
    except Exception as exc:error=str(exc)
    finally:
        if probe and probe.poll() is None:probe.terminate();probe.wait(timeout=5)
        projection='diagnostic_offset_projection_qualified' if args.diagnostic_offset else 'same_frame_native_depth_projection_qualified'
        required=CORE_QUALIFIED+(projection,) if args.calibration_run else QUALIFIED
        passed=bool(report and all(report[k] for k in required))
        if args.triplet:
            log=(folder/'stdout.log').read_text(errors='replace')
            passed=passed and all(f'TRIPLET_X86_EXACT seq={n} ' in log for n in (1,2)) and 'TRIPLET_X86_NORMAL_EXIT packets=2 outputs=6 rejected=0' in log
        fault_observed=False
        if args.triplet_fault:
            log=(folder/'stdout.log').read_text(errors='replace')
            fault_observed=bool(error and 'triplet child timeout/disconnect' in log and 'TRIPLET_X86_EXACT' not in log and 'TRIPLET_RELEASE published=1 ack=0 accepted=0 lease=2' in log)
        outcome=('TRIPLET_GPU_RETURN_QUALIFIED' if args.triplet else 'STANDALONE_DEPTH_COVERAGE_QUALIFIED') if passed and not error else ('EXPECTED_TRIPLET_RECEIVER_FAULT' if fault_observed else 'PARTIAL')
        (folder/'result.json').write_text(json.dumps({'error':error,'exit_code':probe.returncode if probe else None,'seconds':time.monotonic()-start,
            'sfc_launched':False,'owner_coverage_qualified':report['owner_coverage_qualified'] if report else False,
            'expected_fault':args.triplet_fault,'expected_fault_observed':fault_observed,'result':outcome},indent=2))
    print('Evidence: '+str(folder),flush=True)
    if error:raise RuntimeError(error)

def archive(runs):
    if not 1<=len(runs)<=8:raise ValueError('Select1..8 exact coverage runs')
    selected=[]
    for folder in runs:
        folder=Path(folder).resolve()
        if folder.parent!=(ROOT/'artifacts/remix-runtime/runs').resolve() or not folder.name.endswith('-coverage'):raise ValueError('Exact coverage run required')
        files=[p for p in folder.iterdir() if p.is_file() and p.suffix in ('.json','.log','.bin','.png')]
        if any(p.is_symlink() for p in files) or sum(p.stat().st_size for p in files)>32*1024*1024:raise ValueError('Coverage source bounds')
        selected.extend((p,folder.name+'/'+p.name) for p in files)
    from broad_capture import storage_bytes,OVERALL
    total=sum(p.stat().st_size for p,_ in selected)
    if storage_bytes()+total+1024*1024>OVERALL:raise ValueError('Archive coexistence allowance')
    base=ROOT/'artifacts/remix-runtime/archives';base.mkdir(exist_ok=True)
    output=base/(dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f')+'-coverage.zip')
    with zipfile.ZipFile(output,'x',zipfile.ZIP_DEFLATED,compresslevel=1) as z:
        for p,name in selected:z.write(p,name)
    with zipfile.ZipFile(output) as z:
        if z.testzip() or len(z.namelist())!=len(selected):raise ValueError('Coverage archive CRC/count')
    return {'path':str(output.relative_to(ROOT)),'sha256':digest(output),'bytes':output.stat().st_size,'entries':len(selected),'source_bytes':total,'crc_verified':True,'raw_removed':False}

if __name__=='__main__':main()

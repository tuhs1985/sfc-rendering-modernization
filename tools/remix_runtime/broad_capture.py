"""Pinned opt-in dependency, rollback and streaming metadata inspection."""
from pathlib import Path
import collections
import ctypes as C
import hashlib
import json
import struct
import shutil
import os

ROOT=Path(__file__).resolve().parents[2]
FULL=ROOT/'artifacts/remix-runtime/deps/reshade-full-6.7.1/extracted/ReShade32.dll'
FULL_SHA='A1BA732B5E31E0405CDE322CC5EC62CF972B3FBAEFBB6CBDC8A24DA00D58AE24'
OLD_SHA='E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7'
HARD=2_000_000_000
OVERALL=10_000_000_000
NAMES=('unused','device','device_end','resource','resource_end','view','view_end',
       'command','command_end','command_reset','targets','draw','indexed',
       'clear_depth','clear_color','copy','copy_texture','resolve','present',
       'viewport','pipeline','states','execute','gate')
RECORD=struct.Struct('<QQIIQQ11Q')
class Header(C.Structure):
    _fields_=[(n,C.c_uint32) for n in ('magic','version','recordBytes','headerBytes')]+[(n,C.c_int32) for n in ('status','error','reason','warning','attempts','dropped','written','queued')]+[('pid',C.c_uint32),('reserved',C.c_uint32*3)]+[(n,C.c_uint64) for n in ('frequency','startQpc','gateQpc','endQpc','fileBytes','hardBytes','warningBytes','durationMs')]
assert C.sizeof(Header)==RECORD.size==128
def digest(path):
    with open(path,'rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest().upper()
def qualified_full():
    if digest(FULL)!=FULL_SHA:raise ValueError('Full-support dependency hash mismatch')
    return FULL
def storage_bytes():
    return sum(p.stat().st_size for name in ('runs','archives')
               for p in (ROOT/'artifacts/remix-runtime'/name).rglob('*') if p.is_file())
def reserve_capture_budget():
    # Include previous runtime outputs, not just this run. Reserve worst-case ZIP
    # coexistence plus ancillary/rollback/ZIP overhead; dependencies are inputs.
    reserve=2*(HARD+32*1024*1024)+16*1024*1024
    if storage_bytes()+reserve>OVERALL:raise ValueError('10GB capture/archive allowance lacks room; analyze/archive and review exact old raw cleanup first')
    if shutil.disk_usage(ROOT).free<reserve:raise ValueError('Insufficient disk space for bounded capture plus archive')
    return reserve
def install_test_proxy(target,backup):
    target,backup=Path(target),Path(backup)
    if digest(target)!=OLD_SHA:raise ValueError('Isolated proxy baseline changed; no overwrite')
    qualified_full()
    if backup.exists():raise ValueError('Rollback file already exists; no overwrite')
    shutil.copyfile(target,backup)
    if digest(backup)!=OLD_SHA:raise ValueError('Rollback verification failed')
    atomic_copy(FULL,target,FULL_SHA)
    if digest(target)!=FULL_SHA:raise ValueError('Installed full-support proxy verification failed')
def restore_test_proxy(target,backup):
    target,backup=Path(target),Path(backup)
    if digest(backup)!=OLD_SHA:raise ValueError('Rollback hash mismatch; no restore')
    if digest(target) not in (FULL_SHA,OLD_SHA):raise ValueError('Proxy changed independently; no overwrite')
    atomic_copy(backup,target,OLD_SHA)
    if digest(target)!=OLD_SHA:raise ValueError('Proxy restoration verification failed')
def atomic_copy(source,target,expected):
    stage=target.with_name(target.name+'.sfc-broad-stage')
    if stage.exists():raise ValueError('Staged proxy already exists; review interrupted transaction')
    # Stage only beside the validated isolated target, never in accepted install.
    with stage.open('xb') as dst,Path(source).open('rb') as src:shutil.copyfileobj(src,dst)
    if digest(stage)!=expected:raise ValueError('Staged proxy verification failed; target untouched')
    os.replace(stage,target)
def header_at(address):
    h=Header.from_buffer_copy(C.string_at(address+256,128))
    validate(h)
    return {n:int(getattr(h,n)) for n,_ in Header._fields_ if n!='reserved'}
def validate(h):
    if (h.magic,h.version,h.recordBytes,h.headerBytes)!=(0x42524431,1,128,128):raise ValueError('Broad header mismatch')
    if not 256<=h.hardBytes<=HARD or not 0<h.durationMs<=10000 or not h.frequency:raise ValueError('Broad limits invalid')
def analyze(path):
    """No whole-file read. All pointer labels scoped by device and creation record."""
    path=Path(path);size=path.stat().st_size
    if size>HARD or size<128 or (size-128)%128:raise ValueError('Broad file size invalid')
    with path.open('rb') as f:
        h=Header.from_buffer_copy(f.read(128));validate(h)
        if h.fileBytes!=size or h.written!=(size-128)//128:raise ValueError('Broad incomplete file/count')
        counts=collections.Counter();resources={};views={};bindings={};depth={};unknown=0;overflow=0;previous=0;records=0
        while data:=f.read(128):
            seq,qpc,event,thread,obj,dev,*a=RECORD.unpack(data)
            if seq<=previous or event not in range(1,len(NAMES)):raise ValueError('Broad sequence/event invalid')
            previous=seq;records+=1;counts[NAMES[event]]+=1
            if event==2:
                # Device labels can also be recycled. Retire its complete live map.
                for mapping in (resources,views,bindings):
                    for key in [k for k in mapping if k[0]==dev]:del mapping[key]
            elif event==3:
                if len(resources)<65536 or (dev,obj) in resources:
                    resources[dev,obj]={'creation_sequence':seq,'type':a[0],'usage':a[1],'width_or_size':a[5],'height_or_stride':a[6],'format':a[9],'samples':a[10]}
                else:overflow+=1
            elif event==4:resources.pop((dev,obj),None)
            elif event==5:
                if len(views)<65536 or (dev,obj) in views:views[dev,obj]=(a[0],seq,a[1],a[3],resources.get((dev,a[0])))
                else:overflow+=1
            elif event==6:views.pop((dev,obj),None)
            elif event in (8,9):bindings.pop((dev,obj),None)
            elif event==10:
                if len(bindings)<4096 or (dev,obj) in bindings:bindings[dev,obj]=a[1]
                else:overflow+=1
                if a[1]:
                    v=views.get((dev,a[1]));key=(dev,a[1],v[1] if v else 0)
                    if len(depth)<4096 or key in depth:
                        row=depth.setdefault(key,{'device':dev,'view':a[1],'view_creation_sequence':key[2],'bindings':0,'draws':0,'first_qpc':qpc,'last_qpc':qpc,'view_format':v[3] if v else None,'resource':v[0] if v else None,'resource_desc':v[4] if v else None})
                        row['bindings']+=1;row['last_qpc']=qpc
                    else:overflow+=1
            elif event in (11,12) and a[0] and a[1]:
                dsv=bindings.get((dev,obj),0)
                if dsv:
                    v=views.get((dev,dsv));key=(dev,dsv,v[1] if v else 0)
                    if key in depth:depth[key]['draws']+=1
                    else:unknown+=1
        return {'header':{n:int(getattr(h,n)) for n,_ in Header._fields_ if n!='reserved'},'counts':dict(counts),'records':records,'bytes':size,'analysis_overflow':overflow,'unresolved_depth_draws':unknown,'depth_candidate_count':len(depth),'candidate_summary_truncated':len(depth)>512,'depth_candidates':sorted(depth.values(),key=lambda r:r['draws'],reverse=True)[:512],
                'coverage':'enumerated public events only; no geometry/images, shader descriptors, shader contents or exhaustive API transcript; deferred execution not reconstructed',
                'result':'PARTIAL_CAPTURE_LOSS_OR_STOP' if h.status!=3 or h.error or h.dropped or overflow or h.reason!=1 else 'BROAD_METADATA_CAPTURE_COMPLETE_DEPTH_UNQUALIFIED'}
def save_analysis(path):
    result=analyze(path);Path(path).with_suffix('.analysis.json').write_text(json.dumps(result,indent=2));return result

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('trace',type=Path)
    print(json.dumps(save_analysis(p.parse_args().trace),indent=2))

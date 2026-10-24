"""Fresh-asset preparation and native timing receipts. No game drawing."""
import ctypes as C
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess as sp
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/d3d9_proof'))
sys.path.insert(0,str(ROOT/'tools/scene_bridge'))
OFFSET=10*1024*1024
HEADER=struct.Struct('<8IQ3i7I48s')
AUDIT=struct.Struct('<4I7Q4I8s')
CAPACITY=12000
STORE_BYTES=2688+CAPACITY*AUDIT.size
MAGIC=0x314f4c53
QUALIFICATION=ROOT/'artifacts/d3d9-proof/live-owner-qualification.json'
EXE=ROOT/'artifacts/d3d9-proof/direct64-bin/d3d9_direct_host.exe'
RECEIVER=ROOT/'artifacts/d3d9-proof/receiver-bin/output_receiver.exe'
RUNTIME=ROOT/'artifacts/d3d9-intercept/deps/remix-1.5.2/.trex/d3d9.dll'
GUARD=ROOT/'artifacts/remix-ingest/bin/bounded_job.exe'
CONFIG='''rtx.enableReplacementAssets = False
rtx.enableRaytracing = True
rtx.captureInstances = True
rtx.captureEnableMultiframe = False
rtx.graphicsPreset = 4
rtx.integrateIndirectMode = 0
rtx.enableRayReconstruction = False
rtx.dlssPreset = 0
rtx.upscalerType = 0
rtx.resolutionScale = 1.0
'''


def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest().upper()


def source_hashes():
    from source_timing import source_hashes as base
    result=base()
    names=('tools/d3d9_proof/live_owner_wire.h','tools/d3d9_proof/live_owner_decode.h','tools/d3d9_proof/live_owner_input.h',
           'tools/d3d9_proof/d3d9_direct_host.cpp','tools/d3d9_proof/d3d9_replay.cpp','tools/d3d9_proof/output_producer.h',
           'tools/d3d9_proof/output_receiver.cpp','tools/d3d9_proof/output_channel.h','tools/d3d9_proof/ingress_replay.h',
           'tools/d3d9_proof/frame_ingress.h','tools/d3d9_proof/start_live_owner_timing_session.ps1',
           'tools/scene_bridge/scene_bundle.py','tools/remix_runtime/live_owner_timing.py',
           'tests/d3d9_live_owner_tests.cpp','tools/remix_runtime/qualify_live_owner.py','tests/test_live_owner_timing.py')
    result.update({p:digest(ROOT/p) for p in names});return result


def binary_hashes():
    from source_timing import BINARIES
    names=(*BINARIES,str(EXE.relative_to(ROOT)),str(RECEIVER.relative_to(ROOT)),str(RUNTIME.relative_to(ROOT)),
           str(GUARD.relative_to(ROOT)),'artifacts/m1/bin/m1_gate.dll',
           'artifacts/remix-runtime/deps/remix_c.h','artifacts/d3d9-proof/ingress-x86/live_owner_tests.exe','artifacts/d3d9-proof/ingress-x64/live_owner_tests.exe')
    return {p:digest(ROOT/p) for p in names}


def require_qualification():
    q=json.loads(QUALIFICATION.read_text())
    if q.get('result')!='OFFLINE_LIVE_OWNER_PREPARED' or q.get('sources')!=source_hashes() or q.get('binaries')!=binary_hashes():raise ValueError('Live owner offline/source/binary qualification required;no game launch')
    if digest(RUNTIME)!='F7C310821AA98BCDFDEC120330B0A89457B7C5EBA58D21464AF32639611C809F':raise ValueError('Pinned runtime changed')
    return q


def initialize(channel,persistent=False):
    words=[int(channel.name[-32:][i:i+8],16) for i in range(0,32,8)]
    h=HEADER.pack(MAGIC,2 if persistent else 1,STORE_BYTES,*words,0,0,0,0,0,*([0]*7),bytes(48))
    channel.write(OFFSET,h+bytes(STORE_BYTES-HEADER.size))


def parse_audits(raw,session,pid):
    if not HEADER.size<=len(raw)<=STORE_BYTES:raise ValueError('Live owner byte cap')
    h=HEADER.unpack_from(raw);words=tuple(int(session[-32:][i:i+8],16) for i in range(0,32,8))
    if h[0]!=MAGIC or h[1] not in (1,2) or h[2]!=STORE_BYTES or h[3:7]!=words or h[7]!=pid or not h[9] or not 0<=h[16]<=CAPACITY or len(raw)!=2688+h[16]*AUDIT.size:raise ValueError('Live owner final header/session/process/count')
    rows=[];previous=0
    for a in AUDIT.iter_unpack(raw[2688:]):
        if a[3] not in (1,2,3,4,5,6) or a[4]<previous or a[14] or any(a[15]):raise ValueError('Live owner malformed audit')
        previous=a[4]
        if a[3]==1 and (not a[0] or not a[1] or not a[2] or not a[7] or a[7]!=a[8] or a[9]!=a[10] or (a[0],a[1],a[2])!=a[11:14] or not 0<a[5]<=a[6]<=a[4]):raise ValueError('False matched audit')
        rows.append(dict(frame=a[0],owner=a[1],revision=a[2],status=a[3],present=a[4],offered=a[5],completed=a[6],input_sequence=a[7],completed_sequence=a[8],expected_hash=a[9],returned_hash=a[10],returned_frame=a[11],returned_owner=a[12],returned_revision=a[13]))
    return h,rows


class Relay:
    def __init__(self,folder,receiver,game_root,additive=False,offline_fixture=False,persistent=False,buffered=False,multi_scene=False):
        self.folder=Path(folder);self.receiver=receiver;self.root=Path(game_root);self.process=None;self.selected=None;self.error=None;self.attempted=False;self.started=time.monotonic()
        initialize(receiver.channel,persistent=persistent);self.persistent=persistent;self.buffered=buffered;self.multi_scene=multi_scene
        self.additive=additive;self.offline_fixture=offline_fixture;self.pending=None;self.lights=None;self.light_replay=None
        self.selected_model=None
        self.binding_generation=0;self.binding_pending=None;self.binding_events=[];self.bound_row=None;self.binding_requested_at=0
        self.content=None;self.content_signature=None;self.mesh_cache={};self.recovery_polled=0;self.recovery_rejected=set()
        self.service=None
        if additive and not multi_scene:
            from owner_selection import selected_model
            self.selected_model=selected_model()
            (self.folder/'offset-ship-config-accepted.toml').write_bytes((ROOT/'tools/d3d9_proof/offset_ship.toml').read_bytes())
        if additive:
            receiver.channel.write(11*1024*1024+128*1024,bytes(576))
            from light_transport import initialize as init_lights
            init_lights(receiver.channel)

    @property
    def servicing(self):return self.service is not None

    def check_service(self):
        if self.service:self.service.check()

    def start_service(self,pid):
        from recovery_service import Service
        def step():
            self.receiver.drain();self.poll(pid,from_service=True)
        self.service=Service(step)

    def poll(self,pid,from_service=False):
        if self.service and not from_service:self.service.check();return
        if self.error:raise ValueError(self.error)
        if self.lights:self.lights.poll()
        if self.pending:
            if self.offline_fixture or (self.lights and self.lights.ready):
                gpu,manifest,row,pending_pid=self.pending;self.pending=None;self.launch(gpu,manifest,row,pending_pid)
            return
        if self.process:
            if self.process.poll() is not None and not C.c_int32.from_address(self.receiver.channel.view+OFFSET+40).value:raise ValueError('Live renderer exited before source stopped')
            if self.additive and not self.offline_fixture and self.process.poll() is None:self.recover(pid)
            return
        from scene_bundle import prepare
        from live_scene import decode_mesh
        candidates=[]
        for index in range(32):
            row=self.receiver.channel.sample_owner(index)
            if not row or not row[1] or not row[2] or row[4]!=1 or not row[7] or row[48]!=1:continue
            asset=self.folder/'gate'/f'LIVE-SCENE-001-asset-{row[7]}.bin'
            if not asset.is_file() or not asset.with_suffix('.json').is_file():continue
            try:
                mesh=decode_mesh(asset.read_bytes(),asset.with_suffix('.json').read_bytes())
                if (mesh['header'][4],mesh['header'][10],mesh['header'][12])!=(row[1],row[5],row[6]):continue
                from live_camera import camera_state
                camera_state(row,[0,0,0],mesh['used_points'])
            except (ValueError,OSError):continue
            candidates.append((row,mesh))
        if self.additive and not self.multi_scene:
            from owner_selection import choose
            choice=choose(candidates,self.selected_model)
            candidates=[choice] if choice else []
        for row,mesh in candidates:
            asset=self.folder/'gate'/f'LIVE-SCENE-001-asset-{row[7]}.bin'
            if self.attempted:raise ValueError('Fresh asset preparation already attempted')
            self.attempted=True;gpu=self.folder/'gpu'
            if self.additive:
                from owner_rebind import Content
                self.content=Content(self.root);self.content_signature=self.content.signature(mesh)
            manifest=prepare(asset,gpu,self.root,live_record=row)
            from run_direct64 import resize_output
            resize_output(gpu,(1920,1080),manifest)
            (gpu/'rtx.conf').write_text(CONFIG)
            if self.additive:
                from material_binding import prepare as bind_materials
                bind_materials(gpu,self.root)
                (gpu/'rtx.conf').write_text(CONFIG.replace('rtx.enableReplacementAssets = False','rtx.enableReplacementAssets = True')+'rtx.enableReplacementMaterials = True\nrtx.enableReplacementMeshes = False\n')
                from image_controls import encode as encode_image
                from quality_controls import encode as encode_quality
                for name,encoder in [('image',encode_image),('quality',encode_quality)]:
                    raw=(ROOT/f'tools/remix_runtime/config/{name}.toml').read_bytes();(gpu/f'{name}-controls.bin').write_bytes(encoder(raw));(gpu/f'{name}-config-accepted.toml').write_bytes(raw)
                if self.offline_fixture:
                    from light_fixture import Replay
                    self.light_replay=Replay(gpu,manifest,self.receiver)
                else:
                    from live_light_binding import Binding
                    self.lights=Binding(self.folder,gpu,self.receiver,row,persistent=self.persistent)
                self.pending=(gpu,manifest,row,pid);return
            self.launch(gpu,manifest,row,pid);return

    def launch(self,gpu,manifest,row,pid):
        if self.process:raise ValueError('Live renderer already started')
        self.selected=dict(owner=row[1],revision=row[7],model=manifest['model_name'],asset_sha256=manifest['asset_sha256'],preparation_seconds=time.monotonic()-self.started)
        if self.additive:self.selected.update(selection='First qualified fresh asset,cohort scheduling anchor;not player flag' if self.multi_scene else 'Explicit known player-fixture model;not engine player flag',selected_model=self.selected_model)
        env={**os.environ,'DXVK_CONFIG_FILE':str(gpu/'rtx.conf'),'RTX_AUTOMATION_DISABLE_BLOCKING_DIALOG_BOXES':'1','RTX_CAPTURE_REMIX_CONFIGS':'0',
                 'DXVK_ENABLE_RAYTRACING':'1','DXVK_GRAPHICS_PRESET_TYPE':'4','RTX_INTEGRATE_INDIRECT_MODE':'0','DXVK_DLSS_PRESET':'0',
                 'SFC_D3D9_LIVE_TIMING':'1','SFC_D3D9_GAME_PID':str(pid),'SFC_REMIX_CALIBRATION_SCENE':self.receiver.name,
                 'SFC_D3D9_EXPECTED_MODEL':str(row[5]),'SFC_D3D9_EXPECTED_SOURCE':str(row[6]),
                 'SFC_DIRECT64_TIMING_ONLY':'1','SFC_DIRECT64_PACED_FRAMES':'0','SFC_DIRECT64_LATEST_INPUT':'0','SFC_DIRECT64_SINGLE_PRESENT':'1','SFC_DIRECT64_INJECT_LAG_MS':'0'}
        for key in ('DXVK_RTX_CAPTURE_ENABLE_ON_FRAME','DXVK_DUMP_SCREENSHOT_FRAME','DXVK_TERMINATE_APP_FRAME'):env.pop(key,None)
        if not self.offline_fixture:
            for key in ('SFC_DIRECT64_BACKBUFFER_DIAGNOSTIC','SFC_D3D9_REBIND_FIXTURE','SFC_D3D9_FIXTURE_ROWS','SFC_SYNC_FIXTURE_SHORT_LEAD'):
                env.pop(key,None) # Offline diagnostic settings must not leak into gameplay.
        for key in ('SFC_D3D9_GAME_OUTPUT','SFC_D3D9_VISUAL_SETTINGS','SFC_D3D9_LIGHT_SETTINGS'):env[key]='1' if self.additive else '0'
        env['SFC_D3D9_SYNC_BUFFER']='1' if self.buffered else '0'
        env['SFC_D3D9_MULTISCENE']='1' if self.multi_scene else '0'
        env['SFC_PIPELINE_MODE']=getattr(self,'mode','test')
        env.pop('SFC_D3D9_INITIAL_ASSET_MASK',None)
        if self.multi_scene:
            mask=sum(1<<(a['id']-1) for a in self.catalog if a.get('initial'))
            if not mask:raise ValueError('Initial material/catalog batch required')
            env['SFC_D3D9_INITIAL_ASSET_MASK']=format(mask,'x')
        env['SFC_D3D9_SHARED_LIGHTS']='1' if self.additive else '0'
        if self.additive:
            if self.content_signature is None:
                # Explicit offline fixture path also supplies a fresh local packet.
                from owner_rebind import Content
                from live_scene import decode_mesh
                packet=self.folder/'gate'/f'LIVE-SCENE-001-asset-{row[7]}.bin'
                self.content=Content(self.root);self.content_signature=self.content.signature(decode_mesh(packet.read_bytes(),packet.with_suffix('.json').read_bytes()))
            from scene_bundle import read_replay
            vertices=read_replay(gpu/'scene.bin')['vertices'];span=max(max(v[axis] for v in vertices)-min(v[axis] for v in vertices) for axis in range(3))
            from owner_selection import camera_left_offset
            if self.multi_scene:
                from multi_scene import camera_offset,CONFIG as placement_config
                self.selected['camera_offset']=camera_offset()
                self.selected['placement']='common camera-left diagnostic translation;no original suppression'
                (self.folder/'multi-ship-config-accepted.toml').write_bytes(placement_config.read_bytes())
            else:self.selected['camera_offset']=camera_left_offset(span)
            env.update(SFC_D3D9_ASSET_SHA256=manifest['asset_sha256'],SFC_D3D9_OFFSET_X=str(self.selected['camera_offset'][0]))
            from owner_rebind import initialize as init_binding,request
            self.binding_generation=1;self.bound_row=list(row)
            # Stable residency token covers fresh geometry/group/original-image content.
            # Source capture IDs are only provenance;never reusable asset identity.
            cookie=int(self.content_signature[:16],16) or 1
            init_binding(self.receiver.channel,pid);request(self.receiver.channel,1,row,cookie)
            env['SFC_D3D9_REBIND_COOKIE']=f'{cookie:x}'
        from evidence_budget import AGGREGATE_BYTES
        scratch_limit=AGGREGATE_BYTES if self.multi_scene else 128*1024*1024
        command=[str(GUARD),str(gpu),'120' if self.additive else '90',str(scratch_limit),str(2*1024*1024),str(EXE),str(gpu),str(RUNTIME),str(RECEIVER),'normal']
        if getattr(self,'prewarm_process',None):
            if self.prewarm_process.poll() is not None:raise ValueError('Prepared renderer exited before activation')
            from warm_start import activate
            activate(gpu,env,self.receiver.name)
            self.process=self.prewarm_process
        else:self.process=sp.Popen(command,env=env,creationflags=sp.CREATE_NO_WINDOW)
        print(('Multi-ship ordinary-D3D9 diagnostic: ' if self.multi_scene else 'Offset ordinary-D3D9 ship: ' if self.additive else 'Separate D3D9 renderer timing: ')+manifest['model_name']+('. Original ship stays visible;existing visual baseline.' if self.additive else '. No new picture will be displayed.'),flush=True)
        if self.additive and not self.offline_fixture:self.start_service(pid)

    def recover(self,pid):
        from owner_rebind import acknowledged,choose,request
        ack=acknowledged(self.receiver.channel)
        if self.binding_pending:
            row=self.binding_pending
            if ack!=self.binding_generation:return
            self.bound_row=row;self.binding_pending=None
            if self.lights and (self.lights.row[1],self.lights.row[7])!=(row[1],row[7]):
                self.lights.row=list(row);self.lights.ready=False;self.lights.last=0
            self.binding_events.append(dict(generation=ack,owner=row[1],revision=row[7],frame=row[2],acknowledged=True,resident_assets=True,
                acknowledgement_observed_ms=(time.monotonic()-self.binding_requested_at)*1000))
            print('Returning ship reconnected;resident geometry/textures retained.',flush=True)
        if ack!=self.binding_generation:return
        now=time.monotonic()
        if now-self.recovery_polled<.002:return
        self.recovery_polled=now
        current_frame=struct.unpack('<I',self.receiver.channel.read(OFFSET+44,4))[0]
        rows=[r for i in range(32) if (r:=self.receiver.channel.sample_owner(i)) and r[1] and r[2] and r[7] and r[48]==1 and r[4]==1 and 0<=current_frame-r[2]<=8]
        if any((r[1],r[7])==(self.bound_row[1],self.bound_row[7]) for r in rows):return
        candidates=[]
        from live_scene import decode_mesh
        for row in rows:
            key=(row[1],row[7]);asset=self.folder/'gate'/f'LIVE-SCENE-001-asset-{row[7]}.bin'
            if key not in self.mesh_cache:
                shared=getattr(self.receiver,'assets',{}).get(row[7])
                if shared is not None:self.mesh_cache[key]=shared
                elif not asset.is_file() or not asset.with_suffix('.json').is_file():continue
                try:
                    if key not in self.mesh_cache:self.mesh_cache[key]=decode_mesh(asset.read_bytes(),asset.with_suffix('.json').read_bytes())
                except (ValueError,OSError):continue
            mesh=self.mesh_cache[key]
            if (mesh['header'][4],mesh['header'][10],mesh['header'][12])!=(row[1],row[5],row[6]):continue
            candidates.append((row,mesh))
        try:choice=choose(candidates,self.selected_model,self.content,self.content_signature)
        except (ValueError,OSError) as exc:
            reason=str(exc)
            if reason not in self.recovery_rejected and len(self.recovery_rejected)<64:
                self.recovery_rejected.add(reason);self.binding_events.append(dict(rejected=reason,frame=current_frame))
            return
        if not choice:
            matching=[(r,m) for r,m in candidates if m['refs']['model_filename'].lower().replace('\\','/')==self.selected_model]
            if matching:
                reason='AMBIGUOUS_RETURN' if len(matching)>1 else 'UNSUPPORTED_RETURN_CONTENT'
                key=(reason,tuple((r[1],r[7]) for r,_ in matching))
                if key not in self.recovery_rejected and len(self.recovery_rejected)<64:
                    self.recovery_rejected.add(key);self.binding_events.append(dict(rejected=reason,frame=current_frame))
            return
        if self.binding_generation>=64:return
        row,_=choice
        # Publish qualified NEW-owner lights before worker selection changes.
        # Missing fresh observations postpone rebind,never relabel old lights.
        if self.lights and not self.lights.prepare_owner(row):return
        self.binding_generation+=1;self.binding_pending=list(row)
        self.binding_requested_at=time.monotonic()
        request(self.receiver.channel,self.binding_generation,row,int(self.content_signature[:16],16) or 1)
        self.binding_events.append(dict(generation=self.binding_generation,owner=row[1],revision=row[7],frame=row[2],requested=True))

    def stop(self):
        if self.service:
            self.service.close()
            if self.service.error:self.error=str(self.service.error)
            self.service=None
        C.c_int32.from_address(self.receiver.channel.view+OFFSET+40).value=1
        if self.process:
            try:self.process.wait(timeout=10)
            except sp.TimeoutExpired:self.process.terminate();self.process.wait(timeout=5);raise ValueError('Owned live GPU workflow failed to retire normally')
        if self.light_replay:self.light_replay.close();self.light_replay=None

    def finish(self,pid):
        self.stop();head=self.receiver.channel.read(OFFSET,HEADER.size);h=HEADER.unpack(head)
        if h[16]>CAPACITY:raise ValueError('Live audit count cap')
        raw=self.receiver.channel.read(OFFSET,2688+h[16]*AUDIT.size)
        if self.receiver.channel.read(OFFSET,HEADER.size)!=head:raise ValueError('Live owner evidence still changing')
        (self.folder/'D3D9-LIVE-TIMING-001.bin').write_bytes(raw)
        h,rows=parse_audits(raw,self.receiver.name,pid)
        pool_result=None
        if self.additive:
            pool_raw=self.receiver.channel.read(11*1024*1024+128*1024,576)
            (self.folder/'D3D9-ADDITIVE-001.pool.bin').write_bytes(pool_raw)
            fields=struct.unpack_from('<16I',pool_raw)
            expected=tuple(int(self.receiver.name[-32:][i:i+8],16) for i in range(0,32,8))
            if fields[:4]!=(0x314f4753,2,576,pid) or fields[4:8]!=expected:raise ValueError('Additive pool session/process/layout')
            stats=struct.unpack_from('<9I',pool_raw,512)
            pool_result=dict(published=fields[12],overwritten=fields[13],busy=fields[14],error=fields[15],
                             **dict(zip(('drawn','stale','invalid','not_ready','retired','gpu_busy','resource_failed','depth_missing','last_frame'),stats)),
                             asset_sha256=pool_raw[64:96].hex(),camera_offset=list(struct.unpack_from('<3f',pool_raw,96)),
                             lights=self.lights.summary() if self.lights else 'OFFLINE_REPLAY_ONLY')
            pool_result.update(lease_worker_releases=struct.unpack_from('<I',pool_raw,112)[0],retain_ready=bool(struct.unpack_from('<I',pool_raw,124)[0]))
            if self.buffered:
                from synchronized_buffer import save
                pool_result['synchronized_buffer']=save(self.receiver.channel,self.folder,pid)
            if pool_result['asset_sha256']!=self.selected['asset_sha256']:raise ValueError('Additive asset identity changed')
        if not self.process:raise ValueError('No fresh qualified live asset/renderer')
        gpu=self.folder/'gpu';job=json.loads((gpu/'job-result.json').read_text());log=(gpu/'job-console.log').read_text()
        if self.process.returncode or job['exit_code'] or job['stop_reason'] or job['remaining_owned_processes'] or 'OUTPUT_API_SHUTDOWN 0' not in log:raise ValueError('Live GPU cleanup failed')
        match=re.search(r'LIVE_OWNER_COMPLETE received=(\d+) invalid=(\d+) unqualified=(\d+) game_drawing=0',log)
        if not match:raise ValueError('No live owner completion receipt')
        counts=list(map(int,match.groups()));states={str(k):sum(r['status']==k for r in rows) for k in range(1,7)}
        report=dict(probe='D3D9-LIVE-TIMING-001',selected=self.selected,received=counts[0],invalid=counts[1],unqualified=counts[2],status_counts=states,audits=len(rows),published=h[13],replaced=h[14],source_rejected=h[15],audit_dropped=h[17],completion_invalid=h[18],normal_owned_exit=True,backbuffer_drawing=False,
                    source_sha256=hashlib.sha256(raw).hexdigest(),scope='Exact immutable owner publication/current Present identity and GPU receiver ACK;no game image or complete-scene seal')
        report['result']='LIVE_TIMING_OBSERVED_ADJUDICATION_REQUIRED' if counts[0] and rows and not any((counts[1],h[15],h[17],h[18])) else 'PARTIAL'
        if self.additive:
            report.update(game_output=pool_result,backbuffer_drawing=True,scope='Diagnostic offset one-owner ordinary-D3D9 output;exact current source identity;no stale hold or original suppression')
            if self.buffered:report['scope']='One adjacent complete native game-frame/HUD and matching ship/depth paired;see separate buffered correspondence audit,not current-Present audit for display matching'
            report['owner_bindings']=self.binding_events
            from owner_rebind import OFFSET as BIND_OFFSET,MAGIC as BIND_MAGIC,TARGET
            binding=self.receiver.channel.read(BIND_OFFSET,128)
            (self.folder/'D3D9-OWNER-REBIND-001.bin').write_bytes(binding)
            header=struct.unpack_from('<8I',binding)
            if header!=(BIND_MAGIC,1,128,*expected,pid):raise ValueError('Final rebind control identity mismatch')
            target=TARGET.unpack_from(binding,64);ack,rejected=struct.unpack_from('<2I',binding,104)
            report['binding_control']=dict(generation=target[0],owner=target[1],revision=target[2],acknowledged=ack,rejected=rejected,
                content_sha256=self.content_signature,initial_asset_retained=True)
            report['recovery_service_error']=self.error
            admission=re.search(r'LIVE_ADMISSION expired=(\d+) old_epoch=(\d+) maximum_age_us=(\d+)',log)
            if not admission or 'SHARED_LIGHTS active=1 per_frame_file_reads=0' not in log:
                raise ValueError('Fast recovery light/admission receipt missing')
            report['input_admission']=dict(expired=int(admission[1]),old_epoch=int(admission[2]),maximum_age_us=int(admission[3]))
            stage_rows=re.findall(r'LIVE_ADMISSION_STAGE stage=(\d+) reason0=(\d+) reason1=(\d+) reason2=(\d+) reason3=(\d+) reason4=(\d+) reason5=(\d+)',log)
            report['input_admission']['stages']=[dict(stage=int(s),**dict(zip(('accepted','clock','frame','bad_frame','age','closed'),map(int,values)))) for s,*values in stage_rows]
            report['input_admission']['policy']='Actual compositor closed-scene watermark,current/adjacent frame,50ms age guard' if self.multi_scene else 'Legacy2ms current-frame admission'
            report['shared_light_delivery']=True
            summary=re.search(r'LIVE_OUTPUT_SUMMARY outputs=(\d+) light_omitted=(\d+)',log)
            if not summary:raise ValueError('Additive output/omission accounting missing')
            report.update(output_transfers=int(summary[1]),light_omitted=int(summary[2]))
            report['result']='OFFSET_SHIP_SUBMITTED_REVIEW_REQUIRED' if pool_result['drawn'] and not any(pool_result[k] for k in ('invalid','error','resource_failed')) else 'PARTIAL'
            if ack!=target[0] or rejected or self.recovery_rejected or self.error:report['result']='PARTIAL'
        (self.folder/'live-owner.analysis.json').write_text(json.dumps(report,indent=2));return report

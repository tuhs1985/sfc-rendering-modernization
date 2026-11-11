"""Fresh-asset preparation and native timing receipts. No game drawing."""
import ctypes as C
import hashlib
import json
import os
from pathlib import Path
from scene_capacity import OWNERS,ASSETS
import re
import struct
import subprocess as sp
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
from runtime_context import CONTEXT
sys.path.insert(0,str(ROOT/'tools/d3d9_proof'))
sys.path.insert(0,str(ROOT/'tools/scene_bridge'))
OFFSET=10*1024*1024
HEADER=struct.Struct('<8IQ3i7I48s')
AUDIT=struct.Struct('<4I7Q4I8s')
CAPACITY=12000
STORE_BYTES=2688+CAPACITY*AUDIT.size
MAGIC=0x314f4c53
QUALIFICATION=CONTEXT.artifact('d3d9-proof/live-owner-qualification.json')
EXE=CONTEXT.artifact('d3d9-proof/direct64-bin/d3d9_direct_host.exe')
RECEIVER=CONTEXT.artifact('d3d9-proof/receiver-bin/output_receiver.exe')
RUNTIME=CONTEXT.artifact('d3d9-intercept/deps/remix-1.5.2/.trex/d3d9.dll')
GUARD=CONTEXT.artifact('remix-ingest/bin/bounded_job.exe')
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








def initialize(channel,persistent=False):
    words=[int(channel.name[-32:][i:i+8],16) for i in range(0,32,8)]
    h=HEADER.pack(MAGIC,2 if persistent else 1,STORE_BYTES,*words,0,0,0,0,0,*([0]*7),bytes(48))
    channel.write(OFFSET,h+bytes(STORE_BYTES-HEADER.size))




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
        for index in range(OWNERS):
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
                from image_controls import encode_current as encode_image
                from quality_controls import encode as encode_quality
                for name,encoder in [('image',encode_image),('quality',encode_quality)]:
                    raw=(CONTEXT.setting('rendering.toml')).read_bytes();(gpu/f'{name}-controls.bin').write_bytes(encoder(raw));(gpu/f'{name}-config-accepted.toml').write_bytes(raw)
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
        if getattr(self,'player_replacement',False):self.selected.update(selection='Unique configured player-fixture model;not an engine player flag',selected_model=self.replacement_model)
        env={**os.environ,'DXVK_CONFIG_FILE':str(gpu/'rtx.conf'),'RTX_AUTOMATION_DISABLE_BLOCKING_DIALOG_BOXES':'1','RTX_CAPTURE_REMIX_CONFIGS':'0',
                 'DXVK_ENABLE_RAYTRACING':'1','DXVK_GRAPHICS_PRESET_TYPE':'4','RTX_INTEGRATE_INDIRECT_MODE':'0','DXVK_DLSS_PRESET':'0',
                 'SFC_D3D9_LIVE_TIMING':'1','SFC_D3D9_GAME_PID':str(pid),'SFC_REMIX_CALIBRATION_SCENE':self.receiver.name,
                 'SFC_D3D9_EXPECTED_MODEL':str(row[5]),'SFC_D3D9_EXPECTED_SOURCE':str(row[6]),
                 'SFC_DIRECT64_TIMING_ONLY':'1','SFC_DIRECT64_PACED_FRAMES':'0','SFC_DIRECT64_LATEST_INPUT':'0','SFC_DIRECT64_SINGLE_PRESENT':'1','SFC_DIRECT64_INJECT_LAG_MS':'0'}
        env['SFC_D3D9_LEGACY_STARTUP_WARMUP']='1' if getattr(self,'legacy_startup_warmup',False) else '0'
        for key in ('DXVK_RTX_CAPTURE_ENABLE_ON_FRAME','DXVK_DUMP_SCREENSHOT_FRAME','DXVK_TERMINATE_APP_FRAME'):env.pop(key,None)
        if not self.offline_fixture:
            for key in ('SFC_DIRECT64_BACKBUFFER_DIAGNOSTIC','SFC_D3D9_REBIND_FIXTURE','SFC_D3D9_FIXTURE_ROWS','SFC_SYNC_FIXTURE_SHORT_LEAD'):
                env.pop(key,None) # Offline diagnostic settings must not leak into gameplay.
        for key in ('SFC_D3D9_GAME_OUTPUT','SFC_D3D9_VISUAL_SETTINGS','SFC_D3D9_LIGHT_SETTINGS'):env[key]='1' if self.additive else '0'
        env['SFC_D3D9_SYNC_BUFFER']='1' if self.buffered else '0'
        env['SFC_D3D9_MULTISCENE']='1' if self.multi_scene else '0'
        env['SFC_PIPELINE_MODE']=getattr(self,'mode','test')
        env['SFC_D3D9_ADMISSION_SERVICE']='1' if getattr(self,'admission_service',False) else '0'
        env['SFC_D3D9_INITIAL_TEXTURE_DATA']='1' if getattr(self,'initial_texture_data',False) else '0'
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
            if self.multi_scene:
                if getattr(self,'player_replacement',False) or getattr(self,'native_all_ships',False):self.selected['camera_offset']=[0,0,0]
                else:
                    from multi_scene import camera_offset,CONFIG as placement_config
                    self.selected['camera_offset']=camera_offset()
                    (self.folder/'multi-ship-config-accepted.toml').write_bytes(placement_config.read_bytes())
                self.selected['placement']='common camera-left diagnostic translation;no original suppression'
                if getattr(self,'player_replacement',False):self.selected['placement']='Zero-offset player replacement with complete-frame transaction'
                if getattr(self,'native_all_ships',False):self.selected['placement']='Zero-offset retained ships;owner-specific native insertion from one verified scene output'
            else:
                from owner_selection import camera_left_offset
                self.selected['camera_offset']=camera_left_offset(span)
            env.update(SFC_D3D9_ASSET_SHA256=manifest['asset_sha256'],SFC_D3D9_OFFSET_X=str(self.selected['camera_offset'][0]))
            env['SFC_D3D9_PLAYER_REPLACEMENT']='1' if getattr(self,'player_replacement',False) or getattr(self,'native_all_ships',False) else '0'
            env['SFC_NATIVE_INSERTION_ALL_SHIPS']='1' if getattr(self,'native_all_ships',False) else '0'
            from owner_rebind import initialize as init_binding,request
            self.binding_generation=1;self.bound_row=list(row)
            # Stable residency token covers fresh geometry/group/original-image content.
            # Source capture IDs are only provenance;never reusable asset identity.
            cookie=int(self.content_signature[:16],16) or 1
            init_binding(self.receiver.channel,pid);request(self.receiver.channel,1,row,cookie)
            env['SFC_D3D9_REBIND_COOKIE']=f'{cookie:x}'
        if CONTEXT.release:scratch_limit=0
        else:
            from evidence_budget import AGGREGATE_BYTES
            scratch_limit=AGGREGATE_BYTES if self.multi_scene else 128*1024*1024
        backend=getattr(self,'renderer_backend',None)
        renderer_exe,renderer_runtime=(backend['exe'],backend['runtime']) if backend else (EXE,RUNTIME)
        if backend and not getattr(self,'prewarm_process',None):raise ValueError('Async material checkout requires its prepared renderer')
        command=[str(GUARD),str(gpu),'120' if self.additive else '90',str(scratch_limit),str(2*1024*1024),str(renderer_exe),str(gpu),str(renderer_runtime),str(RECEIVER),'normal']
        if getattr(self,'prewarm_process',None):
            if self.prewarm_process.poll() is not None:raise ValueError('Prepared renderer exited before activation')
            from warm_start import activate
            activate(self.receiver.channel,env,self.receiver.name)
            self.process=self.prewarm_process
        else:self.process=sp.Popen(command,env=env,creationflags=sp.CREATE_NO_WINDOW)
        print(('Native supported-ship replacement: ' if getattr(self,'native_all_ships',False) else 'Transactional player replacement: ' if getattr(self,'player_replacement',False) else 'Multi-ship ordinary-D3D9 diagnostic: ' if self.multi_scene else 'Offset ordinary-D3D9 ship: ' if self.additive else 'Separate D3D9 renderer timing: ')+manifest['model_name']+('. Original drawing remains until matching output authorizes each ship.' if getattr(self,'native_all_ships',False) else '. Original drawing remains until paired output authorizes replacement.' if getattr(self,'player_replacement',False) else '. Original ship stays visible;existing visual baseline.' if self.additive else '. No new picture will be displayed.'),flush=True)
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
        rows=[r for i in getattr(self.receiver.channel,"owner_indices",lambda:range(OWNERS))() if (r:=self.receiver.channel.sample_owner(i)) and r[1] and r[2] and r[7] and r[48]==1 and r[4]==1 and 0<=current_frame-r[2]<=8]
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
        if self.binding_generation>=0x3fffffff:return
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
        return development_reports().finish_live_owner_timing(self,pid)


def development_reports():
    directory = ROOT / 'tools/renderer_diagnostics'
    if not (directory / 'renderer_reports.py').is_file():
        raise RuntimeError('Detailed renderer evidence requires development tools')
    sys.path.insert(0, str(directory))
    import renderer_reports
    return renderer_reports


def __getattr__(name):
    if name in {'source_hashes', 'binary_hashes', 'require_qualification', 'parse_audits'}:
        return getattr(development_reports(), name)
    raise AttributeError(name)

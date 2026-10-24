"""Fresh generic asset admission for one retained ordinary-D3D9 scene.

No Toolkit geometry, prepared model template, native-pointer asset identity or
per-ship renderer process. Four bounded non-game workers prepare independent
assets;one coordinator publishes catalogs/materials and owns all shared state.
"""
import ctypes as C
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import time
import os

from live_owner_timing import Relay as SingleRelay,ROOT,CONFIG,OFFSET
from asset_preparation import PreparationQueue
from multi_scene_resources import Reservations
import multi_scene as wire


class Relay(SingleRelay):
    def __init__(self,*args,**kwargs):
        from pipeline_mode import validate
        self.mode=validate(kwargs.pop('pipeline_mode','test'))
        super().__init__(*args,**kwargs,multi_scene=True)
        if not self.additive or not self.persistent or not self.buffered:
            raise ValueError('Multi-scene requires persistent synchronized additive path')
        wire.initialize(self.receiver.channel)
        self.catalog=[];self.resident={};self.attempts=set()
        from owner_rebind import Content
        self.content=Content(self.root)
        self.output_reservations=Reservations()
        self.preparer=PreparationQueue(self.identify_asset,self.prepare_asset)
        self.initial_ids=None;self.first_discovery=None;self.last_discovery=None
        self.initial_context=None;self.renderer_started_ns=None;self.initial_published_ns=None
        self.published_paths=set();self.stopping=False
        self.material_config=(ROOT/'tools/remix_runtime/config/materials.toml').read_bytes()
        self.material_keys={};self.layers=[];self.image_bytes=0;self.original_images=set();self.partial=[];self.anchor_missing=0
        self.frame_log=(self.folder/'D3D9-MULTISCENE-001.frames.bin').open('wb') if self.mode=='test' else None
        self.frame_samples=0;self.frame_sample_dropped=0;self.last_sample=0;self.sample_identity=None
        self.material_events=[]
        self.isolate_late_material_reload=False
        self.isolate_initial_material_library=False
        self.loading_policy='inherit'
        self.loading_receipt=None
        self.candidate_release=None;self.candidate_asset_loading='inherit'
        self.material_library='layers'
        self.material_texture_loading='preload'
        self.native_log_level='inherit'
        self.api_texture_prefetch=False
        self.overlap_texture_prefetch=False;self.prefetch_requests=0
        self.prewarm_process=None;self.prewarm_started_ns=None;self.renderer_activation_ns=None

    def start_on_launch(self,pid):
        """Start the real renderer/device, without a ship or dummy scene template."""
        if self.prewarm_process or self.process:return
        from live_owner_timing import EXE,RUNTIME,RECEIVER,GUARD
        from evidence_budget import AGGREGATE_BYTES
        from multi_scene import camera_offset
        gpu=self.folder/'gpu';gpu.mkdir(exist_ok=True)
        # Do not ingest an empty library and immediately reload it. The native
        # host enables replacement assets only after the complete activation.
        (gpu/'rtx.conf').write_text(CONFIG+'rtx.enableReplacementMaterials = True\nrtx.enableReplacementMeshes = False\n')
        from image_controls import encode as image
        from quality_controls import encode as quality
        for name,encoder in (('image',image),('quality',quality)):
            raw=(ROOT/f'tools/remix_runtime/config/{name}.toml').read_bytes()
            (gpu/f'{name}-controls.bin').write_bytes(encoder(raw));(gpu/f'{name}-config-accepted.toml').write_bytes(raw)
        library=gpu/'rtx-remix/mods/sfc-policy/mod.usda';library.parent.mkdir(parents=True,exist_ok=True)
        library.write_text('#usda 1.0\n(defaultPrim = "RootNode")\ndef Xform "RootNode" {}\n')
        env={**os.environ,'DXVK_CONFIG_FILE':str(gpu/'rtx.conf'),'RTX_AUTOMATION_DISABLE_BLOCKING_DIALOG_BOXES':'1',
             'RTX_CAPTURE_REMIX_CONFIGS':'0','DXVK_ENABLE_RAYTRACING':'1','DXVK_GRAPHICS_PRESET_TYPE':'4',
             'RTX_INTEGRATE_INDIRECT_MODE':'0','DXVK_DLSS_PRESET':'0','SFC_D3D9_LIVE_TIMING':'1',
             'SFC_D3D9_GAME_PID':str(pid),'SFC_REMIX_CALIBRATION_SCENE':self.receiver.name,
             'SFC_DIRECT64_TIMING_ONLY':'1','SFC_DIRECT64_PACED_FRAMES':'0','SFC_DIRECT64_LATEST_INPUT':'0',
             'SFC_DIRECT64_SINGLE_PRESENT':'1','SFC_DIRECT64_INJECT_LAG_MS':'0','SFC_D3D9_PREWARM':'1',
             'SFC_D3D9_GAME_OUTPUT':'1','SFC_D3D9_VISUAL_SETTINGS':'1','SFC_D3D9_LIGHT_SETTINGS':'1',
             'SFC_D3D9_SHARED_LIGHTS':'1','SFC_D3D9_SYNC_BUFFER':'1','SFC_D3D9_MULTISCENE':'1',
             'SFC_PIPELINE_MODE':self.mode,'SFC_D3D9_OFFSET_X':str(camera_offset()[0])}
        for key in ('SFC_D3D9_INITIAL_ASSET_MASK','SFC_D3D9_REBIND_COOKIE','SFC_D3D9_EXPECTED_MODEL',
                    'SFC_D3D9_EXPECTED_SOURCE','SFC_D3D9_ASSET_SHA256','DXVK_RTX_CAPTURE_ENABLE_ON_FRAME',
                    'DXVK_DUMP_SCREENSHOT_FRAME','DXVK_TERMINATE_APP_FRAME','SFC_DIRECT64_BACKBUFFER_DIAGNOSTIC'):
            env.pop(key,None)
        if not self.offline_fixture:env.pop('SFC_D3D9_RENDER_PREWARM',None)
        env.pop('SFC_D3D9_API_PREFETCH',None)
        env.pop('SFC_D3D9_API_PREFETCH_OVERLAP',None)
        if self.api_texture_prefetch:
            if not self.offline_fixture:raise ValueError('Public API texture prefetch experiment is offline only')
            env['SFC_D3D9_API_PREFETCH']='1'
            if self.overlap_texture_prefetch:env['SFC_D3D9_API_PREFETCH_OVERLAP']='1'
        from loading_policy import configure
        extra,self.loading_receipt=configure(self.loading_policy,env,offline=self.offline_fixture)
        if self.candidate_asset_loading!='inherit':
            if self.loading_policy!='inherit':raise ValueError('Candidate initialization excludes other loading overrides')
            from runtime_candidate import configure_initialization
            candidate_extra,candidate_policy=configure_initialization(
                self.candidate_asset_loading,env,offline=self.offline_fixture,release=self.candidate_release)
            extra+=candidate_extra
            self.loading_receipt['candidate_initialization']=candidate_policy
        if self.native_log_level!='inherit':
            if not self.offline_fixture or self.native_log_level!='error':raise ValueError('Native logging experiment is offline only')
            env['DXVK_LOG_LEVEL']='error'
        self.loading_receipt['native_log_level']=env.get('DXVK_LOG_LEVEL')
        if extra:
            with (gpu/'rtx.conf').open('a') as config:config.write(extra)
        (gpu/'loading-inputs.json').write_text(json.dumps(self.loading_receipt,indent=2))
        self.prewarm_started_ns=time.perf_counter_ns();self.renderer_started_ns=self.prewarm_started_ns
        self.prewarm_process=subprocess.Popen([str(GUARD),str(gpu),'285',str(AGGREGATE_BYTES),str(2*1024*1024),str(EXE),str(gpu),str(RUNTIME),str(RECEIVER),'normal'],env=env,creationflags=subprocess.CREATE_NO_WINDOW)

    def poll(self,pid,from_service=False):
        if self.service and not from_service:self.service.check();return
        if self.stopping:return
        if self.error:raise ValueError(self.error)
        if self.prewarm_process and not self.process and self.prewarm_process.poll() is not None:
            raise ValueError('Early renderer exited before scene activation;original game retained')
        if self.lights:self.lights.poll()
        if self.process and self.process.poll() is not None:
            if not C.c_int32.from_address(self.receiver.channel.view+OFFSET+40).value:raise ValueError('Live renderer exited before source stopped')
            return
        rows=self.current_rows()
        self.discover(rows)
        self.collect_prepared()
        if not self.process:
            now=time.monotonic()
            if self.first_discovery is None:return
            if self.initial_ids is None and ((now-self.first_discovery>=.75 and now-self.last_discovery>=.2) or now-self.first_discovery>=2):
                self.initial_ids=set(self.preparer.jobs)
            if now-self.first_discovery>25:raise ValueError('Initial asset batch25s preparation watchdog;original game retained')
            if self.initial_ids is None or not self.preparer.settled(self.initial_ids):return
            if self.initial_context is None:self.prepare_initial_context(pid)
            if self.lights and not self.lights.ready:return
            self.publish_prepared(initial=True)
            gpu,manifest,row=self.initial_context
            self.content_signature=self.preparer.jobs[1]['signature']
            self.renderer_activation_ns=time.perf_counter_ns()
            if self.renderer_started_ns is None:self.renderer_started_ns=self.renderer_activation_ns
            SingleRelay.launch(self,gpu,manifest,row,pid)
        else:
            self.publish_prepared()
            self.recover(pid)

    def current_rows(self):
        return [r for i in range(32) if (r:=self.receiver.channel.sample_owner(i)) and r[1] and r[2] and r[7] and r[4]==1 and r[48]==1]

    def discover(self,rows):
        for row in rows:
            key=row[1],row[7]
            if key in self.attempts or len(self.attempts)>=64:continue
            source=self.folder/'gate'/f'LIVE-SCENE-001-asset-{row[7]}.bin'
            if not source.is_file() or not source.with_suffix('.json').is_file():continue
            snapshot=source.parent/'run-metadata.json'
            if not snapshot.exists():
                with snapshot.open('x') as out:json.dump(dict(live_channel=self.receiver.name,scope='Immutable multi-ship capture session;full mutable runner report is in parent manifest'),out)
            elif json.loads(snapshot.read_text()).get('live_channel')!=self.receiver.name:raise ValueError('Capture metadata session mismatch')
            identity=len(self.attempts)+1;self.attempts.add(key)
            self.preparer.submit(identity,row)
            now=time.monotonic();self.last_discovery=now
            if self.first_discovery is None:self.first_discovery=now

    def identify_asset(self,row):
        from live_scene import decode_mesh
        from owner_rebind import Content
        source=self.folder/'gate'/f'LIVE-SCENE-001-asset-{row[7]}.bin'
        if source.stat().st_size>2*1024*1024 or source.with_suffix('.json').stat().st_size>256*1024:raise ValueError('Fresh source bounds')
        packet=source.read_bytes();references=source.with_suffix('.json').read_bytes()
        if self.mode=='performance':
            from mesh_checksum import calculate
            mesh=decode_mesh(packet,references,checksum=calculate)
        else:mesh=decode_mesh(packet,references)
        mesh['_capture_refs_sha256']=hashlib.sha256(references).hexdigest()
        if (mesh['header'][4],mesh['header'][10],mesh['header'][12])!=(row[1],row[5],row[6]):raise ValueError('Fresh source identity mismatch')
        content=Content(self.root);signature=content.signature(mesh)
        from scene_bundle import resolve_image
        mesh['_content_signature']=signature
        mesh['_original_images']={content.image(r['filename']):resolve_image(self.root,r['filename']).stat().st_size for r in mesh['refs']['resources']}
        return signature,mesh

    def fail_job(self,job,error):
        job.update(phase='failed',error=str(error))
        self.partial.append(dict(owner=job['row'][1],revision=job['row'][7],reason=str(error)))

    def collect_prepared(self):
        for job in self.preparer.pump():
            if job['phase']=='failed':self.fail_job(job,job['error']);continue
            try:
                gpu,manifest,signature,path_id,raw,new,facts=job['prepared']
                raw=self.prepare_catalog(gpu,manifest,job['row'],signature,job['id'],path_id,proof=raw,facts=facts)
                job.update(wire=raw,new=new,gpu=gpu,manifest=manifest)
                self.resident[signature]=(path_id,gpu,manifest,raw)
                if getattr(self,'overlap_texture_prefetch',False):
                    if not self.offline_fixture or not self.api_texture_prefetch:raise ValueError('Prefetch overlap requires offline public API mode')
                    from texture_prefetch import packet
                    root=self.folder/'gpu';library=root/'rtx-remix/mods/sfc-policy'
                    layer=os.path.relpath(gpu/'rtx-remix/mods/sfc-policy/mod.usda',library)
                    raw_pid=struct.unpack_from('<I',self.receiver.channel.read(10*1024*1024,32),28)[0]
                    data=packet(root,[layer],raw_pid,self.receiver.name)
                    self.prefetch_requests+=1
                    if self.prefetch_requests>64:raise ValueError('Prefetch request bound')
                    pending=root/f'texture-prefetch-{self.prefetch_requests}.pending';pending.write_bytes(data);pending.replace(pending.with_suffix('.bin'))
            except (ValueError,OSError,subprocess.SubprocessError) as exc:self.fail_job(job,exc)
        for job in self.preparer.jobs.values():
            if job['phase']!='alias' or 'wire' in job:continue
            canonical=self.preparer.jobs[job['canonical']]
            if canonical['phase']=='failed':self.fail_job(job,'Shared asset preparation failed: '+canonical['error']);continue
            if 'wire' not in canonical:continue
            fields=list(wire.ASSET.unpack(canonical['wire']));row=job['row']
            fields[:6]=[job['id'],fields[1],row[1],row[7],row[5],row[6]]
            raw=wire.ASSET.pack(*fields);raw=raw[:-8]+struct.pack('<Q',wire.fnv(raw[:-8]))
            job.update(wire=raw,new=False,gpu=canonical['gpu'],manifest=canonical['manifest'])

    def prepare_initial_context(self,pid):
        first=self.preparer.jobs[1]
        if 'wire' not in first:raise ValueError('Initial anchor asset unsupported;original game retained')
        source=first['gpu'];gpu=self.folder/'gpu';manifest=first['manifest'];row=first['row']
        # Same-volume links reuse finalized immutable bootstrap bytes. The first
        # asset's material stage stays separate from the master library.
        for name in ('scene.bin','scene.json','material-binding.json','materials-config-accepted.toml',
                     *(f'texture-{i}.bin' for i in range(len(manifest['textures'])))):
            origin=source/name
            if origin.is_file():os.link(origin,gpu/name)
        if not self.prewarm_process:
            (gpu/'rtx.conf').write_text(CONFIG.replace('rtx.enableReplacementAssets = False','rtx.enableReplacementAssets = True')+'rtx.enableReplacementMaterials = True\nrtx.enableReplacementMeshes = False\n')
        from image_controls import encode as encode_image
        from quality_controls import encode as encode_quality
        for name,encoder in [('image',encode_image),('quality',encode_quality)]:
            raw=(ROOT/f'tools/remix_runtime/config/{name}.toml').read_bytes()
            if self.prewarm_process and (gpu/f'{name}-config-accepted.toml').read_bytes()!=raw:
                raise ValueError('Image/quality baseline changed during early startup;restart with one baseline')
            (gpu/f'{name}-controls.bin').write_bytes(encoder(raw));(gpu/f'{name}-config-accepted.toml').write_bytes(raw)
        if self.offline_fixture:
            from light_fixture import Replay
            self.light_replay=Replay(gpu,manifest,self.receiver)
        else:
            from live_light_binding import Binding
            self.lights=Binding(self.folder,gpu,self.receiver,row,persistent=self.persistent)
        self.initial_context=(gpu,manifest,row)

    def publish_prepared(self,initial=False):
        ready=[j for j in self.preparer.jobs.values() if 'wire' in j and not j.get('published')]
        if not ready:return
        changed=False
        for job in ready:
            path_id=wire.ASSET.unpack(job['wire'])[1]
            if job['new'] and path_id not in self.published_paths:
                self.mod_layer(job['gpu'],write=False);self.published_paths.add(path_id);changed=True
        if changed:
            if self.isolate_initial_material_library:
                if not self.offline_fixture:raise ValueError('Initial material-library isolation is offline diagnosis only')
                self.material_events.append(dict(skipped_initial_library_diagnostic_only=True,layers=len(self.layers),supervisor_monotonic_ns=time.perf_counter_ns()))
            elif self.isolate_late_material_reload and not initial:
                if not self.offline_fixture:raise ValueError('Material-reload isolation is offline diagnosis only')
                self.material_events.append(dict(skipped_diagnostic_only=True,layers=len(self.layers),supervisor_monotonic_ns=time.perf_counter_ns()))
            else:self.commit_layers(initial)
        if initial and getattr(self,'api_texture_prefetch',False):
            from texture_prefetch import packet
            gpu=self.folder/'gpu'
            # Verified PID is already frozen into the early host readiness path.
            raw_pid=struct.unpack_from('<I',self.receiver.channel.read(10*1024*1024,32),28)[0]
            raw=packet(gpu,self.layers,raw_pid,self.receiver.name)
            pending=gpu/'texture-prefetch.pending';pending.write_bytes(raw);pending.replace(gpu/'texture-prefetch.bin')
        for job in ready:
            row=job['row'];raw=job['wire'];wire.publish(self.receiver.channel,job['id'],raw);job['published']=True
            self.catalog.append(dict(id=job['id'],path_id=wire.ASSET.unpack(raw)[1],owner=row[1],revision=row[7],model=job['manifest']['model_name'],
                                     signature=job['signature'],manifest=job['manifest'],packet=raw.hex(),initial=initial,published_ns=time.perf_counter_ns()))
            print('Fresh retained ship admitted: '+job['manifest']['model_name'],flush=True)
        if initial:self.initial_published_ns=time.perf_counter_ns()

    def prepare_catalog(self,gpu,manifest,row,signature,identity,path_id,*,proof=None,facts=None):
        from scene_bundle import resolve_image
        material=facts['material'] if facts is not None else json.loads((gpu/'material-binding.json').read_text())
        if material['config_sha256']!=hashlib.sha256(self.material_config).hexdigest():
            raise ValueError('Material configuration changed during cohort preparation;restart with one baseline')
        original={}
        for group in material['groups']:
            key=group['remix_hash']
            value=(group['primary_sha256'],group['secondary_sha256'],material['config_sha256'])
            if key in self.material_keys and self.material_keys[key]!=value:
                raise ValueError('Cross-asset ordinary texture hash has conflicting material policy')
        if facts is not None:original=facts['original'];generated=facts['generated']
        else:
            source=ROOT/manifest['source_packet'];refs=json.loads(source.with_suffix('.json').read_text())
            for resource in refs['resources']:
                sha=self.content.image(resource['filename']);original[sha]=resolve_image(self.root,resource['filename']).stat().st_size
            generated=sum(p.stat().st_size for p in gpu.rglob('*') if p.is_file() and
                          (p.suffix=='.dds' or re.fullmatch(r'texture-\d+\.bin',p.name)))
        additional=generated+sum(size for sha,size in original.items() if sha not in self.original_images)
        from multi_scene_resources import require_capacity
        if facts is None:require_capacity() # Actual finalized output,not double-counted.
        raw=proof if proof is not None else wire.file_packet(identity,path_id,row,signature,gpu,len(manifest['textures']))
        for group in material['groups']:
            self.material_keys[group['remix_hash']]=(group['primary_sha256'],group['secondary_sha256'],material['config_sha256'])
        self.image_bytes+=additional;self.original_images.update(original)
        return raw

    def mod_layer(self,gpu,write=True):
        root=self.folder/'gpu/rtx-remix/mods/sfc-policy'
        stage=gpu/'rtx-remix/mods/sfc-policy/mod.usda'
        layer=os.path.relpath(stage,root).replace('\\','/')
        stage.resolve().relative_to((self.folder/'gpu').resolve())
        if layer not in self.layers:self.layers.append(layer)
        if write:self.commit_layers(False)

    def commit_layers(self,initial):
        root=self.folder/'gpu/rtx-remix/mods/sfc-policy';root.mkdir(parents=True,exist_ok=True)
        layers=self.layers
        if getattr(self,'material_texture_loading','preload')!='preload':
            if not self.offline_fixture or self.material_texture_loading!='stream' or self.material_library!='layers' or self.api_texture_prefetch:
                raise ValueError('Streaming comparison requires isolated offline layered materials without API prefetch')
            from material_library import streamed_layers
            layers,_=streamed_layers(root,layers)
        text='#usda 1.0\n(\n defaultPrim = "RootNode"\n subLayers = [\n'+',\n'.join('  @'+p+'@' for p in layers)+'\n ]\n)\n'
        if getattr(self,'material_library','layers')=='flat':
            if not self.offline_fixture:raise ValueError('Flat material experiment is offline only')
            from material_library import flat
            text,_=flat(root,self.layers)
        pending=root/'mod.usda.pending';pending.write_text(text,encoding='utf-8');pending.replace(root/'mod.usda')
        self.material_events.append(dict(layers=len(self.layers),supervisor_monotonic_ns=time.perf_counter_ns(),clock='QueryPerformanceCounter',initial=initial))

    def prepare_asset(self,row,mesh,identity):
        # Worker has no mailbox/catalog mutations and owns only its output folder.
        signature=mesh['_content_signature']
        gpu=self.folder/'gpu/assets'/str(identity)
        source=self.folder/'gate'/f'LIVE-SCENE-001-asset-{row[7]}.bin'
        from scene_bundle import prepare
        with self.output_reservations.asset(gpu):
            manifest=prepare(source,gpu,self.root,live_record=row,evidence_mode=self.mode,
                             qualified_mesh=mesh if self.mode=='performance' else None)
            from run_direct64 import resize_output
            resize_output(gpu,(1920,1080),manifest)
            from material_binding import prepare as bind
            bind(gpu,self.root,config=self.material_config,evidence_mode=self.mode)
            raw=wire.file_packet(identity,identity,row,signature,gpu,len(manifest['textures']))
            facts=dict(material=json.loads((gpu/'material-binding.json').read_text()),original=mesh['_original_images'],
                generated=sum(p.stat().st_size for p in gpu.rglob('*') if p.is_file() and
                              (p.suffix=='.dds' or re.fullmatch(r'texture-\d+\.bin',p.name))))
        return gpu,manifest,signature,identity,raw,True,facts

    def recover(self,pid):
        from owner_rebind import acknowledged,request
        snapshot=wire.frame_snapshot(self.receiver.channel,self.last_sample+60) if self.mode=='test' else None
        if snapshot:
            number,identity,raw=snapshot
            if number>=self.last_sample+60 or identity!=self.sample_identity:
                self.last_sample=number;self.sample_identity=identity
                if self.frame_samples<120:self.frame_log.write(raw);self.frame_samples+=1
                else:self.frame_sample_dropped+=1
        rows=self.current_rows()
        # Anchor is scheduling/light context only. A new anchor never authorizes
        # reuse of its old geometry;the immutable catalog qualifies every draw.
        ack=acknowledged(self.receiver.channel)
        if self.binding_pending:
            if ack!=self.binding_generation:return
            self.bound_row=self.binding_pending;self.binding_pending=None
        if ack!=self.binding_generation:return
        if any((r[1],r[7])==(self.bound_row[1],self.bound_row[7]) for r in rows):self.anchor_missing=0;return
        # A nonblocking table read can miss a cell being written. Do not change
        # scheduling/light context from one torn/in-progress diagnostic sample.
        self.anchor_missing+=1
        if self.anchor_missing<3:return
        for row in rows:
            if not any((a['owner'],a['revision'])==(row[1],row[7]) and wire.acknowledgement(self.receiver.channel,a['id'])==1 for a in self.catalog):continue
            if self.binding_generation>=64:return
            if self.lights and not self.lights.prepare_owner(row):return
            if self.light_replay:
                self.light_replay.owner=row[1]
                self.light_replay.snapshot.update(owner_epoch=row[1],model_process_local=row[5],source_process_local=row[6])
            self.binding_generation+=1;self.binding_pending=list(row)
            self.anchor_missing=0
            request(self.receiver.channel,self.binding_generation,row,int(self.content_signature[:16],16) or 1)
            self.binding_events.append(dict(generation=self.binding_generation,owner=row[1],revision=row[7],scheduling_anchor_only=True))
            break

    def stop(self):
        self.stopping=True
        try:super().stop()
        finally:
            if self.prewarm_process and not self.process:
                (self.folder/'gpu/renderer-cancel').touch()
                try:self.prewarm_process.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    self.prewarm_process.terminate();self.prewarm_process.wait(timeout=5)
                    self.error='Prewarm cancellation timed out;owned guard stopped'
            self.preparer.close()
            if self.frame_log and not self.frame_log.closed:self.frame_log.close()

    def finish(self,pid):
        report=super().finish(pid)
        ready_path=self.folder/'gpu/renderer-ready.bin';ready_qpc=ready_pid=None
        if ready_path.is_file():ready_qpc,ready_pid=struct.unpack('<2Q',ready_path.read_bytes())
        if self.preparer.report()['unfinished']:self.partial.append(dict(reason='Stopped with unpublished preparation jobs',ids=self.preparer.report()['unfinished']))
        state=wire.summary(self.receiver.channel)
        block=self.receiver.channel.read(wire.OFFSET,wire.STORE_BYTES)
        (self.folder/'D3D9-MULTISCENE-001.bin').write_bytes(block)
        for asset in self.catalog:asset['acknowledgement']=wire.acknowledgement(self.receiver.channel,asset['id'])
        log=(self.folder/'gpu/job-console.log').read_text()
        draws=[dict(owner=int(o),revision=int(r),draws=int(n)) for o,r,n in re.findall(r'MULTISCENE_OWNER owner=(\d+) revision=(\d+) draws=(\d+)',log)]
        stages=re.search(r'MULTISCENE_STAGES lookup_header=(\d+) lookup_packet=(\d+) lookup_identity=(\d+) decode=(\d+) projection=(\d+)',log)
        if not stages:raise ValueError('Multi-ship delivery-stage counters missing')
        stage_counts=dict(zip(('lookup_header','lookup_packet','lookup_identity','decode','projection'),map(int,stages.groups())))
        asset_timings=[dict(id=int(i),cpu_us=int(c),gpu_admit_us=int(g),at_us=int(t)) for i,c,g,t in re.findall(r'MULTISCENE_ASSET_TIMING id=(\d+) cpu_us=(\d+) gpu_admit_us=(\d+) at_us=(\d+)',log)]
        report['multi_scene']=dict(state=state,assets=self.catalog,draws=draws,partial=self.partial,image_bytes=self.image_bytes,
                                  pipeline_mode=self.mode,detailed_evidence=self.mode=='test',
                                  delivery_stages=stage_counts,asset_timings=asset_timings,material_events=self.material_events,
                                  preparation=self.preparer.report(),initial_ids=sorted(self.initial_ids or []),
                                  initial_published_ns=self.initial_published_ns,renderer_started_ns=self.renderer_started_ns,
                                  prewarm_started_ns=self.prewarm_started_ns,renderer_activation_ns=self.renderer_activation_ns,
                                  prewarm_ready_qpc=ready_qpc,prewarm_host_pid=ready_pid,
                                  loading_policy=self.loading_receipt,
                                  material_library=self.material_library,
                                  api_texture_prefetch=self.api_texture_prefetch,
                                  overlap_texture_prefetch=self.overlap_texture_prefetch,prefetch_requests=self.prefetch_requests,
                                  diagnostic_skip_late_material_reload=self.isolate_late_material_reload,
                                  final_store_sha256=hashlib.sha256(block).hexdigest(),frame_samples=self.frame_samples,
                                  frame_sample_dropped=self.frame_sample_dropped,frame_sample_cap=120,
                                  image_policy=__import__('multi_scene_resources').policy(),
                                  image_warning=self.image_bytes>=__import__('evidence_budget').AGGREGATE_BYTES*4//5,original_images=len(self.original_images),
                                  coverage='Union of qualified submitted set;not native per-pixel owner identity',original_suppressed=False)
        report['scope']='Retained multi-ship diagnostic with recorded common camera-left offset;originals remain;not replacement or universal coverage'
        report['result']='MULTISHIP_OVERLAY_REVIEW_REQUIRED' if len(draws)>=2 and len(self.resident)>=2 and not self.partial and not state['asset_rejected'] and report['game_output']['drawn'] else 'PARTIAL'
        (self.folder/'live-owner.analysis.json').write_text(json.dumps(report,indent=2))
        return report

"""Isolated parallel/progressive consumer; legacy gameplay remains qualified.

Native catalog remains immutable. Only supported Remix material stages change.
"""
import ctypes as C
import hashlib
import json
import os
from pathlib import Path
import struct
import time
from collections import deque

from multi_scene_relay import Relay as Baseline
from live_owner_timing import Relay as SingleRelay,OFFSET
from parallel_assets import Pipeline
import multi_scene as wire


class Relay(Baseline):
    def __init__(self,*args,**kwargs):
        experimental=kwargs.pop('experimental_live_checkout',False)
        super().__init__(*args,**kwargs)
        if not self.offline_fixture and not experimental:
            self.preparer.close()
            raise ValueError('Progressive material consumption requires explicit experimental checkout opt-in')
        self.experimental_live_checkout=experimental
        self.admission_service=True
        self.initial_texture_data=True
        self.preparer.close();self.preparer=Pipeline(self)
        self.anchor_id=None;self.path_count=0;self.material_pieces={};self.progressive_events=[];self.pending_enhancements=deque()
        self.pending_stage_ids=set();self.pending_complete_ids=set();self.pending_library=False
        self.publication_busy_since=None;self.publication_retries=0

    def start_service(self,pid):
        # The preparation coordinator starts before first asset, not after the
        # first image. SingleRelay.launch must not start a second owner thread.
        if self.service is None:SingleRelay.start_service(self,pid)

    def start_on_launch(self,pid):
        super().start_on_launch(pid)
        if self.experimental_live_checkout and not self.offline_fixture:self.start_service(pid)

    def poll(self,pid,from_service=False):
        if self.service and not from_service:self.service.check();return
        if self.stopping:return
        if self.error:raise ValueError(self.error)
        if self.prewarm_process and not self.process and self.prewarm_process.poll() is not None:raise ValueError('Prepared renderer exited')
        if self.lights:self.lights.poll()
        if self.process and self.process.poll() is not None:
            if not C.c_int32.from_address(self.receiver.channel.view+OFFSET+40).value:raise ValueError('Renderer exited before source stopped')
            return
        self.discover(self.current_rows());self.collect_prepared()
        if not self.process:
            if self.first_discovery is not None and time.monotonic()-self.first_discovery>25:raise ValueError('No supported diffuse-ready asset within25s')
            if self.anchor_id is None:return
            if self.initial_context is None:self.prepare_initial_context(pid)
            if self.lights and not self.lights.ready:return
            self.publish_prepared(initial=True)
            gpu,manifest,row=self.initial_context
            self.content_signature=self.preparer.jobs[self.anchor_id]['signature']
            self.renderer_activation_ns=time.perf_counter_ns()
            if self.renderer_started_ns is None:self.renderer_started_ns=self.renderer_activation_ns
            SingleRelay.launch(self,gpu,manifest,row,pid)
        else:
            self.publish_prepared();self.recover(pid)
            self.flush_enhancements()

    def collect_prepared(self):
        self.preparer.pump();events=self.preparer.events;self.preparer.events=[]
        for kind,value in events:
            if kind=='failed':self.fail_job(value,value['error']);continue
            if kind=='basic':
                job=value;self.path_count+=1;path_id=self.path_count
                folder=self.folder/'gpu/assets'/str(path_id);folder.parent.mkdir(parents=True,exist_ok=True)
                job['gpu'].rename(folder);job.update(gpu=folder,output=folder,path_id=path_id)
                fields=list(wire.ASSET.unpack(job['wire']));fields[1]=path_id
                raw=wire.ASSET.pack(*fields);job['wire']=raw[:-8]+struct.pack('<Q',wire.fnv(raw[:-8]))
                job['manifest']['parallel_preparation']=True
                self.resident[job['signature']]=(path_id,folder,job['manifest'],job['wire'])
                if self.anchor_id is None:self.anchor_id=job['id'];self.initial_ids={job['id']}
                primary_hashes={t['original_sha256'] for t in job['manifest']['textures']}
                originals={v['sha256']:len(v['raw']) for v in job['source_images'].values()}
                self.image_bytes+=job['manifest']['image_bytes']+sum(size for sha,size in originals.items() if sha not in primary_hashes and sha not in self.original_images)
                self.original_images.update(originals)
                (folder/'materials-config-accepted.toml').write_bytes(self.material_config)
                self.progressive_events.append(dict(event='diffuse_ready',id=job['id'],path_id=path_id,at_ns=time.perf_counter_ns()))
            else:self.pending_enhancements.append((kind,value))
        for job in self.preparer.jobs.values():
            if job['phase']!='alias' or job.get('alias_ready'):continue
            canonical=self.preparer.jobs[job['canonical']]
            if 'path_id' not in canonical:continue
            fields=list(wire.ASSET.unpack(canonical['wire']));row=job['row']
            fields[:6]=[job['id'],fields[1],row[1],row[7],row[5],row[6]]
            raw=wire.ASSET.pack(*fields);raw=raw[:-8]+struct.pack('<Q',wire.fnv(raw[:-8]))
            job.update(wire=raw,gpu=canonical['gpu'],manifest=canonical['manifest'],path_id=canonical['path_id'],new=False,alias_ready=True)

    def flush_enhancements(self):
        """Admit ready bases before doing any enhancement IO. Bound each drain
        so a large enhancement burst cannot monopolize the scene coordinator.
        No collection timer: apply up to four already-complete groups each cycle.
        """
        changed=set();finished=[];processed=0
        while self.pending_enhancements and processed<4:
            kind,value=self.pending_enhancements[0]
            job=value if kind=='complete' else value[0]
            if not job.get('published'):break
            self.pending_enhancements.popleft()
            if kind=='complete':finished.append(job);continue
            if job['phase']=='failed':continue
            _,piece=value
            try:self.accept_piece(job,piece);changed.add(job['id'])
            except (ValueError,OSError) as e:self.fail_job(job,e)
            processed+=1
        self.pending_stage_ids.update(changed)
        self.pending_complete_ids.update(j['id'] for j in finished)
        self.retry_publication()

    def retry_publication(self):
        # Atomic replacement can fail briefly while Remix holds the old stage
        # open without DELETE sharing. Keep the prior stage and retry next cycle;
        # no sleep, file deletion, game wait, or repeated map generation.
        busy=False
        for identity in list(self.pending_stage_ids):
            try:self.write_stage(self.preparer.jobs[identity])
            except PermissionError:busy=True;self.publication_retries+=1;continue
            self.pending_stage_ids.remove(identity);self.pending_library=True
        if self.pending_library:
            try:self.commit_layers(initial=not bool(self.process))
            except PermissionError:busy=True;self.publication_retries+=1
            else:self.pending_library=False
        if busy:
            if self.publication_busy_since is None:self.publication_busy_since=time.monotonic()
            if time.monotonic()-self.publication_busy_since>5:raise RuntimeError('Material atomic publication sharing-busy for5s;preserve existing base')
        else:self.publication_busy_since=None
        if not self.pending_library:
            for identity in list(self.pending_complete_ids):
                if identity in self.pending_stage_ids:continue
                self.preparer._release(self.preparer.jobs[identity]);self.pending_complete_ids.remove(identity)

    def accept_piece(self,job,piece):
        from material_binding import LIMIT
        key=piece['remix_hash'];identity=(piece['primary_sha256'],piece['secondary_sha256'],hashlib.sha256(self.material_config).hexdigest())
        if key in self.material_keys and self.material_keys[key]!=identity:raise ValueError('Conflicting material image roles across assets')
        folder=job['gpu']/'rtx-remix/mods/sfc-policy';folder.mkdir(parents=True,exist_ok=True)
        pieces=self.material_pieces.setdefault(job['id'],{})
        images=job.setdefault('generated_images',{});additional=sum(len(data) for name,(data,_) in piece['encoded'].items() if name not in images)
        originals=job.setdefault('material_originals',{})
        for image in job.get('images',{}).values():originals[image['sha256']]=len(image['raw'])
        if sum(originals.values())+job.get('material_bytes',0)+additional>LIMIT:raise ValueError('Material original/derived image128MiB cap')
        for name,(data,metadata) in piece['encoded'].items():
            if name in images:continue
            target=folder/name;target.parent.mkdir(exist_ok=True);pending=target.with_suffix('.pending')
            pending.write_bytes(data);pending.replace(target);images[name]=metadata
        job['material_bytes']=job.get('material_bytes',0)+additional;self.image_bytes+=additional
        self.material_keys[key]=identity
        piece.pop('encoded');pieces[piece['group']]=piece
        self.progressive_events.append(dict(event='material_ready',id=job['id'],group=piece['group'],remix_hash=key,at_ns=time.perf_counter_ns(),meaning='Complete derivative files;not GPU readiness'))

    def write_stage(self,job):
        from material_binding import shader
        folder=job['gpu']/'rtx-remix/mods/sfc-policy'
        pieces=self.material_pieces[job['id']];blocks={}
        for group in job['manifest']['groups']:
            if group[0] not in pieces:continue
            p=pieces[group[0]];blocks[p['remix_hash']]=shader(p['remix_hash'],p['images'],p['values'])
        stage='#usda 1.0\n(defaultPrim = "RootNode")\ndef Xform "RootNode"\n{\n def Scope "Looks"\n {\n'+''.join(blocks.values())+' }\n}\n'
        pending=folder/'mod.usda.pending';pending.write_text(stage,encoding='utf-8');pending.replace(folder/'mod.usda')
        self.progressive_events.append(dict(event='material_stage_published',id=job['id'],groups=list(pieces),at_ns=time.perf_counter_ns(),meaning='Atomic CPU stage replacement;not GPU consumption'))
        self.mod_layer(job['gpu'],write=False)
        # Group ordering matches the original scene even if tasks complete in a
        # different order. Reports contain no pixel buffers.
        rows=[pieces[g[0]] for g in job['manifest']['groups'] if g[0] in pieces]
        report=dict(schema='sfc.progressive-materials.v1',groups=rows,images=job['generated_images'],
            values=rows[0]['values'],config_sha256=hashlib.sha256(self.material_config).hexdigest(),
            mod_sha256=hashlib.sha256(stage.encode()).hexdigest(),complete=len(rows)==len(job['manifest']['groups']))
        (job['gpu']/'material-binding.json').write_text(json.dumps(report,indent=2))

    def publish_prepared(self,initial=False):
        # No material-library work here. Assets do not wait for enhanced maps.
        ready=[j for j in self.preparer.jobs.values() if 'wire' in j and 'path_id' in j and not j.get('published')]
        for job in ready:
            row=job['row'];wire.publish(self.receiver.channel,job['id'],job['wire']);job['published']=True
            self.catalog.append(dict(id=job['id'],path_id=job['path_id'],owner=row[1],revision=row[7],model=job['manifest']['model_name'],
                signature=job['signature'],manifest=job['manifest'],packet=job['wire'].hex(),initial=job['id'] in (self.initial_ids or set()),published_ns=time.perf_counter_ns()))
        if initial:self.initial_published_ns=time.perf_counter_ns()

    def finish(self,pid):
        if self.pending_enhancements or self.pending_stage_ids or self.pending_library:
            self.partial.append(dict(reason='Stopped before pending enhancements applied',count=len(self.pending_enhancements),stages=len(self.pending_stage_ids),library=self.pending_library))
        report=super().finish(pid)
        report['multi_scene']['progressive_events']=self.progressive_events
        report['multi_scene']['experimental_live_checkout']=self.experimental_live_checkout
        log=(self.folder/'gpu/job-console.log').read_text()
        report['multi_scene']['native_admission_service']='ASSET_SERVICE enabled=1 ' in log
        report['multi_scene']['native_initial_texture_data']='TEXTURE_UPLOAD initial_data=1 ' in log
        report['multi_scene']['native_texture_uploads']=[dict((key,int(value)) for key,value in __import__('re').findall(r'(\w+)=(\d+)',line))
            for line in log.splitlines() if line.startswith('MULTISCENE_UPLOAD ')]
        report['multi_scene']['material_publication_retries']=self.publication_retries
        report['multi_scene']['output_stage_timings']=[dict((key,int(value)) for key,value in __import__('re').findall(r'(\w+)=(\d+)',line))
            for line in log.splitlines() if line.startswith('OUTPUT_STAGE_TIMING ')]
        report['multi_scene']['progressive_scope']='Material publication only;runtime consumption requires pixels/timing comparison'
        (self.folder/'live-owner.analysis.json').write_text(json.dumps(report,indent=2))
        return report

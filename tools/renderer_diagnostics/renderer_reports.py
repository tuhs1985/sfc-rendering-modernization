"""Detailed developer evidence for renderer sessions and fixtures."""
import hashlib
import json
import re
import struct
import time

import multi_scene as wire
from renderer_backend import receipt

def source_hashes():
    from live_owner_timing import ROOT,digest
    from source_timing import source_hashes as base
    result=base()
    names=('tools/d3d9_proof/live_owner_wire.h','tools/d3d9_proof/live_owner_decode.h','tools/d3d9_proof/live_owner_input.h',
           'tools/d3d9_proof/d3d9_direct_host.cpp','tools/d3d9_proof/d3d9_replay.cpp','tools/d3d9_proof/output_producer.h',
           'tools/d3d9_proof/output_receiver.cpp','tools/d3d9_proof/output_channel.h','tools/d3d9_proof/ingress_replay.h',
           'tools/d3d9_proof/frame_ingress.h','tools/d3d9_proof/start_live_owner_timing_session.ps1',
           'tools/d3d9_proof/startup_ticket.h','tools/d3d9_proof/warm_start.h','tools/remix_runtime/warm_start.py',
           'tools/scene_bridge/scene_bundle.py','tools/remix_runtime/live_owner_timing.py',
           'src/transport/warm_start.py','src/rendering/live_owner_timing.py',
           'src/rendering/renderer_backend.py','tools/renderer_diagnostics/renderer_reports.py',
           'tests/d3d9_live_owner_tests.cpp','tools/remix_runtime/qualify_live_owner.py','tests/test_live_owner_timing.py')
    result.update({p:digest(ROOT/p) for p in names});return result


def binary_hashes():
    from live_owner_timing import ROOT,CONTEXT,EXE,RECEIVER,RUNTIME,GUARD,digest
    from source_timing import BINARIES
    names=(*BINARIES,str(CONTEXT.relative(EXE)),str(CONTEXT.relative(RECEIVER)),str(CONTEXT.relative(RUNTIME)),
           str(CONTEXT.relative(GUARD)),'artifacts/m1/bin/m1_gate.dll',
           'artifacts/remix-runtime/deps/remix_c.h','artifacts/d3d9-proof/ingress-x86/live_owner_tests.exe','artifacts/d3d9-proof/ingress-x64/live_owner_tests.exe')
    return {p:digest(ROOT/p) for p in names}


def require_qualification():
    from live_owner_timing import QUALIFICATION,RUNTIME,digest,source_hashes,binary_hashes
    q=json.loads(QUALIFICATION.read_text())
    if q.get('result')!='OFFLINE_LIVE_OWNER_PREPARED' or q.get('sources')!=source_hashes() or q.get('binaries')!=binary_hashes():raise ValueError('Live owner offline/source/binary qualification required;no game launch')
    if digest(RUNTIME)!='F7C310821AA98BCDFDEC120330B0A89457B7C5EBA58D21464AF32639611C809F':raise ValueError('Pinned runtime changed')
    return q


def parse_audits(raw,session,pid):
    from live_owner_timing import HEADER,STORE_BYTES,MAGIC,CAPACITY,AUDIT
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


def finish_live_owner_timing(self, pid):
    from live_owner_timing import OFFSET, HEADER, CAPACITY, AUDIT, parse_audits
    if getattr(self,'player_replacement',False):
        self.stop()
        from player_replacement import finish
        return finish(self,pid)
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
        if fields[:4]!=(0x314f4753,3,576,pid) or fields[4:8]!=expected:raise ValueError('Additive pool session/process/layout')
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


def finish_multi_scene_relay(self, pid, parent_finish):
    report=parent_finish(pid)
    from warm_start import ready,snapshot
    readiness=ready(self.receiver.channel) if self.prewarm_process else None
    ready_qpc,ready_pid=readiness if readiness else (None,None)
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
                              effect_light_recording=getattr(self,'effect_recording',None),
                              pipeline_mode=self.mode,detailed_evidence=self.mode=='test',
                              delivery_stages=stage_counts,asset_timings=asset_timings,material_events=self.material_events,
                              preparation=self.preparer.report(),initial_ids=sorted(self.initial_ids or []),
                              initial_published_ns=self.initial_published_ns,renderer_started_ns=self.renderer_started_ns,
                              prewarm_started_ns=self.prewarm_started_ns,renderer_activation_ns=self.renderer_activation_ns,
                              prewarm_ready_qpc=ready_qpc,prewarm_host_pid=ready_pid,
                              startup_transport=snapshot(self.receiver.channel) if self.prewarm_process else None,
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
    if getattr(self,'texture_memory',None):
        from texture_memory import BUDGET
        report['multi_scene']['texture_transport']=dict(protocol=2,mode='immutable-scene-and-texture-memory',
            created=self.texture_memory.created,acknowledged=self.texture_memory.acknowledged,
            peak_bytes=self.texture_memory.peak,remaining_bytes=self.texture_memory.bytes,budget_bytes=BUDGET,
            renderer_texture_file_fallback=False)
    report['scope']='Retained multi-ship diagnostic with recorded common camera-left offset;originals remain;not replacement or universal coverage'
    report['result']='MULTISHIP_OVERLAY_REVIEW_REQUIRED' if len(draws)>=2 and len(self.resident)>=2 and not self.partial and not state['asset_rejected'] and report['game_output']['drawn'] else 'PARTIAL'
    if self.player_replacement:
        report['scope']='Unique configured player-fixture model;fresh capture,zero offset,transactional presentation'
        report['result']='PLAYER_REPLACEMENT_SPONSOR_REVIEW_REQUIRED' if report['replacement']['committed'] and report['replacement']['suppressed'] and not self.partial and not state['asset_rejected'] else 'PARTIAL'
    if getattr(self,'native_all_ships',False):
        report['multi_scene']['coverage']='Per-pixel semantic owner identity from nearest physical hull;exact rendered membership joined to output'
        from native_cohort import save
        report['native_cohort']=save(self.receiver.channel,self.folder)
        report['multi_scene']['original_suppressed']=bool(report['native_cohort']['suppressed'])
        report['scope']='Owner-qualified native replacement of freshly retained supported ships;one shared completed frame,owner-labelled physical coverage'
        report['result']='NATIVE_COHORT_REVIEW_REQUIRED' if report['native_cohort']['inserted'] and not self.partial and not state['asset_rejected'] else 'PARTIAL'
    (self.folder/'live-owner.analysis.json').write_text(json.dumps(report,indent=2))
    return report


def finish_progressive_scene_relay(self, pid, parent_finish):
    if self.pending_enhancements or self.pending_stage_ids or self.pending_library:
        self.partial.append(dict(reason='Stopped before pending enhancements applied',count=len(self.pending_enhancements),stages=len(self.pending_stage_ids),library=self.pending_library))
    report=parent_finish(pid)
    report['multi_scene']['progressive_events']=self.progressive_events
    report['multi_scene']['experimental_live_checkout']=self.experimental_live_checkout
    log=(self.folder/'gpu/job-console.log').read_text()
    report['multi_scene']['native_admission_service']='ASSET_SERVICE enabled=1 ' in log
    report['multi_scene']['native_initial_texture_data']='TEXTURE_UPLOAD initial_data=1 ' in log
    report['multi_scene']['native_texture_uploads']=[dict((key,int(value)) for key,value in __import__('re').findall(r'(\w+)=(\d+)',line))
        for line in log.splitlines() if line.startswith('MULTISCENE_UPLOAD ')]
    report['multi_scene']['material_publication_retries']=self.publication_retries
    report['multi_scene']['material_publication_status']=dict(
        pending_stages=len(self.pending_stage_ids),pending_library=self.pending_library,
        delayed=self.publication_busy_since is not None,
        delayed_seconds=max(0,time.monotonic()-self.publication_busy_since) if self.publication_busy_since is not None else 0,
        warnings=getattr(self,'publication_warning_count',0),
        last_error=getattr(self,'publication_last_error',None),
        meaning='File publication only;not runtime material installation ACK')
    report['multi_scene']['output_stage_timings']=[dict((key,int(value)) for key,value in __import__('re').findall(r'(\w+)=(\d+)',line))
        for line in log.splitlines() if line.startswith('OUTPUT_STAGE_TIMING ')]
    report['multi_scene']['progressive_scope']='Material publication only;runtime consumption requires pixels/timing comparison'
    (self.folder/'live-owner.analysis.json').write_text(json.dumps(report,indent=2))
    return report


def finish_async_material_checkout(self, pid, parent_finish):
    result=parent_finish(pid)
    result['multi_scene']['async_material_checkout']=dict(
        backend=receipt(self.renderer_backend),material_library='flat',
        complete_asset_stages=True,finished_ns=time.perf_counter_ns(),
        material_priming=self.material_prime_ready)
    (self.folder/'live-owner.analysis.json').write_text(json.dumps(result,indent=2))
    return result

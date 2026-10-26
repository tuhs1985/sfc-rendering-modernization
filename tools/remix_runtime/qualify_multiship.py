"""New-mode preparation gate;does not weaken or overwrite legacy FCA receipts."""
import argparse
import json
from pathlib import Path
import re
import os
import struct
import subprocess as sp
import uuid
from additive_qualification import ROOT,sources,binaries,configs,digest,delivery_window

RECEIPT=ROOT/'artifacts/d3d9-proof/multiship-tests/qualification.json'


def locks():
    extra={}
    for arch in ('32','64'):
        for extension in ('exe','txt'):
            p=ROOT/f'artifacts/d3d9-proof/resource-policy-tests/resource{arch}.{extension}'
            extra[str(p.relative_to(ROOT)).replace('\\','/')]=digest(p)
    for name in ('mesh_checksum.dll','build.json'):
        p=ROOT/'artifacts/d3d9-proof/mesh-checksum'/name
        extra[str(p.relative_to(ROOT)).replace('\\','/')]=digest(p)
    p=ROOT/'artifacts/remix-ingest/bin/bounded_job.exe'
    extra[str(p.relative_to(ROOT)).replace('\\','/')]=digest(p)
    p=ROOT/'artifacts/d3d9-proof/multiship-tests/asset_hash.exe'
    extra[str(p.relative_to(ROOT)).replace('\\','/')]=digest(p)
    p=ROOT/'artifacts/d3d9-proof/persistent-tests/native_scene.exe'
    extra[str(p.relative_to(ROOT)).replace('\\','/')]=digest(p)
    for stem in ('wire32','wire64'):
        for extension in ('exe','txt'):
            p=ROOT/f'artifacts/d3d9-proof/multiship-tests/{stem}.{extension}'
            extra[str(p.relative_to(ROOT)).replace('\\','/')]=digest(p)
    for arch in ('32','64'):
        for extension in ('exe','txt'):
            p=ROOT/f'artifacts/d3d9-proof/buffer-tests/buffer{arch}.{extension}'
            extra[str(p.relative_to(ROOT)).replace('\\','/')]=digest(p)
    for stem in ('identity32','identity64','identity-component'):
        for extension in ('exe','txt','json'):
            p=ROOT/f'artifacts/d3d9-proof/identity-tests/{stem}.{extension}'
            extra[str(p.relative_to(ROOT)).replace('\\','/')]=digest(p)
    policy=configs();policy['multi_ship']=digest(ROOT/'tools/d3d9_proof/multi_ship.toml')
    code=sources();code['tools/remix_ingest/bounded_job.cpp']=digest(ROOT/'tools/remix_ingest/bounded_job.cpp')
    return dict(sources=code,binaries={**binaries(),**extra},configs=policy)


def inspect(fixture):
    for arch in ('32','64'):
        proof=(ROOT/f'artifacts/d3d9-proof/resource-policy-tests/resource{arch}.txt').read_text(encoding='utf-8-sig')
        if ('Native resource policy PASS' not in proof or 'classic_ex_pixels_exact=1 reset_exact=1 recreation_exact=1' not in proof
                or 'remix_reshade_dxvk=absent' not in proof or 'initial_data_pixels_exact=1 source_memory_owned=1' not in proof):
            raise ValueError('Actual system D3D9/Ex resource/reset/recreation proof required')
    fixture=Path(fixture).resolve();fixture.relative_to(ROOT/'artifacts/remix-runtime/runs')
    result=json.loads((fixture/'result.json').read_text());live=result.get('live_owner_timing') or {}
    multi=live.get('multi_scene') or {};game=live.get('game_output') or {};state=multi.get('state') or {}
    assets=multi.get('assets') or [];draws=multi.get('draws') or [];sync=game.get('synchronized_buffer') or {}
    if result.get('runtime_candidate'):
        raise ValueError('Experimental runtime cannot qualify unchanged production dependency')
    if result.get('error') or not result.get('multi_ship_fixture') or result.get('fixture_exit') or result.get('host_exit'):
        raise ValueError('Actual multi-ship fixture incomplete')
    if result.get('render_prewarm','off')!='off':
        raise ValueError('Experimental render warm-up cannot qualify unchanged normal startup')
    if result.get('loading_policy','inherit')!='inherit':
        raise ValueError('Experimental loading policy cannot qualify unchanged normal startup')
    if result.get('material_library','layers')!='layers':
        raise ValueError('Experimental material library cannot qualify unchanged normal startup')
    if result.get('material_texture_loading','preload')!='preload':
        raise ValueError('Experimental material texture loading cannot qualify unchanged normal startup')
    if result.get('native_log_level','inherit')!='inherit':
        raise ValueError('Experimental logging policy cannot qualify unchanged normal startup')
    if result.get('api_texture_prefetch'):
        raise ValueError('Experimental API texture prefetch cannot qualify unchanged normal startup')
    if result.get('diagnostic_skip_initial_material_library'):
        raise ValueError('Initial material-library isolation cannot qualify normal appearance')
    if result.get('diagnostic_skip_late_material_reload') or multi.get('diagnostic_skip_late_material_reload'):
        raise ValueError('Diagnostic material-reload isolation cannot qualify normal appearance/delivery')
    preparation=multi.get('preparation') or {};events=multi.get('material_events') or []
    if preparation.get('workers')!=4 or not preparation.get('closed') or preparation.get('unfinished'):
        raise ValueError('Bounded preparation workers/clean shutdown required')
    if preparation.get('peak_parallel_preparations',0)<2:raise ValueError('Actual overlapping asset preparation required')
    activation=multi.get('renderer_activation_ns') or multi.get('renderer_started_ns',0)
    if not multi.get('initial_published_ns') or multi['initial_published_ns']>=activation:
        raise ValueError('Initial material/catalog publication must precede renderer startup')
    if not events or not events[0].get('initial') or events[0]['supervisor_monotonic_ns']>=activation:
        raise ValueError('Initial material library must be committed before runtime startup')
    if result.get('prewarm'):
        if (not multi.get('prewarm_started_ns') or multi['prewarm_started_ns']!=multi.get('renderer_started_ns')
                or multi['prewarm_started_ns']>=activation or not multi.get('prewarm_ready_qpc')):
            raise ValueError('Early renderer process/readiness/activation evidence missing')
    if result.get('multi_ship_resources_fixture') and not result.get('multi_ship_late_asset_fixture') and (len(events)!=1 or not all(a.get('initial') for a in assets)):
        raise ValueError('Initial fixture requires one complete library and no incremental material reloads')
    if result.get('multi_ship_late_asset_fixture') and (len(events)!=2 or sum(not a.get('initial') for a in assets)!=1):
        raise ValueError('Deliberate late-asset survival/material boundary required')
    if result.get('multi_ship_build_locks')!=locks():raise ValueError('Multi-ship fixture used a different source/binary/config build')
    if live.get('result')!='MULTISHIP_OVERLAY_REVIEW_REQUIRED' or not live.get('normal_owned_exit'):
        raise ValueError('Multi-ship submission/cleanup incomplete')
    if len({a['signature'] for a in assets})<2 or len({a['owner'] for a in assets})<2 or any(a['acknowledgement']!=1 for a in assets):
        raise ValueError('Two genuinely different assets and owner admissions required')
    if result.get('multi_ship_resources_fixture'):
        if len(assets)!=4 or len({a['signature'] for a in assets})!=3 or len({a['path_id'] for a in assets})!=3:
            raise ValueError('Three resident assets and four independently acknowledged owners required')
        if multi['image_bytes']<=128*1024*1024:raise ValueError('Actual output above old image cap required')
    if len(draws)<2 or min(d['draws'] for d in draws)<100 or multi['partial'] or state.get('asset_rejected',1):
        raise ValueError('Independent multi-instance drawing/admission failed')
    if result.get('multi_ship_resources_fixture') and len(draws)!=4:raise ValueError('Shared-asset independent draw counters required')
    stages=multi.get('delivery_stages') or {}
    if any(stages.get(k,1) for k in ('lookup_header','lookup_packet','lookup_identity')):
        raise ValueError('Complete-cohort notification/readiness regression')
    admissions=live.get('input_admission') or {}
    if admissions.get('maximum_age_us')!=50000 or len(admissions.get('stages',[]))!=2:
        raise ValueError('Actual buffered presentation admission/counters missing')
    from multi_scene import camera_offset
    offset=list(struct.unpack('<3f',struct.pack('<3f',*camera_offset())))
    if game.get('camera_offset')!=offset or not game.get('drawn') or any(game.get(k,1) for k in ('invalid','error','resource_failed')):
        raise ValueError('Configured multi-ship return correspondence/output failed')
    if sync.get('paired',0)<540 or sync.get('failed',1) or sync.get('dropped',1) or game.get('overwritten',1):
        raise ValueError('Whole-cohort paired-frame audit failed')
    log=(fixture/'fixture.log').read_text();host=(fixture/'gpu/job-console.log').read_text()
    steady_frames,steady_draws=delivery_window(log)
    for marker in ('native_HUD_and_scene_exact=1','state_errors=0 resized=1 recreated=1','GAME_IMAGE_PIXELS'):
        if marker not in log:raise ValueError('Missing actual compositor/frame/HUD check: '+marker)
    for marker in ('MULTISCENE_SUMMARY','OUTPUT_API_SHUTDOWN 0','sdk_mesh_calls=0'):
        if marker not in host:raise ValueError('Missing actual ordinary-D3D9 receipt: '+marker)
    initial=re.search(r'MULTISCENE_INITIAL mask=(\d+) ready=(\d+) waits=(\d+)',host)
    mask=sum(1<<(a['id']-1) for a in assets if a.get('initial'))
    if not initial or int(initial[1])!=mask or initial[2]!='1':raise ValueError('Initial GPU catalog must resolve before visible submission')
    from evidence_budget import AGGREGATE_BYTES
    if multi['image_bytes']>AGGREGATE_BYTES or multi['original_images']>64*256:raise ValueError('Aggregate resource bounds')
    if not multi.get('image_policy',{}).get('legacy_scene_image_cap_removed'):raise ValueError('Old test image cap still active')
    if any(result['source_files'].get(name)!=digest(ROOT/'artifacts/remix-runtime/return-bin'/name)
           for name in ('SFCRemixReturn.dll','d3d11_return_fixture.exe')):raise ValueError('Fixture used stale return binary')
    return dict(fixture=str(fixture.relative_to(ROOT)),fixture_sha256=digest(fixture/'result.json'),
                prewarm=bool(result.get('prewarm')),
                models=[a['model'] for a in assets],draws=draws,paired=sync['paired'],missing=sync.get('missing'),
                image_bytes=multi['image_bytes'],state=state,aligned=offset==[0,0,0],camera_offset=offset,original_suppressed=False,
                steady_frames=steady_frames,steady_draws=steady_draws)


def qualify(fixture):
    evidence=inspect(fixture)
    if not evidence['prewarm']:raise ValueError('Current launcher requires early-start renderer fixture')
    native=native_source_test()
    performance_native=native_source_test('performance')
    import sys
    sys.path.insert(0,str(ROOT/'tools/m1_component'))
    from identity_census import analyze_summary
    census=analyze_summary(ROOT/'artifacts/d3d9-proof/identity-tests/identity-component.json')
    if (census['native_ship_epoch_pairs']!=3 or len(census['shared_visuals'])!=1
            or len(census['context_choice_mismatches'])!=0 or census['first_ms']<9265):
        raise ValueError('Production full-window identity recorder test required')
    for arch in ('32','64'):
        if 'Multi-scene PASS 93 checks' not in (ROOT/f'artifacts/d3d9-proof/multiship-tests/wire{arch}.txt').read_text(encoding='utf-8-sig'):
            raise ValueError('New wire tests required')
        if 'Synchronized buffer PASS 33 checks' not in (ROOT/f'artifacts/d3d9-proof/buffer-tests/buffer{arch}.txt').read_text(encoding='utf-8-sig'):
            raise ValueError('Scene/HUD/depth buffer GPU tests required')
    from light_discovery import require_qualification as lights
    lights()
    RECEIPT.write_text(json.dumps(dict(result='OFFLINE_MULTISHIP_OVERLAY_PREPARED_NOT_SFC_PASS',locks=locks(),evidence=evidence,native=native,performance_native=performance_native,
        limitations=['Actual SFC delivery stability at this placement pending','Union coverage is not a native per-owner picking map',
                     'Original ships remain drawn','Rigid triangle supported path only;no universal model or deformation claim']),indent=2))
    require_qualification()
    print('Multi-ship configured placement offline preparation PASS;not SFC/replacement PASS')


def native_source_test(mode='test'):
    from pipeline_mode import validate
    validate(mode)
    from present_calibration import Receiver
    from live_owner_timing import initialize
    import multi_scene as wire
    receiver=Receiver();work=RECEIPT.parent/('native-'+uuid.uuid4().hex);work.mkdir()
    try:
        initialize(receiver.channel,persistent=True);wire.initialize(receiver.channel)
        env={**os.environ,'SFC_PERSISTENT_SCENE':'1','SFC_D3D9_MULTISCENE':'1','SFC_D3D9_SOURCE_TIMING':'1',
             'SFC_D3D9_LIVE_TIMING':'1','SFC_REMIX_CALIBRATION_SCENE':receiver.name,'SFC_PIPELINE_MODE':mode}
        for name in ('SFC_NATIVE_LIGHT_DISCOVERY','SFC_D3D9_SHARED_LIGHTS','SFC_D3D9_GAME_OUTPUT'):env.pop(name,None)
        process=sp.Popen([str(ROOT/'artifacts/d3d9-proof/persistent-tests/native_scene.exe'),receiver.name,str(work)],
                         env=env,stdout=sp.PIPE,stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)
        try:output,_=process.communicate(timeout=10)
        except sp.TimeoutExpired:process.kill();process.communicate(timeout=5);raise ValueError('Owned native fixture timeout')
        (work/'test.txt').write_bytes(output)
        state=wire.summary(receiver.channel)
        if process.returncode or b'frames=120 captures=1 instance_generations=1 offscreen=120' not in output:
            raise ValueError('Actual native persistent collector/worker test failed')
        if state['pid']!=process.pid or state['published']!=120 or state['dropped']!=1 or not state['stopped'] or state['invalid']:
            raise ValueError('Actual native cohort publication/retirement/stop failed')
        raw=receiver.channel.read(wire.OFFSET+64+(121%wire.FRAMES)*wire.FRAME_SLOT+8,wire.FRAME_BYTES)
        if struct.unpack_from('<Q',raw,wire.FRAME_BYTES-8)[0]!=wire.fnv(raw[:-8]) or struct.unpack_from('<4I',raw,16)!=(121,1,1,1):
            raise ValueError('Actual native frame/checksum/owner mismatch')
        state.update(result='ACTUAL_NATIVE_SYNTHETIC_MEMORY_SOURCE_PASS',geometry_captures=1,
                     pipeline_mode=mode,
                     last_packet_sha256=__import__('hashlib').sha256(raw).hexdigest(),folder=str(work.relative_to(ROOT)))
        if mode=='performance':
            if (work/'LIVE-SCENE-001-updates.jsonl').exists():raise ValueError('Performance native worker unexpectedly wrote detailed journal')
            worker=json.loads((work/'LIVE-SCENE-001-worker.json').read_text())
            if worker['records'] or worker['io_failed'] or not worker['stopped']:raise ValueError('Performance worker summary/stop failure')
        (work/'result.json').write_text(json.dumps(state,indent=2));return state
    finally:receiver.close()


def require_qualification():
    q=json.loads(RECEIPT.read_text())
    if q.get('result')!='OFFLINE_MULTISHIP_OVERLAY_PREPARED_NOT_SFC_PASS' or q.get('locks')!=locks():
        raise ValueError('Multi-ship source/binary/config qualification stale/missing;no game launch')
    from light_discovery import require_qualification as lights
    lights();return q


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--fixture',required=True);a=p.parse_args();qualify(a.fixture)

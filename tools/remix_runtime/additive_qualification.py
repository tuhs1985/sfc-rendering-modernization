"""Source/binary/config gate for the controlled ordinary-D3D9 extra ship proof."""
import hashlib
import json
from pathlib import Path
import re
import os
from live_owner_timing import ROOT,binary_hashes
QUALIFICATION=ROOT/'artifacts/d3d9-proof/additive-qualification.json'


def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest().upper()


def sources():
    result={}
    for directory in ('tools/d3d9_proof','tools/remix_runtime','tools/scene_bridge','tools/m1_component','tests'):
        for p in (ROOT/directory).iterdir():
            if p.is_file() and p.suffix in ('.h','.cpp','.py','.ps1','.def'):result[str(p.relative_to(ROOT)).replace('\\','/')]=digest(p)
    return result


def binaries():
    result=binary_hashes()
    for name in ('artifacts/d3d9-proof/material-bin/texture_hash.exe','artifacts/remix-runtime/native-light-tests/m1_light_component.dll',
                 'artifacts/d3d9-proof/direct64-bin/loaded_light_tests.exe','artifacts/d3d9-proof/receiver-bin/game_output_tests.exe'):
        result[name]=digest(ROOT/name)
    import broad_capture
    result['full_event_proxy']=digest(broad_capture.qualified_full())
    return result


def configs():
    result={name:digest(ROOT/f'tools/remix_runtime/config/{name}.toml') for name in ('lights','materials','image','quality')}
    result['offset_ship']=digest(ROOT/'tools/d3d9_proof/offset_ship.toml')
    return result


def delivery_window(log):
    delivery=re.search(r'GAME_DELIVERY_WINDOW frames=(\d+) draws=(\d+)',log)
    if not delivery:raise ValueError('Additive steady-delivery preparation gate missing')
    frames,draws=map(int,delivery.groups())
    if frames<600 or draws>frames or draws<.9*frames:
        raise ValueError('Additive steady-delivery preparation gate failed;no repeat gameplay launcher')
    return frames,draws


def qualify(fixture):
    fixture=Path(fixture).resolve();fixture.relative_to(ROOT/'artifacts/remix-runtime/runs')
    result=json.loads((fixture/'result.json').read_text());live=result.get('live_owner_timing') or {};game=live.get('game_output') or {}
    log=(fixture/'fixture.log').read_text()
    worker_log=(fixture/'gpu/job-console.log').read_text()
    receiver_log=(fixture/'gpu/receiver.log').read_text()
    timing_logs=[(fixture/'gpu'/name).read_text() for name in ('frame-timing.csv','live-input.csv')]
    if 'WORKER_POLL microseconds=250 bounded_diagnostics=1' not in worker_log or any('DIAGNOSTICS_TRUNCATED' in text for text in (worker_log,receiver_log,*timing_logs)):
        raise ValueError('Additive worker timing/log policy incomplete')
    if 'SHARED_LIGHTS active=1 per_frame_file_reads=0' not in worker_log or not re.search(r'LIVE_ADMISSION expired=\d+ old_epoch=\d+ maximum_age_us=2000',worker_log):
        raise ValueError('Shared lighting/fresh-input admission policy not exercised')
    pixels=re.search(r'GAME_IMAGE_PIXELS changed=(\d+) border_untouched=1',log)
    delivery_frames,delivery_draws=delivery_window(log)
    binding=live.get('binding_control') or {}
    requests=result.get('synthetic_rebind_requests') or []
    if len(requests)!=2 or binding.get('generation')!=3 or binding.get('acknowledged')!=3 or binding.get('rejected',1):
        raise ValueError('Additive actual-resident-owner rebind fixture required')
    from live_owner_timing import parse_audits
    manifest=json.loads((fixture/'manifest.json').read_text())
    _,audits=parse_audits((fixture/'D3D9-LIVE-TIMING-001.bin').read_bytes(),manifest['semantic_calibration']['scene_session'],result['source_timing']['pid'])
    for request in requests:
        if not any(r['status']==1 and (r['owner'],r['revision'])==(request['owner'],request['revision']) for r in audits):
            raise ValueError('Rebind ACK without matched actual rendering/presentation evidence')
    if (result.get('error') or result.get('fixture_exit') or result.get('host_exit') or not live.get('normal_owned_exit') or
        not pixels or int(pixels[1])<8 or game.get('drawn',0)<120 or any(game.get(k,1) for k in ('error','invalid','resource_failed')) or
        'state_errors=0 resized=1 recreated=1' not in log):raise ValueError('Additive actual-proxy/pixel/state/cleanup qualification incomplete')
    from light_discovery import require_qualification as lights_qualified
    lights_qualified()
    receipt=dict(result='OFFLINE_ADDITIVE_PREPARED_NOT_SFC_PASS',fixture=str(fixture.relative_to(ROOT)),fixture_sha256=digest(fixture/'result.json'),
                 drawn=game['drawn'],changed_pixels=int(pixels[1]),delivery_frames=delivery_frames,delivery_draws=delivery_draws,sources=sources(),binaries=binaries(),configs=configs(),
                 worker_poll_us=250,deferred_diagnostics=True,
                 shared_lights=True,maximum_input_age_us=2000,
                 rebind_generations=3,rebind_owners=[r['owner'] for r in requests],
                 limitations=['Exact-frame omissions remain visible;no stale hold','One resident asset/unique configured fixture model;fresh qualified owner epochs only','Resize/device recreation hides output until a fresh session','No original suppression','Offline lights are explicitly replayed;actual native light join still needs runtime evidence'])
    QUALIFICATION.write_text(json.dumps(receipt,indent=2));require_qualification();return receipt


def require_qualification():
    q=json.loads(QUALIFICATION.read_text())
    if q.get('result')!='OFFLINE_ADDITIVE_PREPARED_NOT_SFC_PASS' or q.get('sources')!=sources() or q.get('binaries')!=binaries() or q.get('configs')!=configs():
        raise ValueError('Additive source/binary/visual-baseline qualification stale or missing;no game launch')
    if q.get('worker_poll_us')!=250 or not q.get('deferred_diagnostics') or os.environ.get('SFC_D3D9_POLL_US','250')!='250':
        raise ValueError('Qualified additive worker policy changed;no game launch')
    if q.get('rebind_generations')!=3:raise ValueError('Resident owner-rebind qualification missing;no game launch')
    if not q.get('shared_lights') or q.get('maximum_input_age_us')!=2000:raise ValueError('Fast recovery qualification missing;no game launch')
    from light_discovery import require_qualification as lights_qualified
    lights_qualified();return q

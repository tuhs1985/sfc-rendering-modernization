"""Source-locked opt-in one-frame presentation gate;never launches SFC."""
import json
from pathlib import Path
from additive_qualification import ROOT,digest,sources,binaries,configs

RECEIPT=ROOT/'artifacts/d3d9-proof/buffer-tests/qualification.json'

def locks():
    extra={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for arch in ('32','64')
        for p in (ROOT/f'artifacts/d3d9-proof/buffer-tests/buffer{arch}.exe',ROOT/f'artifacts/d3d9-proof/buffer-tests/buffer{arch}.txt')}
    return dict(sources=sources(),binaries={**binaries(),**extra},configs=configs())

def require_qualification():
    q=json.loads(RECEIPT.read_text())
    if q.get('result')!='OFFLINE_SYNCHRONIZED_BUFFER_PREPARED' or q.get('locks')!=locks() or not q.get('worker_read_fences') or not q.get('retain_ready') or not q.get('early_evidence'):
        raise ValueError('Synchronized buffer qualification stale/missing;no game launch')
    return q

def phase_qualified(result,early):
    game=result.get('live_owner_timing',{}).get('game_output',{})
    if result.get('buffer_early_ready_fixture',False)!=early or not game.get('retain_ready') or not game.get('lease_worker_releases') or game.get('overwritten',1):
        raise ValueError('Buffered retained-output/worker-fence phase proof missing')
    lead=result['source_timing']['profiles'][0]['last_lead_ms']['p50']
    if (early and lead<12) or (not early and lead>8):raise ValueError('Buffered early/late source-to-Present lead not exercised')

def qualify(fixture,early_fixture):
    fixture=Path(fixture).resolve();fixture.relative_to(ROOT/'artifacts/remix-runtime/runs')
    from qualify_persistent_scene import qualify as persistent
    persistent(fixture)
    result=json.loads((fixture/'result.json').read_text());log=(fixture/'fixture.log').read_text()
    if result.get('error') or not result.get('synchronized_buffer_fixture'):raise ValueError('Actual synchronized fixture required')
    report=result['live_owner_timing']['game_output']['synchronized_buffer']
    from synchronized_buffer import decode
    manifest=json.loads((fixture/'manifest.json').read_text())
    decoded=decode((fixture/'D3D9-SYNC-BUFFER-001.bin').read_bytes(),manifest['semantic_calibration']['scene_session'],result['source_timing']['pid'])
    if any(decoded.get(k)!=v for k,v in report.items()):raise ValueError('Buffered raw audit/summary mismatch')
    report=decoded
    if report['paired']<540 or report['dropped'] or report['failed'] or report['warmup']<2 or not report['reset']:
        raise ValueError('Buffered correspondence/reset/record-bound evidence incomplete')
    if any(marker not in log for marker in ('native_HUD_and_scene_exact=1','BUFFER_FIXTURE_DISABLED','BUFFER_FIXTURE_REENABLED','state_errors=0 resized=1 recreated=1')):
        raise ValueError('Buffered actual scene/HUD pixels/disable/state proof missing')
    phase_qualified(result,False)
    early_fixture=Path(early_fixture).resolve();early_fixture.relative_to(ROOT/'artifacts/remix-runtime/runs')
    if early_fixture==fixture:raise ValueError('Separate early and late fixtures required')
    persistent(early_fixture)
    early_result=json.loads((early_fixture/'result.json').read_text());phase_qualified(early_result,True)
    early_manifest=json.loads((early_fixture/'manifest.json').read_text())
    early_report=decode((early_fixture/'D3D9-SYNC-BUFFER-001.bin').read_bytes(),early_manifest['semantic_calibration']['scene_session'],early_result['source_timing']['pid'])
    if early_report['paired']<540 or early_report['failed'] or early_report['dropped']:raise ValueError('Early-ready buffered correspondence failed')
    for current in (result,early_result):
        if any(current['source_files'].get(name)!=digest(ROOT/'artifacts/remix-runtime/return-bin'/name) for name in ('SFCRemixReturn.dll','d3d11_return_fixture.exe')):
            raise ValueError('Buffered phase used a different return build')
    for arch in ('32','64'):
        log=(ROOT/f'artifacts/d3d9-proof/buffer-tests/buffer{arch}.txt').read_text(encoding='utf-8-sig')
        if f'Synchronized buffer PASS 33 checks color_HUD_depth_identity_age_state=1 size=1920x1080 pointer_bits={arch}' not in log:
            raise ValueError('Actual buffer GPU unit test missing')
    RECEIPT.write_text(json.dumps(dict(result='OFFLINE_SYNCHRONIZED_BUFFER_PREPARED',locks=locks(),fixture=str(fixture.relative_to(ROOT)),
        evidence=report,early_fixture=str(early_fixture.relative_to(ROOT)),early_evidence=early_report,worker_read_fences=True,retain_ready=True,
        sfc_launched=False,limit_frames=1,max_age_ms=50,additional_GPU_bytes=1920*1080*4*4,
        limitations=['Actual SFC responsiveness and camera transitions pending','No prediction or indefinite stale hold','Complete native HUD delayed with scene;hardware cursor not deliberately delayed','No original ship suppression']),indent=2))
    require_qualification();print('Synchronized full-frame/ship/depth/HUD correspondence preparation PASS')

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--fixture',required=True);p.add_argument('--early-fixture',required=True);a=p.parse_args();qualify(a.fixture,a.early_fixture)

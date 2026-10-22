"""Source-matched opt-in scene-depth qualification; no game launch here."""
import json
from live_return import ROOT,source_hashes,binary_hashes,depth_telemetry
from broad_capture import FULL_SHA,qualified_full

RECEIPT=ROOT/'artifacts/remix-runtime/deps/scene-depth-qualification.json'

def require_qualification():
    qualified_full()
    q=json.loads(RECEIPT.read_text())
    if (q.get('result')!='OFFLINE_SCENE_DEPTH_CALLBACK_PASS' or q.get('sources')!=source_hashes()
        or q.get('binaries')!=binary_hashes() or q.get('proxy_sha256')!=FULL_SHA):
        raise ValueError('Scene-depth offline callbacks/occlusion qualification missing or stale')
    return q

def qualify(folders):
    modes=set()
    for relative in folders:
        folder=ROOT/relative
        folder.resolve().relative_to((ROOT/'artifacts/remix-runtime/runs').resolve())
        r=json.loads((folder/'result.json').read_text());m=json.loads((folder/'manifest.json').read_text())
        host_ok=r.get('host_exit')==0 or (r.get('renderer_disconnect') and r.get('host_exit') is not None)
        if (r.get('result')!='OFFLINE_PROXY_PRIVATE_RETURN_PASS' or not r.get('scene_depth_verified') or r.get('sfc_launched') or not host_ok or r.get('fixture_exit')
            or r.get('proxy_sha256')!=FULL_SHA or m.get('source_hashes')!=source_hashes() or m.get('binaries')!=binary_hashes()):
            raise ValueError('Scene-depth fixture/provenance mismatch')
        if 'SCENE_DEPTH_CALLBACK_PASS' not in (folder/'fixture.log').read_text():raise ValueError('Actual callback pixel proof missing')
        modes.add('disconnect' if r.get('renderer_disconnect') else 'slow' if r.get('slow_receiver') else 'normal')
    if modes!={'normal','slow','disconnect'}:raise ValueError('Scene-depth normal/slow/disconnect required')
    q=dict(result='OFFLINE_SCENE_DEPTH_CALLBACK_PASS',sources=source_hashes(),binaries=binary_hashes(),proxy_sha256=FULL_SHA,evidence=folders)
    RECEIPT.write_text(json.dumps(q,indent=2));return q

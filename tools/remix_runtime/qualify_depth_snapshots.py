"""Record verified offline evidence, never launch a game or silently bless old builds."""
from pathlib import Path
import argparse
import json
from broad_capture import ROOT,FULL_SHA,digest
from prepare_full_reshade import source_hashes
from depth_snapshot_analysis import analyze_run,read_packet

def qualify(positive,negative,native):
    evidence=[]
    for folder,want in ((positive,True),(negative,False)):
        folder=Path(folder).resolve();folder.relative_to(ROOT/'artifacts/remix-runtime/runs')
        result=json.loads((folder/'result.json').read_text());report=analyze_run(folder)
        if report['status'].get('feature_level')!=0xA100 or report['status'].get('reader')!='ps_4_1':raise ValueError('Explicit10_1 pixel-reader evidence required')
        log=(folder/'fixture.log').read_text();proxy_log=(folder/'ReShade.log').read_text(errors='replace')
        if result['error'] or result['host_exit'] or result['fixture_exit']:raise ValueError('Offline fixture failed')
        if 'DEPTH_SNAPSHOT_END ' not in log or 'state_errors=0' not in log:raise ValueError('Missing actual callback/state evidence')
        if digest(folder/'dxgi.dll')!=FULL_SHA or 'limited add-on functionality' in proxy_log:raise ValueError('Full-support dependency/callback mismatch')
        if bool(report['complete'])!=want or (not want and report['snapshots']):raise ValueError('Positive/negative content evidence failed')
        if not want and any(report['status'].get(n,True) for n in ('io_errors','gpu_failures','ambiguous','issued','pending_abandoned')):raise ValueError('Negative fixture must be clean missing-content evidence,not a hidden GPU failure')
        if result['source_files']['SFCRemixReturn.dll']!=digest(ROOT/'artifacts/remix-runtime/return-bin/SFCRemixReturn.dll'):raise ValueError('Fixture binary differs from current build')
        evidence.append(str(folder.relative_to(ROOT)))
    native=Path(native).resolve();native.relative_to(ROOT/'artifacts/remix-runtime/runs')
    report=analyze_run(native)
    if not report['complete']:raise ValueError('Native GPU evidence incomplete')
    if report['status'].get('feature_level')!=0xA100 or report['status'].get('reader')!='ps_4_1':raise ValueError('Native10_1 evidence missing')
    legacy=json.loads((native/'legacy-profile-check.json').read_text())
    if legacy.get('feature_level')!=0xA100 or not (legacy.get('legacy_create_shader_hresult',0)&0x80000000):raise ValueError('Old SM5 incompatibility not reproduced')
    _,z0,_=read_packet(native/'depth-0.bin')
    _,z1,_=read_packet(native/'depth-1.bin')
    import numpy as np
    y,x=np.indices(z1.shape[:2]);base=.1015+.002*x+.004*y
    expected=np.stack((base,base,base+.56,base+.28),axis=2)
    if not np.allclose(z0,.625) or not np.allclose(z1,expected,atol=1e-5):raise ValueError('Known8sample/spatial content mismatch')
    evidence.append(str(native.relative_to(ROOT)))
    record={'result':'OFFLINE_DEPTH_SNAPSHOT_PASS','source_hashes':source_hashes(),
            'addon_sha256':digest(ROOT/'artifacts/remix-runtime/return-bin/SFCRemixReturn.dll'),
            'proxy_sha256':FULL_SHA,'evidence':evidence,'sfc_launched':False,
            'tested_feature_level':0xA100,'reader':'ps_4_1','legacy_check':legacy}
    target=ROOT/'artifacts/remix-runtime/deps/depth-snapshot-qualification.json'
    target.write_text(json.dumps(record,indent=2));print('Depth snapshots offline qualification PASS')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('positive',type=Path);p.add_argument('negative',type=Path);p.add_argument('native',type=Path);args=p.parse_args()
    qualify(args.positive,args.negative,args.native)

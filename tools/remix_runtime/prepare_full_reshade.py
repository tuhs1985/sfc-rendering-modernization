"""Download/extract pinned official package without running its installer."""
from pathlib import Path
import argparse
import json
import shutil
import urllib.request
import zipfile
from broad_capture import ROOT,FULL,FULL_SHA,digest

URL='https://reshade.me/downloads/ReShade_Setup_6.7.1_Addon.exe'
PACKAGE_SHA='FC55C5C62D0BC43BF02C40EC9AEF69E0B74F22A6017403AF1897EC32E5CD0E8F'
SOURCES=('return_addon.cpp','broad_trace.h','broad_events.h','return_fixture.cpp','build_return_probe.ps1',
         'broad_capture.py','run_return_game.py','run_return_fixture.py','prepare_full_reshade.py',
         'qualify_broad_rollback.py','archive_broad_evidence.py','start_return_image_session.ps1','recover_broad_session.py',
         '../m1_component/m1_controller.cpp','../m1_component/module_snapshot_retry.h','../m1_component/build_m1_controller.ps1','windows_processes.py',
         'depth_snapshot.h','depth_snapshot_analysis.py','qualify_depth_snapshots.py','../../tests/depth_snapshot_gpu_tests.cpp',
         '../m1_component/m1_present_calibration.h','../m1_component/m1_live_scene.h','../m1_component/m1_component.cpp',
         '../m1_component/build_m1_component.ps1','../m1_component/m1_live_bridge.h',
         '../m1_component/m1_mesh_export.h','../m1_component/m1_texture_references.h',
         'present_calibration.py','qualify_present_calibration.py','../../tests/present_calibration_tests.cpp',
         '../../tests/m1_live_scene_tests.cpp')
def source_hashes():return {n:digest(Path(__file__).parent/n) for n in SOURCES}
def prepare():
    folder=FULL.parent.parent;folder.mkdir(parents=True,exist_ok=True)
    package=folder/'ReShade_Setup_6.7.1_Addon.exe'
    if not package.exists():
        req=urllib.request.Request(URL,headers={'Referer':'https://reshade.me/'})
        with urllib.request.urlopen(req,timeout=45) as src,package.open('xb') as dst:
            size=0
            while part:=src.read(1024*1024):
                size+=len(part)
                if size>64*1024*1024:raise ValueError('Package64MiB download limit')
                dst.write(part)
    if digest(package)!=PACKAGE_SHA:raise ValueError('Pinned official package mismatch; do not execute')
    FULL.parent.mkdir(exist_ok=True)
    if not FULL.exists():
        with zipfile.ZipFile(package) as archive:
            item=archive.getinfo('ReShade32.dll')
            if item.file_size>16*1024*1024:raise ValueError('Unexpected proxy size')
            with archive.open(item) as src,FULL.open('xb') as dst:shutil.copyfileobj(src,dst)
    if digest(FULL)!=FULL_SHA:raise ValueError('Extracted full-support proxy mismatch')
    (folder/'manifest.json').write_text(json.dumps({'url':URL,'package_sha256':PACKAGE_SHA,'proxy_sha256':FULL_SHA,'product_version':'6.7.1','file_version':'6.7.1.2131','original_proxy_file_version':'6.7.1.2133','sdk_commit':'8cf85bd12d56697d756d4fcb45e501f5d1b540fa','installer_executed':False},indent=2))
    print('Pinned package/extraction PASS. No installed proxy changed.')
def qualify(positive,negative):
    prepare();evidence=[]
    for folder,want in ((positive,True),(negative,False)):
        folder=folder.resolve();folder.relative_to(ROOT/'artifacts/remix-runtime/runs')
        result=json.loads((folder/'result.json').read_text());analysis=json.loads((folder/'broad.analysis.json').read_text())
        log=(folder/'fixture.log').read_text();reshade=(folder/'ReShade.log').read_text(errors='replace')
        if digest(folder/'dxgi.dll')!=FULL_SHA:raise ValueError('Fixture proxy mismatch')
        if result['error'] or result['host_exit'] or result['fixture_exit']:raise ValueError('Fixture exit failed')
        if 'state_errors=0 status=3 drops=0 resized=1 recreated=1' not in log:raise ValueError('Native state/resize/recreation/loss qualification failed')
        if 'limited add-on functionality' in reshade:raise ValueError('Restricted callbacks were rejected')
        if analysis['result']!='BROAD_METADATA_CAPTURE_COMPLETE_DEPTH_UNQUALIFIED':raise ValueError('Trace incomplete')
        if bool(analysis['depth_candidates'])!=want:raise ValueError('Positive/negative depth evidence failed')
        if not all(analysis['counts'].get(n) for n in ('resource','view','targets','draw','indexed','present')):raise ValueError('Application callbacks missing')
        evidence.append(str(folder.relative_to(ROOT)))
    (FULL.parent.parent/'qualification.json').write_text(json.dumps({'result':'OFFLINE_EVENT_AND_STATE_PASS','proxy_sha256':FULL_SHA,'source_hashes':source_hashes(),'evidence':evidence},indent=2))
    print('Full-support positive/negative state and transient-binding qualification PASS')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--qualify',nargs=2,type=Path);args=p.parse_args()
    if args.qualify:qualify(*args.qualify)
    else:prepare()

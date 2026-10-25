"""Explicit OFFLINE API-scene experiment; no production launcher or runtime swap."""
import hashlib
import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/remix_runtime'),str(ROOT/'tools/d3d9_proof')]
import run_return_fixture as fixture
import live_owner_timing
import multi_scene_relay
import material_binding
from material_packet import prepare

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emission-off',action='store_true',help='Offline negative control;only API emission scalar becomes zero')
    parser.add_argument('--late-asset',action='store_true',help='Existing bounded fixture withholds third content until120draws')
    options=parser.parse_args()
    from build_record import verify
    build=verify()
    host=ROOT/'artifacts/remix-api-proof/bin/api_host.exe'
    if not host.is_file():raise ValueError('Build isolated API host first')
    live_owner_timing.EXE=host
    # SDK materials are explicit handles; disable USD replacement lookup. The
    # launch-time empty root is never changed or populated in this experiment.
    os.environ['DXVK_DISABLE_ASSET_REPLACEMENT']='1'
    for key in ('DXVK_ASYNC_ASSET_LOADING','DXVK_WAIT_ASYNC_TEXTURES','RTX_ENABLE_ASYNC_COMPILATION'):
        os.environ.pop(key,None)
    original_prepare=material_binding.prepare
    def bind(folder,*args,**kwargs):
        report=original_prepare(folder,*args,**kwargs)
        proof=prepare(folder,emission_off=options.emission_off)
        (Path(folder)/'api-materials.json').write_text(json.dumps(proof,indent=2))
        return report
    material_binding.prepare=bind
    def publish(self,initial):
        if not self.offline_fixture:raise ValueError('API experiment cannot modify live routing')
        self.material_events.append(dict(initial=initial,layers=len(self.layers),
            supervisor_monotonic_ns=time.perf_counter_ns(),sdk_material_sidecars=True,usd_publication=False))
    multi_scene_relay.Relay.commit_layers=publish
    original_finish=multi_scene_relay.Relay.finish
    def finish(self,pid):
        report=original_finish(self,pid)
        report['scope']='ISOLATED SDK scene submission through existing return connection;not ordinary D3D9 draw qualification'
        report['backend']='Remix API explicit material/mesh/instance handles'
        return report
    multi_scene_relay.Relay.finish=finish
    original_copy=shutil.copyfile
    def copy(source,destination,*args,**kwargs):
        if Path(source)==fixture.BIN/'d3d11_return_fixture.exe':
            source=ROOT/'artifacts/interface-cleanup-first-frame/first_frame_fixture.exe'
            proof=dict(probe='REMIX-API-SCENE-001',host_sha256=hashlib.sha256(host.read_bytes()).hexdigest(),
                fixture_sha256=hashlib.sha256(Path(source).read_bytes()).hexdigest(),
                backend='Explicit SDK materials/meshes/instances;not ordinary D3D9 draws',
                production_qualified=False,normal_host_unchanged=True)
            proof['emission_off']=options.emission_off
            proof['late_asset']=options.late_asset
            proof['build']=build
            (Path(destination).parent/'api-scene-control.json').write_text(json.dumps(proof,indent=2))
        return original_copy(source,destination,*args,**kwargs)
    shutil.copyfile=copy
    sys.argv=[str(ROOT/'tools/remix_runtime/run_return_fixture.py'),'--multi-ship','--multi-ship-resources',
              '--prewarm','--startup-profile','--pipeline-mode','performance']
    if options.late_asset:sys.argv.append('--multi-ship-late-asset')
    fixture.main()

if __name__=='__main__':main()

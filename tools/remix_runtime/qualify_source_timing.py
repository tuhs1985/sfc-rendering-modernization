"""Qualify default-off source timing without launching SFC or loading Remix."""
import argparse
import json
import os
import re
from pathlib import Path
import subprocess as sp
import sys
import time
from source_timing import ROOT,QUALIFICATION,BINARIES,digest,source_hashes,require_qualification
from present_calibration import Receiver


def main():
    p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');args=p.parse_args()
    if not args.execute:print('Offline source timing only;explicit --execute required.');return
    runs=ROOT/'artifacts/remix-runtime/runs';before=set(runs.glob('*-return-fixture'))
    sp.run([sys.executable,str(ROOT/'tools/remix_runtime/run_return_fixture.py'),'--source-timing','--observation-only','--graceful'],check=True,timeout=100)
    added=set(runs.glob('*-return-fixture'))-before
    if len(added)!=1:raise ValueError('Exactly one owned source timing fixture required')
    folder=added.pop();result=json.loads((folder/'result.json').read_text());analysis=json.loads((folder/'source-timing.analysis.json').read_text())
    child=re.search(r'VERIFIED_CHILD pid=(\d+) suspended_path_match=1 disk_sha_match=1',(folder/'fixture.log').read_text())
    if not child or analysis['pid']!=int(child[1]) or 'MODE OBSERVATION_ONLY no_runtime_loaded=1' not in (folder/'host.log').read_text():raise ValueError('Fixture process/runtime provenance missing')
    if result['error'] or result['host_exit'] or result['fixture_exit'] or not result.get('source_timing_requested') or analysis['records']<300 or analysis['exact_frame_owner_pairs']<150:raise ValueError('Actual proxy fixture incomplete')
    unit=sp.run([str(ROOT/'artifacts/d3d9-proof/receiver-bin/source_timing_tests.exe')],capture_output=True,timeout=10,check=True,creationflags=sp.CREATE_NO_WINDOW)
    (folder/'source-timing-native.log').write_bytes(unit.stdout+unit.stderr)
    receiver=Receiver();producer=None
    try:
        out=folder/'producer';out.mkdir();env={**os.environ};env.pop('SFC_REMIX_CALIBRATION_SCENE',None);env.pop('SFC_D3D9_SOURCE_TIMING',None)
        producer=sp.Popen([str(ROOT/'artifacts/m1/bin/m1_live_scene_tests.exe'),receiver.name,str(out)],env=env,stdout=sp.PIPE,stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)
        deadline=time.monotonic()+15
        while producer.poll() is None and time.monotonic()<deadline:receiver.drain();time.sleep(.01)
        if producer.poll() is None:raise ValueError('Producer15s timeout')
        text=producer.communicate()[0];(folder/'producer.log').write_bytes(text)
        if producer.returncode:raise ValueError('Native source capture/QPC/worker regression failed')
    finally:
        if producer and producer.poll() is None:producer.terminate();producer.wait(timeout=5)
        receiver.close()
    record=dict(result='OFFLINE_SOURCE_TIMING_PREPARED',sfc_launched=False,remix_loaded=False,evidence=str(folder.relative_to(ROOT)),
        binary_result_sha256=digest(folder/'result.json'),analysis_sha256=digest(folder/'source-timing.analysis.json'),
        sources=source_hashes(),binaries={p:digest(ROOT/p) for p in BINARIES})
    QUALIFICATION.parent.mkdir(parents=True,exist_ok=True);QUALIFICATION.write_text(json.dumps(record,indent=2));require_qualification()
    print('Read-only source timing offline qualification PASS:',folder)


if __name__=='__main__':main()

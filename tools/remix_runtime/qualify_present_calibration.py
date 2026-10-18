"""Offline10_1 GPU-to-worker exact-frame sidecar test. Never starts SFC."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import subprocess as sp
from present_calibration import Receiver,read_semantic,require_qualification
from depth_snapshot_analysis import analyze_run,read_packet,digest,ROOT

def main():
    p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');a=p.parse_args()
    if not a.execute:print('Offline calibration fixture ready; --execute starts owned GPU test only.');return
    folder=ROOT/'artifacts/remix-runtime/runs'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f-calibration-fixture')
    exe=ROOT/'artifacts/remix-runtime/return-bin/depth_snapshot_gpu_tests.exe'
    receiver=Receiver()
    try:
        result=sp.run([str(exe),str(folder)],env={**os.environ,'SFC_REMIX_CALIBRATION_SCENE':receiver.name},
            capture_output=True,timeout=30,creationflags=sp.CREATE_NO_WINDOW)
        if not folder.is_dir():raise ValueError('Fixture did not create output')
        (folder/'fixture.log').write_bytes(result.stdout+result.stderr)
        if result.returncode:raise ValueError('Native fixture failed; inspect retained log')
        depth=analyze_run(folder)
        if not depth['complete']:raise ValueError('Known GPU content incomplete')
        records=[]
        for i in range(3):
            row,_,_=read_packet(folder/f'depth-{i}.bin')
            records.append(read_semantic(folder/f'semantic-{i}.bin',row,receiver.name))
        if len({r['engine_frame'] for r in records})!=3:raise ValueError('Not three distinct engine frames')
        if sum(x.stat().st_size for x in folder.rglob('*') if x.is_file())>1024*1024:raise ValueError('Offline1MiB output bound')
        # Actual existing producer's synthetic-memory tests, including bypass of
        # 30Hz throttle and worker drain. No executable semantics are inferred.
        producer=ROOT/'artifacts/m1/bin/m1_live_scene_tests.exe'
        producer_dir=folder/'producer';producer_dir.mkdir()
        env={**os.environ};env.pop('SFC_REMIX_CALIBRATION_SCENE',None)
        p=sp.Popen([str(producer),receiver.name,str(producer_dir)],env=env,stdout=sp.PIPE,stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)
        import time
        until=time.monotonic()+10
        while p.poll() is None and time.monotonic()<until:
            receiver.drain();time.sleep(.01)
        if p.poll() is None:p.terminate();p.wait(timeout=5);raise ValueError('Producer10s timeout')
        text=p.communicate()[0];(folder/'producer.log').write_bytes(text)
        if p.returncode:raise ValueError('Producer calibration regression failed')
        from prepare_full_reshade import source_hashes
        record=dict(result='OFFLINE_CALIBRATION_SIDECAR_PASS',session=receiver.name,fixture_sha256=digest(exe),
            producer_test_sha256=digest(producer),addon_sha256=digest(ROOT/'artifacts/remix-runtime/return-bin/SFCRemixReturn.dll'),
            component_sha256=digest(ROOT/'artifacts/m1/bin/m1_component.dll'),source_hashes=source_hashes(),
            records=records,sfc_launched=False,evidence=str(folder.relative_to(ROOT)))
        (folder/'calibration.qualification.json').write_text(json.dumps(record,indent=2))
        (ROOT/'artifacts/remix-runtime/deps/present-calibration-qualification.json').write_text(json.dumps(record,indent=2))
        require_qualification()
        print('Calibration paired GPU/semantic provenance PASS: '+str(folder))
    finally:receiver.close()
if __name__=='__main__':main()

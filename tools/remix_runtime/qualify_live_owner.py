"""Offline only:raw-source capture,conversion,actual proxy/GPU return/current key."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import struct
import subprocess as sp
import sys
import time
from live_owner_timing import ROOT,QUALIFICATION,source_hashes,binary_hashes,require_qualification,digest


def conversion(folder):
    from scene_bundle import native_matrix,camera_state
    capture=ROOT/'artifacts/remix-runtime/runs/20261020-051149-684568-in-game/gate/LIVE-SCENE-001-updates.jsonl'
    candidates=[json.loads(line) for line in capture.read_text().splitlines()]
    candidates=[r for r in candidates if r[1] and r[2] and r[4]==1 and r[5] and r[6] and r[7] and r[48]==1 and not any(r[42:45])]
    rows=[candidates[i*(len(candidates)-1)//63] for i in range(64)]
    expected=[]
    for r in rows:
        camera_state(r,[0,0,0],[])
        floats=[x for start in (8,49,66) for line in native_matrix(r[start:start+17]) for x in line]
        floats.extend(struct.unpack('<4f',struct.pack('<4I',*r[83:87])))
        expected.append(struct.pack('<4I52f',r[1],r[7],r[2],1,*floats))
    for index,value in ((42,1),(24,0x200),(8,0x7fc00000),(88,0),(4,3),(2,0)):
        bad=rows[0].copy();bad[index]=value;rows.append(bad);expected.append(None)
    source=folder/'conversion-input.bin';source.write_bytes(b''.join(struct.pack('<96I',*r) for r in rows))
    outputs=[]
    for arch in ('x86','x64'):
        exe=ROOT/f'artifacts/d3d9-proof/ingress-{arch}/live_owner_tests.exe';output=folder/f'conversion-{arch}.bin'
        done=sp.run([str(exe),str(source),str(output)],capture_output=True,check=True,timeout=10,creationflags=sp.CREATE_NO_WINDOW)
        (folder/f'conversion-{arch}.log').write_bytes(done.stdout+done.stderr)
        raw=output.read_bytes()
        if len(raw)!=len(rows)*228:raise ValueError('Native conversion result size')
        for i,wanted in enumerate(expected):
            accepted=struct.unpack_from('<I',raw,i*228)[0]
            if accepted!=int(wanted is not None) or wanted is not None and raw[i*228+4:(i+1)*228]!=wanted:raise ValueError(f'Native/Python raw conversion disagreement at case{i},accepted={accepted}')
        outputs.append(dict(architecture=arch,rows=len(rows),sha256=digest(output)))
    return outputs


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    if not args.execute:print('Explicit --execute required;offline only,no SFC');return
    folder=ROOT/'artifacts/d3d9-proof/live-owner-validation'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f');folder.mkdir(parents=True)
    from run_offline import storage,AGGREGATE_BYTES
    if storage()+128*1024*1024>AGGREGATE_BYTES:raise ValueError('Live owner validation needs128MiB within20GB;archive exact generated evidence first')
    converted=conversion(folder)
    runs=ROOT/'artifacts/remix-runtime/runs';before=set(runs.glob('*-return-fixture'))
    done=sp.run([sys.executable,str(ROOT/'tools/remix_runtime/run_return_fixture.py'),'--source-timing','--observation-only','--graceful','--live-owner-timing'],capture_output=True,timeout=110,creationflags=sp.CREATE_NO_WINDOW)
    (folder/'combined-fixture.log').write_bytes(done.stdout+done.stderr)
    if done.returncode:raise ValueError('Combined proxy/GPU fixture failed;preserve partial evidence')
    added=set(runs.glob('*-return-fixture'))-before
    if len(added)!=1:raise ValueError('Exactly one combined owned fixture required')
    fixture=added.pop();result=json.loads((fixture/'result.json').read_text());live=result['live_owner_timing']
    if result['error'] or result['fixture_exit'] or result['host_exit'] or not live or live['received']<60 or live['status_counts']['1']<60 or any(live[k] for k in ('invalid','unqualified','source_rejected','audit_dropped','completion_invalid')):raise ValueError('Combined current-frame evidence incomplete')
    # Actual capture worker regression,including source publication before30Hz cap.
    from present_calibration import Receiver
    receiver=Receiver();producer=None
    try:
        out=folder/'capture-worker';out.mkdir();env={**os.environ};env.pop('SFC_REMIX_CALIBRATION_SCENE',None);env.pop('SFC_D3D9_LIVE_TIMING',None);env.pop('SFC_D3D9_SOURCE_TIMING',None)
        producer=sp.Popen([str(ROOT/'artifacts/m1/bin/m1_live_scene_tests.exe'),receiver.name,str(out)],env=env,stdout=sp.PIPE,stderr=sp.STDOUT,creationflags=sp.CREATE_NO_WINDOW)
        until=time.monotonic()+15
        while producer.poll() is None and time.monotonic()<until:receiver.drain();time.sleep(.01)
        if producer.poll() is None:raise ValueError('Capture worker15s limit')
        log=producer.communicate()[0];(folder/'capture-worker.log').write_bytes(log)
        if producer.returncode:raise ValueError('Raw source capture/throttle/worker regression failed')
    finally:
        if producer and producer.poll() is None:producer.terminate();producer.wait(timeout=5)
        receiver.close()
    q=dict(result='OFFLINE_LIVE_OWNER_PREPARED',sfc_launched=False,evidence=str(fixture.relative_to(ROOT)),validation=str(folder.relative_to(ROOT)),conversion=converted,
           fixture_result_sha256=digest(fixture/'result.json'),current_present_matches=live['status_counts']['1'],sources=source_hashes(),binaries=binary_hashes())
    QUALIFICATION.write_text(json.dumps(q,indent=2));require_qualification();print('Live owner combined offline qualification PASS:',fixture)


if __name__=='__main__':main()

"""Actual fixed-storage worker exercise, without starting SFC."""
import json
import os
from pathlib import Path
import subprocess as sp
import uuid
from present_calibration import Receiver
from light_discovery import BIN, ROOT, digest
from lifecycle_capture import analyze

RECEIPT=BIN/'lifecycle-qualification.json'


def hashes():
    return {str(p.relative_to(ROOT)):digest(p) for p in (
        BIN/'m1_light_component.dll', BIN/'scene_observer.exe',
        ROOT/'tools/m1_component/m1_live_scene.h', ROOT/'tests/m1_live_scene_tests.cpp',
        Path(__file__), ROOT/'tools/remix_runtime/lifecycle_capture.py')}


def require_qualification():
    q=json.loads(RECEIPT.read_text())
    if q.get('result')!='OFFLINE_LIFECYCLE_WORKER_PASS' or q.get('hashes')!=hashes():
        raise ValueError('Lifecycle worker qualification stale or missing;no game launched')
    return q


def qualify():
    receiver=Receiver();directory=BIN/('lifecycle-'+uuid.uuid4().hex);directory.mkdir()
    try:
        env={**os.environ,'SFC_NATIVE_LIGHT_DISCOVERY':'1','SFC_LIGHT_TUNING':'1','SFC_LIFECYCLE_CAPTURE':'1'}
        env.pop('SFC_REMIX_CALIBRATION_SCENE',None)
        run=sp.run([str(BIN/'scene_observer.exe'),receiver.name,str(directory)],env=env,
                   stdout=sp.PIPE,stderr=sp.STDOUT,timeout=12,creationflags=sp.CREATE_NO_WINDOW)
        (directory/'test.txt').write_bytes(run.stdout)
        if run.returncode:raise ValueError('Native lifecycle worker test failed')
        result=analyze(directory);worker=result['worker']
        if result['owners']['2']['records']<=100:raise ValueError('Detail still ends at old100record limit')
        if not any(r['owner']==2 and r['status']==2 and r['frame']==640 for r in result['transitions']):
            raise ValueError('Coalesced retirement missing from journal')
        if not any(r['owner']==1001 and r['revision']==8 for r in result['transitions']):
            raise ValueError('New epoch transition missing')
        if any(worker[k] for k in ('io_failed','saturated','lifecycle_dropped','lifecycle_omitted','lifecycle_pending')):
            raise ValueError('Lifecycle worker did not drain cleanly within bounds')
        # One drop is forced by the native lock-contention test; concurrent worker
        # contention may add more. Required transition receipts above must exist.
        if worker['dropped']<1:raise ValueError('Synthetic contention was not counted')
        (directory/'analysis.json').write_text(json.dumps(result,indent=2))
        RECEIPT.write_text(json.dumps(dict(result='OFFLINE_LIFECYCLE_WORKER_PASS',hashes=hashes(),evidence=str(directory.relative_to(ROOT)),sfc_launched=False),indent=2))
        require_qualification();print('Lifecycle actual worker,late detail,retirement/reappearance,queue bounds PASS')
    finally:receiver.close()


if __name__=='__main__':qualify()

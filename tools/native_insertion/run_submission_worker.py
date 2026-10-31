"""Actual native publication while its optional calibration mirror is busy."""
import json,os,subprocess as sp,sys,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
from present_calibration import Receiver
from live_owner_timing import initialize
import multi_scene

def main():
    out=ROOT/'artifacts/player-replacement/submission-tests'
    folder=out/('worker-'+uuid.uuid4().hex);folder.mkdir(parents=True)
    receiver=Receiver()
    try:
        initialize(receiver.channel,persistent=True);multi_scene.initialize(receiver.channel)
        env={**os.environ,'SFC_PERSISTENT_SCENE':'1','SFC_REMIX_CALIBRATION_SCENE':receiver.name,'SFC_D3D9_SOURCE_TIMING':'1','SFC_D3D9_LIVE_TIMING':'1','SFC_D3D9_MULTISCENE':'1'}
        for name in ('SFC_D3D9_GAME_OUTPUT','SFC_D3D9_SHARED_LIGHTS','SFC_NATIVE_INSERTION_GATE','SFC_NATIVE_INSERTION_ALL_SHIPS'):env.pop(name,None)
        run=sp.run([str(out/'native_scene.exe'),receiver.name,str(folder)],env=env,stdout=sp.PIPE,stderr=sp.STDOUT,timeout=10,creationflags=sp.CREATE_NO_WINDOW)
        (folder/'console.txt').write_bytes(run.stdout)
        if run.returncode:raise ValueError('Native diagnostic-isolation test failed: '+run.stdout.decode(errors='replace'))
        data=json.loads((folder/'PERSISTENT-SCENE-001.json').read_text())
        if data['publications']!=120 or data['failed_updates'] or data['calibration_misses']!=1:raise ValueError('Native publication/calibration counts differ')
        receipt=dict(calibration_isolated=True,exit_code=run.returncode,folder=folder.relative_to(ROOT).as_posix(),counts=data)
        (out/'worker-result.json').write_text(json.dumps(receipt,indent=2));print('Native calibration isolation PASS;120 current poses,1 diagnostic miss,0 functional failures')
    finally:receiver.close()

if __name__=='__main__':main()

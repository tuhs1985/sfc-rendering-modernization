"""Exact static bytes plus actual external ReadProcessMemory synthetic fixture."""
import hashlib
import json
from pathlib import Path
import subprocess as sp
import sys
from offscreen_position import ROOT,verify_client

RECEIPT=ROOT/'artifacts/d3d9-proof/offscreen-position-qualification.json'
NAMES=('tools/remix_runtime/offscreen_position.py','tools/remix_runtime/qualify_offscreen_position.py',
    'tools/remix_runtime/run_return_game.py','tools/remix_runtime/start_return_image_session.ps1',
    'tools/d3d9_proof/start_d3d9_offscreen_position_session.ps1',
    'tests/test_offscreen_position.py','tests/offscreen_position_child.py')


def hashes():return {n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in NAMES}


def require_qualification():
    q=json.loads(RECEIPT.read_text())
    if q.get('result')!='OFFLINE_EXTERNAL_POSE_READER_PASS' or q.get('sources')!=hashes():
        raise ValueError('Offscreen read-only probe qualification stale/missing;no game launch')
    return q


def qualify():
    static=verify_client(Path(r'C:\Project\SFC-Remix-Return-Test\StarFleetOP.exe'))
    result=sp.run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_offscreen_position.py'],
        cwd=ROOT,stdout=sp.PIPE,stderr=sp.STDOUT,timeout=30,creationflags=sp.CREATE_NO_WINDOW)
    log=ROOT/'artifacts/d3d9-proof/offscreen-position-tests.txt';log.write_bytes(result.stdout)
    if result.returncode:raise ValueError('Actual external-reader tests failed;see '+str(log))
    RECEIPT.write_text(json.dumps(dict(result='OFFLINE_EXTERNAL_POSE_READER_PASS',sources=hashes(),
        static=static,test_log_sha256=hashlib.sha256(result.stdout).hexdigest(),sfc_launched=False,
        limitation='Synthetic memory lifetime only;game offscreen motion and native generation not yet qualified'),indent=2))
    require_qualification();print('External read-only pose fixture and exact native source anchors PASS;no SFC launched')


if __name__=='__main__':qualify()

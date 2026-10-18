"""No game launch: reversible transaction ONLY in the fixed isolated test copy."""
import datetime as dt
import json
from windows_processes import game_running
from broad_capture import ROOT,FULL_SHA,OLD_SHA,install_test_proxy,restore_test_proxy,digest
from run_return_fixture import TEST

def main():
    if game_running():raise RuntimeError('Exit SFC normally first; no proxy changes')
    q=json.loads((ROOT/'artifacts/remix-runtime/deps/reshade-full-6.7.1/qualification.json').read_text())
    if q.get('result')!='OFFLINE_EVENT_AND_STATE_PASS' or q.get('proxy_sha256')!=FULL_SHA:raise RuntimeError('Offline qualification required first')
    work=ROOT/'artifacts/remix-runtime/runs'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f-broad-rollback');work.mkdir()
    target=TEST/'dxgi.dll';backup=work/'dxgi-original.rollback';before=digest(target);installed=None;error=None
    try:
        install_test_proxy(target,backup);installed=digest(target)
    except Exception as exc:error=str(exc)
    finally:
        if backup.exists():restore_test_proxy(target,backup)
    result={'before':before,'installed':installed,'after':digest(target),'expected_original':OLD_SHA,'expected_full':FULL_SHA,'error':error,'game_launched':False,'accepted_install_modified':False}
    (work/'result.json').write_text(json.dumps(result,indent=2))
    if error or before!=OLD_SHA or result['after']!=OLD_SHA or installed!=FULL_SHA:raise RuntimeError('Rollback qualification failed: '+str(work))
    print('Isolated proxy install/rollback PASS: '+str(work))
if __name__=='__main__':main()

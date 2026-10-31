"""Verified interrupted-transaction recovery; never while any SFC is running."""
from pathlib import Path
import argparse
import datetime as dt
import json
import shutil
from broad_capture import ROOT,OLD_SHA,FULL_SHA,digest,restore_test_proxy
from run_return_fixture import TEST

def supported_transaction(manifest):
    return (any(manifest.get(n,{}).get('enabled') is True for n in ('broad_capture','depth_snapshots'))
            or (manifest.get('probe') in ('D3D9-ADDITIVE-001','D3D9-MULTISHIP-001','PLAYER-REPLACEMENT-001','NATIVE-INSERTION-001')
                and isinstance(manifest.get('full_support_qualification'),dict)
                and bool(manifest['full_support_qualification'])))


def recover(run,game_running):
    run=Path(run).resolve()
    if run.parent!=(ROOT/'artifacts/remix-runtime/runs').resolve() or not run.name.endswith('-in-game'):
        raise ValueError('Recovery requires one exact isolated in-game run')
    if game_running():raise RuntimeError('SFC is still running; exit normally before recovery')
    manifest=json.loads((run/'manifest.json').read_text())
    if not supported_transaction(manifest):raise ValueError('Not a full-support capture transaction')
    expected=manifest['copied_critical_before']
    if expected['dxgi.dll']!=OLD_SHA:raise ValueError('Rollback provenance mismatch')
    backup=run/'dxgi-original.rollback';config=run/'ReShade.original.ini'
    if digest(backup)!=OLD_SHA or digest(config)!=expected['ReShade.ini']:raise ValueError('Rollback file hash mismatch')
    # Validate all other frozen inputs before touching either target.
    for name,sha in expected.items():
        if name not in ('dxgi.dll','ReShade.ini') and digest(TEST/name)!=sha:raise ValueError('Unrelated copied baseline changed: '+name)
    if digest(TEST/'dxgi.dll') not in (OLD_SHA,FULL_SHA):raise ValueError('Unknown proxy; no overwrite')
    record=run/'recovery.json'
    if record.exists():raise ValueError('Recovery record already exists; inspect rather than overwrite')
    if (TEST/'ReShade.log').exists():
        if (TEST/'ReShade.log').stat().st_size>16*1024*1024:raise ValueError('Recovery log exceeds bounded-copy limit')
        shutil.copyfile(TEST/'ReShade.log',run/'ReShade.recovery.log')
    shutil.copyfile(TEST/'ReShade.ini',run/'ReShade.before-recovery.ini')
    restore_test_proxy(TEST/'dxgi.dll',backup)
    from broad_capture import atomic_copy
    atomic_copy(config,TEST/'ReShade.ini',expected['ReShade.ini'])
    after={name:digest(TEST/name) for name in expected}
    if after!=expected:raise ValueError('Recovery did not restore complete baseline')
    record.write_text(json.dumps({'utc':dt.datetime.now(dt.timezone.utc).isoformat(),'proxy_restored':True,'config_restored':True,'game_absent_verified':True,'critical_after':after,'historical_result_unchanged':True},indent=2))
    return str(record)

def recover_pending(game_running):
    pending=[]
    for run in (ROOT/'artifacts/remix-runtime/runs').glob('*-in-game'):
        if not (run/'dxgi-original.rollback').exists() or (run/'recovery.json').exists():continue
        manifest=json.loads((run/'manifest.json').read_text())
        if not supported_transaction(manifest):continue
        result=run/'result.json'
        if result.exists() and json.loads(result.read_text()).get('broad_proxy_restored') is True:continue
        pending.append(run)
    if len(pending)>1:raise RuntimeError('Multiple unfinished broad transactions; select exact recovery run for review')
    if pending:return recover(pending[0],game_running)
    return None

if __name__=='__main__':
    from windows_processes import game_running
    p=argparse.ArgumentParser();p.add_argument('run',type=Path);args=p.parse_args()
    print('Verified recovery: '+recover(args.run,game_running))

"""Default-off player-fixture replacement receipts and independent launch gate."""
from pathlib import Path
import hashlib,json,struct
OFFSET=12*1024*1024-64*1024
ROOT=Path(__file__).resolve().parents[2]
RECEIPT=ROOT/'artifacts/player-replacement/qualification.json'


def summary(channel):
    raw=channel.read(OFFSET,4416)
    if len(raw)!=4416:raise ValueError('Replacement ledger incomplete')
    h=struct.unpack_from('<8I',raw)
    if h[:3]!=(0x31525053,1,4416):raise ValueError('Replacement ledger schema/layout')
    c=struct.unpack_from('<10IQ',raw,72)
    names=('native_capable','renderer_capable','suppressed','rejected','committed','repeated','recovered','native_stop','native_restored_frame','repeat_max','native_frame')
    stats=dict(zip(names,struct.unpack_from('<11I',raw,4352)))
    return dict(stats,mode=c[0],generation=c[1],owner=c[2],revision=c[3],epoch=c[7],
                pid=h[3],session=list(h[4:8]))


def finish(relay,pid):
    value=summary(relay.receiver.channel)
    (relay.folder/'PLAYER-REPLACEMENT-001.bin').write_bytes(relay.receiver.channel.read(OFFSET,4416))
    report=dict(result='PLAYER_REPLACEMENT_SPONSOR_REVIEW_REQUIRED' if value['committed'] and value['suppressed'] else 'PARTIAL',
                replacement=value,normal_owned_exit=bool(relay.process and relay.process.returncode==0),
                game_output=dict(drawn=value['committed']),selected=relay.selected,
                scope='Player-fixture only;actual gameplay requires sponsor confirmation;synthetic fixture is not SFC proof')
    return report


def locks():
    from qualify_d3d9_tuning import tuning_locks
    return tuning_locks()


def require_qualification():
    from async_material_checkout import backend_inputs,receipt
    from rendering_config import DEFAULT
    from image_controls import encode as image
    from material_controls import encode as material
    from quality_controls import encode as quality
    q=json.loads(RECEIPT.read_text());backend=backend_inputs()
    if q['locks']!=locks() or q['backend']!=receipt(backend) or q['result']!='OFFLINE_PLAYER_REPLACEMENT_PREPARED_NOT_SFC_PASS':raise ValueError('Player replacement qualification stale')
    for p in q['evidence']:
        path=ROOT/p['path']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=p['sha256']:raise ValueError('Replacement evidence changed')
    raw=DEFAULT.read_bytes();image(raw);material(raw);quality(raw)
    return {**q,'backend_inputs':receipt(backend)}


def qualify(steady,faults):
    from async_material_checkout import backend_inputs,receipt
    from owner_selection import selected_model
    proofs=[]
    for folder,fault in ((Path(steady).resolve(),False),(Path(faults).resolve(),True)):
        folder.relative_to(ROOT/'artifacts/remix-runtime/runs')
        result=json.loads((folder/'result.json').read_text());report=result.get('live_owner_timing') or {}
        actual=result.get('multi_ship_build_locks') or {}
        actual=json.loads(json.dumps(actual))
        for name in ('rendering','lights'):actual.get('configs',{}).pop(name,None)
        if actual!=locks():raise ValueError('Replacement fixture source/binary/placement locks differ')
        counts=report.get('replacement') or {};log=(folder/'fixture.log').read_text()
        if (result.get('error') or not result.get('player_replacement_fixture') or
                bool(result.get('replacement_faults_fixture'))!=fault or result.get('fixture_exit') or result.get('host_exit')):
            raise ValueError('Replacement fixture incomplete')
        if report.get('result')!='PLAYER_REPLACEMENT_SPONSOR_REVIEW_REQUIRED' or not report.get('normal_owned_exit') or counts.get('committed',0)<100 or not counts.get('suppressed'):
            raise ValueError('Actual replacement output/receipt chain incomplete')
        if counts.get('repeat_max',99)>2:raise ValueError('Replacement hold bound exceeded')
        if 'state_errors=0 resized=1 recreated=1' not in log or 'native_HUD_and_scene_exact=1' not in log:raise ValueError('Replacement GPU state/frame/reset proof missing')
        if report['selected'].get('camera_offset')!=[0,0,0] or report['selected'].get('selected_model')!=selected_model():raise ValueError('Player fixture selection/placement mismatch')
        if fault:
            if 'REPLACEMENT_SINGLE_MISS_RECOVERED' not in log or 'REPLACEMENT_SUSTAINED_MISS_NATIVE' not in log or not counts.get('recovered'):raise ValueError('Actual missed-output recovery not proved')
        else:
            import re
            window=re.search(r'GAME_DELIVERY_WINDOW frames=(\d+) draws=(\d+)',log)
            if not window or int(window[1])<600 or int(window[2])<.9*int(window[1]) or counts.get('recovered'):raise ValueError('Unforced replacement delivery not stable')
        proofs.append(dict(path=str((folder/'result.json').relative_to(ROOT)),sha256=hashlib.sha256((folder/'result.json').read_bytes()).hexdigest()))
    for name in ('transaction32.txt','transaction64.txt','component.txt'):
        p=ROOT/'artifacts/player-replacement/run208'/name
        if 'PASS' not in p.read_text():raise ValueError('Native replacement checks incomplete')
        proofs.append(dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    RECEIPT.parent.mkdir(parents=True,exist_ok=True)
    RECEIPT.write_text(json.dumps(dict(result='OFFLINE_PLAYER_REPLACEMENT_PREPARED_NOT_SFC_PASS',locks=locks(),backend=receipt(backend_inputs()),evidence=proofs,
        limitations=['Unique configured player-fixture model,not engine player flag','No SFC suppression runtime proof yet','At most two extra game-frame repeats;recovery latches native until restart']),indent=2))
    require_qualification();print('Player replacement offline gate PASS;not gameplay PASS')


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--steady',type=Path,required=True);p.add_argument('--faults',type=Path,required=True);a=p.parse_args();qualify(a.steady,a.faults)

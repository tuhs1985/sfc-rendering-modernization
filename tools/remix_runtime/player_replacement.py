"""Default-off player-fixture replacement receipts and independent launch gate."""
from pathlib import Path
import hashlib,json,struct,re
OFFSET=12*1024*1024-64*1024
ROOT=Path(__file__).resolve().parents[2]
RECEIPT=ROOT/'artifacts/player-replacement/qualification.json'


def summary(channel):
    raw=channel.read(OFFSET,4416)
    if len(raw)!=4416:raise ValueError('Replacement ledger incomplete')
    h=struct.unpack_from('<8I',raw)
    if h[0]!=0x31525053 or h[1] not in (1,2) or h[2]!=4416:raise ValueError('Replacement ledger schema/layout')
    c=struct.unpack_from('<10IQ',raw,72)
    names=('native_capable','renderer_capable','suppressed','rejected','committed','repeated','recovered','native_stop','native_restored_frame','repeat_max','native_frame')
    stats=dict(zip(names,struct.unpack_from('<11I',raw,4352)))
    if h[1]==2:stats.update(zip(('rearmed','native_presentations','recovery_reason'),struct.unpack_from('<3I',raw,4396)))
    return dict(stats,protocol=h[1],mode=c[0],generation=c[1],owner=c[2],revision=c[3],epoch=c[7],reason=c[9],
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
        native=(folder/'gpu/job-console.log').read_text()
        if 'PHYSICAL_HULL_DEPTH enabled=1 reflected_depth_used=0' not in native or 'PHYSICAL_HULL_SUMMARY batches=' not in native:
            raise ValueError('Physical first-hull depth must be exercised;PSR depth is not hull coverage')
        if counts.get('protocol')!=2:raise ValueError('Automatic recovery protocol2 fixture required')
        if (result.get('error') or not result.get('player_replacement_fixture') or
                bool(result.get('replacement_faults_fixture'))!=fault or result.get('fixture_exit') or result.get('host_exit')):
            raise ValueError('Replacement fixture incomplete')
        if report.get('result')!='PLAYER_REPLACEMENT_SPONSOR_REVIEW_REQUIRED' or not report.get('normal_owned_exit') or counts.get('committed',0)<100 or not counts.get('suppressed'):
            raise ValueError('Actual replacement output/receipt chain incomplete')
        if counts.get('repeat_max',99)>2:raise ValueError('Replacement hold bound exceeded')
        if 'state_errors=0 resized=1 recreated=1' not in log or 'native_HUD_and_scene_exact=1' not in log:raise ValueError('Replacement GPU state/frame/reset proof missing')
        if report['selected'].get('camera_offset')!=[0,0,0] or report['selected'].get('selected_model')!=selected_model():raise ValueError('Player fixture selection/placement mismatch')
        if fault:
            if any(marker not in log for marker in ('REPLACEMENT_SINGLE_MISS_RECOVERED','REPLACEMENT_SUSTAINED_MISS_NATIVE','REPLACEMENT_AUTO_RESUMED','REPLACEMENT_SOURCE_GAP_RESUMED','REPLACEMENT_STOP_STAYS_NATIVE')) or counts.get('recovered',0)<2 or counts.get('rearmed',0)<2:raise ValueError('Actual missed-output/camera-gap recovery and automatic resume not proved')
            native=(folder/'gpu/job-console.log').read_text()
            if not re.search(r'MULTISCENE_SUMMARY [^\n]*\bloads=1\b',native):raise ValueError('Recovery must reuse the one retained ship asset')
        else:
            window=re.search(r'GAME_DELIVERY_WINDOW frames=(\d+) draws=(\d+)',log)
            if not window or int(window[1])<600 or int(window[2])<.9*int(window[1]) or counts.get('recovered'):raise ValueError('Unforced replacement delivery not stable')
        proofs.append(dict(path=str((folder/'result.json').relative_to(ROOT)),sha256=hashlib.sha256((folder/'result.json').read_bytes()).hexdigest()))
    hull_test=ROOT/'artifacts/d3d9-proof/direct64-bin/physical-hull-depth-tests.txt'
    if 'Physical hull GPU PASS' not in hull_test.read_text():raise ValueError('Physical hull GPU proof missing')
    proofs.append(dict(path=str(hull_test.relative_to(ROOT)),sha256=hashlib.sha256(hull_test.read_bytes()).hexdigest()))
    for name in ('transaction32.txt','transaction64.txt','component.txt'):
        p=ROOT/'artifacts/player-replacement/native-tests'/name
        if 'PASS' not in p.read_text():raise ValueError('Native replacement checks incomplete')
        proofs.append(dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    RECEIPT.parent.mkdir(parents=True,exist_ok=True)
    RECEIPT.write_text(json.dumps(dict(result='OFFLINE_PLAYER_REPLACEMENT_PREPARED_NOT_SFC_PASS',locks=locks(),backend=receipt(backend_inputs()),evidence=proofs,
        limitations=['Unique configured player-fixture model,not engine player flag','Previous live replacement observed;automatic recovery still requires sponsor checkout','At most two extra complete-picture repeats;native fallback automatically reprimes fresh paired output;explicit stop remains latched']),indent=2))
    require_qualification();print('Player replacement offline gate PASS;not gameplay PASS')


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--steady',type=Path,required=True);p.add_argument('--faults',type=Path,required=True);a=p.parse_args();qualify(a.steady,a.faults)

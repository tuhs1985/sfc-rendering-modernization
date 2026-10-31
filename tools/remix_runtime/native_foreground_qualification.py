"""Default-off native shield foreground checkout and bounded source receipt."""
from pathlib import Path
import hashlib,json,struct
from player_replacement import ROOT,OFFSET as REPLACEMENT_OFFSET,locks
OFFSET=REPLACEMENT_OFFSET+8192
BYTES=4160
RECEIPT=ROOT/'artifacts/player-replacement/native-foreground-qualification.json'


def save(channel,folder):
    raw=channel.read(OFFSET,BYTES)
    if len(raw)!=BYTES:raise ValueError('Native foreground receipt incomplete')
    h=struct.unpack_from('<8I',raw)
    if h[0]!=0x31464753 or h[1]!=1 or h[2]!=BYTES or not h[3]:raise ValueError('Native foreground schema/pid')
    names=('flags','eligible_frames','partial_frames','captured_draws','replayed_draws','retained_bytes','setup_rejections','hooks_restored')
    result=dict(zip(names,struct.unpack_from('<8I',raw,32)))
    result['last_presentation_flags']=result['flags']
    # The worker's teardown ACK can be newer than the final presentation stamp.
    if result['hooks_restored']==1:result['flags']=(result['flags']|16)&~1
    elif result['hooks_restored']==2:result['flags']|=2
    if result['retained_bytes']>32*1024*1024:raise ValueError('Native foreground retained32MiB cap')
    result.update(pid=h[3],session=list(h[4:8]),packed_native_depth='D24S8;invalid bit2,replacement bit0',output_budget_bytes=1920*1080*4*16)
    folder=Path(folder);(folder/'NATIVE-FOREGROUND-001.bin').write_bytes(raw)
    (folder/'NATIVE-FOREGROUND-001.json').write_text(json.dumps(result,indent=2))
    return result


def qualify(steady,faults):
    evidence=[]
    native=ROOT/'artifacts/player-replacement/native-foreground-tests'
    manifest=json.loads((native/'build.json').read_text(encoding='utf-8-sig'))
    for name,digest in manifest.items():
        path=(ROOT/name).resolve();path.relative_to(ROOT)
        if hashlib.sha256(path.read_bytes()).hexdigest().upper()!=digest:raise ValueError('Native foreground native build/input stale')
    import re
    for name,pattern,minimum in (('resources',r'GPU PASS (\d+) checks',269),('scope',r'ABI hook PASS (\d+) checks',17)):
        match=re.search(pattern,(native/f'{name}.txt').read_text(encoding='utf-8-sig'))
        if not match or int(match[1])<minimum:raise ValueError('Native foreground focused tests incomplete')
    for name in ('build.json','resources.exe','resources.txt','scope.exe','scope.txt'):
        p=native/name;evidence.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    for path,fault in ((steady,False),(faults,True)):
        path=Path(path).resolve();path.relative_to(ROOT/'artifacts/remix-runtime/runs')
        result=json.loads((path/'result.json').read_text());log=(path/'fixture.log').read_text()
        foreground=result.get('native_foreground') or {}
        if result.get('error') or result.get('fixture_exit')!=0 or not result.get('native_foreground_fixture'):raise ValueError('Native foreground fixture failed')
        if result.get('replacement_faults_fixture')!=fault:raise ValueError('Native foreground fault profile mismatch')
        if foreground.get('hooks_restored')!=1 or foreground.get('flags',0)&2 or not foreground.get('flags',0)&16:raise ValueError('Native foreground hook cleanup/readiness failed')
        if foreground.get('replayed_draws',0)<6 or foreground.get('captured_draws',0)<6 or foreground.get('setup_rejections'):raise ValueError('Native foreground drawing/admission incomplete')
        if log.count('NATIVE_FOREGROUND_PIXELS_PASS ')<3 or 'NATIVE_FOREGROUND_FIXTURE_END verified=3' not in log:raise ValueError('Native foreground exact matched-frame pixels unproved')
        actual=json.loads(json.dumps(result.get('multi_ship_build_locks') or {}))
        for name in ('rendering','lights'):actual.get('configs',{}).pop(name,None)
        if actual!=locks():raise ValueError('Native foreground fixture source/binary locks differ')
        for name in ('result.json','fixture.log','NATIVE-FOREGROUND-001.bin'):
            p=path/name;evidence.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    q=dict(result='OFFLINE_NATIVE_FOREGROUND_PREPARED_NOT_SFC_PASS',locks=locks(),evidence=evidence)
    RECEIPT.write_text(json.dumps(q,indent=2));return q


def require_qualification():
    q=json.loads(RECEIPT.read_text())
    if q['result']!='OFFLINE_NATIVE_FOREGROUND_PREPARED_NOT_SFC_PASS' or q['locks']!=locks():raise ValueError('Native foreground qualification stale')
    for proof in q['evidence']:
        if hashlib.sha256((ROOT/proof['path']).read_bytes()).hexdigest()!=proof['sha256']:raise ValueError('Native foreground evidence changed')
    return q


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--steady',required=True);p.add_argument('--faults',required=True)
    a=p.parse_args();print(qualify(a.steady,a.faults)['result'])

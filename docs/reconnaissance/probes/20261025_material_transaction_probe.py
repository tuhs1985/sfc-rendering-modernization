"""Run191 standalone completed-stage transaction; no production/default edits."""
import argparse
from collections import deque
import hashlib
import json
from pathlib import Path
import sys
import time
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'tools/remix_runtime'),str(ROOT/'tools/d3d9_proof')]
HERE=ROOT/'artifacts/material-transaction'


def transaction_flush(self):
    """Keep bounded per-group IO, but publish only complete per-asset stages.

    No waiting for other owners or bootstrap; each finished revision proceeds.
    Original retry_publication retains atomic replacement/release semantics.
    """
    processed=0
    while self.pending_enhancements and processed<4:
        kind,value=self.pending_enhancements[0]
        job=value if kind=='complete' else value[0]
        if not job.get('published'):break
        self.pending_enhancements.popleft()
        if job['phase']=='failed':continue
        if kind=='complete':
            expected={g[0] for g in job['manifest']['groups']}
            if set(self.material_pieces.get(job['id'],{}))!=expected:
                raise ValueError('Completed material revision missing groups;retain base')
            self.pending_stage_ids.add(job['id'])
            self.pending_complete_ids.add(job['id'])
            continue
        _,piece=value
        try:self.accept_piece(job,piece)
        except (ValueError,OSError) as exc:self.fail_job(job,exc)
        processed+=1
    self.retry_publication()


def self_test():
    def relay():
        calls=[]
        r=SimpleNamespace(pending_enhancements=deque(),pending_stage_ids=set(),pending_complete_ids=set(),material_pieces={})
        def accept(job,piece):r.material_pieces.setdefault(job['id'],{})[piece]=True;calls.append(('piece',job['id'],piece))
        r.accept_piece=accept
        r.fail_job=lambda job,error:job.update(phase='failed')
        r.retry_publication=lambda:calls.append(('retry',set(r.pending_stage_ids),set(r.pending_complete_ids)))
        return r,calls
    def job(i,n=2):return dict(id=i,published=True,phase='ready',manifest={'groups':[(j,0,0,0) for j in range(n)]})
    r,calls=relay();a,b=job(1),job(2)
    r.pending_enhancements.extend([('piece',(a,0)),('piece',(b,0)),('piece',(a,1)),('complete',a)])
    transaction_flush(r)
    assert r.pending_stage_ids=={1} and r.pending_complete_ids=={1} and set(r.material_pieces[2])=={0}
    r,calls=relay();a=job(1,8)
    r.pending_enhancements.extend(('piece',(a,i)) for i in range(8));r.pending_enhancements.append(('complete',a))
    transaction_flush(r);assert len(r.material_pieces[1])==4 and not r.pending_stage_ids
    transaction_flush(r);assert len(r.material_pieces[1])==8 and not r.pending_stage_ids
    transaction_flush(r);assert r.pending_stage_ids=={1}
    r,calls=relay();a=job(1);a['published']=False
    r.pending_enhancements.append(('piece',(a,0)));transaction_flush(r)
    assert len(r.pending_enhancements)==1 and not r.material_pieces
    r,calls=relay();a=job(1);a['phase']='failed'
    r.pending_enhancements.extend([('piece',(a,0)),('complete',a)]);transaction_flush(r)
    assert not r.pending_stage_ids and not r.material_pieces
    r,calls=relay();a=job(1);r.pending_enhancements.append(('complete',a))
    try:transaction_flush(r)
    except ValueError:pass
    else:raise AssertionError('Incomplete revision accepted')
    print('Transaction probe self-check PASS: independent owners,bounded drain,base-first,failure,incomplete revision')


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def prepare_slow_frame_host():
    HERE.mkdir(exist_ok=True)
    source=(ROOT/'tools/d3d9_proof/d3d9_direct_host.cpp').read_text()
    needle='if((admission.enabled||startup.enabled)&&(frame==0||measureCohort))'
    assert source.count(needle)==1
    (HERE/'slow_frame_host.cpp').write_text(source.replace(needle,
        'if((admission.enabled||startup.enabled)&&(frame==0||measureCohort||peerDone-began>frequency.QuadPart/20))'))


def run(control=False,slow_frame_host=False):
    import live_owner_timing as live
    import progressive_scene_relay as progressive
    import run_return_fixture as fixture
    from run_offline import storage,AGGREGATE_BYTES
    HERE.mkdir(exist_ok=True)
    extras=sum(p.stat().st_size for name in ('resource-stall','staging-integration','present-stall','material-transaction') for p in (ROOT/'artifacts'/name).rglob('*') if p.is_file())
    assert storage()+extras+1024**3<AGGREGATE_BYTES,'Existing1GiB fixture reservation required'
    frozen={str(p.relative_to(ROOT)):sha(p) for p in (live.EXE,live.RUNTIME,ROOT/'tools/remix_runtime/progressive_scene_relay.py',ROOT/'tools/d3d9_proof/d3d9_direct_host.cpp')}
    original_host=live.EXE
    if slow_frame_host:
        source=(ROOT/'tools/d3d9_proof/d3d9_direct_host.cpp').read_text()
        needle='if((admission.enabled||startup.enabled)&&(frame==0||measureCohort))'
        assert source.count(needle)==1
        expected=source.replace(needle,'if((admission.enabled||startup.enabled)&&(frame==0||measureCohort||peerDone-began>frequency.QuadPart/20))')
        assert (HERE/'slow_frame_host.cpp').read_text()==expected,'Diagnostic body changed'
        live.EXE=HERE/'slow_frame_host.exe'
        assert live.EXE.is_file() and live.EXE.stat().st_mtime_ns>=(HERE/'slow_frame_host.cpp').stat().st_mtime_ns
    before=set((ROOT/'artifacts/remix-runtime/runs').iterdir())
    if not control:progressive.Relay.flush_enhancements=transaction_flush
    sys.argv=['run_return_fixture.py','--multi-ship','--multi-ship-resources','--prewarm','--startup-profile',
              '--pipeline-mode','performance','--parallel-assets','--asset-admission-service','on','--texture-upload','initial-data']
    try:fixture.main()
    finally:
        assert all(sha(ROOT/name)==value for name,value in frozen.items()),'Production inputs changed'
        folders=set((ROOT/'artifacts/remix-runtime/runs').iterdir())-before
        receipt=dict(diagnostic_only=True,production_qualification_eligible=False,completed_stage_transaction=not control,
                     unchanged_production=frozen,probe_sha256=sha(__file__),folders=[str(p) for p in folders],
                     slow_frame_host=slow_frame_host,actual_host_sha256=sha(live.EXE),
                     scope='Same four-group IO drain;publish each complete per-asset stage once;no bootstrap/all-owner wait;unchanged native host/runtime')
        for folder in folders:
            path=folder/'result.json'
            if path.is_file():
                result=json.loads(path.read_text());result['diagnostic_original_reference_locks']=result.pop('multi_ship_build_locks',None)
                result['production_qualification_eligible']=False;result['material_transaction_probe']=receipt
                path.write_text(json.dumps(result,indent=2))
            (folder/'material-transaction-probe.json').write_text(json.dumps(receipt,indent=2))
        (HERE/('slow-frame.json' if slow_frame_host else 'control.json' if control else 'transaction.json')).write_text(json.dumps(receipt,indent=2))
        live.EXE=original_host


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--self-test',action='store_true');parser.add_argument('--control',action='store_true')
    parser.add_argument('--slow-frame-host',action='store_true')
    parser.add_argument('--prepare-slow-frame-host',action='store_true')
    args=parser.parse_args()
    if args.self_test:self_test()
    elif args.prepare_slow_frame_host:prepare_slow_frame_host()
    else:run(args.control,args.slow_frame_host)

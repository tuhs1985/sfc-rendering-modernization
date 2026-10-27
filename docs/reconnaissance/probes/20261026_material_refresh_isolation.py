"""Run200 standalone material refresh controls. NEVER launches SFC.

Reuse captured KFF/FCA packets and the actual owned renderer/return fixture.
All overrides are scoped to this Python process; no qualification promotion.
Snapshots use NVIDIA's pinned primary-perceptual-roughness view (89).
"""
import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import sys
import time

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(Path(__file__).parent))
for name in ('remix_runtime','d3d9_proof','scene_bridge'):
    sys.path.insert(0,str(ROOT/'tools'/name))


def timestamp_contract():
    """Call the packaged library's public path-based timestamp function.

    No runtime rendering, private addresses, vendor modification or SFC process.
    The exported namespace identifies the shipped OpenUSD25.11 build.
    """
    import ctypes as C
    root=ROOT/'artifacts/remix-runtime/deps/candidate-1.6.1/runtime'
    with os.add_dll_directory(str(root)):
        dll=C.CDLL(str(root/'usd_arch.dll'))
        fn=getattr(dll,'?ArchGetModificationTime@pxrInternal_v0_25_11__pxrReserved__@@YA_NPEBDPEAN@Z')
        fn.argtypes=[C.c_char_p,C.POINTER(C.c_double)];fn.restype=C.c_bool
        path=ROOT/'artifacts/candidate-hot-reload/run200-usd-timestamp.txt'
        path.write_text('unchanged bytes');base=int(path.stat().st_mtime);rows=[]
        for offset in (100_000_000,800_000_000,1_100_000_000):
            ns=base*1_000_000_000+offset;os.utime(path,ns=(ns,ns));out=C.c_double()
            if not fn(str(path).encode('utf-8'),C.byref(out)):raise ValueError('USD timestamp read failed')
            rows.append(dict(requested_ns=ns,actual_ntfs_ns=path.stat().st_mtime_ns,usd_timestamp=out.value))
        assert rows[0]['usd_timestamp']==rows[1]['usd_timestamp']
        assert rows[2]['usd_timestamp']!=rows[1]['usd_timestamp']
    record=dict(dll=str((root/'usd_arch.dll').relative_to(ROOT)),
        sha256=hashlib.sha256((root/'usd_arch.dll').read_bytes()).hexdigest(),
        namespace='pxrInternal_v0_25_11',public_export='ArchGetModificationTime(char const*,double*)',
        observations=rows)
    (ROOT/'artifacts/candidate-hot-reload/run200-usd-timestamp.json').write_text(json.dumps(record,indent=2))
    print(json.dumps(record,indent=2))


def add_unused(text):
    # New identity, same already-prepared image references. No new texture/GPU
    # resources or changes to an existing ship's material definitions.
    match=re.search(r'    def Material "mat_([0-9A-F]{16})"\n.*?(?=    def Material| }\n}\n\Z)',text,re.S)
    if not match:raise ValueError('Expected generated flat material definition')
    identity='F0E1D2C3B4A59687'
    if identity in text:raise ValueError('Unused diagnostic identity collision')
    block=match[0].replace(match[1],identity)
    assert text.endswith(' }\n}\n')
    return text[:-5]+block+' }\n}\n'


def run(mode,view,publication_clock,collide_write_clock=False):
    import async_material_checkout as checkout
    prior=importlib.import_module('20261025_early_material_notice_probe')
    prior.SOURCE=ROOT/'artifacts/remix-runtime/runs/20261026-052012-553947-in-game/gate'
    original_configure=checkout.configure_child
    def configure(backend,env):
        text,receipt=original_configure(backend,env)
        return text+f'rtx.debugView.debugViewIdx = {view}\n',dict(receipt,diagnostic_debug_view=view)
    checkout.configure_child=configure
    events=[];publications=[]
    if collide_write_clock:
        original_write=Path.write_text
        def write(path,*args,**kwargs):
            result=original_write(path,*args,**kwargs)
            if (path.name=='mod.usda.pending'
                    and path.parent.parts[-4:]==('gpu','rtx-remix','mods','sfc-policy')):
                previous=path.with_name('mod.usda').stat().st_mtime_ns
                ns=(previous//1_000_000_000)*1_000_000_000+100_000_000
                os.utime(path,ns=(ns,ns))
            return result
        Path.write_text=write
    original_replace=Path.replace
    def replace(path,target):
        target=Path(target)
        # Only the top-level master, never the
        # worker-owned per-asset stages. Preserve content and atomic exchange.
        master=(path.name=='mod.usda.pending' and target.name=='mod.usda'
                and path.parent.parts[-4:]==('gpu','rtx-remix','mods','sfc-policy'))
        if master:
            before=target.stat().st_mtime_ns
            natural=path.stat().st_mtime_ns
            if publication_clock!='natural':
                second=before//1_000_000_000+(publication_clock=='distinct')
                os.utime(path,ns=(natural,second*1_000_000_000))
            publications.append(dict(at_ns=time.perf_counter_ns(),previous_mtime_ns=before,
                natural_mtime_ns=natural,published_mtime_ns=path.stat().st_mtime_ns,
                content_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        return original_replace(path,target)
    Path.replace=replace
    original_flush=checkout.Relay.flush_enhancements
    def flush(self):
        snapshot=self.folder/'fixture-ship.bmp'
        if mode=='after-snapshot' and not snapshot.is_file():return
        original_flush(self)
        if mode!='unused-material' or events or not snapshot.is_file():return
        if (not self.material_events or self.pending_enhancements
                or self.pending_stage_ids or self.pending_library):return
        if any(j['phase'] not in ('ready','alias') for j in self.preparer.jobs.values()):return
        master=self.folder/'gpu/rtx-remix/mods/sfc-policy/mod.usda'
        before=master.read_text(encoding='utf-8');after=add_unused(before)
        pending=master.with_suffix('.diagnostic.pending')
        pending.write_text(after,encoding='utf-8');pending.replace(master)
        events.append(dict(at_ns=time.perf_counter_ns(),event='unused-material-added',
            before_sha256=hashlib.sha256(before.encode()).hexdigest(),
            after_sha256=hashlib.sha256(after.encode()).hexdigest(),
            previous_materials_unchanged=True,new_image_files=0,new_geometry=0))
    checkout.Relay.flush_enhancements=flush
    before=set((ROOT/'artifacts/remix-runtime/runs').iterdir())
    try:prior.run('none',ready_first=True)
    finally:
        for folder in set((ROOT/'artifacts/remix-runtime/runs').iterdir())-before:
            record=dict(mode=mode,debug_view=view,publication_clock=publication_clock,
                collide_write_clock=collide_write_clock,publications=publications,events=events,
                diagnostic_only=True,production_qualification_eligible=False,
                source=str(prior.SOURCE.relative_to(ROOT)),
                probe_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                meaning='Two saved ships in synthetic fixed poses;not gameplay or material-ready ACK')
            (folder/'material-refresh-isolation.json').write_text(json.dumps(record,indent=2))
            result=folder/'result.json'
            if result.is_file():
                data=json.loads(result.read_text());data['material_refresh_isolation']=record
                data['production_qualification_eligible']=False
                result.write_text(json.dumps(data,indent=2))
            print('ISOLATION_EVIDENCE',folder,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode',choices=('control','unused-material','after-snapshot'))
    parser.add_argument('--timestamp-contract',action='store_true')
    parser.add_argument('--view',type=int,choices=(0,30,89),default=89)
    parser.add_argument('--publication-clock',choices=('natural','same-second','distinct'),default='natural')
    parser.add_argument('--collide-write-clock',action='store_true',help='Fault injection before production timestamp policy;force natural writes into prior USD second')
    args=parser.parse_args()
    if args.timestamp_contract:timestamp_contract()
    elif args.mode:run(args.mode,args.view,args.publication_clock,args.collide_write_clock)
    else:parser.error('Select a control or the packaged timestamp contract')

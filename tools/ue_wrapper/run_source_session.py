"""Explicit copied-game observation using the established session/recovery parent."""
import argparse
import ctypes as C
import json
import os
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[2]
for part in ('src/session','src/rendering/ue'):
    sys.path.insert(0,str(ROOT/part))
from coordinator import Session,preflight,game_running,TEST,CONTEXT,critical_hashes,BIN,digest
from source_service import SourceService,source_environment


def package():
    folder=ROOT/'artifacts/ue-foundation/Shipping'
    receipt=json.loads((folder/'build-receipt.json').read_text(encoding='utf-8-sig'))
    if receipt['configuration']!='Shipping' or receipt['engine']['Changelist']!=58902052:raise ValueError('Qualified UE Shipping build required')
    for name,expected in receipt['source_hashes'].items():
        if name.startswith('external/'):
            leaf=name.removeprefix('external/');path=ROOT/leaf if leaf.startswith(('src/','tools/')) else ROOT/'src'/leaf
        else:path=ROOT/'src/ue_wrapper'/name
        if digest(path).lower()!=expected:raise ValueError('UE package is stale: '+name)
    from qualify_stream import runtime_exe
    return runtime_exe(folder/'package/Windows/SFCUEWrapper.exe')


class ReadOnlySession(Session):
    def _prepare(self):
        p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute',action='store_true');self.args=p.parse_args(self.argv)
        self.args.budget_seconds=285;self.args.native_resolution=False;self.args.damage_textures=False;self.args.break_models=False
        self.service=None;self.inspection_summary={};self.ue_exe=package()
        if self.args.execute:
            if not C.windll.shell32.IsUserAnAdmin():raise ValueError('Use the established elevated parent')
            if game_running():raise ValueError('Exit SFC normally before this observation')
            from session_recovery import recover_pending
            recovered=recover_pending(game_running)
            if recovered:print('Recovered prior interrupted test: '+recovered,flush=True)
        preflight()
        from component_qualification import require_qualification
        self.light_qualification=require_qualification();self.q={'ue_read_only':True,'source_component':self.light_qualification['component_sha256']}
        self.checkout_backend={}
        from evidence_storage import storage
        from evidence_budget import AGGREGATE_BYTES
        ue_evidence=sum(p.stat().st_size for folder in (ROOT/'artifacts/ue-foundation').iterdir()
            if folder.is_dir() and folder.name not in ('Development','Shipping') for p in folder.rglob('*') if p.is_file())
        if storage()+ue_evidence+544*1024**2>AGGREGATE_BYTES:raise ValueError('Observation reservation exceeds20GB evidence allowance')
        if not self.args.execute:
            print(getattr(self,'preflight_message','UE read-only preflight PASS. No game or renderer started.'));return False
        return True

    def _initialize(self):
        super()._initialize();self.deadline=self.start+285
        self.metadata.update(probe='UE-SOURCE-001',scene='Read-only source/camera inspection in a separate UE window',
            original_suppressed=False,native_output=False,ue_executable=str(self.ue_exe),workflow_seconds=285)
        (self.work/'manifest.json').write_text(json.dumps(self.metadata,indent=2))

    def _prepare_game(self):
        from scene_receiver import Receiver
        from live_owner_timing import initialize
        import multi_scene
        self.receiver=Receiver(retain_assets=False)
        initialize(self.receiver.channel,persistent=True);multi_scene.initialize(self.receiver.channel)
        self.env=source_environment(os.environ,self.session,self.receiver.name,TEST/'StarFleetOP.exe')
        self.component_path=CONTEXT.artifact('remix-runtime/native-light-tests/m1_light_component.dll')
        self.metadata['source_session']=self.receiver.name
        (self.work/'manifest.json').write_text(json.dumps(self.metadata,indent=2))

    def _after_launch(self):
        self.service=SourceService(self.receiver,TEST,self.pid,self.work/'ue-source',self.ue_exe);self.service.start()

    def enforce(self):
        if self.exit_monitor:self.exit_monitor.check()
        if self.service:self.service.poll()
        if time.monotonic()>self.deadline:raise RuntimeError('Prepared285second observation complete;exit SFC normally')
        if time.monotonic()-self.last_output_check>5:
            self.last_output_check=time.monotonic()
            total=sum(p.stat().st_size for p in self.work.rglob('*') if p.suffix in ('.log','.jsonl'))
            if total>32*1024**2:raise RuntimeError('Observation logs exceed32MiB')

    def _instructions(self):
        print('SFC draws normally. Enter a familiar skirmish; the separate UE window shows recovered ships and camera.',flush=True)

    def _arm(self):
        self.channel.set('armed',0);self.channel.set('enabled',0);self.active=time.monotonic()

    def _begin_observation(self):
        print('Move/turn and switch cameras. No replacement or enhanced lighting in SFC. Exit SFC normally after a short check.',flush=True)

    def _observe(self):
        while True:self.enforce();time.sleep(.005)

    def _stop_extensions(self):
        if self.service:
            try:self.service.stop();self.inspection_summary=self.service.summary()
            except Exception as exc:self.error=(self.error+'; ' if self.error else '')+'UE shutdown: '+str(exc)

    def _report(self):
        self.result.update(probe='UE-SOURCE-001',source_inspection=self.inspection_summary,
            broad_proxy_restored=self.proxy_restored,original_suppressed=False,native_output=False,
            result='READ_ONLY_SOURCE_CHECKOUT_ENDED' if self.normal and not self.error else 'PARTIAL',final_report_complete=True)
        from reports import save
        save(self.work,self.result)


if __name__=='__main__':ReadOnlySession().run()

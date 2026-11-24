"""Explicit player-only additive UE checkout through existing native insertion."""
import json,struct,time,winsound
from pathlib import Path
from run_source_session import ReadOnlySession,Session,ROOT,CONTEXT,TEST,digest
from native_output_service import AdditiveSourceService,additive_environment

OFFSET=(-15.897722721099854,0.0,0.0)
RECEIVER=ROOT/'artifacts/ue-foundation/gpu-exchange/ue_output_receiver.exe'

class AdditiveSession(ReadOnlySession):
    def _prepare(self):
        self.preflight_message='UE additive preflight PASS. No game or renderer started.'
        if not RECEIVER.is_file():raise ValueError('Build the qualified UE output receiver first')
        from qualify_native_gate import require_native_qualification
        qualification=require_native_qualification()
        ready=super()._prepare()
        self.args.native_resolution=True;self.native_capture=None;self.native_result=None
        self.tactical_started=None;self.exit_requested=False
        self.q.update(ue_additive=True,native_qualification=qualification['evidence'],receiver_sha256=digest(RECEIVER),world_offset=list(OFFSET))
        return ready

    def _initialize(self):
        super()._initialize()
        self.metadata.update(probe='UE-ADDITIVE-001',scene='Selected player at fixed native-world X offset; original drawing enabled',
            native_output=True,native_all_ships=False,world_offset=list(OFFSET),timing_policy='ExtraFrame',capture_seconds=90,
            full_support_qualification=self.q,ue_receiver=str(RECEIVER),ue_receiver_sha256=digest(RECEIVER))
        (self.work/'manifest.json').write_text(json.dumps(self.metadata,indent=2))

    def _prepare_game(self):
        super()._prepare_game()
        self.env=additive_environment(self.env)
        # Explicit bounded checkout timing, not normal-play diagnostic imports.
        self.env['SFC_PLAY_SESSION']='0'
        from native_gate import Capture
        words=struct.unpack('<4I',self.receiver.channel.read(16,16))
        self.native_capture=Capture(self.receiver.channel,self.work,list(words))

    def _configure_controller(self):
        super()._configure_controller()
        # This bounded diagnostic checkout has PLAY_SESSION=0. Zero duration
        # belongs to untimed play and is explicitly refused by the controller.
        duration=str(self.args.budget_seconds)
        self.controller_args[self.controller_args.index('--max-seconds')+1]=duration
        from native_config import write
        write(self.config,self.config.read_text(encoding='utf-16').replace('MaxSeconds=0\n','MaxSeconds='+duration+'\n'))

    def _after_launch(self):
        self.service=AdditiveSourceService(self.receiver,TEST,self.pid,self.work/'ue-source',self.ue_exe,
            consumer=RECEIVER,world_offset=OFFSET,environment=self.env)
        self.service.start()

    def _instructions(self):
        print('Enter the usual F-CA skirmish. Original ships stay visible; look for the extra textured player ship beside yours.',flush=True)

    def _arm(self):
        Session._arm(self)

    def _begin_observation(self):
        print('Rotate and zoom the camera, move and turn, expose shields, and pause briefly. Exit normally at the two-beep cue.',flush=True)

    def enforce(self):
        super().enforce()
        if self.native_capture and self.native_capture.error:raise RuntimeError('Native timing capture: '+self.native_capture.error)
        if self.service and self.service.last and self.tactical_started is None:self.tactical_started=time.monotonic()
        if self.tactical_started is not None and not self.exit_requested and time.monotonic()-self.tactical_started>=90:
            self.exit_requested=True;winsound.Beep(880,200);winsound.Beep(880,200)
            print('Checkout complete. Please exit SFC normally.',flush=True)

    def _stop_extensions(self):
        super()._stop_extensions()
        if self.native_capture:
            try:self.native_result=self.native_capture.finish()
            except Exception as exc:self.error=(self.error+'; ' if self.error else '')+'Native timing shutdown: '+str(exc)

    def _report(self):
        self.result.update(source_inspection=self.inspection_summary,broad_proxy_restored=self.proxy_restored,
            original_suppressed=False,final_report_complete=True,probe='UE-ADDITIVE-001',native_output=True,world_offset=list(OFFSET),native_gate=self.native_result,
            result='ADDITIVE_CHECKOUT_ENDED_REVIEW_REQUIRED' if self.normal and not self.error else 'PARTIAL')
        from reports import save
        save(self.work,self.result)

if __name__=='__main__':AdditiveSession().run()

import sys
import re
import json
import tempfile
from pathlib import Path
from unittest import TestCase
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/d3d9_proof'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
from startup_profile import analyze_text

class StartupProfileTests(TestCase):
    def trace(self):
        stages=['activated','scene_loaded','materials_enabled','receiver_started','renderer_assets_started','frame_begin','bootstrap_begin','bootstrap_drawn','bootstrap_presented','output_complete','receiver_ack']
        return '\n'.join(f'STARTUP_PROFILE stage={s} index=0 qpc={i*100} frequency=1000 private_bytes=100 working_set=50 system_commit=1000 commit_limit=2000' for i,s in enumerate(stages))
    def test_phase_times(self):
        report=analyze_text(self.trace())
        self.assertEqual(report['activation_to_bootstrap_output_seconds'],.9)
        self.assertEqual(report['bootstrap'][0]['present_seconds'],.1)
        self.assertEqual(report['first_receiver_ack_seconds'],.1)
    def test_diagnostic_cost_is_separate_and_complete(self):
        trace=self.trace()
        costs=[]
        for stage in re.findall(r'STARTUP_PROFILE stage=(\w+)',trace):
            costs.append(f'STARTUP_PROFILE_COST stage={stage} index=0 process_query_ticks=1 system_query_ticks=5000 frequency=1000')
        report=analyze_text(trace+'\n'+'\n'.join(costs))
        self.assertEqual(report['diagnostic_costs'][2]['system_query_seconds'],5)
        with self.assertRaises(ValueError):analyze_text(trace+'\n'+costs[0])
        with self.assertRaises(ValueError):analyze_text(trace+'\n'+'\n'.join(costs).replace('frequency=1000','frequency=0'))
    def test_narrow_receiver_intervals(self):
        names=('scene_packet_read_begin','scene_packet_read_complete','scene_packet_hash_complete','peer_start_begin','peer_guid_ready','peer_security_ready','peer_mapping_created','peer_events_created','peer_mapping_initialized','peer_process_begin','peer_process_created','peer_start_complete')
        trace=self.trace().replace('frequency=1000','frequency=10000')
        rows='\n'.join(f'STARTUP_PROFILE stage={s} index=0 qpc={201+i*7} frequency=10000 private_bytes=0 working_set=0 system_commit=0 commit_limit=0' for i,s in enumerate(names))
        trace=trace.replace('STARTUP_PROFILE stage=receiver_started',rows+'\nSTARTUP_PROFILE stage=receiver_started')
        report=analyze_text(trace)
        self.assertEqual(len(report['receiver_phases']),13)
        self.assertEqual(report['receiver_phases'][10]['begin'],'peer_process_begin')
        self.assertEqual(report['receiver_phases'][10]['seconds'],.0007)
        with self.assertRaises(ValueError):analyze_text(trace.replace('stage=peer_process_created','stage=wrong'))
    def test_early_receiver_timing_is_not_charged_after_activation(self):
        names=('peer_start_begin','peer_guid_ready','peer_security_ready','peer_mapping_created','peer_events_created','peer_mapping_initialized','peer_process_begin','peer_process_created','peer_passive_ready','peer_start_complete','receiver_started','idle_begin','activated','receiver_activated','scene_loaded','materials_enabled','renderer_assets_started','frame_begin','bootstrap_begin','bootstrap_drawn','bootstrap_presented','output_complete','receiver_ack')
        text='\n'.join(f'STARTUP_PROFILE stage={s} index=0 qpc={i*100} frequency=1000 private_bytes=0 working_set=0 system_commit=0 commit_limit=0' for i,s in enumerate(names))
        r=analyze_text(text)
        self.assertTrue(r['early_passive_receiver'])
        self.assertEqual(r['receiver_ready_before_activation_seconds'],.2)
        self.assertEqual(r['receiver_creation_seconds'],.1)
        self.assertTrue(all(p['seconds']>=0 for p in r['phases']))
    def test_missing_and_duplicate(self):
        with self.assertRaises(ValueError):analyze_text('')
        with self.assertRaises(ValueError):analyze_text(self.trace()+'\n'+self.trace())
    def test_clock_and_capacity(self):
        with self.assertRaises(ValueError):analyze_text(self.trace().replace('frequency=1000','frequency=0'))
        with self.assertRaises(ValueError):analyze_text('\n'.join([self.trace()]*13))
    def test_explicit_launcher_opt_in(self):
        root=Path(__file__).resolve().parents[1]
        text=(root/'tools/d3d9_proof/start_d3d9_multiship_session.ps1').read_text()
        self.assertIn('[switch]$StartupProfile',text)
        self.assertIn("if($StartupProfile){$forward+='-StartupProfile'}",text)
        self.assertIn("if($StartupProfile){'1'}else{$null}",text)
        self.assertIn('finally{$env:SFC_D3D9_STARTUP_PROFILE=$oldStartupProfile}',text)
    def test_optional_render_warm_interval(self):
        def row(stage,tick):return f'STARTUP_PROFILE stage={stage} index=0 qpc={tick} frequency=1000 private_bytes=1 working_set=1 system_commit=2 commit_limit=3'
        trace=re.sub(r'qpc=(\d+)',lambda m:'qpc='+str(int(m[1])+1000),self.trace())
        report=analyze_text(row('render_warm_begin',0)+'\n'+row('render_warm_complete',100)+'\n'+trace)
        self.assertEqual(report['experimental_render_warm_seconds'],.1)
    def test_first_complete_cohort_interval(self):
        names=('cohort_draw_begin','cohort_draw_end','cohort_output_complete','cohort_receiver_ack')
        extra='\n'.join(f'STARTUP_PROFILE stage={s} index=0 qpc={1100+i*100} frequency=1000 private_bytes=1 working_set=1 system_commit=2 commit_limit=3' for i,s in enumerate(names))
        report=analyze_text(self.trace()+'\n'+extra)
        self.assertEqual(report['first_cohort_draw_present_seconds'],.1)
        self.assertEqual(report['first_cohort_copy_seconds'],.1)
        self.assertEqual(report['first_cohort_ack_seconds'],.1)
    def test_experiment_isolated_before_receiver(self):
        root=Path(__file__).resolve().parents[1]
        text=(root/'tools/d3d9_proof/d3d9_direct_host.cpp').read_text()
        self.assertLess(text.index('render_prewarm::run('),text.index('if(argc==5&&!nativeSize)peer.start('))
        self.assertLess(text.index('if(nativeSize){peer.start('),text.index('nativeTarget.wait('))
        relay=(root/'tools/remix_runtime/multi_scene_relay.py').read_text()
        self.assertIn("if not self.offline_fixture:env.pop('SFC_D3D9_RENDER_PREWARM',None)",relay)
    def test_production_warmup_does_not_require_diagnostic_collection(self):
        root=Path(__file__).resolve().parents[1]
        text=(root/'tools/d3d9_proof/render_prewarm.h').read_text()
        self.assertNotIn('require(profile.enabled',text)
        self.assertIn('profile.mark("render_warm_begin")',text)
        self.assertIn('profile.mark("render_warm_complete")',text)
    def test_diagnostics_cannot_qualify_normal_startup(self):
        from qualify_multiship import inspect
        root=Path(__file__).resolve().parents[1]
        for flags in ({'render_prewarm':'triangle'},{'diagnostic_skip_initial_material_library':True},{'loading_policy':'async'},{'material_library':'flat'},{'native_log_level':'error'}):
            with tempfile.TemporaryDirectory(dir=root/'artifacts/remix-runtime/runs') as directory:
                result=dict(multi_ship_fixture=True,fixture_exit=0,host_exit=0,**flags)
                (Path(directory)/'result.json').write_text(json.dumps(result))
                with self.assertRaisesRegex(ValueError,'cannot qualify'):inspect(directory)

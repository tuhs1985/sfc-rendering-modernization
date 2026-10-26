import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
for directory in ('remix_runtime','d3d9_proof','scene_bridge','remix_ingest'):sys.path.insert(0,str(ROOT/'tools'/directory))
from parallel_assets import Tasks,material_piece,load_image,read_image
from progressive_scene_relay import Relay
from material_binding import encode_remix_material_dds,shader
from material_controls import encode
from roughness_maps import pixels
from scene_bundle import geometry_parts
from parallel_assets import Pipeline
from contextlib import contextmanager
from collections import deque


class ParallelAssetTests(unittest.TestCase):
    def mini_pipeline(self,root,secondary_block=None,base_block=None):
        for name in ('primary','secondary'):Image.new('RGB',(3,2),(80,120,160)).save(root/(name+'.bmp'))
        @contextmanager
        def reserve(*_):yield
        relay=SimpleNamespace(root=root,folder=root,material_config=(ROOT/'tools/remix_runtime/config/materials.toml').read_bytes(),output_reservations=SimpleNamespace(asset=reserve))
        mesh={'points':[(1,2,3),(4,5,6),(7,8,9)],'corners':[(i,(0,0,1),(.2,.3)) for i in range(3)],'polygons':[(0,0)],
              'groups':[{'group':0,'flags':0x21,'primary':1,'secondary':2}],
              'refs':{'resources':[{'id':1,'filename':'primary.bmp'},{'id':2,'filename':'secondary.bmp'}]}}
        class Mini(Pipeline):
            def decode(self,job):return root/'source.bin',b'',b'',mesh
            def _basic(self,job):
                if base_block:base_block.wait(timeout=2)
                return root/'output',{'groups':[(0,0,0,3)]},'ab'*32,b'packet',[]
            def _materials(self,job):return self.values,['1'],{},{}
        pipeline=Mini(relay);pipeline.submit(1,[1]*96)
        return pipeline

    def pump(self,tasks,predicate):
        until=time.monotonic()+3
        while time.monotonic()<until:
            tasks.pump()
            if predicate():return
            time.sleep(.001)
        self.fail('Task graph did not settle')

    def test_one_asset_geometry_and_texture_tasks_overlap(self):
        barrier=threading.Barrier(2);tasks=Tasks()
        def part():barrier.wait(timeout=1);return 5
        try:
            tasks.add(('geometry',1),part);tasks.add(('image',1),part)
            tasks.add(('join',1),lambda g,t:g+t,(('geometry',1),('image',1)))
            self.pump(tasks,lambda:tasks.tasks[('join',1)]['state']=='done')
            self.assertEqual(tasks.tasks[('join',1)]['value'],10)
            a,b=tasks.spans[:2];self.assertLess(max(a['begin_ns'],b['begin_ns']),min(a['end_ns'],b['end_ns']))
        finally:tasks.close()

    def test_base_ready_without_waiting_for_secondary_decode(self):
        release=threading.Event();entered=threading.Event()
        from parallel_assets import load_image as original_load
        def load(root,name,data):
            if name=='secondary.bmp':entered.set();release.wait(timeout=2)
            return original_load(root,name,data)
        with tempfile.TemporaryDirectory() as temp,patch('parallel_assets.load_image',side_effect=load):
            pipeline=self.mini_pipeline(Path(temp))
            try:
                self.pump(pipeline,lambda:pipeline.jobs[1].get('basic_ready',False))
                self.assertTrue(entered.is_set());self.assertFalse(pipeline.jobs[1]['material_done'])
                self.assertTrue(any(kind=='basic' for kind,_ in pipeline.events))
            finally:release.set();pipeline.close()

    def test_derivatives_finish_while_base_bundle_is_still_running(self):
        release=threading.Event()
        with tempfile.TemporaryDirectory() as temp:
            pipeline=self.mini_pipeline(Path(temp),base_block=release)
            try:
                self.pump(pipeline,lambda:any(k[0]=='derived' and t['state']=='done' for k,t in pipeline.graph.tasks.items()))
                self.assertFalse(pipeline.jobs[1]['basic_ready'])
                self.assertEqual(pipeline.graph.tasks[('basic',1)]['state'],'running')
            finally:release.set();pipeline.close()

    def test_missing_enhancement_is_partial_without_blocking_base(self):
        with tempfile.TemporaryDirectory() as temp:
            pipeline=self.mini_pipeline(Path(temp));(Path(temp)/'secondary.bmp').unlink()
            try:
                self.pump(pipeline,lambda:pipeline.jobs[1]['phase']=='failed')
                self.assertTrue(pipeline.jobs[1]['basic_ready'])
                self.assertIn('enhancement partial',pipeline.jobs[1]['error'])
                self.assertTrue(any(kind=='basic' for kind,_ in pipeline.events))
            finally:pipeline.close()

    def test_ready_base_publication_precedes_enhancement_io(self):
        relay=object.__new__(Relay);relay.service=None;relay.stopping=False;relay.error=None;relay.prewarm_process=None
        relay.process=SimpleNamespace(poll=lambda:None);relay.lights=None;calls=[]
        relay.current_rows=lambda:[];relay.discover=lambda rows:None;relay.collect_prepared=lambda:calls.append('collect')
        relay.publish_prepared=lambda:calls.append('base');relay.recover=lambda pid:None;relay.flush_enhancements=lambda:calls.append('enhance')
        relay.poll(1)
        self.assertEqual(calls,['collect','base','enhance'])

    def test_enhancement_drain_yields_after_four_ready_groups(self):
        relay=object.__new__(Relay);job={'id':1,'published':True,'phase':'materials'}
        relay.pending_enhancements=deque(('material',(job,{'group':i})) for i in range(10));relay.process=object();calls=[]
        relay.pending_stage_ids=set();relay.pending_complete_ids=set();relay.pending_library=False;relay.publication_busy_since=None;relay.publication_retries=0
        relay.preparer=SimpleNamespace(jobs={1:job});relay.accept_piece=lambda j,p:calls.append(p['group'])
        relay.write_stage=lambda job:None;relay.commit_layers=lambda **kw:None
        relay.flush_enhancements()
        self.assertEqual(calls,[0,1,2,3]);self.assertEqual(len(relay.pending_enhancements),6)

    def test_material_sharing_conflict_retries_without_releasing_pending_assets(self):
        relay=object.__new__(Relay);relay.process=object();job={'id':1,'published':True};released=[]
        relay.pending_stage_ids={1};relay.pending_complete_ids={1};relay.pending_library=False;relay.publication_busy_since=None;relay.publication_retries=0
        relay.preparer=SimpleNamespace(jobs={1:job},_release=lambda j:released.append(j['id']))
        with patch.object(Relay,'write_stage',side_effect=[PermissionError('sharing'),None]),patch.object(Relay,'commit_layers',side_effect=[PermissionError('sharing'),None]):
            relay.retry_publication();self.assertEqual(released,[]);self.assertEqual(relay.pending_stage_ids,{1})
            relay.retry_publication();self.assertEqual(released,[]);self.assertTrue(relay.pending_library)
            relay.retry_publication();self.assertEqual(released,[1]);self.assertFalse(relay.pending_library)
        self.assertEqual(relay.publication_retries,2)

    def test_ready_material_does_not_wait_for_delayed_material_or_other_ship(self):
        release=threading.Event();tasks=Tasks()
        def delayed():release.wait(timeout=2);return 'late'
        try:
            tasks.add(('material',1,0),lambda:'ready')
            tasks.add(('material',1,1),delayed);tasks.add(('decode',2),delayed)
            self.pump(tasks,lambda:tasks.tasks[('material',1,0)]['state']=='done')
            self.assertEqual(tasks.tasks[('material',1,1)]['state'],'running')
            self.assertEqual(tasks.tasks[('decode',2)]['state'],'running')
        finally:release.set();tasks.close()

    def test_shared_task_only_runs_once_and_failure_is_local(self):
        calls=[];tasks=Tasks()
        def fail():raise ValueError('bad texture')
        try:
            tasks.add(('shared',1),lambda:calls.append(1) or 2)
            tasks.add(('shared',1),lambda:self.fail('Repeated work'))
            tasks.add(('owner',1),lambda x:x,(('shared',1),))
            tasks.add(('owner',2),lambda x:x,(('shared',1),))
            tasks.add(('bad',1),fail);tasks.add(('dependent',1),lambda _:0,(('bad',1),))
            self.pump(tasks,lambda:all(tasks.tasks[k]['state'] in ('done','failed') for k in tasks.tasks))
            self.assertEqual(calls,[1]);self.assertEqual(tasks.tasks[('owner',2)]['value'],2)
            self.assertEqual(tasks.tasks[('dependent',1)]['state'],'failed')
        finally:tasks.close()

    def test_shutdown_drains_running_work_and_refuses_submission(self):
        started=threading.Event();release=threading.Event();closed=threading.Event();tasks=Tasks()
        def run():started.set();release.wait(timeout=2)
        tasks.add(('run',1),run);tasks.pump();self.assertTrue(started.wait(timeout=1))
        thread=threading.Thread(target=lambda:(tasks.close(),closed.set()));thread.start()
        try:
            self.assertFalse(closed.wait(timeout=.02));release.set();thread.join(timeout=2)
            self.assertTrue(closed.is_set())
            with self.assertRaises(ValueError):tasks.add(('new',2),lambda:None)
        finally:release.set();thread.join(timeout=2)

    def test_original_decoded_once_and_piece_bytes_match_accepted_convention(self):
        values=struct.unpack('<2I10fQ',encode((ROOT/'tools/remix_runtime/config/materials.toml').read_bytes()))[2:12]
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);Image.new('RGB',(3,2),(80,120,160)).save(root/'a.bmp')
            source=read_image(root,'a.bmp')
            with patch('parallel_assets.read_image',side_effect=AssertionError('Repeated original read')):image=load_image(root,'a.bmp',source)
            piece=material_piece(image,None,values)
            expected=encode_remix_material_dds(image['image']);digest=hashlib.sha256(expected).hexdigest()
            self.assertEqual(piece['images']['color'],'textures/'+digest+'.dds')
            self.assertEqual(piece['encoded'][piece['images']['color']][0],expected)
            rough=encode_remix_material_dds(pixels(image['image'],values[0],values[5],values[6],values[7],bool(values[8]),values[9]))
            self.assertEqual(piece['encoded'][piece['images']['roughness']][0],rough)

    def test_geometry_task_does_not_access_images_or_change_corner_data(self):
        mesh={'points':[(1,2,3),(4,5,6),(7,8,9)],'corners':[(i,(0,0,1),(.2,.3)) for i in range(3)],'polygons':[(9,0)]}
        vertices,raw,groups=geometry_parts(mesh)
        self.assertEqual(vertices[1],(4,5,6,0,0,1,.2,.3));self.assertEqual(len(raw),96);self.assertEqual(groups,{9:[0]})

    def test_malformed_images_and_unsafe_paths_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'bad.bmp').write_bytes(b'not an image')
            with self.assertRaises(Exception):load_image(root,'bad.bmp')
            with self.assertRaises(ValueError):read_image(root,'../outside.bmp')
            Image.new('RGB',(4097,1)).save(root/'large.bmp')
            with self.assertRaisesRegex(ValueError,'dimensions'):load_image(root,'large.bmp')

    def test_worker_count_bound_and_single_worker_dependencies(self):
        for value in (0,5):
            with self.assertRaises(ValueError):Tasks(value)
        tasks=Tasks(1)
        try:
            tasks.add(('input',1),lambda:2)
            tasks.add(('result',1),lambda x:x+1,(('input',1),))
            self.pump(tasks,lambda:tasks.tasks[('result',1)]['state']=='done')
            self.assertEqual(tasks.tasks[('result',1)]['value'],3)
        finally:tasks.close()

    def test_live_poll_has_single_coordinator_owner(self):
        relay=object.__new__(Relay);checks=[]
        relay.service=SimpleNamespace(check=lambda:checks.append('checked'))
        # Main-thread poll must not touch any other relay state once the service
        # owns preparation; absent fields make accidental reentry fail this test.
        relay.poll(123)
        self.assertEqual(checks,['checked'])

    def test_live_service_starts_once_even_when_renderer_launch_requests_it_again(self):
        from live_owner_timing import Relay as Single
        relay=object.__new__(Relay);relay.service=None
        def start(*_):relay.service=object()
        with patch.object(Single,'start_service',side_effect=start) as begin:
            relay.start_service(123);relay.start_service(123)
            self.assertEqual(begin.call_count,1)

    def test_experimental_switch_is_explicit_forwarded_and_recorded(self):
        source=(ROOT/'tools/remix_runtime/run_return_game.py').read_text()
        launcher=(ROOT/'tools/d3d9_proof/start_d3d9_multiship_session.ps1').read_text()
        self.assertIn("[switch]$ExperimentalParallelAssets",launcher)
        self.assertIn("$forward+='-ExperimentalParallelAssets'",launcher)
        self.assertIn("$runArguments+='--experimental-parallel-assets'",launcher)
        self.assertIn("mode_args['experimental_live_checkout']=True",source)
        self.assertIn("metadata['experimental_parallel_assets']=args.experimental_parallel_assets",source)
        self.assertIn("result['experimental_parallel_assets']=args.experimental_parallel_assets",source)

    def test_renderer_admission_service_is_explicit_and_reported(self):
        progressive=(ROOT/'tools/remix_runtime/progressive_scene_relay.py').read_text()
        launch=(ROOT/'tools/remix_runtime/multi_scene_relay.py').read_text()
        self.assertIn('self.admission_service=True',progressive)
        self.assertIn("env['SFC_D3D9_ADMISSION_SERVICE']='1' if getattr(self,'admission_service',False) else '0'",launch)
        self.assertIn("['native_admission_service']",progressive)
        self.assertIn("['output_stage_timings']",progressive)

    def test_initial_texture_data_is_opted_in_and_actual_activation_reported(self):
        progressive=(ROOT/'tools/remix_runtime/progressive_scene_relay.py').read_text()
        self.assertIn('self.initial_texture_data=True',progressive)
        self.assertIn("['native_initial_texture_data']",progressive)
        for name in ('live_owner_timing.py','multi_scene_relay.py'):
            launch=(ROOT/'tools/remix_runtime'/name).read_text()
            self.assertIn("env['SFC_D3D9_INITIAL_TEXTURE_DATA']='1' if getattr(self,'initial_texture_data',False) else '0'",launch)

    def test_texture_upload_override_rejects_unrelated_fixture_before_startup(self):
        import subprocess
        result=subprocess.run([sys.executable,'-B',str(ROOT/'tools/remix_runtime/run_return_fixture.py'),
                               '--texture-upload','initial-data'],capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,2)
        self.assertIn('Texture upload comparison requires performance multi-ship',result.stderr)

    def test_material_failure_keeps_previous_stage_and_rejects_wrong_association(self):
        with tempfile.TemporaryDirectory() as temp:
            relay=object.__new__(Relay);relay.folder=Path(temp);relay.layers=[];relay.material_pieces={};relay.material_keys={};relay.image_bytes=0;relay.progressive_events=[];relay.material_config=b'settings'
            job=dict(id=1,gpu=relay.folder/'gpu/assets/1',manifest={'groups':[(0,0,0,3),(1,1,3,3)]})
            piece=dict(group=0,ordinary_texture=0,remix_hash='1'*16,values=[.4,5,.2,.5,0,.9,0,1,0,.4],images={'color':'textures/a.dds'},encoded={'textures/a.dds':(b'a',dict(sha256='a',bytes=1,dimensions=[1,1]))},primary_sha256='original',secondary_sha256=None)
            relay.accept_piece(job,piece);relay.write_stage(job)
            stage=job['gpu']/'rtx-remix/mods/sfc-policy/mod.usda';before=stage.read_bytes()
            wrong=dict(piece,group=1,primary_sha256='wrong image',encoded={})
            with self.assertRaisesRegex(ValueError,'Conflicting material'):relay.accept_piece(job,wrong)
            self.assertEqual(stage.read_bytes(),before)

    def test_progressive_stage_preserves_existing_group_and_applies_new_group(self):
        values=[.4,5,.2,.5,0,.9,0,1,0,.4]
        with tempfile.TemporaryDirectory() as temp:
            relay=object.__new__(Relay);relay.folder=Path(temp);relay.layers=[];relay.material_pieces={};relay.material_keys={};relay.image_bytes=0;relay.progressive_events=[];relay.material_config=b'settings'
            job=dict(id=2,gpu=relay.folder/'gpu/assets/1',manifest={'groups':[(0,0,0,3),(1,1,3,3)]})
            def piece(group):
                raw=bytes([group])*4;name='textures/'+hashlib.sha256(raw).hexdigest()+'.dds'
                return dict(group=group,ordinary_texture=group,remix_hash=str(group+1)*16,values=values,images={'color':name},
                    encoded={name:(raw,dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=4,dimensions=[1,1]))},primary_sha256=str(group),secondary_sha256=None)
            relay.accept_piece(job,piece(0));relay.write_stage(job)
            stage=job['gpu']/'rtx-remix/mods/sfc-policy/mod.usda';first=stage.read_text()
            report=json.loads((job['gpu']/'material-binding.json').read_text());self.assertFalse(report['complete'])
            relay.accept_piece(job,piece(1));relay.write_stage(job);second=stage.read_text()
            self.assertIn('mat_'+16*'1',first);self.assertNotIn('mat_'+16*'2',first)
            self.assertIn('mat_'+16*'1',second);self.assertIn('mat_'+16*'2',second)
            self.assertTrue(json.loads((job['gpu']/'material-binding.json').read_text())['complete'])


if __name__=='__main__':unittest.main()

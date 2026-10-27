import copy
import json
from collections import deque
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
for name in ('remix_runtime','d3d9_proof','scene_bridge','remix_ingest'):
    sys.path.insert(0,str(ROOT/'tools'/name))
from async_material_checkout import Relay,configure_child,receipt
from parallel_assets import Pipeline,Tasks
from qualify_async_material import policy,delivery,match_assets


class AsyncMaterialTests(unittest.TestCase):
    def test_base_catalog_publishes_before_priming_readiness(self):
        r=object.__new__(Relay);r.material_prime_ready=None;r.catalog=[];r.initial_ids={1}
        row=[0]*96;row[1]=2;row[7]=3
        job=dict(id=1,path_id=1,wire=b'base packet',row=row,signature='content',
                 manifest={'model_name':'fresh.mod'})
        r.preparer=SimpleNamespace(jobs={1:job});r.receiver=SimpleNamespace(channel=object())
        with patch('progressive_scene_relay.wire.publish') as publish:
            r.publish_prepared(initial=True)
        publish.assert_called_once_with(r.receiver.channel,1,b'base packet')
        self.assertTrue(job['published']);self.assertIsNone(r.material_prime_ready)

    def test_priming_gates_only_enhancement_publication(self):
        from progressive_scene_relay import Relay as Parent
        with tempfile.TemporaryDirectory() as directory:
            r=object.__new__(Relay);r.folder=Path(directory);r.material_prime_ready=None
            r.pending_stage_ids={1};r.pending_library=False
            with patch.object(Parent,'retry_publication') as publish:
                r.retry_publication();publish.assert_not_called()
                ready=r.folder/'gpu/renderer-ready.bin';ready.parent.mkdir()
                ready.write_bytes(b'partial');r.retry_publication();publish.assert_not_called()
                ready.write_bytes(struct.pack('<2Q',1234,789));r.retry_publication()
                publish.assert_called_once();self.assertEqual(r.material_prime_ready['host_pid'],789)
                # An idle cycle with no new enhancement does not reread the file.
                r.pending_stage_ids.clear();ready.unlink();r.retry_publication()
                self.assertEqual(publish.call_count,2)

    def test_priming_rejects_invalid_readiness_instead_of_publishing(self):
        with tempfile.TemporaryDirectory() as directory:
            r=object.__new__(Relay);r.folder=Path(directory);r.material_prime_ready=None
            r.pending_stage_ids={1};r.pending_library=False
            ready=r.folder/'gpu/renderer-ready.bin';ready.parent.mkdir()
            for raw in (bytes(17),struct.pack('<2Q',0,1),struct.pack('<2Q',1,1<<40)):
                ready.write_bytes(raw)
                with self.assertRaises(ValueError):r.retry_publication()

    def test_gameplay_qualification_and_backend_are_json_serializable(self):
        import qualify_async_material as gate
        backend=dict(release='1.6.1',exe=ROOT/'candidate.exe',runtime=ROOT/'candidate.dll',
                     host_sha256='host',runtime_sha256='runtime',header_sha256='header')
        saved=dict(result='ASYNC_MATERIAL_CHECKOUT_PREPARED_NOT_SFC_PASS',locks={'source':'hash'},
                   backend=receipt(backend),evidence=[])
        with tempfile.TemporaryDirectory() as directory:
            qpath=Path(directory)/'qualification.json';qpath.write_text(json.dumps(saved))
            with patch.object(gate,'RECEIPT',qpath),patch.object(gate,'backend_inputs',return_value=backend),\
                 patch.object(gate,'locks',return_value=saved['locks']),\
                 patch('qualify_multiship.require_qualification',return_value={}):
                q=gate.require_qualification()
                # Same full-support audit record that failed before SFC startup.
                metadata=dict(full_support_qualification=q,async_material_checkout=receipt(q['backend_inputs']))
                restored=json.loads(json.dumps(metadata))
                self.assertEqual(restored['full_support_qualification']['backend_inputs']['exe'],str(backend['exe']))
                self.assertIsInstance(backend['exe'],Path)  # Verifier input untouched.

    def test_concurrent_asset_completion_matches_content_not_folder_order(self):
        reference=[('1','a.mod','a'),('2','b.mod','b'),('3','c.mod','c')]
        self.assertEqual(match_assets(reference,[('1','a.mod','a'),('3','b.mod','b'),('2','c.mod','c')]),{'1':'1','2':'3','3':'2'})
        with self.assertRaisesRegex(ValueError,'missing'):match_assets(reference,[('1','a.mod','wrong')])
        with self.assertRaisesRegex(ValueError,'Ambiguous'):match_assets(reference,[('1','a.mod','a'),('2','a.mod','a')])

    def setup_alias(self):
        p=object.__new__(Pipeline);p.graph=Tasks(1);key=('derived','fixture')
        p.graph.tasks[key]=dict(state='done',value={'image':True},deps=(),fn=None,priority=3)
        p.graph.add(('material',4,0),lambda value:value,(key,))
        p.image_users={key:{4}}
        return p,dict(id=4,phase='alias',piece_keys={0:key}),key

    def test_queued_alias_consumers_cancel_before_shared_dependency_release(self):
        p,job,key=self.setup_alias()
        try:
            p._release(job);self.assertNotIn(key,p.graph.tasks)
            p.graph.pump()  # Original bug dereferenced the missing key here.
            self.assertFalse(any(t['state']=='queued' for t in p.graph.tasks.values()))
        finally:p.graph.close()

    def test_running_alias_consumer_retains_submitted_arguments(self):
        p,job,key=self.setup_alias();entered=threading.Event();release=threading.Event()
        def consume(value):entered.set();release.wait(2);return value
        p.graph.tasks[('material',4,0)]['fn']=consume
        try:
            p.graph.pump();self.assertTrue(entered.wait(1));p._release(job)
            self.assertNotIn(key,p.graph.tasks);release.set()
            limit=time.monotonic()+2
            while p.graph.tasks[('material',4,0)]['state']=='running' and time.monotonic()<limit:
                p.graph.pump();time.sleep(.001)
            self.assertEqual(p.graph.tasks[('material',4,0)]['value'],{'image':True})
        finally:release.set();p.graph.close()

    def test_other_owner_keeps_shared_dependency(self):
        p,job,key=self.setup_alias();p.image_users[key].add(9)
        p.graph.add(('material',9,0),lambda value:value,(key,))
        try:
            p._release(job);self.assertIn(key,p.graph.tasks);p.graph.pump()
            self.assertIn(p.graph.tasks[('material',9,0)]['state'],('running','done'))
        finally:p.graph.close()

    def test_complete_stage_publication_independent_of_other_owner(self):
        r=object.__new__(Relay);r.pending_enhancements=deque();r.material_pieces={}
        r.pending_stage_ids=set();r.pending_complete_ids=set();calls=[]
        r.accept_piece=lambda job,piece:r.material_pieces.setdefault(job['id'],{}).update({piece:True})
        r.retry_publication=lambda:calls.append(set(r.pending_stage_ids))
        r.fail_job=lambda *_:self.fail('Unexpected material error')
        a=dict(id=1,published=True,phase='ready',manifest={'groups':[(0,),(1,)]})
        b=dict(id=2,published=True,phase='materials',manifest={'groups':[(0,),(1,)]})
        r.pending_enhancements.extend([('piece',(a,0)),('piece',(b,0)),('piece',(a,1)),('complete',a)])
        r.flush_enhancements();self.assertEqual(calls,[{1}]);self.assertEqual(set(r.material_pieces[2]),{0})
        r.pending_enhancements.append(('complete',b))
        with self.assertRaisesRegex(ValueError,'missing groups'):r.flush_enhancements()

    def test_child_overrides_old_sync_environment_without_global_mutation(self):
        backend=dict(release='1.6.1',host_sha256='h',runtime_sha256='r',header_sha256='s')
        inherited={'DXVK_ASYNC_ASSET_LOADING':'0','OTHER':'keep'};child=dict(inherited)
        text,report=configure_child(backend,child)
        self.assertIn('asyncAssetLoading = True',text);self.assertEqual(child['DXVK_ASYNC_ASSET_LOADING'],'1')
        self.assertIn('enableReplacementAssets = True',text)
        self.assertEqual(child['SFC_D3D9_RENDER_PREWARM'],'triangle')
        self.assertEqual(child['SFC_D3D9_STARTUP_PROFILE'],'1')
        self.assertTrue(report['initial_material_priming'])
        self.assertNotIn('SFC_D3D9_RENDER_PREWARM',inherited)
        self.assertEqual(inherited['DXVK_ASYNC_ASSET_LOADING'],'0');self.assertEqual(child['OTHER'],'keep')
        self.assertEqual(report['inherited_async_asset_loading'],'0')
        with self.assertRaises(ValueError):configure_child(None,child)

    def test_gate_rejects_diagnostic_and_unrelated_policy(self):
        r=dict(async_material_checkout=True,runtime_candidate={'release':'1.6.1'},material_library='flat',prewarm=True,
               pipeline_mode='performance',multi_ship_resources_fixture=True,loading_policy='inherit',
               material_texture_loading='preload',render_prewarm='off',native_log_level='inherit')
        policy(r)
        for key,value in [('production_qualification_eligible',False),('material_library','layers'),('host_exit',1),
                          ('candidate_hot_reload_probe',{'mode':'async'}),('api_texture_prefetch',True)]:
            bad=copy.deepcopy(r);bad[key]=value
            with self.assertRaises(ValueError):policy(bad)

    def test_delivery_gate_counts_earlier_gap_not_just_settled_window(self):
        row=struct.Struct('<8I5Q')
        def packet(status):return row.pack(0,0,0,status,*([0]*9))
        good=b'\0'*64+b''.join(packet(s) for s in [2,2,1,2,1,1,2,1])
        self.assertEqual(delivery(good)['post_start_omissions'],2)
        bad=b'\0'*64+b''.join(packet(s) for s in [1,2,2,2]+[1]*600)
        with self.assertRaisesRegex(ValueError,'interruption'):delivery(bad)

    def test_launcher_rejects_wrong_modes_before_setup(self):
        for tool,args in [('run_return_game.py',['--async-material-checkout']),
                          ('run_return_fixture.py',['--async-material-checkout','--multi-ship','--prewarm'])]:
            p=subprocess.run([sys.executable,'-B',str(ROOT/'tools/remix_runtime'/tool),*args],capture_output=True,text=True,timeout=10)
            self.assertEqual(p.returncode,2);self.assertIn('requires',p.stderr)


if __name__=='__main__':unittest.main()

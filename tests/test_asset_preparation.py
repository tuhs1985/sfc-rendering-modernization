import json
from pathlib import Path
import sys
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
for directory in ('remix_runtime','d3d9_proof','scene_bridge','remix_ingest'):
    sys.path.insert(0,str(ROOT/'tools'/directory))
from asset_preparation import PreparationQueue
from multi_scene_relay import Relay
from multi_scene_resources import Reservations
import multi_scene as wire


class AssetPreparationTests(unittest.TestCase):
    def run_queue(self,queue,condition=None):
        until=time.monotonic()+5
        while time.monotonic()<until:
            queue.pump()
            if condition() if condition else queue.settled(queue.jobs):return
            time.sleep(.001)
        self.fail('Bounded preparation did not finish')

    def test_four_actual_workers_overlap(self):
        barrier=threading.Barrier(4)
        def prepare(row,mesh,identity):barrier.wait(timeout=3);return identity
        queue=PreparationQueue(lambda row:(str(row[0]),{}),prepare)
        try:
            for identity in range(1,5):queue.submit(identity,[identity])
            self.run_queue(queue)
            self.assertTrue(all(j['phase']=='ready' for j in queue.jobs.values()))
            self.assertEqual(queue.report()['peak_parallel_preparations'],4)
            self.assertEqual(len({s['thread'] for s in queue.spans if s['phase']=='prepare'}),4)
        finally:queue.close()

    def test_identical_content_prepared_once_without_worker_waits(self):
        prepared=[]
        def prepare(row,mesh,identity):prepared.append(identity);return identity
        queue=PreparationQueue(lambda row:('shared' if row[0]<4 else 'other',{}),prepare)
        try:
            for identity in range(1,5):queue.submit(identity,[identity])
            self.run_queue(queue)
            self.assertEqual(sorted(prepared),[1,4])
            self.assertEqual([queue.jobs[i]['canonical'] for i in (2,3)],[1,1])
        finally:queue.close()

    def test_out_of_order_identity_does_not_change_canonical(self):
        release=threading.Event();second=threading.Event()
        def identify(row):
            if row[0]==1:release.wait(timeout=2)
            else:second.set()
            return 'shared',{}
        queue=PreparationQueue(identify,lambda *args:'prepared')
        try:
            queue.submit(1,[1]);queue.submit(2,[2]);queue.pump();self.assertTrue(second.wait(timeout=1))
            queue.pump();self.assertEqual(queue.contents,{})
            release.set();self.run_queue(queue);self.assertEqual(queue.jobs[2]['canonical'],1)
        finally:release.set();queue.close()

    def test_failure_and_alias_are_bounded_not_deadlocked(self):
        def prepare(*args):raise ValueError('unsupported asset')
        queue=PreparationQueue(lambda row:('shared',{}),prepare)
        try:
            queue.submit(1,[1]);queue.submit(2,[2]);self.run_queue(queue)
            self.assertEqual(queue.jobs[1]['phase'],'failed')
            self.assertEqual(queue.jobs[1]['error'],'unsupported asset')
            self.assertEqual(queue.jobs[2]['phase'],'alias')
        finally:queue.close()

    def test_shutdown_waits_for_worker_then_refuses_more_work(self):
        entered=threading.Event();release=threading.Event();closed=threading.Event()
        def identify(row):entered.set();release.wait(timeout=2);return 'one',{}
        queue=PreparationQueue(identify,lambda *args:None)
        queue.submit(1,[1]);queue.pump();self.assertTrue(entered.wait(timeout=1))
        closer=threading.Thread(target=lambda:(queue.close(),closed.set()));closer.start()
        try:
            self.assertFalse(closed.wait(timeout=.02));release.set();closer.join(timeout=2)
            self.assertTrue(closed.is_set())
            with self.assertRaises(ValueError):queue.submit(2,[2])
        finally:release.set();queue.close();closer.join(timeout=2)

    def test_queue_and_worker_capacity(self):
        with self.assertRaises(ValueError):PreparationQueue(None,None,workers=5)
        queue=PreparationQueue(None,None)
        try:
            for i in range(1,65):queue.submit(i,[i])
            with self.assertRaises(ValueError):queue.submit(65,[65])
        finally:queue.close()

    def test_parallel_disk_reservations_release_even_on_error(self):
        reservations=Reservations(inventory=0);barrier=threading.Barrier(4);calls=[]
        def work():
            try:
                with reservations.asset():barrier.wait(timeout=2);raise ValueError('test')
            except ValueError:pass
        with patch('multi_scene_resources.require_capacity',side_effect=lambda amount,**kwargs:calls.append(amount)):
            threads=[threading.Thread(target=work) for _ in range(4)]
            for t in threads:t.start()
            for t in threads:t.join(timeout=3)
        self.assertEqual(calls[:4],[256*1024*1024*i for i in range(1,5)])
        self.assertEqual(len(calls),8)
        self.assertEqual(reservations.bytes,0)

    def test_initial_materials_committed_once_and_alias_has_no_layer(self):
        with tempfile.TemporaryDirectory() as folder:
            relay=object.__new__(Relay);relay.folder=Path(folder);relay.layers=[];relay.material_events=[]
            relay.published_paths=set();relay.catalog=[];relay.receiver=SimpleNamespace(channel=None)
            relay.isolate_late_material_reload=False;relay.isolate_initial_material_library=False;relay.offline_fixture=False
            jobs={}
            for identity,path in ((1,1),(2,2),(3,1)):
                row=[0]*96;row[1]=identity;row[5]=70;row[6]=71;row[7]=identity
                gpu=relay.folder/'gpu/assets'/str(path)
                raw=wire.asset_packet(identity,path,row,('ab' if path==1 else 'cd')*32,b'g',[b't'])
                jobs[identity]=dict(id=identity,row=row,wire=raw,new=identity!=3,gpu=gpu,
                    manifest={'model_name':'shared' if path==1 else 'other'},signature=str(path))
            relay.preparer=SimpleNamespace(jobs=jobs)
            with patch('multi_scene.publish') as publish:relay.publish_prepared(initial=True)
            self.assertEqual(publish.call_count,3)
            self.assertEqual(len(relay.material_events),1)
            self.assertEqual(relay.material_events[0]['layers'],2)
            self.assertTrue(relay.material_events[0]['initial'])
            self.assertEqual(len(relay.catalog),3)
            self.assertTrue(all(a['initial'] for a in relay.catalog))
            text=(relay.folder/'gpu/rtx-remix/mods/sfc-policy/mod.usda').read_text()
            self.assertEqual(text.count('@'),4)
            with patch('multi_scene.publish') as publish:relay.publish_prepared(initial=True)
            publish.assert_not_called();self.assertEqual(len(relay.material_events),1)


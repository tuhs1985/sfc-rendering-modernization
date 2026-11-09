import sys
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
for name in ('remix_runtime','d3d9_proof','scene_bridge','remix_ingest','m1_component'):
    sys.path.insert(0,str(ROOT/'tools'/name))
from progressive_scene_relay import Relay
import progressive_scene_relay as module


class AliasPublicationTests(unittest.TestCase):
    def test_alias_lower_index_waits_for_canonical_residency_without_blocking(self):
        relay=Relay.__new__(Relay)
        def job(identity,**extra):
            return dict(id=identity,wire=b'packet',path_id=1,row=list(range(96)),phase='ready',
                        signature='same',manifest={'model_name':'synthetic'},**extra)
        canonical=job(3);alias=job(1);alias.update(phase='alias',canonical=3)
        relay.preparer=SimpleNamespace(jobs={1:alias,3:canonical})
        relay.receiver=SimpleNamespace(channel=object());relay.catalog=[];relay.initial_ids={3}
        with patch.object(module.wire,'publish') as publish,patch.object(module.wire,'acknowledgement',return_value=0):
            relay.publish_prepared()
            self.assertEqual([x.args[1] for x in publish.call_args_list],[3])
            self.assertFalse(alias.get('published',False))
        with patch.object(module.wire,'publish') as publish,patch.object(module.wire,'acknowledgement',return_value=1):
            relay.publish_prepared()
            self.assertEqual([x.args[1] for x in publish.call_args_list],[1])
        self.assertEqual([x['id'] for x in relay.catalog],[3,1])


if __name__=='__main__':unittest.main()

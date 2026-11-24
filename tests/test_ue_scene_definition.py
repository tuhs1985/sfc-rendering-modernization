"""Fresh UE base definitions preserve source data and publish only once."""
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src/rendering/ue'))
from scene_definition import DefinitionPublisher


class DefinitionTests(unittest.TestCase):
    def fixture(self):
        asset=NS(content='a'*64,model='assets/models/fixture.mod',positions=((1,2,3),(4,5,6),(7,8,9)),
                 corners=((0,(0,0,1),(.1,.2)),(1,(0,0,1),(.3,.4)),(2,(0,0,1),(.5,.6))),
                 polygons=((0,0),),groups=((0,9,'diffuse','c'*64,'illumination','d'*64,'captured secondary association'),))
        image=NS(decoded_sha256='b'*64,original_sha256='c'*64,width=2,height=2,bgra=bytes(range(16)))
        reader=NS(session='session-A',source_pid=42,assets={'a'*64:asset},images={'diffuse':image},
                  revisions={7:('a'*64,3,53,59)},origins={7:dict(packet_sha256='e'*64,fragment=None)})
        identity=[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
        instance=dict(session=reader.session,owner_epoch=3,revision=7,asset='a'*64,model=identity)
        snapshot=dict(session=reader.session,source_pid=42,frame=11,sequence=13,
                      camera=(identity,identity,(200,30,1720,1020,860,510)),instances=[instance])
        return reader,snapshot,instance

    def test_original_data_and_one_time_atomic_definition(self):
        reader,frame,instance=self.fixture()
        with tempfile.TemporaryDirectory() as folder:
            publisher=DefinitionPublisher(Path(folder))
            path=publisher.publish(reader,frame,instance);data=json.loads(path.read_text())
            self.assertEqual(data['positions'],[list(p) for p in reader.assets['a'*64].positions])
            self.assertEqual(data['corners'][0][2],[.1,.2])
            self.assertEqual(data['groups'][0]['secondary_filename'],'illumination')
            self.assertEqual(data['frames'][0]['source_sequence'],13)
            self.assertEqual(data['source_binding'],dict(pid=42,model=53,source=59))
            self.assertEqual((path.parent/data['images']['diffuse']['file']).read_bytes(),bytes(range(16)))
            with patch.object(Path,'write_bytes',side_effect=AssertionError('Duplicate image write')),patch.object(Path,'write_text',side_effect=AssertionError('Duplicate definition write')):
                self.assertEqual(publisher.publish(reader,frame,instance),path)

    def test_wrong_session_owner_revision_and_asset_are_rejected(self):
        for key,value in (('session','session-B'),('owner_epoch',4),('revision',8),('asset','f'*64)):
            with self.subTest(key=key),tempfile.TemporaryDirectory() as folder:
                reader,frame,instance=self.fixture();instance[key]=value
                with self.assertRaises(ValueError):DefinitionPublisher(Path(folder)).publish(reader,frame,instance)
                self.assertEqual(list(Path(folder).iterdir()),[])

    def test_publisher_cannot_overwrite_a_definition_across_sessions(self):
        reader,frame,instance=self.fixture()
        with tempfile.TemporaryDirectory() as folder:
            publisher=DefinitionPublisher(Path(folder));path=publisher.publish(reader,frame,instance);original=path.read_bytes()
            reader.session=frame['session']=instance['session']='session-B'
            with self.assertRaises(ValueError):publisher.publish(reader,frame,instance)
            self.assertEqual(path.read_bytes(),original)

    def test_recycled_revision_cannot_replace_an_immutable_definition(self):
        reader,frame,instance=self.fixture()
        with tempfile.TemporaryDirectory() as folder:
            publisher=DefinitionPublisher(Path(folder));path=publisher.publish(reader,frame,instance);original=path.read_bytes()
            reader.revisions[7]=('f'*64,3,53,59);instance['asset']='f'*64
            with self.assertRaises(ValueError):publisher.publish(reader,frame,instance)
            self.assertEqual(path.read_bytes(),original)

    def test_shared_asset_publishes_only_owner_metadata_after_first_definition(self):
        reader,frame,instance=self.fixture()
        with tempfile.TemporaryDirectory() as folder:
            publisher=DefinitionPublisher(Path(folder));first=publisher.publish(reader,frame,instance)
            other=dict(instance,owner_epoch=4,revision=8);frame['instances'].append(other)
            reader.revisions[8]=('a'*64,4,61,67);reader.origins[8]=dict(packet_sha256='f'*64,fragment=None)
            second=publisher.publish(reader,frame,other);data=json.loads(second.read_text())
            self.assertEqual(data['asset_reference'],first.name)
            self.assertNotIn('positions',data);self.assertNotIn('images',data)
            self.assertEqual(data['owner_epoch'],4);self.assertEqual(data['source_binding']['source'],67)
            self.assertLess(second.stat().st_size,4096)


if __name__=='__main__':unittest.main()

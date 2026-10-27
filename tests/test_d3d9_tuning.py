import hashlib,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools/remix_runtime'),str(ROOT/'tools/d3d9_proof'),str(ROOT/'tools/remix_ingest'),str(ROOT/'tools/scene_bridge')]
from d3d9_tuning import build_materials
from material_library import flat

class TuningTests(unittest.TestCase):
    def test_originals_unchanged_and_supported_emission_update(self):
        with tempfile.TemporaryDirectory() as folder:
            d=Path(folder);game=d/'game';game.mkdir();out=d/'gpu/rtx-remix/mods/sfc-policy/tuning'
            for name,color in [('a.bmp',(50,100,150)),('b.bmp',(128,128,128))]:Image.new('RGB',(8,8),color).save(game/name)
            original={p:p.read_bytes() for p in game.iterdir()}
            refs=d/'packet.json';refs.write_text(json.dumps(dict(resources=[dict(id=1,filename='a.bmp'),dict(id=2,filename='b.bmp')],groups=[dict(group=7,flags=32,primary=1,secondary=2)])))
            piece=dict(group=7,remix_hash='0000000000000001',primary_sha256=hashlib.sha256(original[game/'a.bmp']).hexdigest(),secondary_sha256=hashlib.sha256(original[game/'b.bmp']).hexdigest())
            jobs=[dict(packet=str(refs.with_suffix('.bin')),pieces=[piece])]
            with patch('run_offline.storage',return_value=0):
                blocks,size=build_materials(game,jobs,b'[material]\nemissive_intensity=0.25\n',out)
                again,extra=build_materials(game,jobs,b'[material]\nemissive_intensity=0.5\n',out)
            self.assertGreater(size,0);self.assertEqual(extra,0)
            self.assertIn('float inputs:emissive_intensity = 0.25',blocks[piece['remix_hash']])
            self.assertIn('@tuning/textures/',again[piece['remix_hash']])
            self.assertEqual(original,{p:p.read_bytes() for p in game.iterdir()})
            piece['primary_sha256']='wrong'
            with patch('run_offline.storage',return_value=0),self.assertRaisesRegex(ValueError,'source images changed'):
                build_materials(game,jobs,b'[material]\n',out)

    def test_launcher_uses_current_path_and_all_runtime_limits(self):
        launcher=(ROOT/'tools/remix_runtime/start_light_tuning_session.ps1').read_text()
        self.assertIn('start_d3d9_multiship_session.ps1',launcher)
        self.assertIn('-Tuning',launcher)
        for name in ['tools/d3d9_proof/live_owner_input.h','tools/d3d9_proof/output_channel.h','tools/remix_ingest/bounded_job.cpp','tools/remix_runtime/multi_scene_relay.py']:
            self.assertIn('1980',(ROOT/name).read_text())
        runner=(ROOT/'tools/remix_runtime/run_return_game.py').read_text()
        self.assertIn('args.d3d9_additive and not d3d9_tuning',runner)
        self.assertIn('timing_relay.live_tuning=d3d9_tuning',runner)

    def test_scalar_updates_share_existing_images_without_reading_game_assets(self):
        from material_controls import encode
        import struct
        with tempfile.TemporaryDirectory() as folder:
            d=Path(folder);refs=d/'packet.json';refs.write_text('{"resources":[],"groups":[]}')
            raw=b'[material]\nroughness=0.4\nroughness_map_enabled=true\nroughness_map_strength=0.9\nroughness_map_gamma=0.4\nemissive_intensity=0.25\n'
            values=list(struct.unpack('<2I10fQ',encode(raw))[2:12]);values[1]=1.2
            piece=dict(group=1,remix_hash='0000000000000001',primary_sha256='captured',secondary_sha256='captured2',values=values,images={'color':'textures/a.dds','emission':'textures/b.dds'})
            jobs=[dict(packet=str(refs.with_suffix('.bin')),base=str(d/f'gpu/assets/{i}/rtx-remix/mods/sfc-policy'),pieces=[piece]) for i in (1,2)]
            with patch('run_offline.storage',return_value=0),patch('parallel_assets.load_image',side_effect=AssertionError('Unexpected asset reread')):
                blocks,written=build_materials(d,jobs,raw,d/'gpu/rtx-remix/mods/sfc-policy/tuning')
            self.assertEqual(written,0);self.assertEqual(len(blocks),1)
            self.assertIn('float inputs:emissive_intensity = 0.25',next(iter(blocks.values())))

    def test_live_lights_keep_last_good_on_missing_required_source(self):
        from live_light_binding import Binding
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as folder:
            d=Path(folder);p=d/'lights.toml'
            raw=b'schema_version=1\nbackend="remix_sdk_0_6_4"\n[[lights]]\nid="native_directional_0"\n'
            p.write_bytes(raw)
            b=Binding.__new__(Binding)
            b.tuning=True;b.config_polled=0;b.config=p;b.config_hash='previous';b.config_revision=3;b.messages=0
            b.controls={'last':'good'};b.row=[0]*96;b.ready=False;b.gpu=d
            b.receiver=SimpleNamespace(channel=SimpleNamespace(sample_owner=lambda _:None))
            b.poll()
            self.assertEqual(b.config_hash,'previous');self.assertEqual(b.config_revision,3);self.assertEqual(b.controls,{'last':'good'})

if __name__=='__main__':unittest.main()

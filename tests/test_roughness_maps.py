import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
from PIL import Image
from material_controls import encode,fnv,Relay
from roughness_maps import pixels,prepare

def acknowledge(folder,packet,active=None,status=1):
    revision=struct.unpack_from('<Q',packet,48)[0]
    body=struct.pack('<IIQQII',0x314b414d,1,revision,revision if active is None else active,status,0)
    (folder/'material-receipt.bin').write_bytes(body+struct.pack('<Q',fnv(body)))

class RoughnessTests(unittest.TestCase):
    def test_levels_strength_inversion(self):
        image=Image.new('RGB',(3,1));image.putdata([(0,0,0),(128,128,128),(255,255,255)])
        self.assertEqual(list(pixels(image,.2,1,0,1,False,1).convert('L').getdata()),[0,128,255])
        self.assertEqual(list(pixels(image,.2,1,0,1,True,1).convert('L').getdata()),[255,127,0])
        self.assertEqual(list(pixels(image,.2,0,0,1,False,1).convert('L').getdata()),[51]*3)
        self.assertEqual(list(pixels(image,0,1,.25,.75,False,1).convert('L').getdata())[::2],[0,255])
        self.assertGreater(pixels(image,0,1,0,1,False,2).getpixel((1,0))[0],128)
    def test_config_validation(self):
        for text in ('roughness_map_enabled=1','roughness_map_strength=2','roughness_map_black=1',
                     'roughness_map_gamma=0','roughness_map_invert="yes"','specular=0.5'):
            with self.subTest(text=text),self.assertRaises(ValueError):encode(('[material]\n'+text).encode())
    def test_generation_provenance_cache_and_last_good(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);textures=folder/'textures';textures.mkdir()
            name='a'*64+'.dds';source=textures/name
            Image.new('RGB',(8,8),(128,128,128)).save(source)
            original=source.read_bytes();payload=struct.pack('<Q72s',1,name.encode())
            table=struct.pack('<8IQ',0x31585453,1,1,1,3,3,len(payload),0,fnv(payload))+payload
            (folder/'live-materials.bin').write_bytes(table)
            config=folder/'materials.toml';config.write_text('[material]\nroughness_map_enabled=true\n')
            relay=Relay(folder,config);relay.poll();good=(folder/'material-controls.bin').read_bytes()
            acknowledge(folder,good)
            manifest=json.loads((folder/'roughness-manifest.json').read_text())
            target=textures/manifest['images'][0]['derived'];before=target.stat().st_mtime_ns
            prepare(folder,good);self.assertEqual(before,target.stat().st_mtime_ns)
            self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(),manifest['images'][0]['derived_sha256'])
            with Image.open(target) as image:self.assertEqual(image.size,(8,8))
            self.assertEqual(source.read_bytes(),original)
            config.write_text('[material]\nroughness_map_enabled=true\nroughness_map_gamma=2\n')
            with patch('roughness_maps.LIMIT',1):relay.poll()
            self.assertEqual((folder/'material-controls.bin').read_bytes(),good);self.assertEqual(relay.rejected,1)
    def test_disabled_does_not_require_assets(self):
        with tempfile.TemporaryDirectory() as folder:prepare(folder,encode(b'[material]\n'))

    def test_retirement_waits_for_matching_host_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);textures=folder/'textures';textures.mkdir()
            source=textures/('b'*64+'.dds');Image.new('RGB',(8,8),(128,128,128)).save(source)
            payload=struct.pack('<Q72s',1,source.name.encode())
            (folder/'live-materials.bin').write_bytes(struct.pack('<8IQ',0x31585453,1,1,1,3,3,len(payload),0,fnv(payload))+payload)
            config=folder/'config.toml';relay=Relay(folder,config)
            # Many edits under a tiny budget that permits only two map sets.
            with patch('roughness_maps.LIMIT',1300):
                for i in range(30):
                    config.write_text(f'[material]\nroughness_map_enabled=true\nroughness_map_strength={i/30}\n')
                    if i:
                        previous=(folder/'material-controls.bin').read_bytes()
                        relay.poll();self.assertEqual((folder/'material-controls.bin').read_bytes(),previous)
                        acknowledge(folder,previous)
                    relay.poll();self.assertEqual(relay.accepted,i+1)
                    self.assertLessEqual(len(list(textures.glob('roughness-*.dds'))),2)
                current=(folder/'material-controls.bin').read_bytes()
                # Corrupt/stale acknowledgement cannot free either protected set.
                before=set(textures.iterdir());(folder/'material-receipt.bin').write_bytes(bytes(40))
                relay.poll();self.assertEqual(set(textures.iterdir()),before)
                acknowledge(folder,encode(b'[material]\nroughness=0.123\n'))
                relay.poll();self.assertEqual(set(textures.iterdir()),before)
                acknowledge(folder,current);relay.poll()
                self.assertEqual(len(list(textures.glob('roughness-*.dds'))),1)
                self.assertGreater(relay.reclaimed_bytes,0);self.assertEqual(relay.rejected,0)

    def test_host_rejection_preserves_active_revision(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);textures=folder/'textures';textures.mkdir()
            config=folder/'config.toml';config.write_text('[material]\n')
            relay=Relay(folder,config);relay.poll();first=(folder/'material-controls.bin').read_bytes()
            active=struct.unpack_from('<Q',first,48)[0];acknowledge(folder,first)
            config.write_text('[material]\nroughness=0.3\n');relay.poll()
            second=(folder/'material-controls.bin').read_bytes();pending=struct.unpack_from('<Q',second,48)[0]
            original=textures/('c'*64+'.dds');original.write_bytes(b'original')
            old=textures/f'roughness-{"c"*64}-{active:016x}.dds';old.write_bytes(b'active')
            failed=textures/f'roughness-{"c"*64}-{pending:016x}.dds';failed.write_bytes(b'rejected')
            acknowledge(folder,second,active=active,status=2);relay.poll()
            self.assertEqual(old.read_bytes(),b'active');self.assertEqual(original.read_bytes(),b'original')
            self.assertFalse(failed.exists());self.assertIsNone(relay.pending_revision)

    def test_asset_publisher_after_relay_creation_is_adopted(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);textures=folder/'textures';textures.mkdir()
            config=folder/'config.toml';config.write_text('[material]\n')
            relay=Relay(folder,config)
            packet=encode(b'[material]\nroughness_map_enabled=true\n')
            revision=struct.unpack_from('<Q',packet,48)[0]
            image=textures/f'roughness-{"d"*64}-{revision:016x}.dds';image.write_bytes(b'protected')
            (folder/'material-controls.bin').write_bytes(packet)
            relay.poll();self.assertEqual(image.read_bytes(),b'protected')
            self.assertEqual(relay.pending_revision,revision);self.assertEqual(relay.accepted,0)

if __name__=='__main__':unittest.main()

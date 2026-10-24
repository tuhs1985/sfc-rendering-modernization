import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools/remix_runtime'),str(ROOT/'tools/d3d9_proof')]
from material_library import flat,streamed_layers
from material_binding import shader


class FlatMaterialTests(unittest.TestCase):
    def prepare(self,gpu,identity=1,roughness=.4):
        asset=gpu/'assets'/str(identity);stage=asset/'rtx-remix/mods/sfc-policy/mod.usda'
        stage.parent.mkdir(parents=True)
        images={'color':'textures/abc.dds','emission':'textures/def.dds'}
        values=[roughness,5,.2,.5,1,.9,0,1,0,.4]
        report=dict(values=values,groups=[dict(remix_hash='ABCDEF0123456789',images=images)],images={path:{} for path in images.values()})
        (asset/'material-binding.json').write_text(json.dumps(report))
        stage.write_text(shader('ABCDEF0123456789',images,values))
        for image in images.values():
            target=stage.parent/image;target.parent.mkdir(exist_ok=True);target.write_bytes(image.encode())
        return stage

    def test_paths_values_and_source_files_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            gpu=Path(directory)/'gpu';root=gpu/'rtx-remix/mods/sfc-policy';root.mkdir(parents=True)
            stage=self.prepare(gpu)
            before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in gpu.rglob('*') if p.is_file()}
            text,count=flat(root,[os.path.relpath(stage,root)])
            self.assertEqual(count,1);self.assertNotIn('subLayers',text)
            self.assertIn('float inputs:emissive_intensity = 5',text)
            self.assertIn('bool inputs:preload_textures = true',text)
            self.assertIn('@../../../assets/1/rtx-remix/mods/sfc-policy/textures/abc.dds@',text)
            self.assertEqual(before,{p:hashlib.sha256(p.read_bytes()).hexdigest() for p in before})

    def test_shared_definition_once_and_conflict_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            gpu=Path(directory)/'gpu';root=gpu/'rtx-remix/mods/sfc-policy';root.mkdir(parents=True)
            stages=[self.prepare(gpu,i) for i in (1,2)]
            layers=[os.path.relpath(p,root) for p in stages]
            self.assertEqual(flat(root,layers)[1],1)
            report=stages[1].parents[3]/'material-binding.json'
            data=json.loads(report.read_text());data['values'][0]=.8;report.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'Conflicting'):flat(root,layers)

    def test_bounds_and_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)/'gpu/rtx-remix/mods/sfc-policy';root.mkdir(parents=True)
            for layers in ([],['missing']*65,['../../../../../../outside/mod.usda']):
                with self.assertRaises(ValueError):flat(root,layers)

    def test_stream_derivative_changes_only_preload_not_source_or_images(self):
        with tempfile.TemporaryDirectory() as directory:
            gpu=Path(directory)/'gpu';root=gpu/'rtx-remix/mods/sfc-policy';root.mkdir(parents=True)
            stage=self.prepare(gpu);before={p:p.read_bytes() for p in gpu.rglob('*') if p.is_file()}
            layers,count=streamed_layers(root,[os.path.relpath(stage,root)])
            self.assertEqual(count,1)
            self.assertEqual((root/layers[0]).read_text(),stage.read_text().replace('bool inputs:preload_textures = true','bool inputs:preload_textures = false'))
            self.assertEqual(before,{p:p.read_bytes() for p in before})
            stage.write_text(stage.read_text().replace('preload_textures = true','preload_textures = unknown'))
            with self.assertRaisesRegex(ValueError,'Unqualified'):streamed_layers(root,[os.path.relpath(stage,root)])

    def test_stream_bounds_and_qualification_rejection(self):
        from qualify_multiship import inspect
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)/'gpu/rtx-remix/mods/sfc-policy';root.mkdir(parents=True)
            for layers in ([],['missing']*65,['../../../../outside/mod.usda']):
                with self.assertRaises(ValueError):streamed_layers(root,layers)
        with tempfile.TemporaryDirectory(dir=ROOT/'artifacts/remix-runtime/runs') as directory:
            (Path(directory)/'result.json').write_text(json.dumps(dict(multi_ship_fixture=True,fixture_exit=0,host_exit=0,material_texture_loading='stream')))
            with self.assertRaisesRegex(ValueError,'cannot qualify'):inspect(directory)

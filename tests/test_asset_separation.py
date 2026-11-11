"""Exercise actual asset helpers across the application/development boundary."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]


class AssetSeparationTests(unittest.TestCase):
    def run_python(self,code,*arguments):
        return subprocess.run([sys.executable,'-I','-B','-c',code,str(ROOT),*arguments],
                              capture_output=True,text=True,timeout=20,cwd=tempfile.gettempdir())

    def test_legacy_and_application_imports_keep_one_implementation(self):
        code=r'''
import importlib,sys
from pathlib import Path
root=Path(sys.argv[1]);order=sys.argv[2]
tools=['remix_runtime','d3d9_proof','scene_bridge','remix_ingest','m1_component']
sys.path[:0]=[str(root/'tools'/name) for name in tools]
if order=='application':sys.path.insert(0,str(root/'src/assets'))
names=('parallel_assets','scene_bundle','material_binding','material_library','roughness_maps','mesh_checksum','damage_materials','damage_mapping','break_scene')
first={name:importlib.import_module(name) for name in names}
for name,module in first.items():assert Path(module.__file__).resolve()==root/'src/assets'/(name+'.py'),module.__file__
sys.path[:0]=[str(root/'src/assets')]+[str(root/'tools'/name) for name in tools]
assert all(importlib.import_module(name) is module for name,module in first.items())
assert 'asset_capture_review' not in sys.modules
print('ASSET_CANONICAL_IDENTITY_PASS')
'''
        for order in ('legacy','application'):
            with self.subTest(order=order):
                result=self.run_python(code,order)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertIn('ASSET_CANONICAL_IDENTITY_PASS',result.stdout)

    def test_normal_image_material_and_task_work_does_not_import_review(self):
        code=r'''
import importlib.abc,sys,tempfile,time
from pathlib import Path
root=Path(sys.argv[1]);sys.path[:0]=[str(root/'src/assets'),str(root/'src/runtime')]+[str(root/'tools'/name) for name in ('remix_runtime','d3d9_proof','scene_bridge','remix_ingest','m1_component')]
blocked={'asset_capture_review','textured_asset','kit_live_scene','prepare_break_replay','run_direct64','run_offline','asset_preparation'}
class Guard(importlib.abc.MetaPathFinder):
 def find_spec(self,fullname,path=None,target=None):
  if fullname.split('.')[0] in blocked:raise AssertionError('Unexpected review import: '+fullname)
sys.meta_path.insert(0,Guard())
import mesh_decode
assert 'live_scene' not in sys.modules,'Neutral decoding imported transport'
from parallel_assets import Tasks,load_image,material_piece
from material_binding import validate_generated_dds
from PIL import Image
with tempfile.TemporaryDirectory() as temp:
 directory=Path(temp);Image.new('RGBA',(4,3),(80,120,160,255)).save(directory/'hull.png')
 tasks=Tasks(record_timings=False)
 try:
  tasks.add(('image','hull'),lambda:load_image(directory,'hull.png'))
  tasks.add(('material','hull'),lambda image:material_piece(image,None,(.5,1,0,0,0,1,0,1,0,1)),(('image','hull'),))
  until=time.monotonic()+5
  while time.monotonic()<until:
   tasks.pump();material=tasks.tasks[('material','hull')]
   if material['state']=='failed':raise AssertionError(material['error'])
   if material['state']=='done':break
   time.sleep(.001)
  assert material['state']=='done'
  piece=material['value'];assert set(piece['images'])=={'color'}
  for data,metadata in piece['encoded'].values():validate_generated_dds(data,(4,3))
  assert tasks.spans==[]
 finally:tasks.close()
assert not blocked.intersection(sys.modules)
print('NORMAL_ASSET_WORK_WITHOUT_REVIEW_PASS')
'''
        result=self.run_python(code)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('NORMAL_ASSET_WORK_WITHOUT_REVIEW_PASS',result.stdout)

    def test_review_helpers_remain_available_only_when_explicitly_requested(self):
        code=r'''
import sys
from pathlib import Path
root=Path(sys.argv[1]);sys.path[:0]=[str(root/'src/assets'),str(root/'src/runtime')]+[str(root/'tools'/name) for name in ('remix_runtime','d3d9_proof','scene_bridge','remix_ingest','m1_component')]
import scene_bundle,material_library,break_scene,live_scene
assert 'asset_capture_review' not in sys.modules
from scene_bundle import snapshots
from material_library import streamed_layers
from break_scene import decode_capture,decode_piece
from live_scene import ImageStore,qualify_mesh,SceneConsumer
import asset_capture_review
assert Path(asset_capture_review.__file__).resolve()==root/'tools/asset_diagnostics/asset_capture_review.py'
for value in (snapshots,streamed_layers,decode_capture,decode_piece,ImageStore,qualify_mesh,SceneConsumer):assert value.__module__=='asset_capture_review'
print('DEVELOPMENT_REVIEW_COMPATIBILITY_PASS')
'''
        result=self.run_python(code)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('DEVELOPMENT_REVIEW_COMPATIBILITY_PASS',result.stdout)


if __name__=='__main__':unittest.main()

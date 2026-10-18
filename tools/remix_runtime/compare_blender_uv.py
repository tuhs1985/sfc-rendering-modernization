"""Offline Blender-only convention control and OBJ importer readback.

Run with Blender --background --factory-startup --threads 2 --python this.py
-- OUTPUT_DIRECTORY EXISTING_OBJ. One 128-square CPU render, no game/SDK hooks.
The caller must impose a 90-second process timeout and 8-MiB output cap.
"""
import json
from pathlib import Path
import sys

import bpy


def main():
    output, source = map(Path, sys.argv[sys.argv.index('--') + 1:])
    if output.exists():
        raise ValueError('Refusing to overwrite evidence')
    output.mkdir(parents=True)
    # Exercise the actual installed OBJ importer, not a second OBJ parser alone.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.obj_import(filepath=str(source))
    obj = next(o for o in bpy.context.scene.objects if o.type == 'MESH')
    uv = obj.data.uv_layers.active
    faces = []
    for poly in obj.data.polygons:
        material = obj.data.materials[poly.material_index]
        for loop_index in poly.loop_indices:
            loop = obj.data.loops[loop_index]
            faces.append([material.name, list(obj.data.vertices[loop.vertex_index].co),
                          list(uv.data[loop_index].uv)])
    (output / 'imported-corners.json').write_text(json.dumps(faces))

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 1
    scene.render.resolution_x = scene.render.resolution_y = 128
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    image = bpy.data.images.new('asymmetric-corners', width=8, height=8)
    # Blender pixel storage starts at bottom left. Saved PNG is independently
    # checked by the caller, so this does not assume the result being tested.
    colors = [(0.5, .02, .02, 1), (.02, .5, .02, 1),
              (.02, .02, .5, 1), (.5, .5, .02, 1)]
    image.pixels = [c for y in range(8) for x in range(8)
                    for c in colors[(0 if y >= 4 else 2) + (x >= 4)]]
    image.filepath_raw = str(output / 'corners.png')
    image.file_format = 'PNG'
    image.save()
    mesh = bpy.data.meshes.new('quad')
    mesh.from_pydata([(-1, 1, 0), (1, 1, 0), (-1, -1, 0), (1, -1, 0)],
                     [], [(0, 2, 1), (2, 3, 1)])
    layer = mesh.uv_layers.new()
    coords = [(0, 0), (1, 0), (0, 1), (1, 1)]
    for loop in mesh.loops:
        layer.data[loop.index].uv = coords[loop.vertex_index]
    quad = bpy.data.objects.new('quad', mesh)
    scene.collection.objects.link(quad)
    material = bpy.data.materials.new('unlit-original-image')
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    tex = nodes.new('ShaderNodeTexImage')
    tex.image = image
    tex.interpolation = 'Closest'
    emission = nodes.new('ShaderNodeEmission')
    out = nodes.new('ShaderNodeOutputMaterial')
    material.node_tree.links.new(tex.outputs['Color'], emission.inputs['Color'])
    material.node_tree.links.new(emission.outputs[0], out.inputs['Surface'])
    mesh.materials.append(material)
    camera_data = bpy.data.cameras.new('camera')
    camera = bpy.data.objects.new('camera', camera_data)
    scene.collection.objects.link(camera)
    camera.location = (0, 0, 5)
    camera_data.type = 'ORTHO'
    camera_data.ortho_scale = 2.5
    scene.camera = camera
    scene.render.filepath = str(output / 'blender-quad.png')
    bpy.ops.render.render(write_still=True)
    (output / 'result.json').write_text(json.dumps(dict(
        blender=bpy.app.version_string, imported_corners=len(faces),
        input_obj=str(source), control='top-left position UV(0,0); unlit image',
        result='CAPTURED_NOT_YET_ADJUDICATED'), indent=2))


if __name__ == '__main__':
    main()

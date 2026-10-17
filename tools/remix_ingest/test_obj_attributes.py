import copy
import unittest
from compare_obj_attributes import compare

OBJ = 'v 0 0 0\nv 1 0 0\nv 0 1 0\nvt 0 0\nvt 1 0\nvt 0 1\nvn 0 0 1\nusemtl source_000\nf 1/1/1 2/2/1 3/3/1\n'
MESH = {'points': [[0,0,0],[1,0,0],[0,1,0]], 'indices': [0,1,2], 'counts': [3],
        'uv': [[0,0],[1,0],[0,1]], 'normals': [[0,0,1]]*3,
        'uv_interpolation': 'faceVarying', 'normal_interpolation': 'faceVarying',
        'material': '/Looks/source_000'}


class AttributeTests(unittest.TestCase):
    def test_matching_corner_attributes(self):
        self.assertTrue(compare(OBJ, {'meshes': [MESH]})['match'])

    def test_changed_uv_normal_group_or_winding_rejected(self):
        for field, value in [('uv', [[0,0],[0,1],[1,0]]),
                             ('normals', [[0,0,-1]]*3), ('material', '/Looks/source_001'),
                             ('indices', [0,2,1])]:
            with self.subTest(field=field):
                mesh = copy.deepcopy(MESH)
                mesh[field] = value
                self.assertFalse(compare(OBJ, {'meshes': [mesh]})['match'])

    def test_incomplete_or_unknown_interpolation_rejected(self):
        for field, value in [('uv', []), ('normal_interpolation', 'vertex')]:
            mesh = copy.deepcopy(MESH)
            mesh[field] = value
            with self.assertRaises(ValueError):
                compare(OBJ, {'meshes': [mesh]})

    def test_float_boundary_roundoff_admitted_but_large_change_rejected(self):
        mesh = copy.deepcopy(MESH)
        mesh['uv'][0][0] = 0.00000004
        self.assertTrue(compare(OBJ, {'meshes': [mesh]})['match'])
        mesh['uv'][0][0] = 0.00001
        self.assertFalse(compare(OBJ, {'meshes': [mesh]})['match'])


if __name__ == '__main__':
    unittest.main()

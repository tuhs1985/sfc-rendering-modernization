import unittest
from audit_mesh_surface import audit


class SurfaceAuditTests(unittest.TestCase):
    def data(self, sign=1):
        return {'meshes': [{'path': '/square', 'points': [[0,0,0], [1,0,0], [1,1,0], [0,1,0]],
                           'indices': [0,1,2,0,2,3], 'counts': [3,3], 'normals': [[0,0,sign]]*6,
                           'normal_interpolation': 'faceVarying', 'orientation': 'rightHanded'}]}

    def test_reports_opposition_not_mesh_repair(self):
        data = self.data(-1)
        result = audit(data)
        self.assertEqual(result['totals']['opposed'], 2)
        self.assertEqual(result['edge_use_counts'], {1: 4, 2: 1})
        self.assertEqual(result['same_direction_shared_edges'], 0)
        self.assertEqual(data['meshes'][0]['orientation'], 'rightHanded')

    def test_aligned_and_malformed_geometry(self):
        self.assertEqual(audit(self.data())['totals']['aligned'], 2)
        left = self.data(-1); left['meshes'][0]['orientation'] = 'leftHanded'
        self.assertEqual(audit(left)['totals']['aligned'], 2)
        data = self.data(); data['meshes'][0]['indices'][0] = 9
        with self.assertRaises(ValueError): audit(data)

import math,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
from light_controls import angled_direction,validate

class LightAngleTests(unittest.TestCase):
    def test_zero_preserves_exact_captured_direction(self):
        original=[.3,-.4,.8660254]
        self.assertIs(angled_direction(original,{}),original)
    def test_raise_source_25_degrees_not_light_ray(self):
        d=angled_direction([-1,0,0],{'elevation_degrees':25})
        self.assertAlmostEqual(d[0],-math.cos(math.radians(25)))
        self.assertAlmostEqual(d[2],-math.sin(math.radians(25)))
        self.assertAlmostEqual(d[1],0)
        self.assertAlmostEqual(sum(v*v for v in d),1)
    def test_absolute_three_point_bearings_and_poles(self):
        d=angled_direction([0,0,-1],{'angle_mode':'absolute','azimuth_degrees':90,'elevation_degrees':25})
        self.assertAlmostEqual(d[0],0);self.assertLess(d[1],0);self.assertLess(d[2],0)
        d=angled_direction([0,0,-1],{'elevation_degrees':25})
        self.assertAlmostEqual(d[2],-1)
    def test_azimuth_stays_in_tactical_xy_plane(self):
        d=angled_direction([-1,0,0],{'azimuth_degrees':90})
        self.assertAlmostEqual(d[0],0)
        self.assertAlmostEqual(d[1],-1)
        self.assertAlmostEqual(d[2],0)

    def test_captured_world_basis_not_mesh_local_basis(self):
        # Actual supplied transform from 20261016-223535 LIVE-SCENE first
        # ship: local Y (thin/up mesh axis) maps to world +Z, not world Y.
        matrix=[[-1,0,0,300],[0,0,1,200],[0,1,0,0],[0,0,0,1]]
        world_up=[row[1] for row in matrix[:3]]
        ray=angled_direction([-1,0,0],{'elevation_degrees':25})
        source_height=-sum(a*b for a,b in zip(ray,world_up))
        self.assertAlmostEqual(source_height,math.sin(math.radians(25)))

    def test_saved_look_migration_for_qualified_bank(self):
        d=[.9889363515567038,0,-.14834046167420217]
        actual=angled_direction(d,{'elevation_degrees':10})
        expected=[.9481531354046523,0,-.3178138320185687]
        for a,b in zip(actual,expected):self.assertAlmostEqual(a,b)
        actual=angled_direction([0,0,1],{'azimuth_degrees':0,'elevation_degrees':10})
        for a,b in zip(actual,[-.17364817766693041,0,.984807753012208]):self.assertAlmostEqual(a,b)

    def test_invalid_controls_rejected_and_uniform_dome_unchanged(self):
        registry={'native_directional_0':{'kind':'directional'}}
        base=dict(schema_version=1,backend='remix_sdk_0_6_4')
        for fields in ({'angle_mode':'camera'},{'elevation_degrees':91},{'azimuth_degrees':float('nan')},{'type':'dome','elevation_degrees':25}):
            with self.assertRaises(ValueError):validate(dict(base,lights=[dict(id='native_directional_0',**fields)]),registry)
        validate(dict(base,lights=[dict(id='native_directional_0',type='dome',elevation_degrees=0)]),registry)

if __name__=='__main__':unittest.main()

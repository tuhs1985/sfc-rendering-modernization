import ctypes
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
import return_channel as wire

class ReturnWireTests(unittest.TestCase):
    def state(self):
        s=wire.State();s.magic=wire.MAGIC;s.version=wire.VERSION;s.bytes=256;s.creatorPid=1;s.width=s.height=256;s.format=wire.FORMAT;s.qpcFrequency=1000;return s
    def test_layout(self):
        self.assertEqual(ctypes.sizeof(wire.State),256)
        self.assertEqual(wire.State.sharedHandle.offset,32)
        self.assertEqual(wire.State.epoch.offset,64)
        self.assertEqual(wire.State.renderEpoch.offset,136)
        self.assertEqual(wire.State.presentedEpoch.offset,140)
        self.assertEqual(wire.State.visibilityVersion.offset,144)
        self.assertEqual(wire.State.depthMultisamples.offset,172)
        self.assertEqual(wire.State.visibilityScope.offset,176)
        self.assertEqual(wire.State.depthViewFormat.offset,180)
    def test_optional_visibility_is_absent_by_default(self):
        s=self.state()
        self.assertTrue(wire.valid(s))
        self.assertEqual(s.visibilityVersion,0)
        self.assertEqual(s.visibilitySamples,0)
        s.visibilityVersion=1;s.visibilitySamples=8;s.depthPresentSamples=0
        self.assertTrue(wire.valid(s))
    def test_visibility_never_claims_scene_depth(self):
        s=self.state()
        self.assertEqual(wire.visibility_result(s),'NOT_REQUESTED')
        s.visibilityVersion=1
        self.assertEqual(wire.visibility_result(s),'INCOMPLETE')
        s.visibilitySamples=8
        self.assertEqual(wire.visibility_result(s),'NO_DSV_AT_LATE_INSERTION')
        s.depthPresentSamples=1;s.depthWidth=1920;s.depthHeight=1080
        self.assertEqual(wire.visibility_result(s),'DSV_DESCRIPTOR_ONLY_UNQUALIFIED')
        s.depthPresentSamples=9
        self.assertEqual(wire.visibility_result(s),'INVALID_OBSERVATION')
        s.depthPresentSamples=0;s.visibilitySamples=9
        self.assertEqual(wire.visibility_result(s),'INVALID_OBSERVATION')
    def test_header(self):
        self.assertTrue(wire.valid(self.state()))
        for field,value in [('magic',0),('version',1),('bytes',128),('creatorPid',0),('width',4096),('height',0),('format',0),('qpcFrequency',0)]:
            with self.subTest(field=field):
                s=self.state();setattr(s,field,value);self.assertFalse(wire.valid(s))
    def test_early_depth_scope_is_distinct_and_unqualified(self):
        s=self.state();s.visibilityVersion=1;s.visibilityScope=2;s.visibilitySamples=8
        self.assertEqual(wire.visibility_result(s),'NO_DSV_AT_EARLY_PRESENT')
        s.depthPresentSamples=8;s.depthWidth=1024;s.depthHeight=768;s.depthFormat=45
        self.assertEqual(wire.visibility_result(s),'EARLY_DSV_DESCRIPTOR_ONLY_UNQUALIFIED')
        s.visibilityScope=3
        self.assertEqual(wire.visibility_result(s),'INVALID_OBSERVATION')
    def test_names(self):
        self.assertTrue(wire.valid_name(r'Local\SFC-Remix-Return-{12345678-1234-1234-1234-123456789ABC}'))
        for name in ['Global\\SFC-Remix-Return-{12345678-1234-1234-1234-123456789ABC}',r'Local\SFC-Remix-Return-../../x',r'Local\SFCBridge_0123','',r'Local\SFC-Remix-Return-{bad}']:
            self.assertFalse(wire.valid_name(name))
    def test_independent_owner_and_epoch_fields(self):
        s=self.state();s.gamePid=10;s.epoch=2;s.renderEpoch=1;s.produced=5;s.acknowledged=4
        self.assertNotEqual(s.epoch,s.renderEpoch)
        self.assertEqual(s.produced-s.acknowledged,1)
        self.assertEqual(s.gamePid,10)
if __name__=='__main__':unittest.main()

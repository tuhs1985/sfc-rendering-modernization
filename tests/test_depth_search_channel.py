import ctypes as C
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/remix_runtime'))
import depth_search_channel as wire

class DepthSearchTests(unittest.TestCase):
    def setup_data(self):
        memory=C.create_string_buffer(4096)
        d=wire.Data.from_buffer(memory,256)
        d.magic=wire.MAGIC;d.version=1;d.bytes=2304;d.capacity=32
        d.status=4;d.installedMask=d.restoredMask=15
        for p in d.phases:p.calls=100;p.missing=100
        return memory,d
    def test_layout_and_no_depth(self):
        memory,d=self.setup_data()
        self.assertEqual(C.sizeof(wire.Data),2304)
        s=wire.snapshot(C.addressof(memory))
        self.assertEqual(wire.verdict(s),'NO_BOUND_DSV_AT_SIX_ENGINE_PRESENTATION_PHASES')
    def test_found_never_means_qualified(self):
        memory,d=self.setup_data();d.resourceCount=1;d.resources[0].format=44
        d.phases[0].found=100;d.phases[0].missing=0
        s=wire.snapshot(C.addressof(memory))
        self.assertEqual(wire.verdict(s),'DEPTH_DESCRIPTORS_FOUND_UNQUALIFIED')
    def test_limits_are_explicit_partial(self):
        for field in ('wrongThread','noContext','busy','invalid'):
            memory,d=self.setup_data();setattr(d.phases[0],field,1)
            self.assertEqual(wire.verdict(wire.snapshot(C.addressof(memory))),'PARTIAL_COVERAGE_LIMIT')
        memory,d=self.setup_data();d.overflow=1
        self.assertEqual(wire.verdict(wire.snapshot(C.addressof(memory))),'PARTIAL_COVERAGE_LIMIT')
    def test_cleanup_and_missing_phase(self):
        memory,d=self.setup_data();d.restoredMask=0
        self.assertEqual(wire.verdict(wire.snapshot(C.addressof(memory))),'PARTIAL_CLEANUP_OR_HOOK_ERROR')
        d.restoredMask=15;d.phases[0].calls=0
        self.assertEqual(wire.verdict(wire.snapshot(C.addressof(memory))),'PARTIAL_UNOBSERVED_PHASE')
    def test_malformed_header_and_count(self):
        memory,d=self.setup_data();d.resourceCount=33
        with self.assertRaises(ValueError):wire.snapshot(C.addressof(memory))
        d.resourceCount=0;d.magic=0
        with self.assertRaises(ValueError):wire.snapshot(C.addressof(memory))
    def test_phase_stopped_early_is_not_full_coverage(self):
        memory,d=self.setup_data();d.startTick=100;d.endTick=90100
        for p in d.phases:p.lastTick=90090
        d.phases[0].lastTick=8100
        s=wire.snapshot(C.addressof(memory))
        self.assertEqual(s['captureWindowMs'],90000)
        self.assertEqual(wire.verdict(s),'PARTIAL_PHASE_NOT_ACTIVE_NEAR_STOP')

if __name__=='__main__':unittest.main()

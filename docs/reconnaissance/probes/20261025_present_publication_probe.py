"""Run190 isolated material-publication control. No game or native policy edit.

Hold enhanced stage publication until the existing native post-bootstrap selection
signal, then publish the same prepared pieces. This is attribution, not a fix.
"""
import argparse
import ctypes
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'tools/remix_runtime'), str(ROOT / 'tools/d3d9_proof')]
HERE = ROOT / 'artifacts/present-stall'


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def run(defer):
    import live_owner_timing as live
    import progressive_scene_relay as progressive
    import run_return_fixture as fixture
    from run_offline import storage, AGGREGATE_BYTES

    HERE.mkdir(exist_ok=True)
    assert storage() + 1024**3 < AGGREGATE_BYTES, 'Existing fixture reservation required'
    production = [live.EXE, live.RUNTIME, ROOT / 'tools/d3d9_proof/d3d9_direct_host.cpp',
                  ROOT / 'tools/remix_runtime/progressive_scene_relay.py']
    before_hashes = {str(p.relative_to(ROOT)): digest(p) for p in production}
    before = set((ROOT / 'artifacts/remix-runtime/runs').iterdir())
    events = []
    original = progressive.Relay.flush_enhancements

    def flush(self):
        if defer:
            # live_owner_input::start sets this only AFTER bootstrap output/ACK.
            # initialize() zeros it; Python does not write the selected word.
            selected = ctypes.c_uint64.from_address(self.receiver.channel.view + live.OFFSET + 32).value
            if not selected:
                if not getattr(self, '_probe_held', False):
                    self._probe_held = True
                    events.append(dict(event='hold',at_ns=time.perf_counter_ns()))
                return
            if not getattr(self, '_probe_released', False):
                self._probe_released = True
                events.append(dict(event='release_after_bootstrap',at_ns=time.perf_counter_ns(),selected=selected))
        original(self)

    progressive.Relay.flush_enhancements = flush
    sys.argv = ['run_return_fixture.py', '--multi-ship', '--multi-ship-resources',
                '--prewarm', '--startup-profile', '--pipeline-mode', 'performance',
                '--parallel-assets', '--asset-admission-service', 'on',
                '--texture-upload', 'initial-data']
    try:
        fixture.main()
    finally:
        assert all(digest(ROOT / p) == h for p, h in before_hashes.items()), 'Production input changed'
        folders = set((ROOT / 'artifacts/remix-runtime/runs').iterdir()) - before
        receipt = dict(diagnostic_only=True,production_qualification_eligible=False,
                       defer_enhancements_until_post_bootstrap=defer,events=events,
                       unchanged_production=before_hashes,folders=[str(p) for p in folders],
                       meaning='Attribution only;unchanged final prepared material content required;not a gameplay/default qualification')
        for folder in folders:
            result = folder / 'result.json'
            if result.is_file():
                data = json.loads(result.read_text())
                data['diagnostic_original_reference_locks'] = data.pop('multi_ship_build_locks', None)
                data['production_qualification_eligible'] = False
                data['present_publication_probe'] = receipt
                result.write_text(json.dumps(data, indent=2))
            (folder / 'present-publication-probe.json').write_text(json.dumps(receipt, indent=2))
        (HERE / ('deferred.json' if defer else 'control.json')).write_text(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--defer-enhancements', action='store_true')
    args = parser.parse_args()
    run(args.defer_enhancements)

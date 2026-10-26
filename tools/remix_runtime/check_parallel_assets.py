"""Bounded CPU replay of an accepted captured asset, never launches SFC/Remix."""
import argparse
import datetime as dt
import hashlib
import json
import shutil
import sys
import time
from collections import deque
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
for directory in ('d3d9_proof','scene_bridge','remix_ingest'):sys.path.insert(0,str(ROOT/'tools'/directory))
from progressive_scene_relay import Relay
from parallel_assets import Pipeline
from multi_scene_resources import Reservations
from run_return_game import TEST,preflight
from run_offline import storage


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--baseline',action='store_true');args=parser.parse_args()
    preflight()
    # Include previous CPU controls in aggregate admission, not just renderer runs.
    extra=sum(p.stat().st_size for n in ('initial-readiness','render-survey','effect-probe','remix-api-proof') for p in (ROOT/'artifacts'/n).rglob('*') if p.is_file())
    inventory=storage()+extra
    if inventory+512*1024**2>20_000_000_000:raise ValueError('CPU replay512MiB admission within20GB')
    original=ROOT/'artifacts/remix-runtime/runs/20261024-222711-351784-return-fixture'
    accepted=json.loads((original/'gpu/assets/1/scene.json').read_text())
    golden=json.loads((original/'gpu/assets/1/material-binding.json').read_text())
    source=ROOT/accepted['source_packet'];row=accepted['fresh_preparation_row']
    out=ROOT/'artifacts/initial-readiness'/('parallel-cpu-'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f'));(out/'gate').mkdir(parents=True)
    shutil.copyfile(source,out/'gate'/source.name);shutil.copyfile(source.with_suffix('.json'),(out/'gate'/source.name).with_suffix('.json'))
    (out/'gate/run-metadata.json').write_text(json.dumps(dict(live_channel=accepted['source_session'])))
    relay=object.__new__(Relay);relay.folder=out;relay.root=TEST;relay.output_reservations=Reservations(inventory=inventory)
    relay.material_config=(original/'gpu/assets/1/materials-config-accepted.toml').read_bytes()
    relay.anchor_id=None;relay.path_count=0;relay.material_pieces={};relay.progressive_events=[];relay.partial=[]
    relay.pending_enhancements=deque()
    relay.pending_stage_ids=set();relay.pending_complete_ids=set();relay.pending_library=False;relay.publication_busy_since=None;relay.publication_retries=0
    relay.material_keys={};relay.layers=[];relay.material_events=[];relay.image_bytes=0;relay.original_images=set();relay.resident={}
    relay.process=None;relay.initial_ids=None;relay.offline_fixture=True;relay.material_library='layers';relay.material_texture_loading='preload'
    relay.preparer=Pipeline(relay);started=time.perf_counter_ns()
    try:
        if args.baseline:
            from multi_scene_relay import Relay as Baseline
            relay.mode='performance'
            signature,mesh=Baseline.identify_asset(relay,row)
            gpu,manifest,_,_,_,_,_=Baseline.prepare_asset(relay,row,mesh,1)
            job=dict(phase='ready',gpu=gpu,manifest=manifest)
        else:
            relay.preparer.submit(1,row)
            while time.perf_counter_ns()-started<30_000_000_000:
                relay.collect_prepared()
                # CPU-only consumer accepts base immediately; no GPU display claim.
                for j in relay.preparer.jobs.values():
                    if 'path_id' in j:j['published']=True
                relay.flush_enhancements()
                if relay.preparer.settled([1]) and not relay.pending_enhancements and not relay.pending_stage_ids and not relay.pending_library:break
                time.sleep(.001)
            job=relay.preparer.jobs[1]
        if job['phase']!='ready' or relay.partial:raise ValueError('Preparation incomplete: '+str(relay.partial or job.get('error')))
        current=json.loads((job['gpu']/'material-binding.json').read_text())
        assert job['manifest']['geometry_sha256']==accepted['geometry_sha256']
        assert current['images']==golden['images']
        assert current['mod_sha256']==golden['mod_sha256']
        assert [t['original_sha256'] for t in job['manifest']['textures']]==[t['original_sha256'] for t in accepted['textures']]
        result=dict(scope='CPU-only retained capture;not runtime consumption/display timing',baseline=args.baseline,
            geometry_and_original_images_exact=True,all_derived_metadata_and_hashes_exact=True,material_stage_exact=True,
            elapsed_seconds=(time.perf_counter_ns()-started)/1e9,events=relay.progressive_events,preparation=relay.preparer.report(),
            generated_bytes=sum(p.stat().st_size for p in out.rglob('*') if p.is_file()),source_run=str(original.relative_to(ROOT)))
        (out/'analysis.json').write_text(json.dumps(result,indent=2))
        print('Evidence:',out);print(json.dumps({k:v for k,v in result.items() if k not in ('events','preparation')},indent=2))
    finally:relay.preparer.close()


if __name__=='__main__':main()

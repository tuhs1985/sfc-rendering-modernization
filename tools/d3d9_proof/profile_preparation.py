"""Bounded preparation profiling ONLY. Never launches SFC or Remix.

First/repeat in this process;does not flush the OS cache or claim cold-boot timing.
"""
import argparse
import cProfile
import datetime as dt
import json
from pathlib import Path
import pstats
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/scene_bridge'))
from run_offline import storage,AGGREGATE_BYTES
from scene_bundle import prepare
from material_binding import prepare as materials
from run_direct64 import resize_output

PYSH=Path(r'C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe')
SOURCE=ROOT/'artifacts/remix-runtime/runs/20261021-024303-198180-in-game'
GAME=ROOT.parent/'SFC-Remix-Return-Test'

def stage(name,callback,profile=True):
    profiler=cProfile.Profile();started=time.perf_counter()
    result=profiler.runcall(callback) if profile else callback();seconds=time.perf_counter()-started
    if not profile:
        return result,dict(stage=name,seconds=seconds,top=[])
    stats=pstats.Stats(profiler)
    top=[]
    for (path,line,function),(primitive,calls,total,cumulative,_) in sorted(stats.stats.items(),key=lambda item:item[1][3],reverse=True)[:24]:
        top.append(dict(function=f'{Path(path).name}:{line}:{function}',calls=calls,self_seconds=total,cumulative_seconds=cumulative))
    return result,dict(stage=name,seconds=seconds,top=top)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');parser.add_argument('--timing-only',action='store_true');parser.add_argument('--samples',type=int,choices=(1,2),default=2);args=parser.parse_args()
    if not args.execute:print('Preparation profile requires --execute;no game/runtime launch');return
    original=json.loads((SOURCE/'gpu/scene.json').read_text())
    asset=ROOT/original['source_packet'];row=original['fresh_preparation_row']
    for label in ('first_in_process','repeat_in_process')[:args.samples]:
        if storage()+192*1024*1024>AGGREGATE_BYTES:raise ValueError('Preparation profile192MiB reservation within20GB required')
        folder=ROOT/'artifacts/d3d9-proof/material-runs'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
        folder.mkdir();output=folder/'baseline'
        report=dict(result='PREPARATION_PROFILE_IN_PROGRESS',label=label,profiler_enabled=not args.timing_only,sfc_launched=False,remix_launched=False,os_cache_flushed=False,source=str(asset.relative_to(ROOT)),stages=[])
        try:
            manifest,record=stage('geometry_and_original_image_uploads',lambda:prepare(asset,output,GAME,live_record=row),not args.timing_only);report['stages'].append(record)
            _,record=stage('output_extent',lambda:resize_output(output,(1920,1080),manifest),not args.timing_only);report['stages'].append(record)
            bound,record=stage('material_hashes_and_derived_images',lambda:materials(output,GAME),not args.timing_only);report['stages'].append(record)
            report.update(result='PREPARATION_PROFILE_COMPLETE',groups=len(bound['groups']),derived_images=len(bound['images']),image_bytes=bound['image_bytes'])
        finally:
            report['total_profiled_seconds']=sum(s['seconds'] for s in report['stages'])
            (folder/'result.json').write_text(json.dumps(report,indent=2))
        # Existing exact-file/hash-verified generated-copy compaction. No source
        # captures,game files,profiles,manifests or scene records are removed.
        subprocess.run([str(PYSH),'-NoProfile','-File',str(ROOT/'tools/d3d9_proof/archive_material_fixture.ps1'),'-RunDirectory',str(folder)],check=True,timeout=60)
        print(json.dumps(dict(folder=str(folder.relative_to(ROOT)),label=label,stages=[dict(stage=s['stage'],seconds=s['seconds'],top=s['top'][:8]) for s in report['stages']]),indent=2),flush=True)

if __name__=='__main__':main()

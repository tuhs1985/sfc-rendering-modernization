"""Known GPU quadrants through the current interop direction; no SFC launch."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[2]


def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def run(width,height):
    if not 2<=width<=3840 or not 2<=height<=2160:raise ValueError('Probe extent2..3840x2..2160')
    folder=ROOT/'artifacts/alpha/share-probe'/dt.datetime.now(dt.timezone.utc).strftime(f'%Y%m%d-%H%M%S-%f-{width}x{height}')
    folder.mkdir(parents=True)
    host=ROOT/'artifacts/alpha/share-probe/shared_layout_probe.exe'
    runtime=ROOT/'artifacts/remix-runtime/deps/candidate-1.6.1/runtime/d3d9_x64.dll'
    record=dict(scope='GPU sharing only;not Remix scene rendering,resize or gameplay',extent=[width,height],
                host_sha256=digest(host),runtime_sha256=digest(runtime),
                source_sha256=digest(ROOT/'tools/release/shared_layout_probe.cpp'),
                header_sha256=digest(ROOT/'artifacts/remix-runtime/deps/candidate-1.6.1/remix_c.h'),sfc_launched=False)
    (folder/'manifest.json').write_text(json.dumps(record,indent=2))
    env=dict(os.environ,RTX_AUTOMATION_DISABLE_BLOCKING_DIALOG_BOXES='1',RTX_CAPTURE_REMIX_CONFIGS='0')
    command=[str(ROOT/'artifacts/remix-ingest/bin/bounded_job.exe'),str(folder),'45',str(32*1024*1024),str(2*1024*1024),str(host),str(runtime),str(width),str(height)]
    process=subprocess.run(command,env=env,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
    text=(folder/'job-console.log').read_text(errors='replace')
    for name,pattern in (
        ('source',r'GPU_SOURCE_LAYOUT width=(\d+) height=(\d+) row_pitch=(\d+) mismatches=(\d+)'),
        ('native',r'GPU_SHARED_LAYOUT width=(\d+) height=(\d+) row_pitch=(\d+) mismatches=(\d+)')):
        found=re.search(pattern,text)
        if found:record[name]=dict(zip(('width','height','row_pitch','mismatches'),map(int,found.groups())))
    record.update(process_exit=process.returncode,job=json.loads((folder/'job-result.json').read_text()),result='PARTIAL')
    if record.get('source',{}).get('mismatches')==0 and 'native' in record:
        if record['native']['mismatches']:record['result']='GPU_SHARED_LAYOUT_CORRUPTION_REPRODUCED'
        elif process.returncode==0:record['result']='GPU_SHARED_LAYOUT_MATCH_ONLY'
        else:record['result']='GPU_SHARED_PIXELS_MATCH_TEARDOWN_PARTIAL'
    (folder/'analysis.json').write_text(json.dumps(record,indent=2))
    print(folder);print(json.dumps(record,indent=2))
    return record


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--extent',nargs=2,type=int,required=True)
    run(*parser.parse_args().extent)

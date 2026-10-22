"""Native reference-consumer environment admission;never changes desktop state."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import subprocess as sp

ROOT=Path(__file__).resolve().parents[2]
EXE=ROOT/'artifacts/d3d9-proof/bin/d3d9_startup_probe.exe'


def classify(text):
    """Evidence classification,not an assertion that the desktop caused failure."""
    def one(pattern):
        rows=re.findall(pattern,text,re.MULTILINE)
        if len(rows)!=1:raise ValueError('Incomplete/ambiguous native startup diagnostic:'+pattern)
        return rows[0].strip()
    thread=one(r'^THREAD_DESKTOP=(.+)$');active=one(r'^INPUT_DESKTOP=(.+)$')
    count=int(one(r'^ADAPTER_COUNT (\d+)$'))
    # The terminal record is parsed independently;adapter labels are observations,
    # not a reason to select another adapter or ignore its failed capability query.
    ends=re.findall(r'^PROBE_DONE successes=(\d+) api_refs=(\d+)\s*$',text,re.MULTILINE)
    if len(ends)!=1:raise ValueError('Missing/ambiguous native completion')
    successes,refs=map(int,ends[0])
    adapters=re.findall(r'^ADAPTER (\d+) .+$',text,re.MULTILINE)
    combinations=re.findall(r'^COMBINATION adapter=(\d+) backbuffer=(\d+) type=(0x[0-9a-f]+) depth=(0x[0-9a-f]+) create=(0x[0-9a-f]+)',text,re.MULTILINE)
    if not 1<=count<=16 or adapters!=list(map(str,range(count))) or len(combinations)!=count*3 or refs:
        raise ValueError('Invalid native diagnostic coverage/lifetime')
    observed={(int(a),int(f)) for a,f,*_ in combinations}
    if observed!={(a,f) for a in range(count) for f in (0,21,22)}:raise ValueError('Native combination coverage')
    if successes!=sum(int(row[4],16)==0 for row in combinations):raise ValueError('Native creation count mismatch')
    supported=[int(a) for a,_,kind,depth,created in combinations if all(int(x,16)==0 for x in (kind,depth,created))]
    if thread!=active:status='BLOCKED_INACTIVE_INPUT_DESKTOP'
    elif not supported or not successes:status='BLOCKED_NATIVE_DEVICE_UNAVAILABLE'
    else:status='NATIVE_STARTUP_AVAILABLE_REFERENCE_TESTS_STILL_REQUIRED'
    return dict(status=status,thread_desktop=thread,input_desktop=active,adapter_count=count,
        successful_creations=successes,supported_adapters=sorted(set(supported)),api_refs=refs,
        cause='UNRESOLVED until paired awake-desktop comparison' if thread!=active else 'Not inferred from startup alone')


def probe(folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    with (folder/'startup.log').open('wb') as output:
        result=sp.run([str(EXE)],stdout=output,stderr=sp.STDOUT,timeout=20,
            creationflags=sp.CREATE_NO_WINDOW)
    path=folder/'startup.log'
    if path.stat().st_size>1024*1024:raise ValueError('Startup diagnostic log cap')
    if result.returncode:raise ValueError('Startup diagnostic incomplete;exit='+str(result.returncode))
    report=classify(path.read_text())
    report.update(exe_sha256=hashlib.sha256(EXE.read_bytes()).hexdigest(),
        source_sha256=hashlib.sha256((ROOT/'tools/d3d9_proof/d3d9_startup_probe.cpp').read_bytes()).hexdigest(),
        log_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),sfc_launched=False,desktop_changed=False)
    (folder/'startup-result.json').write_text(json.dumps(report,indent=2))
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    if not args.execute:print('Explicit --execute required;no desktop changes');raise SystemExit(0)
    folder=ROOT/'artifacts/d3d9-proof/startup'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
    print('Evidence:',folder);print(json.dumps(probe(folder),indent=2))

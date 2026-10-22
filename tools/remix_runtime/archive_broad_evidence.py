"""Archive selected completed runs; exclude binaries; verify CRC; never delete raw."""
from pathlib import Path
import argparse
import json
import re
import zipfile
from broad_capture import ROOT,OVERALL,digest,storage_bytes

def archive(output,runs):
    output=output.resolve();base=(ROOT/'artifacts/remix-runtime/archives').resolve()
    if output.parent!=base or output.suffix!='.zip':raise ValueError('Archive must be directly inside project archives')
    files=[]
    for run in runs:
        run=run.resolve()
        if run.parent!=(ROOT/'artifacts/remix-runtime/runs').resolve():raise ValueError('Select exact generated run directories, not a workspace root')
        files.extend((p,run.name+'/'+p.relative_to(run).as_posix()) for p in run.rglob('*') if p.is_file() and (p.suffix in ('.json','.log','.ini') or p.name=='broad.bin' or re.fullmatch(r'depth-[012](?:\.bin|-(?:color|sample0|min|max|mean)\.png)|semantic-[012]\.bin|LIVE-SCENE-001-asset-[1-8]\.bin',p.name)))
    if not files:raise ValueError('No selected evidence')
    total=sum(p.stat().st_size for p,_ in files)
    if total*2+16*1024*1024>OVERALL:raise ValueError('Source plus archive allowance would exceed20GB')
    if storage_bytes()+total+16*1024*1024>OVERALL:raise ValueError('Existing runtime output plus archive allowance would exceed20GB')
    base.mkdir(exist_ok=True)
    with zipfile.ZipFile(output,'x',zipfile.ZIP_DEFLATED,compresslevel=1,allowZip64=True) as z:
        for p,name in files:z.write(p,name)
    with zipfile.ZipFile(output) as z:
        if z.testzip() is not None:raise ValueError('Archive CRC validation failed; retain raw')
        if len(z.namelist())!=len(files):raise ValueError('Archive entry count mismatch')
    result={'archive':str(output.relative_to(ROOT)),'bytes':output.stat().st_size,'sha256':digest(output),'source_bytes':total,'entries':len(files),'crc_verified':True,'raw_removed':False}
    output.with_suffix('.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('runs',nargs='+',type=Path);a=p.parse_args();archive(a.output,a.runs)

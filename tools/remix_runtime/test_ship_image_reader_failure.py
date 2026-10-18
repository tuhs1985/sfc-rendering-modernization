"""Bounded offline fault injection: kill only the reader this fixture creates."""
import json
from pathlib import Path
import subprocess
import sys
from unittest import mock
import qualify_live_return as fixture

def main():
    original=subprocess.Popen;selected=[]
    def spawn(args,**kwargs):
        process=original(args,**kwargs)
        if Path(args[0]).name=='ship_image_reader.exe':
            selected.append(Path(kwargs['cwd']));process.terminate();process.wait(timeout=5)
        return process
    with mock.patch.object(sys,'argv',['qualify_live_return.py','--execute','--addon','--textured','--capture-image']):
        with mock.patch.object(fixture.sp,'Popen',side_effect=spawn):
            try:fixture.main()
            except RuntimeError as exc:
                if 'Prepared image reader failed' not in str(exc):raise
            else:raise AssertionError('Missing reader was not reported as PARTIAL')
    if len(selected)!=1:raise AssertionError('Expected exactly one owned reader')
    folder=selected[0];log=(folder/'fixture.log').read_text();host=(folder/'host.log').read_text()
    if 'PRIVATE_GPU_FIXTURE_PASS' not in log or 'failed=0' not in log or 'LIVE_SHUTDOWN api=0' not in host:raise AssertionError('Reader failure affected native render path')
    result={'result':'OWNED_READER_FAILURE_ISOLATED','sfc_launched':False,'requested_image_result':'PARTIAL',
            'native_fixture_passed':True,'host_clean_shutdown_api':0,'killed_only_owned_reader':True}
    (folder/'reader-fault-review.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))

if __name__=='__main__':main()

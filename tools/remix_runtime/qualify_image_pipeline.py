"""Repeat current source-matched return gates after image-control changes. No SFC."""
import json
from pathlib import Path
import subprocess as sp
import sys
from live_return import ROOT,qualify

def main():
    # Each child has existing60s/32MiB fixture limits; no uncontrolled captures.
    matrix=[[],['--addon'],['--slow'],['--disconnect'],['--addon','--visible'],
            ['--addon','--textured','--capture-image'],['--addon','--textured','--slow'],
            ['--addon','--textured','--disconnect'],['--light-wiring'],['--light-types'],
            ['--project-fill'],['--material-controls'],['--image-controls'],['--quality-controls']]
    root=Path(__file__).parent;folders=[]
    for flags in matrix:
        before=set((ROOT/'artifacts/remix-runtime/runs').glob('*-live-private'))
        print('OFFLINE RETURN GATE '+repr(flags),flush=True)
        sp.run([sys.executable,str(root/'qualify_live_return.py'),'--execute',*flags],check=True,timeout=85)
        added=set((ROOT/'artifacts/remix-runtime/runs').glob('*-live-private'))-before
        if len(added)!=1:raise RuntimeError('Expected one exact fixture result')
        folders.append(added.pop())
    before=set((ROOT/'artifacts/remix-runtime/runs').glob('*-image-controls'))
    sp.run([sys.executable,str(root/'run_image_probe.py'),'--execute'],check=True,timeout=85)
    added=set((ROOT/'artifacts/remix-runtime/runs').glob('*-image-controls'))-before
    if len(added)!=1:raise RuntimeError('Expected one exact image probe result')
    image=added.pop();before=set((ROOT/'artifacts/remix-runtime/runs').glob('*-image-controls'))
    sp.run([sys.executable,str(root/'run_image_probe.py'),'--execute','--quality'],check=True,timeout=85)
    added=set((ROOT/'artifacts/remix-runtime/runs').glob('*-image-controls'))-before
    if len(added)!=1:raise RuntimeError('Expected one quality probe')
    print(json.dumps(qualify(folders,image,added.pop()),indent=2))

if __name__=='__main__':main()

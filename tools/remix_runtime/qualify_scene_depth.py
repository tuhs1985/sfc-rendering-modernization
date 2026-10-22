"""Three bounded owned-process scene-depth fixtures; NEVER starts SFC."""
import argparse
import subprocess as sp
import sys
from live_return import ROOT
from scene_depth import qualify

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    if not args.execute:print('Offline scene-depth qualification only;--execute starts owned fixtures,not SFC.');return
    pwsh=r'C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'
    tool=ROOT/'tools/remix_runtime';folders=[]
    for flags in ([],['--slow'],['--disconnect']):
        before=set((ROOT/'artifacts/remix-runtime/runs').glob('*-live-private'))
        sp.run([sys.executable,str(tool/'qualify_live_return.py'),'--execute','--scene-depth',*flags],check=True,timeout=85)
        added=set((ROOT/'artifacts/remix-runtime/runs').glob('*-live-private'))-before
        if len(added)!=1:raise ValueError('One exact scene-depth fixture required')
        folder=added.pop();folders.append(str(folder.relative_to(ROOT)))
        for script in ('archive_fixture_textures.ps1','archive_fixture_binaries.ps1'):
            sp.run([pwsh,'-NoProfile','-File',str(tool/script),'-RunDirectory',str(folder)],check=True,timeout=60)
    print(qualify(folders)['result'])

if __name__=='__main__':main()

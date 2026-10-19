"""Source-matched return requalification with recoverable per-fixture compaction."""
import json
from pathlib import Path
import subprocess as sp
import sys
from live_return import ROOT,qualify

def main():
    root=Path(__file__).parent
    # Reuse unchanged independent image/quality proofs; their checked source and
    # executable hashes must still match. Do not rewrite old proof manifests.
    previous=json.loads((ROOT/'artifacts/remix-runtime/deps/live-return-qualification.json').read_text())
    image=quality=None
    for relative in previous['evidence']:
        folder=ROOT/relative
        if not folder.name.endswith('-image-controls'):continue
        result=json.loads((folder/'result.json').read_text())
        if result.get('result')=='OFFLINE_IMAGE_CONTROLS_PASS':image=folder
        if result.get('result')=='OFFLINE_QUALITY_OPTIONS_EXERCISED':quality=folder
    if not image or not quality:raise ValueError('Existing independent pixel proofs required')
    pwsh=Path(r'C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe')
    matrix=[[],['--addon'],['--slow'],['--disconnect'],['--addon','--visible'],
        ['--addon','--textured','--capture-image'],['--addon','--textured','--slow'],
        ['--addon','--textured','--disconnect'],['--light-wiring'],['--light-types'],
        ['--project-fill'],['--material-controls'],['--image-controls'],['--quality-controls']]
    folders=[]
    for flags in matrix:
        before=set((ROOT/'artifacts/remix-runtime/runs').glob('*-live-private'))
        print('OFFLINE RETURN GATE '+repr(flags),flush=True)
        sp.run([sys.executable,str(root/'qualify_live_return.py'),'--execute',*flags],check=True,timeout=85)
        added=set((ROOT/'artifacts/remix-runtime/runs').glob('*-live-private'))-before
        if len(added)!=1:raise RuntimeError('Exact single fixture expected')
        folder=added.pop();folders.append(folder)
        sp.run([str(pwsh),'-NoProfile','-File',str(root/'archive_fixture_textures.ps1'),'-RunDirectory',str(folder)],check=True,timeout=60)
    receipt=qualify(folders,image,quality)
    print(json.dumps(dict(result=receipt['result'],gates=[str(f.relative_to(ROOT)) for f in folders],
        image_proof=str(image.relative_to(ROOT)),quality_proof=str(quality.relative_to(ROOT))),indent=2))

if __name__=='__main__':main()

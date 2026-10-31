"""Freeze the tested metadata-only probe. Does not qualify image insertion."""
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
import native_insertion_probe as probe
from additive_qualification import sources

def record():
    folder=probe.RECEIPT.parent
    files=json.loads((folder/'build.json').read_text(encoding='utf-8-sig'))
    for name,sha in files.items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest().upper()!=sha:raise ValueError('Native insertion tests stale: '+name)
    for arch in (32,64):
        text=(folder/f'probe{arch}.txt').read_text(encoding='utf-8-sig')
        if not re.search(r'Insertion observer PASS 295 checks',text):raise ValueError('Observer tests incomplete')
    component=ROOT/'artifacts/player-replacement/native-tests/component.txt'
    if 'Player suppression recorder PASS checks=13' not in component.read_text(encoding='utf-8-sig'):raise ValueError('Actual suppression-veto recorder test missing')
    # Freeze all interface sources, and the binaries this launcher really uses.
    # This is intentionally a new observation gate, not renewed shield/replacement qualification.
    files.update(sources())
    paths=['tools/native_insertion/record_qualification.py','artifacts/player-replacement/native-tests/component.exe',
           'artifacts/player-replacement/native-tests/component.txt','artifacts/player-replacement/native-insertion-tests/python-tests.txt',
           'artifacts/remix-runtime/return-bin/SFCRemixReturn.dll',
           'artifacts/remix-runtime/native-light-tests/m1_light_component.dll']
    for name in paths:files[name]=hashlib.sha256((ROOT/name).read_bytes()).hexdigest().upper()
    q=dict(result='METADATA_ONLY_PROBE_TESTED',files=files,
           scope='Native observer and actual suppression veto tested;backend binaries verified separately. Not an SFC draw-order or replacement claim.',
           sfc_launched=False,pixels_changed=False,geometry_hook=False)
    probe.RECEIPT.write_text(json.dumps(q,indent=2));probe.require_qualification()
    print('Metadata-only native insertion qualification PASS')
if __name__=='__main__':record()

"""Build-machine notice inventory from identified upstream distributions.

Does not approve redistribution, create a ZIP, or fetch anything at user launch.
Keep full vendor terms alongside the eventual application; MIT covers only our
own code. Missing license closure remains explicit in the receipt.
"""
import hashlib
import json
from pathlib import Path
import shutil
import urllib.request

ROOT=Path(__file__).resolve().parents[2]


def prepare():
    output=ROOT/'artifacts/alpha/notices';output.mkdir(parents=True,exist_ok=True)
    sources={
        'Remix-LICENSE.txt':'artifacts/remix-runtime/deps/candidate-1.6.1/runtime/LICENSE.txt',
        'Remix-ThirdPartyLicenses.txt':'artifacts/remix-runtime/deps/candidate-1.6.1/runtime/ThirdPartyLicenses-dxvk.txt',
        'CPython-LICENSE.txt':'artifacts/alpha/python-3.12.14/LICENSE.txt',
        'NumPy-LICENSE.txt':'artifacts/alpha/python-3.12.14/Lib/site-packages/numpy-2.3.5.dist-info/LICENSE.txt',
        'Pillow-LICENSE.txt':'artifacts/alpha/python-3.12.14/Lib/site-packages/pillow-12.3.0.dist-info/licenses/LICENSE',
        'Detours-LICENSE.txt':'artifacts/remix-runtime/deps/detours/Detours-e4bfd6b03e50de46b47abfbd1e46b384f0c5f833/LICENSE.md',
    }
    records=[]
    for name,relative in sources.items():
        raw=(ROOT/relative).read_bytes();(output/name).write_bytes(raw)
        records.append(dict(file=name,source=relative,sha256=hashlib.sha256(raw).hexdigest()))
    source=ROOT/'artifacts/remix-runtime/deps/xxhash.h'
    raw=source.read_bytes().split(b'*/',1)[0]+b'*/\n'
    (output/'xxHash-LICENSE.txt').write_bytes(raw)
    records.append(dict(file='xxHash-LICENSE.txt',source=source.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(raw).hexdigest()))
    url='https://raw.githubusercontent.com/crosire/reshade/8cf85bd12d56697d756d4fcb45e501f5d1b540fa/LICENSE.md'
    target=output/'ReShade-LICENSE.txt'
    if not target.exists():
        with urllib.request.urlopen(url,timeout=30) as stream:raw=stream.read(65537)
        if not 100<len(raw)<=65536 or b'Copyright 2014 Patrick Mours' not in raw:raise ValueError('Unexpected pinned ReShade notice')
        target.write_bytes(raw)
    records.append(dict(file=target.name,source=url,sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
    record=dict(schema='sfc.alpha.vendor-notices.v1',ready_for_distribution=False,files=records,
                remaining=['Finish exact bundled file allowlist and Microsoft distributable-code terms',
                           'Preserve dgVoodoo2.86.5 mirror/archive provenance and current official redistribution terms',
                           'Include vendor terms separately from project MIT in exact reviewed candidate'])
    (output/'inventory.json').write_text(json.dumps(record,indent=2))
    print(json.dumps(dict(directory=str(output),notices=len(records),ready_for_distribution=False)))
    return output


if __name__=='__main__':prepare()

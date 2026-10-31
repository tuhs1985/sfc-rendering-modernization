"""Version1 actual-rendered membership and per-owner native insertion receipts."""
import hashlib,json,struct
from pathlib import Path
from player_replacement import ROOT,OFFSET as BASE
OFFSET=BASE+58880
SIZE=6464
MAGIC=0x31434e53
RECEIPT=ROOT/'artifacts/player-replacement/native-cohort-tests/qualification.json'

def decode(raw):
    if len(raw)!=SIZE:raise ValueError('Native cohort layout')
    h=struct.unpack_from('<16I',raw)
    if h[:3]!=(MAGIC,1,SIZE) or not h[3]:raise ValueError('Native cohort identity')
    owners=[]
    for i in range(32):
        v=struct.unpack_from('<8I',raw,5440+i*32)
        if v[0]:owners.append(dict(zip(('owner','revision','model','source','inserted','suppressed','unavailable','last_frame'),v)))
    return dict(pid=h[3],session=list(h[4:8]),inserted=h[8],suppressed=h[9],unavailable=h[10],omitted=h[11],owners=owners)

def save(channel,folder):
    raw=channel.read(OFFSET,SIZE);value=decode(raw);folder=Path(folder)
    (folder/'NATIVE-COHORT-001.bin').write_bytes(raw);(folder/'NATIVE-COHORT-001.json').write_text(json.dumps(value,indent=2));return value

def require_qualification(policy):
    q=json.loads(RECEIPT.read_text())
    if q['result']!='NATIVE_COHORT_PREPARED' or policy not in q['policies']:raise ValueError('Native cohort not qualified')
    for name,sha in q['files'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest().upper()!=sha:raise ValueError('Native cohort inputs changed: '+name)
    from async_material_checkout import backend_inputs,receipt
    return dict(q,backend_inputs=receipt(backend_inputs()))

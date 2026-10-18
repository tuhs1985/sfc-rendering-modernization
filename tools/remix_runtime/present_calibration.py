"""Strict contemporaneous capture provenance. Never guesses by nearest timestamp."""
from pathlib import Path
import hashlib
import json
import struct
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/remix_ingest'))
from live_scene import SceneChannel,decode_mesh

STAMP=struct.Struct('<16Q')
HEADER=struct.Struct('<12I')
ROWS=32
SIZE=STAMP.size+HEADER.size+ROWS*384

def require_qualification():
    from prepare_full_reshade import source_hashes
    from depth_snapshot_analysis import digest
    p=ROOT/'artifacts/remix-runtime/deps/present-calibration-qualification.json'
    q=json.loads(p.read_text())
    if q.get('result')!='OFFLINE_CALIBRATION_SIDECAR_PASS' or q.get('source_hashes')!=source_hashes():raise ValueError('Calibration offline source qualification required')
    for key,path in [('addon_sha256','artifacts/remix-runtime/return-bin/SFCRemixReturn.dll'),('component_sha256','artifacts/m1/bin/m1_component.dll')]:
        if q.get(key)!=digest(ROOT/path):raise ValueError('Calibration binary changed; requalify before gameplay')
    return q


class Receiver:
    def __init__(self):
        self.channel=SceneChannel(create=True)
        self.revisions={}

    @property
    def name(self):return self.channel.name

    def drain(self):
        for slot in range(4):
            transfer=self.channel.asset_transfer(slot)
            if transfer is None:continue
            generation,revision,owner,mesh,refs=transfer
            if not 1<=revision<=8:raise ValueError('Calibration eight-revision cap')
            data=decode_mesh(mesh,refs)
            if data['header'][4]!=owner:raise ValueError('Asset transfer owner mismatch')
            identity=hashlib.sha256(mesh+refs).hexdigest()
            if revision in self.revisions and self.revisions[revision]!=identity:raise ValueError('Reused asset revision')
            self.revisions[revision]=identity
            self.channel.acknowledge(slot,generation)

    def close(self):self.channel.close()


def read_semantic(path,depth,session,pid=None):
    path=Path(path)
    if path.stat().st_size!=SIZE:raise ValueError('Calibration packet size')
    raw=path.read_bytes();s=STAMP.unpack_from(raw);h=HEADER.unpack_from(raw,STAMP.size)
    if s[:3]!=(0x31504353,1,SIZE) or any(s[10:]):raise ValueError('Calibration version/reserved')
    if (s[3],s[4],s[5])!=(depth['qpc'],depth['present_frame'],depth['resource_epoch']):raise ValueError('Not the paired GPU submission')
    if not s[6] or s[6]!=s[7] or s[6]==0xffffffff or not s[8] or not s[9]:raise ValueError('Not one semantic/draw frame')
    if pid is not None and s[8]!=pid:raise ValueError('Wrong process')
    expected=tuple(int(session[-32:][i:i+8],16) for i in range(0,32,8))
    if h[:4]!=(0x314c4143,1,SIZE-128,s[6]) or h[4:8]!=expected or any(h[9:]):raise ValueError('Wrong semantic session/frame')
    rows=[struct.unpack_from('<96I',raw,176+i*384) for i in range(ROWS)]
    active=[];seen=set()
    for i,r in enumerate(rows):
        if not r[1]:
            if any(r):raise ValueError('Nonempty unused owner slot')
            continue
        if r[1] in seen or r[2]!=s[6] or r[45]!=i:raise ValueError('Stale/cross-associated owner')
        seen.add(r[1])
        if r[4] not in (1,3) or r[47]!=s[9]:raise ValueError('Unsupported status/thread')
        if r[4]==1 and r[7] and r[48]==1:
            values=struct.unpack('<96f',struct.pack('<96I',*r))
            import math
            if not all(math.isfinite(values[j]) for j in list(range(8,24))+list(range(25,41))+list(range(49,65))+list(range(66,82))+list(range(83,89))):raise ValueError('Nonfinite camera/pose')
            active.append(r)
    if h[8]!=len(seen) or not active:raise ValueError('No unambiguous current owner')
    return dict(file=path.name,sha256=hashlib.sha256(raw).hexdigest(),engine_frame=s[6],thread=s[9],owners=active,
                ambiguous_owners=[r[1] for r in rows if r[1] and r[4]==3])


def analyze(folder,session,pid):
    from depth_snapshot_analysis import read_packet
    folder=Path(folder);packets=sorted(folder.glob('semantic-*.bin'))
    if len(packets)!=3:raise ValueError('Three contemporaneous records required')
    out=[];previous=0
    for i in range(3):
        depth,_,_=read_packet(folder/f'depth-{i}.bin')
        row=read_semantic(folder/f'semantic-{i}.bin',depth,session,pid)
        if row['engine_frame']<=previous:raise ValueError('Repeated/nonmonotonic engine frame')
        previous=row['engine_frame'];associations=[]
        for r in row.pop('owners'):
            base=folder/'gate'/f'LIVE-SCENE-001-asset-{r[7]}'
            mesh=base.with_suffix('.bin').read_bytes();refs=base.with_suffix('.json').read_bytes()
            data=decode_mesh(mesh,refs);h=data['header']
            if (h[4],h[10],h[12])!=(r[1],r[5],r[6]) or h[6]>r[2]:raise ValueError('Unqualified owner/model/source/revision association')
            associations.append(dict(owner=r[1],revision=r[7],model=r[5],source=r[6],asset_frame=h[6],
                packet_sha256=data['packet_sha256'],references_sha256=hashlib.sha256(refs).hexdigest(),record=list(r)))
        row['associations']=associations;out.append(row)
    result=dict(probe='REMIX-CALIBRATION-001',contemporaneous_records_complete=True,snapshots=out,
        interpretation='Submission provenance only. Ship-mask/depth comparison, occlusion and replacement remain unproven.')
    (folder/'semantic.analysis.json').write_text(json.dumps(result,indent=2))
    return result

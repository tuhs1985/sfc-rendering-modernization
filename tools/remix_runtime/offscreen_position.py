"""Default-off external read-only pose experiment;never supplies renderer state.

Readable memory/address continuity is NOT an allocation-lifetime guarantee.
No game getters,threads,suspension,writes or persistent-object claims.
"""
import ctypes as C
from ctypes import wintypes as W
import hashlib
import json
import math
from pathlib import Path
import struct
import threading
import time

ROOT=Path(__file__).resolve().parents[2]
VTABLES=(0x00796F0C,0x007985A4,0x007983E8)
RANGES=((0xE6,12),(0x34,12),(0x90,6),(0x92A,6),(0x980,68),(0x98,68),(0x9C4,68),(0xDC,4))
MAX_RECORDS=2700 # per distinct captured native ship;two ships maximum
MAX_BYTES=8*1024*1024
PHASES=((15,1,'Accelerate your ship and keep it moving;keep both ships alive.'),
        (25,2,'Switch to the enemy camera so your moving ship leaves view;do not stop your ship.'),
        (40,3,'Return to your own ship;keep moving.'),
        (50,1,'Gently turn your moving ship;prepare to look away again.'),
        (60,2,'Switch to the enemy camera again;leave your own ship moving.'),
        (75,3,'Return to your own ship again.'),
        (80,1,'Hold this view;wait for the two LOW exit beeps.'))


def decode_fields(raw):
    if len(raw)!=sum(size for _,size in RANGES):raise ValueError('Pose field byte count')
    offset=0;parts=[]
    for _,size in RANGES:parts.append(raw[offset:offset+size]);offset+=size
    pos=struct.unpack('<3f',parts[0]);base=struct.unpack('<3f',parts[1])
    matrices=[struct.unpack('<16fI',p) for p in parts[4:7]]
    if not all(math.isfinite(v) for v in (*pos,*base,*(v for m in matrices for v in m[:16]))):
        raise ValueError('Nonfinite pose')
    return dict(position=list(pos),base_position=list(base),base_angles=list(struct.unpack('<3H',parts[2])),
        ship_angles_raw=list(struct.unpack('<3H',parts[3])),rotation_words=list(struct.unpack('<17I',parts[4])),
        base_matrix_words=list(struct.unpack('<17I',parts[5])),cache_words=list(struct.unpack('<17I',parts[6])),
        cache_translation=[matrices[2][i] for i in (3,7,11)],base_cache_stamp=struct.unpack('<I',parts[7])[0])


def sample(read,seed):
    """Double-read only known fields;reject races/read failures without target writes."""
    ship,visual,model=seed['ship'],seed['visual'],seed['model']
    def identity():return (struct.unpack('<I',read(ship,4))[0],struct.unpack('<I',read(ship+0x88,4))[0],
        struct.unpack('<I',read(visual,4))[0],struct.unpack('<I',read(model,4))[0])
    expected=(VTABLES[0],visual,VTABLES[1],VTABLES[2])
    try:
        if identity()!=expected:return dict(status='identity_mismatch')
        a=b''.join(read(ship+off,size) for off,size in RANGES)
        tick0=struct.unpack('<I',read(0x00C7C140,4))[0]
        b=b''.join(read(ship+off,size) for off,size in RANGES)
        tick1=struct.unpack('<I',read(0x00C7C140,4))[0]
        if identity()!=expected:return dict(status='identity_mismatch')
        if a!=b:return dict(status='changing_during_read')
        return dict(status='stable_read',native_tick_before=tick0,native_tick_after=tick1,**decode_fields(a))
    except (OSError,ValueError,struct.error):return dict(status='unreadable_or_nonfinite')


class ProcessReader:
    def __init__(self,pid,expected_image):
        self.k=C.WinDLL('kernel32',use_last_error=True)
        self.k.OpenProcess.argtypes=[W.DWORD,W.BOOL,W.DWORD];self.k.OpenProcess.restype=W.HANDLE
        self.k.CloseHandle.argtypes=[W.HANDLE]
        self.k.ReadProcessMemory.argtypes=[W.HANDLE,C.c_void_p,C.c_void_p,C.c_size_t,C.POINTER(C.c_size_t)]
        self.k.QueryFullProcessImageNameW.argtypes=[W.HANDLE,W.DWORD,W.LPWSTR,C.POINTER(W.DWORD)]
        self.handle=self.k.OpenProcess(0x1010,False,pid) # QUERY_LIMITED_INFORMATION|VM_READ ONLY
        if not self.handle:raise C.WinError(C.get_last_error())
        try:
            path=C.create_unicode_buffer(32768);size=W.DWORD(len(path))
            if not self.k.QueryFullProcessImageNameW(self.handle,0,path,C.byref(size)):raise C.WinError(C.get_last_error())
            if Path(path.value).resolve()!=Path(expected_image).resolve():raise ValueError('Offscreen reader process path mismatch')
        except Exception:self.close();raise
    def read(self,address,size):
        if not 0<address<0x80000000 or not 0<size<=68:raise ValueError('Bounded x86 source read')
        buf=C.create_string_buffer(size);done=C.c_size_t()
        if not self.k.ReadProcessMemory(self.handle,address,buf,size,C.byref(done)) or done.value!=size:
            raise OSError('Read-only process memory unavailable')
        return buf.raw
    def close(self):
        if self.handle:self.k.CloseHandle(self.handle);self.handle=None


def verify_client(path):
    import sys
    sys.path.insert(0,str(ROOT/'tools/m1_component'))
    import verify_m1_c01_shading_bytes as check
    anchors={0x00419DDC:'8D AB C4 09 00 00',0x00419DE2:'E8 4D 9D FF FF',
        0x00419DEB:'66 8B 83 2E 09 00 00',0x00419DFF:'66 8B 83 2A 09 00 00',
        0x00419E0E:'8D 83 80 09 00 00',0x00419E1C:'D9 83 EE 00 00 00',
        0x00419E26:'D9 83 EA 00 00 00',0x00419E30:'D9 83 E6 00 00 00',
        0x00419E3C:'E8 FF 2A 28 00',0x00413B61:'D9 46 3C',0x00413B68:'D9 46 38',
        0x00413B6F:'D9 46 34'}
    # Reuse exact-PE verifier without altering its durable baseline anchor list.
    original=check.ANCHORS
    try:check.ANCHORS=anchors;return check.verify(Path(path))
    finally:check.ANCHORS=original


class Capture:
    def __init__(self,folder,pid,expected_image):
        self.folder=Path(folder);self.pid=pid;self.reader=ProcessReader(pid,expected_image)
        self.stop_event=threading.Event();self.error=None;self.tracks={};self.files=set();self.bytes=0;self.saturated=False
        self.frequency=C.c_longlong();C.windll.kernel32.QueryPerformanceFrequency(C.byref(self.frequency))
        self.thread=threading.Thread(target=self.run,name='SFC-offscreen-read',daemon=False);self.thread.start()
    def discover(self):
        for path in sorted((self.folder/'gate').glob('LIVE-SCENE-001-asset-*.bin')):
            if path.name in self.files:continue
            if len(self.files)>=8:raise ValueError('Offscreen asset revision bound8')
            if not 256<=path.stat().st_size<=2*1024*1024:continue # writer may not have closed yet
            with path.open('rb') as f:h=struct.unpack('<64I',f.read(256))
            if h[:2]!=(0x314D4653,1) or h[2]!=path.stat().st_size:continue # incomplete file;retry later
            refs=path.with_suffix('.json')
            if not refs.is_file():continue
            if refs.stat().st_size>128*1024:raise ValueError('Offscreen reference128KiB cap')
            try:
                import sys
                sys.path.insert(0,str(ROOT/'tools/remix_ingest'))
                from live_scene import decode_mesh
                decoded=decode_mesh(path.read_bytes(),refs.read_bytes());meta=decoded['refs']
            except (ValueError,OSError):continue # not published as a seed until fully validated
            self.files.add(path.name)
            if h[8] in self.tracks:
                track=self.tracks[h[8]]
                if (track['visual'],track['model'])!=(h[9],h[10]):
                    track['quarantined']=True;track['reason']='fresh_capture_identity_changed'
                track['observed_epochs'].append([h[4],h[6],h[7],h[10],h[12]])
                continue
            if len(self.tracks)==2:continue
            if not all(0<value<0x80000000 for value in (h[8],h[9],h[10])):raise ValueError('Offscreen captured address bounds')
            self.tracks[h[8]]=dict(ship=h[8],visual=h[9],model=h[10],source=h[12],
                model_name=meta['model_filename'],initial_observer_epoch=h[4],observed_epochs=[[h[4],h[6],h[7],h[10],h[12]]],
                records=0,quarantined=False,source_packet=path.name)
    def run(self):
        started=time.monotonic();discovered=0
        try:
            with (self.folder/'OFFSCREEN-POSITION-001.jsonl').open('w',encoding='utf-8') as out:
                while not self.stop_event.is_set() and time.monotonic()-started<120:
                    if time.monotonic()-discovered>=.25:self.discover();discovered=time.monotonic()
                    for seed in self.tracks.values():
                        if seed['quarantined'] or seed['records']>=MAX_RECORDS:continue
                        before=C.c_longlong();after=C.c_longlong();C.windll.kernel32.QueryPerformanceCounter(C.byref(before))
                        row=sample(self.reader.read,seed);C.windll.kernel32.QueryPerformanceCounter(C.byref(after))
                        row.update(ship=seed['ship'],initial_observer_epoch=seed['initial_observer_epoch'],pid=self.pid,
                            qpc_before=before.value,qpc_after=after.value,frequency=self.frequency.value)
                        text=json.dumps(row,separators=(',',':'))+'\n'
                        if self.bytes+len(text.encode())>MAX_BYTES:self.saturated=True;return
                        out.write(text);self.bytes+=len(text.encode());seed['records']+=1
                        if row['status'] in ('identity_mismatch','unreadable_or_nonfinite'):seed['quarantined']=True
                    if self.stop_event.wait(.05):break # <=20Hz,no catch-up bursts
        except Exception as exc:self.error=str(exc)
    def close(self):
        self.stop_event.set();self.thread.join(3)
        if self.thread.is_alive():raise RuntimeError('Offscreen reader did not join;handle not released')
        self.reader.close()
        result=dict(probe='OFFSCREEN-POSITION-001',pid=self.pid,tracks=list(self.tracks.values()),bytes=self.bytes,
            saturated=self.saturated,error=self.error,joined=True,process_handle_closed=True,
            lifetime_proven=False,renderer_state_modified=False)
        (self.folder/'offscreen-position-worker.json').write_text(json.dumps(result,indent=2))
        if self.error:raise RuntimeError(self.error)
        return result


def analyze(folder):
    """Conservative source-QPC join. Missing coverage never becomes success."""
    from source_timing import HEADER,RECORD,decode
    folder=Path(folder);worker=json.loads((folder/'offscreen-position-worker.json').read_text())
    path=folder/'OFFSCREEN-POSITION-001.jsonl'
    if path.stat().st_size>MAX_BYTES:raise ValueError('Offscreen log bound')
    rows=[json.loads(line) for line in path.read_text().splitlines()]
    if len(rows)>MAX_RECORDS*2:raise ValueError('Offscreen record bound')
    for r in rows:
        if r['pid']!=worker['pid'] or not 0<r['qpc_before']<=r['qpc_after'] or r['frequency']<=0:
            raise ValueError('Offscreen record provenance')
        if r['status']=='stable_read' and not all(math.isfinite(v) for v in r['position']):raise ValueError('Nonfinite recorded position')
    source=(folder/'D3D9-SOURCE-TIMING-001.bin').read_bytes()
    manifest=json.loads((folder/'manifest.json').read_text())
    timing=decode(source,manifest['semantic_calibration']['scene_session'],worker['pid'])
    head=HEADER.unpack_from(source)
    if any(r['frequency']!=head[12] for r in rows):raise ValueError('Offscreen/source QPC frequency mismatch')
    if (len(source)-HEADER.size)%RECORD.size:raise ValueError('Incomplete source timing')
    src=[r for r in RECORD.iter_unpack(source[HEADER.size:]) if r[0]==1]
    if head[4]!=worker['pid']:raise ValueError('Offscreen/source PID mismatch')
    events=[json.loads(l) for l in (folder/'gate/LIFECYCLE-001-events.jsonl').read_text().splitlines()]
    results=[]
    for track in worker['tracks']:
        samples=[r for r in rows if r['ship']==track['ship'] and r['status']=='stable_read']
        labels={e[0] for e in track['observed_epochs']};gaps=[]
        for event in events:
            if event[4]!=2 or event[1] not in labels:continue
            # Require actual fresh reappearance at same captured native ship.
            later=[e for e in track['observed_epochs'] if e[1]>event[2]]
            if not later:continue
            new=min(later,key=lambda e:e[1]);start=[r for r in src if event[2]<=r[1]<new[1]]
            ends=[r for r in src if r[3]==new[0] and r[1]>=new[1]]
            if not start or not ends:continue
            lo=min(r[8] for r in start);hi=min(r[8] for r in ends)
            inside=[r for r in samples if lo<r['qpc_before']<=r['qpc_after']<hi]
            moving=len({tuple(r['position']) for r in inside})>1
            gaps.append(dict(old_epoch=event[1],new_epoch=new[0],retired_frame=event[2],return_frame=new[1],
                conservative_window_ms=(hi-lo)*1000/head[12],samples=len(inside),position_changed=moving,
                first_position=inside[0]['position'] if inside else None,last_position=inside[-1]['position'] if inside else None,
                cache_variants=len({tuple(r['cache_words']) for r in inside}),
                native_tick_variants=len({r['native_tick_before'] for r in inside}),
                missing_owner_render_offers=sum(r[3] in labels for r in start)))
        results.append(dict(ship=track['ship'],model=track['model_name'],samples=len(samples),quarantined=track['quarantined'],gaps=gaps))
    demonstrated=any(g['samples']>=3 and g['position_changed'] and not g['missing_owner_render_offers'] for t in results for g in t['gaps'])
    clean=not worker['error'] and not worker['saturated'] and worker['joined'] and worker['process_handle_closed'] and not any(t['quarantined'] for t in worker['tracks']) and timing['result']=='SOURCE_TIMING_OBSERVATION_COMPLETE_ADJUDICATION_REQUIRED'
    return dict(result='OFFSCREEN_POSITION_UPDATES_OBSERVED_NOT_LIFETIME_PROOF' if demonstrated and clean else 'PARTIAL',
        tracks=results,worker=worker,log_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        limitation='External double reads are not atomic simulation snapshots or allocation generation proof;not renderer input or safe persistent lifetime qualification')

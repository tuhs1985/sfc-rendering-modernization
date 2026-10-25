"""Read-only version2 light/type review. No runtime instrumentation or payload reads."""
import argparse,collections,ctypes as C,hashlib,json,re,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/render_survey'))
from survey_capture import Header,RECORD,validate
from verify_effect_resource_path import Image

def class_name(image,vtable,target):
    """Pinned PE RTTI only; observed address alone is not a guessed weapon label."""
    def u32(address):return struct.unpack('<I',image.read(address,4))[0]
    if u32(vtable+4)!=target:raise ValueError('Observed dispatch differs from pinned vtable')
    locator=u32(vtable-4)
    signature,offset,constructor,descriptor,hierarchy=struct.unpack('<5I',image.read(locator,20))
    if signature or offset or not hierarchy:raise ValueError('Unqualified RTTI locator')
    raw=image.read(descriptor+8,128).split(b'\0',1)[0].decode('ascii')
    if not re.fullmatch(r'\.\?AVtFx_[A-Za-z0-9_]+@@',raw):raise ValueError('Unexpected RTTI descriptor')
    return dict(vtable=f'0x{vtable:08X}',draw_target=f'0x{target:08X}',locator=f'0x{locator:08X}',type_descriptor=f'0x{descriptor:08X}',native_class=raw[4:-2],classification='CONFIRMED_PINNED_RTTI_NOT_PIXEL_OWNER')

def known_light_fields(words):
    # Only +04..+28 are supported float fields. Preserve unknown tail as words.
    values=struct.unpack('<10f',struct.pack('<10I',*words[1:11]))
    import math
    if not all(map(math.isfinite,values)):return None
    return dict(direction=list(values[:3]),position=list(values[3:6]),contribution=list(values[6:9]),scale_native=values[9],unknown_tail_words=list(words[11:]))

def review(folder,image):
    folder=Path(folder).resolve();folder.relative_to(ROOT/'artifacts/remix-runtime/runs')
    path=folder/'broad.bin';lights={};classes={};pending={};origins={};stats=collections.Counter();last=0;tail_origins=0
    caller_controls=collections.Counter();windows=collections.defaultdict(collections.Counter)
    def slot(manager,index):
        key=(manager,index)
        if key not in lights:
            if len(lights)>=512:raise ValueError('Eight-bank/512-slot summary limit')
            lights[key]=dict(manager=manager,slot=index,controls=0,records=0,enabled=False,ever_enabled=False,enable_transitions=0,types=set(),enabled_types=set(),raw_changes=0,position_changes=0,direction_changes=0,contribution_changes=0,last_raw=None,first_seconds=None,last_seconds=None,directional_patterns={})
        return lights[key]
    with path.open('rb') as f:
        h=Header.from_buffer_copy(f.read(128));validate(h)
        if h.version!=2 or h.fileBytes!=path.stat().st_size:raise ValueError('Expected complete version2 file layout')
        def seconds(qpc):return (qpc-h.gateQpc)/h.frequency
        while raw:=f.read(128):
            if len(raw)!=128:raise ValueError('Partial record')
            seq,qpc,event,thread,obj,dev,*a=RECORD.unpack(raw)
            if seq<=last:raise ValueError('Nonmonotonic sequence')
            last=seq;t=seconds(qpc)
            if event==36:
                stats['light_controls']+=1;stats['invalid_light_controls']+=int(not a[5]);caller_controls[f'0x{dev:08X}']+=1
                if a[4]==3:stats['global_gate_calls']+=1;continue
                if a[1]>=64 or not a[5]:continue
                row=slot(obj,a[1]);enabled=bool(a[2]);row['controls']+=1
                if row['controls']>1 and enabled!=row['enabled']:row['enable_transitions']+=1
                row['enabled']=enabled;row['ever_enabled']|=enabled
                if row['last_raw'] and enabled:row['enabled_types'].add(row['last_raw'][0])
                windows[int(t//5)][f'light_control_kind_{a[4]}']+=1
            elif event==35:
                key=(thread,obj,a[0]);offset=a[2]
                if offset not in (0,8) or a[1]>=64:raise ValueError('Malformed light fragment')
                if key not in pending:
                    if len(pending)>=4096:raise ValueError('Pending fragments capacity')
                    pending[key]={}
                parts=pending[key]
                if offset in parts:raise ValueError('Duplicate fragment')
                parts[offset]=a[3:]
                if len(parts)!=2:continue
                words=tuple(parts[0]+parts[8]);pending.pop(key)
                row=slot(obj,a[1]);old=row['last_raw'];row['records']+=1;row['types'].add(words[0])
                if row['enabled']:row['enabled_types'].add(words[0])
                if row['enabled'] and words[0]==0:
                    key=words[1:4];patterns=row['directional_patterns']
                    if key not in patterns and len(patterns)<16:patterns[key]=dict(raw_words=key,direction=list(struct.unpack('<3f',struct.pack('<3I',*key))),records=0)
                    if key in patterns:patterns[key]['records']+=1
                if old:
                    row['raw_changes']+=int(words!=old);row['position_changes']+=int(words[4:7]!=old[4:7]);row['direction_changes']+=int(words[1:4]!=old[1:4]);row['contribution_changes']+=int(words[7:11]!=old[7:11])
                row['last_raw']=words;row['first_seconds']=t if row['first_seconds'] is None else row['first_seconds'];row['last_seconds']=t
                windows[int(t//5)][f'light_native_type_{words[0]}']+=1
                stats['complete_light_records']+=1
            elif event==37:
                key=(a[2],a[3])
                if key not in classes:
                    if len(classes)>=4096:raise ValueError('Concrete type capacity')
                    classes[key]={**class_name(image,*key),'observations':0,'first_seconds':t,'last_seconds':t,'object_addresses':set()}
                row=classes[key];row['observations']+=1;row['last_seconds']=t
                if len(row['object_addresses'])>=65536:raise ValueError('Object address capacity')
                row['object_addresses'].add(obj);windows[int(t//5)][row['native_class']]+=1
            elif event==31:
                key=a[0]
                if key not in origins:origins[key]=set()
                if not 0<a[2]<=32 or a[1]>=a[2] or len(origins)>4096:raise ValueError('Origin fragments invalid')
                origins[key].update(range(a[1],min(a[1]+8,a[2])))
                if len(origins[key])==a[2]:origins.pop(key);stats['complete_origin_samples']+=1;tail_origins+=1
            elif event==32:
                stats['present_flushed_origin_samples']+=a[1];tail_origins=0
    if last!=h.written:raise ValueError('Header count disagreement')
    for row in lights.values():
        row['types']=sorted(row['types']);row['enabled_types']=sorted(row['enabled_types']);row['last_known_fields']=known_light_fields(row['last_raw']) if row['last_raw'] else None
        row['directional_patterns']=list(row['directional_patterns'].values())
    for row in classes.values():row['distinct_process_local_addresses']=len(row.pop('object_addresses'))
    with path.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest().upper()
    return dict(run=folder.name,trace_sha256=sha,bytes=h.fileBytes,records=h.written,retained_tactical_seconds=(h.endQpc-h.gateQpc)/h.frequency,dropped=h.dropped,stop_reason=h.reason,
        statistics=dict(stats),origin_samples_after_last_present_stats=tail_origins,origin_counter_difference_explained=stats['complete_origin_samples']-stats['present_flushed_origin_samples']==tail_origins,
        incomplete_light_fragments=len(pending),incomplete_origins=len(origins),classes=list(classes.values()),light_slots=list(lights.values()),light_control_callers=dict(caller_controls),windows=[dict(window=k,counts=dict(v)) for k,v in sorted(windows.items())],
        limitations=['Concrete RTTI class is not an exact visual atlas region or translated draw owner','List observations are not render calls or lifecycle epochs','Position changes are raw native light fields, not proven weapon-to-light attachment','Race is sponsor fixture context, not inferred from pointer values','Only qualified +04..+28 light floats decoded;unknown tail retained raw'])

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('runs',nargs='+',type=Path);p.add_argument('--client',type=Path,default=Path(r'C:\Project\SFC-Remix-Return-Test\StarFleetOP.exe'));a=p.parse_args()
    image=Image(a.client)
    for folder in a.runs:
        result=review(folder,image);encoded=json.dumps(result,indent=2)
        if len(encoded.encode())>4*1024*1024:raise ValueError('Native review4MiB limit')
        (folder/'native-survey.review.json').write_text(encoded,encoding='utf-8')
        print(folder.name,'classes',len(result['classes']),'light_records',result['statistics']['complete_light_records'],'origin_difference_explained',result['origin_counter_difference_explained'])

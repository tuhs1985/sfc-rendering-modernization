"""Pinned, read-only SFC rendering RTTI/vtable inventory and bounded effects CFG.

No code execution, generic engine decompilation, hooks, asset reads or renderer changes.
Only the selected rendering names and byte-verified effects instructions are exported.
"""
import argparse,collections,hashlib,json,re,struct,sys
from pathlib import Path
from verify_effect_resource_path import Image

NAME=re.compile(rb'\.\?A[VU][A-Za-z0-9_@$?]{1,240}?@@\x00')
LINE=re.compile(r'^\s*([0-9A-F]{8}):\s+((?:[0-9A-F]{2}\s+){0,14}[0-9A-F]{2})\s+([a-z][a-z0-9]*)\s*(.*?)\s*$',re.I)
MAX_CLASSES=128
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'render_survey'))

def category(name):
    leaf=name[4:].split('@')[0]
    if leaf.startswith('tFx_'):return 'effects'
    if leaf.startswith(('tModel','t3DVisual')):return 'semantic_model'
    if leaf.startswith('tCamera') and '@tState_Namespace_Tactical@' in name:return 'tactical_camera'
    if leaf.startswith('tETrait_') and re.search(r'(Explosion|Shield|Damage|Weapon)',leaf):return 'attached_effect'
    if leaf in ('tLightPhaser_Creator','tTRBeamLight_Creator'):return 'light_creator'
    if leaf in ('tGLSprite','tSpriteCntl','tAnimatingSprite','tMetaMapSprite','tVisSprite','tAmbientLightBar'):return 'sprite_or_ui'
    if leaf=='tEntity_DustCloud':return 'environment'
    return None

def u32(image,va):return struct.unpack('<I',image.read(va,4))[0]
def section(image,va,executable=None):
    for s in image.meta['sections']:
        if image.base+s['rva']<=va<image.base+s['rva']+s['raw_size']:
            if executable is None or bool(int(s['characteristics'],16)&0x20000000)==executable:return s
    return None

def data_words(image):
    for s in image.meta['sections']:
        if int(s['characteristics'],16)&0x20000000:continue
        raw=image.data[s['raw_offset']:s['raw_offset']+s['raw_size']]
        for i,(value,) in enumerate(struct.iter_unpack('<I',raw[:len(raw)//4*4])):
            yield image.base+s['rva']+i*4,value

def descriptors(image):
    found={}
    for s in image.meta['sections']:
        if int(s['characteristics'],16)&0x20000000:continue
        raw=image.data[s['raw_offset']:s['raw_offset']+s['raw_size']]
        for match in NAME.finditer(raw):
            name=match.group()[:-1].decode('ascii');kind=category(name)
            if not kind:continue
            va=image.base+s['rva']+match.start()-8
            if va%4 or match.start()<8:continue
            # MSVC x86 TypeDescriptor: type_info vtable, spare=0, name.
            if u32(image,va+4)!=0 or not section(image,u32(image,va),False):continue
            found[va]=dict(native_name=name[4:-2],mangled_name=name,category=kind,type_descriptor=va,vtables=[])
            if len(found)>MAX_CLASSES:raise ValueError('Rendering-class bound exceeded')
    return found

def hierarchy(image,va,descriptor):
    signature,attributes,count,array=struct.unpack('<4I',image.read(va,16))
    if signature or attributes&~7 or not 0<count<=64:raise ValueError('Unqualified class hierarchy')
    bases=[]
    for i in range(count):
        base=u32(image,u32(image,array+i*4));raw=image.read(base+8,128).split(b'\0',1)[0].decode('ascii')
        if not raw.startswith(('.?AV','.?AU')) or not raw.endswith('@@'):raise ValueError('Unqualified base descriptor')
        if i==0 and base!=descriptor:raise ValueError('RTTI hierarchy self mismatch')
        bases.append(raw[4:-2])
    return bases

def inventory(image):
    types=descriptors(image);locators={}
    for va,value in data_words(image):
        if value not in types:continue
        col=va-12
        try:
            sig,offset,construction,td,chd=struct.unpack('<5I',image.read(col,20))
            if sig or offset>0x100000 or construction>0x100000:continue
            bases=hierarchy(image,chd,td)
        except (ValueError,UnicodeError,struct.error):continue
        locators[col]=(td,offset,construction,bases)
    for va,value in data_words(image):
        if value not in locators:continue
        td,offset,construction,bases=locators[value];vt=va+4;methods=[]
        for index in range(128):
            try:target=u32(image,vt+index*4)
            except ValueError:break
            if not section(image,target,True):break
            methods.append(dict(slot=index*4,target=target))
        if not methods:continue
        types[td]['vtables'].append(dict(address=vt,locator=value,object_offset=offset,constructor_displacement=construction,bases=bases,methods=methods,method_scan_capped=len(methods)==128))
    return sorted(types.values(),key=lambda x:(x['category'],x['native_name']))

def disassembly_rows(path):
    """dumpbin wraps the seventh+ instruction bytes onto addressless lines."""
    pending=None
    with path.open(encoding='utf-8',errors='strict') as f:
        for line in f:
            m=LINE.match(line) if ':' in line[:12] else None
            if m:
                if pending:yield pending[0],bytes(pending[1]),pending[2],pending[3]
                pending=[int(m[1],16),bytearray.fromhex(m[2]),m[3].lower(),m[4]]
            elif pending:
                continuation=re.fullmatch(r'\s+((?:[0-9A-F]{2}\s*){1,15})\s*',line,re.I)
                if continuation:
                    pending[1].extend(bytes.fromhex(continuation[1]))
                    if len(pending[1])>15:raise ValueError('Instruction exceeds x86 length bound')
                else:
                    yield pending[0],bytes(pending[1]),pending[2],pending[3];pending=None
    if pending:yield pending[0],bytes(pending[1]),pending[2],pending[3]

def instructions(image,path,low,high,vtables,return_addresses=()):
    if path.stat().st_size>128*1024*1024:raise ValueError('Disassembly input128MiB limit')
    result={};installs=collections.defaultdict(list);caller_instructions={}
    for va,raw,op,args in disassembly_rows(path):
            install=re.fullmatch(r'dword ptr \[[^\]]+\],([0-9A-F]{6,8})h',args,re.I) if op=='mov' else None
            value=int(install[1],16) if install else None
            relevant=low<=va<=high
            caller=va+len(raw) in return_addresses and op=='call'
            if not relevant and value not in vtables and not caller:continue
            if image.read(va,len(raw))!=raw:raise ValueError(f'Disassembly/PE bytes differ at{va:08X}')
            if relevant:result[va]=(raw,op,args)
            if caller:caller_instructions[va+len(raw)]=dict(site=va,opcode=op,operand=args)
            if value in vtables:
                if len(installs[value])>=128:raise ValueError('Vtable install-site bound')
                installs[value].append(va)
    if len(result)>150000:raise ValueError('Effects instruction index bound')
    return result,installs,caller_instructions

def direct(args):return int(args,16) if re.fullmatch(r'[0-9A-F]{8}',args,re.I) else None
def string_at(image,va):
    try:
        raw=image.read(va,128).split(b'\0',1)[0]
        if not 3<=len(raw)<128:return None
        text=raw.decode('ascii')
        return text if re.fullmatch(r'[ -~]+',text) and re.search(r'(?i)(assets[/\\]|\.(?:bmp|pcx|mod)$)',text) else None
    except (ValueError,UnicodeError):return None

def asset_acquisitions(image,code):
    """Exact registry receiver/literal argument/result-store patterns only."""
    addresses=sorted(code);rows=[]
    for i,pc in enumerate(addresses):
        _,op,args=code[pc]
        if op!='call' or not re.fullmatch(r'dword ptr \[[a-z]+\+8\]',args,re.I):continue
        previous=addresses[max(0,i-12):i]
        assignments=[x for x in previous if re.match(r'ecx,',code[x][2],re.I) and code[x][1] in ('mov','lea','xor','pop')]
        if not assignments:continue
        receiver=code[assignments[-1]]
        if receiver[1:]!=('mov','ecx,dword ptr ds:[008CC620h]'):continue
        literals=[]
        for p in previous:
            _,mn,arg=code[p]
            m=re.fullmatch(r'([0-9A-F]{6,8})h',arg,re.I) if mn=='push' else None
            text=string_at(image,int(m[1],16)) if m else None
            if text:literals.append((p,int(m[1],16),text))
        if not literals:continue
        push,pointer,text=literals[-1];stored=None;store_site=None
        pushes=[p for p in previous if code[p][1]=='push']
        if not pushes or pushes[-1]!=push or any(code[p][1]=='call' for p in previous if p>push):continue
        for p in addresses[i+1:i+13]:
            _,mn,arg=code[p]
            m=re.fullmatch(r'dword ptr ds:\[([0-9A-F]{8})h\],eax',arg,re.I) if mn=='mov' else None
            if m:stored=int(m[1],16);store_site=p;break
            if mn.startswith(('call','j','ret')) or re.match(r'eax,',arg,re.I):break
        rows.append(dict(call_site=pc,literal_push=push,literal_address=pointer,filename=text,format_template='%' in text,result_slot=stored,result_store=store_site,confidence='CONFIRMED_STATIC_REGISTRY_ACQUIRE_LITERAL'+('_RESULT_STORE' if stored else '_NO_QUALIFIED_STORE')))
    return rows

def binding_candidates(code,g,assets):
    addresses=sorted(code);indices={pc:i for i,pc in enumerate(addresses)};rows=[]
    for call in g['indirect_calls']:
        if call['slot']!=0x134:continue
        pc=call['site'];i=indices[pc];source=None;push=None;indexed=False
        for prev in reversed(addresses[max(0,i-12):i]):
            _,op,args=code[prev]
            if op=='push':
                m=re.fullmatch(r'dword ptr (?:ds:)?\[([^\]]*?)([0-9A-F]{8})h\]',args,re.I)
                if m:source=int(m[2],16);indexed=bool(m[1]);push=prev
                break
            if op=='call' or op.startswith(('j','ret')):break
        matches=[a for a in assets if a['result_slot']==source] if source else []
        if indexed and source:
            address=source+4
            while len(matches)<64:
                more=[a for a in assets if a['result_slot']==address]
                if not more:break
                matches.extend(more);address+=4
        rows.append(dict(site=pc,source_push=push,source_slot=source,indexed=indexed,static_acquisitions=matches,index_range_proven=False if indexed else None,confidence='STATIC_ARGUMENT_TO_VIRTUAL_SLOT134_RECEIVER_NOT_AUTOMATICALLY_PROVEN'))
    return rows

def graph(image,code,root,low,high,max_depth=2):
    functions=[(root,0)];seen_functions=set();seen=set();calls=[];indirect=[];resources=[];literals=[];gaps=[]
    while functions:
        start,depth=functions.pop()
        if start in seen_functions:continue
        if len(seen_functions)>=32:gaps.append('DIRECT_FUNCTION_LIMIT32');break
        seen_functions.add(start);todo=[start];local=set()
        while todo:
            pc=todo.pop()
            if pc in local:continue
            if len(local)>=4096:gaps.append(f'INSTRUCTION_LIMIT4096:{start:08X}');break
            local.add(pc);seen.add(pc)
            if pc not in code or abs(pc-start)>65536:gaps.append(f'UNRESOLVED_CONTROL:{pc:08X}');continue
            raw,op,args=code[pc];nxt=pc+len(raw)
            for token in re.findall(r'(?<![0-9A-F])([0-9A-F]{6,8})h',args,re.I):
                va=int(token,16)
                if 0x0092F5FC<=va<=0x0092F614 and (va-0x0092F5FC)%4==0:
                    operands=re.findall(r'\[([^\]]+)\]',args)
                    indexed=any(token.lower() in operand.lower() and not re.fullmatch(r'[0-9A-F]+h',operand,re.I) for operand in operands)
                    resources.append(dict(site=pc,slot_address=va,initializer_name=f'fx{(va-0x0092F5FC)//4}',indexed_address=indexed,opcode=op,function=start,confidence='CONFIRMED_CODE_REFERENCE_NOT_RUNTIME_FILENAME_OR_BOUND_PIXEL'))
                text=string_at(image,va)
                if text:literals.append(dict(site=pc,address=va,text=text,function=start,confidence='DIRECT_LITERAL_REFERENCE_NOT_PROVEN_ASSET_BINDING'))
            if op in ('call','jmp'):
                target=direct(args)
                if target is not None:
                    calls.append(dict(site=pc,target=target,opcode=op,function=start,depth=depth))
                    if op=='call' and low<=target<=high and depth<max_depth:functions.append((target,depth+1))
                    elif op=='call' and low<=target<=high:gaps.append(f'CALL_DEPTH_LIMIT:{target:08X}')
                    if op=='jmp':
                        if low<=target<=high:todo.append(target)
                        else:gaps.append(f'TAIL_OUTSIDE_EFFECTS:{target:08X}')
                        continue
                else:
                    slots=re.findall(r'\+([0-9A-F]+)h\]',args,re.I)
                    indirect.append(dict(site=pc,function=start,opcode=op,slot=int(slots[-1],16) if slots else None,receiver='UNRESOLVED_NOT_AUTOMATICALLY_GRAPHICS_MANAGER'))
                    if op=='jmp':gaps.append(f'INDIRECT_JUMP:{pc:08X}');continue
            if op.startswith('ret') or op in ('int','int3','ud2'):continue
            if op.startswith('j') or op.startswith('loop'):
                target=direct(args)
                if target is not None:todo.append(target)
                else:gaps.append(f'UNKNOWN_BRANCH:{pc:08X}')
            todo.append(nxt)
    return dict(root=root,confidence='BYTE_VERIFIED_BOUNDED_STATIC_CONTROL_FLOW_NOT_RUNTIME_EXECUTION',functions=sorted(seen_functions),instruction_count=len(seen),direct_calls=calls,indirect_calls=indirect,fx_global_references=resources,asset_literal_references=literals,limitations=sorted(set(gaps)))

def build(image,disasm,runs):
    rows=inventory(image);vtables={v['address'] for row in rows for v in row['vtables']};observed=collections.defaultdict(list)
    light_callers=collections.defaultdict(collections.Counter);runtime_evidence=[]
    for folder in runs:
        d=json.loads((folder/'native-survey.review.json').read_text())
        for c in d['classes']:observed[int(c['vtable'],16)].append(dict(run=folder.name,draw_target=int(c['draw_target'],16),observations=c['observations']))
        from survey_capture import Header,RECORD,validate
        with (folder/'broad.bin').open('rb') as f:
            header_raw=f.read(128);header=Header.from_buffer_copy(header_raw);validate(header)
            if header.version!=2 or header.fileBytes!=(folder/'broad.bin').stat().st_size:raise ValueError('Runtime trace size/version mismatch')
            sha=hashlib.sha256(header_raw)
            while raw:=f.read(128):
                sha.update(raw)
                _,_,event,_,_,caller,*args=RECORD.unpack(raw)
                if event==36:light_callers[caller][args[4]]+=1
        if sha.hexdigest().upper()!=d['trace_sha256']:raise ValueError('Runtime review/trace SHA mismatch')
        runtime_evidence.append(dict(run=folder.name,trace_sha256=d['trace_sha256'],records=header.written))
        if len(light_callers)>256:raise ValueError('Observed light caller bound')
    roots=[v['methods'][1]['target'] for row in rows if row['category']=='effects' and row['native_name']!='tFx_Base' for v in row['vtables'] if v['object_offset']==0 and len(v['methods'])>1]
    if not roots:raise ValueError('No qualified effects vtables')
    low=min(roots)-8192;high=max(roots)+8192;code,installs,caller_instructions=instructions(image,disasm,low,high,vtables,set(light_callers))
    light_sites=[]
    for caller,counts in sorted(light_callers.items()):
        instruction=caller_instructions.get(caller);slot=None
        if instruction:
            m=re.fullmatch(r'dword ptr \[[a-z]+\+([0-9A-F]+)h?\]',instruction['operand'],re.I)
            if m:slot=int(m[1],16)
        confirmed=instruction is not None and all((kind==4 and direct(instruction['operand'])==0x004ECFB3) or (kind in (1,2,3) and slot=={1:0x80,2:0x98,3:0x90}[kind]) for kind in counts)
        light_sites.append(dict(return_address=caller,counts_by_kind=dict(counts),instruction=instruction,manager_slot=slot,match='CONFIRMED_OBSERVED_KIND_AND_BYTE_VERIFIED_CALL' if confirmed else 'UNRESOLVED_CALLER_RELATIONSHIP'))
    assets=asset_acquisitions(image,code);graphs={}
    for row in rows:
        for v in row['vtables']:
            v['byte_verified_install_sites']=installs.get(v['address'],[]);v['observed_membership']=observed.get(v['address'],[])
            if row['category']=='effects' and row['native_name']!='tFx_Base' and v['object_offset']==0 and len(v['methods'])>1:
                target=v['methods'][1]['target'];v['candidate_global_draw_slot']=4
                for seen in v['observed_membership']:
                    if seen['draw_target']!=target:raise ValueError('Runtime target differs from static vtable')
                v['slot4_role']='CONFIRMED_OBSERVED_DISPATCH' if v['observed_membership'] else 'STATIC_BASE_FAMILY_DISPATCH_CANDIDATE_NOT_OBSERVED'
                if target not in graphs:
                    graphs[target]=graph(image,code,target,low,high)
                    graphs[target]['slot134_binding_candidates']=binding_candidates(code,graphs[target],assets)
                v['effects_graph_root']=target
    with disasm.open('rb') as f:disassembly_sha=hashlib.file_digest(f,'sha256').hexdigest().upper()
    return dict(probe='OFFLINE-RENDER-INVENTORY-001',client_sha256=hashlib.sha256(image.data).hexdigest().upper(),disassembly_sha256=disassembly_sha,runtime_evidence=runtime_evidence,classes=rows,class_count=len(rows),category_counts=dict(collections.Counter(r['category'] for r in rows)),effects_code_window=[low,high],indexed_effects_instructions=len(code),effects_graphs=list(graphs.values()),static_asset_acquisitions=assets,observed_light_call_sites=light_sites,
        limits=dict(classes=128,vtable_methods=128,direct_call_depth=2,functions_per_graph=32,instructions_per_function=4096,function_span_bytes=65536,output_bytes=8*1024*1024),
        exclusions=['No game/runtime launch','No assets opened or copied','No proprietary binary/disassembly export','No new render implementation','Static references do not prove runtime branch or physical light meaning','Non-effects virtual slot roles remain unresolved','Indirect calls and jump tables are not guessed','Class inventory is not complete engine or rendering coverage'])

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--client',type=Path,default=Path(r'C:\Project\SFC-Remix-Return-Test\StarFleetOP.exe'));p.add_argument('--disassembly',type=Path,default=Path('artifacts/pre-m0/raw/StarFleetOP-2.5.6.4.dumpbin-disasm.txt'));p.add_argument('--runtime-run',type=Path,action='append',default=[]);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    r=build(Image(a.client),a.disassembly,a.runtime_run);text=json.dumps(r,indent=2)
    if len(text.encode())>r['limits']['output_bytes']:raise ValueError('Inventory output8MiB bound')
    if a.output.exists():raise ValueError('Choose a new output;do not overwrite prior inventory')
    a.output.write_text(text,encoding='utf-8');print(json.dumps({k:r[k] for k in ('class_count','category_counts','indexed_effects_instructions')},indent=2))

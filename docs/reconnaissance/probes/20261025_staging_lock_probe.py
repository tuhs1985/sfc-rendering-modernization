"""Isolated call-timing derivative. Never deployed to SFC or qualification."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
HERE=ROOT/"artifacts/resource-stall"

HEADER=r'''
// Diagnostic derivative only: bounded deferred call records, no render-time IO.
struct ResourceTrace {
 struct Record {const char* operation;unsigned renderer,index;uint64_t bytes,begin,end,cpu;};
 std::array<Record,8192> records{};unsigned used=0,dropped=0,current=0,next=0;uint64_t frequency=0;
 ResourceTrace(){LARGE_INTEGER f{};QueryPerformanceFrequency(&f);frequency=f.QuadPart;}
 static uint64_t qpc(){LARGE_INTEGER q{};QueryPerformanceCounter(&q);return q.QuadPart;}
 static uint64_t cpu(){FILETIME a{},b{},k{},u{};GetThreadTimes(GetCurrentThread(),&a,&b,&k,&u);
  ULARGE_INTEGER x{},y{};x.LowPart=k.dwLowDateTime;x.HighPart=k.dwHighDateTime;y.LowPart=u.dwLowDateTime;y.HighPart=u.dwHighDateTime;return x.QuadPart+y.QuadPart;}
 void add(const char* op,unsigned index,uint64_t bytes,uint64_t begin,uint64_t end,uint64_t cpuTicks){
  if(used==records.size()){++dropped;return;}records[used++]={op,current,index,bytes,begin,end,cpuTicks};}
 ~ResourceTrace(){for(unsigned i=0;i<used;++i){const auto& r=records[i];
  std::cout<<"RESOURCE_CALL renderer="<<r.renderer<<" op="<<r.operation<<" index="<<r.index<<" bytes="<<r.bytes
   <<" begin_qpc="<<r.begin<<" end_qpc="<<r.end<<" frequency="<<frequency<<" cpu_100ns="<<r.cpu<<'\n';}
  std::cout<<"RESOURCE_CALL_SUMMARY records="<<used<<" dropped="<<dropped<<" thread="<<GetCurrentThreadId()<<'\n';}
};
static ResourceTrace& resourceTrace(){static thread_local ResourceTrace value;return value;}
struct ResourceTraceRenderer {ResourceTrace& trace;unsigned prior;uint64_t begin,cpu;
 ResourceTraceRenderer():trace(resourceTrace()),prior(trace.current),begin(ResourceTrace::qpc()),cpu(ResourceTrace::cpu()){trace.current=++trace.next;}
 ~ResourceTraceRenderer(){trace.add("renderer_total",0,0,begin,ResourceTrace::qpc(),ResourceTrace::cpu()-cpu);trace.current=prior;}
};
template<class Fn>static HRESULT resourceCall(const char* op,unsigned index,uint64_t bytes,Fn fn){
 auto& trace=resourceTrace();const auto begin=ResourceTrace::qpc(),cpu=ResourceTrace::cpu();const HRESULT hr=fn();
 const auto end=ResourceTrace::qpc();trace.add(op,index,bytes,begin,end,ResourceTrace::cpu()-cpu);return hr;
}
'''

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def prepare(initial=False):
 HERE.mkdir(parents=True,exist_ok=True)
 source=ROOT/'tools/d3d9_proof/d3d9_replay.cpp'; text=source.read_text()
 text=text.replace('struct Renderer{',HEADER+'\nstruct Renderer{',1)
 needle='explicit Renderer(IDirect3DDevice9* d,const Scene& s,const fs::path& root,const std::vector<std::vector<BYTE>>* prepared=nullptr):device(d),scene(s){'
 assert text.count(needle)==1;text=text.replace(needle,needle+'\n  ResourceTraceRenderer traceRenderer;')
 calls=[
 ('vb_create','0','nv*sizeof(Vertex)','d->CreateVertexBuffer(nv*sizeof(Vertex),0,fvf,D3DPOOL_DEFAULT,&vb,nullptr)'),
 ('vb_lock','0','nv*sizeof(Vertex)','vb->Lock(0,0,&p,0)'),
 ('vb_unlock','0','nv*sizeof(Vertex)','vb->Unlock()'),
 ('ib_create','0','ni*4','d->CreateIndexBuffer(ni*4,0,D3DFMT_INDEX32,D3DPOOL_DEFAULT,&ib,nullptr)'),
 ('ib_lock','0','ni*4','ib->Lock(0,0,&p,0)'),
 ('ib_unlock','0','ni*4','ib->Unlock()'),
 ('texture_create','i','h[3]','d->CreateTexture(h[1],h[2],1,0,D3DFMT_A8R8G8B8,D3DPOOL_DEFAULT,&textures[i],nullptr)'),
 ('staging_create','i','h[3]','d->CreateTexture(h[1],h[2],1,0,D3DFMT_A8R8G8B8,D3DPOOL_SYSTEMMEM,&upload,nullptr)'),
 ('staging_lock','i','h[3]','upload->LockRect(0,&lock,nullptr,0)'),
 ('staging_unlock','i','h[3]','upload->UnlockRect(0)'),
 ('texture_update','i','h[3]','d->UpdateTexture(upload.Get(),textures[i].Get())')]
 # Replace only the constructor body. Readback TEST branches remain exact.
 begin=text.index('explicit Renderer('); end=text.index('\n void draw(',begin)
 constructor=text[begin:end]
 for op,index,size,call in calls:
  assert constructor.count(call)>=1,(op,constructor.count(call))
  constructor=constructor.replace(call,f'resourceCall("{op}",{index},{size},[&](){{return {call};}})')
 copy='for(uint32_t y=0;y<h[2];++y)memcpy(static_cast<BYTE*>(lock.pBits)+y*lock.Pitch,b.data()+16+size_t(y)*h[1]*4,h[1]*4);'
 assert constructor.count(copy)==1
 constructor=constructor.replace(copy,'ok(resourceCall("texture_cpu_copy",i,h[3],[&](){'+copy+'return S_OK;}),"timed CPU copy");')
 if initial:
  first=constructor.index('   ok(resourceCall("staging_create"')
  last=constructor.index('   ok(resourceCall("texture_update"',first)
  constructor=constructor[:first]+'''   D3DLOCKED_RECT lock{};HANDLE pixelsHandle=reinterpret_cast<HANDLE>(const_cast<BYTE*>(b.data()+16));
   ok(resourceCall("staging_initial_data",i,h[3],[&](){return d->CreateTexture(h[1],h[2],1,0,D3DFMT_A8R8G8B8,D3DPOOL_SYSTEMMEM,&upload,&pixelsHandle);}),"systemmem initial data");
'''+constructor[last:]
 tail='\n   }\n  }\n }'
 assert constructor.endswith(tail)
 constructor=constructor[:-len(tail)]+'\n   }\n   ok(resourceCall("staging_release",i,h[3],[&](){upload.Reset();return S_OK;}),"timed staging release");\n  }\n }'
 text=text[:begin]+constructor+text[end:]
 (HERE/'d3d9_replay.cpp').write_text(text)
 host=ROOT/'tools/d3d9_proof/d3d9_direct_host.cpp'
 (HERE/'profile_host.cpp').write_bytes(host.read_bytes())
 inputs={str(p.relative_to(ROOT)):sha(p) for p in (source,host)}
 manifest=dict(diagnostic_only=True,production_qualification_eligible=False,source=inputs,
  derived={p.name:sha(p) for p in (HERE/'d3d9_replay.cpp',HERE/'profile_host.cpp')},
  initial_data_control=initial,
  transforms='QPC/thread-time wrappers;deferred8192record cap;explicit same-position staging Release;all formats/data unchanged;optional documented SYSTEMMEM initial-data creation replaces staging lock/copy/unlock')
 (HERE/'probe.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))

def run(late):
 sys.path.insert(0,str(ROOT/'tools/remix_runtime'))
 import live_owner_timing as live
 import run_return_fixture as fixture
 manifest=json.loads((HERE/'probe.json').read_text())
 for p,h in manifest['source'].items():assert sha(ROOT/p)==h,'Source changed;regenerate diagnostic'
 before=set((ROOT/'artifacts/remix-runtime/runs').iterdir())
 original=live.EXE;original_hash=sha(original);live.EXE=HERE/'profile_host.exe'
 assert live.EXE.is_file()
 for name,h in manifest['derived'].items():assert sha(HERE/name)==h,'Diagnostic source changed'
 assert live.EXE.stat().st_mtime_ns>=max((HERE/name).stat().st_mtime_ns for name in manifest['derived']),'Rebuild diagnostic after preparation'
 manifest['host_sha256']=sha(live.EXE);manifest['runtime_sha256']=sha(live.RUNTIME)
 (HERE/'run-input.json').write_text(json.dumps(manifest,indent=2))
 sys.argv=['run_return_fixture.py','--multi-ship','--multi-ship-resources','--prewarm','--startup-profile','--pipeline-mode','performance','--parallel-assets','--asset-admission-service','on']
 if late:sys.argv.append('--multi-ship-late-asset')
 try:fixture.main()
 finally:
  assert sha(original)==original_hash
  for folder in set((ROOT/'artifacts/remix-runtime/runs').iterdir())-before:
   p=folder/'result.json'
   if p.is_file():
    d=json.loads(p.read_text());d['diagnostic_original_reference_locks']=d.pop('multi_ship_build_locks',None)
    d['resource_call_profile']=manifest;d['production_qualification_eligible']=False
    p.write_text(json.dumps(d,indent=2))
   (folder/'resource-probe.json').write_text(json.dumps(manifest,indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=('prepare','run'));p.add_argument('--late',action='store_true');p.add_argument('--initial-data',action='store_true');a=p.parse_args()
 prepare(a.initial_data) if a.action=='prepare' else run(a.late)

// Exercise the actual recorder with synthetic x86 engine objects. No game launch.
#include "../tools/m1_component/m1_component.cpp"
#include <iostream>
static unsigned checks=0;
static void test(bool b){++checks;if(!b){std::cerr<<"component check "<<checks<<'\n';std::exit(1);}}
static unsigned gateAcquires=0,gateCommits=0;static bool gateTimeout=false;
static DWORD WINAPI fakeGate(DWORD action,const native_gate::Ticket* t,native_gate::Reply* r){
 test(g_lock.RecursionCount==0&&g_in_native_gate==1&&g_in_recorders==0);
 test(t&&t->owner&&t->source&&t->hash&&t->sequence);
 if(action==DWORD(native_gate::Action::Acquire)){++gateAcquires;r->result=gateTimeout?native_gate::Result::Timeout:native_gate::Result::Acquired;r->token=44;}
 if(action==DWORD(native_gate::Action::Commit)){++gateCommits;test(r->token==44);r->result=native_gate::Result::Inserted;}
 return DWORD(r->result);
}
// Real hook stubs CALL the recorder; do not inline its capture scratch into main.
static __declspec(noinline) void invokeRecorder(const DWORD* saved){RecordHook(kWrapper,saved);}
static __declspec(noinline) void collect(ThreadState* state,const EventRecord& event){state->wrapper_pending=1;observe_mesh_export(state,event,1,[](DWORD a,void* p,DWORD n){if(a==0xC69FF0||a==0xC69FF4||a==0xC74058){memset(p,0,n);return true;}return safe_copy(a,p,n);});state->wrapper_pending=0;}
int main(){
 InitializeCriticalSection(&g_lock);g_running=g_gate=1;g_frame=100;g_gate_tick=GetTickCount64();g_config.enable_mesh_export=true;
 std::array<DWORD,35> ship{};std::array<DWORD,100> visual{};std::array<DWORD,7> model{};
 std::array<DWORD,8192> manager{};std::array<DWORD,9> source{},positions{0,0,0,0x3f800000,0,0,0,0x3f800000,0};
 std::array<DWORD,21> corners{};for(DWORD i=0;i<3;++i){corners[i*7]=i;corners[i*7+3]=0x3f800000;}
 std::array<DWORD,7> polygon{3,0,0,0,0x3f800000,0,reinterpret_cast<DWORD>(corners.data())};std::array<DWORD,1> list{reinterpret_cast<DWORD>(polygon.data())};
 ship[0]=kShipVtable;ship[34]=reinterpret_cast<DWORD>(visual.data());visual[0]=kVisualVtable;visual[0x11c/4]=1;visual[0x120/4]=0xffffffff;
 visual[0x158/4]=reinterpret_cast<DWORD>(source.data());visual[0x160/4]=reinterpret_cast<DWORD>(model.data());
 model={kModel0Vtable,0,3,reinterpret_cast<DWORD>(positions.data()),1,reinterpret_cast<DWORD>(list.data()),reinterpret_cast<DWORD>(list.data())};
 manager[0]=0x007B8D4C;manager[0x554/4]=model[3];manager[0x558/4]=visual[0x158/4];
 auto* state=thread_state(GetCurrentThreadId());state->ship=reinterpret_cast<DWORD>(ship.data());state->visual=reinterpret_cast<DWORD>(visual.data());state->model0=reinterpret_cast<DWORD>(model.data());
 state->source=visual[0x158/4];state->model_manager=reinterpret_cast<DWORD>(manager.data());state->owner_id=g_owners.observe(state->ship,state->visual,100).id;state->model_scope=true;state->copy_depth=1;
 g_live_scene.owners[0].identity.owner=state->owner_id;g_live_scene.owners[0].revision=4;
 auto ledger=std::make_unique<replacement::Store>();DWORD session[]{1,2,3,4};replacement::initialize(*ledger,session,GetCurrentProcessId());g_replacement=ledger.get();
 replacement::Control control{};control.mode=replacement::Active;control.generation=2;control.owner=state->owner_id;control.revision=4;control.model=state->model0;control.source=state->source;control.thread=GetCurrentThreadId();control.epoch=1;control.permit=100;control.expires=replacement::now()+1000000000;
 replacement::write(ledger->control,control);replacement::begin(*ledger,100,GetCurrentThreadId());
 EventRecord event{};event.ecx=state->model_manager;event.arg1=1;event.arg2=reinterpret_cast<DWORD>(list.data());event.return_address=0x0042E55D;event.thread_id=GetCurrentThreadId();
 collect(state,event);
 test(g_mesh_packet.complete&&g_mesh_packet.header[4]==state->owner_id);
 const auto originalPositions=positions;const auto originalModel=model;const auto originalList=list;std::vector<BYTE> mesh(sizeof(g_mesh_packet));memcpy(mesh.data(),&g_mesh_packet,mesh.size());
 std::array<DWORD,5> stack{0x0042E55D,1,reinterpret_cast<DWORD>(list.data()),1,0};std::array<DWORD,9> saved{};saved[3]=reinterpret_cast<DWORD>(stack.data())-4;saved[6]=state->model_manager;
 invokeRecorder(saved.data());test(stack[1]==0);test(stack[2]==reinterpret_cast<DWORD>(list.data()));test(model==originalModel&&list==originalList&&positions==originalPositions);
 test(memcmp(mesh.data(),&g_mesh_packet,mesh.size())==0);test(g_wrapper_samples[0].data[10]==1); // Observer retained original count.
 stack[0]=0x0042E626;stack[1]=1;invokeRecorder(saved.data());test(stack[1]==0);
 replacement::Receipt r{};test(replacement::sample(*ledger,100,r)&&r.primary==1&&r.secondary==1);
 // Metadata-only insertion mode must veto even a mistakenly active permit.
 auto probe=std::make_unique<native_insertion::Store>();native_insertion::initialize(*probe,session,GetCurrentProcessId());g_insertion_probe=probe.get();
 stack[1]=1;invokeRecorder(saved.data());test(stack[1]==1);g_insertion_probe=nullptr;
 // Revoked and nested invocations remain untouched; partial frame is rejected.
 InterlockedExchange(&ledger->native_stop,1);stack[1]=1;invokeRecorder(saved.data());test(stack[1]==1);
 InterlockedExchange(&ledger->native_stop,0);state->copy_depth=2;stack[1]=1;invokeRecorder(saved.data());test(stack[1]==1);
 replacement::sample(*ledger,100,r);test(r.flags&replacement::Invalid);
 state->copy_depth=1;control.owner=999;replacement::write(ledger->control,control);stack[1]=1;invokeRecorder(saved.data());test(stack[1]==1);
 // Actual new post-recorder stage:before-first-list readiness,timeout keeps
 // both original lists,and successful insertion authorizes both consistently.
 auto direct=std::make_unique<live_owner::Store>();direct->header.selected=live_owner::selection(state->owner_id,4);g_live_scene.directSource.store=direct.get();
 auto gate=std::make_unique<native_gate::Store>();native_gate::initialize(*gate,session,GetCurrentProcessId(),native_gate::Policy::ExtraFrame);
 g_native_gate=gate.get();g_native_gate_requested=true;g_native_dispatch=&fakeGate;
 auto start=[&](DWORD frame){g_frame=frame;native_gate::begin(*gate,frame,GetCurrentThreadId());g_native_decided=g_native_inserted=false;
  auto& p=g_live_scene.cohort.pending;p.frame=frame;p.anchor=state->owner_id;p.revision=4;p.sequence=frame;p.offered=native_gate::now();p.checksum=123;
  replacement::begin(*ledger,frame,GetCurrentThreadId());};
 start(101);gateTimeout=true;stack[0]=0x0042e55d;stack[1]=1;invokeRecorder(saved.data());CoordinateAfterCapture(kWrapper,saved.data());
 test(stack[1]==1&&gateAcquires==1&&gateCommits==0);stack[0]=0x0042e626;CoordinateAfterCapture(kWrapper,saved.data());test(stack[1]==1&&gateAcquires==1);
 start(102);gateTimeout=false;stack[0]=0x0042e55d;stack[1]=1;invokeRecorder(saved.data());CoordinateAfterCapture(kWrapper,saved.data());
 test(stack[1]==0&&gateAcquires==2&&gateCommits==1&&g_native_committed==102);
 stack[0]=0x0042e626;stack[1]=1;invokeRecorder(saved.data());CoordinateAfterCapture(kWrapper,saved.data());
 test(stack[1]==0&&gateAcquires==2&&gateCommits==1&&gate->current.primary==1&&gate->current.secondary==1);
 test(!g_in_native_gate&&memcmp(mesh.data(),&g_mesh_packet,mesh.size())==0);
 // Coordinator reentrancy refuses another dispatch and drains its own count.
 g_in_native_gate=1;stack[1]=1;CoordinateAfterCapture(kWrapper,saved.data());test(stack[1]==1&&g_in_native_gate==1&&gateCommits==1);g_in_native_gate=0;
 // Unload's conservative PC exclusion covers each complete naked hook stub.
 for(const auto& hook:g_hooks){const auto* bytes=reinterpret_cast<const BYTE*>(hook.destination);bool end=false;
  for(unsigned j=0;j+6<=128;++j)if(bytes[j]==0xff&&bytes[j+1]==0x25){end=true;break;}test(end);}
 // A later unknown caller is untouched and marks the session partial.
 stack[0]=0x11111111;stack[1]=1;CoordinateAfterCapture(kWrapper,saved.data());test(stack[1]==1&&gate->header.partial==1);
 g_native_gate=nullptr;g_native_gate_requested=false;g_native_dispatch=nullptr;g_live_scene.directSource.store=nullptr;
 g_replacement=nullptr;g_running=0;DeleteCriticalSection(&g_lock);
 std::cout<<"Player suppression recorder PASS checks="<<checks<<" original_capture_preserved=1 primary_secondary=1 nested_other_revoked_passthrough=1\n";
}

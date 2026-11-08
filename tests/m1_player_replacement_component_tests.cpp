// Exercise the actual recorder with synthetic x86 engine objects. No game launch.
#include "../tools/m1_component/m1_component.cpp"
#include <iostream>
static unsigned checks=0;
static void testCheck(bool b,unsigned line){++checks;if(!b){std::cerr<<"component check "<<checks<<" at line "<<line<<'\n';std::exit(1);}}
#define test(value) testCheck((value),__LINE__)
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
 auto start=[&](DWORD frame){g_frame=frame;native_gate::begin(*gate,frame,GetCurrentThreadId());g_native_decided=g_native_inserted=g_native_blocked=false;for(auto& d:g_native_owners)d={};
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
 g_in_native_gate=1;stack[1]=1;CoordinateAfterCapture(kWrapper,saved.data());test(stack[1]==1&&g_in_native_gate==1&&gateCommits==1&&!gate->header.stop&&gate->header.recovery.counts[0]==1);g_in_native_gate=0;
 // Multi-owner mode: two epochs sharing one mesh retain independent decisions.
 g_native_cohort_mode=true;auto cohort=std::make_unique<native_cohort::Store>();native_cohort::initialize(*cohort,session,GetCurrentProcessId());g_native_cohort=cohort.get();
 const DWORD firstOwner=state->owner_id;
 auto otherShip=ship;auto otherVisual=visual;otherShip[34]=reinterpret_cast<DWORD>(otherVisual.data());
 const DWORD secondOwner=g_owners.observe(reinterpret_cast<DWORD>(otherShip.data()),reinterpret_cast<DWORD>(otherVisual.data()),103).id;test(secondOwner==firstOwner+1);
 auto& retained=g_live_scene.registry.entries[0];retained.live=retained.qualified=true;retained.revision=4;retained.id.owner=firstOwner;retained.id.model=state->model0;retained.id.source=state->source;
 auto& second=g_live_scene.registry.entries[1];second=retained;second.id.owner=firstOwner+1;
 gate->header.stop=gate->header.partial=0;start(103);for(auto& d:g_native_owners)d={};auto& pending=g_live_scene.cohort.pending;pending.count=2;
 for(unsigned i=0;i<2;++i){pending.rows[i][1]=firstOwner+i;pending.rows[i][7]=4;pending.rows[i][5]=state->model0;pending.rows[i][6]=state->source;}
 const auto before=gateCommits;
 for(unsigned i=0;i<2;++i){state->owner_id=firstOwner+i;state->ship=reinterpret_cast<DWORD>(i?otherShip.data():ship.data());state->visual=reinterpret_cast<DWORD>(i?otherVisual.data():visual.data());stack[0]=0x0042e55d;stack[1]=1;CoordinateAfterCapture(kWrapper,saved.data());test(stack[1]==0);
  stack[0]=0x0042e626;stack[1]=1;CoordinateAfterCapture(kWrapper,saved.data());test(stack[1]==0);}
 test(gateCommits==before+2&&cohort->header.suppressed==4);
 // A retired owner cannot borrow the other owner's successful decision.
 second.live=false;state->owner_id=firstOwner+1;stack[1]=1;CoordinateAfterCapture(kWrapper,saved.data());test(stack[1]==1&&gateCommits==before+2&&!gate->header.partial&&!gate->header.stop&&gate->header.recovery.counts[1]==1);
 // Retirement/changed submission never disables other owners in this frame.
 state->owner_id=firstOwner;state->ship=reinterpret_cast<DWORD>(ship.data());state->visual=reinterpret_cast<DWORD>(visual.data());
 stack[1]=1;CoordinateAfterCapture(kWrapper,saved.data());test(stack[1]==0&&gateCommits==before+2);
 // A freshly qualified next frame retries naturally,with no restart/asset reload.
 second.live=true;start(104);state->owner_id=firstOwner+1;state->ship=reinterpret_cast<DWORD>(otherShip.data());state->visual=reinterpret_cast<DWORD>(otherVisual.data());
 stack[0]=0x0042e55d;stack[1]=1;CoordinateAfterCapture(kWrapper,saved.data());test(stack[1]==0&&gateCommits==before+3&&!gate->header.stop);
 state->owner_id=firstOwner;state->ship=reinterpret_cast<DWORD>(ship.data());state->visual=reinterpret_cast<DWORD>(visual.data());g_native_cohort_mode=false;g_native_cohort=nullptr;
 // Unload's conservative PC exclusion covers each complete naked hook stub.
 for(const auto& hook:g_hooks){const auto* bytes=reinterpret_cast<const BYTE*>(hook.destination);bool end=false;
  if(!strncmp(hook.name,"break_",6)){
   for(unsigned j=0;j+10<128;++j)if(bytes[j]==0xf0&&bytes[j+1]==0xff&&bytes[j+2]==0x0d){
    DWORD counter=0;memcpy(&counter,bytes+j+3,4);
    if(counter==reinterpret_cast<DWORD>(&g_in_hook_spans)&&(bytes[j+7]==0xc3||bytes[j+7]==0xc2)){end=true;break;}
   }
  }else for(unsigned j=0;j+6<=128;++j)if(bytes[j]==0xff&&bytes[j+1]==0x25){end=true;break;}
  test(end);}
 // Changed/unknown later submissions remain native for this owner/frame only.
 start(105);
 stack[0]=0x0042e55d;stack[1]=1;CoordinateAfterCapture(kWrapper,saved.data());test(stack[1]==0);
 stack[0]=0x11111111;stack[1]=1;CoordinateAfterCapture(kWrapper,saved.data());test(stack[1]==1&&!gate->header.partial&&!gate->header.stop&&gate->header.recovery.counts[2]==1);
 stack[0]=0x0042e626;stack[1]=1;CoordinateAfterCapture(kWrapper,saved.data());test(stack[1]==1); // no further suppression in damaged decision
 start(106);stack[0]=0x0042e55d;stack[1]=1;const auto recovered=gateCommits;
 CoordinateAfterCapture(kWrapper,saved.data());test(stack[1]==0&&gateCommits==recovered+1&&!gate->header.stop);
 // Actual indexed-piece coordinator: a separate child epoch selects only its
 // native primary/secondary slices, with the same acquire/commit obligation.
 std::array<DWORD,14> brokenModel{};std::array<DWORD,100> brokenVisual=visual;
 std::array<DWORD,90> child{};std::array<DWORD,2> ends{1,2},pieceLists{list[0],list[0]};
 brokenModel[0]=kModel0Vtable;brokenModel[2]=3;brokenModel[3]=reinterpret_cast<DWORD>(positions.data());
 brokenModel[4]=2;brokenModel[5]=brokenModel[6]=reinterpret_cast<DWORD>(pieceLists.data());
 brokenModel[11]=1;brokenModel[12]=reinterpret_cast<DWORD>(ends.data());brokenModel[13]=2;
 brokenVisual[0x160/4]=reinterpret_cast<DWORD>(brokenModel.data());
 child[0]=0x7972b4;child[0x24/4]=1;child[0x9c/4]=reinterpret_cast<DWORD>(brokenVisual.data());child[0xa0/4]=1;
 const auto pieceEpoch=g_live_scene.breaks.born(reinterpret_cast<DWORD>(child.data()),firstOwner,reinterpret_cast<DWORD>(brokenVisual.data()),1);
 const auto oldSceneOwner=g_live_scene.owners[0];const auto oldOwnerCount=g_live_scene.owner_count;
 auto& pieceOwner=g_live_scene.owners[0];pieceOwner={};pieceOwner.breakPiece=true;pieceOwner.breakEpoch=pieceEpoch;pieceOwner.revision=5;
 pieceOwner.identity={0x80000000u|DWORD(pieceEpoch),GetCurrentThreadId(),108,0,reinterpret_cast<DWORD>(child.data()),
  reinterpret_cast<DWORD>(brokenVisual.data()),reinterpret_cast<DWORD>(brokenModel.data()),state->model_manager,state->source,
  0x42ea92,reinterpret_cast<DWORD>(pieceLists.data()+1),1};g_live_scene.owner_count=1;
 g_native_cohort_mode=true;g_native_cohort=cohort.get();
 g_break_requested=true;g_break_draw_scope={reinterpret_cast<DWORD>(child.data()),state->model_manager,pieceEpoch};
 auto pieceStart=[&](DWORD frame){start(frame);auto& p=g_live_scene.cohort.pending;p.anchor=pieceOwner.identity.owner;p.revision=5;p.count=1;p.rows[0]={};
  p.rows[0][1]=pieceOwner.identity.owner;p.rows[0][7]=5;p.rows[0][5]=pieceOwner.identity.model;p.rows[0][6]=pieceOwner.identity.source;
  stack={0x42ea92,1,pieceOwner.identity.list,1,0};saved[0]=pieceOwner.identity.model;};
 const auto oldBrokenModel=brokenModel;const auto oldPieceLists=pieceLists;const auto oldChild=child;
 pieceStart(108);const auto beforePieceCommits=gateCommits;CoordinateAfterCapture(kWrapper,saved.data());
 test(stack[1]==0&&gateCommits==beforePieceCommits+1&&gate->current.primary==1);
 stack[0]=0x42eb34;stack[1]=1;CoordinateAfterCapture(kWrapper,saved.data());
 test(stack[1]==0&&gateCommits==beforePieceCommits+1&&gate->current.secondary==1);
 test(brokenModel==oldBrokenModel&&pieceLists==oldPieceLists&&child==oldChild);
 pieceStart(109);g_break_draw_scope.epoch=pieceEpoch+1;CoordinateAfterCapture(kWrapper,saved.data());test(stack[1]==1&&gateCommits==beforePieceCommits+1);
 pieceStart(110);g_break_draw_scope.epoch=pieceEpoch;gateTimeout=true;CoordinateAfterCapture(kWrapper,saved.data());test(stack[1]==1&&gateCommits==beforePieceCommits+1);
 stack[0]=0x42eb34;CoordinateAfterCapture(kWrapper,saved.data());test(stack[1]==1&&gateCommits==beforePieceCommits+1);
 gateTimeout=false;g_break_requested=false;g_break_draw_scope={};g_native_cohort_mode=false;g_native_cohort=nullptr;g_live_scene.breaks.retire(reinterpret_cast<DWORD>(child.data()),pieceEpoch);
 g_live_scene.owners[0]=oldSceneOwner;g_live_scene.owner_count=oldOwnerCount;saved[0]=0;
 stack={0x42e55d,1,reinterpret_cast<DWORD>(list.data()),1,0};
 // Unwritable suppression arguments after insertion are a genuine terminal fault.
 auto* protectedStack=static_cast<DWORD*>(VirtualAlloc(nullptr,4096,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE));test(protectedStack!=nullptr);
 memcpy(protectedStack,stack.data(),sizeof(stack));protectedStack[1]=1;DWORD old=0;test(VirtualProtect(protectedStack,4096,PAGE_READONLY,&old)!=FALSE);
 start(111);saved[3]=reinterpret_cast<DWORD>(protectedStack)-4;CoordinateAfterCapture(kWrapper,saved.data());
 test(protectedStack[1]==1&&gate->header.stop&&gate->header.partial&&gate->header.recovery.terminalReason==LONG(native_gate::TerminalReason::SuppressionWrite));
 test(VirtualFree(protectedStack,0,MEM_RELEASE)!=FALSE);saved[3]=reinterpret_cast<DWORD>(stack.data())-4;
 g_native_gate=nullptr;g_native_gate_requested=false;g_native_dispatch=nullptr;g_live_scene.directSource.store=nullptr;
 g_replacement=nullptr;g_running=0;DeleteCriticalSection(&g_lock);
 std::cout<<"Player suppression recorder PASS checks="<<checks<<" original_capture_preserved=1 primary_secondary=1 nested_other_revoked_passthrough=1\n";
}

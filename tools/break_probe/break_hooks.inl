// Included only in the isolated early-observer build.
using BreakFactory=Word(__cdecl*)(Word,Word);
using BreakVisual=void(__thiscall*)(void*,Word,Word,Word);
using BreakDraw=void(__thiscall*)(void*,Word);
using BreakUpdate=void(__thiscall*)(void*);
using BreakWrapper=Word(__thiscall*)(void*,Word,Word,Word);
inline BreakFactory breakFactory=nullptr;
inline Four breakChild=nullptr;
inline BreakDraw breakDraw=nullptr;
inline BreakVisual breakVisual=nullptr;
inline BreakWrapper breakWrapper=nullptr;
inline BreakUpdate breakUpdate=nullptr;
inline Zero breakRetire=nullptr;
inline constexpr Word BreakStart=110,BreakChild=111,BreakPose=112,BreakGeometry=113;
inline std::atomic<bool> breakSelected{false};
struct BreakScope {Word ship=0,visual=0,epoch=0;};
inline thread_local BreakScope breakScope;
inline thread_local Word drawingPiece=0;
struct BreakPiece {Word pointer=0,ship=0,visual=0,epoch=0,index=0,samples=0,updates=0;bool retired=false;};
inline std::array<BreakPiece,128> breakPieces{};
inline SRWLOCK breakLock=SRWLOCK_INIT;
inline thread_local BreakPiece submittingPiece{};
struct BreakSnapshot {
 std::atomic<unsigned> state{0};
 sfc_m1::LiveMeshPacket mesh;
 sfc_m1::LiveTextureReferences refs;
 sfc_break::Layout layout{};
 Word index=0;
};
// Four diagnostic snapshots, independent of production scene capacity.
inline std::array<BreakSnapshot,4> breakSnapshots;
inline std::atomic<Word> breakPoseMask{0};
inline std::atomic<Word> breakRetiredMask{0};
inline bool breakCaptureComplete(){
 Word expected=0,finished=0;
 for(auto& s:breakSnapshots)if(s.state.load(std::memory_order_acquire)==3){
  expected=s.layout.pieceCount;
  if(s.index<4)finished|=1u<<s.index;
 }
 return expected&&expected<=4&&finished==((1u<<expected)-1)&&
        (breakPoseMask.load(std::memory_order_acquire)&finished)==finished&&
        (breakRetiredMask.load(std::memory_order_acquire)&finished)==finished;
}
inline void breakState(const BreakPiece& c,Word kind,Word sample){
 auto r=record(static_cast<Kind>(kind),c.ship,c.visual);r.mesh=c.pointer;
 r.data[0]=c.epoch;r.data[1]=c.index;r.data[2]=c.retired?1:0;r.data[3]=sample;
 bool ok=true;
 if(!read(c.pointer+0xA4,r.data.data()+4,68)||
    !read(c.pointer+0x34,r.data.data()+21,12)||
    !read(c.pointer+0x144,r.data.data()+24,12)||
    !read(c.pointer+0x150,r.data.data()+27,8))ok=false;
 r.data[29]=word(c.pointer+0x24,ok)&255;r.data[30]=word(c.pointer+0x20,ok);
 if(!ok){r.flags|=ReadBad;++faults;}emit(r);
}
inline bool breakWriteSnapshots(const std::wstring& trace){
 const auto slash=trace.find_last_of(L"\\/");
 if(slash==std::wstring::npos)return false;
 for(unsigned i=0;i<breakSnapshots.size();++i){auto& s=breakSnapshots[i];
  if(s.state.load(std::memory_order_acquire)!=2)continue;
  const auto base=trace.substr(0,slash)+L"/break-piece-"+std::to_wstring(i);
  std::ofstream mesh(base+L".bin",std::ios::binary),refs(base+L".json");
  const bool ok=s.mesh.write(mesh)&&sfc_m1::write_texture_references(refs,s.refs,s.mesh,false);
  mesh.flush();refs.flush();
  if(!ok||!mesh.good()||!refs.good()){s.state.store(4);return false;}
  s.state.store(3,std::memory_order_release);
 }
 return true;
}

inline bool bindBreakTargets(){
 const struct {Word address;const char* bytes;} checks[]={
  {0x0041455B,"\xB8\x66\xBA\x75\x00\xE8"},
  {0x0041B657,"\xB8\x2C\xBD\x75\x00\xE8"},
  {0x0041B900,"\x55\x8B\xEC\x51\x51\x53"},
  {0x0042FE7E,"\x8B\x81\x60\x01\x00\x00"},
  {0x006AC5A0,"\x83\xEC\x08\x53\x56\x8B"},
  {0x0041BA0F,"\x55\x8B\xEC\x83\xEC\x24"},
  {0x0041B8B4,"\xB8\x40\xBD\x75\x00\xE8"}};
 for(const auto& c:checks){char b[6]{};if(!read(c.address,b,sizeof(b))||memcmp(b,c.bytes,sizeof(b)))return false;}
 breakFactory=reinterpret_cast<BreakFactory>(0x0041455B);
 breakChild=reinterpret_cast<Four>(0x0041B657);
 breakDraw=reinterpret_cast<BreakDraw>(0x0041B900);
 breakVisual=reinterpret_cast<BreakVisual>(0x0042FE7E);
 breakWrapper=reinterpret_cast<BreakWrapper>(0x006AC5A0);
 breakUpdate=reinterpret_cast<BreakUpdate>(0x0041BA0F);
 breakRetire=reinterpret_cast<Zero>(0x0041B8B4);
 for(auto& snapshot:breakSnapshots){
  snapshot.mesh.positions={};snapshot.mesh.polygons={};snapshot.mesh.corners={};snapshot.refs={};
 }
 return true;
}
inline Word __cdecl onBreakFactory(Word ship,Word visual){
 LastError last;Active activeCall;
 const auto caller=ptr(_ReturnAddress());bool ok=true;
 const auto old=breakScope;
 struct Restore {BreakScope value;~Restore(){breakScope=value;}} restore{old};
 breakScope={};
 if(observing&&gated&&caller==0x00416754&&visual&&word(ship+0x8C,ok)==visual&&word(visual,ok)==visualVt&&ok){
  const auto owner=entry(owners,ship);
  if(owner.epoch&&!breakSelected.exchange(true)){
   breakScope={ship,visual,owner.epoch};
   auto r=record(static_cast<Kind>(BreakStart),ship,visual);r.caller=caller;r.data[0]=owner.epoch;
   r.data[1]=entry(visuals,visual).epoch;emit(r);
  }
 }
 last.enter();const auto result=breakFactory(ship,visual);last.leave();return result;
}
inline Word __fastcall onBreakChild(void* p,void*,Word visual,Word index,Word initial,Word mode){
 LastError last;Active activeCall;const auto caller=ptr(_ReturnAddress());
 last.enter();const auto result=breakChild(p,visual,index,initial,mode);last.leave();
 if(!observing||!breakSelected)return result;
 if(!TryAcquireSRWLockExclusive(&breakLock)){++busy;uncertain=true;return result;}
 BreakPiece* free=nullptr;
 for(auto& piece:breakPieces){
  if(piece.pointer==ptr(p)){piece={};free=&piece;break;}
  if(!piece.pointer&&!free)free=&piece;
 }
 const auto context=breakScope;
 if(caller==0x0041BAFB&&context.ship&&context.visual==visual&&result==ptr(p)){
  if(free)*free={ptr(p),context.ship,visual,context.epoch,index,0};
  else uncertain=true;
  auto r=record(static_cast<Kind>(BreakChild),context.ship,visual);
  r.mesh=ptr(p);r.caller=caller;r.data[0]=context.epoch;r.data[1]=index;r.data[2]=mode;
  if(!free)r.flags|=Overflow;
  emit(r);
 }
 ReleaseSRWLockExclusive(&breakLock);
 return result;
}
inline void __fastcall onBreakDraw(void* p,void*,Word manager){
 LastError last;Active activeCall;
 struct Restore {Word value;~Restore(){drawingPiece=value;}} restore{drawingPiece};
 drawingPiece=observing&&breakSelected?ptr(p):0;
 last.enter();breakDraw(p,manager);last.leave();
}
inline void __fastcall onBreakVisual(void* p,void*,Word manager,Word index,Word mode){
 LastError last;Active activeCall;const auto caller=ptr(_ReturnAddress());
 struct Restore{BreakPiece old;~Restore(){submittingPiece=old;}}restore{submittingPiece};
 submittingPiece={};
 if(observing&&drawingPiece&&caller==0x0041B9FE){
  BreakPiece match{};
  if(TryAcquireSRWLockExclusive(&breakLock)){
   for(auto& piece:breakPieces)if(piece.pointer==drawingPiece){
    if(!piece.retired&&piece.visual==ptr(p)&&piece.index==index){
     submittingPiece=piece;
     if(piece.samples<8){++piece.samples;match=piece;}
    }
    break;
   }
   ReleaseSRWLockExclusive(&breakLock);
  }else{++busy;uncertain=true;}
  if(match.pointer){
   auto r=record(static_cast<Kind>(BreakPose),match.ship,ptr(p));r.mesh=match.pointer;r.caller=caller;
   r.data[0]=match.epoch;r.data[1]=index;r.data[2]=mode;r.data[3]=match.samples;
   if(!manager||manager>UINT32_MAX-0x738||!read(manager+0x6F4,r.data.data()+4,68)||
      !read(manager+0x6B0,r.data.data()+21,68)){r.flags|=ReadBad;++faults;}
   emit(r);
   breakState(match,114,match.samples);
   auto predicted=record(static_cast<Kind>(118),match.ship,match.visual);
   predicted.mesh=match.pointer;predicted.data[0]=match.epoch;
   predicted.data[1]=index;predicted.data[2]=match.samples;
   sfc_break::Pose pose{};
   if(sfc_break::simulation_pose(match.pointer,pose,read)){
    std::memcpy(predicted.data.data()+4,pose.data(),64);
    bool close=true;
    for(unsigned i=0;i<16;++i){
     const auto actual=std::bit_cast<float>(r.data[4+i]);
     if(!std::isfinite(actual)||std::fabs(double(pose[i])-actual)>
        1e-5*(std::fmax)(1.,std::fabs(double(actual))))close=false;
    }
    predicted.data[3]=close?1:0;
    if(!close)predicted.flags|=Mismatch;
   }else predicted.flags|=ReadBad;
   emit(predicted);
   auto camera=record(static_cast<Kind>(117),match.ship,match.visual);
   camera.mesh=match.pointer;camera.token=match.samples;
   if(!manager||manager>UINT32_MAX-0x774||
      !read(manager+0x628,camera.data.data(),68)||
      !read(manager+0x55c,camera.data.data()+17,68)||
      !read(manager+0x75c,camera.data.data()+34,24)){
    camera.flags|=ReadBad;++faults;
   }
   emit(camera);
   if(match.samples==8&&index<4)breakPoseMask.fetch_or(1u<<index,std::memory_order_release);
  }
 }
 last.enter();breakVisual(p,manager,index,mode);last.leave();
}
inline void __fastcall onBreakUpdate(void* p,void*){
 LastError last;Active activeCall;
 last.enter();breakUpdate(p);last.leave();
 if(!observing||!breakSelected)return;
 BreakPiece match{};
 if(TryAcquireSRWLockExclusive(&breakLock)){
  for(auto& piece:breakPieces)if(piece.pointer==ptr(p)&&!piece.retired){
   if(piece.updates<512){++piece.updates;match=piece;}break;
  }
  ReleaseSRWLockExclusive(&breakLock);
 }else{++busy;uncertain=true;}
 if(match.pointer)breakState(match,115,match.updates);
}
inline Word __fastcall onBreakRetire(void* p,void*){
 LastError last;Active activeCall;BreakPiece match{};
 if(observing&&breakSelected){
  if(TryAcquireSRWLockExclusive(&breakLock)){
   for(auto& piece:breakPieces)if(piece.pointer==ptr(p)&&!piece.retired){
    piece.retired=true;match=piece;break;
   }
   ReleaseSRWLockExclusive(&breakLock);
  }else{++busy;uncertain=true;}
  if(match.pointer){
   auto r=record(static_cast<Kind>(116),match.ship,match.visual);r.mesh=match.pointer;
   r.data[0]=match.epoch;r.data[1]=match.index;emit(r);
   if(match.index<4)breakRetiredMask.fetch_or(1u<<match.index,std::memory_order_release);
  }
 }
 last.enter();const auto result=breakRetire(p);last.leave();return result;
}
inline Word __fastcall onBreakWrapper(void* p,void*,Word count,Word list,Word mode){
 LastError last;Active activeCall;const auto c=submittingPiece;
 if(observing&&c.pointer&&ptr(_ReturnAddress())==0x0042EA92&&mode==1){
  const auto reader=[](Word address,void* output,size_t size){
   if(!address||size>UINT32_MAX-address)return false;
   auto* target=static_cast<BYTE*>(output);
   for(size_t offset=0;offset<size;){
    const auto n=(size-offset)>4096?4096:size-offset;
    if(!read(address+static_cast<Word>(offset),target+offset,n))return false;
    offset+=n;
   }
   return true;
  };
  unsigned slot=static_cast<unsigned>(breakSnapshots.size());bool seen=false;
  for(unsigned i=0;i<breakSnapshots.size();++i){
   auto& s=breakSnapshots[i];const auto state=s.state.load(std::memory_order_acquire);
   if(state==1){seen=true;break;} // another callback owns the immutable snapshot
   if(state&&s.mesh.header[sfc_m1::MeshShip]==c.pointer){seen=true;break;}
   if(!state&&slot==breakSnapshots.size())slot=i;
  }
  if(!seen&&slot<breakSnapshots.size()){
   auto& s=breakSnapshots[slot];unsigned empty=0;
   if(s.state.compare_exchange_strong(empty,1)){
    s.index=c.index;sfc_break::Range part{};
    const auto valid=[&](){
     bool ok=true;return word(c.pointer,ok)==0x007972B4&&
      word(c.pointer+0x9c,ok)==c.visual&&word(c.pointer+0xa0,ok)==c.index&&ok;
    };
    auto result=sfc_m1::MeshStatus::Identity;
    if(sfc_break::layout(c.visual,s.layout,reader)&&sfc_break::range(s.layout,c.index,part)&&
       part.count==count&&part.list==list)
     result=sfc_break::capture(s.mesh,s.layout,c.index,c.epoch,c.pointer,ptr(p),reader,valid);
    if(result==sfc_m1::MeshStatus::Complete)
     sfc_m1::capture_texture_references(s.refs,s.mesh,reader,valid);
    auto r=record(static_cast<Kind>(BreakGeometry),c.ship,c.visual);
    r.mesh=c.pointer;r.data[0]=c.epoch;r.data[1]=c.index;r.data[2]=slot;
    r.data[3]=static_cast<Word>(result);r.data[4]=s.refs.status;
    r.data[5]=part.first;r.data[6]=part.count;r.data[7]=s.layout.pieceCount;
    if(result!=sfc_m1::MeshStatus::Complete||s.refs.status!=1)r.flags|=ReadBad;
    emit(r);
    s.mesh.header[sfc_m1::MeshShip]=c.pointer;
    s.state.store(r.flags&ReadBad?4:2,std::memory_order_release);
   }
  }
 }
 last.enter();const auto result=breakWrapper(p,count,list,mode);last.leave();return result;
}

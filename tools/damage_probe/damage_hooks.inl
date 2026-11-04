// Included inside early_model only in the separate SFC_DAMAGE_PROBE build.
// No original arguments or memory are modified. All native pointers die here.
enum DamageKind:Word {DamageModel=100,DamagePass,DamageMapping,DamageModelEnd,DamageResources};
struct DamageContext {Word owner=0,visual=0,model=0,manager=0,source=0,a=0,b=0,ownerEpoch=0,assetEpoch=0;uint64_t token=0;};
inline thread_local DamageContext damageContext;
inline std::atomic<uint64_t> damageTokens{0};
inline SRWLOCK damageLock=SRWLOCK_INIT;
struct DamageSeen {std::array<Word,10> key{};std::array<Word,32> values{};};
inline std::array<DamageSeen,2048> damageSeen{};
inline std::atomic<unsigned> damageOmitted{0},damageBusy{0};
struct DamageSnapshot {
 std::atomic<unsigned> state{0}; // 0 free,1 callback writing,2 immutable ready,3 written,4 failed
 std::array<Word,32> header{};
 std::array<std::array<Word,3>,65536> positions{};
 std::array<std::array<Word,7>,8192> polygons{};
 std::array<std::array<Word,7>,32768> corners{};
};
inline std::array<DamageSnapshot,4> damageSnapshots{};
inline bool damageRead(Word p,void* target,size_t size){
 if(!p||size>UINT32_MAX-p)return false;auto* out=static_cast<BYTE*>(target);
 for(size_t offset=0;offset<size;){const size_t n=(size-offset)>4096?4096:size-offset;if(!read(p+static_cast<Word>(offset),out+offset,n))return false;offset+=n;}return true;
}
inline Word damageHash(Word h,const void* p,size_t n){const auto* b=static_cast<const BYTE*>(p);for(size_t i=0;i<n;++i){h^=b[i];h*=16777619u;}return h;}
inline Record damageRecord(Word kind){const auto c=damageContext;auto r=record(static_cast<Kind>(kind),c.owner,c.visual);r.mesh=c.model;r.token=c.token;r.data[0]=c.ownerEpoch;r.data[1]=c.assetEpoch;return r;}
inline bool damageChanged(Word kind,const Record& r){
 if(!TryAcquireSRWLockExclusive(&damageLock)){++damageBusy;return false;}
 const std::array<Word,10> key{kind,r.owner,r.visual,r.mesh,r.data[0],r.data[1],r.caller,0,0,0};
 bool changed=false;const auto base=((r.owner>>4)^(r.mesh>>4)^kind)%damageSeen.size();
 for(unsigned i=0;i<64;++i){auto& s=damageSeen[(base+i)%damageSeen.size()];if(s.key==key||!s.key[0]){
  std::array<Word,32> values{};for(unsigned j=0;j<32;++j)values[j]=r.data[j+2];
  changed=s.key!=key||s.values!=values;s.key=key;s.values=values;ReleaseSRWLockExclusive(&damageLock);return changed;}}
 ++damageOmitted;ReleaseSRWLockExclusive(&damageLock);return false;
}
inline Word damageSnapshot(const Record& pass,Word list,Word count){
 const auto c=damageContext;unsigned slot=4;
 if(!TryAcquireSRWLockExclusive(&damageLock)){++damageBusy;return 0;}
 for(unsigned i=0;i<4;++i){auto& s=damageSnapshots[i];const auto state=s.state.load(std::memory_order_acquire);
  if(state&&s.header[4]==c.visual&&s.header[5]==c.assetEpoch&&s.header[6]==c.model&&s.header[7]==list){ReleaseSRWLockExclusive(&damageLock);return i+1;}
  if(!state&&slot==4)slot=i;
 }
 if(slot==4){++damageOmitted;ReleaseSRWLockExclusive(&damageLock);return 0;}
 auto& s=damageSnapshots[slot];s.header={};s.header[4]=c.visual;s.header[5]=c.assetEpoch;s.header[6]=c.model;s.header[7]=list;s.state.store(1,std::memory_order_release);ReleaseSRWLockExclusive(&damageLock);
 bool ok=true;const Word positions=word(c.model+8,ok),base=word(c.model+0xC,ok);
 auto& h=s.header;h[0]=0x444D5031;h[1]=1;h[8]=c.owner;h[9]=c.ownerEpoch;h[10]=positions;h[11]=count;h[13]=c.a;h[14]=c.b;h[15]=pass.data[13];h[16]=pass.data[15];h[17]=pass.data[5];h[18]=c.manager;h[19]=c.source;
 if(!positions||positions>65536||!count||count>8192)ok=false;
 if(ok)ok=damageRead(base,s.positions.data(),positions*12);
 for(Word i=0;ok&&i<count;++i){const Word p=word(list+i*4,ok);auto& poly=s.polygons[i];ok=ok&&read(p,poly.data(),28);if(!ok)break;
  const Word corners=poly[0],nativeCorners=poly[6];if(corners<3||corners>8||poly[1]!=0||corners>32768-h[12]){ok=false;break;}
  poly[6]=h[12];ok=damageRead(nativeCorners,s.corners.data()+h[12],corners*28);
  for(Word j=0;ok&&j<corners;++j){const auto& row=s.corners[h[12]+j];if((row[0]&65535)>=positions){ok=false;break;}
   for(unsigned k=1;k<=5;++k)if((row[k]&0x7F800000)==0x7F800000)ok=false;}
  h[12]+=corners;
 }
 for(Word i=0;ok&&i<positions;++i)for(auto bits:s.positions[i])if((bits&0x7F800000)==0x7F800000)ok=false;
 if(word(c.model+0x18,ok)!=list||word(c.model+0x10,ok)!=count||word(c.model+0xC,ok)!=base)ok=false;
 h[2]=128+positions*12+count*28+h[12]*28;
 if(!ok||h[2]>2*1024*1024){s.state.store(4,std::memory_order_release);}else{
  Word hash=damageHash(2166136261u,h.data(),128);hash=damageHash(hash,s.positions.data(),positions*12);hash=damageHash(hash,s.polygons.data(),count*28);h[3]=damageHash(hash,s.corners.data(),h[12]*28);s.state.store(2,std::memory_order_release);
 }
 auto r=damageRecord(DamageMapping);r.data[2]=slot+1;r.data[3]=ok?1:0;r.data[4]=positions;r.data[5]=count;r.data[6]=h[12];emit(r);return slot+1;
}
inline Word __fastcall onDamageWrapper(void* p,void*,Word count,Word list,Word mode){
 LastError last;Active activeCall;const auto c=damageContext;const Word caller=ptr(_ReturnAddress());
 if(observing&&c.owner&&c.manager==ptr(p)){
  bool ok=true;const Word primary=word(c.model+0x14,ok),secondary=word(c.model+0x18,ok),expected=word(c.model+0x10,ok);
  const bool second=(fixtureMode?list==secondary:caller==0x0042E626);
  const bool first=(fixtureMode?list==primary:caller==0x0042E55D);
  if(ok&&(first||second)&&count==expected&&list==(second?secondary:primary)&&mode==1){
   auto r=damageRecord(DamagePass);r.caller=second?0x0042E626:0x0042E55D;r.data[2]=c.a;r.data[3]=c.b;r.data[4]=count;r.data[5]=list;r.data[6]=mode;
   const Word material=word(c.manager+0x558,ok);r.data[7]=material;
   if(!read(material,r.data.data()+8,36))ok=false;
   // Opaque native manager state words, not asserted D3D blend factors.
   if(!read(c.manager+0x1EC8,r.data.data()+17,16))ok=false;
   r.data[21]=secondary;r.data[22]=word(c.manager+0x554,ok);
   if(!ok){r.flags|=ReadBad;++faults;}if(damageChanged(DamagePass,r))emit(r);
   if(second&&!fixtureMode){auto tables=damageRecord(DamageResources);tables.caller=0x0042E626;
    if(!read(0x008F57F8,tables.data.data()+2,18*4)){tables.flags|=ReadBad;++faults;}if(damageChanged(DamageResources,tables))emit(tables);}
   if(second&&ok)damageSnapshot(r,list,count);
  }
 }
 last.enter();const auto result=damageWrapper(p,count,list,mode);last.leave();return result;
}
struct DamageScope {
 DamageContext previous=damageContext;bool qualified=false;Word before=0;
 DamageScope(void* p,Word manager,Word source,Word a,Word b,Word caller){
  damageContext={};if(!observing)return;const auto c=stack.current();bool ok=true;
  if(c.role!=FirstDraw||!mainline(fixtureMode?expectedCaller:caller,expectedCaller,c.visual,source,word(c.visual+0x158,ok))||word(ptr(p),ok)!=meshVt||word(manager,ok)!=0x007B8D4C||!ok)return;
  const auto owner=entry(owners,c.owner),asset=entry(visuals,c.visual);if(!owner.qualified||!asset.qualified)return;
  damageContext={c.owner,c.visual,ptr(p),manager,source,a,b,owner.epoch,asset.epoch,++damageTokens};qualified=true;
  auto r=damageRecord(DamageModel);r.caller=fixtureMode?expectedCaller:caller;r.data[2]=a;r.data[3]=b;r.data[4]=manager;r.data[5]=source;r.data[6]=word(ptr(p)+0x14,ok);r.data[7]=before=word(ptr(p)+0x18,ok);r.data[8]=word(ptr(p)+0x10,ok);
  if(!ok){r.flags|=ReadBad;++faults;}if(damageChanged(DamageModel,r))emit(r);
 }
 ~DamageScope(){if(qualified){bool ok=true;const Word after=word(damageContext.model+0x18,ok);if(after!=before){auto r=damageRecord(DamageModelEnd);r.data[2]=before;r.data[3]=after;if(!ok)r.flags|=ReadBad;emit(r);}}damageContext=previous;}
};
inline bool damageWriteSnapshots(const std::wstring& trace){
 for(unsigned i=0;i<4;++i){auto& s=damageSnapshots[i];if(s.state.load(std::memory_order_acquire)!=2)continue;
  const auto path=trace+L".mapping-"+std::to_wstring(i+1)+L".bin";
  const auto f=CreateFileW(path.c_str(),GENERIC_WRITE,FILE_SHARE_READ,nullptr,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,nullptr);if(f==INVALID_HANDLE_VALUE)return false;
  DWORD written=0;const auto block=[&](const void* p,Word n){return WriteFile(f,p,n,&written,nullptr)&&written==n;};
  const auto& h=s.header;const bool ok=block(h.data(),128)&&block(s.positions.data(),h[10]*12)&&block(s.polygons.data(),h[11]*28)&&block(s.corners.data(),h[12]*28);CloseHandle(f);if(!ok)return false;s.state.store(3,std::memory_order_release);
 }
 return true;
}

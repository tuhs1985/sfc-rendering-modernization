// Opt-in discovery variant only; no Remix types or writes into game memory.
#pragma once
#include <windows.h>
#include <fstream>
#include "native_light_snapshot.h"
namespace sfc_native_lights {
struct Observer {
 volatile LONG busy=0,active=0;
 std::array<Snapshot,8> queue{};Snapshot a{},b{};
 std::array<Word,4> session{};
 std::array<Word,2> owners{},last{};std::array<bool,2> sampled{};
 Word head=0,tail=0,queued=0,sequence=0,written=0,dropped=0,rejected=0;
 bool ioFailed=false;
 bool tuning=false;
 void start(const Word* words){
  for(unsigned i=0;i<4;++i)session[i]=words[i];
  queue={};a={};b={};owners={};last={};sampled={};
  head=tail=queued=sequence=written=dropped=rejected=0;ioFailed=false;
  InterlockedExchange(&active,1);
 }
 template<class Identity,class Read,class Valid> void observe(const Identity& id,Read read,Valid valid){
  if(!InterlockedCompareExchange(&active,0,0)||id.elapsed>(tuning?1800000u:90000u))return;
  if(InterlockedCompareExchange(&busy,1,0)!=0)return;
  struct Unlock{volatile LONG& lock;~Unlock(){InterlockedExchange(&lock,0);}} unlock{busy};
  unsigned i=0;for(;i<2;++i)if(owners[i]==id.owner||!owners[i])break;
  if(i==2||!id.owner||sequence>=(tuning?18000u:900u))return;
  if(sampled[i]&&id.elapsed-last[i]<200)return;
  owners[i]=id.owner;sampled[i]=true;last[i]=id.elapsed;
  if(queued==queue.size()){++dropped;return;}
  std::array<Word,16> meta={Magic,Version,sizeof(Snapshot),sequence+1,
   session[0],session[1],session[2],session[3],id.owner,id.frame,id.elapsed,
   id.manager,id.model,id.source,id.thread,0};
  if(!capture(a,b,meta,read,valid)){++rejected;return;}
  queue[tail]=a;tail=(tail+1)%8;++queued;++sequence;
 }
 bool take(Snapshot& out){
  if(InterlockedCompareExchange(&busy,1,0)!=0)return false;
  const bool ok=queued!=0;
  if(ok){out=queue[head];head=(head+1)%8;--queued;}
  InterlockedExchange(&busy,0);return ok;
 }
 void drain(std::ofstream& file){
  Snapshot record{};
  for(unsigned i=0;i<8&&take(record);++i){
   if(ioFailed)continue;
   file.write(reinterpret_cast<const char*>(&record),sizeof(record));
   if(!file){ioFailed=true;InterlockedExchange(&active,0);}else ++written;
  }
 }
};
}

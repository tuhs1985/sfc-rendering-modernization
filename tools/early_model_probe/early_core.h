#pragma once
#include <array>
#include <cstdint>
namespace early_model {
using Word=uint32_t;
constexpr Word Magic=0x454D4131,Hard=16*1024*1024,Capacity=2048;
enum Kind:Word {Request=80,RequestEnd,Load,LoadEnd,Parse,ParseEnd,Attach,FirstDraw,OwnerBorn,OwnerRetire,VisualRetire,Gate,Exception,Statistics,Stopped};
enum Flags:Word {NameBad=1,ReadBad=2,Unsupported=4,Uncertain=8,Overflow=16,OriginalException=32,MissingIdentity=64,Mismatch=128,Fixture=256};
struct Record {
 uint64_t sequence=0,qpc=0,token=0,parent=0;
 Word kind=0,thread=0,owner=0,visual=0,mesh=0,flags=0,depth=0,caller=0;
 std::array<Word,40> data{};std::array<char,256> name{};std::array<Word,8> reserved{};
};
static_assert(sizeof(Record)==512);
struct Entry {Word pointer=0,epoch=0;bool alive=false,qualified=false;std::array<Word,4> first{};};
// Fixed open-addressed table. Retired slots keep their key to detect reuse.
struct Book {
 std::array<Entry,4096> rows{};Word serial=0;
 Entry* find(Word p,bool insert=false){
  if(!p)return nullptr;const auto base=(p>>4)%rows.size();
  for(unsigned i=0;i<64;++i){auto& r=rows[(base+i)%rows.size()];if(r.pointer==p)return &r;if(!r.pointer){if(insert){r.pointer=p;return &r;}return nullptr;}}
  return nullptr;
 }
 Entry birth(Word p,bool qualified){auto* r=find(p,true);if(!r||serial==UINT32_MAX)return {};*r={p,++serial,true,qualified,{}};return *r;}
 Entry current(Word p) {auto* r=find(p);return r&&r->alive?*r:Entry{};}
 Entry retire(Word p){auto* r=find(p);if(!r||!r->alive)return {};auto old=*r;r->alive=false;r->first={};return old;}
 void rebound(Word p){auto* r=find(p);if(r&&r->alive)r->first={};}
 bool first(Word p,Word epoch,Word mesh){auto* r=find(p);if(!r||!r->alive||r->epoch!=epoch||!mesh)return false;for(auto m:r->first)if(m==mesh)return false;for(auto& m:r->first)if(!m){m=mesh;return true;}return false;}
};
struct Context {Word owner=0,visual=0;uint64_t token=0;Word role=0,parses=0;};
struct Stack {
 std::array<Context,8> rows{};unsigned depth=0,excess=0;
 bool push(Context c){if(excess||depth==rows.size()){++excess;return false;}rows[depth++]=c;return true;}
 Context current()const{return excess||!depth?Context{}:rows[depth-1];}
 void parsed(){if(excess)return;for(unsigned i=depth;i>0;--i)if(rows[i-1].role==Load){++rows[i-1].parses;break;}}
 unsigned parses()const{return excess||!depth?0:rows[depth-1].parses;}
 void pop(){if(excess)--excess;else if(depth)--depth;}
};
inline bool bounds(uint64_t n,uint64_t extra){return n<=Hard&&extra<=Hard-n;}
inline bool mainline(Word actual,Word expected,Word visual,Word source,Word recordedSource){return actual==expected&&visual&&source&&source==recordedSource;}
}

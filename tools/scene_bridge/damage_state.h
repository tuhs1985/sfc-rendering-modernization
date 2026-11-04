// Source damage semantics. No renderer, SDK, GPU handle or image conversion.
#pragma once
#include <array>
#include <cmath>
#include <cstdint>
#include <cstring>
namespace sfc_damage {
using Word=std::uint32_t;
constexpr Word Version=1;
struct State {Word owner=0,revision=0,scalar=0,family=0,qualified=0;};
static_assert(sizeof(State)==20);
inline float value(Word bits){float f=0;std::memcpy(&f,&bits,4);return f;}
inline Word bits(float f){Word b=0;std::memcpy(&b,&f,4);return b;}
inline int severity(Word scalar){const float f=value(scalar);if(!std::isfinite(f))return -2;
 if(f<.125f)return -1;if(f>=.625f)return 2;return static_cast<int>(double(f)*4.+.5)-1;}
inline bool valid(const State& s){return s.owner&&s.revision&&s.qualified==1&&s.family<3&&severity(s.scalar)>=-1;}
// Read-only equivalent of the simple +0x88 structure accessor used by the
// pinned ship renderer. Reject complex code; never execute an unqualified call.
template<class Read>bool structure(Word object,Word& out,Read read){
 Word vt=0,fn=0;if(!object||!read(object,&vt,4)||!read(vt+0x88,&fn,4)||fn<0x00400000||fn>=0x00800000)return false;
 std::array<unsigned char,8> code{};if(!read(fn,code.data(),8))return false;
 Word offset=0;bool indirect=false;
 // Default simulation constructor00448235 installs0079D530. Its +88 getter
 // has lazy diagnostic-string registration, then ALWAYS returns this+8AC.
 // Read its pinned identity/tail; do not execute registration or reject it as
 // a complex statistics calculation. Alternate simulation uses the simple LEA.
 constexpr std::array<unsigned char,8> prefix{0xF6,0x05,0x2B,0x19,0xC8,0,1,0x56};
 constexpr std::array<unsigned char,8> tail{0x8D,0x86,0xAC,0x08,0,0,0x5E,0xC3};
 if(vt==0x0079D530&&fn==0x00448B6E&&code==prefix){
  std::array<unsigned char,8> actual{};if(!read(0x00448B9B,actual.data(),8)||actual!=tail)return false;offset=0x8AC;
 }
 else if((code[0]==0x8D||code[0]==0x8B)&&code[1]==0x81&&code[6]==0xC3){std::memcpy(&offset,code.data()+2,4);indirect=code[0]==0x8B;}
 else if((code[0]==0x8D||code[0]==0x8B)&&code[1]==0x41&&code[3]==0xC3&&code[2]<0x80){offset=code[2];indirect=code[0]==0x8B;}
 else return false;
 if(offset>0x100000||object>UINT32_MAX-offset)return false;out=object+offset;
 return !indirect||read(out,&out,4);
}
// Same arithmetic as 00416344..0041645D: store the float ratio first, then
// subtract it from1. This is not a guessed percentage or a hit event.
template<class Read>bool source(Word ship,Word& scalar,Word& family,Read read){
 Word category=0,simulation=0,stats=0;if(!read(ship+0x870,&category,4))return false;
 family=category>13&&category<=18?2:category==6?1:0;
 if(category>=24){scalar=0;return true;}
 if(!read(ship+0xAD4,&simulation,4)||!structure(simulation,stats,read))return false;
 std::array<float,3> a{},b{};
 if(!read(stats+0x18,a.data(),12)||!read(stats+0x18,b.data(),12)||a!=b)return false;
 for(float f:a)if(!std::isfinite(f))return false;
 const double denominator=double(a[1])-a[2];if(!(denominator>0))return false;
 const float ratio=static_cast<float>((double(a[0])-a[2])/denominator);
 scalar=bits(static_cast<float>(1.-double(ratio)));return severity(scalar)>=-1;
}
}

// Renderer-neutral read-only core. Not yet connected to the production hook.
#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
namespace sfc_native_lights {
using Word=std::uint32_t;
constexpr Word Magic=0x54494c4e,Version=1;
struct Snapshot {
 // magic,version,bytes,sequence,session[4],owner,frame,elapsed,manager,
 // model,source,thread,reserved. Manager is process-local evidence only.
 std::array<Word,16> header{};
 std::array<Word,17> supplied{},view{};
 std::array<Word,1024> records{};
 std::array<std::uint8_t,64> enables{};
 std::array<Word,192> localPoints{},localDirections{};
 std::array<Word,64> reciprocal{};
 Word gate=0;
};
static_assert(sizeof(Snapshot)==6156);
static_assert(offsetof(Snapshot,records)==200&&offsetof(Snapshot,enables)==4296&&
 offsetof(Snapshot,localPoints)==4360&&offsetof(Snapshot,localDirections)==5128&&
 offsetof(Snapshot,reciprocal)==5896&&offsetof(Snapshot,gate)==6152);
template<class Read> bool readBank(Word manager,Snapshot& s,Read read){
 if(!manager||manager>0xffffe000u)return false;
 Word vtable=0;
 return read(manager,&vtable,4)&&vtable==0x007B8D4C&&
  read(manager+0x6f4,s.supplied.data(),68)&&read(manager+0x628,s.view.data(),68)&&
  read(manager+0x778,s.records.data(),4096)&&read(manager+0x1778,s.enables.data(),64)&&
  read(manager+0x17b8,s.localPoints.data(),768)&&read(manager+0x1ab8,s.localDirections.data(),768)&&
  read(manager+0x1db8,s.reciprocal.data(),256)&&read(manager+0x1eb8,&s.gate,1);
}
// Caller supplies both fixed scratch records,qualified owner/frame metadata,
// try-lock/sampling/queue policy and existing live-validity check. No allocation,
// waits,file/process access or SDK types. False drops this observation only.
template<class Read,class Valid>
bool capture(Snapshot& a,Snapshot& b,const std::array<Word,16>& metadata,Read read,Valid valid){
 if(metadata[0]!=Magic||metadata[1]!=Version||metadata[2]!=sizeof(Snapshot)||
    !metadata[3]||!(metadata[4]|metadata[5]|metadata[6]|metadata[7])||
    !metadata[8]||!metadata[9]||!metadata[12]||!metadata[13]||!metadata[14]||metadata[15])return false;
 a={};b={};a.header=b.header=metadata;
 return valid()&&readBank(metadata[11],a,read)&&readBank(metadata[11],b,read)&&
  std::memcmp(&a,&b,sizeof(Snapshot))==0&&valid();
}
}

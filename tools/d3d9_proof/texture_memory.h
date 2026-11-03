// External renderer workers only. Immutable supervisor bytes, no disk fallback
// when enabled. GPU ownership and upload backing remain Renderer responsibilities.
#pragma once
#include "multi_scene_wire.h"
#include <cstdio>
namespace texture_memory {
constexpr DWORD HeaderBytes=2176,Limit=128*1024*1024;
inline bool requested(){wchar_t flag[2]{};return GetEnvironmentVariableW(L"SFC_D3D9_TEXTURE_MEMORY",flag,2)==1&&flag[0]==L'1';}
inline std::array<DWORD,4> words(const DWORD* session,DWORD id){
 std::array<DWORD,4> value{};memcpy(value.data(),session,16);value[0]^=0x54585431;value[3]^=id;return value;
}
inline std::wstring name(const DWORD* session,DWORD id){const auto value=words(session,id);wchar_t text[64]{};
 swprintf_s(text,L"Local\\SFCTextures_%08x%08x%08x%08x",value[0],value[1],value[2],value[3]);return text;
}
struct Payload {std::vector<BYTE> geometry;std::vector<std::vector<BYTE>> textures;};
inline Payload receive_asset(const DWORD* session,const multi_scene::Asset& asset,DWORD count=0){
 require(count<=256&&multi_scene::valid(asset),"asset memory catalog/count");
 struct Handle {HANDLE h;~Handle(){if(h)CloseHandle(h);}} handle{OpenFileMappingW(FILE_MAP_READ,FALSE,name(session,asset.id).c_str())};
 require(handle.h!=nullptr,"texture memory missing;no texture-file fallback");
 struct View {const BYTE* p;~View(){if(p)UnmapViewOfFile(p);}} header{static_cast<const BYTE*>(MapViewOfFile(handle.h,FILE_MAP_READ,0,0,HeaderBytes))};
 require(header.p!=nullptr,"texture memory header missing");
 const auto readyBefore=*reinterpret_cast<const volatile LONG*>(header.p+124);MemoryBarrier();
 require(readyBefore==1,"texture memory incomplete publication");
 std::array<BYTE,HeaderBytes> seal{};memcpy(seal.data(),header.p,HeaderBytes);
 DWORD h[8]{};memcpy(h,seal.data(),32);const auto expected=words(session,asset.id);
 require(h[0]==0x31424c53&&h[1]==2&&h[2]==HeaderBytes+asset.geometry_bytes+asset.image_bytes&&h[3]==0&&
  !memcmp(h+4,expected.data(),16)&&h[2]<=HeaderBytes+2*1024*1024+Limit,"asset memory session/version/size");
 multi_scene::Asset proof{};memcpy(&proof,seal.data()+32,sizeof(proof));
 // Path IDs are assigned by completion order after the worker seals its bytes.
 require(multi_scene::valid(proof)&&proof.id==asset.id&&proof.owner==asset.owner&&proof.revision==asset.revision&&
  proof.model==asset.model&&proof.source==asset.source&&proof.geometry_bytes==asset.geometry_bytes&&
  proof.image_bytes==asset.image_bytes&&!memcmp(proof.content,asset.content,32)&&proof.replay_hash==asset.replay_hash&&
  proof.textures_hash==asset.textures_hash,"texture memory exact asset identity");
 DWORD publishedCount=0,ready=0;memcpy(&publishedCount,seal.data()+120,4);memcpy(&ready,seal.data()+124,4);
 require(ready==1&&publishedCount&&publishedCount<=256&&(!count||publishedCount==count),"texture memory incomplete publication");MemoryBarrier();count=publishedCount;
 View full{static_cast<const BYTE*>(MapViewOfFile(handle.h,FILE_MAP_READ,0,0,h[2]))};require(full.p!=nullptr,"texture memory full size");
 Payload result;result.geometry.assign(full.p+HeaderBytes,full.p+HeaderBytes+asset.geometry_bytes);
 require(output_wire::hash(result.geometry.data(),result.geometry.size())==asset.replay_hash,"asset memory geometry content");
 result.textures.reserve(count);uint64_t offset=HeaderBytes+asset.geometry_bytes,hash=14695981039346656037ull;
 for(DWORD i=0;i<count;++i){DWORD entry[2]{};memcpy(entry,seal.data()+128+i*8,8);
  require(entry[0]==offset&&entry[1]>16&&entry[1]<=64*1024*1024+16&&offset+entry[1]<=h[2],"texture memory payload bounds");
  DWORD image[4]{};memcpy(image,full.p+offset,16);
  require(image[0]==0x31544653&&image[1]&&image[1]<=4096&&image[2]&&image[2]<=4096&&
   uint64_t(image[1])*image[2]*4==image[3]&&uint64_t(image[3])+16==entry[1],"texture memory image header");
  result.textures.emplace_back(full.p+offset,full.p+offset+entry[1]);hash^=output_wire::hash(result.textures.back().data(),result.textures.back().size());hash*=1099511628211ull;offset+=entry[1];
 }
 require(offset==h[2]&&hash==asset.textures_hash&&!memcmp(seal.data(),full.p,HeaderBytes),"texture memory content/seal");
 return result;
}
inline std::vector<std::vector<BYTE>> receive(const DWORD* session,const multi_scene::Asset& asset,DWORD count){return receive_asset(session,asset,count).textures;}
}

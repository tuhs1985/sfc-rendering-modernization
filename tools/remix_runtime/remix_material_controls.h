// Fixed worker-written Remix-only material settings;no SFC ABI changes.
#pragma once
#include <array>
struct RemixMaterialControls {
 std::array<float,10> values{1,1,0,0,1,1,1,1,1,1};uint64_t revision=0;
 bool read(){
  std::ifstream f("material-controls.bin",std::ios::binary);if(!f)return false;
  std::array<BYTE,56> raw{};f.read(reinterpret_cast<char*>(raw.data()),raw.size());if(!f||f.peek()!=EOF)return false;
  uint32_t header[2]{};uint64_t checksum=0;std::array<float,10> next{};
  memcpy(header,raw.data(),8);memcpy(next.data(),raw.data()+8,40);memcpy(&checksum,raw.data()+48,8);
  if(header[0]!=0x3143544d||header[1]!=1||ship_triplet::hash(raw.data(),48)!=checksum)return false;
  for(unsigned i=0;i<10;++i){const float lo=i==3?-1.f:0.f,hi=i==1?100.f:1.f;if(!std::isfinite(next[i])||next[i]<lo||next[i]>hi)return false;}
  for(unsigned i=4;i<10;++i)if(next[i]!=1.f)return false; // reserved neutral fallback colours
  if(checksum==revision)return false;values=next;revision=checksum;return true;
 }
};

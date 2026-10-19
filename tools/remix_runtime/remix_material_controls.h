// Fixed worker-written Remix-only material settings;no SFC ABI changes.
#pragma once
#include <array>
// Host worker only. Success is issued after GPU completion and old mesh/material
// destruction, never merely because the Python worker published a packet.
inline bool materialReceipt(uint64_t processed,uint64_t active,uint32_t status){
 std::array<BYTE,40> raw{};uint32_t h[2]{0x314b414d,1};memcpy(raw.data(),h,8);
 memcpy(raw.data()+8,&processed,8);memcpy(raw.data()+16,&active,8);memcpy(raw.data()+24,&status,4);
 const auto checksum=ship_triplet::hash(raw.data(),32);memcpy(raw.data()+32,&checksum,8);
 {std::ofstream f("material-receipt.pending",std::ios::binary|std::ios::trunc);f.write(reinterpret_cast<const char*>(raw.data()),raw.size());f.close();if(!f)return false;}
 return MoveFileExW(L"material-receipt.pending",L"material-receipt.bin",MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH)!=FALSE;
}
struct RemixMaterialControls {
 std::array<float,10> values{1,1,0,0,0,.5f,0,1,0,1};uint64_t revision=0;
 bool read(){
  std::ifstream f("material-controls.bin",std::ios::binary);if(!f)return false;
  std::array<BYTE,56> raw{};f.read(reinterpret_cast<char*>(raw.data()),raw.size());if(!f||f.peek()!=EOF)return false;
  uint32_t header[2]{};uint64_t checksum=0;std::array<float,10> next{};
  memcpy(header,raw.data(),8);memcpy(next.data(),raw.data()+8,40);memcpy(&checksum,raw.data()+48,8);
  if(header[0]!=0x3143544d||(header[1]!=1&&header[1]!=2)||ship_triplet::hash(raw.data(),48)!=checksum)return false;
  for(unsigned i=0;i<10;++i){const float lo=i==3?-1.f:0.f,hi=i==1?100.f:(i==9&&header[1]==2?4.f:1.f);if(!std::isfinite(next[i])||next[i]<lo||next[i]>hi)return false;}
  if(header[1]==1){for(unsigned i=4;i<10;++i)if(next[i]!=1.f)return false;next[4]=0;next[5]=.5f;next[6]=0;next[7]=1;next[8]=0;next[9]=1;}
  else if((next[4]!=0&&next[4]!=1)||(next[8]!=0&&next[8]!=1)||next[7]<=next[6]||next[9]<.25f)return false;
  if(checksum==revision)return false;values=next;revision=checksum;return true;
 }
};

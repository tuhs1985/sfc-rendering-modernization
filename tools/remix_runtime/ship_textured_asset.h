// Remix adapter only. Game-facing capture does not depend on these SDK records.
#pragma once
#include <filesystem>
struct DiskMaterial {uint64_t hash;char filename[72];};
struct DiskGroup {uint32_t identity,material,first,count;};
static_assert(sizeof(DiskMaterial)==80&&sizeof(DiskGroup)==16);
struct TexturedAsset {
 std::vector<DiskMaterial> materials;std::vector<DiskGroup> groups;std::vector<uint32_t> indices;
 std::vector<std::wstring> paths;std::vector<remixapi_MaterialHandle> handles;
 void load(uint32_t vertices){
  std::ifstream f("live-materials.bin",std::ios::binary|std::ios::ate);
  if(!f||f.tellg()<40||f.tellg()>2*1024*1024)throw std::runtime_error("textured material file bound");
  const auto bytes=static_cast<size_t>(f.tellg());f.seekg(0);uint32_t h[8]{};uint64_t expected=0;
  f.read(reinterpret_cast<char*>(h),32);f.read(reinterpret_cast<char*>(&expected),8);
  if(h[0]!=0x31585453||h[1]!=1||!h[2]||h[2]>256||!h[3]||h[3]>256||h[4]!=vertices||h[5]!=vertices||h[7]||
     h[6]!=h[2]*80+h[3]*16+h[4]*4||bytes!=40+h[6])throw std::runtime_error("textured material schema");
  std::vector<BYTE> data(h[6]);f.read(reinterpret_cast<char*>(data.data()),data.size());
  if(!f||ship_triplet::hash(data.data(),data.size())!=expected)throw std::runtime_error("textured material checksum");
  materials.resize(h[2]);groups.resize(h[3]);indices.resize(h[4]);
  memcpy(materials.data(),data.data(),h[2]*80);memcpy(groups.data(),data.data()+h[2]*80,h[3]*16);
  memcpy(indices.data(),data.data()+h[2]*80+h[3]*16,h[4]*4);
  std::vector<BYTE> used(vertices);uint32_t cursor=0;
  for(auto g:groups){if(g.material>=materials.size()||g.first!=cursor||!g.count||g.count%3||g.count>vertices-cursor)throw std::runtime_error("textured group range");cursor+=g.count;}
  if(cursor!=vertices)throw std::runtime_error("textured group coverage");
  for(auto i:indices){if(i>=vertices||used[i]++)throw std::runtime_error("textured index identity");}
  for(auto m:materials){
   if(!m.hash||m.filename[68]||std::memcmp(m.filename+64,".dds",4))throw std::runtime_error("textured DDS filename");
   for(unsigned i=0;i<64;++i)if(!((m.filename[i]>='0'&&m.filename[i]<='9')||(m.filename[i]>='a'&&m.filename[i]<='f')))throw std::runtime_error("textured DDS digest");
   std::wstring filename;for(unsigned i=0;i<68;++i)filename+=static_cast<wchar_t>(m.filename[i]);
   const auto path=std::filesystem::current_path()/L"textures"/filename;
   if(!std::filesystem::is_regular_file(path)||std::filesystem::file_size(path)>128*1024*1024)throw std::runtime_error("textured DDS file missing/bound");
   paths.push_back(path.wstring());
  }
 }
 void create(remixapi_Interface& api){
  handles.resize(materials.size());
  for(size_t i=0;i<materials.size();++i){
   remixapi_MaterialInfoOpaqueEXT opaque{};opaque.sType=REMIXAPI_STRUCT_TYPE_MATERIAL_INFO_OPAQUE_EXT;
   opaque.albedoConstant={1,1,1};opaque.opacityConstant=1;opaque.roughnessConstant=1;opaque.alphaTestType=7;
   remixapi_MaterialInfo info{};info.sType=REMIXAPI_STRUCT_TYPE_MATERIAL_INFO;info.pNext=&opaque;info.hash=materials[i].hash;
   // Ordinary hull colour is reflected surface colour, not a whole-ship lamp.
   // Secondary-image emission remains unqualified and is deliberately absent.
   info.albedoTexture=paths[i].c_str();info.emissiveTexture=nullptr;info.emissiveIntensity=0;info.emissiveColorConstant={0,0,0};
   check(api.CreateMaterial(&info,&handles[i]),"textured original material");
  }
 }
};

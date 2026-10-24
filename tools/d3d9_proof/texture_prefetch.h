// Offline-only public material API cache experiment. Never submit SDK geometry.
#pragma once
#include <set>
struct ApiTexturePrefetch {
 remixapi_Interface* api=nullptr;std::vector<remixapi_MaterialHandle> handles;
 std::set<std::wstring> seen;unsigned calls=0,nextRequest=1;
 static bool requested(){wchar_t v[2]{};return GetEnvironmentVariableW(L"SFC_D3D9_API_PREFETCH",v,2)==1&&v[0]==L'1';}
 static bool overlap(){wchar_t v[2]{};return GetEnvironmentVariableW(L"SFC_D3D9_API_PREFETCH_OVERLAP",v,2)==1&&v[0]==L'1';}
 void run(const fs::path& root,remixapi_Interface& external,IDirect3DQuery9* fence,WorkerPoll& poll,StartupProfile& profile,const fs::path& request=L"texture-prefetch.bin"){
  require(profile.enabled&&warm_start::requested(),"API prefetch requires isolated startup experiment");
  require(external.CreateMaterial&&external.DestroyMaterial,"public material API required");api=&external;
  const auto raw=read(root/request,32+1024*256+8);require(raw.size()>=40,"prefetch request length");
  uint32_t h[8]{};memcpy(h,raw.data(),32);uint64_t checksum=0;memcpy(&checksum,raw.data()+raw.size()-8,8);
  wchar_t pid[16]{};GetEnvironmentVariableW(L"SFC_D3D9_GAME_PID",pid,16);const auto session=warm_start::session();
  require(h[0]==0x31504654&&h[1]==1&&h[2]==wcstoul(pid,nullptr,10)&&h[3]&&h[3]<=1024&&
    !memcmp(h+4,session.data(),16)&&raw.size()==32+size_t(h[3])*256+8&&checksum==output_wire::hash(raw.data(),raw.size()-8),"prefetch session/count/checksum");
  const unsigned index=calls++;profile.mark("api_prefetch_begin",index);handles.reserve(1024);
  for(unsigned i=0;i<h[3];++i){
   const auto* text=reinterpret_cast<const char*>(raw.data()+32+size_t(i)*256);size_t n=0;while(n<256&&text[n])++n;
   require(n>0&&n<256,"prefetch path termination");for(size_t k=n;k<256;++k)require(text[k]==0,"prefetch path padding");
   const std::string relative(text,n);
   require(relative.rfind("assets/",0)==0&&relative.find("..") == std::string::npos&&relative.ends_with(".dds"),"prefetch relative DDS path");
   for(char c:relative)require((c>='a'&&c<='z')||(c>='0'&&c<='9')||c=='/'||c=='-'||c=='.',"prefetch path alphabet");
   const auto target=fs::weakly_canonical(root/fs::path(relative));require(fs::is_regular_file(target)&&!fs::relative(target,fs::weakly_canonical(root)).wstring().starts_with(L".."),"prefetch owned image");
   auto name=target.wstring(); // USD's resolved Windows path normalizes drive case.
   if(name.size()>1&&name[1]==L':'&&name[0]>=L'A'&&name[0]<=L'Z')name[0]=static_cast<wchar_t>(name[0]+L'a'-L'A');
   if(seen.contains(name))continue;require(handles.size()<1024,"aggregate prefetch handle bound");
   remixapi_MaterialInfoOpaqueEXT opaque{};opaque.sType=REMIXAPI_STRUCT_TYPE_MATERIAL_INFO_OPAQUE_EXT;opaque.albedoConstant={1,1,1};opaque.opacityConstant=1;opaque.roughnessConstant=1;
   remixapi_MaterialInfo info{};info.sType=REMIXAPI_STRUCT_TYPE_MATERIAL_INFO;info.pNext=&opaque;info.hash=0x5346435000000000ull+handles.size()+1;info.albedoTexture=name.c_str();info.filterMode=1;info.wrapModeU=info.wrapModeV=1;
   remixapi_MaterialHandle handle=nullptr;apiok(api->CreateMaterial(&info,&handle),"queue public texture preload");require(handle!=nullptr,"prefetch handle");handles.push_back(handle);seen.insert(name);
  }
  profile.mark("api_prefetch_queued",index);wait9(fence,poll);profile.mark("api_prefetch_drained",index);
  std::cout<<"API_TEXTURE_PREFETCH call="<<index<<" textures="<<handles.size()<<" commands_drained=1 gpu_residency_claim=0 sdk_mesh_calls=0\n";
 }
 void pump(const fs::path& root,remixapi_Interface& external,IDirect3DQuery9* fence,WorkerPoll& poll,StartupProfile& profile){
  if(nextRequest>64)return;const auto request=L"texture-prefetch-"+std::to_wstring(nextRequest)+L".bin";
  if(!fs::exists(root/request))return;run(root,external,fence,poll,profile,request);++nextRequest;
 }
 void close(IDirect3DQuery9* fence,WorkerPoll& poll){if(!api)return;for(auto h:handles)apiok(api->DestroyMaterial(h),"retire preload-only material");handles.clear();wait9(fence,poll);std::cout<<"API_TEXTURE_PREFETCH_RETIRED commands_drained=1\n";api=nullptr;}
 ~ApiTexturePrefetch(){if(api)for(auto h:handles)api->DestroyMaterial(h);}
};

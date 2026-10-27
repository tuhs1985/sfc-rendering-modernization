// D3D9 backend worker only. Retain geometry;draw one coherent tracked set.
// Included after the existing Scene/Renderer and LiveOwnerInput definitions.
#pragma once
#include "multi_scene_wire.h"
#include "replacement_transaction.h"
#include <map>
#include <memory>
#include <future>
struct MultiSceneRuntime {
 struct Resident {Scene scene;std::unique_ptr<Renderer> renderer;Renderer* drawRenderer=nullptr;uint64_t bytes=0;multi_scene::Asset provenance{};};
 sfc_calibration::Reader source;multi_scene::Store* store=nullptr;multi_scene::Frame packet{};
 std::array<multi_scene::Asset,64> entries{};std::array<std::shared_ptr<Resident>,64> bound{};
 std::map<std::array<BYTE,32>,std::shared_ptr<Resident>> content;
 fs::path root;IDirect3DDevice9* device=nullptr;const Scene* bootstrapScene=nullptr;Renderer* bootstrapRenderer=nullptr;bool enabled=false;DWORD pid=0;uint64_t bytes=0,frames=0,draws=0,omitted=0,rejected=0,loads=0,shared=0;
 std::map<uint64_t,uint64_t> ownerDraws;bool replacementOnly=false;
 struct Prepared {Scene scene;std::vector<std::vector<BYTE>> textures;uint64_t backing=0,cpu_us=0;};
 std::future<Prepared> preparing;multi_scene::Asset pendingAsset{};
 uint64_t lookup_header=0,lookup_packet=0,lookup_identity=0,decode_rejected=0,projection_rejected=0;
 uint64_t initialMask=0,initialWaits=0;bool initialReady=false;
 TextureUpload uploadPolicy=TextureUpload::StagedLock;
 static uint64_t clock(){LARGE_INTEGER q{},f{};QueryPerformanceCounter(&q);QueryPerformanceFrequency(&f);const auto n=uint64_t(q.QuadPart),d=uint64_t(f.QuadPart);return n/d*1000000+n%d*1000000/d;}
 static Prepared prepare(const fs::path& folder,const multi_scene::Asset& a,uint64_t residentBytes){
  const auto began=clock();Prepared p{};
  require(residentBytes+2*(uint64_t(a.geometry_bytes)+a.image_bytes)<=256ull*1024*1024,"pending+resident256MiB cap");
  require(!fs::is_symlink(fs::symlink_status(folder)),"multi-scene asset symlink");
  const auto raw=read(folder/L"scene.bin",2*1024*1024);require(raw.size()==a.geometry_bytes&&output_wire::hash(raw.data(),raw.size())==a.replay_hash,"multi-scene replay bytes/provenance");
  p.scene=load(folder);require(p.scene.width==1920&&p.scene.height==1080,"multi-scene output extent");
  uint32_t images=0;for(auto g:p.scene.groups)images=(std::max)(images,g.material+1);
  uint64_t hash=14695981039346656037ull,imageBytes=0;
  for(uint32_t n=0;n<images;++n){auto image=read(folder/(L"texture-"+std::to_wstring(n)+L".bin"),64*1024*1024+16);
   imageBytes+=image.size();require(imageBytes<=a.image_bytes,"prepared texture byte cap");hash^=output_wire::hash(image.data(),image.size());hash*=1099511628211ull;p.textures.push_back(std::move(image));}
  require(imageBytes==a.image_bytes&&hash==a.textures_hash,"multi-scene texture bytes/provenance");
  p.backing=2*(p.scene.vertices.size()*sizeof(Vertex)+p.scene.indices.size()*4+imageBytes);p.cpu_us=clock()-began;return p;
 }
 void start(const fs::path& directory,IDirect3DDevice9* d,const Scene& initial,Renderer& initialRenderer,TextureUpload policy=TextureUpload::StagedLock){
  uploadPolicy=policy;
  wchar_t flag[2]{};enabled=GetEnvironmentVariableW(L"SFC_D3D9_MULTISCENE",flag,2)==1&&flag[0]==L'1';if(!enabled)return;replacementOnly=replacement::requested();
  root=directory;device=d;bootstrapScene=&initial;bootstrapRenderer=&initialRenderer;require(source.prepare()&&source.requested,"multi-scene explicit mapping");
  auto* base=reinterpret_cast<BYTE*>(source.mailbox)-sfc_calibration::Offset;store=reinterpret_cast<multi_scene::Store*>(base+multi_scene::Offset);
  wchar_t pidText[16]{};GetEnvironmentVariableW(L"SFC_D3D9_GAME_PID",pidText,16);pid=static_cast<DWORD>(_wcstoui64(pidText,nullptr,10));
  require(multi_scene::valid(store->header,source.session,pid),"multi-scene session/process/version");
  wchar_t mask[32]{};if(GetEnvironmentVariableW(L"SFC_D3D9_INITIAL_ASSET_MASK",mask,32)){
   wchar_t* end=nullptr;initialMask=_wcstoui64(mask,&end,16);require(initialMask&&end&&!*end,"initial catalog mask");}
 }
 ~MultiSceneRuntime(){if(preparing.valid())preparing.wait();if(enabled){std::cout<<"MULTISCENE_SUMMARY frames="<<frames<<" draws="<<draws<<" loads="<<loads<<" shared="<<shared<<" omitted="<<omitted<<" rejected="<<rejected<<" retained_bytes="<<bytes<<" owners="<<ownerDraws.size()<<'\n';
  std::cout<<"MULTISCENE_STAGES lookup_header="<<lookup_header<<" lookup_packet="<<lookup_packet<<" lookup_identity="<<lookup_identity<<" decode="<<decode_rejected<<" projection="<<projection_rejected<<'\n';
  std::cout<<"MULTISCENE_INITIAL mask="<<initialMask<<" ready="<<initialReady<<" waits="<<initialWaits<<'\n';
  for(const auto& pair:ownerDraws)std::cout<<"MULTISCENE_OWNER owner="<<DWORD(pair.first)<<" revision="<<DWORD(pair.first>>32)<<" draws="<<pair.second<<'\n';}source.close();}
 void assets(){if(!enabled)return;
  if(preparing.valid()&&preparing.wait_for(std::chrono::seconds(0))!=std::future_status::ready)return;
  for(unsigned i=0;i<64;++i){auto& slot=store->assets[i];if(InterlockedCompareExchange(&slot.ack,0,0))continue;
   if(preparing.valid()&&pendingAsset.id!=i+1)continue;
   multi_scene::Asset a{};if(!multi_scene::read(slot,a))continue;
   try{
    require(a.id==i+1,"multi-scene catalog index");std::array<BYTE,32> key{};memcpy(key.data(),a.content,32);
    auto found=content.find(key);std::shared_ptr<Resident> item;
    if(found!=content.end()){item=found->second;const auto& proof=item->provenance;
     require(a.path_id==proof.path_id&&a.geometry_bytes==proof.geometry_bytes&&a.image_bytes==proof.image_bytes&&
      a.replay_hash==proof.replay_hash&&a.textures_hash==proof.textures_hash,"shared asset content/provenance mismatch");++shared;}
    else{
     const auto folder=a.path_id==1?root:root/L"assets"/std::to_wstring(a.path_id);
     if(!preparing.valid()){pendingAsset=a;preparing=std::async(std::launch::async,[folder,a,residentBytes=bytes]{return prepare(folder,a,residentBytes);});return;}
     require(memcmp(&a,&pendingAsset,sizeof(a))==0,"asset changed during preparation");auto prepared=preparing.get();
     const auto gpuBegan=clock();item=std::make_shared<Resident>();item->scene=std::move(prepared.scene);item->bytes=prepared.backing;
     require(bytes+item->bytes<=256ull*1024*1024,"multi-scene retained256MiB cap");
     if(a.path_id==1){require(item->scene.vertices.size()==bootstrapScene->vertices.size(),"multi-scene bootstrap identity");item->drawRenderer=bootstrapRenderer;}
     else{item->renderer=std::make_unique<Renderer>(device,item->scene,folder,&prepared.textures,uploadPolicy);item->drawRenderer=item->renderer.get();}
     std::cout<<"MULTISCENE_ASSET_TIMING id="<<a.id<<" cpu_us="<<prepared.cpu_us<<" gpu_admit_us="<<clock()-gpuBegan<<" at_us="<<clock()<<'\n';
     const auto* uploader=item->drawRenderer;
     std::cout<<"MULTISCENE_UPLOAD id="<<a.id<<" initial="<<uploader->initialDataUploads<<" staged="<<uploader->stagedUploads<<" unsupported="<<uploader->initialDataUnsupported<<'\n';
     item->provenance=a;bytes+=item->bytes;content.emplace(key,item);++loads;
    }
    entries[i]=a;bound[i]=item;InterlockedIncrement(&store->header.asset_ready);InterlockedExchange(&slot.ack,1);
    std::cout<<"MULTISCENE_ASSET id="<<a.id<<" path_id="<<a.path_id<<" owner="<<a.owner<<" revision="<<a.revision<<" retained_bytes="<<bytes<<'\n';
   }catch(const std::exception& e){if(preparing.valid()){try{preparing.get();}catch(...){}}++rejected;InterlockedIncrement(&store->header.asset_rejected);InterlockedExchange(&slot.ack,-1);std::cout<<"MULTISCENE_ASSET_REJECTED id="<<a.id<<" reason="<<e.what()<<'\n';}
   break; // at most one admission per worker iteration,never game-thread work
  }
 }
 bool next(const live_owner::Packet& anchor){if(!enabled)return true;
  if(!initialReady){if(!multi_scene::initial_resolved(*store,initialMask)){++initialWaits;return false;}
   initialReady=true;std::cout<<"MULTISCENE_INITIAL_READY mask="<<initialMask<<'\n';}
  if(!multi_scene::valid(store->header,source.session,pid)){++lookup_header;return false;}
  if(!multi_scene::read(*store,anchor.row[2],anchor.sequence,packet)){++lookup_packet;return false;}
  if(packet.anchor!=anchor.row[1]||packet.revision!=anchor.row[7]){++lookup_identity;return false;}return true;
 }
 bool draw(uint32_t width,uint32_t height,const float* displacement){bool first=true;unsigned count=0;
  for(DWORD n=0;n<packet.count;++n){const auto& row=packet.rows[n];std::shared_ptr<Resident> resident;DWORD asset=0;
   if(replacementOnly&&(row[1]!=packet.anchor||row[7]!=packet.revision))continue;
   for(unsigned i=0;i<64;++i)if(bound[i]&&multi_scene::matches(entries[i],row)){resident=bound[i];asset=i+1;break;}
   if(!resident){++omitted;continue;}live_owner::Packet p{};p.row=row;Frame frame{};
   if(!live_owner::decode(p,frame)){++decode_rejected;++rejected;continue;}
   bool good=true;const auto& vertices=resident->scene.vertices;const auto stride=(std::max)(size_t(1),vertices.size()/64);
   for(size_t k=0;k<vertices.size();k+=stride)if(!live_owner::projection_matches(p,frame,vertices[k].p)){good=false;break;}
   if(!good){++projection_rejected;++rejected;continue;}
   for(unsigned axis=0;axis<3;++axis)frame.model[axis*4+3]+=displacement[axis];
   resident->drawRenderer->draw(frame,false,width,height,first);first=false;++count;++draws;
   ++ownerDraws[live_owner::selection(row[1],row[7])];
   if(frames<8||frames%60==0)std::cout<<"MULTISCENE_DRAW frame="<<packet.frame<<" owner="<<row[1]<<" revision="<<row[7]<<" asset="<<asset<<" set_hash="<<packet.checksum<<'\n';
  }++frames;return count!=0;
 }
};

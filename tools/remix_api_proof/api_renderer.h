// Isolated Remix backend. Same immutable Scene; no USD lookup or D3D9 mesh draws.
#pragma once
#include "output_channel.h"
namespace api_scene {
inline remixapi_Interface* api=nullptr;
inline uint64_t serial=0,meshes=0,materials=0,draws=0,retireFailures=0;
inline uint64_t key(){require(serial<64*512,"API handle bound");return 0x534643a000000000ull+(++serial);}
struct Material {uint32_t group,index;uint64_t provenance;char image[3][80];};
static_assert(sizeof(Material)==256);
inline std::wstring path(const fs::path& root,const char* name,bool required){
 if(!name[0]){require(!required,"API primary image missing");for(unsigned i=0;i<80;++i)require(!name[i],"API empty path padding");return {};}
 for(unsigned i=0;i<64;++i)require((name[i]>='0'&&name[i]<='9')||(name[i]>='a'&&name[i]<='f'),"API DDS digest");
 require(!memcmp(name+64,".dds",4),"API DDS suffix");for(unsigned i=68;i<80;++i)require(!name[i],"API path padding");
 const auto target=root/L"rtx-remix/mods/sfc-policy/textures"/fs::path(std::string(name,68));
 require(!fs::is_symlink(target)&&fs::is_regular_file(target)&&fs::file_size(target)<=128ull*1024*1024,"API image missing/bound");
 return fs::absolute(target).wstring();
}
inline remixapi_CameraInfo camera(const Frame& f,uint32_t width,uint32_t height){
 require(width&&height,"API output extent");remixapi_CameraInfo c{};c.sType=REMIXAPI_STRUCT_TYPE_CAMERA_INFO;c.type=REMIXAPI_CAMERA_TYPE_WORLD;
 // Vendor Matrix4{info.view/projection} reads column-major arrays. Native Frame
 // is row-major column-vector math. Also preserve the source's inset viewport.
 const float sx=f.viewport[2]/1920.f,sy=f.viewport[3]/1080.f;
 const float tx=(2*f.viewport[0]+f.viewport[2])/1920.f-1,ty=1-(2*f.viewport[1]+f.viewport[3])/1080.f;
 for(unsigned row=0;row<4;++row)for(unsigned col=0;col<4;++col){
  c.view[col][row]=f.view[row*4+col];
  const float p=f.projection[row*4+col];
  c.projection[col][row]=row==0?sx*p+tx*f.projection[12+col]:row==1?sy*p+ty*f.projection[12+col]:p;
 }
 return c;
}
}
struct ApiRenderer {
 const Scene& scene;remixapi_MeshHandle mesh=nullptr;
 std::vector<remixapi_MaterialHandle> handles;
 ApiRenderer(IDirect3DDevice9*,const Scene& s,const fs::path& root,const std::vector<std::vector<BYTE>>* =nullptr):scene(s){
  using namespace api_scene;require(api&&api->CreateMaterial&&api->DestroyMaterial&&api->CreateMesh&&api->DestroyMesh&&api->DrawInstance&&api->SetupCamera,"API scene capabilities");
  try{
   auto base=root;
   if(!fs::exists(base/L"api-materials.bin")){
    base=root/L"assets/1";
    require(read(root/L"scene.bin",2*1024*1024)==read(base/L"scene.bin",2*1024*1024),"API bootstrap/source geometry mismatch");
   }
   const auto raw=read(base/L"api-materials.bin",64+256*256);require(raw.size()>=64,"API material packet length");size_t at=0;
   const auto h=take<std::array<uint32_t,4>>(raw,at);const auto v=take<std::array<float,10>>(raw,at);
   uint64_t expected=0;memcpy(&expected,raw.data()+raw.size()-8,8);
   require(h[0]==0x314d5041&&h[1]==1&&h[2]==scene.groups.size()&&h[2]&&h[2]<=256&&h[3]==256&&raw.size()==64ull+256*h[2]&&expected==output_wire::hash(raw.data(),raw.size()-8),"API material packet schema/checksum");
   for(float x:v)require(std::isfinite(x),"API scalar finite");
   std::vector<std::vector<remixapi_HardcodedVertex>> vertices(h[2]);std::vector<std::vector<uint32_t>> indices(h[2]);std::vector<remixapi_MeshInfoSurfaceTriangles> surfaces(h[2]);
   for(unsigned i=0;i<h[2];++i){
    const auto m=take<Material>(raw,at);const auto& group=scene.groups[i];
    require(m.group==group.id&&m.index==group.material&&m.provenance,"API group association");
    const auto color=path(base,m.image[0],true),emission=path(base,m.image[1],false),roughness=path(base,m.image[2],false);
    require(bool(v[4])==!roughness.empty(),"API roughness association");
    remixapi_MaterialInfoOpaqueEXT opaque{};opaque.sType=REMIXAPI_STRUCT_TYPE_MATERIAL_INFO_OPAQUE_EXT;
    opaque.albedoConstant={1,1,1};opaque.opacityConstant=1;opaque.roughnessConstant=v[0];opaque.metallicConstant=v[2];opaque.anisotropy=v[3];opaque.alphaTestType=7;
    opaque.roughnessTexture=roughness.empty()?nullptr:roughness.c_str();
    remixapi_MaterialInfo info{};info.sType=REMIXAPI_STRUCT_TYPE_MATERIAL_INFO;info.pNext=&opaque;info.hash=key();
    info.albedoTexture=color.c_str();info.emissiveTexture=emission.empty()?nullptr:emission.c_str();info.emissiveIntensity=emission.empty()?0:v[1];info.emissiveColorConstant={1,1,1};info.filterMode=info.wrapModeU=info.wrapModeV=1;
    remixapi_MaterialHandle handle=nullptr;apiok(api->CreateMaterial(&info,&handle),"API material registration");require(handle!=nullptr,"API material handle");handles.push_back(handle);++materials;
    auto& points=vertices[i];auto& order=indices[i];points.resize(group.count);order.resize(group.count);
    for(unsigned n=0;n<group.count;++n){
     const auto& from=scene.vertices[scene.indices[group.first+n]];auto& to=points[n];
     memcpy(to.position,from.p,12);memcpy(to.normal,from.n,12);memcpy(to.texcoord,from.uv,8);to.color=0xffffffff;order[n]=n;
    }
    auto& surface=surfaces[i];surface.vertices_values=points.data();surface.vertices_count=points.size();surface.indices_values=order.data();surface.indices_count=order.size();surface.material=handle;
   }
   remixapi_MeshInfo info{};info.sType=REMIXAPI_STRUCT_TYPE_MESH_INFO;info.hash=key();info.surfaces_values=surfaces.data();info.surfaces_count=h[2];
   apiok(api->CreateMesh(&info,&mesh),"API mesh registration");require(mesh!=nullptr,"API mesh handle");++meshes;
   std::cout<<"API_ASSET_REGISTERED groups="<<handles.size()<<" corners="<<scene.vertices.size()<<" geometry_uv_unchanged=1\n";
  }catch(...){retire();throw;}
 }
 void retire() noexcept {
  if(mesh)std::cerr<<"API_RETIRE_BEGIN materials="<<handles.size()<<'\n';
  if(mesh){if(api_scene::api->DestroyMesh(mesh)!=REMIXAPI_ERROR_CODE_SUCCESS)++api_scene::retireFailures;mesh=nullptr;}
  for(auto h:handles)if(api_scene::api->DestroyMaterial(h)!=REMIXAPI_ERROR_CODE_SUCCESS)++api_scene::retireFailures;handles.clear();
  std::cerr<<"API_RETIRE_END failures="<<api_scene::retireFailures<<'\n';
 }
 ~ApiRenderer(){retire();}
 void draw(const Frame& f,bool mask,uint32_t width,uint32_t height,bool =true){
  require(!mask,"API mask mode not qualified");const auto c=api_scene::camera(f,width,height);apiok(api_scene::api->SetupCamera(&c),"API captured camera");
  if(!f.active)return;remixapi_InstanceInfo instance{};instance.sType=REMIXAPI_STRUCT_TYPE_INSTANCE_INFO;instance.mesh=mesh;instance.doubleSided=1;
  memcpy(instance.transform.matrix,f.model,48);apiok(api_scene::api->DrawInstance(&instance),"API retained instance");++api_scene::draws;
 }
 void save(const fs::path&,uint32_t,uint32_t){throw std::runtime_error("API ordinary-backbuffer diagnostic is unsupported;use returned pixels");}
};
using Renderer=ApiRenderer;

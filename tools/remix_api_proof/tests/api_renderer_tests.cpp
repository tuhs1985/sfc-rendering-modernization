#define SFC_D3D9_REPLAY_TYPES_ONLY
#define Renderer RasterRenderer
#include "../../d3d9_proof/d3d9_replay.cpp"
#undef Renderer
#define REMIX_WINAPI_NO_LIBRARY_LOADER
#include <remix_c.h>
static void apiok(remixapi_ErrorCode r,const char* why){require(r==REMIXAPI_ERROR_CODE_SUCCESS,why);}
#include "../api_renderer.h"
static const Scene* expectedScene=nullptr;
static std::vector<api_scene::Material> expectedMaterials;
static std::array<float,10> expectedValues{};
static std::set<remixapi_MaterialHandle> activeMaterials;
static std::vector<remixapi_MaterialHandle> materialOrder;
static unsigned submitted=0,materialCalls=0,cameraCalls=0;
static bool failMesh=false,failMaterial=false;
static Frame expectedFrame{};
static remixapi_ErrorCode REMIXAPI_CALL material(const remixapi_MaterialInfo* p,remixapi_MaterialHandle* out){
 if(failMaterial)return REMIXAPI_ERROR_CODE_GENERAL_FAILURE;
 const auto& m=expectedMaterials[materialCalls%expectedMaterials.size()];++materialCalls;
 const auto* opaque=static_cast<const remixapi_MaterialInfoOpaqueEXT*>(p->pNext);
 require(opaque&&opaque->sType==REMIXAPI_STRUCT_TYPE_MATERIAL_INFO_OPAQUE_EXT,"mock opaque type");
 require(opaque->roughnessConstant==expectedValues[0]&&opaque->metallicConstant==expectedValues[2]&&opaque->anisotropy==expectedValues[3],"mock exact material scalars");
 require(opaque->opacityConstant==1&&opaque->albedoConstant.x==1&&opaque->albedoConstant.y==1&&opaque->albedoConstant.z==1,"mock albedo/opacity");
 require(p->filterMode==1&&p->wrapModeU==1&&p->wrapModeV==1,"mock sampler");
 const auto file=[](const wchar_t* value){return value?fs::path(value).filename().string():std::string();};
 require(file(p->albedoTexture)==std::string(m.image[0]),"mock primary association");
 require(file(p->emissiveTexture)==std::string(m.image[1])&&file(opaque->roughnessTexture)==std::string(m.image[2]),"mock emission/roughness associations");
 require(p->emissiveIntensity==(m.image[1][0]?expectedValues[1]:0)&&p->emissiveColorConstant.x==1,"mock emission strength");
 *out=reinterpret_cast<remixapi_MaterialHandle>(p->hash);require(activeMaterials.insert(*out).second,"mock unique material handle");materialOrder.push_back(*out);return REMIXAPI_ERROR_CODE_SUCCESS;
}
static remixapi_ErrorCode REMIXAPI_CALL retireMaterial(remixapi_MaterialHandle h){require(activeMaterials.erase(h)==1,"mock material retirement");return REMIXAPI_ERROR_CODE_SUCCESS;}
static remixapi_ErrorCode REMIXAPI_CALL mesh(const remixapi_MeshInfo* p,remixapi_MeshHandle* out){
 require(p->surfaces_count==expectedScene->groups.size(),"mock mesh group count");
 for(unsigned i=0;i<p->surfaces_count;++i){const auto& part=p->surfaces_values[i];const auto& group=expectedScene->groups[i];
  require(part.vertices_count==group.count&&part.indices_count==group.count,"mock group corner counts");
  require(part.material==materialOrder[materialOrder.size()-p->surfaces_count+i],"mock group material handle");
  for(unsigned j=0;j<group.count;++j){const auto& a=part.vertices_values[j];const auto& b=expectedScene->vertices[expectedScene->indices[group.first+j]];
   require(part.indices_values[j]==j,"mock index rebasing/order");require(!memcmp(a.position,b.p,12)&&!memcmp(a.normal,b.n,12)&&!memcmp(a.texcoord,b.uv,8),"mock exact corners/normals/UV");require(a.color==0xffffffff,"mock vertex color");
  }
 }
 if(failMesh)return REMIXAPI_ERROR_CODE_GENERAL_FAILURE;
 *out=reinterpret_cast<remixapi_MeshHandle>(p->hash);return REMIXAPI_ERROR_CODE_SUCCESS;
}
static remixapi_ErrorCode REMIXAPI_CALL retireMesh(remixapi_MeshHandle){require(!activeMaterials.empty(),"mock mesh retired before materials");return REMIXAPI_ERROR_CODE_SUCCESS;}
static remixapi_ErrorCode REMIXAPI_CALL camera(const remixapi_CameraInfo*){++cameraCalls;return REMIXAPI_ERROR_CODE_SUCCESS;}
static remixapi_ErrorCode REMIXAPI_CALL draw(const remixapi_InstanceInfo* p){
 require(!memcmp(p->transform.matrix,expectedFrame.model,48),"mock native3x4 transform");require(p->doubleSided&&p->mesh,"mock instance flags/mesh");++submitted;return REMIXAPI_ERROR_CODE_SUCCESS;
}
int wmain(int argc,wchar_t** argv){try{
 require(argc==2,"prepared packet-derived asset folder required");const fs::path root=argv[1];const auto scene=load(root);expectedScene=&scene;
 const auto raw=read(root/L"api-materials.bin",64+256*256);size_t offset=16;expectedValues=take<std::array<float,10>>(raw,offset);
 for(size_t i=0;i<scene.groups.size();++i)expectedMaterials.push_back(take<api_scene::Material>(raw,offset));
 remixapi_Interface mock{};mock.CreateMaterial=material;mock.DestroyMaterial=retireMaterial;mock.CreateMesh=mesh;mock.DestroyMesh=retireMesh;mock.SetupCamera=camera;mock.DrawInstance=draw;api_scene::api=&mock;
 const auto original=scene.vertices;
 {ApiRenderer asset(nullptr,scene,root);expectedFrame=scene.frames.front();asset.draw(expectedFrame,false,1920,1080);expectedFrame.model[3]+=10;asset.draw(expectedFrame,false,1920,1080);expectedFrame.active=0;asset.draw(expectedFrame,false,1920,1080);require(submitted==2&&cameraCalls==3,"mock independent poses/inactive no draw");}
 require(activeMaterials.empty()&&!api_scene::retireFailures,"mock clean asset retirement");
 failMesh=true;bool rejected=false;try{ApiRenderer asset(nullptr,scene,root);}catch(const std::runtime_error&){rejected=true;}failMesh=false;require(rejected&&activeMaterials.empty(),"mock mesh failure cleans materials");
 failMaterial=true;rejected=false;try{ApiRenderer asset(nullptr,scene,root);}catch(const std::runtime_error&){rejected=true;}failMaterial=false;require(rejected&&activeMaterials.empty(),"mock material failure cleanup");
 auto changed=scene;changed.groups[0].id^=1;rejected=false;try{ApiRenderer asset(nullptr,changed,root);}catch(const std::runtime_error&){rejected=true;}require(rejected&&activeMaterials.empty(),"mock mismatched group rejected");
 require(!memcmp(original.data(),scene.vertices.data(),scene.vertices.size()*sizeof(Vertex)),"mock original geometry unchanged");
 const auto& f=scene.frames.front();const auto c=api_scene::camera(f,1920,1080);
 for(unsigned i=0;i<4;++i)for(unsigned j=0;j<4;++j)require(c.view[j][i]==f.view[i*4+j],"mock camera transpose");
 for(const std::array<float,4>& point:{std::array<float,4>{1,2,-10,1},std::array<float,4>{-4,1,-30,1}}){
  float native[4]{},apiClip[4]{};for(unsigned row=0;row<4;++row)for(unsigned col=0;col<4;++col){native[row]+=f.projection[row*4+col]*point[col];apiClip[row]+=c.projection[col][row]*point[col];}
  const float x=f.viewport[0]+(native[0]/native[3]+1)*f.viewport[2]*.5f,y=f.viewport[1]+(1-native[1]/native[3])*f.viewport[3]*.5f;
  require(std::abs(x-(apiClip[0]/apiClip[3]+1)*960)<.001f&&std::abs(y-(1-apiClip[1]/apiClip[3])*540)<.001f,"mock viewport pixel equivalence");
 }
 std::cout<<"API renderer mock PASS checks="<<checks<<" exact_geometry_uv_materials=1 camera_viewport=1 failures_cleanup=1 gpu_claim=0\n";return 0;
 }catch(const std::exception& e){std::cerr<<"API mock FAIL "<<e.what()<<'\n';return 1;}}

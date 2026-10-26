// Actual shared Renderer on SYSTEM D3D9Ex: admission must not change bound state
// or already-rendered pixels. No SFC, Remix or unqualified graphics threads.
#define SFC_D3D9_REPLAY_TYPES_ONLY
#include "../tools/d3d9_proof/d3d9_replay.cpp"
#include "../tools/d3d9_proof/asset_service.h"
#include <thread>
#include <atomic>
#include <memory>
struct Upload {
 IDirect3DDevice9* device;const Scene* scene;std::vector<std::vector<BYTE>>* textures;
 std::unique_ptr<Renderer> created;AssetService* service;unsigned calls=0;
 static void run(void* pointer){auto& u=*static_cast<Upload*>(pointer);++u.calls;
  u.created=std::make_unique<Renderer>(u.device,*u.scene,fs::path{},u.textures,TextureUpload::InitialData);
  u.service->tick(AssetService::RenderQuery); // Recursive callback suppressed.
 }
};
int main(){try{
 SetEnvironmentVariableW(L"SFC_PIPELINE_MODE",L"performance");
 Module module;module.value=LoadLibraryExW(L"d3d9.dll",nullptr,LOAD_LIBRARY_SEARCH_SYSTEM32);require(module.value!=nullptr,"native D3D9 only");
 auto create=reinterpret_cast<decltype(&Direct3DCreate9Ex)>(GetProcAddress(module.value,"Direct3DCreate9Ex"));require(create!=nullptr,"native Ex export");
 Window window;WNDCLASSW wc{};wc.hInstance=GetModuleHandleW(nullptr);wc.lpfnWndProc=proc;wc.lpszClassName=L"SFC_AssetService_Test";
 require(RegisterClassW(&wc)!=0,"class");window.value=CreateWindowW(wc.lpszClassName,L"Native admission test",WS_POPUP,0,0,32,32,nullptr,nullptr,wc.hInstance,nullptr);require(window.value!=nullptr,"window");
 ComPtr<IDirect3D9Ex> api;ok(create(D3D_SDK_VERSION,&api),"API");ComPtr<IDirect3DDevice9Ex> device;
 D3DPRESENT_PARAMETERS pp{};pp.BackBufferWidth=32;pp.BackBufferHeight=32;pp.BackBufferFormat=D3DFMT_A8R8G8B8;pp.BackBufferCount=1;pp.Windowed=TRUE;pp.hDeviceWindow=window.value;pp.SwapEffect=D3DSWAPEFFECT_DISCARD;pp.EnableAutoDepthStencil=TRUE;pp.AutoDepthStencilFormat=D3DFMT_D24S8;
 ok(api->CreateDeviceEx(0,D3DDEVTYPE_HAL,window.value,D3DCREATE_HARDWARE_VERTEXPROCESSING|D3DCREATE_FPU_PRESERVE,&pp,nullptr,&device),"single-thread device");
 Scene scene;scene.width=scene.height=32;scene.vertices={{{-.5f,-.5f,.5f},{0,0,1},{0,0}},{{.5f,-.5f,.5f},{0,0,1},{1,0}},{{0,.5f,.5f},{0,0,1},{.5f,1}}};scene.indices={0,1,2};scene.groups={{0,0,0,3}};
 Frame frame{};frame.owner=frame.revision=frame.frame=frame.active=1;
 for(unsigned i=0;i<4;++i){frame.model[i*4+i]=frame.view[i*4+i]=frame.projection[i*4+i]=1;}frame.viewport[2]=frame.viewport[3]=32;
 std::vector<std::vector<BYTE>> textures(1,std::vector<BYTE>(16+12,255));const uint32_t header[]={0x31544653,3,1,12};memcpy(textures[0].data(),header,16);
 Renderer original(device.Get(),scene,fs::path{},&textures);original.draw(frame,false,32,32);const auto pixels=original.pixels(32,32);
 ComPtr<IDirect3DVertexBuffer9> beforeVB;ComPtr<IDirect3DIndexBuffer9> beforeIB;ComPtr<IDirect3DBaseTexture9> beforeTexture;UINT beforeOffset=0,beforeStride=0;DWORD beforeFVF=0;
 ok(device->GetStreamSource(0,&beforeVB,&beforeOffset,&beforeStride),"before VB");ok(device->GetIndices(&beforeIB),"before IB");ok(device->GetTexture(0,&beforeTexture),"before texture");ok(device->GetFVF(&beforeFVF),"before FVF");
 AssetService service;Upload upload{device.Get(),&scene,&textures,{},&service};service.start(true,Upload::run,&upload);
 ComPtr<IDirect3DQuery9> query;ok(device->CreateQuery(D3DQUERYTYPE_EVENT,&query),"query");ok(query->Issue(D3DISSUE_END),"query issue");
 service.tick(AssetService::RenderQuery);
 require(textures[0].empty()&&upload.created->uploadBacking[0].size()==28,"prepared source moved into renderer ownership");
 const auto deadline=GetTickCount64()+5000;HRESULT status;
 while((status=query->GetData(nullptr,0,D3DGETDATA_FLUSH))==S_FALSE){require(GetTickCount64()<deadline,"query deadline");Sleep(1);}ok(status,"actual query completion");
 require(upload.calls==1&&upload.created&&service.calls[AssetService::RenderQuery]==1,"bounded nonrecursive upload");
 ComPtr<IDirect3DVertexBuffer9> afterVB;ComPtr<IDirect3DIndexBuffer9> afterIB;ComPtr<IDirect3DBaseTexture9> afterTexture;UINT offset=0,stride=0;DWORD fvf=0;
 ok(device->GetStreamSource(0,&afterVB,&offset,&stride),"after VB");ok(device->GetIndices(&afterIB),"after IB");ok(device->GetTexture(0,&afterTexture),"after texture");ok(device->GetFVF(&fvf),"after FVF");
 require(beforeVB==afterVB&&beforeIB==afterIB&&beforeTexture==afterTexture&&offset==beforeOffset&&stride==beforeStride&&fvf==beforeFVF,"bound resource state preserved");
 require(original.pixels(32,32)==pixels,"pending output pixels unchanged");
 std::atomic<bool> rejected=false;std::thread wrong([&]{try{service.tick(AssetService::Peer);}catch(const std::runtime_error&){rejected=true;}});wrong.join();require(rejected,"wrong graphics thread rejected");
 service.enabled=false;service.tick(AssetService::Bootstrap);require(upload.calls==1,"disabled no work");
 AssetService failure;failure.start(true,[](void*){throw std::runtime_error("injected");},nullptr);try{failure.tick(AssetService::Boundary);}catch(const std::runtime_error&){}require(!failure.active,"exception drains service guard");
 auditModules();std::cout<<"Asset service PASS checks="<<checks<<" native_d3d9ex=1 bound_state_exact=1 pixels_exact=1 wrong_thread_rejected=1 no_reentrancy=1\n";
 return 0;
 }catch(const std::exception& e){std::cerr<<"Asset service FAILED "<<e.what()<<'\n';return 1;}}

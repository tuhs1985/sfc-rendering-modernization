// Fresh semantic SDK producer; no Toolkit and no historical-pose input mode.
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <d3d9.h>
#include <d3d11.h>
#include <dxgi.h>
#include <wrl/client.h>
#include <remix/remix_c.h>
#include <fstream>
#include <iostream>
#include <vector>
#include "ship_live_camera.h"
using Microsoft::WRL::ComPtr;
static void check(HRESULT h,const char* s){if(FAILED(h))throw std::runtime_error(s);}
static void check(remixapi_ErrorCode e,const char* s){if(e!=REMIXAPI_ERROR_CODE_SUCCESS)throw std::runtime_error(s);}
#include "ship_textured_asset.h"
#include "remix_texture_coordinates.h"
#include "remix_live_lights.h"
static LRESULT CALLBACK proc(HWND w,UINT m,WPARAM p,LPARAM l){return DefWindowProcW(w,m,p,l);}
struct SceneReader:sfc_calibration::Reader{~SceneReader(){close();}};
int wmain(int argc,wchar_t** argv){
 if(argc!=2)return 2;std::cout.setf(std::ios::unitbuf);
 const bool textured=GetEnvironmentVariableW(L"SFC_REMIX_TEXTURED_SHIP",nullptr,0)!=0;
 const bool lightWiring=GetEnvironmentVariableW(L"SFC_REMIX_LIGHT_WIRING",nullptr,0)!=0;
 if(lightWiring&&!textured)return 2;
 const UINT outputWidth=textured?1920u:256u,outputHeight=textured?1080u:256u;
 remixapi_Interface api{};HMODULE dll=nullptr;HWND window=nullptr;int result=1;
 try{
  using namespace ship_live;
  return_path::Mapping mapping(true);auto& state=*mapping.state;
  auto& wire=*reinterpret_cast<Wire*>(reinterpret_cast<BYTE*>(mapping.state)+ship_triplet::Offset);wire={};
  if(textured)wire.version=BufferedVersion;
  auto& cmd=command(mapping);cmd={};auto& reg=registration(mapping);reg={};
  struct Stop{Wire& w;return_path::State& s;~Stop(){store(w.stop,1);return_path::write(s.stop,1);}} stop{wire,state};
  SceneReader scene;if(!scene.prepare()||!scene.requested)throw std::runtime_error("fresh scene mapping missing");
  WNDCLASSW wc{};wc.lpfnWndProc=proc;wc.hInstance=GetModuleHandleW(nullptr);wc.lpszClassName=L"SFC_PrivateShipHost";
  if(!RegisterClassW(&wc))throw std::runtime_error("ship host window class");
  // SDK Present resizes its swapchain to this HWND's client area. Shared texture
  // dimensions alone do not prevent a 256-square render being enlarged on copy.
  window=CreateWindowW(wc.lpszClassName,L"Private ship SDK host",WS_POPUP,0,0,outputWidth,outputHeight,nullptr,nullptr,wc.hInstance,nullptr);if(!window)throw std::runtime_error("ship host window");
  RECT client{};if(!GetClientRect(window,&client)||client.right-client.left!=static_cast<LONG>(outputWidth)||client.bottom-client.top!=static_cast<LONG>(outputHeight))throw std::runtime_error("ship host client dimensions");
  std::cout<<"LIVE_STAGE sdk_load\n";check(remixapi_lib_loadRemixDllAndInitialize(argv[1],&api,&dll),"ship SDK load");
  if(textured)check(api.SetConfigVariable("rtx.resolutionScale","1.0"),"textured native render scale");
  {
   ComPtr<IDirect3D9Ex> d9;ComPtr<IDirect3DDevice9Ex> initial;check(api.dxvk_CreateD3D9(FALSE,&d9),"ship D3D9");
   D3DPRESENT_PARAMETERS pp{};pp.BackBufferWidth=outputWidth;pp.BackBufferHeight=outputHeight;pp.BackBufferCount=1;pp.BackBufferFormat=D3DFMT_X8R8G8B8;pp.Windowed=TRUE;pp.hDeviceWindow=window;pp.SwapEffect=D3DSWAPEFFECT_DISCARD;pp.PresentationInterval=D3DPRESENT_INTERVAL_IMMEDIATE;
   check(d9->CreateDeviceEx(0,D3DDEVTYPE_HAL,window,D3DCREATE_HARDWARE_VERTEXPROCESSING,&pp,nullptr,&initial),"ship device");check(api.dxvk_RegisterD3D9Device(initial.Get()),"ship registration");auto* device=initial.Detach();
   ComPtr<ID3D11Device> native;ComPtr<ID3D11DeviceContext> nc;const D3D_FEATURE_LEVEL feature=D3D_FEATURE_LEVEL_10_1;
   check(D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,&feature,1,D3D11_SDK_VERSION,&native,nullptr,&nc),"ship native producer");
   ComPtr<IDXGIDevice> dx;ComPtr<IDXGIAdapter> adapter;DXGI_ADAPTER_DESC ad{};check(native.As(&dx),"ship DXGI");check(dx->GetAdapter(&adapter),"ship adapter");check(adapter->GetDesc(&ad),"ship LUID");
   wire.creator=GetCurrentProcessId();wire.width=outputWidth;wire.height=outputHeight;wire.resourceEpoch=1;wire.adapterLow=ad.AdapterLuid.LowPart;wire.adapterHigh=static_cast<uint32_t>(ad.AdapterLuid.HighPart);wire.frequency=state.qpcFrequency;
   Key session{};sessionKey(mapping.name,session);memcpy(wire.session,session.session,16);
   struct Output{ComPtr<ID3D11Texture2D> native;ComPtr<IDirect3DTexture9> imported;ComPtr<IDirect3DSurface9> surface;};
   Output outputs[3];const remixapi_dxvk_CopyRenderingOutputType types[]={REMIXAPI_DXVK_COPY_RENDERING_OUTPUT_TYPE_FINAL_COLOR,REMIXAPI_DXVK_COPY_RENDERING_OUTPUT_TYPE_DEPTH,REMIXAPI_DXVK_COPY_RENDERING_OUTPUT_TYPE_OBJECT_PICKING};
   for(unsigned i=0;i<3;++i){D3D11_TEXTURE2D_DESC t{};t.Width=outputWidth;t.Height=outputHeight;t.MipLevels=t.ArraySize=1;t.SampleDesc.Count=1;t.Format=i?DXGI_FORMAT_R32_FLOAT:DXGI_FORMAT_B8G8R8A8_UNORM;t.BindFlags=D3D11_BIND_RENDER_TARGET|D3D11_BIND_SHADER_RESOURCE;t.MiscFlags=D3D11_RESOURCE_MISC_SHARED;
    check(native->CreateTexture2D(&t,nullptr,&outputs[i].native),"ship shared texture");ComPtr<IDXGIResource> resource;check(outputs[i].native.As(&resource),"ship shared resource");HANDLE h=nullptr;check(resource->GetSharedHandle(&h),"ship shared handle");wire.handles[i]=canonicalHandle(h);
    check(device->CreateTexture(outputWidth,outputHeight,1,D3DUSAGE_RENDERTARGET,i?D3DFMT_R32F:D3DFMT_A8R8G8B8,D3DPOOL_DEFAULT,&outputs[i].imported,&h),"ship SDK import");check(outputs[i].imported->GetSurfaceLevel(0,&outputs[i].surface),"ship SDK surface");}
   ComPtr<IDirect3DQuery9> fence;check(device->CreateQuery(D3DQUERYTYPE_EVENT,&fence),"ship SDK fence");
   remixapi_Float4D clear{-1234,0,0,0},zero{};check(api.dxvk_SetDefaultOutput(types[1],&clear),"ship default depth");check(api.dxvk_SetDefaultOutput(types[2],&zero),"ship default picking");
   check(api.dxvk_CopyRenderingOutput(outputs[2].surface.Get(),types[2]),"ship prime picking");
   store(wire.ready,1);std::string name;for(const auto ch:mapping.name){if(ch>127)throw std::runtime_error("non ASCII session");name.push_back(static_cast<char>(ch));}std::cout<<"SESSION "<<name<<"\n";
   Seed seed{};remixapi_MeshHandle mesh=nullptr;remixapi_MaterialHandle material=nullptr;remixapi_LightHandle light=nullptr;
   std::vector<remixapi_HardcodedVertex> vertices;std::vector<uint32_t> indices;
   TexturedAsset texture;std::vector<remixapi_MeshInfoSurfaceTriangles> surfaces;
   RemixMaterialControls materialSettings;ULONGLONG lastMaterialPoll=0;unsigned materialRevisions=0;
   RemixLiveLights nativeLights;
   const auto started=GetTickCount64();ULONGLONG lastRender=0;bool loaded=false,inflight=false,resolutionLogged=false;Key rendering{};uint64_t requestAt=0,busyPublications=0;unsigned detailed=0;
   const ULONGLONG hostLimit=GetEnvironmentVariableW(L"SFC_LIGHT_TUNING",nullptr,0)?1980000ull:285000ull;
   while(!return_path::read(state.stop)&&!load(wire.stop)&&GetTickCount64()-started<hostLimit){
    MSG msg{};while(PeekMessageW(&msg,nullptr,0,0,PM_REMOVE)){TranslateMessage(&msg);DispatchMessageW(&msg);}
    if(load(wire.error))throw std::runtime_error("private receiver failed");
    if(!loaded){
     std::ifstream seedFile("live-asset.seed",std::ios::binary);if(!seedFile){Sleep(2);continue;}
     seedFile.read(reinterpret_cast<char*>(&seed),sizeof(seed));if(!seedFile||seedFile.peek()!=EOF)throw std::runtime_error("live seed size");
     memcpy(seed.key.session,wire.session,16);
     if(!validKey(seed.key)||!seed.model||!seed.source||seed.reserved||seed.key.sourcePid!=state.gamePid||memcmp(seed.key.sourceSession,scene.session,16)||seed.key.width!=wire.width||seed.key.height!=wire.height||textured!=(seed.key.diagnosticMode==BufferedMode))throw std::runtime_error("live source seed identity");
     std::ifstream f("live-mesh.bin",std::ios::binary|std::ios::ate);if(!f||f.tellg()>2*1024*1024)throw std::runtime_error("live mesh bound");const auto size=static_cast<size_t>(f.tellg());f.seekg(0);std::vector<BYTE> bytes(size);f.read(reinterpret_cast<char*>(bytes.data()),size);
     if(!f||size<32||hash(bytes.data(),bytes.size())!=seed.meshHash)throw std::runtime_error("live mesh hash");uint32_t h[4]{};memcpy(h,bytes.data(),16);
     if(h[0]!=0x53464347||h[1]!=1||!h[2]||h[2]>32768||h[2]%3||h[3]!=h[2]||size!=32+size_t(h[2])*32)throw std::runtime_error("live mesh schema");
     vertices.resize(h[2]);indices.resize(h[2]);for(unsigned i=0;i<h[2];++i){float v[8]{};memcpy(v,bytes.data()+32+size_t(i)*32,32);for(float x:v)if(!std::isfinite(x))throw std::runtime_error("live mesh finite");memcpy(vertices[i].position,v,12);memcpy(vertices[i].normal,v+3,12);memcpy(vertices[i].texcoord,v+6,8);vertices[i].color=0xffffffff;indices[i]=i;}
     // Remix SDK/DDS adapter only: never mutate captured or shared mesh data.
     if(textured){for(auto& vertex:vertices)vertex.texcoord[1]=sfc_remix_adapter::textureV(vertex.texcoord[1]);
      std::cout<<"REMIX_TEXTURE_ORIGIN captured_bottom_to_dds_top v=1-v raw_mesh_unchanged=1\n";}
     // Fixed diagnostic visibility,not an appearance improvement or game light.
     if(!textured){
     remixapi_MaterialInfoOpaqueEXT opaque{};opaque.sType=REMIXAPI_STRUCT_TYPE_MATERIAL_INFO_OPAQUE_EXT;opaque.albedoConstant={1,0,1};opaque.opacityConstant=1;opaque.roughnessConstant=1;
     // SDK C++ defaults (pinned reference remix.h):7=Always. Zero is Never,
     // not "disabled";zero-initialization otherwise erases ray-traced surfaces.
     opaque.alphaTestType=7;opaque.useDrawCallAlphaState=FALSE;
     remixapi_MaterialInfo mi{};mi.sType=REMIXAPI_STRUCT_TYPE_MATERIAL_INFO;mi.pNext=&opaque;mi.hash=0x5346434c01;mi.emissiveColorConstant={1,0,1};mi.emissiveIntensity=1;check(api.CreateMaterial(&mi,&material),"live diagnostic material");
     }
     remixapi_MeshInfoSurfaceTriangles surface{};surface.vertices_values=vertices.data();surface.vertices_count=vertices.size();surface.indices_values=indices.data();surface.indices_count=indices.size();surface.material=material;
     remixapi_MeshInfo info{};info.sType=REMIXAPI_STRUCT_TYPE_MESH_INFO;info.hash=0x5346434c02;info.surfaces_values=&surface;info.surfaces_count=1;
     if(textured){
      materialSettings.read();texture.load(static_cast<uint32_t>(vertices.size()));texture.create(api,materialSettings);
      std::cout<<"MATERIAL_APPLIED initial=1 revision="<<materialSettings.revision<<" roughness="<<materialSettings.values[0]<<" illumination="<<materialSettings.values[1]<<"\n";
      for(auto g:texture.groups){auto part=surface;part.indices_values=texture.indices.data()+g.first;part.indices_count=g.count;part.material=texture.handles[g.material];surfaces.push_back(part);}
      info.hash=seed.meshHash;info.surfaces_values=surfaces.data();info.surfaces_count=static_cast<uint32_t>(surfaces.size());
      std::cout<<"TEXTURED_ASSET_READY materials="<<texture.materials.size()<<" groups="<<texture.groups.size()<<" output="<<wire.width<<"x"<<wire.height<<" policy=delayed_additive100ms\n";
     }
     check(api.CreateMesh(&info,&mesh),"live fresh mesh");
     // Texture-only hulls need illumination at arbitrary world positions. The
     // legacy tiny origin light was ineffective hundreds of units from the hull.
     remixapi_LightInfoSphereEXT sphere{};sphere.sType=REMIXAPI_STRUCT_TYPE_LIGHT_INFO_SPHERE_EXT;sphere.radius=.1f;
     remixapi_LightInfoDistantEXT distant{};distant.sType=REMIXAPI_STRUCT_TYPE_LIGHT_INFO_DISTANT_EXT;distant.direction={0,-.70710678f,-.70710678f};distant.angularDiameterDegrees=.53f;
     remixapi_LightInfo li{};li.sType=REMIXAPI_STRUCT_TYPE_LIGHT_INFO;li.pNext=textured?static_cast<void*>(&distant):static_cast<void*>(&sphere);li.hash=textured?0x5346434c04:0x5346434c03;
     li.radiance=textured?remixapi_Float3D{1,1,1}:remixapi_Float3D{200,200,200};check(api.CreateLight(&li,&light),"live diagnostic light");
     {Lock lock(wire);if(!lock.held)throw std::runtime_error("seed registration lock");reg.seed=seed;store(reg.ready,1);}
     loaded=true;std::cout<<"FRESH_ASSET_READY owner="<<seed.key.owner<<" revision="<<seed.key.revision<<" vertices="<<vertices.size()<<" source_pid="<<seed.key.sourcePid<<"\n";
    }
    if(inflight){const HRESULT done=fence->GetData(nullptr,0,D3DGETDATA_FLUSH);
     if(done==S_FALSE){if(return_path::now()-requestAt>wire.frequency*5)throw std::runtime_error("live GPU5s timeout");Sleep(1);continue;}check(done,"live GPU completion");
     uint64_t unused[3]{};const auto outcome=publishCompleted(wire,rendering,unused,textured?requestAt:return_path::now(),inflight);
     if(outcome==Publication::Busy){++busyPublications;if(return_path::now()-requestAt>wire.frequency*5)throw std::runtime_error("live publication5s timeout");Sleep(1);continue;}
     if(outcome==Publication::Invalid)throw std::runtime_error("live publication invalid lease");
     const bool sent=outcome==Publication::Published;
     if(sent)InterlockedIncrement(&cmd.rendered);else InterlockedIncrement(&cmd.cancelled);
     if(detailed++<100)std::cout<<"FRESH_OUTPUT source_frame="<<rendering.frame<<" published="<<sent<<" elapsed_ticks="<<return_path::now()-requestAt<<"\n";
    }
    if(!return_path::read(state.armed)||!return_path::read(state.enabled)||GetTickCount64()-lastRender<34||load(wire.lease)!=Idle){Sleep(1);continue;}
    // Only after output GPU completion and receiver release;no SFC callback IO.
    if(textured&&GetTickCount64()-lastMaterialPoll>=500&&materialRevisions<256){
     lastMaterialPoll=GetTickCount64();auto next=materialSettings;
     if(next.read()){
      TexturedAsset candidate=texture;candidate.handles.clear();remixapi_MeshHandle replacement=nullptr;auto parts=surfaces;
      try{
       candidate.create(api,next);for(size_t i=0;i<parts.size();++i)parts[i].material=candidate.handles[texture.groups[i].material];
       remixapi_MeshInfo mi{};mi.sType=REMIXAPI_STRUCT_TYPE_MESH_INFO;mi.hash=seed.meshHash^next.revision;if(!mi.hash)mi.hash=1;mi.surfaces_values=parts.data();mi.surfaces_count=static_cast<uint32_t>(parts.size());
       check(api.CreateMesh(&mi,&replacement),"material revision mesh");
      }catch(const std::exception& e){if(replacement)api.DestroyMesh(replacement);replacement=nullptr;for(auto h:candidate.handles)if(h)api.DestroyMaterial(h);std::cout<<"MATERIAL_REJECTED "<<e.what()<<"\n";}
      if(replacement){
       // A retirement failure stops this optional host;never continue with a
       // partially destroyed previous mesh. Original SFC rendering is independent.
       check(api.DestroyMesh(mesh),"retire material revision mesh");for(auto h:texture.handles)check(api.DestroyMaterial(h),"retire material revision handle");
       mesh=replacement;texture.handles=std::move(candidate.handles);surfaces=std::move(parts);materialSettings=next;++materialRevisions;
       std::cout<<"MATERIAL_APPLIED revision="<<next.revision<<" roughness="<<next.values[0]<<" illumination="<<next.values[1]<<"\n";
      }
     }
    }
    sfc_calibration::Snapshot snap{};if(!sfc_calibration::read(scene.mailbox,snap)){Sleep(1);continue;}
    uint32_t thread=0;for(const auto& row:snap.owner)if(row[1]==seed.key.owner)thread=row[47];
    Key key{};std::array<uint32_t,96> row{};if(!makeKey(seed,snap,seed.key.sourcePid,thread,key,row)){Sleep(1);continue;}
    Camera cameraState{};if(!camera(row,cameraState)){InterlockedIncrement(&cmd.invalid);Sleep(1);continue;}
    if(lightWiring&&!nativeLights.update(api,seed,key,wire.frequency,cameraState.model)){Sleep(1);continue;}
    if(!offer(wire,cmd,key,row,return_path::now())||!ship_live::begin(wire,cmd,rendering,row,return_path::now()))continue;
    requestAt=return_path::now();lastRender=GetTickCount64();
    remixapi_CameraInfoParameterizedEXT cp{};cp.sType=REMIXAPI_STRUCT_TYPE_CAMERA_INFO_PARAMETERIZED_EXT;
    cp.position={cameraState.position[0],cameraState.position[1],cameraState.position[2]};cp.right={cameraState.right[0],cameraState.right[1],cameraState.right[2]};cp.up={cameraState.up[0],cameraState.up[1],cameraState.up[2]};cp.forward={cameraState.forward[0],cameraState.forward[1],cameraState.forward[2]};cp.fovYInDegrees=cameraState.fov;cp.aspect=cameraState.aspect;cp.nearPlane=cameraState.nearZ;cp.farPlane=cameraState.farZ;
    remixapi_CameraInfo ci{};ci.sType=REMIXAPI_STRUCT_TYPE_CAMERA_INFO;ci.pNext=&cp;check(api.SetupCamera(&ci),"live camera");
    remixapi_InstanceInfoObjectPickingEXT pick{};pick.sType=REMIXAPI_STRUCT_TYPE_INSTANCE_INFO_OBJECT_PICKING_EXT;pick.objectPickingValue=29;
    remixapi_InstanceInfo instance{};instance.sType=REMIXAPI_STRUCT_TYPE_INSTANCE_INFO;instance.pNext=&pick;instance.mesh=mesh;instance.doubleSided=1;memcpy(&instance.transform,cameraState.model,48);for(unsigned i=0;i<3;++i)instance.transform.matrix[i][3]+=key.worldOffset[i];
    check(api.DrawInstance(&instance),"live draw");if(lightWiring)nativeLights.draw(api);else check(api.DrawLightInstance(light),"live diagnostic lighting");check(api.Present(nullptr),"live present");
    // Check AFTER Present: the SDK can silently ResetEx to its HWND size there.
    ComPtr<IDirect3DSwapChain9> actualSwap;D3DPRESENT_PARAMETERS actual{};
    check(device->GetSwapChain(0,&actualSwap),"live actual swapchain");check(actualSwap->GetPresentParameters(&actual),"live actual present parameters");
    if(actual.BackBufferWidth!=outputWidth||actual.BackBufferHeight!=outputHeight)throw std::runtime_error("live rendering resolution drift");
    if(!resolutionLogged){std::cout<<"LIVE_RENDER_RESOLUTION client="<<outputWidth<<"x"<<outputHeight<<" swapchain="<<actual.BackBufferWidth<<"x"<<actual.BackBufferHeight<<" scale="<<(textured?"1.0":"legacy")<<"\n";resolutionLogged=true;}
    for(unsigned i=0;i<3;++i)check(api.dxvk_CopyRenderingOutput(outputs[i].surface.Get(),types[i]),"live three output copy");check(fence->Issue(D3DISSUE_END),"live output fence");inflight=true;
   }
   store(wire.ready,0);store(wire.stop,1);
   nativeLights.close(api);
   if(mesh)check(api.DestroyMesh(mesh),"live destroy mesh");if(material)check(api.DestroyMaterial(material),"live destroy material");if(light)check(api.DestroyLight(light),"live destroy light");
   for(auto handle:texture.handles)check(api.DestroyMaterial(handle),"retire textured material");
   check(fence->Issue(D3DISSUE_END),"live retire fence");const auto deadline=GetTickCount64()+5000;HRESULT done;
   while((done=fence->GetData(nullptr,0,D3DGETDATA_FLUSH))==S_FALSE){if(GetTickCount64()>deadline)throw std::runtime_error("live retirement timeout");Sleep(1);}check(done,"live retirement drain");
   std::cout<<"PRIVATE_RETURN_STOP offered="<<load(cmd.offered)<<" produced="<<load(cmd.rendered)<<" rejected="<<load(wire.rejected)<<" acquired="<<load(cmd.acquired)<<" drawn="<<load(cmd.drawn)<<" ack="<<load(wire.ack)<<" failed="<<load(cmd.failed)<<" publication_busy="<<busyPublications<<" cancelled="<<load(cmd.cancelled)<<"\n";result=0;
  }
 }catch(const std::exception& e){std::cout<<"LIVE_HOST_FAILED "<<e.what()<<"\n";}
 if(window)SetWindowLongPtrW(window,GWLP_WNDPROC,reinterpret_cast<LONG_PTR>(proc));
 if(api.Shutdown)std::cout<<"LIVE_SHUTDOWN api="<<static_cast<unsigned>(api.Shutdown())<<"\n";
 if(window)DestroyWindow(window);if(dll)FreeLibrary(dll);return result;
}

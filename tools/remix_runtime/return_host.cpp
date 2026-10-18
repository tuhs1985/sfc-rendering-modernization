#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <d3d9.h>
#include <d3d11.h>
#include <wrl/client.h>
#include <remix/remix_c.h>
#include <iostream>
#include <cmath>
#include "return_wire.h"
using Microsoft::WRL::ComPtr;
static void check(HRESULT h,const char* s){if(FAILED(h))throw std::runtime_error(s);}
static void check(remixapi_ErrorCode h,const char* s){if(h!=REMIXAPI_ERROR_CODE_SUCCESS)throw std::runtime_error(s);}
static LRESULT CALLBACK proc(HWND w,UINT m,WPARAM p,LPARAM l){return DefWindowProcW(w,m,p,l);}
int wmain(int argc,wchar_t** argv){
  std::cout.setf(std::ios::unitbuf);if(argc!=2)return 2;
  remixapi_Interface api{};HMODULE dll=nullptr;HWND window=nullptr;int result=1;
  try{
    return_path::Mapping channel(true);auto& s=*channel.state;
    struct StopOnExit{ return_path::State& state;~StopOnExit(){return_path::write(state.stop,1);} } stopOnExit{s};
    if(!wcscmp(argv[1],L"--observe-only")){
      // Same current-user control channel, NO Remix load, GPU or window. A
      // depth-binding question must not depend on an unrelated renderer crash.
      std::string name;for(const auto c:channel.name)name.push_back(static_cast<char>(c));
      std::cout<<"MODE OBSERVATION_ONLY no_runtime_loaded=1\nSESSION "<<name<<"\n";
      const auto begin=GetTickCount64();
      while(!return_path::read(s.stop)&&GetTickCount64()-begin<290000){
        if(!return_path::valid(s))throw std::runtime_error("observation channel invalid");Sleep(50);
      }
      const bool stopped=return_path::read(s.stop)!=0;
      std::cout<<"OBSERVATION_STOP samples="<<return_path::read(s.visibilitySamples)<<" bounded="<<stopped<<"\n";
      return stopped?0:120;
    }
    WNDCLASSW wc{};wc.lpfnWndProc=proc;wc.hInstance=GetModuleHandleW(nullptr);wc.lpszClassName=L"SFC_RemixReturnHost";
    if(!RegisterClassW(&wc))throw std::runtime_error("host window class");
    window=CreateWindowW(wc.lpszClassName,L"Remix output host",WS_POPUP,0,0,256,256,nullptr,nullptr,wc.hInstance,nullptr);if(!window)throw std::runtime_error("host window");
    check(remixapi_lib_loadRemixDllAndInitialize(argv[1],&api,&dll),"host SDK load");
    {
      ComPtr<IDirect3D9Ex> d9;ComPtr<IDirect3DDevice9Ex> initial;
      check(api.dxvk_CreateD3D9(FALSE,&d9),"host D3D9");
      D3DPRESENT_PARAMETERS pp{};pp.BackBufferWidth=pp.BackBufferHeight=256;pp.BackBufferCount=1;pp.BackBufferFormat=D3DFMT_X8R8G8B8;pp.Windowed=TRUE;pp.hDeviceWindow=window;pp.SwapEffect=D3DSWAPEFFECT_DISCARD;pp.PresentationInterval=D3DPRESENT_INTERVAL_IMMEDIATE;
      check(d9->CreateDeviceEx(0,D3DDEVTYPE_HAL,window,D3DCREATE_HARDWARE_VERTEXPROCESSING,&pp,nullptr,&initial),"host device");
      check(api.dxvk_RegisterD3D9Device(initial.Get()),"host registration");auto* device=initial.Detach();
      remixapi_HardcodedVertex vertices[3]{};const float xy[3][2]={{-2,-2},{0,2},{2,-2}};const uint32_t indices[]={0,1,2};
      for(unsigned i=0;i<3;++i){vertices[i].position[0]=xy[i][0];vertices[i].position[1]=xy[i][1];vertices[i].position[2]=6;vertices[i].normal[2]=-1;vertices[i].color=0xFFFFFFFF;}
      remixapi_MeshInfoSurfaceTriangles triangles{};triangles.vertices_values=vertices;triangles.vertices_count=3;triangles.indices_values=indices;triangles.indices_count=3;
      remixapi_MeshInfo mesh{};mesh.sType=REMIXAPI_STRUCT_TYPE_MESH_INFO;mesh.hash=0x5346432001;mesh.surfaces_values=&triangles;mesh.surfaces_count=1;remixapi_MeshHandle mh=nullptr;check(api.CreateMesh(&mesh,&mh),"host mesh");
      remixapi_LightInfoSphereEXT sphere{};sphere.sType=REMIXAPI_STRUCT_TYPE_LIGHT_INFO_SPHERE_EXT;sphere.position={0,-1,0};sphere.radius=0.1f;
      remixapi_LightInfo light{};light.sType=REMIXAPI_STRUCT_TYPE_LIGHT_INFO;light.pNext=&sphere;light.hash=0x5346432002;light.radiance={100,200,100};remixapi_LightHandle lh=nullptr;check(api.CreateLight(&light,&lh),"host light");
      ComPtr<IDirect3DTexture9> output;ComPtr<IDirect3DSurface9> surface;ComPtr<IDirect3DQuery9> completion;check(device->CreateQuery(D3DQUERYTYPE_EVENT,&completion),"host query");
      ComPtr<ID3D11Device> verifier;ComPtr<ID3D11DeviceContext> verifierContext;ComPtr<ID3D11Texture2D> nativeLease;
      check(D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,nullptr,0,D3D11_SDK_VERSION,&verifier,nullptr,&verifierContext),"native handle verifier");
      LONG epoch=0;bool needsFirstPacket=false;uint64_t frame=0;const auto start=GetTickCount64();ULONGLONG activeAt=0,lastPublish=0;
      std::string asciiName;for(const auto c:channel.name){if(c>127)throw std::runtime_error("non-ASCII session identifier");asciiName.push_back(static_cast<char>(c));}
      std::cout<<"SESSION "<<asciiName<<"\n";
      while(!return_path::read(s.stop)&&GetTickCount64()-start<290000){
        MSG message{};while(PeekMessageW(&message,nullptr,0,0,PM_REMOVE)){TranslateMessage(&message);DispatchMessageW(&message);}
        if(!return_path::valid(s)||return_path::read(s.error))throw std::runtime_error("host invalid/disconnected channel");
        remixapi_CameraInfoParameterizedEXT cp{};cp.sType=REMIXAPI_STRUCT_TYPE_CAMERA_INFO_PARAMETERIZED_EXT;cp.forward={0,0,1};cp.up={0,1,0};cp.right={1,0,0};cp.fovYInDegrees=70;cp.aspect=1;cp.nearPlane=0.1f;cp.farPlane=100;
        remixapi_CameraInfo camera{};camera.sType=REMIXAPI_STRUCT_TYPE_CAMERA_INFO;camera.pNext=&cp;check(api.SetupCamera(&camera),"host camera");
        remixapi_InstanceInfo instance{};instance.sType=REMIXAPI_STRUCT_TYPE_INSTANCE_INFO;instance.mesh=mh;instance.doubleSided=1;
        const auto t=static_cast<float>(GetTickCount64()-start)/1000.0f;
        instance.transform={{{std::cos(t),-std::sin(t),0,std::sin(t)*1.5f},{std::sin(t),std::cos(t),0,0},{0,0,1,0}}};
        check(api.DrawInstance(&instance),"host draw");check(api.DrawLightInstance(lh),"host light instance");check(api.Present(nullptr),"host present");++frame;
        if(return_path::read(s.ready)&&return_path::read(s.armed)&&return_path::read(s.enabled)){
          if(!activeAt)activeAt=GetTickCount64();if(GetTickCount64()-activeAt>90000)break;
          const auto current=return_path::read(s.epoch);
          if(current!=epoch){
            const auto handleValue=s.sharedHandle;HANDLE shared=reinterpret_cast<HANDLE>(static_cast<uintptr_t>(handleValue));
            if(!current||!shared||handleValue>UINT32_MAX)throw std::runtime_error("host invalid output descriptor");
            if(!return_path::read(s.ready)||return_path::read(s.epoch)!=current)continue;
            ComPtr<ID3D11Texture2D> lease;
            const auto opened=verifier->OpenSharedResource(shared,IID_PPV_ARGS(&lease));
            if(!return_path::read(s.ready)||return_path::read(s.epoch)!=current)continue;
            check(opened,"host invalid native handle");D3D11_TEXTURE2D_DESC desc{};lease->GetDesc(&desc);
            if(desc.Width!=256||desc.Height!=256||desc.Format!=DXGI_FORMAT_B8G8R8A8_UNORM||desc.SampleDesc.Count!=1||desc.MipLevels!=1||desc.ArraySize!=1||desc.Usage!=D3D11_USAGE_DEFAULT||!(desc.MiscFlags&D3D11_RESOURCE_MISC_SHARED))throw std::runtime_error("host incompatible native descriptor");
            surface.Reset();output.Reset();nativeLease=lease;
            check(device->CreateTexture(256,256,1,D3DUSAGE_RENDERTARGET,D3DFMT_A8R8G8B8,D3DPOOL_DEFAULT,&output,&shared),"host native texture import");check(output->GetSurfaceLevel(0,&surface),"host surface");epoch=current;needsFirstPacket=true;
          }
          const LONG prior=return_path::read(s.produced);
          const LONG ack=return_path::read(s.acknowledged);
          if((needsFirstPacket||prior==ack)&&return_path::read(s.ready)&&return_path::read(s.epoch)==epoch&&GetTickCount64()-lastPublish>=34){
            check(api.dxvk_CopyRenderingOutput(surface.Get(),REMIXAPI_DXVK_COPY_RENDERING_OUTPUT_TYPE_FINAL_COLOR),"host output copy");
            check(completion->Issue(D3DISSUE_END),"host fence issue");const auto deadline=GetTickCount64()+5000;HRESULT ready;
            while((ready=completion->GetData(nullptr,0,D3DGETDATA_FLUSH))==S_FALSE){if(GetTickCount64()>deadline)throw std::runtime_error("host GPU completion timeout");Sleep(1);}check(ready,"host GPU completion");
            if(!return_path::read(s.stop)&&return_path::read(s.ready)&&return_path::read(s.epoch)==epoch){
              s.renderedAt=return_path::now();s.renderFrame=frame;return_path::write(s.renderEpoch,epoch);return_path::write(s.produced,prior+1);lastPublish=GetTickCount64();needsFirstPacket=false;
              if(prior<5||prior%30==0)std::cout<<"OUTPUT seq="<<prior+1<<" runtime_frame="<<frame<<" epoch="<<epoch<<" qpc="<<s.renderedAt<<"\n";
            }
          }
        }
        Sleep(34);
      }
      return_path::write(s.stop,1);surface.Reset();output.Reset();
      check(api.DestroyMesh(mh),"host destroy mesh");check(api.DestroyLight(lh),"host destroy light");
      // SDK retirement is queued on the command stream. Drain that work before
      // scoped COM resources disappear and the registered SDK device shuts down.
      // Never guess a Release count: Shutdown owns registered-device teardown.
      check(completion->Issue(D3DISSUE_END),"host shutdown fence issue");
      const auto shutdownDeadline=GetTickCount64()+5000;HRESULT shutdownReady;
      while((shutdownReady=completion->GetData(nullptr,0,D3DGETDATA_FLUSH))==S_FALSE){
        if(GetTickCount64()>shutdownDeadline)throw std::runtime_error("host shutdown fence timeout");Sleep(1);
      }
      check(shutdownReady,"host shutdown fence");
      std::cout<<"HOST_RETIREMENT_DRAINED\n";
      std::cout<<"HOST_STOP frames="<<frame<<" produced="<<return_path::read(s.produced)<<" acknowledged="<<return_path::read(s.acknowledged)<<" drawn="<<return_path::read(s.drawCount)<<"\n";
      result=0;
    }
  }catch(const std::exception& e){std::cout<<"HOST_FAILED "<<e.what()<<"\n";}
  if(window)SetWindowLongPtrW(window,GWLP_WNDPROC,reinterpret_cast<LONG_PTR>(proc));
  if(api.Shutdown)std::cout<<"HOST_SHUTDOWN api="<<static_cast<unsigned>(api.Shutdown())<<"\n";
  if(window)DestroyWindow(window);if(dll)FreeLibrary(dll);return result;
}

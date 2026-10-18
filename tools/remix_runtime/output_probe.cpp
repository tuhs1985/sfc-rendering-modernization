// Standalone prerequisite probe; never loads SFC or installs hooks.
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <d3d9.h>
#include <d3d11.h>
#include <dxgi.h>
#include <wrl/client.h>
#include <remix/remix_c.h>
#include <iostream>
#include <stdexcept>
#include <cmath>
#include <fstream>
#include <functional>
#include "output_channel.h"
using Microsoft::WRL::ComPtr;
static void hr(const char* stage, HRESULT value) {
  std::cout << stage << " hr=0x" << std::hex << static_cast<unsigned long>(value) << std::dec << '\n';
  if (FAILED(value)) throw std::runtime_error(stage);
}
static void api(const char* stage, remixapi_ErrorCode value) {
  std::cout << stage << " api=" << static_cast<unsigned>(value) << '\n';
  if (value != REMIXAPI_ERROR_CODE_SUCCESS) throw std::runtime_error(stage);
}
static LRESULT CALLBACK wndproc(HWND w, UINT m, WPARAM p, LPARAM l) { return DefWindowProcW(w,m,p,l); }
static void wait9(IDirect3DQuery9* query) {
  hr("producer_issue",query->Issue(D3DISSUE_END));
  const auto end=GetTickCount64()+5000;
  HRESULT result;
  while((result=query->GetData(nullptr,0,D3DGETDATA_FLUSH))==S_FALSE) {
    if(GetTickCount64()>end) throw std::runtime_error("producer GPU timeout");
    Sleep(1);
  }
  hr("producer_complete",result);
}
static void renderDiagnostic(remixapi_Interface& r, IDirect3DDevice9Ex* device,
    IDirect3DSurface9* transferTarget=nullptr,
    const std::function<void(uint32_t,uint64_t)>& onOutput={}) {
  // First rendering control uses the SDK sample's default material. Explicit
  // material registration is deferred until this output path is verified.
  remixapi_MaterialHandle mat=nullptr;
  remixapi_HardcodedVertex vertices[3]{};
  const float xy[3][2]={{-2,-2},{0,2},{2,-2}};
  for(unsigned i=0;i<3;++i){vertices[i].position[0]=xy[i][0];vertices[i].position[1]=xy[i][1];vertices[i].position[2]=6;vertices[i].normal[2]=-1;vertices[i].color=0xFFFFFFFF;}
  const uint32_t indices[]={0,1,2};
  remixapi_MeshInfoSurfaceTriangles tri{};tri.vertices_values=vertices;tri.vertices_count=3;tri.indices_values=indices;tri.indices_count=3;tri.material=mat;
  remixapi_MeshInfo mesh{};mesh.sType=REMIXAPI_STRUCT_TYPE_MESH_INFO;mesh.hash=0x5346431002;mesh.surfaces_values=&tri;mesh.surfaces_count=1;
  remixapi_MeshHandle mh=nullptr;api("mesh",r.CreateMesh(&mesh,&mh));
  remixapi_LightInfoSphereEXT sphere{};sphere.sType=REMIXAPI_STRUCT_TYPE_LIGHT_INFO_SPHERE_EXT;sphere.position={0,-1,0};sphere.radius=0.1f;
  remixapi_LightInfo light{};light.sType=REMIXAPI_STRUCT_TYPE_LIGHT_INFO;light.pNext=&sphere;light.hash=0x5346431003;light.radiance={100,200,100};
  remixapi_LightHandle lh=nullptr;api("light",r.CreateLight(&light,&lh));
  ComPtr<IDirect3DSurface9> output,readback;
  if(transferTarget)output=transferTarget;
  else hr("private_output",device->CreateRenderTarget(256,256,D3DFMT_A8R8G8B8,D3DMULTISAMPLE_NONE,0,FALSE,&output,nullptr));
  ComPtr<IDirect3DQuery9> outputDone;hr("output_event_query",device->CreateQuery(D3DQUERYTYPE_EVENT,&outputDone));
  hr("private_readback",device->CreateOffscreenPlainSurface(256,256,D3DFMT_A8R8G8B8,D3DPOOL_SYSTEMMEM,&readback,nullptr));
  unsigned framesWithTriangle=0;
  for(unsigned frame=0;frame<32;++frame){
    MSG msg{};while(PeekMessageW(&msg,nullptr,0,0,PM_REMOVE)){TranslateMessage(&msg);DispatchMessageW(&msg);}
    remixapi_CameraInfoParameterizedEXT cp{};cp.sType=REMIXAPI_STRUCT_TYPE_CAMERA_INFO_PARAMETERIZED_EXT;
    cp.forward={0,0,1};cp.up={0,1,0};cp.right={1,0,0};cp.fovYInDegrees=70;cp.aspect=1;cp.nearPlane=0.1f;cp.farPlane=100;
    remixapi_CameraInfo camera{};camera.sType=REMIXAPI_STRUCT_TYPE_CAMERA_INFO;camera.pNext=&cp;
    api("camera",r.SetupCamera(&camera));
    remixapi_InstanceInfo instance{};instance.sType=REMIXAPI_STRUCT_TYPE_INSTANCE_INFO;instance.mesh=mh;instance.doubleSided=1;
    instance.transform={{{1,0,0,frame<16?-1.0f:1.0f},{0,1,0,0},{0,0,1,0}}};
    api("draw",r.DrawInstance(&instance));api("draw_light",r.DrawLightInstance(lh));api("present",r.Present(nullptr));
    if(frame==15||frame==31){
      api("copy_rendering_output",r.dxvk_CopyRenderingOutput(output.Get(),REMIXAPI_DXVK_COPY_RENDERING_OUTPUT_TYPE_FINAL_COLOR));
      wait9(outputDone.Get()); // Explicit producer GPU completion, independent of validation readback.
      hr("read_rendering_output",device->GetRenderTargetData(output.Get(),readback.Get()));
      D3DLOCKED_RECT pixels{};hr("lock_output",readback->LockRect(&pixels,nullptr,D3DLOCK_READONLY));
      uint64_t hash=14695981039346656037ULL;unsigned colored=0;unsigned maxRgb[3]{};
      BITMAPFILEHEADER fileHeader{};fileHeader.bfType=0x4D42;fileHeader.bfOffBits=sizeof(BITMAPFILEHEADER)+sizeof(BITMAPINFOHEADER);fileHeader.bfSize=fileHeader.bfOffBits+256*256*4;
      BITMAPINFOHEADER bitmap{};bitmap.biSize=sizeof(bitmap);bitmap.biWidth=256;bitmap.biHeight=-256;bitmap.biPlanes=1;bitmap.biBitCount=32;bitmap.biCompression=BI_RGB;
      std::ofstream snapshot(frame==15?"output-15.bmp":"output-31.bmp",std::ios::binary);
      snapshot.write(reinterpret_cast<const char*>(&fileHeader),sizeof(fileHeader));snapshot.write(reinterpret_cast<const char*>(&bitmap),sizeof(bitmap));
      for(unsigned y=0;y<256;++y){const auto* row=static_cast<const unsigned char*>(pixels.pBits)+y*pixels.Pitch;
        snapshot.write(reinterpret_cast<const char*>(row),256*4);
        for(unsigned x=0;x<256;++x){for(unsigned b=0;b<4;++b){hash^=row[x*4+b];hash*=1099511628211ULL;}
          for(unsigned b=0;b<3;++b)if(row[x*4+b]>maxRgb[b])maxRgb[b]=row[x*4+b];
          if(row[x*4+1]>row[x*4]+20&&row[x*4+1]>row[x*4+2]+20)++colored;}}
      hr("unlock_output",readback->UnlockRect());
      std::cout<<"runtime_frame="<<frame<<" output_fnv="<<hash<<" green_pixels="<<colored<<" max_bgr="<<maxRgb[0]<<","<<maxRgb[1]<<","<<maxRgb[2]<<"\n";
      if(colored)++framesWithTriangle;
      if(onOutput)onOutput(frame,hash);
    }
    Sleep(20);
  }
  api("destroy_mesh",r.DestroyMesh(mh));if(mat)api("destroy_material",r.DestroyMaterial(mat));api("destroy_light",r.DestroyLight(lh));
  if(framesWithTriangle!=2)throw std::runtime_error("diagnostic triangle not validated in both actual output snapshots");
  std::cout<<"REMIX_RENDERING_READBACK_PASS (two validation snapshots, not GPU return path)\n";
}
#include "coverage_probe.h"
int wmain(int argc,wchar_t** argv) {
  std::cout.setf(std::ios::unitbuf);
  if(argc==3&&(!wcscmp(argv[1],L"--consumer")||!wcscmp(argv[1],L"--consumer-slow")||!wcscmp(argv[1],L"--consumer-exit"))){
    try{return output_probe::consume(argv[2],!wcscmp(argv[1],L"--consumer-slow")?1:(!wcscmp(argv[1],L"--consumer-exit")?2:0));}catch(...){return 3;}
  }
  if(argc!=3 || (wcscmp(argv[2],L"coverage") && wcscmp(argv[2],L"sharing") && wcscmp(argv[2],L"rendering") && wcscmp(argv[2],L"crossprocess") && wcscmp(argv[2],L"crossprocess-slow") && wcscmp(argv[2],L"crossprocess-exit") && wcscmp(argv[2],L"crossprocess-x86"))) return 2;
  remixapi_Interface r{}; HMODULE module=nullptr;
  HWND window=nullptr;
  int exitCode=1;
  try {
    WNDCLASSW wc{};wc.lpfnWndProc=wndproc;wc.hInstance=GetModuleHandleW(nullptr);wc.lpszClassName=L"SFC_RemixOutputProbe";
    if(!RegisterClassW(&wc)) throw std::runtime_error("RegisterClass");
    window=CreateWindowW(wc.lpszClassName,L"Standalone Remix output probe",WS_POPUP,0,0,256,256,nullptr,nullptr,wc.hInstance,nullptr);
    if(!window) throw std::runtime_error("CreateWindow");
    api("load",remixapi_lib_loadRemixDllAndInitialize(argv[1],&r,&module));
    // Inner scope releases all owned resource references before SDK Shutdown.
    {
      ComPtr<IDirect3D9Ex> d9; ComPtr<IDirect3DDevice9Ex> ownedDevice;
      api("create_d3d9",r.dxvk_CreateD3D9(FALSE,&d9));
      D3DPRESENT_PARAMETERS pp{};pp.BackBufferWidth=256;pp.BackBufferHeight=256;
      pp.BackBufferFormat=D3DFMT_X8R8G8B8;pp.BackBufferCount=1;pp.SwapEffect=D3DSWAPEFFECT_DISCARD;
      pp.hDeviceWindow=window;pp.Windowed=TRUE;pp.PresentationInterval=D3DPRESENT_INTERVAL_IMMEDIATE;
      hr("create_device",d9->CreateDeviceEx(0,D3DDEVTYPE_HAL,window,D3DCREATE_HARDWARE_VERTEXPROCESSING,&pp,nullptr,&ownedDevice));
      api("register",r.dxvk_RegisterD3D9Device(ownedDevice.Get()));
      auto* device=ownedDevice.Detach(); // SDK now owns the registered lifetime, including error exits.
      // Register retains its own D3D9 ref; SDK owns the device at Shutdown.
      // Keep device reference non-owning after resource scope, avoiding forced
      // SDK release loops against a live ComPtr.
      if(!wcscmp(argv[2],L"coverage")){renderCoverage(r,device);exitCode=0;}
      else if(!wcsncmp(argv[2],L"crossprocess",12)){
        output_probe::Channel channel(true);
        channel.start(!wcscmp(argv[2],L"crossprocess-slow")?L"--consumer-slow":(!wcscmp(argv[2],L"crossprocess-exit")?L"--consumer-exit":L"--consumer"),!wcscmp(argv[2],L"crossprocess-x86"));
        HANDLE shared=reinterpret_cast<HANDLE>(static_cast<uintptr_t>(channel.state->sharedHandle));
        ComPtr<IDirect3DTexture9> transferred;ComPtr<IDirect3DSurface9> surface;
        hr("crossprocess_import",device->CreateTexture(256,256,1,D3DUSAGE_RENDERTARGET,D3DFMT_A8R8G8B8,D3DPOOL_DEFAULT,&transferred,&shared));
        hr("crossprocess_surface",transferred->GetSurfaceLevel(0,&surface));
        ShowWindow(window,SW_SHOWNOACTIVATE);UpdateWindow(window);
        double firstX=0;
        renderDiagnostic(r,device,surface.Get(),[&](uint32_t frame,uint64_t hash){
          channel.publish(frame==15?1:2,frame,hash);
          const double x=static_cast<double>(channel.state->centroidNumerator)/channel.state->greenPixels;
          std::cout<<"crossprocess_frame="<<frame<<" exact_hash_match=1 green="<<channel.state->greenPixels<<" centroid_x="<<x<<"\n";
          if(frame==15)firstX=x;else if(x<firstX+20)throw std::runtime_error("unexpected output orientation/movement");
        });
        surface.Reset();transferred.Reset();channel.finish();
        std::cout<<"CROSS_PROCESS_REMIX_GPU_OUTPUT_PASS\n";exitCode=0;
      }else{
      if(!wcscmp(argv[2],L"rendering")) {ShowWindow(window,SW_SHOWNOACTIVATE);UpdateWindow(window);renderDiagnostic(r,device);}
      ComPtr<ID3D11Device> consumer;ComPtr<ID3D11DeviceContext> context;
      D3D_FEATURE_LEVEL feature{};
      hr("create_d3d11",D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,nullptr,0,D3D11_SDK_VERSION,&consumer,&feature,&context));
      ComPtr<IDirect3DTexture9> texture;ComPtr<ID3D11Texture2D> imported;
      const D3DFORMAT formats[]={D3DFMT_A8B8G8R8,D3DFMT_A8R8G8B8,D3DFMT_A16B16G16R16F};
      for(const auto format:formats){
        HANDLE shared=nullptr;texture.Reset();imported.Reset();
        const HRESULT created=device->CreateTexture(256,256,1,D3DUSAGE_RENDERTARGET,format,D3DPOOL_DEFAULT,&texture,&shared);
        std::cout<<"share_format="<<static_cast<unsigned>(format)<<" create=0x"<<std::hex<<static_cast<unsigned long>(created)<<std::dec<<" handle="<<shared<<"\n";
        if(SUCCEEDED(created)&&shared){
          const HRESULT opened=consumer->OpenSharedResource(shared,IID_PPV_ARGS(&imported));
          std::cout<<"native_open=0x"<<std::hex<<static_cast<unsigned long>(opened)<<std::dec<<"\n";
          if(SUCCEEDED(opened))break;
        }
      }
      if(!imported){
        // Native-native control, then public reverse-direction import. No Vulkan internals.
        D3D11_TEXTURE2D_DESC nativeDesc{};nativeDesc.Width=256;nativeDesc.Height=256;nativeDesc.MipLevels=1;nativeDesc.ArraySize=1;
        nativeDesc.Format=DXGI_FORMAT_B8G8R8A8_UNORM;nativeDesc.SampleDesc.Count=1;nativeDesc.Usage=D3D11_USAGE_DEFAULT;
        nativeDesc.BindFlags=D3D11_BIND_RENDER_TARGET|D3D11_BIND_SHADER_RESOURCE;nativeDesc.MiscFlags=D3D11_RESOURCE_MISC_SHARED;
        ComPtr<ID3D11Texture2D> native;hr("native_shared_create",consumer->CreateTexture2D(&nativeDesc,nullptr,&native));
        ComPtr<IDXGIResource> resource;hr("native_dxgi",native.As(&resource));HANDLE nativeHandle=nullptr;hr("native_get_handle",resource->GetSharedHandle(&nativeHandle));
        ComPtr<ID3D11Device> second;ComPtr<ID3D11DeviceContext> secondContext;
        hr("native_control_device",D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,nullptr,0,D3D11_SDK_VERSION,&second,nullptr,&secondContext));
        ComPtr<ID3D11Texture2D> control;hr("native_native_open_control",second->OpenSharedResource(nativeHandle,IID_PPV_ARGS(&control)));
        ComPtr<IDirect3DTexture9> reverse;
        const HRESULT reverseResult=device->CreateTexture(256,256,1,D3DUSAGE_RENDERTARGET,D3DFMT_A8R8G8B8,D3DPOOL_DEFAULT,&reverse,&nativeHandle);
        std::cout<<"native_to_remix_import=0x"<<std::hex<<static_cast<unsigned long>(reverseResult)<<std::dec<<"\n";
        if(SUCCEEDED(reverseResult)){
          ComPtr<IDirect3DSurface9> reverseSurface;hr("reverse_surface",reverse->GetSurfaceLevel(0,&reverseSurface));
          ComPtr<IDirect3DQuery9> done;hr("reverse_query",device->CreateQuery(D3DQUERYTYPE_EVENT,&done));
          nativeDesc.Usage=D3D11_USAGE_STAGING;nativeDesc.BindFlags=0;nativeDesc.MiscFlags=0;nativeDesc.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
          ComPtr<ID3D11Texture2D> staging;hr("reverse_staging",second->CreateTexture2D(&nativeDesc,nullptr,&staging));
          for(unsigned seq=1;seq<=3;++seq){
            hr("reverse_gpu_write",device->ColorFill(reverseSurface.Get(),nullptr,D3DCOLOR_ARGB(255,seq*19,71,139)));
            wait9(done.Get());
            secondContext->CopyResource(staging.Get(),control.Get());secondContext->Flush();
            D3D11_MAPPED_SUBRESOURCE pixels{};hr("reverse_consume",secondContext->Map(staging.Get(),0,D3D11_MAP_READ,0,&pixels));
            const auto* p=static_cast<const unsigned char*>(pixels.pData);
            const bool match=p[0]==139&&p[1]==71&&p[2]==seq*19&&p[3]==255;
            std::cout<<"reverse_sequence="<<seq<<" bgra="<<unsigned(p[0])<<","<<unsigned(p[1])<<","<<unsigned(p[2])<<","<<unsigned(p[3])<<" match="<<match<<"\n";
            secondContext->Unmap(staging.Get(),0);
            if(!match)throw std::runtime_error("reverse GPU pixels mismatch");
          }
          std::cout<<"REVERSE_SHARED_GPU_REUSE_PASS (D3D9 clear, not Remix rendering or cross-process proof)\n";
          exitCode=0;
        }else{
        throw std::runtime_error("all forward native D3D11 imports rejected; reverse result recorded separately");
        }
      }else{
      D3D11_TEXTURE2D_DESC desc{};imported->GetDesc(&desc);
      if(desc.Width!=256||desc.Height!=256||desc.Format!=DXGI_FORMAT_R8G8B8A8_UNORM) throw std::runtime_error("import metadata mismatch; sentinel only qualified for RGBA8");
      ComPtr<IDirect3DSurface9> surface;hr("surface",texture->GetSurfaceLevel(0,&surface));
      ComPtr<IDirect3DQuery9> done;hr("query9",device->CreateQuery(D3DQUERYTYPE_EVENT,&done));
      hr("producer_sentinel",device->ColorFill(surface.Get(),nullptr,D3DCOLOR_ARGB(255,19,71,139)));
      wait9(done.Get());
      desc.Usage=D3D11_USAGE_STAGING;desc.BindFlags=0;desc.CPUAccessFlags=D3D11_CPU_ACCESS_READ;desc.MiscFlags=0;
      ComPtr<ID3D11Texture2D> staging;hr("staging",consumer->CreateTexture2D(&desc,nullptr,&staging));
      context->CopyResource(staging.Get(),imported.Get());context->Flush();
      D3D11_MAPPED_SUBRESOURCE mapped{};hr("map_sentinel",context->Map(staging.Get(),0,D3D11_MAP_READ,0,&mapped));
      const auto* pixel=static_cast<const unsigned char*>(mapped.pData);
      const bool match=pixel[0]==19&&pixel[1]==71&&pixel[2]==139&&pixel[3]==255;
      std::cout<<"sentinel_rgba="<<unsigned(pixel[0])<<","<<unsigned(pixel[1])<<","<<unsigned(pixel[2])<<","<<unsigned(pixel[3])<<" match="<<match<<"\n";
      context->Unmap(staging.Get(),0);
      if(!match) throw std::runtime_error("GPU import sentinel mismatch");
      std::cout<<"PRELIMINARY_SHARED_GPU_IMPORT_PASS (not Remix rendering or cross-process proof)\n";
      exitCode=0;
      }
      }
    }
  }catch(const std::exception& e){std::cout<<"FAILED stage="<<e.what()<<"\n";}
  // This is our own standalone window, not SFC. Restore its host procedure
  // before the SDK releases the device used by its window subclass.
  if(window)SetWindowLongPtrW(window,GWLP_WNDPROC,reinterpret_cast<LONG_PTR>(wndproc));
  if(r.Shutdown){api("shutdown",r.Shutdown());}
  if(window)DestroyWindow(window);
  // Any runtime-installed window procedure must still be resident at destruction.
  if(module) FreeLibrary(module);
  return exitCode;
}

// Offline plain D3D9 consumer. No SFC hook,Remix SDK,USD or live IPC dependency.
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <d3d9.h>
#include <tlhelp32.h>
#include <wrl/client.h>
#include <algorithm>
#include <array>
#include <cmath>
#include <cstring>
#include <cwctype>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <set>
#include <stdexcept>
#include <vector>
using Microsoft::WRL::ComPtr;
namespace fs=std::filesystem;
// Diagnostic totals belong to the calling thread. Asset preparation also uses
// require(); sharing this counter with the renderer was an unnecessary race.
static thread_local unsigned checks=0;
static void require(bool b,const char* why){if(!b)throw std::runtime_error(why);++checks;}
static void ok(HRESULT h,const char* why){if(FAILED(h)){std::cerr<<"HRESULT "<<std::hex<<static_cast<unsigned long>(h)<<std::dec<<' ';throw std::runtime_error(why);}}
static std::vector<unsigned char> read(const fs::path& path,size_t cap){
 std::ifstream f(path,std::ios::binary|std::ios::ate);require(bool(f),"input missing");const auto length=f.tellg();
 require(length>=0&&static_cast<uint64_t>(length)<=cap,"input byte cap");std::vector<unsigned char> out(static_cast<size_t>(length));
 f.seekg(0);f.read(reinterpret_cast<char*>(out.data()),static_cast<std::streamsize>(out.size()));require(bool(f),"input truncated");return out;
}
template<class T>static T take(const std::vector<unsigned char>& bytes,size_t& offset){
 require(offset<=bytes.size()&&sizeof(T)<=bytes.size()-offset,"packet truncated");T value{};memcpy(&value,bytes.data()+offset,sizeof(T));offset+=sizeof(T);return value;
}
struct Vertex{float p[3],n[3],uv[2];};
struct Group{uint32_t id,material,first,count;};
struct Frame{uint32_t owner,revision,frame,active;float model[16],view[16],projection[16],viewport[4];};
static_assert(sizeof(Vertex)==32&&sizeof(Group)==16&&sizeof(Frame)==224);
struct Scene{uint32_t width=0,height=0;std::vector<Vertex> vertices;std::vector<uint32_t> indices;std::vector<Group> groups;std::vector<Frame> frames;};
static Scene load(const fs::path& root){
 auto b=read(root/L"scene.bin",2*1024*1024);size_t at=0;auto h=take<std::array<uint32_t,8>>(b,at);
 require(h[0]==0x31534653&&h[1]==1&&h[2]>=3&&h[2]<=32768&&h[2]%3==0&&h[3]==h[2]&&h[4]&&h[4]<=256&&h[5]&&h[5]<=16&&h[6]&&h[6]<=1920&&h[7]&&h[7]<=1080,"scene schema");
 Scene s;s.width=h[6];s.height=h[7];
 for(uint32_t i=0;i<h[2];++i){auto v=take<Vertex>(b,at);for(float x:v.p)require(std::isfinite(x),"position finite");for(float x:v.n)require(std::isfinite(x),"normal finite");for(float x:v.uv)require(std::isfinite(x),"UV finite");s.vertices.push_back(v);}
 std::vector<bool> used(h[2]);for(uint32_t i=0;i<h[3];++i){auto index=take<uint32_t>(b,at);require(index<h[2]&&!used[index],"index coverage");used[index]=true;s.indices.push_back(index);}
 uint32_t cursor=0;std::set<uint32_t> ids;
 for(uint32_t i=0;i<h[4];++i){auto g=take<Group>(b,at);require(g.material<256&&g.first==cursor&&g.count&&g.count%3==0&&g.count<=h[3]-cursor&&ids.insert(g.id).second,"group coverage");cursor+=g.count;s.groups.push_back(g);}require(cursor==h[3],"complete groups");
 for(uint32_t i=0;i<h[5];++i){auto f=take<Frame>(b,at);require(f.owner&&f.revision&&f.frame&&f.active<=1,"frame identity");
  for(float x:f.model)require(std::isfinite(x),"model finite");for(float x:f.view)require(std::isfinite(x),"view finite");for(float x:f.projection)require(std::isfinite(x),"projection finite");for(float x:f.viewport)require(std::isfinite(x),"viewport finite");
  require(f.viewport[0]>=0&&f.viewport[1]>=0&&f.viewport[2]>0&&f.viewport[3]>0&&f.viewport[0]+f.viewport[2]<=1920&&f.viewport[1]+f.viewport[3]<=1080,"viewport range");s.frames.push_back(f);}
 require(at==b.size(),"trailing scene data");return s;
}
// Native column-vector matrices -> D3D row-vector API,transpose ONLY.
static D3DMATRIX matrix(const float* column){D3DMATRIX m{};for(unsigned i=0;i<4;++i)for(unsigned j=0;j<4;++j)m.m[i][j]=column[j*4+i];return m;}
static LRESULT CALLBACK proc(HWND w,UINT msg,WPARAM p,LPARAM l){return DefWindowProcW(w,msg,p,l);}
struct Window{HWND value=nullptr;~Window(){if(value)DestroyWindow(value);}};
struct Module{HMODULE value=nullptr;~Module(){if(value)FreeLibrary(value);}};
static void auditModules(){
 HANDLE snapshot=CreateToolhelp32Snapshot(TH32CS_SNAPMODULE,GetCurrentProcessId());require(snapshot!=INVALID_HANDLE_VALUE,"own module snapshot");
 MODULEENTRY32W entry{};entry.dwSize=sizeof(entry);bool valid=true;unsigned count=0;
 if(Module32FirstW(snapshot,&entry))do{
  std::wstring name(entry.szModule),path(entry.szExePath);for(auto& c:name)c=static_cast<wchar_t>(std::towlower(c));for(auto& c:path)c=static_cast<wchar_t>(std::towlower(c));
#ifndef SFC_D3D9_REMIX_PROOF
  valid&=name.find(L"remix")==std::wstring::npos&&name.find(L"reshade")==std::wstring::npos&&name.find(L"dxvk")==std::wstring::npos&&path.find(L"\\.trex\\")==std::wstring::npos;
#else
  valid&=name.find(L"reshade")==std::wstring::npos;
#endif
  ++count;
 }while(Module32NextW(snapshot,&entry));
 CloseHandle(snapshot);require(count>0&&valid,"unexpected proxy module in D3D9 proof");
#ifndef SFC_D3D9_REMIX_PROOF
 std::cout<<"MODULE_AUDIT_PASS count="<<count<<" remix_reshade_dxvk=absent\n";
#else
 std::cout<<"MODULE_AUDIT_PASS count="<<count<<" reshade=absent normal_interception=1\n";
#endif
}
#include "pipeline_mode.h"
enum class TextureUpload {StagedLock,InitialData};
struct Renderer{
 // Declared first, destroyed last: pixels outlive all texture/device references.
 // InitialData takes the prepared vectors rather than making another copy.
 std::vector<std::vector<BYTE>> uploadBacking;
 ComPtr<IDirect3DDevice9> device;ComPtr<IDirect3DVertexBuffer9> vb;ComPtr<IDirect3DIndexBuffer9> ib;
 std::vector<ComPtr<IDirect3DTexture9>> textures;const Scene& scene;
 unsigned initialDataUploads=0,stagedUploads=0,initialDataUnsupported=0;
 explicit Renderer(IDirect3DDevice9* d,const Scene& s,const fs::path& root,std::vector<std::vector<BYTE>>* prepared=nullptr,TextureUpload policy=TextureUpload::StagedLock):device(d),scene(s){
  constexpr DWORD fvf=D3DFVF_XYZ|D3DFVF_NORMAL|D3DFVF_TEX1;
  const auto nv=static_cast<UINT>(s.vertices.size()),ni=static_cast<UINT>(s.indices.size());
  // DEFAULT is valid on both D3D9 and D3D9Ex. Retained Scene is the rebuild
  // source; release this Renderer before device reset/recreation.
  ok(d->CreateVertexBuffer(nv*sizeof(Vertex),0,fvf,D3DPOOL_DEFAULT,&vb,nullptr),"vertex buffer");
  void* p=nullptr;ok(vb->Lock(0,0,&p,0),"VB upload lock");memcpy(p,s.vertices.data(),nv*sizeof(Vertex));ok(vb->Unlock(),"VB unlock");
  if(!pipeline_mode::performance()){ok(vb->Lock(0,0,&p,D3DLOCK_READONLY),"VB readback");require(memcmp(p,s.vertices.data(),nv*sizeof(Vertex))==0,"VB bytes differ");ok(vb->Unlock(),"VB read unlock");}
  ok(d->CreateIndexBuffer(ni*4,0,D3DFMT_INDEX32,D3DPOOL_DEFAULT,&ib,nullptr),"index buffer");
  ok(ib->Lock(0,0,&p,0),"IB upload lock");memcpy(p,s.indices.data(),ni*4);ok(ib->Unlock(),"IB unlock");
  if(!pipeline_mode::performance()){ok(ib->Lock(0,0,&p,D3DLOCK_READONLY),"IB readback");require(memcmp(p,s.indices.data(),ni*4)==0,"IB bytes differ");ok(ib->Unlock(),"IB read unlock");}
  uint32_t count=0;for(auto g:s.groups)count=std::max(count,g.material+1);textures.resize(count);size_t total=0;
  require(!prepared||prepared->size()==count,"prepared texture count");
  if(policy==TextureUpload::InitialData)uploadBacking.resize(count);
  for(uint32_t i=0;i<count;++i){std::vector<BYTE> disk;if(!prepared)disk=read(root/(L"texture-"+std::to_wstring(i)+L".bin"),64*1024*1024+16);
   if(policy==TextureUpload::InitialData)uploadBacking[i]=prepared?std::move((*prepared)[i]):std::move(disk);
   const auto& b=policy==TextureUpload::InitialData?uploadBacking[i]:(prepared?(*prepared)[i]:disk);size_t at=0;const auto h=take<std::array<uint32_t,4>>(b,at);
   require(h[0]==0x31544653&&h[1]&&h[1]<=4096&&h[2]&&h[2]<=4096&&h[3]==uint64_t(h[1])*h[2]*4&&b.size()==16ull+h[3],"texture schema");
   total+=h[3];require(total<=128*1024*1024,"decoded texture cap");
   ok(d->CreateTexture(h[1],h[2],1,0,D3DFMT_A8R8G8B8,D3DPOOL_DEFAULT,&textures[i],nullptr),"texture create");
   // Microsoft UpdateTexture contract: SYSTEMMEM source -> DEFAULT destination.
   // Do not LockRect a non-dynamic DEFAULT texture (invalid on native D3D9Ex).
   ComPtr<IDirect3DTexture9> upload;D3DLOCKED_RECT lock{};
   if(policy==TextureUpload::InitialData&&!initialDataUnsupported){
    // Microsoft CreateTexture remarks: one mip, tightly packed SYSTEMMEM pixels.
    // This is a CPU pointer, NOT an exported GPU resource handle. Owned above.
    HANDLE pixels=reinterpret_cast<HANDLE>(const_cast<BYTE*>(b.data()+16));
    const auto status=d->CreateTexture(h[1],h[2],1,0,D3DFMT_A8R8G8B8,D3DPOOL_SYSTEMMEM,&upload,&pixels);
    if(status==D3DERR_INVALIDCALL){upload.Reset();++initialDataUnsupported;} // Classic D3D9 may not expose this contract.
    else{ok(status,"texture staging initial pixels");++initialDataUploads;}
   }
   if(!upload){
    ++stagedUploads;
    ok(d->CreateTexture(h[1],h[2],1,0,D3DFMT_A8R8G8B8,D3DPOOL_SYSTEMMEM,&upload,nullptr),"texture upload staging");
    ok(upload->LockRect(0,&lock,nullptr,0),"texture upload lock");require(lock.Pitch>=static_cast<INT>(h[1]*4),"texture pitch");for(uint32_t y=0;y<h[2];++y)memcpy(static_cast<BYTE*>(lock.pBits)+y*lock.Pitch,b.data()+16+size_t(y)*h[1]*4,h[1]*4);ok(upload->UnlockRect(0),"texture unlock");
   }
   ok(d->UpdateTexture(upload.Get(),textures[i].Get()),"texture staged upload");
   if(!pipeline_mode::performance()){
    ComPtr<IDirect3DSurface9> target,readback;ok(d->CreateRenderTarget(h[1],h[2],D3DFMT_A8R8G8B8,D3DMULTISAMPLE_NONE,0,FALSE,&target,nullptr),"texture test target");
    ComPtr<IDirect3DSurface9> source;ok(textures[i]->GetSurfaceLevel(0,&source),"texture test source");
    ok(d->StretchRect(source.Get(),nullptr,target.Get(),nullptr,D3DTEXF_NONE),"texture test copy");
    ok(d->CreateOffscreenPlainSurface(h[1],h[2],D3DFMT_A8R8G8B8,D3DPOOL_SYSTEMMEM,&readback,nullptr),"texture test staging");
    ok(d->GetRenderTargetData(target.Get(),readback.Get()),"texture test readback");
    ok(readback->LockRect(&lock,nullptr,D3DLOCK_READONLY),"texture readback");require(lock.Pitch>=static_cast<INT>(h[1]*4),"texture readback pitch");
    for(uint32_t y=0;y<h[2];++y)require(memcmp(static_cast<BYTE*>(lock.pBits)+y*lock.Pitch,b.data()+16+size_t(y)*h[1]*4,h[1]*4)==0,"texture row differs");ok(readback->UnlockRect(),"texture read unlock");
   }
  }
 }
 void draw(const Frame& f,bool mask,uint32_t width,uint32_t height,bool clear=true){
  auto* d=device.Get();ok(d->SetVertexShader(nullptr),"fixed VS");ok(d->SetPixelShader(nullptr),"fixed PS");ok(d->SetFVF(D3DFVF_XYZ|D3DFVF_NORMAL|D3DFVF_TEX1),"FVF");
  ok(d->SetStreamSource(0,vb.Get(),0,sizeof(Vertex)),"stream");ok(d->SetIndices(ib.Get()),"indices");
  auto w=matrix(f.model),v=matrix(f.view),p=matrix(f.projection);ok(d->SetTransform(D3DTS_WORLD,&w),"world");ok(d->SetTransform(D3DTS_VIEW,&v),"view");ok(d->SetTransform(D3DTS_PROJECTION,&p),"projection");
  D3DVIEWPORT9 viewport{static_cast<DWORD>(std::lround(f.viewport[0]*width/1920)),static_cast<DWORD>(std::lround(f.viewport[1]*height/1080)),
   static_cast<DWORD>(std::lround(f.viewport[2]*width/1920)),static_cast<DWORD>(std::lround(f.viewport[3]*height/1080)),0,1};
  ok(d->SetViewport(&viewport),"viewport");ok(d->SetRenderState(D3DRS_LIGHTING,FALSE),"unlit primary");ok(d->SetRenderState(D3DRS_CULLMODE,D3DCULL_NONE),"two sided baseline");
  ok(d->SetRenderState(D3DRS_ZENABLE,TRUE),"Z enable");ok(d->SetRenderState(D3DRS_ZWRITEENABLE,TRUE),"Z write");ok(d->SetRenderState(D3DRS_ZFUNC,D3DCMP_LESSEQUAL),"Z compare");
  ok(d->SetRenderState(D3DRS_ALPHABLENDENABLE,FALSE),"opaque");ok(d->SetRenderState(D3DRS_ALPHATESTENABLE,FALSE),"alpha test off");ok(d->SetRenderState(D3DRS_SRGBWRITEENABLE,FALSE),"encoded output baseline");
  ok(d->SetRenderState(D3DRS_TEXTUREFACTOR,0xffffffff),"mask color");ok(d->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_SELECTARG1),"color select");
  ok(d->SetTextureStageState(0,D3DTSS_COLORARG1,mask?D3DTA_TFACTOR:D3DTA_TEXTURE),"color input");ok(d->SetTextureStageState(0,D3DTSS_ALPHAOP,D3DTOP_DISABLE),"opaque alpha");
  ok(d->SetTextureStageState(0,D3DTSS_TEXCOORDINDEX,0),"captured UV");ok(d->SetTextureStageState(0,D3DTSS_TEXTURETRANSFORMFLAGS,D3DTTFF_DISABLE),"UV transform off");ok(d->SetTextureStageState(1,D3DTSS_COLOROP,D3DTOP_DISABLE),"secondary deferred");
  ok(d->SetSamplerState(0,D3DSAMP_MINFILTER,D3DTEXF_POINT),"point min");ok(d->SetSamplerState(0,D3DSAMP_MAGFILTER,D3DTEXF_POINT),"point mag");ok(d->SetSamplerState(0,D3DSAMP_MIPFILTER,D3DTEXF_NONE),"no mip");
  ok(d->SetSamplerState(0,D3DSAMP_ADDRESSU,D3DTADDRESS_WRAP),"UV wrap U");ok(d->SetSamplerState(0,D3DSAMP_ADDRESSV,D3DTADDRESS_WRAP),"UV wrap V");ok(d->SetSamplerState(0,D3DSAMP_SRGBTEXTURE,FALSE),"encoded sample baseline");
  // Clear the WHOLE proof target,not only the captured offset viewport. Otherwise
  // undefined backbuffer contents outside it could be mistaken for scene pixels.
  D3DVIEWPORT9 full{0,0,width,height,0,1};ok(d->SetViewport(&full),"full clear viewport");
  if(clear)ok(d->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xff000000,1,0),"clear");ok(d->SetViewport(&viewport),"restore scene viewport");ok(d->BeginScene(),"begin");
  if(f.active)for(auto g:scene.groups){ok(d->SetTexture(0,mask?nullptr:textures[g.material].Get()),"group texture");ok(d->DrawIndexedPrimitive(D3DPT_TRIANGLELIST,0,0,static_cast<UINT>(scene.vertices.size()),g.first,g.count/3),"indexed triangle group");}
  ok(d->EndScene(),"end");
 }
 std::vector<BYTE> pixels(uint32_t width,uint32_t height){
  ComPtr<IDirect3DSurface9> back,staging;ok(device->GetRenderTarget(0,&back),"backbuffer");
  ok(device->CreateOffscreenPlainSurface(width,height,D3DFMT_A8R8G8B8,D3DPOOL_SYSTEMMEM,&staging,nullptr),"readback surface");
  ok(device->GetRenderTargetData(back.Get(),staging.Get()),"offline readback");D3DLOCKED_RECT lock{};ok(staging->LockRect(&lock,nullptr,D3DLOCK_READONLY),"readback lock");
  std::vector<BYTE> out(size_t(width)*height*4);for(uint32_t y=0;y<height;++y)memcpy(out.data()+size_t(y)*width*4,static_cast<BYTE*>(lock.pBits)+y*lock.Pitch,width*4);ok(staging->UnlockRect(),"readback unlock");return out;
 }
 void save(const fs::path& path,uint32_t w,uint32_t h){auto out=pixels(w,h);std::ofstream file(path,std::ios::binary);file.write(reinterpret_cast<const char*>(&w),4);file.write(reinterpret_cast<const char*>(&h),4);file.write(reinterpret_cast<const char*>(out.data()),static_cast<std::streamsize>(out.size()));require(bool(file),"output write");}
};
#ifndef SFC_D3D9_REPLAY_TYPES_ONLY
int wmain(int argc,wchar_t** argv){
 try{
#ifndef SFC_D3D9_REMIX_PROOF
  require(argc==2,"one replay folder argument required");
#else
  require(argc==3,"replay folder and pinned bridge DLL required");
#endif
  const auto root=fs::path(argv[1]);const auto scene=load(root);
#ifndef SFC_D3D9_REMIX_PROOF
  wchar_t system[MAX_PATH]{};const auto n=GetSystemDirectoryW(system,MAX_PATH);require(n&&n<MAX_PATH,"system directory");
  const auto library=fs::path(system)/L"d3d9.dll";
#else
  const auto library=fs::absolute(argv[2]);
#endif
  Module module;
#ifndef SFC_D3D9_REMIX_PROOF
  module.value=LoadLibraryExW(library.c_str(),nullptr,LOAD_LIBRARY_SEARCH_SYSTEM32);
#else
  module.value=LoadLibraryExW(library.c_str(),nullptr,LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR|LOAD_LIBRARY_SEARCH_SYSTEM32);
#endif
  require(module.value!=nullptr,"D3D9 load");
  wchar_t actual[MAX_PATH]{};require(GetModuleFileNameW(module.value,actual,MAX_PATH)>0&&fs::equivalent(library,actual),"not system D3D9");
  const auto* dos=reinterpret_cast<const IMAGE_DOS_HEADER*>(module.value);require(dos->e_magic==IMAGE_DOS_SIGNATURE,"D3D9 PE DOS header");
  const auto* pe=reinterpret_cast<const IMAGE_NT_HEADERS32*>(reinterpret_cast<const BYTE*>(module.value)+dos->e_lfanew);
  require(pe->Signature==IMAGE_NT_SIGNATURE&&pe->FileHeader.Machine==IMAGE_FILE_MACHINE_I386&&pe->OptionalHeader.Magic==IMAGE_NT_OPTIONAL_HDR32_MAGIC,"D3D9 module must be x86 PE32");
  const auto create=reinterpret_cast<decltype(&Direct3DCreate9)>(GetProcAddress(module.value,"Direct3DCreate9"));require(create!=nullptr,"D3D9 export");ComPtr<IDirect3D9> d9;d9.Attach(create(D3D_SDK_VERSION));require(bool(d9),"D3D9 init");
#ifndef SFC_D3D9_REMIX_PROOF
  std::wcout<<L"SYSTEM_D3D9 "<<actual<<L'\n';
#else
  std::wcout<<L"PINNED_BRIDGE_D3D9 "<<actual<<L'\n';
#endif
  WNDCLASSW wc{};wc.lpfnWndProc=proc;wc.hInstance=GetModuleHandleW(nullptr);wc.lpszClassName=L"SFC_D3D9_OfflineProof";require(RegisterClassW(&wc)!=0,"window class");
  RECT client{0,0,static_cast<LONG>(scene.width),static_cast<LONG>(scene.height)};
  require(AdjustWindowRect(&client,WS_OVERLAPPEDWINDOW,FALSE)!=0,"window client dimensions");
  Window window;window.value=CreateWindowW(wc.lpszClassName,L"SFC offline D3D9 proof",WS_OVERLAPPEDWINDOW,0,0,client.right-client.left,client.bottom-client.top,nullptr,nullptr,wc.hInstance,nullptr);require(window.value!=nullptr,"hidden window");
  D3DPRESENT_PARAMETERS pp{};pp.BackBufferWidth=scene.width;pp.BackBufferHeight=scene.height;pp.BackBufferFormat=D3DFMT_A8R8G8B8;pp.BackBufferCount=1;pp.Windowed=TRUE;pp.hDeviceWindow=window.value;pp.SwapEffect=D3DSWAPEFFECT_DISCARD;pp.EnableAutoDepthStencil=TRUE;pp.AutoDepthStencilFormat=D3DFMT_D24S8;pp.PresentationInterval=D3DPRESENT_INTERVAL_IMMEDIATE;
  D3DDISPLAYMODE mode{};ok(d9->GetAdapterDisplayMode(0,&mode),"adapter display mode");
  D3DADAPTER_IDENTIFIER9 adapter{};ok(d9->GetAdapterIdentifier(0,0,&adapter),"adapter identity");std::cout<<"ADAPTER "<<adapter.Description<<" vendor="<<adapter.VendorId<<" device="<<adapter.DeviceId<<'\n';
  std::cout<<"DISPLAY_MODE "<<mode.Width<<'x'<<mode.Height<<" format="<<mode.Format<<" refresh="<<mode.RefreshRate<<'\n';
  ok(d9->CheckDeviceType(0,D3DDEVTYPE_HAL,mode.Format,pp.BackBufferFormat,TRUE),"windowed backbuffer compatibility");
  ComPtr<IDirect3DDevice9> device;ok(d9->CreateDevice(0,D3DDEVTYPE_HAL,window.value,D3DCREATE_HARDWARE_VERTEXPROCESSING|D3DCREATE_FPU_PRESERVE,&pp,&device),"HAL hardware vertex device");
  {Renderer renderer(device.Get(),scene,root);
#ifdef SFC_D3D9_REMIX_PROOF
   // Same fixed-function VB/IB/texture/group draw path. No SDK calls. Repeated
   // presents give the normal bridge bounded startup/capture/drain time.
   bool exported=false;unsigned presented=0;
   for(unsigned i=0;i<600;++i){
    const size_t sample=i<45?0:(i<85?std::min<size_t>(1,scene.frames.size()-1):scene.frames.size()-1);
    renderer.draw(scene.frames[sample],false,pp.BackBufferWidth,pp.BackBufferHeight);
    ok(device->Present(nullptr,nullptr,nullptr,nullptr),"intercepted present");
    MSG message{};while(PeekMessageW(&message,nullptr,0,0,PM_REMOVE)){TranslateMessage(&message);DispatchMessageW(&message);}
    if(i%20==0)std::cout<<"INTERCEPT_FRAME "<<i<<" source_frame="<<scene.frames[sample].frame<<std::endl;
    Sleep(10);
    presented=i+1;
    // Offline harness only: keep the bridge alive until its asynchronous USD
    // exporter finishes. Never use this wait on SFC's rendering callback.
    if(i>=119){std::ifstream log(root/L"rtx-remix/logs/remix-dxvk.log");
     const std::string text((std::istreambuf_iterator<char>(log)),std::istreambuf_iterator<char>());
     exported=text.find("End USD export")!=std::string::npos;
     if(exported)break;
    }
   }
   require(exported,"bounded capture export drain incomplete");
   std::cout<<"EXPORT_DRAIN_PASS presents="<<presented<<'\n';
#else
   for(size_t i=0;i<scene.frames.size();++i){const auto& f=scene.frames[i];renderer.draw(f,false,pp.BackBufferWidth,pp.BackBufferHeight);renderer.save(root/(L"color-"+std::to_wstring(i)+L".bgra"),pp.BackBufferWidth,pp.BackBufferHeight);
    renderer.draw(f,true,pp.BackBufferWidth,pp.BackBufferHeight);renderer.save(root/(L"mask-"+std::to_wstring(i)+L".bgra"),pp.BackBufferWidth,pp.BackBufferHeight);ok(device->Present(nullptr,nullptr,nullptr,nullptr),"present");
    std::cout<<"FRAME "<<i<<" owner="<<f.owner<<" revision="<<f.revision<<" source_frame="<<f.frame<<'\n';}
   auto first=scene.frames.front();renderer.draw(first,true,pp.BackBufferWidth,pp.BackBufferHeight);auto before=renderer.pixels(pp.BackBufferWidth,pp.BackBufferHeight);
   ok(device->SetTexture(0,nullptr),"unbind texture");ok(device->SetStreamSource(0,nullptr,0,0),"unbind VB");ok(device->SetIndices(nullptr),"unbind IB");
   ok(device->Reset(&pp),"reset same device");renderer.draw(first,true,pp.BackBufferWidth,pp.BackBufferHeight);require(before==renderer.pixels(pp.BackBufferWidth,pp.BackBufferHeight),"reset changes pixels");
   first.active=0;renderer.draw(first,true,pp.BackBufferWidth,pp.BackBufferHeight);const auto retired=renderer.pixels(pp.BackBufferWidth,pp.BackBufferHeight);for(size_t i=0;i<retired.size();i+=4)require(retired[i]==0&&retired[i+1]==0&&retired[i+2]==0,"retired owner still visible");
   first.owner+=100;first.active=1;renderer.draw(first,true,pp.BackBufferWidth,pp.BackBufferHeight);require(before==renderer.pixels(pp.BackBufferWidth,pp.BackBufferHeight),"new owner instance differs");
   ok(device->SetTexture(0,nullptr),"resize unbind texture");ok(device->SetStreamSource(0,nullptr,0,0),"resize unbind VB");ok(device->SetIndices(nullptr),"resize unbind IB");
   pp.BackBufferWidth=scene.width/2;pp.BackBufferHeight=scene.height/2;require(pp.BackBufferWidth&&pp.BackBufferHeight,"resized dimensions");
   ok(device->Reset(&pp),"resize device");renderer.draw(first,true,pp.BackBufferWidth,pp.BackBufferHeight);renderer.save(root/L"mask-resized.bgra",pp.BackBufferWidth,pp.BackBufferHeight);
   std::cout<<"RESOURCE_READBACK_RESET_RETIRE_REAPPEAR_RESIZE_PASS\n";
#endif
  }
  auditModules();auto* rawDevice=device.Detach();require(rawDevice->Release()==0,"device references remain");auto* rawD9=d9.Detach();require(rawD9->Release()==0,"D3D9 references remain");
#ifndef SFC_D3D9_REMIX_PROOF
  std::cout<<"D3D9_OFFLINE_RENDER_PASS checks="<<checks<<" frames="<<scene.frames.size()<<" triangles="<<scene.indices.size()/3<<" groups="<<scene.groups.size()<<" pe=x86 device_refs=0 api_refs=0\n";
#else
  std::cout<<"D3D9_INTERCEPTION_CLIENT_PASS triangles="<<scene.indices.size()/3<<" groups="<<scene.groups.size()<<" pe=x86 device_refs=0 api_refs=0\n";
#endif
  return 0;
 }catch(const std::exception& e){std::cerr<<"D3D9_PROOF_FAIL "<<e.what()<<'\n';return 1;}
}
#endif

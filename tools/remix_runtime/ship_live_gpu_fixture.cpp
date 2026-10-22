// Owned synthetic publisher/native receiver test. NEVER SFC;readback only here.
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#define SFC_LIVE_FIXTURE
#include "ship_live_receiver.h"
#include <fstream>
#include <iostream>
#include <memory>
#include <vector>
#include "../m1_component/native_light_snapshot.h"
using namespace ship_live;
static LRESULT CALLBACK procedure(HWND w,UINT m,WPARAM p,LPARAM l){return DefWindowProcW(w,m,p,l);}
static void dump(ID3D11DeviceContext* c,ID3D11Texture2D* texture,const char* name){
 D3D11_MAPPED_SUBRESOURCE data{};checked(c->Map(texture,0,D3D11_MAP_READ,0,&data),"fixture map");
 std::ofstream file(name,std::ios::binary);for(unsigned y=0;y<256;++y)file.write(static_cast<const char*>(data.pData)+size_t(y)*data.RowPitch,1024);c->Unmap(texture,0);if(!file)throw std::runtime_error("fixture dump");
}
int wmain(int argc,wchar_t** argv){wchar_t session[128]{};if(argc==2)wcscpy_s(session,argv[1]);else if(argc!=1||!GetEnvironmentVariableW(L"SFC_REMIX_RETURN_SESSION",session,128))return 2;std::cout.setf(std::ios::unitbuf);try{
 const bool addonMode=GetEnvironmentVariableW(L"SFC_PRIVATE_CALLBACK_FIXTURE",nullptr,0)!=0;
 const bool visibleMode=GetEnvironmentVariableW(L"SFC_REMIX_VISIBLE_SHIP",nullptr,0)!=0;bool visibleVerified=false;
 const bool texturedMode=GetEnvironmentVariableW(L"SFC_REMIX_TEXTURED_SHIP",nullptr,0)!=0;
 const bool lightMode=GetEnvironmentVariableW(L"SFC_REMIX_LIGHT_WIRING",nullptr,0)!=0;
 const bool sceneMode=GetEnvironmentVariableW(L"SFC_REMIX_SCENE_DEPTH",nullptr,0)!=0;
 float sceneZ=1;bool sceneBound=true;unsigned sceneHidden=0,sceneMissing=0,sceneRestored=0;
 std::ofstream syntheticLights;ULONGLONG lightAt=0;uint32_t lightSequence=0;
 if(lightMode)syntheticLights.open("gate/native-lights.bin",std::ios::binary|std::ios::trunc);
 unsigned steadySamples=0,steadyDisplayed=0;
 const unsigned frameWidth=visibleMode?1920u:800u,frameHeight=visibleMode?1080u:600u;
 std::vector<BYTE> visibleMask(visibleMode?size_t(frameWidth)*frameHeight:0);
 const auto splashUntil=GetTickCount64()+5000;
 return_path::Mapping mapping(false,session);auto& state=*mapping.state;
 auto& wire=*reinterpret_cast<Wire*>(reinterpret_cast<BYTE*>(mapping.state)+ship_triplet::Offset);auto& cmd=command(mapping);
 struct Source:sfc_calibration::Reader{~Source(){close();}} scene;
 if(!scene.prepare()||!scene.requested)throw std::runtime_error("fixture source");
 std::ifstream file("fixture-row.bin",std::ios::binary);sfc_calibration::Snapshot snap{};
 file.read(reinterpret_cast<char*>(snap.owner[0].data()),384);if(!file||file.peek()!=EOF)throw std::runtime_error("fixture row");
 auto& row=snap.owner[0];row[45]=0;row[47]=GetCurrentThreadId();snap.frame=row[2];snap.rows=1;memcpy(snap.session,scene.session,16);
 const auto publish=[&](){
  if(!sfc_calibration::lock(scene.mailbox))return;
  scene.mailbox->snapshot=snap;InterlockedExchange(&scene.mailbox->active,1);sfc_calibration::unlock(scene.mailbox);
  auto* base=reinterpret_cast<BYTE*>(scene.mailbox)-sfc_calibration::Offset;
  auto* guard=reinterpret_cast<LONG*>(base+4096);InterlockedIncrement(guard);memcpy(base+4100,row.data(),384);MemoryBarrier();InterlockedIncrement(guard);
  if(lightMode&&GetTickCount64()-lightAt>=200){
   lightAt=GetTickCount64();sfc_native_lights::Snapshot l{};
   l.header={sfc_native_lights::Magic,1,sizeof(l),++lightSequence,scene.session[0],scene.session[1],scene.session[2],scene.session[3],row[1],row[2],row[3],0x12340000,row[5],row[6],row[47],0};
   memcpy(l.supplied.data(),row.data()+8,68);memcpy(l.view.data(),row.data()+49,68);
   const float dir[3]={.98893636f,0,-.14834046f};memcpy(l.records.data()+1,dir,12);
   l.records[7]=l.records[8]=l.records[9]=0x3f800000;l.records[10]=0x3fc00000;
   l.records[19]=l.records[23]=l.records[24]=l.records[25]=0x3f800000;l.records[26]=0x3e800000;
   l.enables[0]=l.enables[1]=1;l.gate=1;
   syntheticLights.write(reinterpret_cast<const char*>(&l),sizeof(l));syntheticLights.flush();
   if(!syntheticLights)throw std::runtime_error("synthetic light fixture output");
  }
 };
 state.gamePid=GetCurrentProcessId();publish();std::cout<<"FIXTURE_PID "<<GetCurrentProcessId()<<"\n";
 ComPtr<ID3D11Device> d;ComPtr<ID3D11DeviceContext> c;const D3D_FEATURE_LEVEL level=D3D_FEATURE_LEVEL_10_1;
 ComPtr<IDXGISwapChain> swap;ComPtr<ID3D11RenderTargetView> originalTarget;ComPtr<ID3D11Texture2D> visibleBack,visibleStage;HWND window=nullptr;
 if(addonMode){
  if(!GetModuleHandleW(L"SFCRemixReturn.dll")||!LoadLibraryW(L".\\dxgi.dll"))throw std::runtime_error("callback fixture preload");
  WNDCLASSW wc{};wc.lpfnWndProc=procedure;wc.hInstance=GetModuleHandleW(nullptr);wc.lpszClassName=L"SFC_PrivateCallbackFixture";if(!RegisterClassW(&wc))throw std::runtime_error("callback window class");
  window=CreateWindowW(wc.lpszClassName,L"Offline private-return test - NOT SFC",WS_POPUP,0,0,frameWidth,frameHeight,nullptr,nullptr,wc.hInstance,nullptr);if(!window)throw std::runtime_error("callback window");ShowWindow(window,SW_SHOWNOACTIVATE);
  DXGI_SWAP_CHAIN_DESC sd{};sd.BufferDesc.Width=frameWidth;sd.BufferDesc.Height=frameHeight;sd.BufferDesc.Format=DXGI_FORMAT_B8G8R8A8_UNORM;sd.SampleDesc.Count=1;sd.BufferCount=1;sd.BufferUsage=DXGI_USAGE_RENDER_TARGET_OUTPUT;sd.OutputWindow=window;sd.Windowed=TRUE;sd.SwapEffect=DXGI_SWAP_EFFECT_DISCARD;
  checked(D3D11CreateDeviceAndSwapChain(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,&level,1,D3D11_SDK_VERSION,&sd,&swap,&d,nullptr,&c),"callback device10_1");
  ComPtr<ID3D11Texture2D> back;checked(swap->GetBuffer(0,IID_PPV_ARGS(&back)),"callback buffer");checked(d->CreateRenderTargetView(back.Get(),nullptr,&originalTarget),"callback RTV");
  if(visibleMode){visibleBack=back;D3D11_TEXTURE2D_DESC v{};back->GetDesc(&v);v.BindFlags=v.MiscFlags=0;v.Usage=D3D11_USAGE_STAGING;v.CPUAccessFlags=D3D11_CPU_ACCESS_READ;checked(d->CreateTexture2D(&v,nullptr,&visibleStage),"visible fixture staging");}
 }else checked(D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,&level,1,D3D11_SDK_VERSION,&d,nullptr,&c),"fixture10_1");
 std::unique_ptr<Receiver> receiver;if(!addonMode)receiver=std::make_unique<Receiver>(mapping,d.Get());state.armed=state.enabled=1;
 ComPtr<ID3D11Texture2D> sceneColor,sceneDepth;ComPtr<ID3D11RenderTargetView> sceneTarget;ComPtr<ID3D11DepthStencilView> sceneView;
 ComPtr<ID3D11VertexShader> sceneVS;ComPtr<ID3D11PixelShader> scenePS;ComPtr<ID3D11DepthStencilState> sceneNoWrite;
 if(sceneMode){
  if(!addonMode||!texturedMode)throw std::runtime_error("scene fixture requires textured callbacks");
  D3D11_TEXTURE2D_DESC sd{};sd.Width=frameWidth;sd.Height=frameHeight;sd.ArraySize=sd.MipLevels=1;sd.SampleDesc.Count=8;
  sd.Format=DXGI_FORMAT_B8G8R8A8_UNORM;sd.BindFlags=D3D11_BIND_RENDER_TARGET;
  checked(d->CreateTexture2D(&sd,nullptr,&sceneColor),"synthetic native scene color");checked(d->CreateRenderTargetView(sceneColor.Get(),nullptr,&sceneTarget),"synthetic scene RTV");
  sd.Format=DXGI_FORMAT_R32_TYPELESS;sd.BindFlags=D3D11_BIND_DEPTH_STENCIL|D3D11_BIND_SHADER_RESOURCE;
  checked(d->CreateTexture2D(&sd,nullptr,&sceneDepth),"synthetic native scene depth");D3D11_DEPTH_STENCIL_VIEW_DESC sv{};sv.Format=DXGI_FORMAT_D32_FLOAT;sv.ViewDimension=D3D11_DSV_DIMENSION_TEXTURE2DMS;
  checked(d->CreateDepthStencilView(sceneDepth.Get(),&sv,&sceneView),"synthetic scene DSV");
  const char* shader="float4 vs(uint i:SV_VertexID):SV_Position{float2 p[3]={float2(-1,-1),float2(-1,3),float2(3,-1)};return float4(p[i],0,1);}float4 ps():SV_Target{return float4(0,0,0,1);}";
  ComPtr<ID3DBlob> vs,ps;checked(D3DCompile(shader,strlen(shader),nullptr,nullptr,nullptr,"vs","vs_4_1",0,0,&vs,nullptr),"scene VS compile");
  checked(D3DCompile(shader,strlen(shader),nullptr,nullptr,nullptr,"ps","ps_4_1",0,0,&ps,nullptr),"scene PS compile");
  checked(d->CreateVertexShader(vs->GetBufferPointer(),vs->GetBufferSize(),nullptr,&sceneVS),"scene VS");checked(d->CreatePixelShader(ps->GetBufferPointer(),ps->GetBufferSize(),nullptr,&scenePS),"scene PS");
  D3D11_DEPTH_STENCIL_DESC noWrite{};checked(d->CreateDepthStencilState(&noWrite,&sceneNoWrite),"scene no-write state");
 }
 const auto step=[&](){if(receiver)receiver->step();else{
  MSG message{};while(PeekMessageW(&message,nullptr,0,0,PM_REMOVE)){TranslateMessage(&message);DispatchMessageW(&message);}
  const float blue[]={.02f,.05f,.3f,1};c->ClearRenderTargetView(originalTarget.Get(),blue);
  if(sceneMode){
   c->ClearDepthStencilView(sceneView.Get(),D3D11_CLEAR_DEPTH,sceneZ,0);auto* rt=sceneTarget.Get();c->OMSetRenderTargets(1,&rt,sceneBound?sceneView.Get():nullptr);
   c->OMSetDepthStencilState(sceneNoWrite.Get(),0);c->VSSetShader(sceneVS.Get(),nullptr,0);c->PSSetShader(scenePS.Get(),nullptr,0);
   c->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);D3D11_VIEWPORT vp{0,0,static_cast<float>(frameWidth),static_cast<float>(frameHeight),0,1};c->RSSetViewports(1,&vp);c->Draw(3,0);
  }
  auto* target=originalTarget.Get();c->OMSetRenderTargets(1,&target,nullptr);c->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_LINELIST);
  checked(swap->Present(0,0),"callback Present");D3D11_PRIMITIVE_TOPOLOGY topology{};c->IAGetPrimitiveTopology(&topology);if(topology!=D3D11_PRIMITIVE_TOPOLOGY_LINELIST)throw std::runtime_error("callback immediate state changed");
  // ReShade's own transient startup banner modifies this standalone frame.
  // Wait it out rather than excluding any pixels from the comparison.
  if(visibleMode&&!visibleVerified&&state.drawCount>0&&GetTickCount64()>=splashUntil){
   c->CopyResource(visibleStage.Get(),visibleBack.Get());D3D11_MAPPED_SUBRESOURCE v{};checked(c->Map(visibleStage.Get(),0,D3D11_MAP_READ,0,&v),"visible fixture readback");
   unsigned magenta=0,texturedPixels=0;std::array<unsigned,4096> colors{};
   for(unsigned y=0;y<frameHeight;++y)for(unsigned x=0;x<frameWidth;++x){auto* pixel=static_cast<const BYTE*>(v.pData)+size_t(y)*v.RowPitch+x*4;
    if(y>=96&&pixel[0]>40&&pixel[2]>40&&pixel[1]<40)++magenta;
    visibleMask[size_t(y)*frameWidth+x]=static_cast<BYTE>(y>=96&&(std::abs(int(pixel[0])-77)>2||std::abs(int(pixel[1])-13)>2||std::abs(int(pixel[2])-5)>2));
    if(visibleMask[size_t(y)*frameWidth+x]){++texturedPixels;++colors[(pixel[0]>>4)|((pixel[1]>>4)<<4)|((pixel[2]>>4)<<8)];}
   }
   c->Unmap(visibleStage.Get(),0);
   unsigned unique=0;for(auto count:colors)unique+=count!=0;
   if(texturedMode?(texturedPixels>100&&unique>=8):magenta>10){
    std::ofstream mask("visible-camera-mask.bin",std::ios::binary);mask.write(reinterpret_cast<const char*>(visibleMask.data()),visibleMask.size());if(!mask)throw std::runtime_error("visible camera mask output");
    visibleVerified=true;std::cout<<"VISIBLE_CAMERA_PIXELS_PASS magenta="<<magenta<<" width="<<frameWidth<<" height="<<frameHeight<<" excluded_banner_rows=96\n";
    if(texturedMode)std::cout<<"TEXTURED_PIXELS_PASS pixels="<<texturedPixels<<" colors="<<unique<<" output="<<wire.width<<"x"<<wire.height<<"\n";
   }
  }
  if(sceneMode&&visibleVerified&&(!sceneBound||sceneZ==0)){
   c->CopyResource(visibleStage.Get(),visibleBack.Get());D3D11_MAPPED_SUBRESOURCE m{};checked(c->Map(visibleStage.Get(),0,D3D11_MAP_READ,0,&m),"scene hidden readback");
   unsigned nonblue=0;for(unsigned y=96;y<frameHeight;++y)for(unsigned x=0;x<frameWidth;++x){const auto* p=static_cast<const BYTE*>(m.pData)+size_t(y)*m.RowPitch+x*4;nonblue+=std::abs(int(p[0])-77)>2||std::abs(int(p[1])-13)>2||std::abs(int(p[2])-5)>2;}
   c->Unmap(visibleStage.Get(),0);if(nonblue)throw std::runtime_error("scene near-depth/missing-depth did not hide additive image");
   if(sceneBound)++sceneHidden;else ++sceneMissing;
  }
 }};
 const auto waitUntil=GetTickCount64()+(texturedMode?30000:10000);while(!load(registration(mapping).ready)){
  if(GetTickCount64()>waitUntil)throw std::runtime_error("fixture seed10s");publish();step();Sleep(2);}
 if(GetEnvironmentVariableW(L"SFC_PRIVATE_SLOW",nullptr,0)){
  const auto readyBy=GetTickCount64()+5000;
  while(load(wire.lease)!=Ready){if(GetTickCount64()>readyBy)throw std::runtime_error("slow fixture readiness");publish();Sleep(1);}
  const LONG sequence=load(wire.sequence);Sleep(1500);
  if(load(wire.sequence)!=sequence||load(wire.lease)!=Ready)throw std::runtime_error("slow fixture lease overwritten");
  std::cout<<"SLOW_LEASE_NO_OVERWRITE seq="<<sequence<<"\n";
 }
 ComPtr<ID3D11Texture2D> stageColor,stagePicking,stageDepth;D3D11_TEXTURE2D_DESC desc{};
 if(receiver){receiver->fixtureOutput()->GetDesc(&desc);desc.BindFlags=desc.MiscFlags=0;desc.Usage=D3D11_USAGE_STAGING;desc.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
 checked(d->CreateTexture2D(&desc,nullptr,&stageColor),"fixture color staging");desc.Format=DXGI_FORMAT_R32_FLOAT;checked(d->CreateTexture2D(&desc,nullptr,&stagePicking),"fixture picking staging");
 checked(d->CreateTexture2D(&desc,nullptr,&stageDepth),"fixture depth staging");}LONG observedDraw=0;unsigned debug=0;
 bool captured=false;const auto start=GetTickCount64();ULONGLONG qualifiedAt=0;LONG hold=0,retiredAt=0,disabledAt=0;bool retirement=false,disabled=false;
 const ULONGLONG cacheHold=GetEnvironmentVariableW(L"SFC_PRIVATE_MATERIAL_CACHE",nullptr,0)?20000u:0u;
 while(!qualifiedAt||GetTickCount64()-qualifiedAt<cacheHold+(visibleMode?7000u:5000u)){
  if(GetTickCount64()-start>15000+cacheHold)throw std::runtime_error("fixture bounded cold-start/hold cap");
  const auto rawTime=qualifiedAt?GetTickCount64()-qualifiedAt:0;
  const auto rawElapsed=rawTime>cacheHold?rawTime-cacheHold:0;
  const auto elapsed=visibleMode?(rawElapsed>2000?rawElapsed-2000:0):rawElapsed;
  if(sceneMode){sceneBound=!(elapsed>=1000&&elapsed<1400);sceneZ=(elapsed>=400&&elapsed<900)?0.f:1.f;}
  if(elapsed<2000){hold=load(cmd.drawn);}
  else if(elapsed<3000){++snap.frame;row[2]=snap.frame;if(texturedMode){float x=0;memcpy(&x,&row[11],4);x+=.01f;memcpy(&row[11],&x,4);}}
  else if(elapsed<3500){if(!disabled){disabled=true;disabledAt=load(cmd.drawn);state.enabled=0;}}
  else if(elapsed<4500){state.enabled=1;}
  else {if(!retirement){retirement=true;retiredAt=load(cmd.drawn);}row[4]=2;}
  publish();const auto beforeDisplay=state.drawCount;step();c->Flush();
  if(sceneMode&&visibleVerified&&elapsed>=1500&&elapsed<2000&&state.drawCount>beforeDisplay){
   if(++sceneRestored==1)std::cout<<"SCENE_DEPTH_PHASES_READY\n";
  }
  if(texturedMode&&elapsed>=2000&&elapsed<3000){++steadySamples;steadyDisplayed+=state.drawCount>beforeDisplay;}
  if(texturedMode&&!visibleVerified&&captured)qualifiedAt=GetTickCount64();
  if(retirement&&load(cmd.drawn)!=retiredAt)throw std::runtime_error("retired owner accepted");
  if(disabled&&elapsed>=3000&&elapsed<3500&&load(cmd.drawn)!=disabledAt)throw std::runtime_error("disabled receiver drew");
  if(addonMode&&!captured&&load(cmd.drawn)>0){captured=true;qualifiedAt=GetTickCount64();std::cout<<"PRIVATE_CALLBACK_ACTIVE source_frame="<<snap.frame<<"\n";}
  if(receiver&&!captured&&load(cmd.drawn)>observedDraw&&elapsed<2000){observedDraw=load(cmd.drawn);
   c->CopyResource(stageColor.Get(),receiver->fixtureOutput());c->CopyResource(stagePicking.Get(),receiver->fixturePicking());c->CopyResource(stageDepth.Get(),receiver->fixtureDepth());c->Flush();
   D3D11_MAPPED_SUBRESOURCE data{};checked(c->Map(stagePicking.Get(),0,D3D11_MAP_READ,0,&data),"fixture picking check");unsigned pixels=0;
   for(unsigned y=0;y<256;++y)for(unsigned x=0;x<256;++x){uint32_t id=0;memcpy(&id,static_cast<const BYTE*>(data.pData)+size_t(y)*data.RowPitch+x*4,4);if(id==29)++pixels;}
   c->Unmap(stagePicking.Get(),0);
   checked(c->Map(stageColor.Get(),0,D3D11_MAP_READ,0,&data),"fixture color check");unsigned visible=0;
   for(unsigned y=0;y<256;++y)for(unsigned x=0;x<256;++x){const auto* rgba=static_cast<const BYTE*>(data.pData)+size_t(y)*data.RowPitch+x*4;if(rgba[3]&&rgba[0]>20&&rgba[2]>20)++visible;}
   c->Unmap(stageColor.Get(),0);
   checked(c->Map(stageDepth.Get(),0,D3D11_MAP_READ,0,&data),"fixture depth check");float minZ=1e9f,maxZ=-1e9f;
   for(unsigned y=0;y<256;++y)for(unsigned x=0;x<256;++x){float z=0;memcpy(&z,static_cast<const BYTE*>(data.pData)+size_t(y)*data.RowPitch+x*4,4);minZ=(std::min)(minZ,z);maxZ=(std::max)(maxZ,z);}
   c->Unmap(stageDepth.Get(),0);if(debug++<3)std::cout<<"PRIVATE_WARMUP picking="<<pixels<<" visible="<<visible<<" minZ="<<minZ<<" maxZ="<<maxZ<<"\n";
   if(pixels>10&&visible>10){dump(c.Get(),stageColor.Get(),"private-color.bin");dump(c.Get(),stagePicking.Get(),"private-picking.bin");dump(c.Get(),stageDepth.Get(),"private-depth.bin");captured=true;qualifiedAt=GetTickCount64();std::cout<<"PRIVATE_MASK pixels="<<pixels<<" source_frame="<<snap.frame<<" cold_ready_ms="<<qualifiedAt-start<<"\n";}
  }
  Sleep(16);
 }
 state.enabled=0;store(wire.stop,1);const auto drain=GetTickCount64()+2000;
 while(load(wire.lease)==Reading&&GetTickCount64()<drain){step();c->Flush();Sleep(1);}if(receiver)receiver->stop();state.stop=1;
 const bool disconnect=GetEnvironmentVariableW(L"SFC_PRIVATE_DISCONNECT",nullptr,0)!=0;
 if(!captured||!hold||(!disconnect&&!texturedMode&&!load(wire.rejected))||load(cmd.failed)||load(wire.lease)==Reading||(visibleMode&&!visibleVerified)){std::cout<<"FIXTURE_PARTIAL captured="<<captured<<" hold="<<hold<<" rejected="<<load(wire.rejected)<<" failed="<<load(cmd.failed)<<" lease="<<load(wire.lease)<<"\n";throw std::runtime_error("fixture acceptance/rejection/drain");}
 if(sceneMode){
  if(!sceneHidden||!sceneMissing||!sceneRestored)throw std::runtime_error("scene depth phases incomplete");
  std::cout<<"SCENE_DEPTH_CALLBACK_PASS hidden="<<sceneHidden<<" missing="<<sceneMissing<<" restored="<<sceneRestored<<"\n";
 }
 if(texturedMode&&!disconnect&&!sceneMode){
  if(!steadySamples||steadyDisplayed*4<steadySamples*3)throw std::runtime_error("textured steady-display duty below75percent");
  std::cout<<"STEADY_DISPLAY_PASS samples="<<steadySamples<<" displayed="<<steadyDisplayed<<" max_request_age_ms=100\n";
 }
 std::cout<<"PRIVATE_GPU_FIXTURE_PASS drawn="<<load(cmd.drawn)<<" rejected="<<load(wire.rejected)<<" failed="<<load(cmd.failed)<<" retired_draws_stopped=1 disabled_draws_stopped=1 addon="<<addonMode<<"\n";
 c->ClearState();originalTarget.Reset();swap.Reset();c.Reset();d.Reset();if(window)DestroyWindow(window);return 0;
}catch(const std::exception& e){std::cout<<"PRIVATE_FIXTURE_FAILED "<<e.what()<<"\n";return 1;}}

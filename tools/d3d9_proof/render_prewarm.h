// Experimental external-host-only warm-up. Never publish these empty frames.
#pragma once
namespace render_prewarm {
inline bool requested(){wchar_t text[16]{};const auto n=GetEnvironmentVariableW(L"SFC_D3D9_RENDER_PREWARM",text,16);
 if(!n)return false;require(n<16&&(!wcscmp(text,L"empty")||!wcscmp(text,L"triangle")),"render prewarm mode");return true;}
inline void run(IDirect3DDevice9Ex* device,WorkerPoll& poll,StartupProfile& profile){
 require(profile.enabled,"experimental render prewarm requires startup measurement");
 ComPtr<IDirect3DStateBlock9> saved;ok(device->CreateStateBlock(D3DSBT_ALL,&saved),"warm state capture");
 ComPtr<IDirect3DQuery9> fence;ok(device->CreateQuery(D3DQUERYTYPE_EVENT,&fence),"warm completion query");
 wchar_t mode[16]{};GetEnvironmentVariableW(L"SFC_D3D9_RENDER_PREWARM",mode,16);const bool triangle=!wcscmp(mode,L"triangle");
 ComPtr<IDirect3DVertexBuffer9> vertices;ComPtr<IDirect3DTexture9> texture;
 if(triangle){
  const Vertex data[]={{{-.5f,-.5f,2},{0,0,-1},{0,1}},{{0,.5f,2},{0,0,-1},{.5f,0}},{{.5f,-.5f,2},{0,0,-1},{1,1}}};
  constexpr DWORD fvf=D3DFVF_XYZ|D3DFVF_NORMAL|D3DFVF_TEX1;
  ok(device->CreateVertexBuffer(sizeof(data),0,fvf,D3DPOOL_MANAGED,&vertices,nullptr),"warm vertices");
  void* target=nullptr;ok(vertices->Lock(0,0,&target,0),"warm upload");memcpy(target,data,sizeof(data));ok(vertices->Unlock(),"warm unlock");
  ok(device->CreateTexture(1,1,1,0,D3DFMT_A8R8G8B8,D3DPOOL_MANAGED,&texture,nullptr),"warm texture");
  D3DLOCKED_RECT tex{};ok(texture->LockRect(0,&tex,nullptr,0),"warm tex lock");*static_cast<DWORD*>(tex.pBits)=0xffffffff;ok(texture->UnlockRect(0),"warm tex unlock");
  D3DMATRIX identity{};identity._11=identity._22=identity._33=identity._44=1;
  D3DMATRIX projection{};projection._11=projection._22=1;projection._33=1.001f;projection._34=1;projection._43=-.1f;
  ok(device->SetTransform(D3DTS_WORLD,&identity),"warm world");ok(device->SetTransform(D3DTS_VIEW,&identity),"warm view");ok(device->SetTransform(D3DTS_PROJECTION,&projection),"warm projection");
  ok(device->SetVertexShader(nullptr),"warm VS");ok(device->SetPixelShader(nullptr),"warm PS");ok(device->SetFVF(fvf),"warm format");
  ok(device->SetStreamSource(0,vertices.Get(),0,sizeof(Vertex)),"warm stream");ok(device->SetTexture(0,texture.Get()),"warm image");
  ok(device->SetRenderState(D3DRS_LIGHTING,FALSE),"warm lighting");ok(device->SetRenderState(D3DRS_CULLMODE,D3DCULL_NONE),"warm cull");
  ok(device->SetRenderState(D3DRS_ZENABLE,TRUE),"warm depth");ok(device->SetRenderState(D3DRS_ZWRITEENABLE,TRUE),"warm depth write");
  ok(device->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_SELECTARG1),"warm colorop");ok(device->SetTextureStageState(0,D3DTSS_COLORARG1,D3DTA_TEXTURE),"warm colorarg");
 }
 profile.mark("render_warm_begin");const auto end=GetTickCount64()+10000;
 for(unsigned i=0;i<(triangle?56u:24u);++i){
  require(GetTickCount64()<end,"empty warm10s limit");
  ok(device->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xff000000,1,0),"empty warm clear");
  ok(device->BeginScene(),"empty warm begin");
  if(triangle&&i<24)ok(device->DrawPrimitive(D3DPT_TRIANGLELIST,0,1),"private warm triangle");
  ok(device->EndScene(),"empty warm end");
  ok(device->PresentEx(nullptr,nullptr,nullptr,nullptr,0),"empty warm present");
  MSG message{};while(PeekMessageW(&message,nullptr,0,0,PM_REMOVE)){TranslateMessage(&message);DispatchMessageW(&message);}
 }
 wait9(fence.Get(),poll);ok(saved->Apply(),"warm state restore");profile.mark("render_warm_complete");
 std::cout<<"RENDER_PREWARM mode="<<(triangle?"triangle":"empty")<<" frames="<<(triangle?56:24)<<" private_primitives="<<(triangle?1:0)<<" published=0 gpu_complete=1 state_restored=1\n";
}
}

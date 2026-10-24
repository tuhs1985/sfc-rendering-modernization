// Real SYSTEM native D3D9/9Ex, not Remix. Includes the actual shared Renderer.
#define SFC_D3D9_REPLAY_TYPES_ONLY
#include "../tools/d3d9_proof/d3d9_replay.cpp"
static std::vector<std::vector<BYTE>> exercise(IDirect3DDevice9* device,const Scene& scene,const fs::path& root){
 Renderer renderer(device,scene,root);D3DVERTEXBUFFER_DESC vb{};D3DINDEXBUFFER_DESC ib{};
 ok(renderer.vb->GetDesc(&vb),"VB descriptor");ok(renderer.ib->GetDesc(&ib),"IB descriptor");
 require(vb.Pool==D3DPOOL_DEFAULT&&ib.Pool==D3DPOOL_DEFAULT,"documented buffer pool");
 for(auto& texture:renderer.textures){D3DSURFACE_DESC d{};ok(texture->GetLevelDesc(0,&d),"texture descriptor");require(d.Pool==D3DPOOL_DEFAULT,"documented texture pool");}
 std::vector<std::vector<BYTE>> images;
 for(size_t i=0;i<(std::min)(size_t(3),scene.frames.size());++i){renderer.draw(scene.frames[i],false,scene.width,scene.height);images.push_back(renderer.pixels(scene.width,scene.height));}
 ok(device->SetTexture(0,nullptr),"unbind texture");ok(device->SetStreamSource(0,nullptr,0,0),"unbind VB");ok(device->SetIndices(nullptr),"unbind IB");
 return images;
}
int wmain(int argc,wchar_t** argv){try{
 require(argc==2,"fresh prepared scene directory required");SetEnvironmentVariableW(L"SFC_PIPELINE_MODE",L"test");
 const auto root=fs::absolute(argv[1]);const auto scene=load(root);
 wchar_t system[MAX_PATH]{};require(GetSystemDirectoryW(system,MAX_PATH)>0,"system directory");
 Module module;module.value=LoadLibraryExW((fs::path(system)/L"d3d9.dll").c_str(),nullptr,LOAD_LIBRARY_SEARCH_SYSTEM32);require(module.value!=nullptr,"native system D3D9");
 const auto create=reinterpret_cast<decltype(&Direct3DCreate9)>(GetProcAddress(module.value,"Direct3DCreate9"));
 const auto createEx=reinterpret_cast<decltype(&Direct3DCreate9Ex)>(GetProcAddress(module.value,"Direct3DCreate9Ex"));require(create&&createEx,"native D3D9/Ex exports");
 WNDCLASSW wc{};wc.hInstance=GetModuleHandleW(nullptr);wc.lpfnWndProc=proc;wc.lpszClassName=L"SFCResourcePolicyNative";require(RegisterClassW(&wc)!=0,"window class");
 Window window;window.value=CreateWindowW(wc.lpszClassName,L"Native resource policy test",WS_POPUP,0,0,scene.width,scene.height,nullptr,nullptr,wc.hInstance,nullptr);require(window.value!=nullptr,"native window");
 D3DPRESENT_PARAMETERS p{};p.BackBufferWidth=scene.width;p.BackBufferHeight=scene.height;p.BackBufferFormat=D3DFMT_A8R8G8B8;p.BackBufferCount=1;
 p.Windowed=TRUE;p.hDeviceWindow=window.value;p.SwapEffect=D3DSWAPEFFECT_DISCARD;p.EnableAutoDepthStencil=TRUE;p.AutoDepthStencilFormat=D3DFMT_D24S8;p.PresentationInterval=D3DPRESENT_INTERVAL_IMMEDIATE;
 ComPtr<IDirect3D9> api;api.Attach(create(D3D_SDK_VERSION));require(bool(api),"native API");ComPtr<IDirect3DDevice9> classic;
 ok(api->CreateDevice(0,D3DDEVTYPE_HAL,window.value,D3DCREATE_HARDWARE_VERTEXPROCESSING|D3DCREATE_FPU_PRESERVE,&p,&classic),"native classic device");
 const auto expected=exercise(classic.Get(),scene,root);classic.Reset();api.Reset();
 ComPtr<IDirect3D9Ex> apiEx;ok(createEx(D3D_SDK_VERSION,&apiEx),"native Ex API");ComPtr<IDirect3DDevice9Ex> ex;
 ok(apiEx->CreateDeviceEx(0,D3DDEVTYPE_HAL,window.value,D3DCREATE_HARDWARE_VERTEXPROCESSING|D3DCREATE_FPU_PRESERVE,&p,nullptr,&ex),"native Ex device");
 require(exercise(ex.Get(),scene,root)==expected,"classic and Ex pixel parity");
 // All DEFAULT resources have left scope/unbound before reset and are rebuilt
 // from the same immutable Scene and original packet-derived texture bytes.
 ok(ex->ResetEx(&p,nullptr),"native Ex reset");require(exercise(ex.Get(),scene,root)==expected,"reset/rebuild pixel parity");
 const auto prior=expected;ex.Reset();apiEx.Reset();
 ok(createEx(D3D_SDK_VERSION,&apiEx),"recreated Ex API");ok(apiEx->CreateDeviceEx(0,D3DDEVTYPE_HAL,window.value,D3DCREATE_HARDWARE_VERTEXPROCESSING|D3DCREATE_FPU_PRESERVE,&p,nullptr,&ex),"recreated Ex device");
 require(exercise(ex.Get(),scene,root)==prior,"device recreation pixel parity");auditModules();
 std::cout<<"Native resource policy PASS checks="<<checks<<" frames="<<expected.size()<<" classic_ex_pixels_exact=1 reset_exact=1 recreation_exact=1\n";return 0;
 }catch(const std::exception& e){std::cerr<<"Native resource policy FAILED "<<e.what()<<'\n';return 1;}}

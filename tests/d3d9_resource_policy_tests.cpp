// Real SYSTEM native D3D9/9Ex, not Remix. Includes the actual shared Renderer.
#define SFC_D3D9_REPLAY_TYPES_ONLY
#include "../tools/d3d9_proof/d3d9_replay.cpp"
static unsigned fastRenderers=0,fallbackRenderers=0;
static std::vector<std::vector<BYTE>> exercise(IDirect3DDevice9* device,const Scene& scene,const fs::path& root,TextureUpload policy=TextureUpload::StagedLock){
 uint32_t count=0;for(const auto& g:scene.groups)count=(std::max)(count,g.material+1);
 std::vector<std::vector<BYTE>> prepared;std::vector<const BYTE*> originals;
 if(policy==TextureUpload::InitialData)for(uint32_t i=0;i<count;++i){prepared.push_back(read(root/(L"texture-"+std::to_wstring(i)+L".bin"),64*1024*1024+16));originals.push_back(prepared.back().data());}
 Renderer renderer(device,scene,root,policy==TextureUpload::InitialData?&prepared:nullptr,policy);D3DVERTEXBUFFER_DESC vb{};D3DINDEXBUFFER_DESC ib{};
 if(policy==TextureUpload::InitialData){
  require(renderer.uploadBacking.size()==count,"source owner count");
  for(uint32_t i=0;i<count;++i)require(prepared[i].empty()&&renderer.uploadBacking[i].data()==originals[i],"source memory moved,not copied or borrowed");
  prepared.clear();prepared.shrink_to_fit(); // Caller containers gone before readback/draw.
  require(renderer.initialDataUploads+renderer.stagedUploads==count,"all uploads accounted");
  if(renderer.initialDataUnsupported){require(renderer.initialDataUnsupported==1&&renderer.stagedUploads==count,"unsupported contract falls back once per renderer");++fallbackRenderers;}
  else{require(renderer.initialDataUploads==count&&!renderer.stagedUploads,"supported contract uses only initial data");++fastRenderers;}
 }
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
 const auto expected=exercise(classic.Get(),scene,root);require(exercise(classic.Get(),scene,root,TextureUpload::InitialData)==expected,"classic initial-data pixels exact");classic.Reset();api.Reset();
 ComPtr<IDirect3D9Ex> apiEx;ok(createEx(D3D_SDK_VERSION,&apiEx),"native Ex API");ComPtr<IDirect3DDevice9Ex> ex;
 ok(apiEx->CreateDeviceEx(0,D3DDEVTYPE_HAL,window.value,D3DCREATE_HARDWARE_VERTEXPROCESSING|D3DCREATE_FPU_PRESERVE,&p,nullptr,&ex),"native Ex device");
 require(exercise(ex.Get(),scene,root)==expected,"classic and Ex pixel parity");
 require(exercise(ex.Get(),scene,root,TextureUpload::InitialData)==expected,"Ex initial-data pixels exact");
 // All DEFAULT resources have left scope/unbound before reset and are rebuilt
 // from the same immutable Scene and original packet-derived texture bytes.
 ok(ex->ResetEx(&p,nullptr),"native Ex reset");require(exercise(ex.Get(),scene,root)==expected,"reset/rebuild pixel parity");
 require(exercise(ex.Get(),scene,root,TextureUpload::InitialData)==expected,"initial-data reset/rebuild pixel parity");
 const auto prior=expected;ex.Reset();apiEx.Reset();
 ok(createEx(D3D_SDK_VERSION,&apiEx),"recreated Ex API");ok(apiEx->CreateDeviceEx(0,D3DDEVTYPE_HAL,window.value,D3DCREATE_HARDWARE_VERTEXPROCESSING|D3DCREATE_FPU_PRESERVE,&p,nullptr,&ex),"recreated Ex device");
 require(exercise(ex.Get(),scene,root)==prior,"device recreation pixel parity");require(exercise(ex.Get(),scene,root,TextureUpload::InitialData)==prior,"initial-data recreation pixel parity");auditModules();
 require(fastRenderers>0,"native initial-data contract exercised");
 std::cout<<"Native resource policy PASS checks="<<checks<<" frames="<<expected.size()<<" classic_ex_pixels_exact=1 reset_exact=1 recreation_exact=1 initial_data_pixels_exact=1 source_memory_owned=1 fast_renderers="<<fastRenderers<<" fallback_renderers="<<fallbackRenderers<<'\n';return 0;
 }catch(const std::exception& e){std::cerr<<"Native resource policy FAILED "<<e.what()<<'\n';return 1;}}

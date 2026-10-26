// Experimental x64 ordinary-D3D9 consumer plus supported Remix output API.
// Reuse EXACT replay parser/Renderer implementation;do not fork geometry or UVs.
#define SFC_D3D9_REPLAY_TYPES_ONLY
#define SFC_D3D9_REMIX_PROOF
#include "d3d9_replay.cpp"
#define REMIX_WINAPI_NO_LIBRARY_LOADER
#include <remix_c.h>
#include <d3d11.h>
#include <dxgi.h>
#include "output_producer.h"
#include "ingress_replay.h"
#include "live_owner_input.h"
static void apiok(remixapi_ErrorCode result,const char* why){if(result!=REMIXAPI_ERROR_CODE_SUCCESS){std::cerr<<"API_CODE "<<result<<' ';throw std::runtime_error(why);}}
#include "visual_controls.h"
#include "direct_lights.h"
#include "normal_coverage.h"
#include "game_output_wire.h"
#include "worker_gpu_fence.h"
#include "camera_left.h"
#include "deferred_diagnostics.h"
#include "multi_scene_runtime.h"
#include "pipeline_mode.h"
#include "warm_start.h"
#include "startup_profile.h"
static int64_t outputTicks(){LARGE_INTEGER t{};require(QueryPerformanceCounter(&t)!=FALSE,"output QPC");return t.QuadPart;}
struct SharedOutput{
 ComPtr<ID3D11Texture2D> image,staging;ComPtr<IDirect3DTexture9> imported;ComPtr<IDirect3DSurface9> surface;
};
struct PollTiming {uint64_t polls=0,sleeps=0,sleep_ticks=0,last_pending=0,ready=0;};
static PollTiming wait9(IDirect3DQuery9* query,WorkerPoll& poll,AssetService* service=nullptr){
 PollTiming timing{};
 ok(query->Issue(D3DISSUE_END),"output completion issue");const auto deadline=GetTickCount64()+5000;HRESULT status;
 for(;;){++timing.polls;status=query->GetData(nullptr,0,D3DGETDATA_FLUSH);const auto observed=outputTicks();if(status!=S_FALSE){timing.ready=observed;break;}
  timing.last_pending=observed;require(GetTickCount64()<deadline,"offline GPU completion5s limit");
  if(service)service->tick(AssetService::RenderQuery);
  ++timing.sleeps;poll.pause();timing.sleep_ticks+=outputTicks()-observed;}
 ok(status,"output completion");return timing;
}
#include "render_prewarm.h"
#include "texture_prefetch.h"
static void read11(ID3D11DeviceContext* context,ID3D11Query* query,SharedOutput& output,const fs::path& path,UINT width,UINT height){
 context->CopyResource(output.staging.Get(),output.image.Get());context->End(query);context->Flush();const auto deadline=GetTickCount64()+5000;BOOL complete=FALSE;HRESULT status;
 while((status=context->GetData(query,&complete,sizeof(complete),0))==S_FALSE||!complete){require(SUCCEEDED(status),"consumer query error");require(GetTickCount64()<deadline,"consumer5s limit");Sleep(1);}ok(status,"consumer completion");
 D3D11_MAPPED_SUBRESOURCE map{};ok(context->Map(output.staging.Get(),0,D3D11_MAP_READ,0,&map),"consumer readback");
 std::ofstream file(path,std::ios::binary);file.write(reinterpret_cast<const char*>(&width),4);file.write(reinterpret_cast<const char*>(&height),4);
 for(UINT y=0;y<height;++y)file.write(static_cast<const char*>(map.pData)+size_t(y)*map.RowPitch,width*4);
 context->Unmap(output.staging.Get(),0);require(bool(file),"readback file write");
}
int wmain(int argc,wchar_t** argv){
 const bool detailed=!pipeline_mode::performance();
 wchar_t buffered[2]{};const bool bufferedDiagnostics=GetEnvironmentVariableW(L"SFC_D3D9_LIVE_TIMING",buffered,2)==1&&buffered[0]==L'1';
 DeferredDiagnostics diagnosticLog(std::cout,bufferedDiagnostics);
 std::cout.setf(std::ios::unitbuf);remixapi_Interface external{};bool registered=false;
 Module module;Window window;ComPtr<IDirect3D9Ex> api;ComPtr<IDirect3DDevice9Ex> device;int result=1;
 StartupProfile startup;
 try{
  require(argc==3||argc==5,"replay directory,runtime and optional receiver/mode required");const fs::path root=fs::absolute(argv[1]),library=fs::absolute(argv[2]);
  const bool prewarm=warm_start::requested();Scene scene;if(prewarm){scene.width=1920;scene.height=1080;}else scene=load(root);
  wchar_t investigate[2]{};require(output_wire::qualified_extent(scene.width,scene.height)||(GetEnvironmentVariableW(L"SFC_DIRECT64_INVESTIGATE_EXTENT",investigate,2)==1&&investigate[0]==L'1'),"unqualified output extent;explicit offline investigation required");
  module.value=LoadLibraryExW(library.c_str(),nullptr,LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR|LOAD_LIBRARY_SEARCH_SYSTEM32);require(module.value!=nullptr,"direct runtime load");
  wchar_t actual[MAX_PATH]{};require(GetModuleFileNameW(module.value,actual,MAX_PATH)>0&&fs::equivalent(library,actual),"loaded runtime differs");
  const auto* dos=reinterpret_cast<IMAGE_DOS_HEADER*>(module.value);require(dos->e_magic==IMAGE_DOS_SIGNATURE,"runtime PE DOS");
  const auto* nt=reinterpret_cast<IMAGE_NT_HEADERS64*>(reinterpret_cast<BYTE*>(module.value)+dos->e_lfanew);
  require(nt->Signature==IMAGE_NT_SIGNATURE&&nt->FileHeader.Machine==IMAGE_FILE_MACHINE_AMD64&&nt->OptionalHeader.Magic==IMAGE_NT_OPTIONAL_HDR64_MAGIC,"runtime x64 PE32+");
  const auto initialize=reinterpret_cast<PFN_remixapi_InitializeLibrary>(GetProcAddress(module.value,"remixapi_InitializeLibrary"));require(initialize!=nullptr,"runtime API export");
  remixapi_InitializeLibraryInfo info{};info.sType=REMIXAPI_STRUCT_TYPE_INITIALIZE_LIBRARY_INFO;info.version=REMIXAPI_VERSION_MAKE(REMIXAPI_VERSION_MAJOR,REMIXAPI_VERSION_MINOR,REMIXAPI_VERSION_PATCH);
  apiok(initialize(&info,&external),"runtime output API init");
  std::cout<<"DIRECT64_CAPABILITIES copy="<<bool(external.dxvk_CopyRenderingOutput)<<" register="<<bool(external.dxvk_RegisterD3D9Device)<<" shutdown="<<bool(external.Shutdown)<<'\n';
  require(external.dxvk_CopyRenderingOutput&&external.dxvk_RegisterD3D9Device&&external.dxvk_SetDefaultOutput&&external.Shutdown,"required64bit output API absent");
  const auto create=reinterpret_cast<decltype(&Direct3DCreate9Ex)>(GetProcAddress(module.value,"Direct3DCreate9Ex"));require(create!=nullptr,"ordinary D3D9Ex export");
  ok(create(D3D_SDK_VERSION,&api),"ordinary D3D9Ex create");
  WNDCLASSW wc{};wc.hInstance=GetModuleHandleW(nullptr);wc.lpfnWndProc=proc;wc.lpszClassName=L"SFC_D3D9_Direct64";require(RegisterClassW(&wc)!=0,"direct64 window class");
  window.value=CreateWindowW(wc.lpszClassName,L"Offline direct64 D3D9 output",WS_POPUP,0,0,scene.width,scene.height,nullptr,nullptr,wc.hInstance,nullptr);require(window.value!=nullptr,"direct64 window");
  D3DPRESENT_PARAMETERS pp{};pp.BackBufferWidth=scene.width;pp.BackBufferHeight=scene.height;pp.BackBufferFormat=D3DFMT_A8R8G8B8;pp.BackBufferCount=1;pp.Windowed=TRUE;pp.hDeviceWindow=window.value;pp.SwapEffect=D3DSWAPEFFECT_DISCARD;pp.EnableAutoDepthStencil=TRUE;pp.AutoDepthStencilFormat=D3DFMT_D24S8;pp.PresentationInterval=D3DPRESENT_INTERVAL_IMMEDIATE;
  ok(api->CreateDeviceEx(0,D3DDEVTYPE_HAL,window.value,D3DCREATE_HARDWARE_VERTEXPROCESSING|D3DCREATE_FPU_PRESERVE,&pp,nullptr,&device),"ordinary D3D9Ex device");
  startup.mark("device_ready");
  apiok(external.dxvk_RegisterD3D9Device(device.Get()),"register ordinary device for output only");registered=true;
  {
   LUID adapterLuid{};ok(api->GetAdapterLUID(0,&adapterLuid),"renderer adapter LUID");
   ComPtr<IDXGIFactory1> factory;ok(CreateDXGIFactory1(IID_PPV_ARGS(&factory)),"native DXGI factory");ComPtr<IDXGIAdapter1> selected;
   for(UINT i=0;i<16;++i){ComPtr<IDXGIAdapter1> candidate;if(factory->EnumAdapters1(i,&candidate)==DXGI_ERROR_NOT_FOUND)break;DXGI_ADAPTER_DESC1 desc{};ok(candidate->GetDesc1(&desc),"consumer adapter desc");if(desc.AdapterLuid.HighPart==adapterLuid.HighPart&&desc.AdapterLuid.LowPart==adapterLuid.LowPart){selected=candidate;break;}}
   require(bool(selected),"consumer must match renderer GPU LUID");
   ComPtr<ID3D11Device> native;ComPtr<ID3D11DeviceContext> context;D3D_FEATURE_LEVEL level{};
   ok(D3D11CreateDevice(selected.Get(),D3D_DRIVER_TYPE_UNKNOWN,nullptr,D3D11_CREATE_DEVICE_BGRA_SUPPORT,nullptr,0,D3D11_SDK_VERSION,&native,&level,&context),"native D3D11 consumer");
   require(level>=D3D_FEATURE_LEVEL_11_0,"consumer feature level");
   wchar_t stagingFlag[2]{};const bool allocateStaging=!(GetEnvironmentVariableW(L"SFC_DIRECT64_TIMING_ONLY",stagingFlag,2)==1&&stagingFlag[0]==L'1');
   std::array<SharedOutput,3> outputs;std::array<uint64_t,3> sharedHandles{};const remixapi_dxvk_CopyRenderingOutputType types[]={REMIXAPI_DXVK_COPY_RENDERING_OUTPUT_TYPE_FINAL_COLOR,REMIXAPI_DXVK_COPY_RENDERING_OUTPUT_TYPE_DEPTH,REMIXAPI_DXVK_COPY_RENDERING_OUTPUT_TYPE_OBJECT_PICKING};
   for(unsigned i=0;i<3;++i){D3D11_TEXTURE2D_DESC desc{};desc.Width=scene.width;desc.Height=scene.height;desc.MipLevels=desc.ArraySize=desc.SampleDesc.Count=1;desc.Format=i?DXGI_FORMAT_R32_FLOAT:DXGI_FORMAT_B8G8R8A8_UNORM;desc.BindFlags=D3D11_BIND_RENDER_TARGET|D3D11_BIND_SHADER_RESOURCE;desc.MiscFlags=D3D11_RESOURCE_MISC_SHARED;
    ok(native->CreateTexture2D(&desc,nullptr,&outputs[i].image),"consumer shared image");ComPtr<IDXGIResource> resource;ok(outputs[i].image.As(&resource),"shared resource interface");HANDLE shared=nullptr;ok(resource->GetSharedHandle(&shared),"native shared handle");
    ok(device->CreateTexture(scene.width,scene.height,1,D3DUSAGE_RENDERTARGET,i?D3DFMT_R32F:D3DFMT_A8R8G8B8,D3DPOOL_DEFAULT,&outputs[i].imported,&shared),"ordinary device imports consumer image");ok(outputs[i].imported->GetSurfaceLevel(0,&outputs[i].surface),"shared output surface");
    sharedHandles[i]=reinterpret_cast<uintptr_t>(shared);
    if(allocateStaging){desc.BindFlags=desc.MiscFlags=0;desc.Usage=D3D11_USAGE_STAGING;desc.CPUAccessFlags=D3D11_CPU_ACCESS_READ;ok(native->CreateTexture2D(&desc,nullptr,&outputs[i].staging),"offline readback staging");}
   }
   require(uint64_t(scene.width)*scene.height*12<=128ull*1024*1024,"shared output resource limit");
   WorkerPoll renderPollWait;std::cout<<"WORKER_POLL microseconds="<<renderPollWait.microseconds<<" bounded_diagnostics="<<bufferedDiagnostics<<'\n';
   ComPtr<IDirect3DQuery9> fence;ok(device->CreateQuery(D3DQUERYTYPE_EVENT,&fence),"renderer completion query");ComPtr<ID3D11Query> consumerFence;D3D11_QUERY_DESC query{D3D11_QUERY_EVENT,0};ok(native->CreateQuery(&query,&consumerFence),"consumer completion query");
   remixapi_Float4D background{-1234,0,0,0},zero{};apiok(external.dxvk_SetDefaultOutput(types[1],&background),"depth background sentinel");apiok(external.dxvk_SetDefaultOutput(types[2],&zero),"picking background sentinel");
   DirectVisualControls visuals;visuals.start(external,native.Get(),outputs[0].image.Get());
   NormalCoverage coverage;coverage.start(native.Get(),outputs[1].image.Get(),outputs[2].image.Get());
   // Additive mode supplies its own UNION coverage; it never consumes vendor
   // picking. Only genuine picking consumers request vendor image retention.
   if(!coverage.enabled)apiok(external.dxvk_CopyRenderingOutput(outputs[2].surface.Get(),types[2]),"request picking image retention");
   WorkerGpuFence postFence;if(coverage.enabled)postFence.start(native.Get(),context.Get());
   const auto postValues=visuals.image.post();
   const bool combinedPost=coverage.enabled&&visuals.enabled&&(postValues[0]!=1||postValues[1]!=1||postValues[2]!=1);
   if(combinedPost){visuals.grade.prepareCoverage(native.Get(),outputs[1].image.Get(),outputs[2].image.Get());std::cout<<"COMBINED_POST grade_coverage=1 draws_per_frame=1\n";}
   wchar_t multiFlag[2]{};const bool multiMode=GetEnvironmentVariableW(L"SFC_D3D9_MULTISCENE",multiFlag,2)==1&&multiFlag[0]==L'1';
   float offsetX=0;if(coverage.enabled){wchar_t text[64]{};require(GetEnvironmentVariableW(L"SFC_D3D9_OFFSET_X",text,64)>0,"Additive offset required");offsetX=static_cast<float>(_wtof(text));require(std::isfinite(offsetX)&&(multiMode?(offsetX<=0&&offsetX>=-1e6f):(std::abs(offsetX)>1e-5f&&std::abs(offsetX)<=1e6f)),"explicit aligned-cohort or diagnostic offset bounds");}
   if(render_prewarm::requested()){require(prewarm,"render warm requires early-start workflow");render_prewarm::run(device.Get(),renderPollWait,startup);}
   ApiTexturePrefetch texturePrefetch;
   if(prewarm){startup.mark("idle_begin");
    if(ApiTexturePrefetch::requested()&&ApiTexturePrefetch::overlap())warm_start::wait(root,[&]{texturePrefetch.pump(root,external,fence.Get(),renderPollWait,startup);});
    else warm_start::wait(root);
    startup.mark("activated");scene=load(root);require(scene.width==1920&&scene.height==1080,"warm output extent unchanged");
    startup.mark("scene_loaded");
    if(ApiTexturePrefetch::requested())texturePrefetch.run(root,external,fence.Get(),renderPollWait,startup);
    apiok(external.SetConfigVariable("rtx.enableReplacementAssets","True"),"enable complete initial material library");
    startup.mark("materials_enabled");
    std::cout<<"WARM_ACTIVATED complete_material_library=1 replacements=1\n";}
   const auto sceneBytes=read(root/L"scene.bin",2*1024*1024);const auto sceneHash=output_wire::hash(sceneBytes.data(),sceneBytes.size());
   OutputPeer peer;if(argc==5)peer.start(fs::absolute(argv[3]),root,argv[4]);
   startup.mark("receiver_started");
   wchar_t single[2]{};const bool singlePresent=GetEnvironmentVariableW(L"SFC_DIRECT64_SINGLE_PRESENT",single,2)==1&&single[0]==L'1';
   wchar_t pacedValue[16]{};GetEnvironmentVariableW(L"SFC_DIRECT64_PACED_FRAMES",pacedValue,16);const unsigned paced=static_cast<unsigned>(_wtoi(pacedValue));require(paced==0||(paced>=60&&paced<=300),"offline paced frame cap");
   wchar_t liveValue[2]{};const bool liveMode=GetEnvironmentVariableW(L"SFC_D3D9_LIVE_TIMING",liveValue,2)==1&&liveValue[0]==L'1';
   wchar_t timingOnly[2]{};const bool noReadback=GetEnvironmentVariableW(L"SFC_DIRECT64_TIMING_ONLY",timingOnly,2)==1&&timingOnly[0]==L'1';require(!noReadback||paced||liveMode,"timing-only needs paced or live proof");
   require(!liveMode||(noReadback&&!paced&&argc==5&&std::wstring(argv[4])==L"normal"),"live timing requires isolated GPU receiver without readback");
   wchar_t latestValue[2]{},lagValue[16]{};const bool latest=GetEnvironmentVariableW(L"SFC_DIRECT64_LATEST_INPUT",latestValue,2)==1&&latestValue[0]==L'1';
   GetEnvironmentVariableW(L"SFC_DIRECT64_INJECT_LAG_MS",lagValue,16);const unsigned injectedLag=static_cast<unsigned>(_wtoi(lagValue));
   require((!latest&&!injectedLag)||(latest&&paced==300&&noReadback&&(injectedLag==0||injectedLag==35||injectedLag==60)),"offline latest-input test bounds");
   require(!liveMode||!latest,"live input excludes synthetic source");
   LARGE_INTEGER frequency{};require(QueryPerformanceFrequency(&frequency)!=FALSE,"output QPC frequency");
   IngressReplay ingress;uint64_t ingressAsset=0;std::ofstream inputTiming;if(latest){ingressAsset=ingressAssetHash(scene,root);inputTiming.open(root/L"input-timing.csv");inputTiming<<"sequence,source_frame,offered_qpc,deadline_qpc,completed_qpc,frequency,on_time\n";}
   LiveOwnerInput ownerInput;std::ofstream liveTiming;if(liveMode&&detailed){liveTiming.open(root/L"live-input.csv");liveTiming<<"sequence,source_frame,owner,revision,offered_qpc,completed_qpc,frequency,state_hash,output_sequence,taken_qpc,light_ready_qpc\n";}
   std::ofstream timing;if(detailed)timing.open(root/L"frame-timing.csv");
   DeferredDiagnostics deferredLive(liveTiming,liveMode&&detailed),deferredTiming(timing,liveMode&&detailed,2*1024*1024);
   if(detailed)timing<<"sequence,source_frame,presents,draw_present_us,output_gpu_us,local_readback_us,peer_us,scheduled_us,completed_us,copy_submit_us,render_ready_wait_us,postprocess_us,query_polls,query_sleeps,query_sleep_us,query_last_pending_qpc,query_ready_qpc,input_empty_polls,input_sleep_us,input_validation_us\n";int64_t scheduleStart=0;
   wchar_t textureFlag[2]{};const auto texturePolicy=GetEnvironmentVariableW(L"SFC_D3D9_INITIAL_TEXTURE_DATA",textureFlag,2)==1&&textureFlag[0]==L'1'?TextureUpload::InitialData:TextureUpload::StagedLock;
   std::cout<<"TEXTURE_UPLOAD initial_data="<<(texturePolicy==TextureUpload::InitialData)<<" source_lifetime="<<(texturePolicy==TextureUpload::InitialData?"renderer":"staging_scope")<<'\n';
   {Renderer renderer(device.Get(),scene,root,nullptr,texturePolicy);DirectLights lights;lights.start();MultiSceneRuntime cohort;cohort.start(root,device.Get(),scene,renderer,texturePolicy);
    AssetService admission;wchar_t admissionFlag[2]{};
    admission.start(cohort.enabled&&GetEnvironmentVariableW(L"SFC_D3D9_ADMISSION_SERVICE",admissionFlag,2)==1&&admissionFlag[0]==L'1',
      [](void* p){static_cast<MultiSceneRuntime*>(p)->assets();},&cohort);
    std::cout<<"ASSET_SERVICE enabled="<<admission.enabled<<" renderer_thread="<<GetCurrentThreadId()<<'\n';
    startup.mark("renderer_assets_started");
    if(cohort.enabled){ownerInput.idleWork=[](void* p){static_cast<MultiSceneRuntime*>(p)->assets();};ownerInput.idleContext=&cohort;}
    bool measuredCohort=false;
    uint64_t outputSequence=0;unsigned lightOmitted=0;
    // Live input supplies source-stop and elapsed watchdogs in next(); skipped
    // submissions must not consume a proof-era frame-count lifetime budget.
    for(size_t frame=0;run_lifetime::iteration(liveMode,frame,paced?paced+(latest?1u:0u):scene.frames.size());++frame){
     if(frame<2)startup.mark("frame_begin",static_cast<unsigned>(frame));
     admission.tick(AssetService::Boundary);
     Frame state=scene.frames[frame%scene.frames.size()];frame_ingress::Packet input{};
     live_owner::Packet rawInput{};if(liveMode&&frame){if(!ownerInput.next(scene,state,rawInput))break;}
     if(cohort.enabled&&frame&&!cohort.next(rawInput))continue;
     const auto takenAt=outputTicks();
     if(latest&&frame){if(!ingress.next(input,state))break;}
     float displacement[3]{};
     if(coverage.enabled&&offsetX!=0){require(diagnostic_offset::camera_left(state.view,-offsetX,displacement),"qualified camera-left offset");for(unsigned i=0;i<3;++i)state.model[i*4+3]+=displacement[i];} // Raw packet unchanged.
     if(!(liveMode&&!frame)&&!lights.update(external,state,liveMode&&frame?&rawInput:nullptr,ownerInput,static_cast<uint64_t>(frequency.QuadPart))){
      require(liveMode,"Offline light fixture association required");if(lightOmitted++<32)std::cout<<"LIGHT_INPUT_UNAVAILABLE source_sequence="<<rawInput.sequence<<" source_frame="<<state.frame<<'\n';continue;
     }
     if(liveMode&&frame&&!ownerInput.admit(rawInput))continue;
     const bool measureCohort=cohort.enabled&&frame&&!measuredCohort;
     if(paced&&frame&&!latest){if(!scheduleStart)scheduleStart=outputTicks();const auto due=scheduleStart+static_cast<int64_t>(frame-1)*frequency.QuadPart/60;while(outputTicks()<due)Sleep(1);}
     // TRANSITIONAL compatibility policy, NOT NVIDIA-required readiness.
     // Run160 tested one startup Present: earlier pixels exposed incomplete
     // initial appearance and later misses. Keep the accepted policy until a
     // vendor-backed material lifecycle replacement is qualified. Ordinary
     // live updates remain one Present; GPU/source checks are independent.
     const auto began=outputTicks();const unsigned presents=(singlePresent||liveMode)&&frame?1u:24u;
     if(measureCohort)startup.mark("cohort_draw_begin");
     bool submitted=false;
     for(unsigned warm=0;warm<presents;++warm){if(!frame)startup.mark("bootstrap_begin",warm,false);lights.draw(external);if(cohort.enabled&&frame){if(!cohort.draw(scene.width,scene.height,displacement))break;}else renderer.draw(state,false,scene.width,scene.height);if(!frame)startup.mark("bootstrap_drawn",warm,false);submitted=true;ok(device->PresentEx(nullptr,nullptr,nullptr,nullptr,0),"normal D3D9 PresentEx");
      admission.tick(frame?AssetService::Boundary:AssetService::Bootstrap);
      if(!frame)startup.mark("bootstrap_presented",warm,false);
      MSG message{};while(PeekMessageW(&message,nullptr,0,0,PM_REMOVE)){TranslateMessage(&message);DispatchMessageW(&message);}if(presents>1)Sleep(10);
     }
     if(!submitted)continue;
     const auto drawn=outputTicks();
     if(measureCohort)startup.mark("cohort_draw_end");
     // Offline independent check:did ordinary rasterization produce the ship
     // while returned ray-traced output remained empty? Never a live transport.
     wchar_t diagnostic[2]{};
     if(GetEnvironmentVariableW(L"SFC_DIRECT64_BACKBUFFER_DIAGNOSTIC",diagnostic,2)==1&&diagnostic[0]==L'1')
      renderer.save(root/(L"ordinary-color-"+std::to_wstring(frame)+L".bgra"),scene.width,scene.height);
     if(peer.disconnected){std::cout<<"OUTPUT_OMITTED peer_retired=1 source_frame="<<state.frame<<'\n';continue;}
     // Additive coverage replaces ordinary picking from semantic identity/depth.
     // Do not copy an unused vendor picking image every frame.
     for(unsigned i=0;i<(coverage.enabled?2u:3u);++i)apiok(external.dxvk_CopyRenderingOutput(outputs[i].surface.Get(),types[i]),"copy normal rendered output");
     const auto copiesQueued=outputTicks();
     const auto renderPoll=wait9(fence.Get(),renderPollWait,&admission);
     const auto renderReady=outputTicks();
     const bool graded=combinedPost?visuals.grade.drawCoverage(context.Get(),outputs[0].image.Get(),visuals.image.post(),state.owner):visuals.apply(context.Get(),outputs[0].image.Get());
     const bool covered=combinedPost||coverage.draw(context.Get(),state.owner,scene.width,scene.height);
     if(graded||covered){
      if(coverage.enabled)postFence.wait(&admission);else{
      context->End(consumerFence.Get());context->Flush();const auto limit=GetTickCount64()+5000;BOOL done=FALSE;HRESULT status;
      do{status=context->GetData(consumerFence.Get(),&done,sizeof(done),0);ok(status,"coverage GPU completion");require(GetTickCount64()<limit,"coverage GPU5s limit");if(status==S_FALSE||!done)Sleep(1);}while(status==S_FALSE||!done);
      }
     }
     const auto outputDone=outputTicks();
     if(measureCohort)startup.mark("cohort_output_complete");
     if(frame<2)startup.mark("output_complete",static_cast<unsigned>(frame));
     if(!noReadback&&(!paced||frame==0||(frame+1)%output_wire::verification_stride==0))for(unsigned i=0;i<3;++i)read11(context.Get(),consumerFence.Get(),outputs[i],root/(L"returned-"+std::to_wstring(frame)+L"-"+std::to_wstring(i)+L".raw32"),scene.width,scene.height);
     const auto localDone=outputTicks();
     if(detailed)std::cout<<"RETURNED frame="<<frame<<" source_frame="<<state.frame<<" completed=1 ordinary_draws=1\n";
     ++outputSequence;
     if(argc==5){output_wire::Packet p{};p.sequence=outputSequence;p.source_frame=state.frame;p.owner=state.owner;p.revision=state.revision;p.source_state_hash=liveMode&&frame?rawInput.state_hash:output_wire::hash(&state,sizeof(Frame));p.scene_hash=sceneHash;p.width=scene.width;p.height=scene.height;p.luid_low=adapterLuid.LowPart;p.luid_high=adapterLuid.HighPart;memcpy(p.handles,sharedHandles.data(),sizeof(p.handles));
      if(liveMode&&frame){game_output::Metadata meta{};meta.source_sequence=rawInput.sequence;memcpy(meta.source_session,rawInput.session,16);meta.checksum=game_output::checksum(meta);game_output::metadata(*peer.channel,meta);}
      if(cohort.enabled&&frame)p.source_state_hash=cohort.packet.checksum;
      peer.publish(p,&admission);}
     if(frame<2)startup.mark("receiver_ack",static_cast<unsigned>(frame));
     if(measureCohort){startup.mark("cohort_receiver_ack");measuredCohort=true;}
     const auto peerDone=outputTicks();const auto us=[&](int64_t a,int64_t b){return (b-a)*1000000/frequency.QuadPart;};
     if((admission.enabled||startup.enabled)&&(frame==0||measureCohort))std::cout<<"OUTPUT_STAGE_TIMING index="<<frame<<" source_frame="<<state.frame<<" frequency="<<frequency.QuadPart
       <<" began_qpc="<<began<<" peer_done_qpc="<<peerDone<<" draw_present_us="<<us(began,drawn)<<" copy_submit_us="<<us(drawn,copiesQueued)
       <<" query_wait_us="<<us(copiesQueued,renderReady)<<" postprocess_us="<<us(renderReady,outputDone)<<" peer_us="<<us(localDone,peerDone)
       <<" admission_service_total_us="<<us(0,static_cast<int64_t>(admission.ticks))<<'\n';
     if(liveMode){if(!frame)ownerInput.start(scene);
      else{if(!coverage.enabled||!peer.channel->reserved){ownerInput.complete(rawInput,static_cast<uint64_t>(peerDone));if(detailed){liveTiming<<rawInput.sequence<<','<<state.frame<<','<<state.owner<<','<<state.revision<<','<<rawInput.offered<<','<<peerDone<<','<<frequency.QuadPart<<','<<rawInput.state_hash<<','<<outputSequence<<','<<takenAt<<','<<began<<'\n';require(bool(liveTiming),"live timing output");}}else if(detailed)std::cout<<"GAME_POOL_OMITTED source_sequence="<<rawInput.sequence<<'\n';}}
     if(detailed){timing<<frame+1<<','<<state.frame<<','<<presents<<','<<us(began,drawn)<<','<<us(drawn,outputDone)<<','<<us(outputDone,localDone)<<','<<us(localDone,peerDone)<<','<<(paced&&frame&&!latest?static_cast<int64_t>(frame-1)*1000000/60:-1)<<','<<(paced&&frame&&!latest?us(scheduleStart,peerDone):-1)<<','<<us(drawn,copiesQueued)<<','<<us(copiesQueued,renderReady)<<','<<us(renderReady,outputDone)<<','<<renderPoll.polls<<','<<renderPoll.sleeps<<','<<us(0,renderPoll.sleep_ticks)<<','<<renderPoll.last_pending<<','<<renderPoll.ready<<','<<ownerInput.empty_polls<<','<<us(0,ownerInput.sleep_ticks)<<','<<us(0,ownerInput.validation_ticks)<<'\n';require(bool(timing),"timing output");}
     if(latest){
      if(!frame)ingress.start(scene,ingressAsset,paced,static_cast<uint64_t>(frequency.QuadPart),injectedLag);
      else{const bool onTime=frame_ingress::usable(input,input.key,static_cast<uint64_t>(peerDone),true);
       inputTiming<<input.key.sequence<<','<<state.frame<<','<<input.offered_qpc<<','<<input.deadline_qpc<<','<<peerDone<<','<<frequency.QuadPart<<','<<onTime<<'\n';require(bool(inputTiming),"input timing output");}
     }
    }
    if(latest)std::cout<<"INPUT_REPLAY_COMPLETE source_late="<<ingress.source_late<<" obsolete="<<ingress.stats.obsolete<<" expired="<<ingress.stats.expired<<" invalid="<<ingress.stats.invalid<<" lag_used="<<ingress.lag_used<<" lag_sequence="<<ingress.lag_sequence<<" mapping_bytes="<<sizeof(frame_ingress::Channel)<<'\n';
    if(liveMode)std::cout<<"LIVE_OWNER_COMPLETE received="<<ownerInput.received<<" invalid="<<ownerInput.invalid<<" unqualified="<<ownerInput.unqualified<<" game_drawing=0\n";
    if(liveMode)std::cout<<"LIVE_OUTPUT_SUMMARY outputs="<<outputSequence<<" light_omitted="<<lightOmitted<<'\n';
    if(liveMode){std::cout<<"LIVE_ADMISSION expired="<<ownerInput.expired<<" old_epoch="<<ownerInput.oldPackets<<" maximum_age_us="<<(ownerInput.closedFrame?50000:2000)<<'\n';
     for(unsigned stage=0;stage<2;++stage){std::cout<<"LIVE_ADMISSION_STAGE stage="<<stage;
      for(unsigned reason=0;reason<static_cast<unsigned>(live_owner::Admission::Count);++reason)std::cout<<" reason"<<reason<<'='<<ownerInput.admissionCounts[stage][reason];std::cout<<'\n';}}
    if(admission.enabled)std::cout<<"ASSET_SERVICE_SUMMARY bootstrap="<<admission.calls[AssetService::Bootstrap]<<" query="<<admission.calls[AssetService::RenderQuery]
      <<" post="<<admission.calls[AssetService::Postprocess]<<" peer="<<admission.calls[AssetService::Peer]<<" boundary="<<admission.calls[AssetService::Boundary]
      <<" ticks="<<admission.ticks<<" frequency="<<frequency.QuadPart<<'\n';
    lights.close(external);
   }
   if(argc==5)peer.finish();
   texturePrefetch.close(fence.Get(),renderPollWait);
   ok(device->SetTexture(0,nullptr),"unbind texture");ok(device->SetStreamSource(0,nullptr,0,0),"unbind VB");ok(device->SetIndices(nullptr),"unbind IB");wait9(fence.Get(),renderPollWait);context->ClearState();context->Flush();
   ok(native->GetDeviceRemovedReason(),"consumer device remains valid");
  }
  auditModules();std::cout<<"DIRECT64_OUTPUT_RETURNED sdk_mesh_calls=0 offline_readback_only=1\n";result=0;
 }catch(const warm_start::Cancelled&){std::cout<<"WARM_CANCELLED no_scene_submitted=1\n";result=0;}
 catch(const std::exception& error){std::cerr<<"DIRECT64_FAILED "<<error.what()<<'\n';}
 if(registered){device.Detach();api.Detach();const auto status=external.Shutdown();std::cout<<"OUTPUT_API_SHUTDOWN "<<status<<'\n';if(status!=REMIXAPI_ERROR_CODE_SUCCESS)result=1;}
 return result;
}

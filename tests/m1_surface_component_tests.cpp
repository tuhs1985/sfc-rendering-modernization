// Production recorder/helper fixture. No game launch or installed hooks.
#include "../tools/m1_component/m1_component.cpp"
#include <cstdlib>
#include <iostream>

void require_surface(bool ok,const char* message){if(!ok){std::cerr<<message<<'\n';std::exit(1);}}
int wmain(int argc,wchar_t** argv) {
    InitializeCriticalSection(&g_lock);g_running=g_gate=g_saturated=1;
    g_config.enable_surface_lighting=g_config.enable_private_copy=g_config.enable_wrapper_observation=true;
    g_config.enable_corner_snapshot=true;g_config.enable_geometry_hook=false;
    g_copy_ready_event=CreateEventW(nullptr,TRUE,TRUE,nullptr);
    HMODULE pinned=nullptr;
    g_copy_module_pinned=GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_PIN|GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS,
        reinterpret_cast<LPCWSTR>(&g_surface_graphs),&pinned)!=FALSE;
    require_surface(g_copy_module_pinned,"module pin succeeds");
    std::array<DWORD,35> ship{};std::array<DWORD,1> visual{kVisualVtable};
    std::array<DWORD,7> model{};std::array<DWORD,2048> manager{};
    std::array<DWORD,9> source{};source[0]=2;source[1]=0x00ffffff;
    std::array<DWORD,7> polygon{3,0,0x3f800000,0,0,0,0};
    std::array<DWORD,21> corners{};for(unsigned c=0;c<3;++c){corners[c*7]=c;corners[c*7+1]=0x3f800000;}
    polygon[6]=reinterpret_cast<DWORD>(corners.data());std::array<DWORD,1> list{reinterpret_cast<DWORD>(polygon.data())};
    ship[0]=kShipVtable;ship[34]=reinterpret_cast<DWORD>(visual.data());
    model[0]=kModel0Vtable;model[2]=3;model[4]=1;model[5]=reinterpret_cast<DWORD>(list.data());manager[0]=0x007B8D4C;
    const DWORD original_source=reinterpret_cast<DWORD>(source.data());
    manager[0x558/4]=original_source;
    const auto original_polygon=polygon;const auto original_corners=corners;const auto original_source_bytes=source;
    auto* state=thread_state(GetCurrentThreadId());
    const auto frame=[&](DWORD elapsed) {
        ++g_frame;
        state->ship=reinterpret_cast<DWORD>(ship.data());state->visual=reinterpret_cast<DWORD>(visual.data());
        state->owner_id=g_owners.observe(state->ship,state->visual,static_cast<DWORD>(g_frame)).id;
        state->model0=reinterpret_cast<DWORD>(model.data());state->model_manager=reinterpret_cast<DWORD>(manager.data());
        state->source=original_source;state->model_scope=true;state->copy_depth=1;state->wrapper_pending=0;
        std::array<DWORD,5> model_stack{0x0042FDD5,state->model_manager,original_source,0,0};
        std::array<DWORD,9> saved{};saved[3]=reinterpret_cast<DWORD>(model_stack.data())-4;
        EventRecord event{};event.owner_id=state->owner_id;event.thread_id=GetCurrentThreadId();
        event.model0=state->model0;event.manager=state->model_manager;event.source=state->source;
        if(g_surface_tick)g_surface_tick=GetTickCount64()-elapsed;
        begin_surface_model(state,event,saved.data());
        if(state->tint_lease.active){
            require_surface(model_stack[2]!=original_source && state->tint_snapshot.bytes[4]==255 &&
                state->tint_snapshot.bytes[5]==0 && state->tint_snapshot.bytes[6]==255,"magenta source identified");
            manager[0x558/4]=model_stack[2]; // Emulate original Model0 source initializer.
        }
        std::array<DWORD,5> wrapper_stack{0x0042E55D,1,model[5],1,0};
        saved[3]=reinterpret_cast<DWORD>(wrapper_stack.data())-4;saved[6]=state->model_manager;
        RecordHook(kWrapper,saved.data());
        const auto phase=sfc_m1::surface_test_phase(elapsed);
        if(phase==1 || phase==2){
            const auto& graph=phase==1?g_surface_graphs.neutral:g_surface_graphs.altered;
            require_surface(wrapper_stack[2]==reinterpret_cast<DWORD>(graph.list.data()),"correct phase graph reaches original argument");
            std::array<DWORD,5> prepare_stack{0x006AC600,1,1,wrapper_stack[2],1};
            saved[3]=reinterpret_cast<DWORD>(prepare_stack.data())-4;RecordHook(kPrepare,saved.data());
        }else require_surface(wrapper_stack[2]==model[5],"original geometry in marker/restored phases");
        RecordHook(kVisualExit,saved.data());
        require_surface(!g_surface_failure && !g_tint_live && manager[0x558/4]==original_source &&
            polygon==original_polygon && corners==original_corners && source==original_source_bytes,
            "source lease restored, original payload unchanged");
    };
    frame(0);frame(19000);frame(19990);
    frame(20010);frame(22500);frame(24990);
    frame(25010);frame(32000);frame(39990);frame(41000);
    require_surface(g_surface_phases[0].applied==3 && g_surface_phases[1].applied==3 &&
        g_surface_phases[2].applied==3 && g_surface_phases[3].applied==0 && g_surface_graphs.intact(),"complete sequence with one immutable target");
    if(argc>1)g_config.output_dir=argv[1];else g_config.output_dir=L"artifacts\\m1\\test-temp\\surface-component";
    require_surface(M1Stop(nullptr)==0 && g_surface_graphs.intact(),"actual stop retains graph pair");
    // A changed original cannot be rendered with stale private data.
    g_running=1;g_surface_tick=GetTickCount64()-30000;
    state->owner_id=g_surface_owner;state->model_scope=true;state->copy_depth=1;state->wrapper_pending=0;
    state->ship=g_surface_ship;state->visual=g_surface_visual;state->model0=g_surface_model;
    state->source=g_surface_source;state->model_manager=g_surface_manager;
    std::array<DWORD,5> wrapper_stack{0x0042E55D,1,model[5],1,0};std::array<DWORD,9> saved{};
    saved[3]=reinterpret_cast<DWORD>(wrapper_stack.data())-4;saved[6]=state->model_manager;
    corners[1]^=1;RecordHook(kWrapper,saved.data());
    require_surface(g_surface_failure==6 && wrapper_stack[2]==model[5] && g_surface_graphs.intact(),"changed input fails open without overwriting immutable graph");
    g_running=0;CloseHandle(g_copy_ready_event);DeleteCriticalSection(&g_lock);
    std::cout<<"Production surface sequence/cleanup/fail-open tests passed.\n";
}

// Production selection/config/stop writer with synthetic native x86 objects.
// No game launch, process injection, installed hooks or native code patches.
#include "../tools/m1_component/m1_component.cpp"
#include <iostream>
#include <cstdlib>

void require_mesh(bool ok,const char* why){if(!ok){std::cerr<<why<<'\n';std::exit(1);}}
int wmain(int argc,wchar_t** argv) {
    require_mesh(argc==2,"output directory required");
    InitializeCriticalSection(&g_lock);g_running=g_gate=1;g_gate_tick=GetTickCount64();
    g_config.output_dir=argv[1];CreateDirectoryW(argv[1],nullptr);
    const auto ini=g_config.output_dir+L"\\mesh-test.ini";
    {
        std::ofstream config(narrow(ini));config << "[m1]\nOutputDirectory=" << narrow(g_config.output_dir)
            << "\nEnableMeshExport=1\nEnableWrapperObservation=1\nEnableGeometryHook=0\n";
    }
    require_mesh(load_config(ini.c_str()),"valid read-only export configuration");
    require_mesh(!g_config.enable_texture_references,"texture reference capture is default off");
    WritePrivateProfileStringW(L"m1",L"EnableTextureReferences",L"1",ini.c_str());
    require_mesh(load_config(ini.c_str()) && g_config.enable_texture_references,"texture reference opt-in accepted with mesh");
    WritePrivateProfileStringW(L"m1",L"LiveChannel",L"Local\\SFCBridge_0123456789abcdef0123456789abcdef",ini.c_str());
    require_mesh(load_config(ini.c_str()),"live opt-in accepted only with read-only asset mode");
    WritePrivateProfileStringW(L"m1",L"EnableTextureReferences",L"0",ini.c_str());
    require_mesh(!load_config(ini.c_str()),"live without references rejected");
    WritePrivateProfileStringW(L"m1",L"LiveChannel",L"Global\\bad",ini.c_str());
    require_mesh(!load_config(ini.c_str()),"malformed live session rejected");
    WritePrivateProfileStringW(L"m1",L"LiveChannel",L"",ini.c_str());
    WritePrivateProfileStringW(L"m1",L"EnableTextureReferences",L"1",ini.c_str());
    WritePrivateProfileStringW(L"m1",L"EnableMeshExport",L"0",ini.c_str());
    require_mesh(!load_config(ini.c_str()),"texture references without mesh rejected");
    WritePrivateProfileStringW(L"m1",L"EnableMeshExport",L"1",ini.c_str());
    WritePrivateProfileStringW(L"m1",L"EnableTextureReferences",L"0",ini.c_str());
    WritePrivateProfileStringW(L"m1",L"EnablePrivateCopy",L"1",ini.c_str());
    require_mesh(!load_config(ini.c_str()),"mutation combination rejected");
    WritePrivateProfileStringW(L"m1",L"EnablePrivateCopy",L"0",ini.c_str());
    WritePrivateProfileStringW(L"m1",L"EnableGeometryHook",L"1",ini.c_str());
    require_mesh(!load_config(ini.c_str()),"hot geometry rejected");
    WritePrivateProfileStringW(L"m1",L"EnableGeometryHook",L"0",ini.c_str());
    require_mesh(load_config(ini.c_str()),"read-only mode restored");
    std::array<DWORD,35> ship{};std::array<DWORD,100> visual{};
    std::array<DWORD,6> model{};std::array<DWORD,2048> manager{};std::array<DWORD,9> source{};
    std::array<DWORD,9> positions{0,0,0,0x3f800000,0,0,0,0x3f800000,0};
    std::array<DWORD,21> corners{};
    for(DWORD c=0;c<3;++c){corners[c*7]=c;corners[c*7+3]=0x3f800000;}
    std::array<DWORD,7> polygon{3,0,0,0,0x3f800000,0,reinterpret_cast<DWORD>(corners.data())};
    std::array<DWORD,1> list{reinterpret_cast<DWORD>(polygon.data())};
    ship[0]=kShipVtable;ship[34]=reinterpret_cast<DWORD>(visual.data());
    visual[0]=kVisualVtable;visual[0x11c/4]=1;visual[0x120/4]=0xffffffff;
    visual[0x158/4]=reinterpret_cast<DWORD>(source.data());visual[0x160/4]=reinterpret_cast<DWORD>(model.data());
    model={kModel0Vtable,0,3,reinterpret_cast<DWORD>(positions.data()),1,reinterpret_cast<DWORD>(list.data())};
    manager[0]=0x007B8D4C;manager[0x554/4]=model[3];manager[0x558/4]=visual[0x158/4];
    const auto before_positions=positions;
    const auto before_corners=corners;
    auto* state=thread_state(GetCurrentThreadId());
    state->thread_id=GetCurrentThreadId();state->ship=reinterpret_cast<DWORD>(ship.data());
    state->visual=reinterpret_cast<DWORD>(visual.data());state->model0=reinterpret_cast<DWORD>(model.data());
    state->source=visual[0x158/4];state->model_manager=reinterpret_cast<DWORD>(manager.data());
    state->owner_id=g_owners.observe(state->ship,state->visual,0).id;
    state->model_scope=false;state->copy_depth=0;state->wrapper_pending=0;
    std::array<DWORD,5> entry_stack{0x0042FDD5,state->model_manager,state->source,0,0};
    const auto original_entry=entry_stack;std::array<DWORD,9> entry_saved{};
    entry_saved[3]=reinterpret_cast<DWORD>(entry_stack.data())-4;
    entry_saved[6]=state->model0;entry_saved[1]=state->visual;
    RecordHook(kModel0,entry_saved.data());
    require_mesh(state->model_scope && state->copy_depth==1 && entry_stack==original_entry,
        "actual Model0 recorder establishes read-only export depth without altering arguments");
    state->wrapper_pending=1;
    EventRecord event{};event.ecx=state->model_manager;event.thread_id=state->thread_id;
    event.arg1=1;event.arg2=list.empty()?0:reinterpret_cast<DWORD>(list.data());event.return_address=0x0042E55D;
    const auto read=[](DWORD address,void* out,DWORD size){
        if(address==0x00C69FF0 || address==0x00C69FF4 || address==0x00C74058){std::memset(out,0,size);return true;}
        return safe_copy(address,out,size);
    };
    observe_mesh_export(state,event,2,read);require_mesh(!g_mesh_budget.attempts,"secondary excluded");
    state->copy_depth=2;observe_mesh_export(state,event,1,read);require_mesh(!g_mesh_budget.attempts,"nested excluded");
    state->copy_depth=1;observe_mesh_export(state,event,1,read);
    require_mesh(g_mesh_packet.complete && g_mesh_budget.attempts==1,"production selection invokes collector");
    std::array<DWORD,5> stack{0x0042E55D,1,reinterpret_cast<DWORD>(list.data()),1,0};
    const auto before_stack=stack;std::array<DWORD,9> saved{};
    saved[3]=reinterpret_cast<DWORD>(stack.data())-4;saved[6]=state->model_manager;state->wrapper_pending=0;
    RecordHook(kWrapper,saved.data());
    require_mesh(stack==before_stack && positions==before_positions && corners==before_corners &&
        g_mesh_budget.attempts==1,"actual recorder passes original arguments/data and never recaptures complete packet");
    RecordHook(kVisualExit,saved.data());
    require_mesh(!state->copy_depth && !state->wrapper_pending && !state->model_scope,"actual parent exit drains export scope");
    require_mesh(M1Stop(nullptr)==0,"actual stop restores/writes and returns success");
    require_mesh(g_mesh_packet.complete && g_in_recorders==0 && g_tint_live==0,"stop leaves no native lease");
    DeleteCriticalSection(&g_lock);
    std::cout<<"Production mesh configuration, scope, pass-through and stop writer tests passed.\n";
}

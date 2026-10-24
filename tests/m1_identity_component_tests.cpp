// Exercise actual recorder choices after detailed logging has saturated.
// Synthetic x86 memory ONLY;no game process,hook installation or native VA patch.
#include "../tools/m1_component/m1_component.cpp"
#include <iostream>
int main(int argc,char** argv){
    auto test=[](bool okay){if(!okay){std::cerr<<"Production identity census FAIL\n";std::exit(1);}};
    InitializeCriticalSection(&g_lock);g_gate=1;g_gate_tick=GetTickCount64()-10000;g_start_tick=g_gate_tick;
    g_running=1;g_saturated=1;g_frame=600;g_live_scene_mode=true;
    EventRecord disabled{};record_identity(disabled,{},0);test(!g_identity_census.enabled);
    multi_scene::Store cohort{};g_live_scene.cohort.store=&cohort;
    std::array<DWORD,1> visual{kVisualVtable};std::array<DWORD,8> model{};model[0]=kModel0Vtable;
    std::array<std::array<DWORD,0x88/4+1>,3> ships{};
    std::array<DWORD,5> stack{kVisualMainlineReturn,0,0,0,0};std::array<DWORD,9> saved{};
    saved[3]=reinterpret_cast<DWORD>(stack.data())-4;
    for(auto& ship:ships){ship[0]=kShipVtable;ship[0x88/4]=reinterpret_cast<DWORD>(visual.data());
        saved[6]=reinterpret_cast<DWORD>(ship.data());RecordHook(kShip,saved.data());
        saved[6]=reinterpret_cast<DWORD>(model.data());saved[1]=reinterpret_cast<DWORD>(visual.data());RecordHook(kModel0,saved.data());++g_frame;}
    test(g_owners.active_count()==3&&g_identity_census.count==6&&g_event_count==0);
    unsigned mismatches=0;for(DWORD i=0;i<g_identity_census.count;++i){const auto& e=g_identity_census.entries[i];using C=sfc_m1::IdentityCensus;
        test(e.first_ms>=9265);if(e.key[C::Kind]==3){test(e.key[C::ChosenOwner]==e.key[C::ContextShipOwner]);test(e.key[C::VisualOwnerCount]>=1);
            mismatches+=e.key[C::ChosenOwner]!=e.key[C::ContextShipOwner];}}
    test(mismatches==0); // Shared geometry must not collapse native owners.
    if(argc==2){std::ofstream out(argv[1]);out<<"{\"identity_census\":";g_identity_census.write(out);out<<'}';test(bool(out));}
    auto* context=thread_state(GetCurrentThreadId());test(context!=nullptr);
    context->ship=context->visual=context->owner_id=0;
    RecordHook(kModel0,saved.data());
    test(g_identity_census.entries[g_identity_census.count-1].key[sfc_m1::IdentityCensus::ChosenOwner]==0);
    context->ship=reinterpret_cast<DWORD>(ships[1].data());context->visual=reinterpret_cast<DWORD>(visual.data());context->owner_id=2;
    ships[1][0x88/4]=0;RecordHook(kModel0,saved.data());
    test(g_identity_census.entries[g_identity_census.count-1].key[sfc_m1::IdentityCensus::Reason]==12);
    ships[1][0x88/4]=context->visual;g_owners.destroy_ship(context->ship);g_owners.observe(context->ship,context->visual,static_cast<DWORD>(g_frame));
    RecordHook(kModel0,saved.data());
    test(g_identity_census.entries[g_identity_census.count-1].key[sfc_m1::IdentityCensus::ChosenOwner]==0);
    g_live_scene.cohort.store=nullptr;g_running=0;DeleteCriticalSection(&g_lock);
    std::cout<<"Production identity census PASS synthetic_ships=3 shared_visual=1 choice_mismatches=0 beyond_detail_window=1 guarded_rejections=3\n";
}

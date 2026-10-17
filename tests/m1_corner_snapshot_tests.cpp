// Synthetic x86 objects; no SFC process, target code patch or geometry hook.
#include "../tools/m1_component/m1_component.cpp"
#include <cstdlib>
#include <iostream>

void require_corner(bool ok, const char* message) {
    if (!ok) { std::cerr << "FAIL: " << message << '\n'; std::exit(1); }
}
// Replay exactly the wrapper's displaced five bytes, then read original args.
__declspec(naked) DWORD wrapper_trampoline_fixture() {
    __asm { sub esp,8 }
    __asm { push ebx }
    __asm { push esi }
    __asm { mov eax,dword ptr [esp+14h] }
    __asm { xor eax,dword ptr [esp+18h] }
    __asm { xor eax,dword ptr [esp+1Ch] }
    __asm { xor eax,ecx }
    __asm { pop esi }
    __asm { pop ebx }
    __asm { add esp,8 }
    __asm { ret 0Ch }
}
__declspec(naked) DWORD prepare_trampoline_fixture() {
    __asm { sub esp,84h }
    __asm { mov eax,dword ptr [esp+88h] }
    __asm { xor eax,dword ptr [esp+8Ch] }
    __asm { xor eax,dword ptr [esp+90h] }
    __asm { xor eax,dword ptr [esp+94h] }
    __asm { xor eax,ecx }
    __asm { add esp,84h }
    __asm { ret 10h }
}
namespace {
DWORD fake_error = 0, fake_index = 0, fake_mode = 0, fake_resumes = 0;
bool fake_bad_rollback = false;
HANDLE WINAPI fake_snapshot(DWORD, DWORD) { fake_index = fake_resumes = 0;
    if (fake_mode == 1) { fake_error = 111; return INVALID_HANDLE_VALUE; }
    return reinterpret_cast<HANDLE>(1000); }
BOOL WINAPI fake_first(HANDLE, LPTHREADENTRY32 entry) {
    if (fake_mode == 2) { fake_error = 112; return FALSE; }
    entry->th32OwnerProcessID = 71; entry->th32ThreadID = 2; return TRUE; }
BOOL WINAPI fake_next(HANDLE, LPTHREADENTRY32 entry) {
    if (fake_mode == 5) { fake_error = 113; return FALSE; }
    if (++fake_index == 1) { entry->th32ThreadID = 3; return TRUE; }
    fake_error = ERROR_NO_MORE_FILES; return FALSE; }
DWORD WINAPI fake_pid() { return 71; }
DWORD WINAPI fake_tid() { return 1; }
HANDLE WINAPI fake_open(DWORD, BOOL, DWORD tid) {
    if (fake_mode == 3 && tid == 3) { fake_error = 114; return nullptr; }
    return reinterpret_cast<HANDLE>(static_cast<std::uintptr_t>(100 + tid)); }
DWORD WINAPI fake_suspend(HANDLE thread) {
    if (fake_mode == 4 && thread == reinterpret_cast<HANDLE>(103)) { fake_error = 115; return DWORD(-1); }
    return 0; }
DWORD WINAPI fake_resume(HANDLE) { ++fake_resumes; return fake_bad_rollback ? DWORD(-1) : 1; }
BOOL WINAPI fake_close(HANDLE) { fake_error = 999; return TRUE; }
DWORD WINAPI fake_last_error() { return fake_error; }
void test_thread_transaction() {
    sfc_m1::ThreadSuspendApi api;
    api.snapshot = fake_snapshot; api.first = fake_first; api.next = fake_next;
    api.process_id = fake_pid; api.thread_id = fake_tid; api.open = fake_open;
    api.suspend = fake_suspend; api.resume = fake_resume; api.close = fake_close; api.error = fake_last_error;
    bool ok = false; sfc_m1::ThreadSuspendDiagnostic diagnostic;
    fake_mode = 0;
    auto held = sfc_m1::suspend_thread_transaction(ok, diagnostic, api);
    require_corner(ok && held.size() == 2 && !diagnostic.error, "complete suspend transaction succeeds");
    for (DWORD mode = 1; mode <= 5; ++mode) {
        fake_mode = mode;
        held = sfc_m1::suspend_thread_transaction(ok, diagnostic, api);
        const DWORD expected[] = {0, 111, 112, 114, 115, 113};
        require_corner(!ok && held.empty() && diagnostic.error == expected[mode],
                       "precise error retained across CloseHandle and all failures refuse patching");
        if (mode >= 3) require_corner(fake_resumes == 1, "earlier suspended thread resumed on failure");
    }
    fake_mode = 4; fake_bad_rollback = true;
    held = sfc_m1::suspend_thread_transaction(ok, diagnostic, api);
    require_corner(!ok && diagnostic.error == 115 && diagnostic.rollback_failures == 1 &&
                   diagnostic.thread == 3 && std::strcmp(diagnostic.api, "SuspendThread") == 0,
                   "rollback failure recorded without masking primary API/TID/error");
    fake_bad_rollback = false;
}
} // namespace
int wmain(int argc, wchar_t** argv) {
    test_thread_transaction();
    // Counters remain complete while bounded signature/examples saturate.
    sfc_m1::RejectionDiagnostics diagnostic;
    for(DWORD i=0;i<10000;++i) {
        sfc_m1::RejectionSample s{};s.phase=i%4;s.kind=1+i%3;s.reason=1+i%12;
        s.elapsed=i;s.caller=i;s.thread=0xffffffff;s.ship=0xffffffff;
        diagnostic.record(s);
    }
    require_corner(diagnostic.total==10000 && diagnostic.bucket_count==32 &&
                   diagnostic.signature_overflow==9968 && diagnostic.examples[0].elapsed==0,
                   "fixed32 signatures/first32 last32 examples with complete counters");
    std::uint64_t sum=0;for(const auto& phase:diagnostic.counts)for(const auto& kind:phase)for(auto count:kind)sum+=count;
    require_corner(sum==10000,"all phases/reasons reconcile after detail saturation");
    std::ostringstream diagnostic_json;diagnostic.write(diagnostic_json);
    require_corner(diagnostic_json.str().size()<65536,"worst fixed diagnostic output under64KiB");
    InitializeCriticalSection(&g_lock);g_running=1;g_gate=g_saturated=0;
    std::array<DWORD,9> rejection_saved{};
    std::array<DWORD,5> rejection_stack{ kVisualMainlineReturn,0,0,0,0 };
    rejection_saved[3]=reinterpret_cast<DWORD>(rejection_stack.data())-4;
    RecordHook(kShip,rejection_saved.data());
    require_corner(g_rejection_diagnostics.counts[0][kShip][1]==1 && !g_gate,
                   "production unreadable ship counted before gate without reads after failure");
    g_gate=g_saturated=1;g_gate_tick=GetTickCount64()-31000;
    RecordHook(kModel0,rejection_saved.data());
    require_corner(g_rejection_diagnostics.counts[3][kModel0][8]==1 && g_rejected_semantics==2,
                   "production unreadable Model0 counted after CSV saturation");
    std::array<DWORD,0x88/4+1> rejected_ship{};
    std::array<DWORD,1> rejected_visual{},rejected_model{};
    auto reject = [&](DWORD kind,DWORD reason) {
        const auto before=g_rejection_diagnostics.counts[3][kind][reason];
        RecordHook(kind,rejection_saved.data());
        require_corner(g_rejection_diagnostics.counts[3][kind][reason]==before+1,
                       "production first-failed reason retained without changing acceptance");
    };
    rejection_saved[6]=reinterpret_cast<DWORD>(rejected_ship.data());reject(kShip,2);
    rejected_ship[0]=kShipVtable;reject(kShip,4);
    rejected_ship[0x88/4]=reinterpret_cast<DWORD>(rejected_visual.data());reject(kShip,5);
    SYSTEM_INFO system{};GetSystemInfo(&system);
    auto* pages=static_cast<BYTE*>(VirtualAlloc(nullptr,system.dwPageSize*2,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE));
    require_corner(pages!=nullptr,"guarded unreadable ship-link fixture allocated");
    DWORD old=0;require_corner(VirtualProtect(pages+system.dwPageSize,system.dwPageSize,PAGE_NOACCESS,&old)!=FALSE,
                              "guarded second page configured");
    auto* edge=reinterpret_cast<DWORD*>(pages+system.dwPageSize-4);*edge=kShipVtable;
    rejection_saved[6]=reinterpret_cast<DWORD>(edge);reject(kShip,3);VirtualFree(pages,0,MEM_RELEASE);
    rejected_visual[0]=kVisualVtable;
    rejection_saved[6]=reinterpret_cast<DWORD>(rejected_visual.data());
    rejection_saved[4]=reinterpret_cast<DWORD>(rejected_ship.data());
    rejected_ship[0x88/4]=0;reject(kVisual,6);
    rejection_saved[6]=reinterpret_cast<DWORD>(rejected_model.data());
    rejection_saved[1]=reinterpret_cast<DWORD>(rejected_visual.data());
    rejection_stack[0]=0x12345678;reject(kModel0,7);
    rejection_stack[0]=kVisualMainlineReturn;reject(kModel0,9);
    rejected_model[0]=kModel0Vtable;rejection_saved[1]=0;reject(kModel0,10);
    rejection_saved[1]=reinterpret_cast<DWORD>(rejected_visual.data());rejected_visual[0]=0;reject(kModel0,11);
    rejected_visual[0]=kVisualVtable;reject(kModel0,12);
    const auto before_exception=g_rejected_semantics;
    rejection_stack[0]=kKnownExceptionReturn;RecordHook(kModel0,rejection_saved.data());
    require_corner(g_rejected_semantics==before_exception,"known exception remains excluded from rejection diagnostics");
    g_running=0;g_gate=g_saturated=0;g_rejected_semantics=0;g_rejection_diagnostics={};
    g_exception_509843=0;
    DeleteCriticalSection(&g_lock);
    // Wrapper observation consumes the original three stack args without replacing them.
    InitializeCriticalSection(&g_lock);g_running=g_gate=g_saturated=1;
    std::array<DWORD,0x18/4+1> wrapper_model{};
    std::array<DWORD,1> wrapper_manager{0x007B8D4C};
    wrapper_model[4]=452;wrapper_model[5]=0x1000;wrapper_model[6]=0x2000;
    auto* wrapper_state=thread_state(GetCurrentThreadId());
    wrapper_state->model_scope=true;wrapper_state->owner_id=71;wrapper_state->ship=0x3000;
    wrapper_state->visual=0x4000;wrapper_state->model0=reinterpret_cast<DWORD>(wrapper_model.data());
    wrapper_state->model_manager=reinterpret_cast<DWORD>(wrapper_manager.data());
    std::array<DWORD,5> wrapper_stack{0x0042E55D,452,0x1000,1,0};
    std::array<DWORD,9> wrapper_saved{};
    wrapper_saved[3]=reinterpret_cast<DWORD>(wrapper_stack.data())-4;
    wrapper_saved[6]=wrapper_state->model_manager;
    const auto original_wrapper_model=wrapper_model;
    const auto original_wrapper_saved=wrapper_saved;
    RecordHook(kWrapper,wrapper_saved.data());
    require_corner(g_wrapper_outcomes[1]==1 && wrapper_state->wrapper_pending==1,
                   "primary caller/count/list/manager scoped exactly");
    wrapper_stack[0]=0x0042E626;wrapper_stack[2]=0x2000;RecordHook(kWrapper,wrapper_saved.data());
    require_corner(g_wrapper_outcomes[2]==1,"secondary path distinguished without substitution");
    wrapper_stack[2]=0x9999;RecordHook(kWrapper,wrapper_saved.data());
    require_corner(g_wrapper_outcomes[7]==1,"list mismatch remains observation only");
    wrapper_stack[0]=0x12345678;RecordHook(kWrapper,wrapper_saved.data());
    require_corner(g_wrapper_outcomes[5]==1,"other caller not classified primary");
    wrapper_saved[6]=0;RecordHook(kWrapper,wrapper_saved.data());
    require_corner(g_wrapper_outcomes[4]==1,"manager mismatch isolated");
    wrapper_saved=original_wrapper_saved;
    wrapper_stack[0]=0x0042E55D;wrapper_stack[2]=0x1000;
    for(DWORD i=0;i<10000;++i) RecordHook(kWrapper,wrapper_saved.data());
    require_corner(g_wrapper_total==10005 && g_wrapper_samples.size()==64,
                   "wrapper summaries continue after CSV saturation with64 fixed samples");
    RecordHook(kVisualExit,wrapper_saved.data());
    require_corner(g_wrapper_parent_closed==10002 && !wrapper_state->wrapper_pending,
                   "parent return closes observations, not a nonretention proof");
    RecordHook(kWrapper,wrapper_saved.data());
    require_corner(g_wrapper_outcomes[3]==1,"outside Model0 scope kept separate");
    require_corner(wrapper_model==original_wrapper_model && wrapper_saved==original_wrapper_saved,
                   "observer never edits target header or saved state");
    g_tramp_wrapper=reinterpret_cast<void*>(&wrapper_trampoline_fixture);
    using WrapperFunction=DWORD(__thiscall*)(void*,DWORD,DWORD,DWORD);
    auto wrapper_function=reinterpret_cast<WrapperFunction>(&HookWrapper);
    const DWORD wrapper_result=wrapper_function(wrapper_manager.data(),452,0x1000,1);
    require_corner(wrapper_result==(452u^0x1000u^1u^reinterpret_cast<DWORD>(wrapper_manager.data())),
                   "real wrapper thunk preserves ECX/three stack args, replays prologue and ret0Ch");
    g_tramp_wrapper=nullptr;
    g_config.enable_wrapper_observation=true;
    std::ostringstream wrapper_fixture_json;write_wrapper_observation(wrapper_fixture_json);
    require_corner(wrapper_fixture_json.str().size()<16384,"fixed64 sample serialization under16KiB");
    g_config.enable_wrapper_observation=false;
    g_running=g_gate=g_saturated=0;g_wrapper_outcomes={};g_wrapper_total=g_wrapper_parent_closed=0;
    g_wrapper_samples={};g_threads={};DeleteCriticalSection(&g_lock);
    std::array<DWORD, 0x738 / 4> manager{};
    manager[0] = 0x007B8D4C;
    for (DWORD offset : {0x6B0u, 0x6F4u}) {
        for (DWORD diagonal : {0u, 20u, 40u, 60u}) manager[(offset + diagonal) / 4] = 0x3F800000;
        manager[(offset + 64) / 4] = 0x100; // metadata bytes, not another float
    }
    std::array<DWORD, 8> model{};
    std::array<DWORD, 9> positions{0x3F800000,0,0,0,0x3F800000,0,0,0,0x3F800000};
    std::array<DWORD, 21> corners{}; // 3 x28-byte records
    for (DWORD i = 0; i < 3; ++i) { corners[i * 7] = i; corners[i * 7 + 1 + i] = 0x3F800000; }
    std::array<DWORD, 7> polygon{3,0,0x3F800000,0,0,0, reinterpret_cast<DWORD>(corners.data())};
    std::array<DWORD, 1> list{reinterpret_cast<DWORD>(polygon.data())};
    std::array<BYTE, 36> source{};
    source[0] = 0x23;
    model[0] = kModel0Vtable; model[2] = 3; model[3] = reinterpret_cast<DWORD>(positions.data());
    model[4] = 1; model[5] = reinterpret_cast<DWORD>(list.data());
    const auto original_source = source; const auto original_corners = corners;
    const auto original_manager = manager; const auto original_model = model;
    auto read = [](std::uint32_t address, std::uint32_t& value) {
        if (address == 0x00C69FF0 || address == 0x00C69FF4 || address == 0x00C74058) {
            value = 0; return true;
        }
        return read_tint32(address, value);
    };
    sfc_m1::CornerSnapshot sample{};
    sample.owner = 1; sample.thread = GetCurrentThreadId(); sample.ship = 0x1000; sample.visual = 0x2000;
    sample.model = reinterpret_cast<DWORD>(model.data()); sample.manager = reinterpret_cast<DWORD>(manager.data());
    sample.source = reinterpret_cast<DWORD>(source.data());
    require_corner(sfc_m1::capture_corner_inputs(sample, read, safe_copy), "valid corner layout captured");
    require_corner(sample.corners == 3 && sample.polygons == 1 && !sample.truncated &&
                   sample.corner_data[2].index == 2 && sample.corner_data[2].vector[2] == 0x3F800000,
                   "indices/vectors/positions preserve exact bits");
    corners[0] = 3;
    require_corner(!sfc_m1::capture_corner_inputs(sample, read, safe_copy) && sample.status == 2,
                   "vertex index out of bounds rejected");
    corners = original_corners;
    polygon[1] = 256;
    require_corner(!sfc_m1::capture_corner_inputs(sample, read, safe_copy), "source index refused");
    polygon[1] = 0;
    const DWORD good_model = sample.model; sample.model = 0xFFFFFFFC;
    require_corner(!sfc_m1::capture_corner_inputs(sample, read, safe_copy) && sample.status == 1,
                   "pointer arithmetic overflow is refused");
    sample.model = good_model;
    model[2] = 65537;
    require_corner(!sfc_m1::capture_corner_inputs(sample, read, safe_copy), "unsupported count refused");
    model[2] = 3;
    // Full worst-case capacity with repeated legitimate records, no output flood.
    std::array<DWORD, 65> big_list{}; big_list.fill(reinterpret_cast<DWORD>(polygon.data()));
    std::array<DWORD, 9 * 7> big_corners{};
    for (DWORD i = 0; i < 9; ++i) big_corners[i * 7 + 1] = 0x3F800000;
    polygon[0] = 9; polygon[6] = reinterpret_cast<DWORD>(big_corners.data());
    model[4] = 65; model[5] = reinterpret_cast<DWORD>(big_list.data());
    require_corner(sfc_m1::capture_corner_inputs(sample, read, safe_copy) && sample.truncated &&
                   sample.polygons == 64 && sample.corners == 512, "both sampling ceilings enforced");
    model[4] = 6370;
    require_corner(sfc_m1::capture_corner_inputs(sample, read, safe_copy) && sample.polygons == 64 &&
                   sample.corners == 512, "6370-polygon model accepted without expanding actual reads");
    model[4] = 65537;
    require_corner(!sfc_m1::capture_corner_inputs(sample, read, safe_copy) && sample.status == 2,
                   "read-only advertised count sanity ceiling enforced");
    model[4] = 6370;
    require_corner(sfc_m1::capture_corner_inputs(sample, read, safe_copy), "valid large model restored");
    for (DWORD i = 0; i < 2 * sfc_m1::kCornerWindows; ++i) {
        g_corner_snapshots[i] = sample; g_corner_snapshots[i].owner = i % 2 + 1;
        g_corner_snapshots[i].filter = i % 2;
        g_corner_snapshots[i].ship = 0x1000 + (i % 2) * 0x2000;
        g_corner_snapshots[i].visual = 0x2000 + (i % 2) * 0x2000;
        g_corner_snapshots[i].window = i / 2; g_corner_snapshots[i].elapsed_ms = (i / 2) * 5000;
    }
    g_corner_count = 2 * sfc_m1::kCornerWindows; g_config.enable_corner_snapshot = true;
    for (DWORD i = 0; i < 2; ++i) {
        g_corner_owners[i].ship = 0x1000 + i * 0x2000;
        g_corner_owners[i].visual = 0x2000 + i * 0x2000;
        g_corner_owners[i].owner = i + 1;
        g_corner_owners[i].seen_mask = g_corner_owners[i].success_mask = (1u << 18) - 1;
    }
    if (argc >= 2) {
        g_config.output_dir = argv[1]; CreateDirectoryW(argv[1], nullptr);
        std::ofstream rejection_fixture(narrow(g_config.output_dir+L"\\M1-A-summary.json"));
        rejection_fixture << "{\"rejected_semantics\":10000,\"rejection_diagnostics\":";
        diagnostic.write(rejection_fixture);
        rejection_fixture << ",\"wrapper_observation\":" << wrapper_fixture_json.str() << '}';
        rejection_fixture.close();
        require_corner(write_corner_outputs(), "production JSON writes bounded full packet");
        HANDLE file = CreateFileW((g_config.output_dir + L"\\M1-C01-corners.json").c_str(), GENERIC_READ,
            FILE_SHARE_READ, nullptr, OPEN_EXISTING, 0, nullptr);
        require_corner(file != INVALID_HANDLE_VALUE && GetFileSize(file, nullptr) <= sfc_m1::kCornerPacketBytes,
                       "worst-case packet under hard3MiB cap"); CloseHandle(file);
    }
    // Production recorder budget/retirement rules survive exhausted semantic log.
    g_corner_count = 0; g_corner_owners = {}; g_running = g_gate = g_saturated = 1;
    model = original_model; polygon[0] = 3; polygon[6] = reinterpret_cast<DWORD>(corners.data());
    EventRecord event{};
    event.owner_id = 1; event.thread_id = GetCurrentThreadId(); event.model0 = sample.model;
    event.manager = sample.manager; event.source = sample.source; event.ship = 0x1000; event.visual = 0x2000;
    for (DWORD window = 0; window < sfc_m1::kCornerWindows; ++window) {
        g_gate_tick = GetTickCount64() - window * 5000;
        event.ship = 0x1000; event.visual = 0x2000;
        event.owner_id = window < 4 ? 1 : 3;
        maybe_capture_corner_inputs(event); maybe_capture_corner_inputs(event);
        event.ship = 0x3000; event.visual = 0x4000;
        event.owner_id = window < 4 ? 2 : 4; maybe_capture_corner_inputs(event);
        event.ship = 0x5000; event.visual = 0x6000;
        event.owner_id = 9; maybe_capture_corner_inputs(event);
    }
    require_corner(g_corner_count == 36 && !g_tint_live && !g_tint_applied,
                   "two address filters/18 windows across fresh epochs; no intervention");
    require_corner(g_corner_snapshots[8].owner == 3 && g_corner_snapshots[9].owner == 4 &&
                   g_corner_transition_count == 4 && g_corner_outside_filter == 18,
                   "fresh epoch IDs preserved, transition ledger and outside-filter counts bounded");
    g_gate_tick = GetTickCount64() - 91000; maybe_capture_corner_inputs(event);
    require_corner(g_corner_count == 36, "capture is inert after90s");
    require_corner(sfc_m1::kTintPolygonLimit == 4096, "tint whole-model guard unchanged");
    require_corner(source == original_source && corners == original_corners && manager == original_manager &&
                   model == original_model, "game inputs never mutated");
    std::cout << "All M1 corner snapshot tests passed.\n";
    // Private graph fixtures preserve padding/UV and all original storage.
    std::array<DWORD,7> copy_header{3,0,0x3f800000,0,0,0xabcdef01,0};
    std::array<BYTE,84> copy_corners{};copy_corners.fill(0x5a);
    for(WORD i=0;i<3;++i)std::memcpy(copy_corners.data()+i*28,&i,2);
    copy_header[6]=reinterpret_cast<DWORD>(copy_corners.data());
    std::array<DWORD,65> copy_list{};copy_list.fill(reinterpret_cast<DWORD>(copy_header.data()));
    const auto original_header=copy_header;const auto original_copy_corners=copy_corners;const auto original_list=copy_list;
    sfc_m1::PinnedPolygonCopy graph;
    require_corner(graph.build(reinterpret_cast<DWORD>(copy_list.data()),65,3,safe_copy) && graph.copied==64 &&
                   graph.list[64]==copy_list[64] && graph.payload_hash()==graph.before_hash,
                   "complete pointer list,64 headers/full corners; tail/payload preserved");
    require_corner(!graph.build(reinterpret_cast<DWORD>(copy_list.data()),65,3,safe_copy),"no rearming or graph reuse");
    require_corner(copy_header==original_header && copy_corners==original_copy_corners && copy_list==original_list,
                   "original graph bytes never written");
    sfc_m1::PinnedPolygonCopy too_large;
    require_corner(!too_large.build(reinterpret_cast<DWORD>(copy_list.data()),1025,3,safe_copy),"oversized list bypass");
    sfc_m1::PinnedPolygonCopy unreadable;
    require_corner(!unreadable.build(0xfffffffc,3,3,safe_copy) && !unreadable.published,"overflow never published");
    copy_header[0]=9;sfc_m1::PinnedPolygonCopy too_many;
    require_corner(!too_many.build(reinterpret_cast<DWORD>(copy_list.data()),1,3,safe_copy),"no corner truncation");
    copy_header=original_header;
    sfc_m1::PinnedPolygonCopy bad_index;
    require_corner(!bad_index.build(reinterpret_cast<DWORD>(copy_list.data()),1,2,safe_copy),"vertex-index guard");
    graph.headers[0][0]=255;require_corner(!graph.intact(),"corrupted count detected without out-of-bounds hashing");
    // Production one-use handoff, explicit start gate and downstream consumption.
    InitializeCriticalSection(&g_lock);g_running=g_gate=g_saturated=1;
    g_gate_tick=GetTickCount64()-20000;
    g_frame=1200;
    g_config.enable_private_copy=g_config.enable_wrapper_observation=true;
    g_config.enable_geometry_hook=false;
    const bool failure_fixture=argc>2 && std::wstring(argv[2])==L"--failure";
    const bool epoch_fixture=argc>2 && std::wstring(argv[2])==L"--epochs";
    g_config.enable_copy_epoch_requalification=epoch_fixture;
    g_config.enable_repeated_private_copy=epoch_fixture;
    std::array<DWORD,7> copy_model{};copy_model[0]=kModel0Vtable;copy_model[2]=3;copy_model[4]=1;copy_model[5]=reinterpret_cast<DWORD>(copy_list.data());
    std::array<DWORD,35> copy_ship{};std::array<DWORD,1> copy_visual{kVisualVtable};
    copy_ship[0]=kShipVtable;copy_ship[34]=reinterpret_cast<DWORD>(copy_visual.data());
    g_owners={};DWORD active_epoch=g_owners.observe(reinterpret_cast<DWORD>(copy_ship.data()),
        reinterpret_cast<DWORD>(copy_visual.data()),static_cast<DWORD>(g_frame)).id;
    std::array<DWORD,1> copy_manager{0x007B8D4C};
    auto* cs=thread_state(GetCurrentThreadId());cs->model_scope=true;cs->owner_id=active_epoch;
    cs->ship=reinterpret_cast<DWORD>(copy_ship.data());cs->visual=reinterpret_cast<DWORD>(copy_visual.data());cs->source=0x3000;cs->model0=reinterpret_cast<DWORD>(copy_model.data());
    cs->model_manager=reinterpret_cast<DWORD>(copy_manager.data());cs->copy_depth=2;
    std::array<DWORD,5> copy_stack{0x0042E55D,1,copy_model[5],1,0};std::array<DWORD,9> copy_saved{};
    copy_saved[3]=reinterpret_cast<DWORD>(copy_stack.data())-4;copy_saved[6]=cs->model_manager;
    g_copy_ready_event=CreateEventW(nullptr,TRUE,FALSE,nullptr);
    require_corner(g_copy_ready_event!=nullptr,"explicit gate fixture created");
    RecordHook(kWrapper,copy_saved.data());require_corner(!g_private_copy.attempted,"setup can't apply copy");
    SetEvent(g_copy_ready_event);cs->wrapper_pending=0;
    RecordHook(kWrapper,copy_saved.data());require_corner(!g_private_copy.attempted,"nested scope bypassed");
    cs->copy_depth=1;cs->wrapper_pending=0;
    if(epoch_fixture) {
        copy_model[0]=0;RecordHook(kWrapper,copy_saved.data());
        require_corner(!g_private_copy.attempted,"fresh validation rejects wrong current Model0 vtable");
        copy_model[0]=kModel0Vtable;cs->wrapper_pending=0;
        copy_visual[0]=0;RecordHook(kWrapper,copy_saved.data());
        require_corner(!g_private_copy.attempted,"fresh validation rejects wrong current visual vtable");
        copy_visual[0]=kVisualVtable;cs->wrapper_pending=0;
        cs->owner_id=72;RecordHook(kWrapper,copy_saved.data());
        require_corner(!g_private_copy.attempted,"unqualified ID cannot replace an active selected object");
        cs->owner_id=active_epoch;cs->wrapper_pending=0;
    }
    HMODULE pinned=nullptr;
    g_copy_module_pinned=GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_PIN|GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS,
        reinterpret_cast<LPCWSTR>(&g_private_copy),&pinned)!=FALSE;
    require_corner(g_copy_module_pinned,"Windows pin mechanism succeeds in synthetic process");
    RecordHook(kWrapper,copy_saved.data());
    require_corner(g_copy_applied==1 && copy_stack[2]==reinterpret_cast<DWORD>(g_private_copy.list.data()) &&
                   g_private_copy.published && g_private_copy.intact(),"only stack list redirected to complete pinned copy");
    g_tramp_prepare=reinterpret_cast<void*>(&prepare_trampoline_fixture);
    using PrepareFunction=DWORD(__thiscall*)(void*,DWORD,DWORD,DWORD,DWORD);
    auto prepare_function=reinterpret_cast<PrepareFunction>(&HookPrepare);
    const DWORD prepared=prepare_function(copy_manager.data(),1,1,copy_stack[2],1);
    require_corner(prepared==(1u^1u^copy_stack[2]^1u^reinterpret_cast<DWORD>(copy_manager.data())),
                   "actual preparation thunk preserves four args/ECX and replays subesp84/ret10h");
    g_tramp_prepare=nullptr;
    require_corner(g_copy_consumed==1,"preparation sees the private list under original semantic scope");
    RecordHook(kVisualExit,copy_saved.data());require_corner(g_copy_parent==1 && g_private_copy.intact(),"parent returns; copy retained");
    cs->model_scope=true;cs->copy_depth=1;cs->owner_id=72;cs->wrapper_pending=0;
    copy_stack[2]=copy_model[5];copy_saved[3]=reinterpret_cast<DWORD>(copy_stack.data())-4;
    RecordHook(kWrapper,copy_saved.data());
    require_corner(g_copy_applied==1 && copy_stack[2]==copy_model[5],"fresh epoch doesn't rearm a used slot");
    require_corner(copy_header==original_header && copy_corners==original_copy_corners && copy_list==original_list,
                   "production handoff leaves originals untouched");
    if(argc>1) {
        g_config.output_dir=std::wstring(argv[1])+L"\\private-copy";
        require_corner(M1Stop(nullptr)==0 && g_private_copy.intact() && g_private_copy.published,
                       "actual stop writes evidence/restores hooks without clearing pinned slot");
    }
    // Extend the synthetic first handoff with fresh slots, never reset/reuse it.
    // Production chooses this mode at start; changing config here is fixture-only.
    g_running=1;g_config.enable_repeated_private_copy=true;
    auto reset_copy_scope=[&]() {
        cs->model_scope=true;cs->owner_id=active_epoch;cs->ship=reinterpret_cast<DWORD>(copy_ship.data());
        cs->visual=reinterpret_cast<DWORD>(copy_visual.data());cs->source=0x3000;
        cs->model0=reinterpret_cast<DWORD>(copy_model.data());cs->model_manager=reinterpret_cast<DWORD>(copy_manager.data());
        cs->copy_depth=1;cs->wrapper_pending=0;cs->copy_slot_pending=0;copy_stack[2]=copy_model[5];
        g_owners.observe(cs->ship,cs->visual,static_cast<DWORD>(g_frame));
    };
    reset_copy_scope();g_gate_tick=GetTickCount64()-(g_copy_last_elapsed+999);
    RecordHook(kWrapper,copy_saved.data());
    require_corner(g_copy_attempts==1 && copy_stack[2]==copy_model[5],"subsecond call bypasses original path");
    reset_copy_scope();cs->owner_id=72;g_gate_tick=GetTickCount64()-22000;
    RecordHook(kWrapper,copy_saved.data());
    require_corner(g_copy_attempts==1,"fresh owner epoch never retargets repeated bank");
    reset_copy_scope();cs->source=0x4000;RecordHook(kWrapper,copy_saved.data());
    require_corner(g_copy_attempts==1,"source mismatch bypasses repeated handoff");
    g_tramp_prepare=reinterpret_cast<void*>(&prepare_trampoline_fixture);
    const DWORD first_hash=g_private_copy.before_hash;
    if(failure_fixture) {
        reset_copy_scope();g_gate_tick=GetTickCount64()-22000;copy_header[0]=9;
        RecordHook(kWrapper,copy_saved.data());
        require_corner(g_copy_attempts==2 && g_copy_halted && g_additional_copies[0].failure==2 &&
                       !g_additional_copies[0].data.published && copy_stack[2]==copy_model[5] && g_private_copy.intact(),
                       "malformed fresh copy fails open, preserving earlier pinned data");
        copy_header=original_header;reset_copy_scope();g_gate_tick=GetTickCount64()-23000;
        RecordHook(kWrapper,copy_saved.data());
        require_corner(g_copy_attempts==2 && copy_stack[2]==copy_model[5],"failure never retries or retargets");
    } else {
    for(DWORD i=1;i<32;++i) {
        g_frame=1200+i*60;
        DWORD next_elapsed=g_copy_last_elapsed+1000;
        if(epoch_fixture && (i==8 || i==16)) {
            g_gate_tick=GetTickCount64()-next_elapsed;
            const DWORD retired_owner=active_epoch;
            RecordHook(kScene,copy_saved.data());
            require_corner(!g_owners.find_by_id(retired_owner) && g_copy_retired_ms==next_elapsed,
                           "real scene retirement recorded before fresh epoch");
            active_epoch=g_owners.observe(reinterpret_cast<DWORD>(copy_ship.data()),
                reinterpret_cast<DWORD>(copy_visual.data()),static_cast<DWORD>(g_frame)).id;
            require_corner(active_epoch!=retired_owner,"reobserved raw pointers receive a fresh ID");
            const DWORD retired_ms=g_copy_retired_ms;
            for(DWORD wait: {0u,100u,249u}) {
                ++g_frame;reset_copy_scope();g_gate_tick=GetTickCount64()-(retired_ms+wait);
                RecordHook(kWrapper,copy_saved.data());
                require_corner(g_copy_attempts==i && copy_stack[2]==copy_model[5],
                               "fresh epoch never inherits lease before frame/dwell qualification");
            }
            ++g_frame;next_elapsed=retired_ms+250;
            reset_copy_scope();copy_ship[34]=0;RecordHook(kWrapper,copy_saved.data());
            require_corner(g_copy_attempts==i,"wrong live ship-visual link bypasses candidate");
            copy_ship[34]=reinterpret_cast<DWORD>(copy_visual.data());
        }
        reset_copy_scope();g_gate_tick=GetTickCount64()-next_elapsed;
        copy_header[2]^=1; // Simulate changing original payload; earlier private data stays immutable.
        const auto before_header=copy_header;
        RecordHook(kWrapper,copy_saved.data());
        auto& record=g_additional_copies[i-1];
        require_corner(g_copy_attempts==i+1 && record.data.published && record.data.intact() &&
                       copy_stack[2]==reinterpret_cast<DWORD>(record.data.list.data()) &&
                       copy_header==before_header && g_private_copy.intact() && g_private_copy.before_hash==first_hash,
                       "fresh immutable slot published; original and older copy unchanged");
        if(i==1) {
            const DWORD published_list=copy_stack[2];
            g_gate_tick=GetTickCount64()-(g_copy_last_elapsed+1000);cs->wrapper_pending=0;
            copy_stack[2]=copy_model[5];RecordHook(kWrapper,copy_saved.data());
            require_corner(g_copy_attempts==2 && copy_stack[2]==copy_model[5],"missing prior receipt/return prevents next handoff");
            copy_stack[2]=published_list;
        }
        const DWORD prepared_again=prepare_function(copy_manager.data(),1,1,copy_stack[2],1);
        (void)prepared_again;
        // Fixture trampoline must remain available during the real thunk call.
        RecordHook(kVisualExit,copy_saved.data());
        require_corner(record.consumed==1 && record.parent==1,"every fresh slot received and parent closed");
    }
    reset_copy_scope();g_gate_tick=GetTickCount64()-85000;RecordHook(kWrapper,copy_saved.data());
    require_corner(g_copy_attempts==32 && copy_stack[2]==copy_model[5],"bank exhaustion fails open without reuse");
    for(const auto& item:g_additional_copies)require_corner(item.data.intact(),"all copies retained intact");
    if(epoch_fixture) {
        require_corner(g_copy_requalifications==2 && g_copy_owner!=g_copy_current_owner &&
                       g_additional_copies[7].requalified_from==g_copy_owner &&
                       g_additional_copies[15].requalified_from==g_additional_copies[7].owner,
                       "per-slot provenance survives two independent qualifications without ID merge");
        g_frame+=100;g_gate_tick=GetTickCount64()-88000;RecordHook(kScene,copy_saved.data());
        active_epoch=g_owners.observe(reinterpret_cast<DWORD>(copy_ship.data()),
            reinterpret_cast<DWORD>(copy_visual.data()),static_cast<DWORD>(g_frame)).id;
        reset_copy_scope();EventRecord candidate{};candidate.ecx=cs->model_manager;
        candidate.thread_id=GetCurrentThreadId();candidate.arg1=1;candidate.arg2=copy_model[5];
        require_corner(!admissible_copy_identity(*cs,candidate,88500),"third epoch qualification refused at independent limit");
    }
    }
    g_tramp_prepare=nullptr;
    if(argc>1) {
        g_config.output_dir=std::wstring(argv[1])+L"\\repeated-private-copy";
        require_corner(M1Stop(nullptr)==0 && g_private_copy.intact() &&
                       (failure_fixture || g_additional_copies.back().data.intact()),
                       "stop retains entire used bank while writing bounded summary");
    }
    g_running=0;CloseHandle(g_copy_ready_event);g_copy_ready_event=nullptr;DeleteCriticalSection(&g_lock);
    std::cout << "All M1 one-use and bounded fresh-copy tests passed.\n";
}

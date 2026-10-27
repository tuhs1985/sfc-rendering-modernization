#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <tlhelp32.h>

#include <array>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <string>
#include <vector>

#include "m1_contract.h"
#include "m1_visual_tint.h"
#include "m1_corner_snapshot.h"
#include "m1_thread_suspend.h"
#include "m1_rejection_diagnostics.h"
#include "m1_identity_census.h"
#include "m1_private_copy.h"
#include "m1_surface_graph.h"
#include "m1_mesh_export.h"
#include "m1_texture_references.h"
#include "m1_live_bridge.h"
#include "m1_live_scene.h"
#include "../d3d9_proof/replacement_transaction.h"

namespace {

#ifdef M1_GATE_ONLY
constexpr const char* kSchema = "m1.scene-gate.v1";
constexpr const char* kComponentVersion = "0.1-gate";
#else
constexpr const char* kSchema = "m1.semantic.v1";
constexpr const char* kComponentVersion = "0.20";
#endif
constexpr DWORD kImageBase = 0x00400000;
constexpr DWORD kShipVtable = 0x00796F0C;
constexpr DWORD kVisualVtable = 0x007985A4;
constexpr DWORD kModel0Vtable = 0x007983E8;
constexpr DWORD kVisualMainlineReturn = 0x0042FDD5;
constexpr DWORD kKnownExceptionReturn = 0x00509843;
constexpr std::size_t kEventCapacity = 100000;
constexpr std::size_t kOwnerCapacity = 32;
constexpr std::size_t kThreadCapacity = 8;
replacement::Store* g_replacement=nullptr;

enum EventKind : DWORD {
    kScene = 0,
    kShip = 1,
    kVisual = 2,
    kModel0 = 3,
    kVisualExit = 4,
    kGeometry = 5,
    kRetire = 6,
    kWrapper = 7,
    kPrepare = 8,
    kDestroy = 9,
    kEventKindCount = 10,
};

const char* event_name(DWORD kind) {
    static const char* names[] = {
        "scene_begin", "ship_owner", "visual_model", "model0",
        "visual_exit", "geometry_submit", "owner_retired", "polygon_wrapper", "polygon_prepare", "ship_destroy"
    };
    return kind < kEventKindCount ? names[kind] : "unknown";
}

struct EventRecord {
    DWORD elapsed_ms = 0;
    DWORD sequence = 0;
    DWORD frame = 0;
    DWORD kind = 0;
    DWORD thread_id = 0;
    DWORD origin = 0;
    DWORD return_address = 0;
    DWORD ecx = 0;
    DWORD ebx = 0;
    DWORD esi = 0;
    DWORD arg1 = 0;
    DWORD arg2 = 0;
    DWORD arg3 = 0;
    DWORD arg4 = 0;
    DWORD owner_id = 0;
    DWORD ship = 0;
    DWORD visual = 0;
    DWORD model0 = 0;
    DWORD manager = 0;
    DWORD source = 0;
    DWORD ship_vtable = 0;
    DWORD visual_vtable = 0;
    DWORD model0_vtable = 0;
    DWORD lod_count = 0;
    DWORD lod_override = 0;
    DWORD lod_selected = 0;
    DWORD selected_child = 0;
    DWORD correlated = 0;
    DWORD effective_source = 0;
    DWORD tint_entries = 0;
    DWORD tint_original_rgb = 0;
    DWORD tint_applied = 0;
    DWORD tint_restore = 0;
    DWORD tint_elapsed_ms = 0;
};

struct ThreadState {
    DWORD thread_id = 0;
    DWORD owner_id = 0;
    DWORD ship = 0;
    DWORD visual = 0;
    DWORD model0 = 0;
    DWORD source = 0;
    DWORD geometry_sample_frame = 0xFFFFFFFFu;
    DWORD geometry_samples_in_frame = 0;
    bool model_scope = false;
    DWORD model_manager = 0, wrapper_pending = 0;
    DWORD copy_depth=0;
    DWORD copy_slot_pending=0;
    DWORD surface_pending=0;
    sfc_m1::TintSnapshot tint_snapshot;
    sfc_m1::TintLease tint_lease;
    int shading_sample = -1;
    DWORD shading_lease_phase = 0;
};

struct Hook {
    const char* name;
    DWORD rva;
    const BYTE* expected;
    SIZE_T length;
    void* destination;
    BYTE original[8]{};
    BYTE* trampoline = nullptr;
    bool installed = false;
};

struct Config {
    std::wstring output_dir;
    DWORD max_frames = 120;
    DWORD max_events = 10000;
    DWORD max_owners = 8;
    DWORD warning_bytes = 16u * 1024u * 1024u;
    DWORD hard_bytes = 32u * 1024u * 1024u;
    DWORD geometry_samples_per_owner_frame = 1;
    DWORD uncorrelated_geometry_samples_per_frame = 1;
    bool enable_geometry_hook = true;
    bool enable_visual_tint = false;
    bool enable_shading_off = false;
    bool enable_corner_snapshot = false;
    bool enable_wrapper_observation = false;
    bool enable_private_copy = false;
    bool enable_repeated_private_copy = false;
    bool enable_copy_epoch_requalification = false;
    bool enable_surface_lighting = false;
    bool enable_mesh_export = false;
    bool enable_texture_references = false;
    std::wstring live_channel;
    DWORD tint_delay_ms = 5000;
    DWORD tint_duration_ms = 10000;
};

CRITICAL_SECTION g_lock;
Config g_config;
sfc_m1::MeshPacket g_mesh_packet;
sfc_m1::TextureReferences g_texture_references;
sfc_m1::MeshCaptureBudget g_mesh_budget;
sfc_m1::LiveBridge g_live_bridge;
sfc_m1::LiveScene g_live_scene;
bool g_performance_mode=false;
bool g_live_scene_mode=false;
bool stop_live(){const bool scene=g_live_scene.stop();const bool legacy=g_live_bridge.stop();return scene && legacy;}
std::array<LONGLONG,2> g_mesh_capture_ticks{};
LARGE_INTEGER g_mesh_capture_frequency{};
sfc_m1::OwnerTable<kOwnerCapacity> g_owners;
std::array<EventRecord, kEventCapacity> g_events{};
std::array<ThreadState, kThreadCapacity> g_threads{};
volatile LONG g_running = 0;
volatile LONG g_gate = 0;
volatile LONG g_saturated = 0;
volatile LONG g_in_recorders = 0;
volatile LONG g_event_count = 0;
volatile LONG g_sequence = 0;
volatile LONG g_frame = 0;
volatile LONG g_counts[kEventKindCount]{};
volatile LONG g_correlated_geometry = 0;
volatile LONG g_uncorrelated_geometry = 0;
volatile LONG g_sampled_correlated_geometry = 0;
volatile LONG g_sampled_uncorrelated_geometry = 0;
volatile LONG g_exception_509843 = 0;
volatile LONG g_rejected_semantics = 0;
sfc_m1::RejectionDiagnostics g_rejection_diagnostics;
sfc_m1::IdentityCensus g_identity_census;
struct WrapperSample {
    std::array<DWORD,15> data{};
};
std::array<WrapperSample,64> g_wrapper_samples{};
std::array<ULONGLONG,8> g_wrapper_outcomes{};
ULONGLONG g_wrapper_total = 0, g_wrapper_parent_closed = 0;
sfc_m1::PinnedPolygonCopy g_private_copy;
DWORD g_copy_owner=0,g_copy_thread=0,g_copy_ship=0,g_copy_visual=0,g_copy_model=0;
DWORD g_copy_manager=0,g_copy_original_list=0,g_copy_elapsed=0,g_copy_failure=0;
DWORD g_copy_source=0;
DWORD g_copy_applied=0,g_copy_consumed=0,g_copy_parent=0;
DWORD g_copy_frame=0;
bool g_copy_module_pinned=false;
// Fresh process-lifetime slots, never overwritten or returned to a free list.
struct AdditionalCopy {
    sfc_m1::PinnedPolygonCopy data;
    DWORD elapsed=0, frame=0, consumed=0, parent=0, failure=0;
    DWORD owner=0, requalified_from=0, retired_ms=0, retired_frame=0;
    DWORD qualification_ms=0, qualification_frame=0, qualification_frames=0;
};
std::array<AdditionalCopy,31> g_additional_copies;
static_assert(sizeof(g_private_copy)+sizeof(g_additional_copies)<=700u*1024u,
              "Pinned fresh-copy bank exceeds its fixed budget");
DWORD g_copy_attempts=0,g_copy_last_elapsed=0,g_copy_receipt_mismatch=0;
ULONGLONG g_copy_identity_skips=0;
bool g_copy_halted=false;
DWORD g_copy_current_owner=0,g_copy_requalifications=0;
DWORD g_copy_retired_ms=0,g_copy_retired_frame=0;
struct CopyEpochCandidate {
    DWORD owner=0, first_ms=0, first_frame=0, last_frame=0, frames=0;
    bool observe(DWORD id,DWORD frame,DWORD elapsed) {
        if(owner!=id) {owner=id;first_ms=elapsed;first_frame=last_frame=frame;frames=1;}
        else if(frame>last_frame) {last_frame=frame;++frames;}
        return frames>=3 && elapsed-first_ms>=250;
    }
};
CopyEpochCandidate g_copy_candidate;
struct SurfacePhaseStats {
    DWORD observed=0,applied=0,received=0,parent=0,first_ms=0,last_ms=0;
};
sfc_m1::SurfaceGraphPair g_surface_graphs;
std::array<SurfacePhaseStats,4> g_surface_phases{};
DWORD g_surface_owner=0,g_surface_thread=0,g_surface_ship=0,g_surface_visual=0;
DWORD g_surface_model=0,g_surface_source=0,g_surface_manager=0,g_surface_vertices=0;
DWORD g_surface_count=0,g_surface_list=0,g_surface_failure=0;
ULONGLONG g_surface_tick=0;
bool g_surface_attempted=false;
HANDLE g_surface_lighting_event=nullptr,g_surface_restored_event=nullptr;
volatile LONG g_owner_overflow = 0;
volatile LONG g_thread_overflow = 0;
volatile LONG g_log_truncated = 0;
volatile LONG g_tint_live = 0;
volatile LONG g_tint_applied = 0;
volatile LONG g_tint_restored = 0;
volatile LONG g_tint_renderer_replaced = 0;
volatile LONG g_tint_rejected = 0;
volatile LONG g_tint_restore_failed = 0;
volatile LONG g_tint_thread_mismatch = 0;
DWORD g_tint_target_owner = 0;
DWORD g_tint_target_thread = 0;
struct ShadingPhaseStats {
    ULONGLONG observed = 0;
    ULONGLONG eligible = 0;
    ULONGLONG applied = 0;
    ULONGLONG released = 0;
};
struct ShadingSample {
    DWORD elapsed_ms = 0, phase = 0, owner = 0, ship = 0, visual = 0;
    DWORD model0 = 0, source = 0, effective = 0, flags = 0, effective_flags = 0;
    DWORD lit_entries = 0, manager_mode = 0, applied = 0, restore = 0;
};
std::array<ShadingPhaseStats, 5> g_shading_phases{};
std::array<ShadingSample, 96> g_shading_samples{};
DWORD g_shading_sample_count = 0;
ULONGLONG g_shading_sample_second = ~ULONGLONG(0);
DWORD g_shading_last_phase = 5;
struct CornerOwnerWindow {
    DWORD owner = 0, thread = 0, next_window = 0;
    DWORD ship = 0, visual = 0, seen_mask = 0, success_mask = 0;
    DWORD thread_rejections = 0;
    DWORD visual_mismatches = 0;
    bool retired = false;
    ULONGLONG last_elapsed = 0;
};
std::array<CornerOwnerWindow, 2> g_corner_owners{};
std::array<sfc_m1::CornerSnapshot, 2 * sfc_m1::kCornerWindows> g_corner_snapshots{};
DWORD g_corner_count = 0;
struct CornerTransition {
    DWORD elapsed = 0, reason = 0, filter = 0, from = 0, to = 0, thread = 0;
    DWORD observed_visual = 0;
};
std::array<CornerTransition, 64> g_corner_transitions{};
DWORD g_corner_transition_count = 0, g_corner_transition_dropped = 0;
DWORD g_corner_outside_filter = 0;
sfc_m1::ThreadSuspendDiagnostic g_thread_suspend_diagnostic;
ULONGLONG g_start_tick = 0;
ULONGLONG g_gate_tick = 0;
HANDLE g_burst_event = nullptr;
HANDLE g_tactical_event = nullptr;
HANDLE g_copy_ready_event=nullptr;
HMODULE g_self = nullptr;
DWORD g_uncorrelated_sample_frame = 0xFFFFFFFFu;
DWORD g_uncorrelated_samples_in_frame = 0;

#ifdef M1_WINMM_PROXY
volatile LONG g_proxy_started = 0;
INIT_ONCE g_winmm_once = INIT_ONCE_STATIC_INIT;
HMODULE g_system_winmm = nullptr;
using M1TimeCallback = void (CALLBACK*)(UINT, UINT, DWORD_PTR, DWORD_PTR, DWORD_PTR);
using TimeGetTimeFn = DWORD (WINAPI*)();
using TimeKillEventFn = UINT (WINAPI*)(UINT);
using TimeSetEventFn = UINT (WINAPI*)(UINT, UINT, M1TimeCallback, DWORD_PTR, UINT);
TimeGetTimeFn g_time_get_time = nullptr;
TimeKillEventFn g_time_kill_event = nullptr;
TimeSetEventFn g_time_set_event = nullptr;
#endif

void* g_tramp_scene = nullptr;
void* g_tramp_ship = nullptr;
void* g_tramp_visual = nullptr;
void* g_tramp_model0 = nullptr;
void* g_tramp_visual_exit = nullptr;
void* g_tramp_geometry = nullptr;
void* g_tramp_wrapper = nullptr;
void* g_tramp_prepare = nullptr;
void* g_tramp_destroy = nullptr;
bool g_persistent_requested=false;
const BYTE kDestroyBytes[]={0xb8,0x13,0xbb,0x75,0x00};

const BYTE kSceneBytes[] = {0x53, 0x56, 0x8B, 0xF1, 0x57};
const BYTE kShipBytes[] = {0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x50};
const BYTE kVisualBytes[] = {0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x0C};
const BYTE kModel0Bytes[] = {0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x38};
const BYTE kVisualExitBytes[] = {0x5F, 0x5E, 0xC9, 0xC2, 0x0C, 0x00};
const BYTE kGeometryBytes[] = {0x83, 0xEC, 0x14, 0x53, 0x8B, 0xD9};
const BYTE kWrapperBytes[] = {0x83,0xEC,0x08,0x53,0x56};
const BYTE kPrepareBytes[] = {0x81,0xEC,0x84,0,0,0};

extern "C" void HookScene();
extern "C" void HookShip();
extern "C" void HookVisual();
extern "C" void HookModel0();
extern "C" void HookVisualExit();
extern "C" void HookGeometry();
extern "C" void HookWrapper();
extern "C" void HookPrepare();
extern "C" void HookDestroy();

#ifdef M1_GATE_ONLY
std::array<Hook, 1> g_hooks = {{
    {"ship_owner_gate", 0x000162B9, kShipBytes, sizeof(kShipBytes),
        reinterpret_cast<void*>(&HookShip)},
}};
#else
std::array<Hook, 9> g_hooks = {{
    {"scene_begin", 0x0029E300, kSceneBytes, sizeof(kSceneBytes),
        reinterpret_cast<void*>(&HookScene)},
    {"ship_owner", 0x000162B9, kShipBytes, sizeof(kShipBytes),
        reinterpret_cast<void*>(&HookShip)},
    {"visual_model", 0x0002FD3F, kVisualBytes, sizeof(kVisualBytes),
        reinterpret_cast<void*>(&HookVisual)},
    {"model0", 0x0002E4B2, kModel0Bytes, sizeof(kModel0Bytes),
        reinterpret_cast<void*>(&HookModel0)},
    {"visual_exit", 0x0002FDD5, kVisualExitBytes, sizeof(kVisualExitBytes),
        reinterpret_cast<void*>(&HookVisualExit)},
    {"geometry_submit", 0x002AB410, kGeometryBytes, sizeof(kGeometryBytes),
        reinterpret_cast<void*>(&HookGeometry)},
    {"polygon_wrapper",0x002AC5A0,kWrapperBytes,sizeof(kWrapperBytes),
        reinterpret_cast<void*>(&HookWrapper)},
    {"polygon_prepare",0x002ABFC0,kPrepareBytes,sizeof(kPrepareBytes),
        reinterpret_cast<void*>(&HookPrepare)},
    {"ship_destroy",0x000158C1,kDestroyBytes,sizeof(kDestroyBytes),reinterpret_cast<void*>(&HookDestroy)},
}};
#endif

std::string narrow(const std::wstring& value) {
    if (value.empty()) return {};
    int size = WideCharToMultiByte(CP_UTF8, 0, value.data(),
        static_cast<int>(value.size()), nullptr, 0, nullptr, nullptr);
    std::string result(size, '\0');
    WideCharToMultiByte(CP_UTF8, 0, value.data(), static_cast<int>(value.size()),
        result.data(), size, nullptr, nullptr);
    return result;
}

#ifdef M1_WINMM_PROXY
std::wstring proxy_config_path() {
    std::array<wchar_t, 32768> path{};
    DWORD length = GetModuleFileNameW(g_self, path.data(),
        static_cast<DWORD>(path.size()));
    if (!length || length >= path.size()) return {};
    std::wstring result(path.data(), length);
    const std::size_t separator = result.find_last_of(L"\\/");
    if (separator == std::wstring::npos) return {};
    result.resize(separator + 1);
    result += L"m1-component.ini";
    return result;
}

void write_proxy_status(const std::wstring& output_dir, const char* message) {
    if (output_dir.empty()) return;
    const std::wstring path = output_dir + L"\\proxy-loader.log";
    HANDLE file = CreateFileW(path.c_str(), FILE_APPEND_DATA, FILE_SHARE_READ,
        nullptr, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (file == INVALID_HANDLE_VALUE) return;
    DWORD written = 0;
    WriteFile(file, message, static_cast<DWORD>(std::strlen(message)), &written,
        nullptr);
    WriteFile(file, "\r\n", 2, &written, nullptr);
    CloseHandle(file);
}

DWORD WINAPI launch_proxy_controller(void*) {
    Sleep(250);
    const std::wstring config = proxy_config_path();
    if (config.empty()) return 1;
    std::array<wchar_t, 32768> controller{};
    std::array<wchar_t, 32768> output{};
    GetPrivateProfileStringW(L"m1", L"ControllerPath", L"", controller.data(),
        static_cast<DWORD>(controller.size()), config.c_str());
    GetPrivateProfileStringW(L"m1", L"OutputDirectory", L"", output.data(),
        static_cast<DWORD>(output.size()), config.c_str());
    if (!controller[0] || !output[0]) return 2;
    const DWORD max_seconds = GetPrivateProfileIntW(L"m1", L"MaxSeconds", 300,
        config.c_str());
    const DWORD stop_on_burst = GetPrivateProfileIntW(L"m1", L"StopOnBurst", 1,
        config.c_str());
    std::array<wchar_t, 32768> module_path{};
    if (!GetModuleFileNameW(g_self, module_path.data(),
            static_cast<DWORD>(module_path.size()))) return 3;

    SECURITY_ATTRIBUTES security{};
    security.nLength = sizeof(security);
    security.bInheritHandle = TRUE;
    const std::wstring stdout_path = std::wstring(output.data()) +
        L"\\controller.stdout.txt";
    const std::wstring stderr_path = std::wstring(output.data()) +
        L"\\controller.stderr.txt";
    HANDLE stdout_file = CreateFileW(stdout_path.c_str(), GENERIC_WRITE,
        FILE_SHARE_READ, &security, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
    HANDLE stderr_file = CreateFileW(stderr_path.c_str(), GENERIC_WRITE,
        FILE_SHARE_READ, &security, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (stdout_file == INVALID_HANDLE_VALUE || stderr_file == INVALID_HANDLE_VALUE) {
        if (stdout_file != INVALID_HANDLE_VALUE) CloseHandle(stdout_file);
        if (stderr_file != INVALID_HANDLE_VALUE) CloseHandle(stderr_file);
        return 4;
    }

    std::wostringstream command;
    command << L'"' << controller.data() << L"\" --pid " << GetCurrentProcessId()
            << L" --dll \"" << module_path.data() << L"\" --config \""
            << config << L"\" --max-seconds " << max_seconds
            << L" --stop-on-burst " << stop_on_burst << L" --already-loaded 1";
    std::wstring mutable_command = command.str();
    mutable_command.push_back(L'\0');
    STARTUPINFOW startup{};
    startup.cb = sizeof(startup);
    startup.dwFlags = STARTF_USESTDHANDLES;
    startup.hStdInput = GetStdHandle(STD_INPUT_HANDLE);
    startup.hStdOutput = stdout_file;
    startup.hStdError = stderr_file;
    PROCESS_INFORMATION process{};
    BOOL created = CreateProcessW(controller.data(), mutable_command.data(),
        nullptr, nullptr, TRUE, CREATE_NO_WINDOW, nullptr, nullptr, &startup,
        &process);
    CloseHandle(stdout_file);
    CloseHandle(stderr_file);
    if (!created) {
        write_proxy_status(output.data(), "controller_launch_failed");
        return 5;
    }
    CloseHandle(process.hThread);
    CloseHandle(process.hProcess);
    write_proxy_status(output.data(), "controller_launched_with_inherited_token");
    return 0;
}

void ensure_proxy_controller() {
    if (InterlockedCompareExchange(&g_proxy_started, 1, 0) != 0) return;
    HANDLE thread = CreateThread(nullptr, 0, launch_proxy_controller, nullptr, 0,
        nullptr);
    if (thread) CloseHandle(thread);
    else InterlockedExchange(&g_proxy_started, 0);
}

BOOL CALLBACK load_system_winmm(PINIT_ONCE, PVOID, PVOID*) {
    std::array<wchar_t, MAX_PATH> directory{};
    UINT length = GetSystemDirectoryW(directory.data(),
        static_cast<UINT>(directory.size()));
    if (!length || length >= directory.size()) return FALSE;
    std::wstring path(directory.data(), length);
    path += L"\\winmm.dll";
    g_system_winmm = LoadLibraryW(path.c_str());
    if (!g_system_winmm || g_system_winmm == g_self) return FALSE;
    g_time_get_time = reinterpret_cast<TimeGetTimeFn>(
        GetProcAddress(g_system_winmm, "timeGetTime"));
    g_time_kill_event = reinterpret_cast<TimeKillEventFn>(
        GetProcAddress(g_system_winmm, "timeKillEvent"));
    g_time_set_event = reinterpret_cast<TimeSetEventFn>(
        GetProcAddress(g_system_winmm, "timeSetEvent"));
    return g_time_get_time && g_time_kill_event && g_time_set_event;
}

bool ensure_system_winmm() {
    return InitOnceExecuteOnce(&g_winmm_once, load_system_winmm, nullptr, nullptr)
        && g_time_get_time && g_time_kill_event && g_time_set_event;
}
#endif

std::string hex32(DWORD value) {
    std::ostringstream out;
    out << "0x" << std::uppercase << std::hex << std::setw(8)
        << std::setfill('0') << value;
    return out.str();
}

bool safe_read32(DWORD address, DWORD& value) {
    if (!address) return false;
    __try {
        value = *reinterpret_cast<const DWORD*>(address);
        return true;
    } __except (EXCEPTION_EXECUTE_HANDLER) {
        value = 0;
        return false;
    }
}

bool read_tint32(std::uint32_t address, std::uint32_t& value) {
    DWORD word = 0;
    const bool ok = safe_read32(address, word);
    value = word;
    return ok;
}

bool safe_copy(DWORD address, void* target, DWORD length) {
    __try {
        std::memcpy(target, reinterpret_cast<const void*>(address), length);
        return true;
    } __except (EXCEPTION_EXECUTE_HANDLER) { return false; }
}

bool safe_write32(DWORD address, DWORD value) {
    __try {
        *reinterpret_cast<DWORD*>(address) = value;
        return true;
    } __except (EXCEPTION_EXECUTE_HANDLER) { return false; }
}

DWORD snapshot_entry_esp(const DWORD* saved) {
    return saved[3] + sizeof(DWORD);
}

DWORD safe_stack(const DWORD* saved, DWORD index) {
    DWORD value = 0;
    safe_read32(snapshot_entry_esp(saved) + index * sizeof(DWORD), value);
    return value;
}

void signal_saturation() {
    if (InterlockedCompareExchange(&g_saturated, 1, 0) == 0 && g_burst_event) {
        SetEvent(g_burst_event);
    }
}

ThreadState* thread_state(DWORD thread_id) {
    ThreadState* empty = nullptr;
    for (ThreadState& state : g_threads) {
        if (state.thread_id == thread_id) return &state;
        if (!state.thread_id && !empty) empty = &state;
    }
    if (empty) {
        empty->thread_id = thread_id;
        return empty;
    }
    InterlockedIncrement(&g_thread_overflow);
    return nullptr;
}

bool detail_available() {
    if(g_performance_mode)return false;
    if (!g_gate || g_saturated) return false;
    if (static_cast<DWORD>(g_frame) >= g_config.max_frames ||
        static_cast<DWORD>(g_event_count) >= g_config.max_events) {
        signal_saturation();
        return false;
    }
    return true;
}

void append_event_locked(const EventRecord& input) {
    if (!detail_available()) return;
    LONG index = g_event_count;
    if (index < 0 || static_cast<DWORD>(index) >= g_config.max_events ||
        index >= static_cast<LONG>(kEventCapacity)) {
        signal_saturation();
        return;
    }
    EventRecord event = input;
    event.sequence = static_cast<DWORD>(InterlockedIncrement(&g_sequence));
    event.elapsed_ms = static_cast<DWORD>(GetTickCount64() - g_start_tick);
    event.frame = static_cast<DWORD>(g_frame);
    g_events[static_cast<std::size_t>(index)] = event;
    InterlockedIncrement(&g_event_count);
    if (static_cast<DWORD>(g_event_count) >= g_config.max_events) signal_saturation();
}

DWORD observe_owner(DWORD ship, DWORD visual, bool& first_seen) {
    first_seen = false;
    DWORD existing = g_owners.find_by_ship(ship);
    if (!existing && g_owners.active_count() >= g_config.max_owners) {
        InterlockedIncrement(&g_owner_overflow);
        return 0;
    }
    auto observation = g_owners.observe(ship, visual, static_cast<DWORD>(g_frame));
    if (observation.overflow) {
        InterlockedIncrement(&g_owner_overflow);
        return 0;
    }
    first_seen = observation.first_seen;
    return observation.id;
}

DWORD restore_active_tint(ThreadState* state) {
    if (!state || !state->tint_lease.active) return 0;
    const auto result = sfc_m1::restore_tint_source(
        state->tint_lease, read_tint32, safe_write32);
    if (result == sfc_m1::TintRestore::Failed) {
        InterlockedIncrement(&g_tint_restore_failed);
        signal_saturation();
    } else {
        InterlockedDecrement(&g_tint_live);
        if (result == sfc_m1::TintRestore::Restored)
            InterlockedIncrement(&g_tint_restored);
        else InterlockedIncrement(&g_tint_renderer_replaced);
        if (g_config.enable_shading_off) {
            ++g_shading_phases[state->shading_lease_phase].released;
        }
    }
    if (state->shading_sample >= 0) {
        g_shading_samples[static_cast<std::size_t>(state->shading_sample)].restore =
            static_cast<DWORD>(result);
        state->shading_sample = -1;
    }
    return static_cast<DWORD>(result);
}

void maybe_apply_tint(ThreadState* state, EventRecord& event, const DWORD* saved) {
    if (!g_running || (!g_config.enable_visual_tint && !g_config.enable_shading_off) ||
        !state || !event.owner_id) return;
    if (!g_tint_target_owner) {
        g_tint_target_owner = event.owner_id;
        g_tint_target_thread = event.thread_id;
    }
    if (event.thread_id != g_tint_target_thread) {
        InterlockedIncrement(&g_tint_thread_mismatch);
        return;
    }
    if (event.owner_id != g_tint_target_owner || g_tint_restore_failed ||
        g_tint_thread_mismatch) return;
    const ULONGLONG elapsed = GetTickCount64() - g_gate_tick;
    const DWORD phase = sfc_m1::shading_phase(elapsed);
    const bool shading = g_config.enable_shading_off;
    if (!shading && (!detail_available() || !sfc_m1::tint_window(
            elapsed, g_config.tint_delay_ms, g_config.tint_duration_ms))) return;
    // Shading diagnostic duration is independent of semantic detail saturation.
    // Its evidence is a fixed 96-slot, one-per-second/phase-change sample array.
    bool sample = shading && g_shading_sample_count < g_shading_samples.size() &&
        (elapsed / 1000 != g_shading_sample_second || phase != g_shading_last_phase);
    if (shading) ++g_shading_phases[phase].observed;
    const bool intervention = !shading || phase == 1 || phase == 3;
    if (!intervention && !sample) return;
    const auto modification = !shading || phase == 1 ?
        sfc_m1::SourceModification::Magenta : phase == 3 ?
        sfc_m1::SourceModification::ShadingOff : sfc_m1::SourceModification::Observe;
    DWORD manager_vtable = 0, count = 0, list = 0, manager_mode = 0;
    if (state->tint_lease.active ||
        !safe_read32(event.manager, manager_vtable) || manager_vtable != 0x007B8D4C ||
        (shading && !safe_read32(event.manager + 0x1ECC, manager_mode)) ||
        !safe_read32(event.model0 + 0x10, count) ||
        !safe_read32(event.model0 + 0x14, list) ||
        !sfc_m1::prepare_tint_snapshot(event.source, count, list,
            read_tint32, safe_copy, state->tint_snapshot, modification)) {
        InterlockedIncrement(&g_tint_rejected);
        return;
    }
    const DWORD effective = reinterpret_cast<DWORD>(state->tint_snapshot.bytes.data());
    const ULONGLONG tint_elapsed = GetTickCount64() - g_gate_tick;
    if (!g_running || (shading ? sfc_m1::shading_phase(tint_elapsed) != phase :
        !sfc_m1::tint_window(tint_elapsed,
            g_config.tint_delay_ms, g_config.tint_duration_ms))) return;
    // Preserve the first actually lighting-eligible source, even when the
    // first mesh sampled in this second happened to be already unlit.
    const bool eligible = state->tint_snapshot.lit_entries && manager_mode != 3;
    if (shading && phase == 3 && eligible &&
        !g_shading_phases[phase].eligible && g_shading_sample_count < g_shading_samples.size())
        sample = true;
    int sample_index = -1;
    if (sample) {
        sample_index = static_cast<int>(g_shading_sample_count++);
        auto& entry = g_shading_samples[static_cast<std::size_t>(sample_index)];
        entry.elapsed_ms = static_cast<DWORD>(tint_elapsed);
        entry.phase = phase; entry.owner = event.owner_id; entry.ship = event.ship;
        entry.visual = event.visual; entry.model0 = event.model0; entry.source = event.source;
        entry.flags = state->tint_snapshot.original_flags;
        entry.effective_flags = entry.flags;
        entry.lit_entries = state->tint_snapshot.lit_entries;
        entry.manager_mode = manager_mode;
        g_shading_sample_second = elapsed / 1000;
        g_shading_last_phase = phase;
    }
    if (shading && phase == 3 && eligible)
        ++g_shading_phases[phase].eligible;
    // Already-unlit data is a documented no-op, not a successful intervention.
    if (!intervention || (shading && phase == 3 && !eligible)) return;
    const DWORD source_argument = snapshot_entry_esp(saved) + 2 * sizeof(DWORD);
    if (!safe_write32(source_argument, effective)) {
        InterlockedIncrement(&g_tint_rejected);
        return;
    }
    state->tint_lease = {event.manager, event.source, effective, true};
    state->shading_lease_phase = phase;
    state->shading_sample = sample_index;
    if (shading) ++g_shading_phases[phase].applied;
    if (sample_index >= 0) {
        auto& entry = g_shading_samples[static_cast<std::size_t>(sample_index)];
        entry.applied = 1; entry.effective = effective;
        std::memcpy(&entry.effective_flags, state->tint_snapshot.bytes.data() +
            state->tint_snapshot.sample_index * sfc_m1::kTintSourceStride, 4);
    }
    InterlockedIncrement(&g_tint_live);
    InterlockedIncrement(&g_tint_applied);
    event.effective_source = effective;
    event.tint_entries = state->tint_snapshot.entries;
    event.tint_original_rgb = state->tint_snapshot.original_rgb;
    event.tint_applied = 1;
    event.tint_elapsed_ms = static_cast<DWORD>(tint_elapsed);
}

void corner_transition(DWORD reason, DWORD filter, DWORD from, DWORD to, DWORD thread,
    DWORD observed_visual = 0) {
    if (g_corner_transition_count == g_corner_transitions.size()) {
        ++g_corner_transition_dropped; return;
    }
    g_corner_transitions[g_corner_transition_count++] = {
        static_cast<DWORD>(GetTickCount64() - g_gate_tick), reason, filter, from, to, thread,
        observed_visual ? observed_visual : g_corner_owners[filter].visual};
}

void maybe_capture_corner_inputs(const EventRecord& event) {
    if (!g_config.enable_corner_snapshot || !g_running || !g_gate || !event.owner_id) return;
    const ULONGLONG elapsed = GetTickCount64() - g_gate_tick;
    if (elapsed >= sfc_m1::kCornerWindows * sfc_m1::kCornerWindowMs) return;
    const DWORD window = static_cast<DWORD>(elapsed / sfc_m1::kCornerWindowMs);
    CornerOwnerWindow* target = nullptr;
    DWORD filter = 0;
    for (auto& slot : g_corner_owners) {
        if (slot.ship == event.ship && slot.visual != event.visual) {
            if (!slot.visual_mismatches) corner_transition(5, filter, slot.owner,
                event.owner_id, event.thread_id, event.visual);
            ++slot.visual_mismatches; ++g_corner_outside_filter; return;
        }
        if (slot.ship == event.ship && slot.visual == event.visual) { target = &slot; break; }
        if (!slot.ship) {
            slot.ship = event.ship; slot.visual = event.visual;
            slot.owner = event.owner_id; slot.thread = event.thread_id; target = &slot;
            corner_transition(1, filter, 0, event.owner_id, event.thread_id); break;
        }
        ++filter;
    }
    if (!target) { ++g_corner_outside_filter; return; }
    // Address pair is a read-only interest filter, NOT persistent object identity.
    // Fresh validated epochs retain their literal IDs and get a transition record.
    if (target->owner != event.owner_id) {
        corner_transition(3, filter, target->owner, event.owner_id, event.thread_id);
        target->owner = event.owner_id; target->thread = event.thread_id; target->retired = false;
    }
    if (target->thread != event.thread_id) {
        if (!target->thread_rejections) corner_transition(4, filter, target->owner, target->owner, event.thread_id);
        ++target->thread_rejections; return;
    }
    target->seen_mask |= DWORD(1) << window;
    if (window < target->next_window) return;
    if (g_corner_count >= g_corner_snapshots.size()) return;
    if (target->next_window && elapsed - target->last_elapsed < 1000) return;
    target->last_elapsed = elapsed;
    target->next_window = window + 1; // bounded attempts, including failed snapshots
    auto& snapshot = g_corner_snapshots[g_corner_count++];
    snapshot.elapsed_ms = static_cast<DWORD>(elapsed); snapshot.window = window;
    snapshot.owner = event.owner_id; snapshot.thread = event.thread_id;
    snapshot.filter = filter;
    snapshot.ship = event.ship; snapshot.visual = event.visual; snapshot.model = event.model0;
    snapshot.manager = event.manager; snapshot.source = event.source;
    if (sfc_m1::capture_corner_inputs(snapshot, read_tint32, safe_copy))
        target->success_mask |= DWORD(1) << window;
}

void record_rejection(const EventRecord& e, DWORD reason) {
    InterlockedIncrement(&g_rejected_semantics);
    sfc_m1::RejectionSample sample{};
    sample.phase = !g_gate ? 0 : (GetTickCount64()-g_gate_tick < 15000 ? 1 :
                                 (GetTickCount64()-g_gate_tick < 30000 ? 2 : 3));
    sample.elapsed = static_cast<DWORD>(GetTickCount64()-(g_gate ? g_gate_tick : g_start_tick));
    sample.kind=e.kind; sample.reason=reason; sample.caller=e.return_address;
    sample.thread=e.thread_id; sample.ship=e.ship; sample.visual=e.visual;
    sample.model=e.model0; sample.source=e.source; sample.owner=e.owner_id;
    sample.ship_vtable=e.ship_vtable; sample.visual_vtable=e.visual_vtable;
    sample.model_vtable=e.model0_vtable;
    for(DWORD i=0;i<g_corner_owners.size();++i) {
        const auto& filter=g_corner_owners[i];
        if(filter.ship && e.ship==filter.ship) sample.ship_match |= 1u<<i;
        if(filter.visual && e.visual==filter.visual) sample.visual_match |= 1u<<i;
    }
    g_rejection_diagnostics.record(sample);
}

// Observe existing ownership decisions,never change them. Context is copied
// before the current model callback can overwrite ThreadState with its choice.
struct IdentityContext {DWORD ship=0,visual=0,owner=0;};
void record_identity(const EventRecord& e,const IdentityContext& context,DWORD reason){
    if(g_performance_mode)return;
    if(!g_gate||!g_live_scene_mode||!g_live_scene.cohort.store)return;
    DWORD matches=0;for(const auto& owner:g_owners.slots())if(owner.active&&owner.visual==e.visual&&e.visual)++matches;
    sfc_m1::IdentityCensus::Key key{e.kind,e.return_address,e.ship,e.visual,e.model0,e.source,e.owner_id,
        context.ship,context.visual,context.owner,g_owners.find_by_ship(e.ship),g_owners.find_by_ship(context.ship),
        e.visual?g_owners.find_by_visual(e.visual):0,matches,reason,e.ship_vtable,e.visual_vtable,e.model0_vtable,e.thread_id};
    g_identity_census.record(key,static_cast<DWORD>(g_frame),static_cast<DWORD>(GetTickCount64()-g_gate_tick));
}

// Only validates already-established fields; raw filter equality never merges IDs.
bool validated_copy_owner(const ThreadState& state) {
    const auto* owner=g_owners.find_by_id(state.owner_id);
    DWORD ship_vtable=0,visual_vtable=0,model_vtable=0,linked_visual=0;
    return owner && owner->ship==state.ship && owner->visual==state.visual &&
        safe_read32(state.ship,ship_vtable) && ship_vtable==kShipVtable &&
        safe_read32(state.ship+0x88,linked_visual) && linked_visual==state.visual &&
        safe_read32(state.visual,visual_vtable) && visual_vtable==kVisualVtable &&
        safe_read32(state.model0,model_vtable) && model_vtable==kModel0Vtable;
}

template<class Read>
void observe_mesh_export(ThreadState* state,const EventRecord& event,DWORD outcome,Read read) {
    if(!g_config.enable_mesh_export || !g_gate || outcome!=1 || !state ||
       state->copy_depth!=1 || state->wrapper_pending!=1 || !validated_copy_owner(*state))return;
    sfc_m1::MeshIdentity id;
    id.owner=state->owner_id;id.thread=event.thread_id;id.frame=static_cast<DWORD>(g_frame);
    id.elapsed=static_cast<DWORD>(GetTickCount64()-g_gate_tick);id.ship=state->ship;id.visual=state->visual;
    id.model=state->model0;id.manager=event.ecx;id.source=state->source;id.caller=event.return_address;
    id.list=event.arg2;id.count=event.arg1;
    auto live_valid=[&](){
        return g_running && state->model_scope && state->owner_id==id.owner &&
            state->model0==id.model && state->source==id.source && validated_copy_owner(*state);
    };
    if(!g_config.live_channel.empty()){
        if(g_live_scene_mode)g_live_scene.observe(id,read,live_valid);
        else g_live_bridge.observe(id,read,live_valid);
    }
    if(g_live_scene_mode || !g_mesh_budget.admit(id))return;
    LARGE_INTEGER before{},after{};
    QueryPerformanceFrequency(&g_mesh_capture_frequency);
    const bool timed=QueryPerformanceCounter(&before)!=FALSE;
    g_mesh_budget.status=sfc_m1::capture_mesh(g_mesh_packet,id,read,[&](){
        return g_running && state->model_scope && state->owner_id==id.owner &&
            state->model0==id.model && state->source==id.source && validated_copy_owner(*state);
    });
    if(g_config.enable_texture_references && g_mesh_packet.complete && !g_texture_references.status)
        sfc_m1::capture_texture_references(g_texture_references,g_mesh_packet,read,[&](){
            return g_running && state->model_scope && state->owner_id==id.owner &&
                state->model0==id.model && state->source==id.source && validated_copy_owner(*state);
        });
    if(timed && QueryPerformanceCounter(&after))g_mesh_capture_ticks[g_mesh_budget.attempts-1]=after.QuadPart-before.QuadPart;
}

bool admissible_copy_identity(const ThreadState& state,const EventRecord& event,DWORD elapsed) {
    if(g_config.enable_copy_epoch_requalification && !validated_copy_owner(state))return false;
    if(!g_copy_attempts)return true;
    if(state.ship!=g_copy_ship || state.visual!=g_copy_visual || state.model0!=g_copy_model ||
       state.source!=g_copy_source || event.ecx!=g_copy_manager || event.thread_id!=g_copy_thread ||
       event.arg2!=g_copy_original_list || event.arg1!=g_private_copy.count)return false;
    if(state.owner_id==g_copy_current_owner)return true;
    if(!g_config.enable_copy_epoch_requalification || g_copy_requalifications>=2 ||
       !g_copy_retired_ms || g_owners.find_by_id(g_copy_current_owner))return false;
    return g_copy_candidate.observe(state.owner_id,static_cast<DWORD>(g_frame),elapsed);
}

bool surface_tuple(const ThreadState& state) {
    return state.owner_id==g_surface_owner && GetCurrentThreadId()==g_surface_thread &&
        state.ship==g_surface_ship && state.visual==g_surface_visual &&
        state.model0==g_surface_model && state.source==g_surface_source &&
        state.model_manager==g_surface_manager && validated_copy_owner(state);
}

void begin_surface_model(ThreadState* state,EventRecord& event,const DWORD* saved) {
    if(!g_config.enable_surface_lighting || !state || !g_copy_ready_event ||
       WaitForSingleObject(g_copy_ready_event,0)!=WAIT_OBJECT_0 || g_surface_failure || state->copy_depth!=1)return;
    if(!g_surface_attempted) {
        DWORD count=0,list=0,vertices=0,manager_vtable=0,mode=0;
        if(!safe_read32(event.model0+0x10,count) || !count || count>512)return;
        g_surface_attempted=true;
        if(!validated_copy_owner(*state) || !safe_read32(event.manager,manager_vtable) || manager_vtable!=0x007B8D4C ||
           !safe_read32(event.manager+0x1ECC,mode) || mode==3 || !safe_read32(event.model0+0x14,list) ||
           !safe_read32(event.model0+8,vertices) || !sfc_m1::prepare_tint_snapshot(event.source,count,list,
               read_tint32,safe_copy,state->tint_snapshot,sfc_m1::SourceModification::Observe)) {
            g_surface_failure=1;return;
        }
        bool vertex_lit=false;
        for(DWORD i=0;i<count;++i) {
            DWORD polygon=0,index=0,flags=0;
            if(!safe_read32(list+i*4,polygon) || !safe_read32(polygon+4,index) || index>=256) {g_surface_failure=1;return;}
            std::memcpy(&flags,state->tint_snapshot.bytes.data()+index*36,4);
            vertex_lit|=(flags&2)!=0;
        }
        if(!vertex_lit || !g_surface_graphs.build(list,count,vertices,safe_copy)){g_surface_failure=2;return;}
        g_surface_owner=state->owner_id;g_surface_thread=event.thread_id;
        g_surface_ship=state->ship;g_surface_visual=state->visual;g_surface_model=state->model0;
        g_surface_source=state->source;g_surface_manager=state->model_manager;
        g_surface_count=count;g_surface_list=list;g_surface_vertices=vertices;
    }
    if(state->owner_id!=g_surface_owner)return; // Other ship; never select it.
    DWORD current_count=0,current_list=0,current_vertices=0;
    if(!surface_tuple(*state) || g_tint_restore_failed || state->tint_lease.active ||
       !safe_read32(state->model0+0x10,current_count) || current_count!=g_surface_count ||
       !safe_read32(state->model0+0x14,current_list) || current_list!=g_surface_list ||
       !safe_read32(state->model0+8,current_vertices) || current_vertices!=g_surface_vertices){g_surface_failure=3;return;}
    const DWORD elapsed=g_surface_tick?static_cast<DWORD>(GetTickCount64()-g_surface_tick):0;
    const auto phase=sfc_m1::surface_test_phase(elapsed);
    auto& stats=g_surface_phases[phase];
    if(!stats.observed)stats.first_ms=elapsed;
    stats.last_ms=elapsed;++stats.observed;
    if(phase==2 && g_surface_lighting_event)SetEvent(g_surface_lighting_event);
    if(phase==3 && g_surface_restored_event)SetEvent(g_surface_restored_event);
    if(phase!=0)return;
    if(!sfc_m1::prepare_tint_snapshot(state->source,g_surface_count,g_surface_list,
          read_tint32,safe_copy,state->tint_snapshot,sfc_m1::SourceModification::Magenta)) {g_surface_failure=4;return;}
    const DWORD effective=reinterpret_cast<DWORD>(state->tint_snapshot.bytes.data());
    if(!safe_write32(snapshot_entry_esp(saved)+8,effective)){g_surface_failure=5;return;}
    if(!g_surface_tick)g_surface_tick=GetTickCount64(); // Full20s from actual marker activation.
    state->tint_lease={state->model_manager,state->source,effective,true};
    ++stats.applied;state->surface_pending=1;
    InterlockedIncrement(&g_tint_live);InterlockedIncrement(&g_tint_applied);
    event.effective_source=effective;event.tint_applied=1;
}

void apply_surface_graph(ThreadState* state,const EventRecord& event,const DWORD* saved,DWORD outcome) {
    if(!g_config.enable_surface_lighting || !g_surface_tick || g_surface_failure || outcome!=1 ||
       !state || state->owner_id!=g_surface_owner || state->copy_depth!=1 || state->wrapper_pending!=1)return;
    const auto phase=sfc_m1::surface_test_phase(GetTickCount64()-g_surface_tick);
    if(phase!=1 && phase!=2)return;
    DWORD vertices=0;
    if(!surface_tuple(*state) || event.arg1!=g_surface_count || event.arg2!=g_surface_list ||
       !safe_read32(state->model0+8,vertices) ||
       !g_surface_graphs.neutral.matches_original(event.arg2,event.arg1,vertices,safe_copy) ||
       !g_surface_graphs.intact()){g_surface_failure=6;return;}
    const auto& graph=phase==1?g_surface_graphs.neutral:g_surface_graphs.altered;
    if(!safe_write32(snapshot_entry_esp(saved)+8,reinterpret_cast<DWORD>(graph.list.data()))) {g_surface_failure=7;return;}
    state->surface_pending=phase+1;++g_surface_phases[phase].applied;
}

extern "C" void __cdecl RecordHook(DWORD kind, const DWORD* saved) {
    InterlockedIncrement(&g_in_recorders);
    if (!g_running || kind >= kEventKindCount) {
        // Stop blocks new substitutions but must leave the exit hook able to
        // drain an original Model0 invocation already using our source copy.
        if (kind == kVisualExit && g_tint_live) {
            EnterCriticalSection(&g_lock);
            restore_active_tint(thread_state(GetCurrentThreadId()));
            LeaveCriticalSection(&g_lock);
        }
        InterlockedDecrement(&g_in_recorders);
        return;
    }
    InterlockedIncrement(&g_counts[kind]);

    const DWORD thread_id = GetCurrentThreadId();
    EventRecord event{};
    event.kind = kind;
    event.thread_id = thread_id;
    event.return_address = safe_stack(saved, 0);
    event.ecx = saved[6];
    event.ebx = saved[4];
    event.esi = saved[1];
    event.arg1 = safe_stack(saved, 1);
    event.arg2 = safe_stack(saved, 2);
    event.arg3 = safe_stack(saved, 3);
    event.arg4 = safe_stack(saved, 4);

    EnterCriticalSection(&g_lock);
    ThreadState* state = thread_state(thread_id);
    const IdentityContext identity_context{state?state->ship:0,state?state->visual:0,state?state->owner_id:0};

    if(kind==kDestroy) {
        event.origin=0x004158C1;event.ship=event.ecx;event.owner_id=g_owners.find_by_ship(event.ship);
        if(event.owner_id)record_identity(event,{},0);
        if(g_persistent_requested&&event.owner_id){
            const auto elapsed=static_cast<DWORD>(GetTickCount64()-g_gate_tick);
            g_live_scene.retire(event.owner_id,static_cast<DWORD>(g_frame),elapsed);
            if(auto* m=g_live_scene.calibration){if(sfc_calibration::lock(m)){
                for(auto& row:m->snapshot.owner)if(row[1]==event.owner_id)row[4]=2;
                sfc_calibration::unlock(m);
            }}
            g_owners.destroy_ship(event.ship);append_event_locked(event);
        }
    } else if(kind==kPrepare) {
        if(g_config.enable_surface_lighting && g_surface_graphs.built) {
            const DWORD pointer=event.arg3;
            DWORD phase=0;
            if(pointer==reinterpret_cast<DWORD>(g_surface_graphs.neutral.list.data()))phase=1;
            else if(pointer==reinterpret_cast<DWORD>(g_surface_graphs.altered.list.data()))phase=2;
            if(phase) {
                if(state && surface_tuple(*state) && state->surface_pending==phase+1 &&
                   event.arg2==g_surface_count && event.ecx==g_surface_manager)++g_surface_phases[phase].received;
                else g_surface_failure=8;
            }
        }
        for(DWORD i=0;i<g_copy_attempts;++i) {
            const auto& copy=i?g_additional_copies[i-1].data:g_private_copy;
            const DWORD owner=i?g_additional_copies[i-1].owner:g_copy_owner;
            if(!copy.published || event.arg3!=reinterpret_cast<DWORD>(copy.list.data()))continue;
            if(event.arg2==copy.count && event.ecx==g_copy_manager && thread_id==g_copy_thread &&
               state && state->model_scope && state->owner_id==owner &&
               state->model0==g_copy_model && state->source==g_copy_source && state->copy_depth==1 &&
               state->copy_slot_pending==i+1) {
                if(i)++g_additional_copies[i-1].consumed;else ++g_copy_consumed;
            } else {++g_copy_receipt_mismatch;g_copy_halted=true;}
        }
    } else if (kind == kWrapper) {
        DWORD outcome=0, expected_count=0, expected_list=0, manager_vtable=0;
        if(!state || !state->model_scope || !state->owner_id) outcome=3;
        else if(event.ecx!=state->model_manager || !safe_read32(event.ecx,manager_vtable) ||
                manager_vtable!=0x007B8D4C) outcome=4;
        else if(event.return_address!=0x0042E55D && event.return_address!=0x0042E626) outcome=5;
        else if(!safe_read32(state->model0+0x10,expected_count) ||
                !safe_read32(state->model0+(event.return_address==0x0042E55D?0x14:0x18),expected_list)) outcome=6;
        else if(!expected_count || expected_count>65536 || !expected_list ||
                event.arg1!=expected_count || event.arg2!=expected_list || event.arg3!=1) outcome=7;
        else outcome=event.return_address==0x0042E55D?1:2;
        ++g_wrapper_total;++g_wrapper_outcomes[outcome];
        if(outcome==1 || outcome==2) ++state->wrapper_pending;
        observe_mesh_export(state,event,outcome,safe_copy);
        if(outcome==1&&g_live_scene_mode&&g_live_scene.persistent)
            g_live_scene.updatePersistent(event.ecx,static_cast<DWORD>(g_frame),static_cast<DWORD>(GetTickCount64()-g_gate_tick),safe_copy);
        if(g_replacement&&state){
            replacement::Control c{};
            if(replacement::read(g_replacement->control,c)&&c.owner==state->owner_id&&c.mode==replacement::Active){
                DWORD revision=0;for(const auto& o:g_live_scene.owners)if(o.identity.owner==state->owner_id&&!o.retired)revision=o.revision;
                // Capture above sees original arguments. Validate BOTH lists before
                // suppressing either; no model/source/batch memory is changed.
                DWORD count=0,primary=0,secondary=0;
                const bool qualified=(outcome==1||outcome==2)&&state->copy_depth==1&&validated_copy_owner(*state)&&
                    safe_read32(state->model0+0x10,count)&&safe_read32(state->model0+0x14,primary)&&
                    safe_read32(state->model0+0x18,secondary)&&count&&count<=65536&&primary&&
                    event.arg1==count&&event.arg2==(outcome==1?primary:secondary);
                if(!qualified)replacement::invalidate(*g_replacement,static_cast<DWORD>(g_frame));
                else if(replacement::suppress(*g_replacement,static_cast<DWORD>(g_frame),state->owner_id,revision,
                        state->model0,state->source,thread_id,outcome==1,replacement::now())){
                    if(!safe_write32(snapshot_entry_esp(saved)+4,0))replacement::invalidate(*g_replacement,static_cast<DWORD>(g_frame));
                }
            }
        }
        const auto index=g_wrapper_total<=32?g_wrapper_total-1:32+(g_wrapper_total-33)%32;
        auto& s=g_wrapper_samples[static_cast<std::size_t>(index)];
        s.data={static_cast<DWORD>(g_gate?GetTickCount64()-g_gate_tick:0),
            static_cast<DWORD>(g_gate),outcome,event.thread_id,event.return_address,
            state?state->owner_id:0,state?state->ship:0,state?state->visual:0,
            state?state->model0:0,event.ecx,event.arg1,event.arg2,event.arg3,expected_count,expected_list};
        // RT-007 uses one slot. RT-008 uses fresh immutable slots <=1/second.
        if(g_config.enable_private_copy && !g_config.enable_surface_lighting && outcome==1 && g_gate &&
           g_copy_ready_event && WaitForSingleObject(g_copy_ready_event,0)==WAIT_OBJECT_0 &&
           !g_copy_halted && g_copy_attempts<(g_config.enable_repeated_private_copy?32u:1u) &&
           expected_count<=1024 &&
           state->copy_depth==1 && state->wrapper_pending==1) {
          const DWORD elapsed=static_cast<DWORD>(GetTickCount64()-g_gate_tick);
          const bool same=admissible_copy_identity(*state,event,elapsed);
          if(!same) ++g_copy_identity_skips;
          else if(!g_copy_attempts || elapsed-g_copy_last_elapsed>=1000) {
            const DWORD previous=g_copy_attempts?g_copy_attempts-1:0;
            const bool previous_closed=!g_copy_attempts || (previous?
                (g_additional_copies[previous-1].parent && g_additional_copies[previous-1].consumed):
                (g_copy_parent && g_copy_consumed));
            if(previous_closed) {
            if(!g_copy_attempts) {
            g_copy_owner=state->owner_id;g_copy_thread=thread_id;g_copy_ship=state->ship;
            g_copy_visual=state->visual;g_copy_model=state->model0;g_copy_manager=event.ecx;
            g_copy_source=state->source;
            g_copy_current_owner=state->owner_id;
            g_copy_original_list=event.arg2;g_copy_elapsed=elapsed;g_copy_frame=static_cast<DWORD>(g_frame);
            }
            const DWORD copy_index=g_copy_attempts++;
            auto& copy=copy_index?g_additional_copies[copy_index-1].data:g_private_copy;
            auto& failure=copy_index?g_additional_copies[copy_index-1].failure:g_copy_failure;
            if(copy_index) {
                g_additional_copies[copy_index-1].elapsed=elapsed;
                g_additional_copies[copy_index-1].frame=static_cast<DWORD>(g_frame);
                g_additional_copies[copy_index-1].owner=state->owner_id;
                if(state->owner_id!=g_copy_current_owner) {
                    auto& record=g_additional_copies[copy_index-1];
                    record.requalified_from=g_copy_current_owner;
                    record.retired_ms=g_copy_retired_ms;record.retired_frame=g_copy_retired_frame;
                    record.qualification_ms=g_copy_candidate.first_ms;
                    record.qualification_frame=g_copy_candidate.first_frame;
                    record.qualification_frames=g_copy_candidate.frames;
                }
            }
            g_copy_last_elapsed=elapsed;
            DWORD vertices=0;
            if(!safe_read32(state->model0+8,vertices)) {copy.attempted=true;failure=1;}
            else if(!copy.build(event.arg2,expected_count,vertices,safe_copy)) {
                copy.attempted=true;failure=2;
            } else {
                const DWORD argument=snapshot_entry_esp(saved)+8;
                const DWORD relocated=reinterpret_cast<DWORD>(copy.list.data());
                if(safe_write32(argument,relocated)) {
                    copy.published=true;state->copy_slot_pending=copy_index+1;if(!copy_index)g_copy_applied=1;
                    if(state->owner_id!=g_copy_current_owner) {
                        g_copy_current_owner=state->owner_id;++g_copy_requalifications;
                        g_copy_retired_ms=g_copy_retired_frame=0;g_copy_candidate={};
                    }
                }
                else failure=3;
            }
            if(failure)g_copy_halted=true;
            }
          }
        }
        apply_surface_graph(state,event,saved,outcome);
    } else if (kind == kScene) {
        event.origin = 0x0069E300;
        if (g_gate) {
            DWORD frame = static_cast<DWORD>(InterlockedIncrement(&g_frame));
            if(g_replacement)replacement::begin(*g_replacement,frame,thread_id);
            if(g_live_scene_mode){g_live_scene.directSource.begin(frame);sfc_calibration::begin(g_live_scene.calibration,frame);}
            if (frame > 2) {
                if(g_live_scene.persistent)for(const auto& entry:g_live_scene.registry.entries)
                    if(entry.live)g_owners.retain_simulation_owner(entry.id.owner,frame);
                g_owners.retire_before(frame - 2, [&](const auto& slot) {
                    if(!g_config.live_channel.empty()){
                        const auto elapsed=static_cast<DWORD>(GetTickCount64()-g_gate_tick);
                        if(g_live_scene_mode)g_live_scene.retire(slot.id,frame,elapsed);
                        else g_live_bridge.retire(slot.id,frame,elapsed);
                    }
                    if(g_config.enable_mesh_export && slot.id==g_mesh_budget.target.owner)g_mesh_budget.retired=true;
                    if(g_config.enable_surface_lighting && slot.id==g_surface_owner)g_surface_failure=9;
                    if(g_config.enable_copy_epoch_requalification && slot.id==g_copy_current_owner) {
                        g_copy_retired_ms=static_cast<DWORD>(GetTickCount64()-g_gate_tick);
                        g_copy_retired_frame=frame;g_copy_candidate={};
                    }
                    if (g_config.enable_corner_snapshot) {
                        for (DWORD i = 0; i < g_corner_owners.size(); ++i) {
                            auto& interest = g_corner_owners[i];
                            if (interest.owner == slot.id && !interest.retired) {
                                corner_transition(2, i, slot.id, 0, thread_id);
                                interest.retired = true;
                            }
                        }
                    }
                    EventRecord retired{};
                    retired.kind = kRetire;
                    retired.thread_id = thread_id;
                    retired.origin = 0x0069E300;
                    retired.owner_id = slot.id;
                    retired.ship = static_cast<DWORD>(slot.ship);
                    retired.visual = static_cast<DWORD>(slot.visual);
                    record_identity(retired,{},0);
                    InterlockedIncrement(&g_counts[kRetire]);
                    append_event_locked(retired);
                });
            }
            append_event_locked(event);
            if (frame >= g_config.max_frames) signal_saturation();
        }
    } else if (kind == kShip) {
        event.origin = 0x004162B9;
        event.ship = event.ecx;
        DWORD visual = 0;
        DWORD reason=0;
        if(!safe_read32(event.ship,event.ship_vtable)) reason=1;
        else if(event.ship_vtable!=kShipVtable) reason=2;
        else if(!safe_read32(event.ship+0x88,visual)) reason=3;
        event.visual = visual;
        if(!reason) {
            if(!safe_read32(visual,event.visual_vtable)) reason=4;
            else if(event.visual_vtable!=kVisualVtable) reason=5;
        }
        const bool valid = reason==0;
        if (valid) {
            if (InterlockedCompareExchange(&g_gate, 1, 0) == 0) {
                g_gate_tick = GetTickCount64();
                g_start_tick = g_gate_tick;
                if (g_tactical_event) SetEvent(g_tactical_event);
            }
            bool first_seen = false;
            event.owner_id = observe_owner(event.ship, event.visual, first_seen);
            if (state && event.owner_id) {
                state->owner_id = event.owner_id;
                state->ship = event.ship;
                state->visual = event.visual;
                state->model0 = 0;
                state->source = 0;
                state->model_scope = false;
            }
            append_event_locked(event);
#ifdef M1_GATE_ONLY
            // The gate detector is a one-shot instrument. The controller removes
            // this hook before the disabled baseline telemetry window begins.
            signal_saturation();
#endif
        } else {
            record_rejection(event,reason);
        }
        record_identity(event,{},reason);
    } else if (kind == kVisual) {
        event.origin = 0x0042FD3F;
        event.visual = event.ecx;
        event.ship = event.ebx;
        DWORD ship_visual = 0;
        DWORD reason=0;
        if(!safe_read32(event.ship,event.ship_vtable)) reason=1;
        else if(event.ship_vtable!=kShipVtable) reason=2;
        else if(!safe_read32(event.visual,event.visual_vtable)) reason=4;
        else if(event.visual_vtable!=kVisualVtable) reason=5;
        else if(!safe_read32(event.ship+0x88,ship_visual)) reason=3;
        else if(ship_visual!=event.visual) reason=6;
        const bool valid = reason==0;
        if (valid) {
            safe_read32(event.visual + 0x158, event.source);
            safe_read32(event.visual + 0x11C, event.lod_count);
            safe_read32(event.visual + 0x120, event.lod_override);
            safe_read32(event.visual + 0x124, event.lod_selected);
            if (event.lod_selected < 64) {
                safe_read32(event.visual + 0x160 + event.lod_selected * 4,
                    event.selected_child);
            }
            bool first_seen = false;
            event.owner_id = observe_owner(event.ship, event.visual, first_seen);
            if (state && event.owner_id) {
                state->owner_id = event.owner_id;
                state->ship = event.ship;
                state->visual = event.visual;
                state->model0 = 0;
                state->source = event.source;
                state->model_scope = false;
            }
            append_event_locked(event);
        } else {
            record_rejection(event,reason);
        }
        record_identity(event,identity_context,reason);
    } else if (kind == kModel0) {
        event.origin = 0x0042E4B2;
        event.model0 = event.ecx;
        event.visual = event.esi;
        event.manager = event.arg1;
        event.source = event.arg2;
        const bool model_read=safe_read32(event.model0, event.model0_vtable);
        const bool visual_read=safe_read32(event.visual, event.visual_vtable);
        const bool matching_context=state&&state->visual==event.visual;
        event.owner_id = g_owners.model_owner(event.visual,matching_context?state->ship:0,
                                             matching_context?state->owner_id:0);
        if(const auto* owner=g_owners.find_by_id(event.owner_id)){
            DWORD linked_visual=0;
            event.ship=static_cast<DWORD>(owner->ship);
            if(!safe_read32(event.ship,event.ship_vtable)||event.ship_vtable!=kShipVtable||
               !safe_read32(event.ship+0x88,linked_visual)||linked_visual!=event.visual)event.owner_id=0;
        }
        const bool mainline = event.return_address == kVisualMainlineReturn &&
            event.model0_vtable == kModel0Vtable &&
            event.visual_vtable == kVisualVtable && event.owner_id;
        if(g_replacement&&!mainline){replacement::Control c{};if(replacement::read(g_replacement->control,c)&&c.mode==replacement::Active&&c.owner==event.owner_id)replacement::invalidate(*g_replacement,static_cast<DWORD>(g_frame));}
        if (event.return_address == kKnownExceptionReturn) {
            InterlockedIncrement(&g_exception_509843);
        }
        if (state) {
            if (mainline) {
                if(g_config.enable_private_copy || g_config.enable_mesh_export) ++state->copy_depth;
                state->owner_id = event.owner_id;
                state->visual = event.visual;
                state->model0 = event.model0;
                state->source = event.source;
                state->model_scope = true;
                state->model_manager = event.manager;
                if (auto* slot = g_owners.find_by_id(event.owner_id)) {
                    event.ship = static_cast<DWORD>(slot->ship);
                    state->ship = event.ship;
                }
                begin_surface_model(state,event,saved);
                maybe_apply_tint(state, event, saved);
                maybe_capture_corner_inputs(event);
            } else {
                state->model_scope = false;
                state->model0 = 0;
            }
        }
        const DWORD identity_reason=mainline?0:(event.return_address!=kVisualMainlineReturn ? 7 :
                (!model_read ? 8 : (event.model0_vtable!=kModel0Vtable ? 9 :
                (!visual_read ? 10 : (event.visual_vtable!=kVisualVtable ? 11 : 12)))));
        if (!mainline && event.return_address != kKnownExceptionReturn) {
            record_rejection(event,identity_reason);
        }
        record_identity(event,identity_context,identity_reason);
        append_event_locked(event);
    } else if (kind == kGeometry) {
        event.origin = 0x006AB410;
        event.manager = event.ecx;
        if (state && state->model_scope) {
            event.correlated = 1;
            event.owner_id = state->owner_id;
            event.ship = state->ship;
            event.visual = state->visual;
            event.model0 = state->model0;
            event.source = state->source;
            InterlockedIncrement(&g_correlated_geometry);
            if (sfc_m1::should_sample_geometry(static_cast<DWORD>(g_frame),
                    state->geometry_sample_frame,
                    state->geometry_samples_in_frame,
                    g_config.geometry_samples_per_owner_frame)) {
                InterlockedIncrement(&g_sampled_correlated_geometry);
                append_event_locked(event);
            }
        } else {
            InterlockedIncrement(&g_uncorrelated_geometry);
            if (sfc_m1::should_sample_geometry(static_cast<DWORD>(g_frame),
                    g_uncorrelated_sample_frame,
                    g_uncorrelated_samples_in_frame,
                    g_config.uncorrelated_geometry_samples_per_frame)) {
                InterlockedIncrement(&g_sampled_uncorrelated_geometry);
                append_event_locked(event);
            }
        }
    } else if (kind == kVisualExit) {
        event.origin = 0x0042FDD5;
        if (state) {
            if(state->surface_pending && surface_tuple(*state)) {
                ++g_surface_phases[state->surface_pending-1].parent;
                state->surface_pending=0;
            }
            const DWORD pending_owner=state->copy_slot_pending>1?
                g_additional_copies[state->copy_slot_pending-2].owner:g_copy_owner;
            if(state->copy_slot_pending && state->owner_id==pending_owner && thread_id==g_copy_thread &&
               state->copy_depth==1 && state->model0==g_copy_model && state->source==g_copy_source) {
                if(state->copy_slot_pending==1)g_copy_parent=1;
                else g_additional_copies[state->copy_slot_pending-2].parent=1;
                state->copy_slot_pending=0;
            }
            if(state->copy_depth) --state->copy_depth;
            g_wrapper_parent_closed+=state->wrapper_pending;
            state->wrapper_pending=0;
            if (state->tint_lease.active) {
                event.manager = state->tint_lease.manager;
                event.effective_source = state->tint_lease.effective;
                event.tint_restore = restore_active_tint(state);
            }
            event.owner_id = state->owner_id;
            event.ship = state->ship;
            event.visual = state->visual;
            event.model0 = state->model0;
            event.source = state->source;
            event.correlated = state->model_scope ? 1u : 0u;
            state->owner_id = 0;
            state->ship = 0;
            state->visual = 0;
            state->model0 = 0;
            state->source = 0;
            state->model_scope = false;
        }
        append_event_locked(event);
    }
    LeaveCriticalSection(&g_lock);
    InterlockedDecrement(&g_in_recorders);
}

#define M1_HOOK_BODY(kind_value, trampoline_name) \
    __asm { pushfd } \
    __asm { pushad } \
    __asm { cld } \
    __asm { sub esp, 544 } \
    __asm { mov eax, esp } \
    __asm { add eax, 15 } \
    __asm { and eax, 0FFFFFFF0h } \
    __asm { fxsave [eax] } \
    __asm { lea eax, [esp + 544] } \
    __asm { push eax } \
    __asm { push kind_value } \
    __asm { call RecordHook } \
    __asm { add esp, 8 } \
    __asm { mov eax, esp } \
    __asm { add eax, 15 } \
    __asm { and eax, 0FFFFFFF0h } \
    __asm { fxrstor [eax] } \
    __asm { add esp, 544 } \
    __asm { popad } \
    __asm { popfd } \
    __asm { jmp dword ptr [trampoline_name] }

extern "C" void __declspec(naked) HookScene() {
    M1_HOOK_BODY(0, g_tramp_scene)
}

extern "C" void __declspec(naked) HookShip() {
    M1_HOOK_BODY(1, g_tramp_ship)
}

extern "C" void __declspec(naked) HookVisual() {
    M1_HOOK_BODY(2, g_tramp_visual)
}

extern "C" void __declspec(naked) HookModel0() {
    M1_HOOK_BODY(3, g_tramp_model0)
}

extern "C" void __declspec(naked) HookVisualExit() {
    M1_HOOK_BODY(4, g_tramp_visual_exit)
}

extern "C" void __declspec(naked) HookGeometry() {
    M1_HOOK_BODY(5, g_tramp_geometry)
}
extern "C" void __declspec(naked) HookWrapper() {
    M1_HOOK_BODY(7, g_tramp_wrapper)
}
extern "C" void __declspec(naked) HookPrepare() {
    M1_HOOK_BODY(8, g_tramp_prepare)
}
extern "C" void __declspec(naked) HookDestroy() {M1_HOOK_BODY(9,g_tramp_destroy)}

#undef M1_HOOK_BODY

std::vector<HANDLE> suspend_other_threads(bool& ok) {
    return sfc_m1::suspend_thread_transaction(ok, g_thread_suspend_diagnostic);
}

void write_thread_failure(const char* stage) {
    // One overwritten bounded record per stage, after suspension rollback.
    std::ofstream out(narrow(g_config.output_dir + L"\\M1-thread-transaction-failure.log"),
        std::ios::out | std::ios::trunc);
    out << "stage=" << stage << "\napi=" << g_thread_suspend_diagnostic.api
        << "\nthread_id=" << g_thread_suspend_diagnostic.thread
        << "\nwin32_error=" << g_thread_suspend_diagnostic.error
        << "\nrollback_resume_failures=" << g_thread_suspend_diagnostic.rollback_failures << '\n';
}

void resume_threads(std::vector<HANDLE>& threads) {
    for (HANDLE thread : threads) {
        ResumeThread(thread);
        CloseHandle(thread);
    }
    threads.clear();
}

bool write_code(void* address, const void* data, SIZE_T size) {
    DWORD old_protect = 0;
    if (!VirtualProtect(address, size, PAGE_EXECUTE_READWRITE, &old_protect))
        return false;
    std::memcpy(address, data, size);
    FlushInstructionCache(GetCurrentProcess(), address, size);
    DWORD ignored = 0;
    VirtualProtect(address, size, old_protect, &ignored);
    return true;
}

bool prepare_hook(Hook& hook, DWORD module_base) {
    BYTE* target = reinterpret_cast<BYTE*>(module_base + hook.rva);
    if (std::memcmp(target, hook.expected, hook.length) != 0) return false;
    std::memcpy(hook.original, target, hook.length);
    hook.trampoline = static_cast<BYTE*>(VirtualAlloc(nullptr, hook.length + 5,
        MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE));
    if (!hook.trampoline) return false;
    std::memcpy(hook.trampoline, target, hook.length);
    hook.trampoline[hook.length] = 0xE9;
    const std::intptr_t back = reinterpret_cast<BYTE*>(target + hook.length) -
        (hook.trampoline + hook.length + 5);
    *reinterpret_cast<std::int32_t*>(hook.trampoline + hook.length + 1) =
        static_cast<std::int32_t>(back);
    FlushInstructionCache(GetCurrentProcess(), hook.trampoline, hook.length + 5);
    return true;
}

bool install_hook(Hook& hook, DWORD module_base) {
    BYTE* target = reinterpret_cast<BYTE*>(module_base + hook.rva);
    BYTE patch[8]{};
    std::memset(patch, 0x90, hook.length);
    patch[0] = 0xE9;
    const std::intptr_t relative = static_cast<BYTE*>(hook.destination) -
        (target + 5);
    *reinterpret_cast<std::int32_t*>(patch + 1) =
        static_cast<std::int32_t>(relative);
    if (!write_code(target, patch, hook.length)) return false;
    hook.installed = true;
    return true;
}

bool restore_hooks(DWORD module_base) {
    bool ok = true;
    for (auto it = g_hooks.rbegin(); it != g_hooks.rend(); ++it) {
        if (!it->installed) continue;
        BYTE* target = reinterpret_cast<BYTE*>(module_base + it->rva);
        if (!write_code(target, it->original, it->length)) ok = false;
        else it->installed = false;
    }
    return ok;
}

void assign_trampolines() {
#ifdef M1_GATE_ONLY
    g_tramp_ship = g_hooks[0].trampoline;
#else
    g_tramp_scene = g_hooks[0].trampoline;
    g_tramp_ship = g_hooks[1].trampoline;
    g_tramp_visual = g_hooks[2].trampoline;
    g_tramp_model0 = g_hooks[3].trampoline;
    g_tramp_visual_exit = g_hooks[4].trampoline;
    g_tramp_geometry = g_hooks[5].trampoline;
    g_tramp_wrapper = g_hooks[6].trampoline;
    g_tramp_prepare = g_hooks[7].trampoline;
    g_tramp_destroy = g_hooks[8].trampoline;
#endif
}

bool load_config(const wchar_t* path) {
    g_performance_mode=pipeline_mode::performance();
    if (!path || !*path) return false;
    std::array<wchar_t, 32768> output{};
    GetPrivateProfileStringW(L"m1", L"OutputDirectory", L"", output.data(),
        static_cast<DWORD>(output.size()), path);
    if (!output[0]) return false;
    g_config.output_dir = output.data();
    g_config.max_frames = GetPrivateProfileIntW(L"m1", L"MaxFrames", 120, path);
    g_config.max_events = GetPrivateProfileIntW(L"m1", L"MaxEvents", 10000, path);
    g_config.max_owners = GetPrivateProfileIntW(L"m1", L"MaxOwners", 8, path);
    g_config.warning_bytes = GetPrivateProfileIntW(L"m1", L"WarningBytes",
        16u * 1024u * 1024u, path);
    g_config.hard_bytes = GetPrivateProfileIntW(L"m1", L"HardBytes",
        32u * 1024u * 1024u, path);
    g_config.geometry_samples_per_owner_frame = GetPrivateProfileIntW(
        L"m1", L"GeometrySamplesPerOwnerFrame", 1, path);
    g_config.uncorrelated_geometry_samples_per_frame = GetPrivateProfileIntW(
        L"m1", L"UncorrelatedGeometrySamplesPerFrame", 1, path);
    g_config.enable_geometry_hook = GetPrivateProfileIntW(
        L"m1", L"EnableGeometryHook", 1, path) != 0;
    g_config.enable_visual_tint = GetPrivateProfileIntW(
        L"m1", L"EnableVisualTint", 0, path) != 0;
    g_config.enable_shading_off = GetPrivateProfileIntW(
        L"m1", L"EnableShadingOff", 0, path) != 0;
    g_config.enable_corner_snapshot = GetPrivateProfileIntW(
        L"m1", L"EnableCornerSnapshot", 0, path) != 0;
    g_config.enable_wrapper_observation = GetPrivateProfileIntW(
        L"m1",L"EnableWrapperObservation",0,path)!=0;
    g_config.enable_private_copy=GetPrivateProfileIntW(L"m1",L"EnablePrivateCopy",0,path)!=0;
    g_config.enable_repeated_private_copy=GetPrivateProfileIntW(L"m1",L"EnableRepeatedPrivateCopy",0,path)!=0;
    g_config.enable_copy_epoch_requalification=GetPrivateProfileIntW(L"m1",L"EnableCopyEpochRequalification",0,path)!=0;
    g_config.enable_surface_lighting=GetPrivateProfileIntW(L"m1",L"EnableSurfaceLighting",0,path)!=0;
    g_config.enable_mesh_export=GetPrivateProfileIntW(L"m1",L"EnableMeshExport",0,path)!=0;
    g_config.enable_texture_references=GetPrivateProfileIntW(L"m1",L"EnableTextureReferences",0,path)!=0;
    std::array<wchar_t,128> channel{};
    GetPrivateProfileStringW(L"m1",L"LiveChannel",L"",channel.data(),static_cast<DWORD>(channel.size()),path);
    g_config.live_channel=channel.data();
    g_config.tint_delay_ms = GetPrivateProfileIntW(L"m1", L"TintDelayMs", 5000, path);
    g_config.tint_duration_ms = GetPrivateProfileIntW(L"m1", L"TintDurationMs", 10000, path);
#ifdef M1_GATE_ONLY
    if (g_config.enable_visual_tint || g_config.enable_shading_off || g_config.enable_corner_snapshot || g_config.enable_wrapper_observation || g_config.enable_private_copy || g_config.enable_mesh_export) return false;
#endif
    return g_config.max_frames >= 1 && g_config.max_frames <= 6000 &&
        g_config.max_events >= 1 && g_config.max_events <= kEventCapacity &&
        g_config.max_owners >= 1 && g_config.max_owners <= kOwnerCapacity &&
        g_config.geometry_samples_per_owner_frame <= 8 &&
        g_config.uncorrelated_geometry_samples_per_frame <= 8 &&
        (!g_config.enable_visual_tint || !g_config.enable_geometry_hook) &&
        (!g_config.enable_shading_off ||
            (!g_config.enable_geometry_hook && !g_config.enable_visual_tint)) &&
        (!g_config.enable_corner_snapshot || (!g_config.enable_geometry_hook &&
            !g_config.enable_visual_tint && !g_config.enable_shading_off)) &&
        (!g_config.enable_wrapper_observation || g_config.enable_corner_snapshot || g_config.enable_mesh_export) &&
        (!g_config.enable_texture_references || g_config.enable_mesh_export) &&
        (g_config.live_channel.empty() || (sfc_m1::LiveBridge::name_ok(g_config.live_channel) &&
            g_config.enable_mesh_export && g_config.enable_texture_references)) &&
        (!g_config.enable_mesh_export || (g_config.enable_wrapper_observation && !g_config.enable_geometry_hook &&
            !g_config.enable_corner_snapshot && !g_config.enable_private_copy && !g_config.enable_visual_tint &&
            !g_config.enable_shading_off && !g_config.enable_surface_lighting)) &&
        (!g_config.enable_private_copy || g_config.enable_wrapper_observation) &&
        (!g_config.enable_repeated_private_copy || g_config.enable_private_copy) &&
        (!g_config.enable_copy_epoch_requalification || g_config.enable_repeated_private_copy) &&
        (!g_config.enable_surface_lighting || (g_config.enable_private_copy &&
            !g_config.enable_repeated_private_copy && !g_config.enable_copy_epoch_requalification &&
            !g_config.enable_visual_tint && !g_config.enable_shading_off)) &&
        g_config.tint_delay_ms <= 10000 &&
        g_config.tint_duration_ms >= 1 && g_config.tint_duration_ms <= 10000 &&
        g_config.warning_bytes <= g_config.hard_bytes &&
        g_config.hard_bytes >= 1024 &&
        g_config.hard_bytes <= 32u * 1024u * 1024u;
}

bool write_corner_outputs() {
    if (!g_config.enable_corner_snapshot) return true;
    std::ofstream out(narrow(g_config.output_dir + L"\\M1-C01-corners.json"),
        std::ios::out | std::ios::trunc);
    if (!out) return false;
    out << "{\"schema\":\"m1.c01.corners.v3\",\"captured\":" << g_corner_count << ",\"records\":[\n";
    DWORD written = 0;
    for (DWORD i = 0; i < g_corner_count; ++i) {
        const auto& s = g_corner_snapshots[i];
        std::ostringstream row;
        row << (i ? ",\n" : "") << "{\"elapsed_ms\":" << s.elapsed_ms
            << ",\"window\":" << s.window << ",\"owner\":" << s.owner
            << ",\"filter\":" << s.filter
            << ",\"thread\":" << s.thread << ",\"ship\":" << s.ship
            << ",\"visual\":" << s.visual << ",\"model\":" << s.model
            << ",\"manager\":" << s.manager << ",\"source\":" << s.source
            << ",\"vertex_count\":" << s.vertex_count << ",\"vertex_base\":" << s.vertex_base
            << ",\"polygon_count\":" << s.polygon_count << ",\"status\":" << s.status
            << ",\"sample_truncated\":" << (s.truncated ? "true" : "false");
        auto array = [&](const char* name, const auto& values) {
            row << ",\"" << name << "\":[";
            for (std::size_t j = 0; j < values.size(); ++j) row << (j ? "," : "") << values[j];
            row << ']';
        };
        array("object_transform", s.object_transform);
        array("position_transform", s.position_transform);
        array("dispatch", s.dispatch);
        row << ",\"polygons\":[";
        for (DWORD p = 0; p < s.polygons; ++p) {
            const auto& polygon = s.polygon_data[p];
            row << (p ? "," : "") << '[' << polygon.address << ',' << polygon.source_index
                << ',' << polygon.count << ',' << polygon.source_flags;
            for (const auto value : polygon.vector) row << ',' << value;
            row << ']';
        }
        row << "],\"corners\":[";
        for (DWORD c = 0; c < s.corners; ++c) {
            const auto& corner = s.corner_data[c];
            row << (c ? "," : "") << '[' << corner.polygon << ',' << corner.index;
            for (const auto value : corner.vector) row << ',' << value;
            for (const auto value : corner.position) row << ',' << value;
            row << ']';
        }
        row << "]}";
        const auto encoded = row.str();
        if (static_cast<std::streamoff>(out.tellp()) +
            static_cast<std::streamoff>(encoded.size()) + 8192 > sfc_m1::kCornerPacketBytes) break;
        out << encoded; ++written;
    }
    out << "\n],\"filters\":[";
    for (std::size_t i = 0; i < g_corner_owners.size(); ++i) {
        const auto& f = g_corner_owners[i];
        out << (i ? "," : "") << "[" << f.ship << ',' << f.visual << ',' << f.owner
            << ',' << f.seen_mask << ',' << f.success_mask << ',' << f.thread_rejections
            << ',' << f.visual_mismatches << ']';
    }
    out << "],\"transitions\":[";
    for (DWORD i = 0; i < g_corner_transition_count; ++i) {
        const auto& t = g_corner_transitions[i];
        out << (i ? "," : "") << '[' << t.elapsed << ',' << t.reason << ',' << t.filter
            << ',' << t.from << ',' << t.to << ',' << t.thread << ',' << t.observed_visual << ']';
    }
    out << "],\"transition_dropped\":" << g_corner_transition_dropped
        << ",\"outside_filter_calls\":" << g_corner_outside_filter
        << ",\"written\":" << written << ",\"output_truncated\":"
        << (written != g_corner_count ? "true" : "false") << "}\n";
    return static_cast<bool>(out);
}

void write_wrapper_observation(std::ostream& summary) {
    summary << "{\"schema\":\"m1.wrapper.v1\",\"enabled\":"
            << (g_config.enable_wrapper_observation?"true":"false") << ",\"total\":" << g_wrapper_total
            << ",\"parent_closed\":" << g_wrapper_parent_closed << ",\"outcomes\":[";
    for(std::size_t i=0;i<g_wrapper_outcomes.size();++i) summary << (i?",":"") << g_wrapper_outcomes[i];
    summary << "],\"example_omitted\":" << (g_wrapper_total>64?g_wrapper_total-64:0) << ",\"samples\":[";
    const DWORD n=g_wrapper_total<64?static_cast<DWORD>(g_wrapper_total):64;
    for(DWORD i=0;i<n;++i) {
        summary << (i?",[":"[");
        for(std::size_t j=0;j<15;++j) summary << (j?",":"") << g_wrapper_samples[i].data[j];
        summary << ']';
    }
    summary << "]}";
}

bool write_outputs(bool hooks_restored) {
    CreateDirectoryW(g_config.output_dir.c_str(), nullptr);
    const std::wstring csv_path = g_config.output_dir + L"\\M1-A-events.csv";
    const std::wstring summary_path = g_config.output_dir + L"\\M1-A-summary.json";
    const std::wstring component_path = g_config.output_dir + L"\\M1-A-component.log";
    std::ofstream csv(narrow(csv_path), std::ios::out | std::ios::trunc);
    if (!csv) return false;
    csv << "schema,component_version,elapsed_ms,sequence,frame,event,thread,origin,"
           "return_address,ecx,ebx,esi,arg1,arg2,arg3,arg4,owner_id,ship,visual,"
           "model0,manager,source,ship_vtable,visual_vtable,model0_vtable,"
           "lod_count,lod_override,lod_selected,selected_child,correlated,"
           "effective_source,tint_entries,tint_original_rgb,tint_applied,tint_restore,tint_elapsed_ms\n";
    const LONG count = (g_event_count < 0) ? 0 :
        ((g_event_count > static_cast<LONG>(kEventCapacity)) ?
            static_cast<LONG>(kEventCapacity) : g_event_count);
    for (LONG i = 0; i < count; ++i) {
        const EventRecord& e = g_events[static_cast<std::size_t>(i)];
        std::ostringstream row;
        row << kSchema << ',' << kComponentVersion << ',' << e.elapsed_ms << ','
            << e.sequence << ',' << e.frame << ',' << event_name(e.kind) << ','
            << e.thread_id << ',' << hex32(e.origin) << ','
            << hex32(e.return_address) << ',' << hex32(e.ecx) << ','
            << hex32(e.ebx) << ',' << hex32(e.esi) << ',' << hex32(e.arg1) << ','
            << hex32(e.arg2) << ',' << hex32(e.arg3) << ',' << hex32(e.arg4) << ','
            << e.owner_id << ',' << hex32(e.ship) << ',' << hex32(e.visual) << ','
            << hex32(e.model0) << ',' << hex32(e.manager) << ','
            << hex32(e.source) << ',' << hex32(e.ship_vtable) << ','
            << hex32(e.visual_vtable) << ',' << hex32(e.model0_vtable) << ','
            << e.lod_count << ',' << static_cast<LONG>(e.lod_override) << ','
            << e.lod_selected << ',' << hex32(e.selected_child) << ','
            << e.correlated << ',' << hex32(e.effective_source) << ','
            << e.tint_entries << ',' << hex32(e.tint_original_rgb) << ','
            << e.tint_applied << ',' << e.tint_restore << ',' << e.tint_elapsed_ms << '\n';
        const std::string encoded = row.str();
        if (csv.tellp() + static_cast<std::streamoff>(encoded.size()) >
                static_cast<std::streamoff>(g_config.hard_bytes)) {
            InterlockedExchange(&g_log_truncated, 1);
            break;
        }
        csv << encoded;
    }
    csv.flush();
    const auto csv_size = csv.tellp();
    csv.close();

    std::ofstream summary(narrow(summary_path), std::ios::out | std::ios::trunc);
    if (!summary) return false;
    summary << "{\n"
            << "  \"schema\": \"" << kSchema << "\",\n"
            << "  \"component_version\": \"" << kComponentVersion << "\",\n"
            << "  \"hooks_restored\": " << (hooks_restored ? "true" : "false") << ",\n"
            << "  \"gate_activated\": " << (g_gate ? "true" : "false") << ",\n"
            << "  \"gate_tick_ms\": " << g_gate_tick << ",\n"
            << "  \"detailed_saturated\": " << (g_saturated ? "true" : "false") << ",\n"
            << "  \"detailed_events\": " << count << ",\n"
            << "  \"frames_observed\": " << g_frame << ",\n"
            << "  \"event_log_bytes\": " << static_cast<long long>(csv_size) << ",\n"
            << "  \"log_truncated\": " << (g_log_truncated ? "true" : "false") << ",\n"
            << "  \"warning_threshold_exceeded\": "
            << (csv_size >= static_cast<std::streamoff>(g_config.warning_bytes) ? "true" : "false") << ",\n"
            << "  \"counts\": {\n";
    for (DWORD kind = 0; kind < kEventKindCount; ++kind) {
        summary << "    \"" << event_name(kind) << "\": " << g_counts[kind]
                << (kind + 1 == kEventKindCount ? "\n" : ",\n");
    }
    summary << "  },\n"
            << "  \"correlated_geometry\": " << g_correlated_geometry << ",\n"
            << "  \"uncorrelated_geometry\": " << g_uncorrelated_geometry << ",\n"
            << "  \"sampled_correlated_geometry\": " << g_sampled_correlated_geometry << ",\n"
            << "  \"sampled_uncorrelated_geometry\": " << g_sampled_uncorrelated_geometry << ",\n"
            << "  \"geometry_hook_enabled\": "
            << (g_config.enable_geometry_hook ? "true" : "false") << ",\n"
            << "  \"visual_tint\": {\n"
            << "    \"enabled\": " << (g_config.enable_visual_tint ? "true" : "false") << ",\n"
            << "    \"target_owner_id\": " << g_tint_target_owner << ",\n"
            << "    \"target_thread_id\": " << g_tint_target_thread << ",\n"
            << "    \"thread_mismatch\": " << g_tint_thread_mismatch << ",\n"
            << "    \"delay_ms\": " << g_config.tint_delay_ms << ",\n"
            << "    \"duration_ms\": " << g_config.tint_duration_ms << ",\n"
            << "    \"applied\": " << g_tint_applied << ",\n"
            << "    \"restored\": " << g_tint_restored << ",\n"
            << "    \"renderer_replaced\": " << g_tint_renderer_replaced << ",\n"
            << "    \"rejected\": " << g_tint_rejected << ",\n"
            << "    \"restore_failed\": " << g_tint_restore_failed << ",\n"
            << "    \"active_scopes\": " << g_tint_live << "\n  },\n"
            << "  \"shading_off\": {\n"
            << "    \"enabled\": " << (g_config.enable_shading_off ? "true" : "false") << ",\n"
            << "    \"sample_capacity\": 96,\n"
            << "    \"phases\": [\n";
    for (std::size_t i = 0; i < g_shading_phases.size(); ++i) {
        const auto& phase = g_shading_phases[i];
        summary << "      {\"phase\":" << i << ",\"observed\":" << phase.observed
            << ",\"eligible\":" << phase.eligible << ",\"applied\":" << phase.applied
            << ",\"released\":" << phase.released << "}"
            << (i + 1 == g_shading_phases.size() ? "\n" : ",\n");
    }
    summary << "    ],\n    \"samples\": [\n";
    for (DWORD i = 0; i < g_shading_sample_count; ++i) {
        const auto& sample = g_shading_samples[i];
        summary << "      {\"elapsed_ms\":" << sample.elapsed_ms
            << ",\"phase\":" << sample.phase << ",\"owner\":" << sample.owner
            << ",\"ship\":\"" << hex32(sample.ship) << "\",\"visual\":\""
            << hex32(sample.visual) << "\",\"model0\":\"" << hex32(sample.model0)
            << "\",\"source\":\"" << hex32(sample.source) << "\",\"effective\":\""
            << hex32(sample.effective) << "\",\"flags\":" << sample.flags
            << ",\"effective_flags\":" << sample.effective_flags
            << ",\"lit_entries\":" << sample.lit_entries
            << ",\"manager_mode\":" << sample.manager_mode
            << ",\"applied\":" << sample.applied << ",\"restore\":" << sample.restore << "}"
            << (i + 1 == g_shading_sample_count ? "\n" : ",\n");
    }
    summary << "    ]\n  },\n"
            << "  \"known_exception_00509843\": " << g_exception_509843 << ",\n"
            << "  \"rejected_semantics\": " << g_rejected_semantics << ",\n"
            << "  \"rejection_diagnostics\": ";
    std::ostringstream rejection_section;
    g_rejection_diagnostics.write(rejection_section);
    const auto rejection_json=rejection_section.str();
    if(rejection_json.size()<=65536) summary << rejection_json;
    else summary << "{\"schema\":\"m1.rejections.v1\",\"output_truncated\":true}";
    summary << ",\n  \"identity_census\":";
    g_identity_census.write(summary);
    summary << ",\n  \"wrapper_observation\":";
    write_wrapper_observation(summary);
    summary << ",\n  \"private_copy\":{\"enabled\":" << (g_config.enable_private_copy?"true":"false")
        << ",\"attempted\":" << (g_private_copy.attempted?"true":"false")
        << ",\"applied\":" << g_copy_applied << ",\"consumed\":" << g_copy_consumed
        << ",\"parent_return\":" << g_copy_parent << ",\"failure\":" << g_copy_failure
        << ",\"owner\":" << g_copy_owner << ",\"thread\":" << g_copy_thread
        << ",\"ship\":" << g_copy_ship << ",\"visual\":" << g_copy_visual << ",\"model\":" << g_copy_model
        << ",\"manager\":" << g_copy_manager << ",\"original_list\":" << g_copy_original_list
        << ",\"source\":" << g_copy_source
        << ",\"copy_list\":" << reinterpret_cast<DWORD>(g_private_copy.list.data())
        << ",\"elapsed_ms\":" << g_copy_elapsed << ",\"count\":" << g_private_copy.count
        << ",\"copied_polygons\":" << g_private_copy.copied << ",\"payload_bytes\":" << g_private_copy.payload_bytes
        << ",\"slot_bytes\":" << sizeof(g_private_copy) << ",\"before_hash\":" << g_private_copy.before_hash
        << ",\"after_hash\":" << (g_private_copy.built?g_private_copy.payload_hash():0)
        << ",\"intact\":" << (g_private_copy.intact()?"true":"false")
        << ",\"pinned_until_exit\":" << (g_copy_module_pinned?"true":"false") << '}';
    summary << ",\n  \"repeated_private_copy\":{\"enabled\":"
        << (g_config.enable_repeated_private_copy?"true":"false")
        << ",\"limit\":32,\"interval_ms\":1000,\"attempts\":" << g_copy_attempts
        << ",\"storage_bytes\":" << sizeof(g_private_copy)+sizeof(g_additional_copies)
        << ",\"halted\":" << (g_copy_halted?"true":"false")
        << ",\"identity_skips\":" << g_copy_identity_skips
        << ",\"receipt_mismatch\":" << g_copy_receipt_mismatch << ",\"records\":[";
    for(DWORD i=0;i<g_copy_attempts;++i) {
        const auto& copy=i?g_additional_copies[i-1].data:g_private_copy;
        if(i)summary << ',';
        summary << "{\"slot\":" << i << ",\"elapsed_ms\":" << (i?g_additional_copies[i-1].elapsed:g_copy_elapsed)
            << ",\"frame\":" << (i?g_additional_copies[i-1].frame:g_copy_frame)
            << ",\"owner\":" << (i?g_additional_copies[i-1].owner:g_copy_owner)
            << ",\"requalified_from\":" << (i?g_additional_copies[i-1].requalified_from:0)
            << ",\"retired_ms\":" << (i?g_additional_copies[i-1].retired_ms:0)
            << ",\"retired_frame\":" << (i?g_additional_copies[i-1].retired_frame:0)
            << ",\"qualification_ms\":" << (i?g_additional_copies[i-1].qualification_ms:0)
            << ",\"qualification_frame\":" << (i?g_additional_copies[i-1].qualification_frame:0)
            << ",\"qualification_frames\":" << (i?g_additional_copies[i-1].qualification_frames:0)
            << ",\"applied\":" << (copy.published?1:0)
            << ",\"consumed\":" << (i?g_additional_copies[i-1].consumed:g_copy_consumed)
            << ",\"parent_return\":" << (i?g_additional_copies[i-1].parent:g_copy_parent)
            << ",\"failure\":" << (i?g_additional_copies[i-1].failure:g_copy_failure)
            << ",\"copy_list\":" << reinterpret_cast<DWORD>(copy.list.data())
            << ",\"count\":" << copy.count << ",\"copied_polygons\":" << copy.copied
            << ",\"payload_bytes\":" << copy.payload_bytes << ",\"before_hash\":" << copy.before_hash
            << ",\"after_hash\":" << (copy.built?copy.payload_hash():0)
            << ",\"intact\":" << (copy.intact()?"true":"false") << '}';
    }
    summary << "],\"epoch_requalification_enabled\":" << (g_config.enable_copy_epoch_requalification?"true":"false")
        << ",\"epoch_requalifications\":" << g_copy_requalifications << ",\"epoch_limit\":2}";
    summary << ",\n  \"surface_lighting\":{\"enabled\":" << (g_config.enable_surface_lighting?"true":"false")
        << ",\"attempted\":" << (g_surface_attempted?"true":"false")
        << ",\"started\":" << (g_surface_tick?"true":"false") << ",\"failure\":" << g_surface_failure
        << ",\"owner\":" << g_surface_owner << ",\"thread\":" << g_surface_thread
        << ",\"ship\":" << g_surface_ship << ",\"visual\":" << g_surface_visual << ",\"model\":" << g_surface_model
        << ",\"source\":" << g_surface_source << ",\"manager\":" << g_surface_manager
        << ",\"original_list\":" << g_surface_list << ",\"count\":" << g_surface_count
        << ",\"neutral_list\":" << reinterpret_cast<DWORD>(g_surface_graphs.neutral.list.data())
        << ",\"altered_list\":" << reinterpret_cast<DWORD>(g_surface_graphs.altered.list.data())
        << ",\"storage_bytes\":" << sizeof(g_surface_graphs)
        << ",\"changed_vectors\":" << g_surface_graphs.changed_vectors
        << ",\"intact\":" << (g_surface_graphs.intact()?"true":"false")
        << ",\"pinned_until_exit\":" << (g_copy_module_pinned?"true":"false")
        << ",\"marker_ms\":20000,\"normal_gap_ms\":5000,\"altered_ms\":15000,\"phases\":[";
    for(DWORD i=0;i<4;++i) {
        if(i)summary << ',';const auto& phase=g_surface_phases[i];
        summary << "{\"phase\":" << i << ",\"observed\":" << phase.observed << ",\"applied\":" << phase.applied
            << ",\"received\":" << phase.received << ",\"parent\":" << phase.parent
            << ",\"first_ms\":" << phase.first_ms << ",\"last_ms\":" << phase.last_ms << '}';
    }
    summary << "]}";
    summary << ",\n"
            << "  \"owner_overflow\": " << g_owner_overflow << ",\n"
            << "  \"thread_overflow\": " << g_thread_overflow << ",\n"
            << "  \"limits\": {\n"
            << "    \"max_frames\": " << g_config.max_frames << ",\n"
            << "    \"max_events\": " << g_config.max_events << ",\n"
            << "    \"max_owners\": " << g_config.max_owners << ",\n"
            << "    \"warning_bytes\": " << g_config.warning_bytes << ",\n"
            << "    \"hard_bytes\": " << g_config.hard_bytes << ",\n"
            << "    \"geometry_samples_per_owner_frame\": "
            << g_config.geometry_samples_per_owner_frame << ",\n"
            << "    \"uncorrelated_geometry_samples_per_frame\": "
            << g_config.uncorrelated_geometry_samples_per_frame << "\n"
            << "  }\n"
            << "}\n";
    summary.close();

    std::ofstream component(narrow(component_path), std::ios::out | std::ios::trunc);
    if (!component) return false;
    component << "schema=" << kSchema << "\n"
              << "component_version=" << kComponentVersion << "\n"
              << "image_base=" << hex32(reinterpret_cast<DWORD>(
                    GetModuleHandleW(nullptr))) << "\n"
              << "hooks_restored=" << (hooks_restored ? "true" : "false") << "\n";
    for (const Hook& hook : g_hooks) {
        component << "hook=" << hook.name << ",target="
                  << hex32(kImageBase + hook.rva) << ",restored="
                  << (!hook.installed ? "true" : "false") << "\n";
    }
    bool mesh_wrote=true;
    if(g_config.enable_mesh_export && !g_live_scene_mode) {
        // Stop has drained recorders and restored hooks. No I/O on the render thread.
        if(g_mesh_packet.complete) {
            std::ofstream mesh(narrow(g_config.output_dir+L"\\MESH-EXPORT-001.bin"),std::ios::binary|std::ios::trunc);
            mesh_wrote=g_mesh_packet.write(mesh);mesh.flush();mesh_wrote=mesh_wrote && mesh.good();
        }
        std::ofstream receipt(narrow(g_config.output_dir+L"\\MESH-EXPORT-001-receipt.json"));
        receipt << "{\"schema\":\"sfc.mesh.receipt.v1\",\"component_version\":\"" << kComponentVersion
            << "\",\"attempts\":" << g_mesh_budget.attempts << ",\"status\":" << static_cast<DWORD>(g_mesh_budget.status)
            << ",\"complete\":" << (g_mesh_packet.complete?"true":"false")
            << ",\"owner_retired_after_selection\":" << (g_mesh_budget.retired?"true":"false")
            << ",\"hooks_restored\":" << (hooks_restored?"true":"false")
            << ",\"file_write_ok\":" << (mesh_wrote?"true":"false")
            << ",\"owner_epoch\":" << g_mesh_budget.target.owner
            << ",\"packet_bytes\":" << g_mesh_packet.header[sfc_m1::MeshBytes]
            << ",\"packet_fnv1a\":" << g_mesh_packet.header[sfc_m1::MeshHash]
            << ",\"capture_qpc_frequency\":" << g_mesh_capture_frequency.QuadPart
            << ",\"capture_qpc_ticks\":[" << g_mesh_capture_ticks[0] << ',' << g_mesh_capture_ticks[1] << "]}";
        receipt.flush();mesh_wrote=mesh_wrote && receipt.good();
        if(g_config.enable_texture_references){
            std::ofstream refs(narrow(g_config.output_dir+L"\\TEXTURE-EXPORT-001.json"));
            mesh_wrote=sfc_m1::write_texture_references(refs,g_texture_references,g_mesh_packet,hooks_restored) && mesh_wrote;
            refs.flush();mesh_wrote=mesh_wrote && refs.good();
        }
    }
    return write_corner_outputs() && mesh_wrote;
}

}  // namespace

#ifdef M1_WINMM_PROXY
extern "C" DWORD WINAPI timeGetTime() {
    ensure_proxy_controller();
    return ensure_system_winmm() ? g_time_get_time() : GetTickCount();
}

extern "C" UINT WINAPI timeKillEvent(UINT timer_id) {
    ensure_proxy_controller();
    return ensure_system_winmm() ? g_time_kill_event(timer_id) : 97u;
}

extern "C" UINT WINAPI timeSetEvent(UINT delay, UINT resolution,
                                     M1TimeCallback callback, DWORD_PTR user,
                                     UINT event_type) {
    ensure_proxy_controller();
    return ensure_system_winmm()
        ? g_time_set_event(delay, resolution, callback, user, event_type) : 0u;
}
#endif

extern "C" DWORD WINAPI M1StartW(void* parameter) {
    wchar_t persistentMode[2]{};
    g_persistent_requested=GetEnvironmentVariableW(L"SFC_PERSISTENT_SCENE",persistentMode,2)==1&&persistentMode[0]==L'1';
#ifdef M1_GATE_ONLY
    g_persistent_requested=false;
#endif
    if (InterlockedCompareExchange(&g_running, 0, 0)) return 10;
    if (!load_config(static_cast<const wchar_t*>(parameter))) return 1;
    if(g_persistent_requested&&g_config.live_channel.empty())return 1;
    const DWORD module_base = reinterpret_cast<DWORD>(GetModuleHandleW(nullptr));
    if (module_base != kImageBase) return 2;

    std::wostringstream event_name_stream;
    event_name_stream << L"Local\\SFCM1BurstComplete_" << GetCurrentProcessId();
    g_burst_event = CreateEventW(nullptr, TRUE, FALSE, event_name_stream.str().c_str());
    if (!g_burst_event) return 3;
    std::wostringstream tactical_name;
    tactical_name << L"Local\\SFCM1TacticalGate_" << GetCurrentProcessId();
    g_tactical_event = CreateEventW(nullptr, TRUE, FALSE, tactical_name.str().c_str());
    if (!g_tactical_event) return 3;
    if(g_config.enable_private_copy) {
        HMODULE pinned=nullptr;
        if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_PIN|GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS,
            reinterpret_cast<LPCWSTR>(&g_private_copy),&pinned))return 3;
        g_copy_module_pinned=true;
        std::wostringstream name;name << L"Local\\SFCM1PrivateCopyReady_" << GetCurrentProcessId();
        g_copy_ready_event=CreateEventW(nullptr,TRUE,FALSE,name.str().c_str());
        if(!g_copy_ready_event)return 3;
        if(!ResetEvent(g_copy_ready_event))return 3;
        if(g_config.enable_surface_lighting) {
            std::wostringstream lighting,restored;
            lighting << L"Local\\SFCM1SurfaceLighting_" << GetCurrentProcessId();
            restored << L"Local\\SFCM1SurfaceRestored_" << GetCurrentProcessId();
            g_surface_lighting_event=CreateEventW(nullptr,TRUE,FALSE,lighting.str().c_str());
            g_surface_restored_event=CreateEventW(nullptr,TRUE,FALSE,restored.str().c_str());
            if(!g_surface_lighting_event || !g_surface_restored_event ||
               !ResetEvent(g_surface_lighting_event) || !ResetEvent(g_surface_restored_event))return 3;
        }
    }

    for (Hook& hook : g_hooks) {
        if(!g_persistent_requested&&std::strcmp(hook.name,"ship_destroy")==0)continue;
        if(!g_config.enable_private_copy && std::strcmp(hook.name,"polygon_prepare")==0) continue;
        if(!g_config.enable_wrapper_observation && std::strcmp(hook.name,"polygon_wrapper")==0) continue;
        if (!g_config.enable_geometry_hook &&
            std::strcmp(hook.name, "geometry_submit") == 0) continue;
        if (!prepare_hook(hook, module_base)) return 4;
    }
    assign_trampolines();

    if(!g_config.live_channel.empty()){
        g_live_scene_mode=g_live_scene.start(g_config.live_channel,g_config.output_dir);
        if(!g_live_scene_mode && !g_live_bridge.start(g_config.live_channel,g_config.output_dir))return 3;
    }
#ifndef M1_GATE_ONLY
    if(replacement::requested()){
        if(!g_live_scene_mode||!g_live_scene.persistent||!g_config.enable_wrapper_observation)return 3;
        auto* candidate=reinterpret_cast<replacement::Store*>(g_live_scene.view+replacement::Offset);
        if(!replacement::valid(candidate,reinterpret_cast<DWORD*>(g_live_scene.view)+4,GetCurrentProcessId()))return 3;
        g_replacement=candidate;InterlockedExchange(&g_replacement->native_capable,1);
    }
#endif

    bool suspend_ok = false;
    auto suspended = suspend_other_threads(suspend_ok);
    if (!suspend_ok) { write_thread_failure("start"); stop_live(); return 5; }
    bool installed = true;
    for (Hook& hook : g_hooks) {
        if(!g_persistent_requested&&std::strcmp(hook.name,"ship_destroy")==0)continue;
        if(!g_config.enable_private_copy && std::strcmp(hook.name,"polygon_prepare")==0) continue;
        if(!g_config.enable_wrapper_observation && std::strcmp(hook.name,"polygon_wrapper")==0) continue;
        if (!g_config.enable_geometry_hook &&
            std::strcmp(hook.name, "geometry_submit") == 0) continue;
        if (!install_hook(hook, module_base)) {
            installed = false;
            break;
        }
    }
    if (!installed) restore_hooks(module_base);
    g_start_tick = GetTickCount64();
    if (installed) InterlockedExchange(&g_running, 1);
    resume_threads(suspended);
    if(!installed)stop_live();
    return installed ? 0 : 6;
}

extern "C" DWORD WINAPI M1Stop(void*) {
    if(g_replacement){
        InterlockedExchange(&g_replacement->native_stop,1);replacement::Control c{};replacement::read(g_replacement->control,c);
        if(c.mode==replacement::Active||c.mode==replacement::Recovering){
            const auto frame=static_cast<DWORD>(g_frame);const auto until=GetTickCount64()+2000;
            while(static_cast<DWORD>(InterlockedCompareExchange(&g_replacement->native_restored_frame,0,0))<=frame&&GetTickCount64()<until)Sleep(1);
            if(static_cast<DWORD>(InterlockedCompareExchange(&g_replacement->native_restored_frame,0,0))<=frame)return 12; // Retain hooks/storage, originals enabled, never unload an unacknowledged frame.
        }
    }
    if (!InterlockedExchange(&g_running, 0)) return 11;
    if(g_live_scene.calibration)InterlockedExchange(&g_live_scene.calibration->active,0);
    const ULONGLONG deadline = GetTickCount64() + 5000;
    while ((g_in_recorders || g_tint_live) && GetTickCount64() < deadline) Sleep(1);
    if (g_in_recorders || g_tint_live) return 12;

    const DWORD module_base = reinterpret_cast<DWORD>(GetModuleHandleW(nullptr));
    bool suspend_ok = false;
    auto suspended = suspend_other_threads(suspend_ok);
    if (!suspend_ok) { write_thread_failure("stop"); return 13; }
    const bool restored = restore_hooks(module_base);
    resume_threads(suspended);
    if(g_replacement){InterlockedExchange(&g_replacement->native_capable,0);g_replacement=nullptr;}
    if(!stop_live())return 12; // Never unload storage while worker remains live.
    const bool wrote = write_outputs(restored);
    if (g_burst_event) SetEvent(g_burst_event);
    return restored && wrote ? 0 : 14;
}

BOOL WINAPI DllMain(HINSTANCE instance, DWORD reason, LPVOID) {
    if (reason == DLL_PROCESS_ATTACH) {
        g_self = instance;
        DisableThreadLibraryCalls(instance);
        InitializeCriticalSection(&g_lock);
    } else if (reason == DLL_PROCESS_DETACH) {
        if (g_burst_event) CloseHandle(g_burst_event);
        if (g_tactical_event) CloseHandle(g_tactical_event);
        DeleteCriticalSection(&g_lock);
    }
    return TRUE;
}

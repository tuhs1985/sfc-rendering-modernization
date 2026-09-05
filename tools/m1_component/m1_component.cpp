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

namespace {

#ifdef M1_GATE_ONLY
constexpr const char* kSchema = "m1.scene-gate.v1";
constexpr const char* kComponentVersion = "0.1-gate";
#else
constexpr const char* kSchema = "m1.semantic.v1";
constexpr const char* kComponentVersion = "0.1";
#endif
constexpr DWORD kImageBase = 0x00400000;
constexpr DWORD kShipVtable = 0x00796F0C;
constexpr DWORD kVisualVtable = 0x007985A4;
constexpr DWORD kModel0Vtable = 0x007983E8;
constexpr DWORD kVisualMainlineReturn = 0x0042FDD5;
constexpr DWORD kKnownExceptionReturn = 0x00509843;
constexpr std::size_t kEventCapacity = 10000;
constexpr std::size_t kOwnerCapacity = 8;
constexpr std::size_t kThreadCapacity = 8;

enum EventKind : DWORD {
    kScene = 0,
    kShip = 1,
    kVisual = 2,
    kModel0 = 3,
    kVisualExit = 4,
    kGeometry = 5,
    kRetire = 6,
    kEventKindCount = 7,
};

const char* event_name(DWORD kind) {
    static const char* names[] = {
        "scene_begin", "ship_owner", "visual_model", "model0",
        "visual_exit", "geometry_submit", "owner_retired"
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
};

struct ThreadState {
    DWORD thread_id = 0;
    DWORD owner_id = 0;
    DWORD ship = 0;
    DWORD visual = 0;
    DWORD model0 = 0;
    DWORD source = 0;
    bool model_scope = false;
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
};

CRITICAL_SECTION g_lock;
Config g_config;
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
volatile LONG g_exception_509843 = 0;
volatile LONG g_rejected_semantics = 0;
volatile LONG g_owner_overflow = 0;
volatile LONG g_thread_overflow = 0;
volatile LONG g_log_truncated = 0;
ULONGLONG g_start_tick = 0;
ULONGLONG g_gate_tick = 0;
HANDLE g_burst_event = nullptr;
HMODULE g_self = nullptr;

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

const BYTE kSceneBytes[] = {0x53, 0x56, 0x8B, 0xF1, 0x57};
const BYTE kShipBytes[] = {0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x50};
const BYTE kVisualBytes[] = {0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x0C};
const BYTE kModel0Bytes[] = {0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x38};
const BYTE kVisualExitBytes[] = {0x5F, 0x5E, 0xC9, 0xC2, 0x0C, 0x00};
const BYTE kGeometryBytes[] = {0x83, 0xEC, 0x14, 0x53, 0x8B, 0xD9};

extern "C" void HookScene();
extern "C" void HookShip();
extern "C" void HookVisual();
extern "C" void HookModel0();
extern "C" void HookVisualExit();
extern "C" void HookGeometry();

#ifdef M1_GATE_ONLY
std::array<Hook, 1> g_hooks = {{
    {"ship_owner_gate", 0x000162B9, kShipBytes, sizeof(kShipBytes),
        reinterpret_cast<void*>(&HookShip)},
}};
#else
std::array<Hook, 6> g_hooks = {{
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

extern "C" void __cdecl RecordHook(DWORD kind, const DWORD* saved) {
    InterlockedIncrement(&g_in_recorders);
    if (!g_running || kind >= kEventKindCount) {
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

    if (kind == kScene) {
        event.origin = 0x0069E300;
        if (g_gate) {
            DWORD frame = static_cast<DWORD>(InterlockedIncrement(&g_frame));
            if (frame > 2) {
                g_owners.retire_before(frame - 2, [&](const auto& slot) {
                    EventRecord retired{};
                    retired.kind = kRetire;
                    retired.thread_id = thread_id;
                    retired.origin = 0x0069E300;
                    retired.owner_id = slot.id;
                    retired.ship = static_cast<DWORD>(slot.ship);
                    retired.visual = static_cast<DWORD>(slot.visual);
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
        bool valid = safe_read32(event.ship, event.ship_vtable) &&
            event.ship_vtable == kShipVtable &&
            safe_read32(event.ship + 0x88, visual);
        event.visual = visual;
        valid = valid && safe_read32(visual, event.visual_vtable) &&
            event.visual_vtable == kVisualVtable;
        if (valid) {
            if (InterlockedCompareExchange(&g_gate, 1, 0) == 0) {
                g_gate_tick = GetTickCount64();
                g_start_tick = g_gate_tick;
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
            InterlockedIncrement(&g_rejected_semantics);
        }
    } else if (kind == kVisual) {
        event.origin = 0x0042FD3F;
        event.visual = event.ecx;
        event.ship = event.ebx;
        DWORD ship_visual = 0;
        bool valid = safe_read32(event.ship, event.ship_vtable) &&
            event.ship_vtable == kShipVtable &&
            safe_read32(event.visual, event.visual_vtable) &&
            event.visual_vtable == kVisualVtable &&
            safe_read32(event.ship + 0x88, ship_visual) &&
            ship_visual == event.visual;
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
            InterlockedIncrement(&g_rejected_semantics);
        }
    } else if (kind == kModel0) {
        event.origin = 0x0042E4B2;
        event.model0 = event.ecx;
        event.visual = event.esi;
        event.manager = event.arg1;
        event.source = event.arg2;
        safe_read32(event.model0, event.model0_vtable);
        safe_read32(event.visual, event.visual_vtable);
        event.owner_id = g_owners.find_by_visual(event.visual);
        const bool mainline = event.return_address == kVisualMainlineReturn &&
            event.model0_vtable == kModel0Vtable &&
            event.visual_vtable == kVisualVtable && event.owner_id;
        if (event.return_address == kKnownExceptionReturn) {
            InterlockedIncrement(&g_exception_509843);
        }
        if (state) {
            if (mainline) {
                state->owner_id = event.owner_id;
                state->visual = event.visual;
                state->model0 = event.model0;
                state->source = event.source;
                state->model_scope = true;
                if (auto* slot = g_owners.find_by_id(event.owner_id)) {
                    event.ship = static_cast<DWORD>(slot->ship);
                    state->ship = event.ship;
                }
            } else {
                state->model_scope = false;
                state->model0 = 0;
            }
        }
        if (!mainline && event.return_address != kKnownExceptionReturn) {
            InterlockedIncrement(&g_rejected_semantics);
        }
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
        } else {
            InterlockedIncrement(&g_uncorrelated_geometry);
        }
        append_event_locked(event);
    } else if (kind == kVisualExit) {
        event.origin = 0x0042FDD5;
        if (state) {
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

#undef M1_HOOK_BODY

std::vector<HANDLE> suspend_other_threads(bool& ok) {
    std::vector<HANDLE> suspended;
    ok = false;
    HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0);
    if (snapshot == INVALID_HANDLE_VALUE) return suspended;
    THREADENTRY32 entry{};
    entry.dwSize = sizeof(entry);
    const DWORD process_id = GetCurrentProcessId();
    const DWORD current_thread = GetCurrentThreadId();
    bool enumeration_ok = Thread32First(snapshot, &entry) != FALSE;
    while (enumeration_ok) {
        if (entry.th32OwnerProcessID == process_id &&
            entry.th32ThreadID != current_thread) {
            HANDLE thread = OpenThread(THREAD_SUSPEND_RESUME, FALSE,
                entry.th32ThreadID);
            if (thread) {
                if (SuspendThread(thread) == static_cast<DWORD>(-1)) {
                    CloseHandle(thread);
                    enumeration_ok = false;
                    break;
                }
                suspended.push_back(thread);
            }
        }
        enumeration_ok = Thread32Next(snapshot, &entry) != FALSE;
    }
    DWORD enumeration_error = GetLastError();
    CloseHandle(snapshot);
    if (!enumeration_ok && enumeration_error != ERROR_NO_MORE_FILES) {
        for (HANDLE thread : suspended) {
            ResumeThread(thread);
            CloseHandle(thread);
        }
        suspended.clear();
        return suspended;
    }
    ok = true;
    return suspended;
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
#endif
}

bool load_config(const wchar_t* path) {
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
    return g_config.max_frames >= 1 && g_config.max_frames <= 120 &&
        g_config.max_events >= 1 && g_config.max_events <= kEventCapacity &&
        g_config.max_owners >= 1 && g_config.max_owners <= kOwnerCapacity &&
        g_config.warning_bytes <= g_config.hard_bytes &&
        g_config.hard_bytes <= 32u * 1024u * 1024u;
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
           "lod_count,lod_override,lod_selected,selected_child,correlated\n";
    const LONG count = (g_event_count < 0) ? 0 :
        ((g_event_count > static_cast<LONG>(kEventCapacity)) ?
            static_cast<LONG>(kEventCapacity) : g_event_count);
    for (LONG i = 0; i < count; ++i) {
        const EventRecord& e = g_events[static_cast<std::size_t>(i)];
        csv << kSchema << ',' << kComponentVersion << ',' << e.elapsed_ms << ','
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
            << e.correlated << '\n';
        if (csv.tellp() >= static_cast<std::streamoff>(g_config.hard_bytes)) {
            InterlockedExchange(&g_log_truncated, 1);
            break;
        }
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
            << "  \"counts\": {\n";
    for (DWORD kind = 0; kind < kEventKindCount; ++kind) {
        summary << "    \"" << event_name(kind) << "\": " << g_counts[kind]
                << (kind + 1 == kEventKindCount ? "\n" : ",\n");
    }
    summary << "  },\n"
            << "  \"correlated_geometry\": " << g_correlated_geometry << ",\n"
            << "  \"uncorrelated_geometry\": " << g_uncorrelated_geometry << ",\n"
            << "  \"known_exception_00509843\": " << g_exception_509843 << ",\n"
            << "  \"rejected_semantics\": " << g_rejected_semantics << ",\n"
            << "  \"owner_overflow\": " << g_owner_overflow << ",\n"
            << "  \"thread_overflow\": " << g_thread_overflow << ",\n"
            << "  \"limits\": {\n"
            << "    \"max_frames\": " << g_config.max_frames << ",\n"
            << "    \"max_events\": " << g_config.max_events << ",\n"
            << "    \"max_owners\": " << g_config.max_owners << ",\n"
            << "    \"warning_bytes\": " << g_config.warning_bytes << ",\n"
            << "    \"hard_bytes\": " << g_config.hard_bytes << "\n"
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
    return true;
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
    if (InterlockedCompareExchange(&g_running, 0, 0)) return 10;
    if (!load_config(static_cast<const wchar_t*>(parameter))) return 1;
    const DWORD module_base = reinterpret_cast<DWORD>(GetModuleHandleW(nullptr));
    if (module_base != kImageBase) return 2;

    std::wostringstream event_name_stream;
    event_name_stream << L"Local\\SFCM1BurstComplete_" << GetCurrentProcessId();
    g_burst_event = CreateEventW(nullptr, TRUE, FALSE, event_name_stream.str().c_str());
    if (!g_burst_event) return 3;

    for (Hook& hook : g_hooks) {
        if (!prepare_hook(hook, module_base)) return 4;
    }
    assign_trampolines();

    bool suspend_ok = false;
    auto suspended = suspend_other_threads(suspend_ok);
    if (!suspend_ok) return 5;
    bool installed = true;
    for (Hook& hook : g_hooks) {
        if (!install_hook(hook, module_base)) {
            installed = false;
            break;
        }
    }
    if (!installed) restore_hooks(module_base);
    g_start_tick = GetTickCount64();
    if (installed) InterlockedExchange(&g_running, 1);
    resume_threads(suspended);
    return installed ? 0 : 6;
}

extern "C" DWORD WINAPI M1Stop(void*) {
    if (!InterlockedExchange(&g_running, 0)) return 11;
    const ULONGLONG deadline = GetTickCount64() + 5000;
    while (g_in_recorders && GetTickCount64() < deadline) Sleep(1);
    if (g_in_recorders) return 12;

    const DWORD module_base = reinterpret_cast<DWORD>(GetModuleHandleW(nullptr));
    bool suspend_ok = false;
    auto suspended = suspend_other_threads(suspend_ok);
    if (!suspend_ok) return 13;
    const bool restored = restore_hooks(module_base);
    resume_threads(suspended);
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
        DeleteCriticalSection(&g_lock);
    }
    return TRUE;
}

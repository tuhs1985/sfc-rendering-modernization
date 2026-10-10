// In-process offline fixture: exercise the production recorder/stop lifecycle
// using synthetic x86 objects. No SFC process or real executable VA is patched.
#include "../tools/m1_component/m1_component.cpp"

#include <atomic>
#include <iostream>
#include <thread>

namespace {
void require_component(bool condition, const char* message) {
    if (!condition) { std::cerr << "FAIL: " << message << '\n'; std::exit(1); }
}
}

int main() {
    InitializeCriticalSection(&g_lock);
    std::array<DWORD, 0x558 / 4 + 1> manager{};
    std::array<DWORD, 8> model{};
    std::array<DWORD, 1> visual{kVisualVtable};
    std::array<DWORD, 0x88 / 4 + 1> ship{};
    ship[0] = kShipVtable;
    ship[0x88 / 4] = reinterpret_cast<DWORD>(visual.data());
    std::array<BYTE, 36> source{};
    source[4] = source[5] = source[6] = 255;
    const auto original = source;
    std::array<DWORD, 2> polygon{3, 0};
    DWORD list = reinterpret_cast<DWORD>(polygon.data());
    manager[0] = 0x007B8D4C;
    model[0] = kModel0Vtable;
    model[4] = 1;
    model[5] = reinterpret_cast<DWORD>(&list);
    const DWORD source_pointer = reinterpret_cast<DWORD>(source.data());
    std::array<DWORD, 5> stack{kVisualMainlineReturn,
        reinterpret_cast<DWORD>(manager.data()), source_pointer, 0x3F800000, 0};
    std::array<DWORD, 9> saved{};
    saved[1] = reinterpret_cast<DWORD>(visual.data());
    saved[3] = reinterpret_cast<DWORD>(stack.data()) - 4;
    saved[6] = reinterpret_cast<DWORD>(model.data());
    g_config.enable_geometry_hook = false;
    g_config.enable_visual_tint = true;
    g_running = 1;
    g_tactical_event = CreateEventW(nullptr, TRUE, FALSE, nullptr);
    saved[6] = reinterpret_cast<DWORD>(ship.data());
    RecordHook(kShip, saved.data());
    require_component(g_gate && WaitForSingleObject(g_tactical_event, 0) == WAIT_OBJECT_0,
                      "validated ship observation automatically signals tactical gate");
    saved[6] = reinterpret_cast<DWORD>(model.data());
    g_gate_tick = g_start_tick = GetTickCount64() - 6000;

    RecordHook(kModel0, saved.data());
    require_component(stack[2] != source_pointer && g_tint_live == 1 &&
                      g_tint_applied == 1, "production hook substitutes only source argument");
    const BYTE* copied = reinterpret_cast<const BYTE*>(stack[2]);
    require_component(copied[4] == 255 && copied[5] == 0 && copied[6] == 255 &&
                      source == original, "production substitution is magenta and copy-only");
    require_component(g_events[1].source == source_pointer &&
                      g_events[1].effective_source == stack[2] &&
                      g_events[1].owner_id == 1, "logical and effective identity are distinct");
    manager[0x558 / 4] = stack[2]; // emulate the original source setter
    RecordHook(kVisualExit, saved.data());
    require_component(manager[0x558 / 4] == source_pointer && g_tint_live == 0 &&
                      g_tint_restored == 1, "normal visual exit releases the copy");

    // A different owner must pass its original source without substitution.
    std::array<DWORD, 1> visual2{kVisualVtable};
    saved[1] = reinterpret_cast<DWORD>(visual2.data());
    g_owners.observe(0x2000, saved[1], 0);
    stack[2] = source_pointer;
    RecordHook(kModel0, saved.data());
    require_component(stack[2] == source_pointer && g_tint_applied == 1,
                      "second owner is never tinted");
    RecordHook(kVisualExit, saved.data());

    stack[0] = kKnownExceptionReturn;
    RecordHook(kModel0, saved.data());
    require_component(stack[2] == source_pointer && g_tint_applied == 1,
                      "known non-ship exception remains unmodified");
    RecordHook(kVisualExit, saved.data());
    stack[0] = kVisualMainlineReturn;

    saved[1] = reinterpret_cast<DWORD>(visual.data());
    RecordHook(kModel0, saved.data());
    manager[0x558 / 4] = stack[2];
    std::array<wchar_t, MAX_PATH> temp{};
    GetTempPathW(static_cast<DWORD>(temp.size()), temp.data());
    g_config.output_dir = std::wstring(temp.data()) + L"sfc-m1-tint-offline-" +
        std::to_wstring(GetCurrentProcessId()) + L"-" + std::to_wstring(GetTickCount64());
    std::atomic<DWORD> result{0xFFFFFFFFu};
    std::thread stopper([&]() { result = M1Stop(nullptr); });
    const auto deadline = GetTickCount64() + 2000;
    while (g_running && GetTickCount64() < deadline) Sleep(1);
    Sleep(20);
    require_component(!g_running && result == 0xFFFFFFFFu && g_tint_live == 1,
                      "stop waits for a live original-render invocation");
    RecordHook(kVisualExit, saved.data()); // exit remains active after stop request
    stopper.join();
    require_component(result == 0 && g_tint_live == 0 && g_tint_restored == 2 &&
                      manager[0x558 / 4] == source_pointer,
                      "stop drains then restores hooks/writes evidence");
    g_config.hard_bytes = 1024;
    require_component(write_outputs(true) && g_log_truncated,
                      "small output bound stops on a whole-row boundary");
    HANDLE bounded = CreateFileW((g_config.output_dir + L"\\M1-A-events.csv").c_str(),
        GENERIC_READ, FILE_SHARE_READ, nullptr, OPEN_EXISTING, 0, nullptr);
    require_component(bounded != INVALID_HANDLE_VALUE && GetFileSize(bounded, nullptr) <= 1024,
                      "event log never exceeds its byte cap");
    CloseHandle(bounded);
    for (const auto* name : {L"M1-A-events.csv", L"M1-A-summary.json", L"M1-A-component.log"})
        DeleteFileW((g_config.output_dir + L"\\" + name).c_str());
    RemoveDirectoryW(g_config.output_dir.c_str());
    CloseHandle(g_tactical_event);
    g_tactical_event = nullptr;
    DeleteCriticalSection(&g_lock);
    std::cout << "All M1 production tint lifecycle tests passed.\n";
}

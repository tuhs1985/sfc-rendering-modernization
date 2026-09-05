#define WIN32_LEAN_AND_MEAN
#include <windows.h>

#include <cstdlib>
#include <iostream>

namespace {

HANDLE callback_event = nullptr;

void CALLBACK timer_callback(UINT, UINT, DWORD_PTR, DWORD_PTR, DWORD_PTR) {
    SetEvent(callback_event);
}

void require(bool condition, const char* message) {
    if (!condition) {
        std::cerr << "FAIL: " << message << " error=" << GetLastError() << "\n";
        std::exit(1);
    }
}

}  // namespace

int wmain(int argc, wchar_t** argv) {
    require(argc == 2, "proxy path argument required");
    HMODULE proxy = LoadLibraryW(argv[1]);
    require(proxy != nullptr, "proxy loads");

    using TimeGetTime = DWORD (WINAPI*)();
    using TimeKillEvent = UINT (WINAPI*)(UINT);
    using TimeSetEvent = UINT (WINAPI*)(UINT, UINT,
        void (CALLBACK*)(UINT, UINT, DWORD_PTR, DWORD_PTR, DWORD_PTR),
        DWORD_PTR, UINT);
    auto time_get_time = reinterpret_cast<TimeGetTime>(
        GetProcAddress(proxy, "timeGetTime"));
    auto time_kill_event = reinterpret_cast<TimeKillEvent>(
        GetProcAddress(proxy, "timeKillEvent"));
    auto time_set_event = reinterpret_cast<TimeSetEvent>(
        GetProcAddress(proxy, "timeSetEvent"));
    require(time_get_time && time_kill_event && time_set_event,
            "all three forwarder exports resolve");

    DWORD first = time_get_time();
    Sleep(15);
    DWORD second = time_get_time();
    require(second >= first, "forwarded timeGetTime advances");

    callback_event = CreateEventW(nullptr, TRUE, FALSE, nullptr);
    require(callback_event != nullptr, "callback event created");
    constexpr UINT time_periodic = 1;
    UINT timer = time_set_event(10, 1, timer_callback, 0, time_periodic);
    require(timer != 0, "forwarded timeSetEvent creates a timer");
    require(WaitForSingleObject(callback_event, 2000) == WAIT_OBJECT_0,
            "forwarded timer callback executes");
    require(time_kill_event(timer) == 0, "forwarded timeKillEvent succeeds");

    CloseHandle(callback_event);
    Sleep(350);  // allow the no-config proxy controller worker to return
    FreeLibrary(proxy);
    std::cout << "All M1 WINMM proxy forwarding tests passed.\n";
    return 0;
}

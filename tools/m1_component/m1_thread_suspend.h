#pragma once
#include <windows.h>
#include <tlhelp32.h>
#include <vector>

namespace sfc_m1 {
struct ThreadSuspendDiagnostic {
    const char* api = "none";
    DWORD thread = 0, error = 0, rollback_failures = 0;
};
struct ThreadSuspendApi {
    decltype(&CreateToolhelp32Snapshot) snapshot = &CreateToolhelp32Snapshot;
    decltype(&Thread32First) first = &Thread32First;
    decltype(&Thread32Next) next = &Thread32Next;
    decltype(&GetCurrentProcessId) process_id = &GetCurrentProcessId;
    decltype(&GetCurrentThreadId) thread_id = &GetCurrentThreadId;
    decltype(&OpenThread) open = &OpenThread;
    decltype(&SuspendThread) suspend = &SuspendThread;
    decltype(&ResumeThread) resume = &ResumeThread;
    decltype(&CloseHandle) close = &CloseHandle;
    decltype(&GetLastError) error = &GetLastError;
};

inline std::vector<HANDLE> suspend_thread_transaction(bool& ok,
    ThreadSuspendDiagnostic& diagnostic, const ThreadSuspendApi& api = {}) {
    std::vector<HANDLE> suspended;
    ok = false; diagnostic = {};
    HANDLE snapshot = api.snapshot(TH32CS_SNAPTHREAD, 0);
    if (snapshot == INVALID_HANDLE_VALUE) {
        diagnostic.api = "CreateToolhelp32Snapshot"; diagnostic.error = api.error();
        return suspended;
    }
    THREADENTRY32 entry{}; entry.dwSize = sizeof(entry);
    const DWORD pid = api.process_id(), current = api.thread_id();
    bool available = api.first(snapshot, &entry) != FALSE;
    if (!available) {
        diagnostic.api = "Thread32First"; diagnostic.error = api.error();
    }
    while (available) {
        if (entry.th32OwnerProcessID == pid && entry.th32ThreadID != current) {
            diagnostic.thread = entry.th32ThreadID;
            HANDLE thread = api.open(THREAD_SUSPEND_RESUME, FALSE, entry.th32ThreadID);
            if (!thread) {
                diagnostic.api = "OpenThread"; diagnostic.error = api.error(); break;
            }
            if (api.suspend(thread) == static_cast<DWORD>(-1)) {
                diagnostic.api = "SuspendThread"; diagnostic.error = api.error();
                api.close(thread); break;
            }
            suspended.push_back(thread);
        }
        available = api.next(snapshot, &entry) != FALSE;
        if (!available) {
            const DWORD error = api.error();
            if (error == ERROR_NO_MORE_FILES) { ok = true; diagnostic = {}; }
            else { diagnostic.api = "Thread32Next"; diagnostic.error = error; }
        }
    }
    api.close(snapshot);
    if (!ok) {
        for (HANDLE thread : suspended) {
            if (api.resume(thread) == static_cast<DWORD>(-1)) ++diagnostic.rollback_failures;
            api.close(thread);
        }
        suspended.clear();
    }
    return suspended;
}
} // namespace sfc_m1

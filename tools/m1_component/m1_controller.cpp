#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <tlhelp32.h>
#include <wincrypt.h>

#include <algorithm>
#include <array>
#include <cstdint>
#include <cstring>
#include <cwctype>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>

#pragma comment(lib, "advapi32.lib")

namespace {

constexpr const char* kExpectedMd5 = "2BE8F713F81B1C68D50EAD6088C32886";

std::wstring lower(std::wstring value) {
    std::transform(value.begin(), value.end(), value.begin(),
        [](wchar_t c) { return static_cast<wchar_t>(std::towlower(c)); });
    return value;
}

std::string hex32(DWORD value) {
    std::ostringstream out;
    out << "0x" << std::uppercase << std::hex << std::setw(8)
        << std::setfill('0') << value;
    return out.str();
}

bool query_process_path(HANDLE process, std::wstring& path) {
    std::array<wchar_t, 32768> buffer{};
    DWORD size = static_cast<DWORD>(buffer.size());
    if (!QueryFullProcessImageNameW(process, 0, buffer.data(), &size)) return false;
    path.assign(buffer.data(), size);
    return true;
}

bool md5_file(const std::wstring& path, std::string& result) {
    HANDLE file = CreateFileW(path.c_str(), GENERIC_READ, FILE_SHARE_READ, nullptr,
        OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (file == INVALID_HANDLE_VALUE) return false;
    HCRYPTPROV provider = 0;
    HCRYPTHASH hash = 0;
    bool ok = CryptAcquireContextW(&provider, nullptr, nullptr, PROV_RSA_FULL,
        CRYPT_VERIFYCONTEXT) && CryptCreateHash(provider, CALG_MD5, 0, 0, &hash);
    std::array<BYTE, 64 * 1024> buffer{};
    while (ok) {
        DWORD count = 0;
        if (!ReadFile(file, buffer.data(), static_cast<DWORD>(buffer.size()),
                &count, nullptr)) {
            ok = false;
            break;
        }
        if (!count) break;
        ok = CryptHashData(hash, buffer.data(), count, 0) != FALSE;
    }
    BYTE digest[16]{};
    DWORD digest_size = sizeof(digest);
    if (ok) ok = CryptGetHashParam(hash, HP_HASHVAL, digest, &digest_size, 0) != FALSE;
    if (ok) {
        std::ostringstream out;
        for (BYTE byte : digest) {
            out << std::uppercase << std::hex << std::setw(2)
                << std::setfill('0') << static_cast<unsigned>(byte);
        }
        result = out.str();
    }
    if (hash) CryptDestroyHash(hash);
    if (provider) CryptReleaseContext(provider, 0);
    CloseHandle(file);
    return ok;
}

std::uintptr_t remote_module_base(DWORD pid, const std::wstring& module_name) {
    HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE |
        TH32CS_SNAPMODULE32, pid);
    if (snapshot == INVALID_HANDLE_VALUE) return 0;
    MODULEENTRY32W entry{};
    entry.dwSize = sizeof(entry);
    std::uintptr_t result = 0;
    if (Module32FirstW(snapshot, &entry)) {
        const std::wstring wanted = lower(module_name);
        do {
            if (lower(entry.szModule) == wanted) {
                result = reinterpret_cast<std::uintptr_t>(entry.modBaseAddr);
                break;
            }
        } while (Module32NextW(snapshot, &entry));
    }
    CloseHandle(snapshot);
    return result;
}

LPTHREAD_START_ROUTINE remote_kernel_proc(DWORD pid, const char* name) {
    HMODULE local = GetModuleHandleW(L"kernel32.dll");
    FARPROC local_proc = GetProcAddress(local, name);
    if (!local || !local_proc) return nullptr;
    MEMORY_BASIC_INFORMATION memory{};
    if (!VirtualQuery(reinterpret_cast<void*>(local_proc), &memory,
            sizeof(memory))) return nullptr;
    HMODULE owner = static_cast<HMODULE>(memory.AllocationBase);
    std::array<wchar_t, MAX_PATH> owner_path{};
    if (!GetModuleFileNameW(owner, owner_path.data(),
            static_cast<DWORD>(owner_path.size()))) return nullptr;
    std::wstring owner_name = owner_path.data();
    const std::size_t separator = owner_name.find_last_of(L"\\/");
    if (separator != std::wstring::npos) owner_name.erase(0, separator + 1);
    std::uintptr_t remote = remote_module_base(pid, owner_name);
    if (!remote) return nullptr;
    const std::uintptr_t offset = reinterpret_cast<std::uintptr_t>(local_proc) -
        reinterpret_cast<std::uintptr_t>(owner);
    return reinterpret_cast<LPTHREAD_START_ROUTINE>(remote + offset);
}

bool remote_call(HANDLE process, LPTHREAD_START_ROUTINE procedure, void* parameter,
                 DWORD timeout_ms, DWORD& result) {
    HANDLE thread = CreateRemoteThread(process, nullptr, 0, procedure, parameter,
        0, nullptr);
    if (!thread) return false;
    const DWORD wait = WaitForSingleObject(thread, timeout_ms);
    bool ok = wait == WAIT_OBJECT_0 && GetExitCodeThread(thread, &result);
    CloseHandle(thread);
    return ok;
}

void* remote_string(HANDLE process, const std::wstring& value) {
    const SIZE_T bytes = (value.size() + 1) * sizeof(wchar_t);
    void* remote = VirtualAllocEx(process, nullptr, bytes, MEM_COMMIT | MEM_RESERVE,
        PAGE_READWRITE);
    if (!remote) return nullptr;
    SIZE_T written = 0;
    if (!WriteProcessMemory(process, remote, value.c_str(), bytes, &written) ||
        written != bytes) {
        VirtualFreeEx(process, remote, 0, MEM_RELEASE);
        return nullptr;
    }
    return remote;
}

bool restored_bytes(HANDLE process) {
    struct Check { DWORD address; const BYTE* bytes; SIZE_T size; };
    static const BYTE scene[] = {0x53, 0x56, 0x8B, 0xF1, 0x57};
    static const BYTE ship[] = {0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x50};
    static const BYTE visual[] = {0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x0C};
    static const BYTE model[] = {0x55, 0x8B, 0xEC, 0x83, 0xEC, 0x38};
    static const BYTE visual_exit[] = {0x5F, 0x5E, 0xC9, 0xC2, 0x0C, 0x00};
    static const BYTE geometry[] = {0x83, 0xEC, 0x14, 0x53, 0x8B, 0xD9};
    const Check checks[] = {
        {0x0069E300, scene, sizeof(scene)},
        {0x004162B9, ship, sizeof(ship)},
        {0x0042FD3F, visual, sizeof(visual)},
        {0x0042E4B2, model, sizeof(model)},
        {0x0042FDD5, visual_exit, sizeof(visual_exit)},
        {0x006AB410, geometry, sizeof(geometry)},
    };
    for (const Check& check : checks) {
        BYTE observed[8]{};
        SIZE_T read = 0;
        if (!ReadProcessMemory(process, reinterpret_cast<void*>(check.address),
                observed, check.size, &read) || read != check.size ||
            std::memcmp(observed, check.bytes, check.size) != 0) return false;
    }
    return true;
}

void usage() {
    std::wcerr << L"Usage: m1_controller.exe --pid <pid> --dll <path> "
                  L"--config <path> [--max-seconds 300] [--stop-on-burst 0|1] "
                  L"[--already-loaded 0|1] [--unload-after-stop 0|1] "
                  L"[--gate-timeout-seconds 0..900]\n";
}

}  // namespace

int wmain(int argc, wchar_t** argv) {
    DWORD pid = 0;
    DWORD max_seconds = 300;
    bool stop_on_burst = true;
    bool already_loaded = false;
    bool unload_after_stop = false;
    DWORD gate_timeout_seconds = 0;
    std::wstring dll_path;
    std::wstring config_path;
    for (int i = 1; i < argc; ++i) {
        const std::wstring arg = argv[i];
        if (arg == L"--pid" && i + 1 < argc) pid = _wtoi(argv[++i]);
        else if (arg == L"--dll" && i + 1 < argc) dll_path = argv[++i];
        else if (arg == L"--config" && i + 1 < argc) config_path = argv[++i];
        else if (arg == L"--max-seconds" && i + 1 < argc)
            max_seconds = _wtoi(argv[++i]);
        else if (arg == L"--stop-on-burst" && i + 1 < argc)
            stop_on_burst = _wtoi(argv[++i]) != 0;
        else if (arg == L"--already-loaded" && i + 1 < argc)
            already_loaded = _wtoi(argv[++i]) != 0;
        else if (arg == L"--unload-after-stop" && i + 1 < argc)
            unload_after_stop = _wtoi(argv[++i]) != 0;
        else if (arg == L"--gate-timeout-seconds" && i + 1 < argc)
            gate_timeout_seconds = _wtoi(argv[++i]);
        else { usage(); return 2; }
    }
    if (!pid || dll_path.empty() || config_path.empty() || gate_timeout_seconds > 900 || max_seconds < 1 ||
        max_seconds > 2100) {
        usage();
        return 2;
    }

    HANDLE process = OpenProcess(PROCESS_CREATE_THREAD | PROCESS_QUERY_INFORMATION |
        PROCESS_VM_OPERATION | PROCESS_VM_WRITE | PROCESS_VM_READ | SYNCHRONIZE,
        FALSE, pid);
    if (!process) {
        std::cerr << "OpenProcess failed: " << GetLastError() << "\n";
        return 3;
    }
    std::wstring image_path;
    std::string md5;
    if (!query_process_path(process, image_path) || !md5_file(image_path, md5) ||
        md5 != kExpectedMd5) {
        std::cerr << "Refusing target: exact client MD5 validation failed.\n";
        CloseHandle(process);
        return 4;
    }
    std::cout << "target_md5=" << md5 << "\n";

    DWORD remote_module = 0;
    if (already_loaded) {
        std::wstring module_name = dll_path;
        const std::size_t separator = module_name.find_last_of(L"\\/");
        if (separator != std::wstring::npos) module_name.erase(0, separator + 1);
        remote_module = static_cast<DWORD>(remote_module_base(pid, module_name));
        if (!remote_module) {
            std::cerr << "Already-loaded component module was not found.\n";
            CloseHandle(process);
            return 5;
        }
    } else {
        void* remote_dll_path = remote_string(process, dll_path);
        LPTHREAD_START_ROUTINE load_library = remote_kernel_proc(pid, "LoadLibraryW");
        if (!remote_dll_path || !load_library ||
            !remote_call(process, load_library, remote_dll_path, 15000,
                remote_module) || !remote_module) {
            std::cerr << "Remote LoadLibraryW failed: " << GetLastError() << "\n";
            if (remote_dll_path)
                VirtualFreeEx(process, remote_dll_path, 0, MEM_RELEASE);
            CloseHandle(process);
            return 5;
        }
        VirtualFreeEx(process, remote_dll_path, 0, MEM_RELEASE);
    }
    std::cout << "component_module=" << hex32(remote_module) << "\n";

    HMODULE local_image = LoadLibraryExW(dll_path.c_str(), nullptr,
        DONT_RESOLVE_DLL_REFERENCES);
    FARPROC local_start = local_image ? GetProcAddress(local_image, "M1StartW") : nullptr;
    FARPROC local_stop = local_image ? GetProcAddress(local_image, "M1Stop") : nullptr;
    if (!local_start || !local_stop) {
        std::cerr << "Component exports unavailable.\n";
        if (local_image) FreeLibrary(local_image);
        CloseHandle(process);
        return 6;
    }
    auto remote_export = [&](FARPROC local_proc) {
        return reinterpret_cast<LPTHREAD_START_ROUTINE>(remote_module +
            (reinterpret_cast<std::uintptr_t>(local_proc) -
             reinterpret_cast<std::uintptr_t>(local_image)));
    };

    void* remote_config = remote_string(process, config_path);
    DWORD start_result = 0;
    if (!remote_config || !remote_call(process, remote_export(local_start),
            remote_config, 15000, start_result) || start_result != 0) {
        std::cerr << "M1StartW failed: " << start_result << "\n";
        if (remote_config) VirtualFreeEx(process, remote_config, 0, MEM_RELEASE);
        FreeLibrary(local_image);
        CloseHandle(process);
        return 7;
    }
    VirtualFreeEx(process, remote_config, 0, MEM_RELEASE);
    std::cout << "component_state=enabled\n";

    std::wostringstream event_name;
    event_name << L"Local\\SFCM1BurstComplete_" << pid;
    HANDLE burst = nullptr;
    for (int attempt = 0; attempt < 50 && !burst; ++attempt) {
        burst = OpenEventW(SYNCHRONIZE, FALSE, event_name.str().c_str());
        if (!burst) Sleep(20);
    }

    DWORD wait_result = WAIT_TIMEOUT;
    bool gate_ready = gate_timeout_seconds == 0;
    if (gate_timeout_seconds && gate_timeout_seconds <= 900) {
        std::wostringstream tactical_name;
        tactical_name << L"Local\\SFCM1TacticalGate_" << pid;
        HANDLE tactical = OpenEventW(SYNCHRONIZE, FALSE, tactical_name.str().c_str());
        if (tactical) {
            HANDLE gates[] = {process, tactical};
            wait_result = WaitForMultipleObjects(2, gates, FALSE, gate_timeout_seconds * 1000);
            gate_ready = wait_result == WAIT_OBJECT_0 + 1;
            CloseHandle(tactical);
        }
        std::cout << "tactical_gate=" << (gate_ready ? "detected" : "not_detected") << "\n";
    }
    if (gate_ready && stop_on_burst && burst) {
        HANDLE waits[] = {process, burst};
        wait_result = WaitForMultipleObjects(2, waits, FALSE, max_seconds * 1000);
    } else if (gate_ready) {
        wait_result = WaitForSingleObject(process, max_seconds * 1000);
    }
    if (wait_result == WAIT_OBJECT_0) {
        std::cerr << "Target exited before controlled component removal.\n";
        if (burst) CloseHandle(burst);
        FreeLibrary(local_image);
        CloseHandle(process);
        return 8;
    }
    std::cout << "stop_trigger="
              << (!gate_ready ? "gate_timeout" :
                  (stop_on_burst && wait_result == WAIT_OBJECT_0 + 1) ?
                    "detail_bound" : "duration") << "\n";

    DWORD stop_result = 0;
    if (!remote_call(process, remote_export(local_stop), nullptr, 15000,
            stop_result) || stop_result != 0) {
        std::cerr << "M1Stop failed: " << stop_result << "\n";
        if (burst) CloseHandle(burst);
        FreeLibrary(local_image);
        CloseHandle(process);
        return 9;
    }
    const bool restored = restored_bytes(process);
    std::cout << "component_state=removed\n"
              << "hook_bytes_restored=" << (restored ? "true" : "false") << "\n";
    bool unloaded = true;
    if (restored && unload_after_stop) {
        DWORD unload_result = 0;
        LPTHREAD_START_ROUTINE free_library = remote_kernel_proc(pid, "FreeLibrary");
        unloaded = free_library && remote_call(process, free_library,
            reinterpret_cast<void*>(remote_module), 15000, unload_result) &&
            unload_result != 0;
        std::cout << "component_unloaded=" << (unloaded ? "true" : "false") << "\n";
    }
    if (burst) CloseHandle(burst);
    FreeLibrary(local_image);
    CloseHandle(process);
    return !gate_ready ? 15 : restored && unloaded ? 0 : 10;
}

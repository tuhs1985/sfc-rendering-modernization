#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <wincrypt.h>

#include <array>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <vector>

#pragma comment(lib, "advapi32.lib")

namespace {

constexpr DWORD kImageBase = 0x00400000;
constexpr const char* kExpectedMd5 = "2BE8F713F81B1C68D50EAD6088C32886";
constexpr const char* kProbeVersion = "0.4";

struct ProbePoint {
    const char* id;
    DWORD rva;
    BYTE expected;
    std::uint64_t max_hits;
    const char* profile;
    std::uint64_t hits = 0;
    BYTE original = 0;
    std::uintptr_t address = 0;
    bool armed = false;
};

std::vector<ProbePoint> points = {
    {"ship_model_init",       0x0001C271, 0x55, 2000, "path"},
    {"model_parse",           0x0002FEF9, 0xB8,  500, "path"},
    {"scene_begin",           0x0029E300, 0x53, 4000, "path"},
    {"scene_end",             0x0029E3D0, 0x53, 4000, "path"},
    {"engine_present",        0x0029EB90, 0x56, 4000, "path"},
    {"batch_flush",           0x002AB380, 0x56, 1000, "both"},
    {"draw_indexed_call",     0x002AB3C0, 0xFF, 1000, "both"},
    {"geometry_submit",       0x002AB410, 0x83, 1500, "both"},
    {"surface_present",       0x002A84B0, 0x8B, 4000, "path"},
    {"owner_source_init",     0x002ABF80, 0x56,  256, "owner"},
    {"owner_source_ptr",      0x002ABFB0, 0x8B,  256, "owner"},
    {"polygon_owner_entry",   0x002ABFC0, 0x81, 1200, "owner"},
    {"visual_model_render",   0x0002FD3F, 0x55,  384, "semantic"},
    {"visual_to_model_call",  0x0002FDD2, 0xFF,  384, "semantic"},
    {"model0_render",         0x0002E4B2, 0x55,  384, "semantic"},
};

std::ofstream log_file;
std::uint64_t sequence_no = 0;
ULONGLONG start_tick = 0;
HANDLE process_handle = nullptr;
DWORD process_id = 0;
std::uintptr_t image_base = 0;
std::map<DWORD, std::size_t> pending_single_step;

std::string narrow(const std::wstring& value) {
    if (value.empty()) return {};
    int size = WideCharToMultiByte(CP_UTF8, 0, value.data(),
        static_cast<int>(value.size()), nullptr, 0, nullptr, nullptr);
    std::string result(size, '\0');
    WideCharToMultiByte(CP_UTF8, 0, value.data(), static_cast<int>(value.size()),
        result.data(), size, nullptr, nullptr);
    return result;
}

std::string hex32(DWORD value) {
    std::ostringstream out;
    out << "0x" << std::uppercase << std::hex << std::setw(8)
        << std::setfill('0') << value;
    return out.str();
}

bool read_memory(std::uintptr_t address, void* output, SIZE_T size) {
    SIZE_T read = 0;
    return ReadProcessMemory(process_handle,
        reinterpret_cast<LPCVOID>(address), output, size, &read) && read == size;
}

DWORD read_u32(std::uintptr_t address) {
    DWORD value = 0;
    read_memory(address, &value, sizeof(value));
    return value;
}

bool write_byte(std::uintptr_t address, BYTE value) {
    DWORD old_protect = 0;
    if (!VirtualProtectEx(process_handle, reinterpret_cast<LPVOID>(address), 1,
            PAGE_EXECUTE_READWRITE, &old_protect)) {
        return false;
    }
    SIZE_T written = 0;
    bool ok = WriteProcessMemory(process_handle, reinterpret_cast<LPVOID>(address),
        &value, 1, &written) && written == 1;
    FlushInstructionCache(process_handle, reinterpret_cast<LPCVOID>(address), 1);
    DWORD ignored = 0;
    VirtualProtectEx(process_handle, reinterpret_cast<LPVOID>(address), 1,
        old_protect, &ignored);
    return ok;
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

bool query_process_path(DWORD pid, std::wstring& path) {
    HANDLE process = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, pid);
    if (!process) return false;
    std::array<wchar_t, 32768> buffer{};
    DWORD size = static_cast<DWORD>(buffer.size());
    bool ok = QueryFullProcessImageNameW(process, 0, buffer.data(), &size) != FALSE;
    if (ok) path.assign(buffer.data(), size);
    CloseHandle(process);
    return ok;
}

void write_meta(const std::string& event, const std::string& detail) {
    log_file << "META," << (GetTickCount64() - start_tick) << ","
             << event << "," << detail << "\n";
    log_file.flush();
}

void write_sample(const ProbePoint& point, DWORD thread_id, const CONTEXT& context) {
    std::array<DWORD, 8> stack{};
    read_memory(context.Esp, stack.data(), sizeof(stack));
    std::array<DWORD, 6> data{};

    const std::string id(point.id);
    if (id == "scene_begin" || id == "scene_end" || id == "engine_present") {
        data[0] = read_u32(context.Ecx + 0x7F64);
        data[1] = read_u32(context.Ecx + 0x3C54);
        data[2] = read_u32(context.Ecx + 0x3C30);
        data[3] = read_u32(context.Ecx + 0x3C28);
        data[4] = read_u32(context.Ecx + 0x3BFc);
    } else if (id == "batch_flush") {
        data[0] = read_u32(context.Ecx + 0x1CC0);
        data[1] = read_u32(context.Ecx + 0x1CB0);
        data[2] = read_u32(context.Ecx + 0x1CB4);
        data[3] = read_u32(context.Ecx + 0x1CBC);
        data[4] = context.Ecx - 0x1F4C;
    } else if (id == "draw_indexed_call") {
        data[0] = context.Esi;
        data[1] = stack[0];
        data[2] = stack[3];
        data[3] = stack[4];
        data[4] = stack[5];
        data[5] = stack[6];
    } else if (id == "geometry_submit") {
        data[0] = stack[1];
        data[1] = stack[2];
        data[2] = stack[3];
        data[3] = stack[4];
        data[4] = read_u32(context.Ecx + 0x7F64);
        data[5] = context.Ecx + 0x1F4C;
    } else if (id == "owner_source_init") {
        data[0] = stack[1];
        data[1] = stack[2];
        data[2] = read_u32(context.Ecx + 0x04);
        data[3] = read_u32(context.Ecx + 0x554);
        data[4] = read_u32(context.Ecx + 0x558);
        data[5] = read_u32(context.Ebp + 0x04);
    } else if (id == "owner_source_ptr") {
        data[0] = stack[1];
        data[1] = read_u32(stack[1]);
        data[2] = read_u32(context.Ecx + 0x04);
        data[3] = read_u32(context.Ecx + 0x554);
        data[4] = read_u32(context.Ecx + 0x558);
        data[5] = read_u32(context.Ebp + 0x04);
    } else if (id == "polygon_owner_entry") {
        data[0] = stack[1];
        data[1] = stack[2];
        data[2] = stack[3];
        data[3] = stack[4];
        data[4] = read_u32(stack[3]);
        data[5] = read_u32(context.Ecx + 0x558);
    } else if (id == "visual_model_render") {
        data[0] = read_u32(context.Ecx);
        data[1] = read_u32(context.Ecx + 0x158);
        data[2] = read_u32(context.Ecx + 0x11C);
        data[3] = read_u32(context.Ecx + 0x120);
        data[4] = read_u32(context.Ecx + 0x124);
        data[5] = stack[0];
    } else if (id == "visual_to_model_call") {
        data[0] = stack[0];
        data[1] = stack[1];
        data[2] = stack[2];
        data[3] = stack[3];
        data[4] = read_u32(context.Ecx);
        data[5] = read_u32(context.Esi);
    } else if (id == "model0_render") {
        data[0] = read_u32(context.Ecx);
        data[1] = stack[1];
        data[2] = stack[2];
        data[3] = stack[3];
        data[4] = stack[4];
        data[5] = stack[0];
    } else if (id == "surface_present") {
        data[0] = read_u32(context.Ecx + 0x30);
        data[1] = read_u32(context.Ecx + 0x34);
        data[2] = read_u32(context.Ecx + 0x38);
        data[3] = read_u32(context.Ecx + 0x04);
        data[4] = read_u32(context.Ecx + 0x40);
    } else if (id == "ship_model_init") {
        for (std::size_t i = 0; i < data.size(); ++i) data[i] = stack[i + 1];
    } else if (id == "model_parse") {
        data[0] = stack[1];
        data[1] = read_u32(context.Ecx + 0x154);
        data[2] = read_u32(context.Ecx + 0x15C);
    }

    log_file << "SAMPLE," << (GetTickCount64() - start_tick) << ","
             << ++sequence_no << "," << point.id << "," << point.hits << ","
             << thread_id << "," << hex32(context.Eip) << ","
             << hex32(context.Eax) << "," << hex32(context.Ebx) << ","
             << hex32(context.Ecx) << "," << hex32(context.Edx) << ","
             << hex32(context.Esi) << "," << hex32(context.Edi) << ","
             << hex32(context.Esp) << "," << hex32(context.Ebp) << ","
             << hex32(stack[0]);
    for (DWORD value : data) log_file << "," << hex32(value);
    log_file << "\n";
    log_file.flush();
}

bool arm_points() {
    for (ProbePoint& point : points) {
        point.address = image_base + point.rva;
        BYTE current = 0;
        if (!read_memory(point.address, &current, 1)) {
            write_meta("arm_error", std::string(point.id) + ":read_failed");
            return false;
        }
        if (current != point.expected) {
            write_meta("arm_error", std::string(point.id) + ":expected_" +
                hex32(point.expected) + "_observed_" + hex32(current));
            return false;
        }
        point.original = current;
        if (!write_byte(point.address, 0xCC)) {
            write_meta("arm_error", std::string(point.id) + ":write_failed");
            return false;
        }
        point.armed = true;
    }
    write_meta("armed", std::to_string(points.size()) + "_points");
    return true;
}

void restore_all() {
    for (ProbePoint& point : points) {
        if (point.armed) {
            write_byte(point.address, point.original);
            point.armed = false;
        }
    }
}

ProbePoint* find_point(std::uintptr_t address, std::size_t& index) {
    for (std::size_t i = 0; i < points.size(); ++i) {
        if (points[i].armed && points[i].address == address) {
            index = i;
            return &points[i];
        }
    }
    return nullptr;
}

void write_summary(const char* reason) {
    write_meta("stop_reason", reason);
    for (const ProbePoint& point : points) {
        write_meta("count", std::string(point.id) + "=" + std::to_string(point.hits));
    }
}

void usage() {
    std::wcerr << L"Usage: m0_probe.exe --pid <pid> --log <path> "
                  L"[--max-seconds <seconds>] "
                  L"[--profile m0-rt-001|m0-rt-002|m0-rt-003]\n";
}

}  // namespace

int wmain(int argc, wchar_t** argv) {
    DWORD attach_pid = 0;
    DWORD max_seconds = 300;
    std::wstring log_path;
    std::string profile = "m0-rt-001";
    for (int i = 1; i < argc; ++i) {
        std::wstring arg = argv[i];
        if (arg == L"--pid" && i + 1 < argc) {
            attach_pid = static_cast<DWORD>(_wtoi(argv[++i]));
        } else if (arg == L"--log" && i + 1 < argc) {
            log_path = argv[++i];
        } else if (arg == L"--max-seconds" && i + 1 < argc) {
            max_seconds = static_cast<DWORD>(_wtoi(argv[++i]));
        } else if (arg == L"--profile" && i + 1 < argc) {
            profile = narrow(argv[++i]);
        } else if (arg == L"--help") {
            usage();
            return 0;
        } else {
            usage();
            return 2;
        }
    }
    if (!attach_pid || log_path.empty()) {
        usage();
        return 2;
    }
    if (profile != "m0-rt-001" && profile != "m0-rt-002" &&
        profile != "m0-rt-003") {
        usage();
        return 2;
    }
    const std::string selected =
        profile == "m0-rt-003" ? "semantic" :
        profile == "m0-rt-002" ? "owner" : "path";
    std::vector<ProbePoint> selected_points;
    for (const ProbePoint& point : points) {
        if (selected == point.profile || std::string(point.profile) == "both" ||
            (selected == "semantic" && std::string(point.profile) == "owner"))
            selected_points.push_back(point);
    }
    points.swap(selected_points);

    std::wstring image_path;
    if (!query_process_path(attach_pid, image_path)) {
        std::wcerr << L"Could not query target process path.\n";
        return 3;
    }
    std::string md5;
    if (!md5_file(image_path, md5) || md5 != kExpectedMd5) {
        std::cerr << "Refusing target: MD5 is " << md5 << ", expected "
                  << kExpectedMd5 << ".\n";
        return 4;
    }

    log_file.open(narrow(log_path), std::ios::out | std::ios::trunc);
    if (!log_file) {
        std::wcerr << L"Could not create probe log.\n";
        return 5;
    }
    start_tick = GetTickCount64();
    log_file << "kind,elapsed_ms,sequence_or_event,event_or_detail,hit,thread,eip,"
                "eax,ebx,ecx,edx,esi,edi,esp,ebp,return_or_stack0,"
                "data1,data2,data3,data4,data5,data6\n";
    write_meta("probe",
        profile == "m0-rt-003" ? "M0-RT-003" :
        profile == "m0-rt-002" ? "M0-RT-002" : "M0-RT-001");
    write_meta("probe_version", kProbeVersion);
    write_meta("target_md5", md5);
    write_meta("target_path", narrow(image_path));

    if (!DebugActiveProcess(attach_pid)) {
        write_meta("attach_error", std::to_string(GetLastError()));
        return 6;
    }
    DebugSetProcessKillOnExit(FALSE);
    process_id = attach_pid;
    bool armed = false;
    bool detached = false;
    bool stop_requested = false;

    while (!detached) {
        if (!stop_requested &&
            GetTickCount64() - start_tick >= static_cast<ULONGLONG>(max_seconds) * 1000) {
            stop_requested = true;
            write_meta("timeout", std::to_string(max_seconds));
            DebugBreakProcess(process_handle);
        }

        DEBUG_EVENT event{};
        if (!WaitForDebugEvent(&event, 100)) continue;
        DWORD continue_status = DBG_CONTINUE;

        if (event.dwDebugEventCode == CREATE_PROCESS_DEBUG_EVENT) {
            process_handle = event.u.CreateProcessInfo.hProcess;
            image_base = reinterpret_cast<std::uintptr_t>(
                event.u.CreateProcessInfo.lpBaseOfImage);
            write_meta("image_base", hex32(static_cast<DWORD>(image_base)));
            if (event.u.CreateProcessInfo.hFile)
                CloseHandle(event.u.CreateProcessInfo.hFile);
            armed = arm_points();
            if (!armed) stop_requested = true;
        } else if (event.dwDebugEventCode == CREATE_THREAD_DEBUG_EVENT) {
            if (event.u.CreateThread.hThread) CloseHandle(event.u.CreateThread.hThread);
        } else if (event.dwDebugEventCode == LOAD_DLL_DEBUG_EVENT) {
            if (event.u.LoadDll.hFile) CloseHandle(event.u.LoadDll.hFile);
        } else if (event.dwDebugEventCode == EXIT_PROCESS_DEBUG_EVENT) {
            write_summary("process_exit");
            ContinueDebugEvent(event.dwProcessId, event.dwThreadId, DBG_CONTINUE);
            detached = true;
            break;
        } else if (event.dwDebugEventCode == EXCEPTION_DEBUG_EVENT) {
            const auto& exception = event.u.Exception.ExceptionRecord;
            DWORD code = exception.ExceptionCode;
            std::uintptr_t address = reinterpret_cast<std::uintptr_t>(
                exception.ExceptionAddress);
            HANDLE thread = OpenThread(THREAD_GET_CONTEXT | THREAD_SET_CONTEXT |
                THREAD_QUERY_INFORMATION, FALSE, event.dwThreadId);
            CONTEXT context{};
            context.ContextFlags = CONTEXT_FULL;
            if (!thread || !GetThreadContext(thread, &context)) {
                continue_status = DBG_EXCEPTION_NOT_HANDLED;
            } else if (code == EXCEPTION_BREAKPOINT) {
                std::size_t index = 0;
                ProbePoint* point = find_point(address, index);
                if (point) {
                    write_byte(point->address, point->original);
                    context.Eip = static_cast<DWORD>(point->address);
                    context.EFlags |= 0x100;
                    SetThreadContext(thread, &context);
                    ++point->hits;
                    write_sample(*point, event.dwThreadId, context);
                    pending_single_step[event.dwThreadId] = index;
                } else if (stop_requested) {
                    restore_all();
                    context.EFlags &= ~0x100u;
                    SetThreadContext(thread, &context);
                    write_summary(armed ? "timeout_detach" : "arm_failure");
                    ContinueDebugEvent(event.dwProcessId, event.dwThreadId, DBG_CONTINUE);
                    DebugActiveProcessStop(process_id);
                    detached = true;
                    CloseHandle(thread);
                    break;
                }
            } else if (code == EXCEPTION_SINGLE_STEP) {
                auto pending = pending_single_step.find(event.dwThreadId);
                if (pending != pending_single_step.end()) {
                    ProbePoint& point = points[pending->second];
                    context.EFlags &= ~0x100u;
                    SetThreadContext(thread, &context);
                    if (point.hits < point.max_hits) {
                        write_byte(point.address, 0xCC);
                    } else {
                        point.armed = false;
                        write_meta("point_saturated",
                            std::string(point.id) + "=" + std::to_string(point.hits));
                    }
                    pending_single_step.erase(pending);
                } else {
                    continue_status = DBG_EXCEPTION_NOT_HANDLED;
                }
            } else {
                continue_status = DBG_EXCEPTION_NOT_HANDLED;
            }
            if (thread) CloseHandle(thread);
        }

        if (!detached)
            ContinueDebugEvent(event.dwProcessId, event.dwThreadId, continue_status);
    }

    restore_all();
    return 0;
}

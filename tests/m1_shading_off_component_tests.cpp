// Production recorder with synthetic x86 objects only: no SFC or target VA patching.
#include "../tools/m1_component/m1_component.cpp"
#include <cstdlib>
#include <iostream>

void check(bool condition, const char* message) {
    if (!condition) { std::cerr << "FAIL: " << message << '\n'; std::exit(1); }
}

int wmain(int argc, wchar_t** argv) {
    InitializeCriticalSection(&g_lock);
    std::array<DWORD, 0x1ECC / 4 + 1> manager{};
    std::array<DWORD, 8> model{};
    std::array<DWORD, 1> visual{kVisualVtable}, visual2{kVisualVtable};
    std::array<BYTE, 36> source{};
    source[0] = 0xA7; source[4] = 80; source[5] = 120; source[6] = 160;
    const auto original = source;
    std::array<DWORD, 2> polygon{3, 0};
    DWORD list = reinterpret_cast<DWORD>(polygon.data());
    manager[0] = 0x007B8D4C;
    model[0] = kModel0Vtable; model[4] = 1; model[5] = reinterpret_cast<DWORD>(&list);
    const DWORD source_pointer = reinterpret_cast<DWORD>(source.data());
    std::array<DWORD, 5> stack{kVisualMainlineReturn,
        reinterpret_cast<DWORD>(manager.data()), source_pointer, 0x3F800000, 0};
    std::array<DWORD, 9> saved{};
    saved[1] = reinterpret_cast<DWORD>(visual.data());
    saved[3] = reinterpret_cast<DWORD>(stack.data()) - 4;
    saved[6] = reinterpret_cast<DWORD>(model.data());
    g_owners.observe(0x1000, saved[1], 0);
    g_config.enable_geometry_hook = false; g_config.enable_shading_off = true;
    g_running = g_gate = g_saturated = 1;
    g_frame = 120; // detail exhausted before all phases: intervention must continue
    auto invoke = [&](DWORD elapsed) {
        stack[2] = source_pointer;
        g_gate_tick = GetTickCount64() - elapsed;
        RecordHook(kModel0, saved.data());
    };
    auto release = [&]() {
        manager[0x558 / 4] = stack[2];
        RecordHook(kVisualExit, saved.data());
        check(manager[0x558 / 4] == source_pointer && !g_tint_live,
              "original source restored after each intervention");
    };
    invoke(1000);
    check(stack[2] == source_pointer, "initial baseline is untouched");
    invoke(6000);
    check(stack[2] != source_pointer && reinterpret_cast<BYTE*>(stack[2])[5] == 0,
          "magenta cue survives detail saturation");
    release();
    invoke(9000);
    check(stack[2] == source_pointer, "normal comparison gap is untouched");
    invoke(20000);
    check(stack[2] != source_pointer && reinterpret_cast<BYTE*>(stack[2])[0] == 0xA1,
          "lighting mask survives detail saturation");
    check(reinterpret_cast<BYTE*>(stack[2])[5] == 120 && source == original,
          "lighting-off preserves RGB and original bytes");
    release();
    invoke(57000); check(stack[2] != source_pointer, "late off window remains active");
    release();
    invoke(59000); check(stack[2] == source_pointer, "post-window rendering is untouched");
    check(g_shading_phases[3].eligible == 2 && g_shading_phases[3].applied == 2 &&
          g_shading_phases[3].released == 2 && g_event_count == 0,
          "bounded phase evidence continues without semantic CSV growth");
    // No-op source must be reported, not substituted or called a lighting success.
    source[0] &= ~BYTE(6); invoke(30000);
    check(stack[2] == source_pointer && g_shading_phases[3].applied == 2,
          "already-unlit source is a no-op");
    source = original;
    manager[0x1ECC / 4] = 3; invoke(30000);
    check(stack[2] == source_pointer && g_shading_phases[3].applied == 2,
          "manager mode already suppressing lighting is a no-op");
    manager[0x1ECC / 4] = 0;
    saved[1] = reinterpret_cast<DWORD>(visual2.data());
    g_owners.observe(0x2000, saved[1], 120);
    invoke(30000); check(stack[2] == source_pointer, "second owner remains untouched");
    saved[1] = reinterpret_cast<DWORD>(visual.data());
    stack[0] = kKnownExceptionReturn;
    invoke(30000); check(stack[2] == source_pointer, "exception remains untouched");
    stack[0] = kVisualMainlineReturn;
    // Renderer-owned replacement survives release.
    invoke(31000); manager[0x558 / 4] = 0x12345678;
    RecordHook(kVisualExit, saved.data());
    check(manager[0x558 / 4] == 0x12345678 && !g_tint_live && g_tint_renderer_replaced == 1,
          "secondary renderer source not overwritten");
    // Optional ignored output permits an end-to-end production JSON/parser
    // check. This is labelled synthetic evidence, never gameplay evidence.
    if (argc == 2) {
        g_config.output_dir = argv[1];
        check(write_outputs(true), "production summary serialization succeeds");
    }
    // Fixed sample capacity cannot grow after saturation.
    g_shading_sample_count = 96;
    invoke(32000); g_running = 0; release(); g_running = 1;
    check(!g_tint_live, "stop request still permits shading lease drainage");
    check(g_shading_sample_count == 96, "sample ring is strictly bounded");
    // Fail-open on unreadable manager; no stack edit or live lease.
    const DWORD good_manager = stack[1]; stack[1] = 1;
    invoke(33000); check(stack[2] == source_pointer && !g_tint_live && g_tint_rejected == 1,
                          "invalid data fails open");
    stack[1] = good_manager;
    // Target retirement does not automatically transfer the effect to another owner.
    g_owners.retire_before(121, [](const auto&) {});
    g_owners.observe(0x1000, saved[1], 121);
    invoke(34000); check(stack[2] == source_pointer, "retired identity is never retargeted");
    // Configuration rejects incompatible intervention modes and hot geometry hook.
    std::array<wchar_t, MAX_PATH> temp{};
    GetTempPathW(static_cast<DWORD>(temp.size()), temp.data());
    const std::wstring config = std::wstring(temp.data()) + L"sfc-shading-config-" +
        std::to_wstring(GetCurrentProcessId()) + L".ini";
    WritePrivateProfileStringW(L"m1", L"OutputDirectory", temp.data(), config.c_str());
    WritePrivateProfileStringW(L"m1", L"EnableShadingOff", L"1", config.c_str());
    check(!load_config(config.c_str()), "geometry-enabled shading configuration refused");
    WritePrivateProfileStringW(L"m1", L"EnableGeometryHook", L"0", config.c_str());
    WritePrivateProfileStringW(L"m1", L"EnableVisualTint", L"1", config.c_str());
    check(!load_config(config.c_str()), "simultaneous modes refused");
    WritePrivateProfileStringW(L"m1", L"EnableVisualTint", L"0", config.c_str());
    check(load_config(config.c_str()), "valid shading configuration accepted");
    DeleteFileW(config.c_str());
    DeleteCriticalSection(&g_lock);
    std::cout << "All M1 production shading-off tests passed.\n";
}

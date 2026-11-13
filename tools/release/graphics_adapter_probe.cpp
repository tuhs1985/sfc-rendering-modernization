// Standalone x86 DirectDraw 7 fixture for the pinned wrapper. Never starts SFC.
#define WIN32_LEAN_AND_MEAN
#define DIRECTDRAW_VERSION 0x0700
#define DIRECT3D_VERSION 0x0700
#include <windows.h>
#include <ddraw.h>
#include <d3d.h>
#include <d3d11.h>
#include <dxgi1_6.h>
#include <wrl/client.h>
#include <reshade.hpp>
#include <bit>
#include <filesystem>
#include <iostream>
#include <stdexcept>

using Microsoft::WRL::ComPtr;
namespace fs = std::filesystem;

static void check(HRESULT result, const char* operation) {
    if (FAILED(result)) {
        std::cerr << operation << " failed, HRESULT=0x" << std::hex
                  << static_cast<unsigned long>(result) << '\n';
        throw std::runtime_error(operation);
    }
}

static void list_adapters() {
    ComPtr<IDXGIFactory1> factory;
    check(CreateDXGIFactory1(IID_PPV_ARGS(&factory)), "DXGI factory");
    for (UINT index = 0; index < 32; ++index) {
        ComPtr<IDXGIAdapter1> adapter;
        const auto result = factory->EnumAdapters1(index, &adapter);
        if (result == DXGI_ERROR_NOT_FOUND) break;
        check(result, "DXGI adapter");
        DXGI_ADAPTER_DESC1 desc{};
        check(adapter->GetDesc1(&desc), "DXGI adapter description");
        std::wcout << L"DXGI index=" << index << L" vendor=" << desc.VendorId
                   << L" device=" << desc.DeviceId << L" flags=" << desc.Flags
                   << L" luid=" << desc.AdapterLuid.HighPart << L':' << desc.AdapterLuid.LowPart
                   << L" name=" << desc.Description << L'\n';
    }
}

static void observe_device(reshade::api::device* device) {
    if (device->get_api() != reshade::api::device_api::d3d11) return;
    const auto native = reinterpret_cast<ID3D11Device*>(static_cast<uintptr_t>(device->get_native()));
    ComPtr<IDXGIDevice> dxgi;
    ComPtr<IDXGIAdapter> adapter;
    DXGI_ADAPTER_DESC desc{};
    if (SUCCEEDED(native->QueryInterface(IID_PPV_ARGS(&dxgi))) &&
        SUCCEEDED(dxgi->GetAdapter(&adapter)) && SUCCEEDED(adapter->GetDesc(&desc))) {
        std::wcout << L"WRAPPER_D3D11 luid=" << desc.AdapterLuid.HighPart << L':'
                   << desc.AdapterLuid.LowPart << L" name=" << desc.Description << L'\n';
    }
}

static void draw(const fs::path& fixture) {
    // Pin both modules to the fixture directory. ReShade logs the D3D11 GPU
    // created by the wrapper, which can differ from an emulated DD adapter name.
    constexpr auto search = LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR | LOAD_LIBRARY_SEARCH_SYSTEM32;
    const auto reshade_module = LoadLibraryExW((fixture/L"dxgi.dll").c_str(), nullptr, search);
    if (!reshade_module)
        throw std::runtime_error("load fixture ReShade");
    const auto module = GetModuleHandleW(nullptr);
    if (!reshade::register_addon(module, reshade_module))
        throw std::runtime_error("register fixture ReShade observer");
    reshade::register_event<reshade::addon_event::init_device>(observe_device);
    struct Observer {
        HMODULE module, reshade_module;
        ~Observer() {
            reshade::unregister_event<reshade::addon_event::init_device>(observe_device);
            reshade::unregister_addon(module, reshade_module);
        }
    } observer{module, reshade_module};
    const auto ddraw = LoadLibraryExW((fixture/L"DDraw.dll").c_str(), nullptr, search);
    if (!ddraw) throw std::runtime_error("load fixture DirectDraw");
    const auto create = std::bit_cast<decltype(&DirectDrawCreateEx)>(GetProcAddress(ddraw, "DirectDrawCreateEx"));
    if (!create) throw std::runtime_error("DirectDrawCreateEx export");

    WNDCLASSW wc{};
    wc.lpfnWndProc = DefWindowProcW;
    wc.hInstance = GetModuleHandleW(nullptr);
    wc.lpszClassName = L"SFCGraphicsAdapterProbe";
    if (!RegisterClassW(&wc)) throw std::runtime_error("register fixture window");
    const auto window = CreateWindowW(wc.lpszClassName, L"Graphics adapter probe", WS_POPUP,
                                      0, 0, 128, 128, nullptr, nullptr, wc.hInstance, nullptr);
    if (!window) throw std::runtime_error("create fixture window");
    try {
        ComPtr<IDirectDraw7> draw7;
        check(create(nullptr, reinterpret_cast<void**>(draw7.GetAddressOf()), IID_IDirectDraw7, nullptr),
              "DirectDraw device");
        check(draw7->SetCooperativeLevel(window, DDSCL_NORMAL), "DirectDraw cooperative level");
        ComPtr<IDirect3D7> d3d;
        check(draw7->QueryInterface(IID_IDirect3D7, reinterpret_cast<void**>(d3d.GetAddressOf())),
              "Direct3D7 interface");

        DDSURFACEDESC2 primary_desc{};
        primary_desc.dwSize = sizeof(primary_desc);
        primary_desc.dwFlags = DDSD_CAPS;
        primary_desc.ddsCaps.dwCaps = DDSCAPS_PRIMARYSURFACE;
        ComPtr<IDirectDrawSurface7> primary;
        check(draw7->CreateSurface(&primary_desc, &primary, nullptr), "DirectDraw primary");

        DDSURFACEDESC2 target_desc{};
        target_desc.dwSize = sizeof(target_desc);
        target_desc.dwFlags = DDSD_CAPS | DDSD_WIDTH | DDSD_HEIGHT;
        target_desc.dwWidth = target_desc.dwHeight = 128;
        target_desc.ddsCaps.dwCaps = DDSCAPS_OFFSCREENPLAIN | DDSCAPS_3DDEVICE | DDSCAPS_VIDEOMEMORY;
        ComPtr<IDirectDrawSurface7> target;
        check(draw7->CreateSurface(&target_desc, &target, nullptr), "DirectDraw target");

        ComPtr<IDirect3DDevice7> device;
        check(d3d->CreateDevice(IID_IDirect3DHALDevice, target.Get(), &device), "Direct3D7 HAL");
        check(device->Clear(0, nullptr, D3DCLEAR_TARGET, 0xff2a60a0, 1.f, 0), "Direct3D7 clear");
        RECT bounds{0, 0, 128, 128};
        check(primary->Blt(&bounds, target.Get(), nullptr, DDBLT_WAIT, nullptr), "DirectDraw primary blit");
    } catch (...) {
        DestroyWindow(window);
        throw;
    }
    DestroyWindow(window);
}

int wmain(int argc, wchar_t** argv) {
    try {
        if (argc != 2 || !fs::path(argv[1]).is_absolute()) return 2;
        list_adapters();
        draw(argv[1]);
        std::wcout << L"DIRECTDRAW_ADAPTER_PROBE_PASS\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}

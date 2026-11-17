// Standalone D3D9 reference for the observed main drone quad.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <d3d9.h>
#include <wrl/client.h>
#include <array>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <vector>

using Microsoft::WRL::ComPtr;
namespace fs = std::filesystem;
constexpr UINT Extent = 48, Atlas = 256;
struct Vertex { float x, y, z, rhw; DWORD diffuse, specular; float u, v; };
static_assert(sizeof(Vertex) == 32);

void checked(HRESULT hr, const char* operation) {
    if (SUCCEEDED(hr)) return;
    std::cerr << operation << " failed (0x" << std::hex << static_cast<DWORD>(hr) << ")\n";
    throw std::runtime_error(operation);
}

void configure(IDirect3DDevice9& device) {
    const std::pair<D3DRENDERSTATETYPE, DWORD> states[] = {
        {D3DRS_ZENABLE, TRUE}, {D3DRS_ZWRITEENABLE, FALSE}, {D3DRS_ZFUNC, D3DCMP_LESSEQUAL},
        {D3DRS_CULLMODE, D3DCULL_NONE}, {D3DRS_ALPHATESTENABLE, FALSE}, {D3DRS_ALPHAREF, 0},
        {D3DRS_ALPHAFUNC, D3DCMP_ALWAYS}, {D3DRS_ALPHABLENDENABLE, TRUE},
        {D3DRS_SRCBLEND, D3DBLEND_ONE}, {D3DRS_DESTBLEND, D3DBLEND_ONE}, {D3DRS_BLENDOP, D3DBLENDOP_ADD},
        {D3DRS_SRGBWRITEENABLE, FALSE}, {D3DRS_SPECULARENABLE, FALSE}, {D3DRS_DITHERENABLE, FALSE},
    };
    for (const auto& [key, value] : states) checked(device.SetRenderState(key, value), "draw state");
    const std::pair<D3DTEXTURESTAGESTATETYPE, DWORD> stages[] = {
        {D3DTSS_COLOROP, D3DTOP_MODULATE}, {D3DTSS_COLORARG1, D3DTA_TEXTURE}, {D3DTSS_COLORARG2, D3DTA_DIFFUSE},
        {D3DTSS_ALPHAOP, D3DTOP_SELECTARG1}, {D3DTSS_ALPHAARG1, D3DTA_TEXTURE}, {D3DTSS_ALPHAARG2, D3DTA_CURRENT},
    };
    for (const auto& [key, value] : stages) checked(device.SetTextureStageState(0, key, value), "texture stage");
    const std::pair<D3DSAMPLERSTATETYPE, DWORD> samplers[] = {
        {D3DSAMP_ADDRESSU, D3DTADDRESS_WRAP}, {D3DSAMP_ADDRESSV, D3DTADDRESS_WRAP},
        {D3DSAMP_MINFILTER, D3DTEXF_LINEAR}, {D3DSAMP_MAGFILTER, D3DTEXF_LINEAR},
        {D3DSAMP_MIPFILTER, D3DTEXF_NONE}, {D3DSAMP_SRGBTEXTURE, FALSE},
    };
    for (const auto& [key, value] : samplers) checked(device.SetSamplerState(0, key, value), "sampler state");
    checked(device.SetFVF(D3DFVF_XYZRHW | D3DFVF_DIFFUSE | D3DFVF_SPECULAR | D3DFVF_TEX1), "vertex format");
}

int wmain(int argc, wchar_t** argv) try {
    if (argc != 2) throw std::runtime_error("expected replay output folder");
    const fs::path folder = argv[1];
    std::array<Vertex, 4> vertices{};
    std::array<uint16_t, 6> indices{};
    std::vector<DWORD> atlas(size_t{Atlas} * Atlas);
    std::ifstream input(folder / "input.bin", std::ios::binary);
    if (!input.read(reinterpret_cast<char*>(vertices.data()), sizeof(vertices)) ||
        !input.read(reinterpret_cast<char*>(indices.data()), sizeof(indices)) ||
        !input.read(reinterpret_cast<char*>(atlas.data()), static_cast<std::streamsize>(atlas.size() * sizeof(DWORD))) ||
        input.peek() != EOF || indices != std::array<uint16_t, 6>{0, 1, 2, 0, 2, 3})
        throw std::runtime_error("invalid replay input");

    const HWND window = CreateWindowExW(0, L"STATIC", L"Drone replay", WS_POPUP,
                                        0, 0, Extent, Extent, nullptr, nullptr, nullptr, nullptr);
    if (!window) throw std::runtime_error("could not create replay window");
    ComPtr<IDirect3D9> api;
    api.Attach(Direct3DCreate9(D3D_SDK_VERSION));
    if (!api) throw std::runtime_error("Direct3D9 unavailable");
    D3DDISPLAYMODE mode{};
    checked(api->GetAdapterDisplayMode(0, &mode), "adapter display mode");
    D3DPRESENT_PARAMETERS pp{};
    pp.Windowed = TRUE; pp.SwapEffect = D3DSWAPEFFECT_DISCARD; pp.hDeviceWindow = window;
    pp.BackBufferWidth = Extent; pp.BackBufferHeight = Extent; pp.BackBufferFormat = mode.Format;
    ComPtr<IDirect3DDevice9> device;
    checked(api->CreateDevice(0, D3DDEVTYPE_HAL, window, D3DCREATE_SOFTWARE_VERTEXPROCESSING, &pp, &device), "D3D9 device");
    ComPtr<IDirect3DSurface9> target, depth, staging;
    checked(device->CreateRenderTarget(Extent, Extent, D3DFMT_A8R8G8B8, D3DMULTISAMPLE_NONE, 0, FALSE, &target, nullptr), "render target");
    checked(device->CreateDepthStencilSurface(Extent, Extent, D3DFMT_D24S8, D3DMULTISAMPLE_NONE, 0, TRUE, &depth, nullptr), "depth target");
    checked(device->SetRenderTarget(0, target.Get()), "set render target");
    checked(device->SetDepthStencilSurface(depth.Get()), "set depth target");
    checked(device->CreateOffscreenPlainSurface(Extent, Extent, D3DFMT_A8R8G8B8, D3DPOOL_SYSTEMMEM, &staging, nullptr), "readback surface");
    ComPtr<IDirect3DTexture9> texture;
    checked(device->CreateTexture(Atlas, Atlas, 1, 0, D3DFMT_A8R8G8B8, D3DPOOL_MANAGED, &texture, nullptr), "atlas texture");
    D3DLOCKED_RECT lock{};
    checked(texture->LockRect(0, &lock, nullptr, 0), "atlas upload");
    for (UINT y = 0; y < Atlas; ++y)
        std::memcpy(static_cast<char*>(lock.pBits) + y * lock.Pitch, atlas.data() + y * Atlas, Atlas * sizeof(DWORD));
    checked(texture->UnlockRect(0), "atlas unlock");
    configure(*device.Get());
    checked(device->SetTexture(0, texture.Get()), "bind atlas");

    const auto draw = [&](const auto& quad) {
        checked(device->DrawIndexedPrimitiveUP(D3DPT_TRIANGLELIST, 0, 4, 2, indices.data(), D3DFMT_INDEX16,
                                               quad.data(), sizeof(Vertex)), "indexed drone draw");
    };
    const auto render = [&](const wchar_t* name, const auto& quad, DWORD background, float clearDepth, bool repeat = false) {
        checked(device->Clear(0, nullptr, D3DCLEAR_TARGET | D3DCLEAR_ZBUFFER, background, clearDepth, 0), "clear");
        checked(device->BeginScene(), "begin replay scene");
        draw(quad);
        if (repeat) {
            auto further = quad;
            for (auto& vertex : further) vertex.z = 0.99f;
            draw(further);
        }
        checked(device->EndScene(), "end replay scene");
        checked(device->GetRenderTargetData(target.Get(), staging.Get()), "replay readback");
        checked(staging->LockRect(&lock, nullptr, D3DLOCK_READONLY), "readback lock");
        std::ofstream output(folder / name, std::ios::binary);
        for (UINT y = 0; y < Extent; ++y)
            output.write(static_cast<const char*>(lock.pBits) + y * lock.Pitch, Extent * sizeof(DWORD));
        output.close();
        checked(staging->UnlockRect(), "readback unlock");
        if (!output) throw std::runtime_error("replay output write failed");
    };
    render(L"raw-v.bgra", vertices, 0xff000000, 1.0f);
    for (auto& vertex : vertices) vertex.v = 1.0f - vertex.v;
    render(L"inverted-v.bgra", vertices, 0xff000000, 1.0f);
    render(L"destination.bgra", vertices, 0xff172b3d, 1.0f);
    render(L"occluded.bgra", vertices, 0xff172b3d, 0.95f);
    render(L"two-depths.bgra", vertices, 0xff000000, 1.0f, true);
    std::cout << "D3D9 HAL rendered five offline control cases\n";
    return 0;
} catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 1;
}

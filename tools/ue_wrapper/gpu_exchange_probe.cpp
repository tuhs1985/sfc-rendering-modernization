// Standalone qualification of the Windows GPU-sharing fallback. No game or UE hooks.
#include <windows.h>
#include <d3d11_4.h>
#include <d3d12.h>
#include <d3dcompiler.h>
#include <dxgi1_6.h>
#include <wrl/client.h>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <string>

using Microsoft::WRL::ComPtr;
constexpr UINT Size = 16;
constexpr UINT Frames = 4;
constexpr DWORD DeadlineMs = 5000;
constexpr std::array<DXGI_FORMAT, 3> Formats{
    DXGI_FORMAT_R8G8B8A8_UNORM, DXGI_FORMAT_R32_FLOAT, DXGI_FORMAT_R32_UINT};

struct Handle {
    HANDLE value{};
    ~Handle() { if (value) CloseHandle(value); }
    Handle() = default;
    explicit Handle(HANDLE v) : value(v) {}
    Handle(const Handle&) = delete;
    Handle& operator=(const Handle&) = delete;
};

void check(HRESULT result, const char* step) {
    if (FAILED(result)) {
        std::fprintf(stderr, "%s: HRESULT 0x%08lx\n", step, static_cast<unsigned long>(result));
        throw std::runtime_error(step);
    }
}

void require(bool condition, const char* step) {
    if (!condition) throw std::runtime_error(step);
}

std::array<float, 4> pixel(UINT plane, UINT frame) {
    if (plane == 0) return {frame % 2 ? 0.f : 1.f, frame % 2 ? 0.f : 1.f, 0.f, 1.f};
    if (plane == 1) return {frame * 0.125f, 0.f, 0.f, 0.f};
    return {float(4096 + frame), 0.f, 0.f, 0.f};
}

template<class Fence>
void completed(Fence* fence, UINT64 value, HANDLE event) {
    check(fence->SetEventOnCompletion(value, event), "SetEventOnCompletion");
    require(WaitForSingleObject(event, DeadlineMs) == WAIT_OBJECT_0, "GPU fence deadline");
    const UINT64 reached = fence->GetCompletedValue();
    require(reached != UINT64_MAX && reached >= value, "Invalid GPU fence value");
}

template<UINT SlotCount = 1>
int consume(wchar_t** args) {
    const LUID luid{static_cast<DWORD>(std::stoul(args[2])), std::stol(args[3])};
    ComPtr<IDXGIFactory4> factory;
    check(CreateDXGIFactory1(IID_PPV_ARGS(&factory)), "CreateDXGIFactory1");
    ComPtr<IDXGIAdapter> adapter;
    check(factory->EnumAdapterByLuid(luid, IID_PPV_ARGS(&adapter)), "EnumAdapterByLuid");
    ComPtr<ID3D11Device> base;
    ComPtr<ID3D11DeviceContext> context;
    check(D3D11CreateDevice(adapter.Get(), D3D_DRIVER_TYPE_UNKNOWN, nullptr, 0,
                            nullptr, 0, D3D11_SDK_VERSION, &base, nullptr, &context),
          "D3D11CreateDevice");
    ComPtr<ID3D11Device5> device;
    ComPtr<ID3D11DeviceContext4> queue;
    check(base.As(&device), "D3D11 device fences");
    check(context.As(&queue), "D3D11 context fences");
    std::array<ComPtr<ID3D11Texture2D>, 3 * SlotCount> input, staging;
    for (UINT i = 0; i < input.size(); ++i) {
        Handle shared(reinterpret_cast<HANDLE>(std::stoull(args[4+i])));
        check(device->OpenSharedResource1(shared.value, IID_PPV_ARGS(&input[i])), "OpenSharedResource1");
        D3D11_TEXTURE2D_DESC desc{};
        input[i]->GetDesc(&desc);
        require(desc.Format == Formats[i % 3] && desc.Width == Size && desc.Height == Size &&
                desc.MipLevels == 1 && desc.ArraySize == 1 && desc.SampleDesc.Count == 1,
                "Wrong texture descriptor");
        desc.Usage = D3D11_USAGE_STAGING;
        desc.BindFlags = desc.MiscFlags = 0;
        desc.CPUAccessFlags = D3D11_CPU_ACCESS_READ;
        check(device->CreateTexture2D(&desc, nullptr, &staging[i]), "Create staging texture");
    }
    Handle readyHandle(reinterpret_cast<HANDLE>(std::stoull(args[4 + 3 * SlotCount])));
    Handle ackHandle(reinterpret_cast<HANDLE>(std::stoull(args[5 + 3 * SlotCount])));
    ComPtr<ID3D11Fence> ready, ack;
    check(device->OpenSharedFence(readyHandle.value, IID_PPV_ARGS(&ready)), "Open producer fence");
    check(device->OpenSharedFence(ackHandle.value, IID_PPV_ARGS(&ack)), "Open consumer fence");
    Handle event(CreateEventW(nullptr, FALSE, FALSE, nullptr));
    require(event.value != nullptr, "Create consumer event");
    constexpr UINT FrameCount = SlotCount == 2 ? 12 : Frames;
    for (UINT frame = 1; frame <= FrameCount; ++frame) {
        const UINT slot = (frame - 1) % SlotCount;
        check(queue->Wait(ready.Get(), frame), "D3D11 GPU wait");
        if constexpr (SlotCount == 2) {
            // Force both slots to be occupied before the first acknowledgement.
            if (frame == 1) {
                completed(ready.Get(), 2, event.value);
                Sleep(100); // Explicit slow-consumer fixture, never normal play.
            }
        }
        for (UINT i = 0; i < Formats.size(); ++i)
            queue->CopyResource(staging[slot * 3 + i].Get(), input[slot * 3 + i].Get());
        check(queue->Signal(ack.Get(), frame), "D3D11 GPU acknowledgement");
        queue->Flush();
        completed(ack.Get(), frame, event.value);
        // Diagnostic readback only, after the GPU transfer and completion.
        for (UINT i = 0; i < Formats.size(); ++i) {
            D3D11_MAPPED_SUBRESOURCE data{};
            const auto deadline = GetTickCount64() + DeadlineMs;
            HRESULT mapped;
            do {
                mapped = queue->Map(staging[slot * 3 + i].Get(), 0, D3D11_MAP_READ,
                                    D3D11_MAP_FLAG_DO_NOT_WAIT, &data);
                if (mapped != DXGI_ERROR_WAS_STILL_DRAWING) break;
                Sleep(1);
            } while (GetTickCount64() < deadline);
            check(mapped, "Map verification staging texture");
            const auto expected = pixel(i, frame);
            uint32_t bits = i == 0 ? (frame % 2 ? 0xff000000u : 0xff00ffffu) : uint32_t(expected[0]);
            if (i == 1) std::memcpy(&bits, &expected[0], sizeof(bits));
            bool correct = true;
            for (UINT y = 0; y < Size; ++y) {
                const auto* row = reinterpret_cast<const uint32_t*>(
                    static_cast<const uint8_t*>(data.pData) + y * data.RowPitch);
                for (UINT x = 0; x < Size; ++x) correct &= row[x] == bits;
            }
            queue->Unmap(staging[slot * 3 + i].Get(), 0);
            require(correct, "Wrong frame pixels");
        }
        std::printf("D3D11 frame %u: all three %ux%u planes match\n", frame, Size, Size);
    }
    return 0;
}

template<UINT SlotCount = 1>
int produce(bool disconnect) {
    ComPtr<ID3D12Device> device;
    check(D3D12CreateDevice(nullptr, D3D_FEATURE_LEVEL_11_0, IID_PPV_ARGS(&device)), "D3D12CreateDevice");
    const LUID luid = device->GetAdapterLuid();
    D3D12_COMMAND_QUEUE_DESC qdesc{};
    ComPtr<ID3D12CommandQueue> queue;
    check(device->CreateCommandQueue(&qdesc, IID_PPV_ARGS(&queue)), "Create producer queue");
    D3D12_DESCRIPTOR_HEAP_DESC hdesc{D3D12_DESCRIPTOR_HEAP_TYPE_RTV, UINT(Formats.size() * SlotCount)};
    ComPtr<ID3D12DescriptorHeap> rtv;
    check(device->CreateDescriptorHeap(&hdesc, IID_PPV_ARGS(&rtv)), "Create RTV heap");
    std::array<ComPtr<ID3D12Resource>, 3 * SlotCount> textures;
    std::array<D3D12_CPU_DESCRIPTOR_HANDLE, 3 * SlotCount> views{};
    std::array<Handle, 3 * SlotCount + 2> handles;
    SECURITY_ATTRIBUTES inherit{sizeof(inherit), nullptr, TRUE};
    for (UINT i = 0; i < textures.size(); ++i) {
        D3D12_HEAP_PROPERTIES heap{};
        heap.Type = D3D12_HEAP_TYPE_DEFAULT;
        heap.CreationNodeMask = heap.VisibleNodeMask = 1;
        D3D12_RESOURCE_DESC desc{};
        desc.Dimension = D3D12_RESOURCE_DIMENSION_TEXTURE2D;
        desc.Width = desc.Height = Size;
        desc.DepthOrArraySize = desc.MipLevels = 1;
        desc.Format = Formats[i % 3];
        desc.SampleDesc.Count = 1;
        desc.Flags = D3D12_RESOURCE_FLAG_ALLOW_RENDER_TARGET | D3D12_RESOURCE_FLAG_ALLOW_SIMULTANEOUS_ACCESS;
        check(device->CreateCommittedResource(&heap, D3D12_HEAP_FLAG_SHARED, &desc,
              D3D12_RESOURCE_STATE_COMMON, nullptr, IID_PPV_ARGS(&textures[i])), "Create shared texture");
        check(device->CreateSharedHandle(textures[i].Get(), &inherit, GENERIC_ALL, nullptr, &handles[i].value), "Export shared texture");
        views[i] = rtv->GetCPUDescriptorHandleForHeapStart();
        views[i].ptr += i * device->GetDescriptorHandleIncrementSize(D3D12_DESCRIPTOR_HEAP_TYPE_RTV);
        device->CreateRenderTargetView(textures[i].Get(), nullptr, views[i]);
    }
    ComPtr<ID3D12Fence> ready, ack;
    check(device->CreateFence(0, D3D12_FENCE_FLAG_SHARED, IID_PPV_ARGS(&ready)), "Create ready fence");
    check(device->CreateFence(0, D3D12_FENCE_FLAG_SHARED, IID_PPV_ARGS(&ack)), "Create ack fence");
    check(device->CreateSharedHandle(ready.Get(), &inherit, GENERIC_ALL, nullptr, &handles[3 * SlotCount].value), "Export ready fence");
    check(device->CreateSharedHandle(ack.Get(), &inherit, GENERIC_ALL, nullptr, &handles[3 * SlotCount + 1].value), "Export ack fence");
    // Restrict the child to exactly these inherited handles.
    std::array<HANDLE, 3 * SlotCount + 2> inherited{};
    for (size_t i = 0; i < inherited.size(); ++i) inherited[i] = handles[i].value;
    SIZE_T bytes = 0;
    InitializeProcThreadAttributeList(nullptr, 1, 0, &bytes);
    struct Attributes {
        LPPROC_THREAD_ATTRIBUTE_LIST list{};
        bool initialized{};
        ~Attributes() {
            if (initialized) DeleteProcThreadAttributeList(list);
            if (list) HeapFree(GetProcessHeap(), 0, list);
        }
    } attributes;
    attributes.list = static_cast<LPPROC_THREAD_ATTRIBUTE_LIST>(HeapAlloc(GetProcessHeap(), 0, bytes));
    require(attributes.list && InitializeProcThreadAttributeList(attributes.list, 1, 0, &bytes), "Initialize child handle list");
    attributes.initialized = true;
    require(UpdateProcThreadAttribute(attributes.list, 0, PROC_THREAD_ATTRIBUTE_HANDLE_LIST,
                                     inherited.data(), sizeof(inherited), nullptr, nullptr), "Set child handle list");
    wchar_t exe[32768]{};
    const auto len = GetModuleFileNameW(nullptr, exe, UINT(std::size(exe)));
    require(len > 0 && len < std::size(exe), "Get fixture executable path");
    std::wstring cmd = L"\"" + std::wstring(exe) +
                       (disconnect ? L"\" --disconnect " : SlotCount == 2 ? L"\" --consume-pool " : L"\" --consume ") +
                       std::to_wstring(luid.LowPart) + L" " + std::to_wstring(luid.HighPart);
    for (auto value : inherited) cmd += L" " + std::to_wstring(reinterpret_cast<uintptr_t>(value));
    STARTUPINFOEXW startup{};
    startup.StartupInfo.cb = sizeof(startup);
    startup.lpAttributeList = attributes.list;
    PROCESS_INFORMATION info{};
    require(CreateProcessW(exe, cmd.data(), nullptr, nullptr, TRUE, EXTENDED_STARTUPINFO_PRESENT,
                           nullptr, nullptr, &startup.StartupInfo, &info), "Create D3D11 process");
    Handle process(info.hProcess), thread(info.hThread);
    Handle event(CreateEventW(nullptr, FALSE, FALSE, nullptr));
    require(event.value != nullptr, "Create producer event");
    constexpr UINT FrameCount = SlotCount == 2 ? 12 : Frames;
    UINT peakOutstanding = 0;
    for (UINT frame = 1; frame <= FrameCount; ++frame) {
        const UINT slot = (frame - 1) % SlotCount;
        if (frame > SlotCount)
            require(ack->GetCompletedValue() >= frame - SlotCount, "Slot overwritten before consumer completion");
        ComPtr<ID3D12CommandAllocator> allocator;
        ComPtr<ID3D12GraphicsCommandList> list;
        check(device->CreateCommandAllocator(D3D12_COMMAND_LIST_TYPE_DIRECT, IID_PPV_ARGS(&allocator)), "Create allocator");
        check(device->CreateCommandList(0, D3D12_COMMAND_LIST_TYPE_DIRECT, allocator.Get(), nullptr, IID_PPV_ARGS(&list)), "Create command list");
        for (UINT i = 0; i < Formats.size(); ++i) {
            D3D12_RESOURCE_BARRIER barrier{};
            barrier.Type = D3D12_RESOURCE_BARRIER_TYPE_TRANSITION;
            barrier.Transition = {textures[slot * 3 + i].Get(), D3D12_RESOURCE_BARRIER_ALL_SUBRESOURCES,
                                  D3D12_RESOURCE_STATE_COMMON, D3D12_RESOURCE_STATE_RENDER_TARGET};
            list->ResourceBarrier(1, &barrier);
            list->ClearRenderTargetView(views[slot * 3 + i], pixel(i, frame).data(), 0, nullptr);
            std::swap(barrier.Transition.StateBefore, barrier.Transition.StateAfter);
            list->ResourceBarrier(1, &barrier);
        }
        check(list->Close(), "Close command list");
        ID3D12CommandList* submit[]{list.Get()};
        queue->ExecuteCommandLists(1, submit);
        check(queue->Signal(ready.Get(), frame), "D3D12 GPU publication");
        // This test uses one slot, so wait for its GPU read before overwriting it.
        completed(ready.Get(), frame, event.value);
        const UINT64 acknowledged = ack->GetCompletedValue();
        require(acknowledged != UINT64_MAX && acknowledged <= frame, "Invalid consumer timeline");
        peakOutstanding = max(peakOutstanding, frame - UINT(acknowledged));
        if (frame < SlotCount) continue;
        const UINT64 requiredAck = frame - SlotCount + 1;
        check(ack->SetEventOnCompletion(requiredAck, event.value), "Arm acknowledgement");
        HANDLE waits[]{event.value, process.value};
        const DWORD outcome = WaitForMultipleObjects(2, waits, FALSE, DeadlineMs);
        if (disconnect) {
            require(outcome == WAIT_OBJECT_0 + 1 && ack->GetCompletedValue() == 0,
                    "Disconnected consumer acknowledged output or failed to exit");
            DWORD code{};
            require(GetExitCodeProcess(process.value, &code) && code == 0,
                    "Unexpected disconnect fixture exit");
            std::puts("PASS: early disconnect leaves the slot unacknowledged");
            return 0;
        }
        require(outcome == WAIT_OBJECT_0 &&
                ack->GetCompletedValue() >= requiredAck, "Consumer disconnected or missed acknowledgement");
    }
    require(WaitForSingleObject(process.value, DeadlineMs) == WAIT_OBJECT_0, "Consumer exit timeout");
    DWORD code{};
    require(GetExitCodeProcess(process.value, &code) && code == 0, "Consumer verification failed");
    require(ack->GetCompletedValue() == FrameCount, "Final consumer reads not complete");
    if constexpr (SlotCount == 2) require(peakOutstanding == 2, "Two-slot occupancy not exercised");
    std::printf("PASS: %u DX12-to-D3D11 cross-process frames, %u slots, peak outstanding %u, same LUID %08lx:%08lx\n",
                FrameCount, SlotCount, peakOutstanding, static_cast<unsigned long>(luid.HighPart), static_cast<unsigned long>(luid.LowPart));
    return 0;
}



void convertDepth(ID3D11Device* device, ID3D11DeviceContext* context,
                  ID3D11Texture2D* input, float p22, float p23, UINT owner,
                  const wchar_t* outputName) {
    const char* shader=R"(
cbuffer Parameters:register(b0){float p22;float p23;uint owner;uint pad;};
Texture2D<float> linearDepth:register(t0);
RWTexture2D<float> nativeDepth:register(u0);
RWTexture2D<float> owners:register(u1);
[numthreads(8,8,1)] void main(uint3 p:SV_DispatchThreadID){
 uint width,height;linearDepth.GetDimensions(width,height);
 if(p.x>=width||p.y>=height)return;
 float d=linearDepth[p.xy];
 float z=-p22+p23/d;
 bool covered=isfinite(d)&&d>0&&isfinite(z)&&z>=0&&z<1;
 nativeDepth[p.xy]=covered?z:-1234;
 owners[p.xy]=asfloat(covered?owner:0);
})";
    ComPtr<ID3DBlob> blob,error;
    check(D3DCompile(shader,std::strlen(shader),nullptr,nullptr,nullptr,"main","cs_5_0",
                     D3DCOMPILE_ENABLE_STRICTNESS,0,&blob,&error),"Compile depth conversion");
    ComPtr<ID3D11ComputeShader> compute;
    check(device->CreateComputeShader(blob->GetBufferPointer(),blob->GetBufferSize(),nullptr,&compute),"Create depth conversion");
    D3D11_TEXTURE2D_DESC desc{};
    input->GetDesc(&desc);
    ComPtr<ID3D11ShaderResourceView> source;
    check(device->CreateShaderResourceView(input,nullptr,&source),"View linear depth");
    std::array<ComPtr<ID3D11Texture2D>,2> targets,staging;
    std::array<ComPtr<ID3D11UnorderedAccessView>,2> views;
    desc.BindFlags=D3D11_BIND_UNORDERED_ACCESS;
    desc.MiscFlags=0;
    for(UINT i=0;i<2;++i){
        check(device->CreateTexture2D(&desc,nullptr,&targets[i]),"Create converted output");
        check(device->CreateUnorderedAccessView(targets[i].Get(),nullptr,&views[i]),"View converted output");
    }
    struct Constants{float p22,p23;UINT owner,pad;} constants{p22,p23,owner,0};
    D3D11_BUFFER_DESC buffer{};
    buffer.ByteWidth=sizeof(constants);buffer.BindFlags=D3D11_BIND_CONSTANT_BUFFER;
    D3D11_SUBRESOURCE_DATA data{&constants};
    ComPtr<ID3D11Buffer> cb;
    check(device->CreateBuffer(&buffer,&data,&cb),"Create conversion constants");
    context->CSSetShader(compute.Get(),nullptr,0);
    auto* srv=source.Get();context->CSSetShaderResources(0,1,&srv);
    ID3D11UnorderedAccessView* uav[]{views[0].Get(),views[1].Get()};
    context->CSSetUnorderedAccessViews(0,2,uav,nullptr);
    auto* c=cb.Get();context->CSSetConstantBuffers(0,1,&c);
    context->Dispatch((desc.Width+7)/8,(desc.Height+7)/8,1);
    context->ClearState();
    desc.Usage=D3D11_USAGE_STAGING;desc.BindFlags=0;desc.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
    for(UINT i=0;i<2;++i){
        check(device->CreateTexture2D(&desc,nullptr,&staging[i]),"Create conversion staging");
        context->CopyResource(staging[i].Get(),targets[i].Get());
    }
    context->Flush();
    for(UINT i=0;i<2;++i){
        D3D11_MAPPED_SUBRESOURCE map{};
        HRESULT hr;
        const auto deadline=GetTickCount64()+DeadlineMs;
        do{
            hr=context->Map(staging[i].Get(),0,D3D11_MAP_READ,D3D11_MAP_FLAG_DO_NOT_WAIT,&map);
            if(hr!=DXGI_ERROR_WAS_STILL_DRAWING)break;
            Sleep(1);
        }while(GetTickCount64()<deadline);
        check(hr,"Read converted diagnostic");
        const std::wstring path=std::wstring(outputName)+(i?L".owners":L".native");
        FILE* out=nullptr;
        bool good=_wfopen_s(&out,path.c_str(),L"wb")==0&&out;
        if(good){
            for(UINT y=0;y<desc.Height;++y)
                good=good&&std::fwrite(static_cast<const uint8_t*>(map.pData)+y*map.RowPitch,4,desc.Width,out)==desc.Width;
            good=std::fclose(out)==0&&good;
        }
        context->Unmap(staging[i].Get(),0);
        require(good,"Write converted diagnostic");
    }
}

int consumeUE(wchar_t** args, bool convert) {
    wchar_t fault[32]{};
    GetEnvironmentVariableW(L"SFC_GPU_PROBE_FAULT",fault,UINT(std::size(fault)));
    if(std::wcscmp(fault,L"exit-before-import")==0) return 7;
    if(std::wcscmp(fault,L"stall-before-import")==0) Sleep(30000);
    const DWORD pid=std::stoul(args[2]);
    const uintptr_t handle=std::stoull(args[3]);
    const LUID luid{static_cast<DWORD>(std::stoul(args[4])),std::stol(args[5])};
    Handle parent(OpenProcess(PROCESS_DUP_HANDLE,FALSE,pid)), texture;
    require(parent.value!=nullptr,"Open UE producer");
    require(DuplicateHandle(parent.value,reinterpret_cast<HANDLE>(handle),GetCurrentProcess(),
                            &texture.value,0,FALSE,DUPLICATE_SAME_ACCESS),"Duplicate UE shared texture");
    ComPtr<IDXGIFactory4> factory;
    ComPtr<IDXGIAdapter> adapter;
    ComPtr<ID3D11Device> base;
    ComPtr<ID3D11DeviceContext> context;
    ComPtr<ID3D11Device1> device;
    ComPtr<ID3D11Texture2D> input,staging;
    check(CreateDXGIFactory1(IID_PPV_ARGS(&factory)),"Create factory");
    check(factory->EnumAdapterByLuid(luid,IID_PPV_ARGS(&adapter)),"Match UE adapter");
    check(D3D11CreateDevice(adapter.Get(),D3D_DRIVER_TYPE_UNKNOWN,nullptr,0,nullptr,0,
                           D3D11_SDK_VERSION,&base,nullptr,&context),"Create D3D11 consumer");
    check(base.As(&device),"D3D11 NT handle support");
    check(device->OpenSharedResource1(texture.value,IID_PPV_ARGS(&input)),"Import UE texture");
    ComPtr<ID3D11Device5> modern;
    ComPtr<ID3D11DeviceContext4> queue;
    ComPtr<ID3D11Fence> ready,ack;
    check(device.As(&modern),"Import shared fence support");
    check(context.As(&queue),"Consumer GPU queue support");
    Handle readyHandle,ackHandle;
    require(DuplicateHandle(parent.value,reinterpret_cast<HANDLE>(std::stoull(args[7])),GetCurrentProcess(),
                            &readyHandle.value,0,FALSE,DUPLICATE_SAME_ACCESS),"Duplicate producer fence");
    require(DuplicateHandle(parent.value,reinterpret_cast<HANDLE>(std::stoull(args[8])),GetCurrentProcess(),
                            &ackHandle.value,0,FALSE,DUPLICATE_SAME_ACCESS),"Duplicate acknowledgement fence");
    check(modern->OpenSharedFence(readyHandle.value,IID_PPV_ARGS(&ready)),"Import producer fence");
    check(modern->OpenSharedFence(ackHandle.value,IID_PPV_ARGS(&ack)),"Import acknowledgement fence");
    check(queue->Wait(ready.Get(),1),"Wait for UE on GPU");
    if(convert) convertDepth(device.Get(),context.Get(),input.Get(),std::stof(args[9]),std::stof(args[10]),std::stoul(args[11]),args[6]);
    D3D11_TEXTURE2D_DESC desc{};
    input->GetDesc(&desc);
    require((desc.Format==DXGI_FORMAT_B8G8R8A8_UNORM||desc.Format==DXGI_FORMAT_R32_FLOAT)&&desc.Width>0&&desc.Height>0&&
            desc.Width<=4096&&desc.Height<=4096&&desc.SampleDesc.Count==1&&
            desc.MipLevels==1&&desc.ArraySize==1,"UE output descriptor");
    desc.Usage=D3D11_USAGE_STAGING;desc.BindFlags=desc.MiscFlags=0;
    desc.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
    check(device->CreateTexture2D(&desc,nullptr,&staging),"Create diagnostic staging");
    context->CopyResource(staging.Get(),input.Get());context->Flush();
    D3D11_MAPPED_SUBRESOURCE map{};
    HRESULT hr;
    const auto deadline=GetTickCount64()+DeadlineMs;
    do {
        hr=context->Map(staging.Get(),0,D3D11_MAP_READ,D3D11_MAP_FLAG_DO_NOT_WAIT,&map);
        if(hr!=DXGI_ERROR_WAS_STILL_DRAWING)break;
        Sleep(1);
    }while(GetTickCount64()<deadline);
    check(hr,"Read diagnostic pixels");
    FILE* output=nullptr;
    const errno_t opened=_wfopen_s(&output,args[6],L"wb");
    bool good=opened==0&&output;
    if(good) {
        for(UINT y=0;y<desc.Height;++y)
            good=good&&fwrite(static_cast<const uint8_t*>(map.pData)+y*map.RowPitch,4,desc.Width,output)==desc.Width;
        good=fclose(output)==0&&good;
    }
    context->Unmap(staging.Get(),0);
    require(good,"Write diagnostic pixels");
    const UINT64 ackValue=std::wcscmp(fault,L"wrong-ack")==0?2:1;
    check(queue->Signal(ack.Get(),ackValue),"Release UE GPU read lease");
    queue->Flush();
    Handle event(CreateEventW(nullptr,FALSE,FALSE,nullptr));
    require(event.value!=nullptr,"Create GPU acknowledgement event");
    completed(ack.Get(),ackValue,event.value);
    return 0;
}

int wmain(int count, wchar_t** args) {
    try {
        if ((count == 9 || count == 12) && std::wcscmp(args[1], L"--ue-consume") == 0) return consumeUE(args,count==12);
        if (count == 1) return produce<>(false);
        if (count == 2 && std::wcscmp(args[1], L"--check-pool") == 0) return produce<2>(false);
        if (count == 2 && std::wcscmp(args[1], L"--check-pool-disconnect") == 0) return produce<2>(true);
        if (count == 2 && std::wcscmp(args[1], L"--check-disconnect") == 0)
            return produce<>(true);
        if (count == 12 && std::wcscmp(args[1], L"--consume-pool") == 0) return consume<2>(args);
        if (count == 9 && std::wcscmp(args[1], L"--consume") == 0) return consume<>(args);
        if ((count == 9 || count == 12) && std::wcscmp(args[1], L"--disconnect") == 0) return 0;
        return 2;
    } catch (const std::exception& error) {
        std::fprintf(stderr, "GPU exchange probe failed: %s\n", error.what());
        return 1;
    }
}

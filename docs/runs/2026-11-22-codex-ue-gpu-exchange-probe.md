# Standalone DX12-to-D3D11 exchange probe

November 22, 2026. OpenSpec change `ue-native-insertion`, tasks 2.1 and 2.2
remain open. This probes the Windows boundary independently of Unreal and SFC.

## Epic Texture Share review

The pinned UE 5.8.4 installation has the Win64 SDK DLL, import library, and
DX11/DX12 sample source under `Engine/Extras/VirtualProduction/TextureShare`.
The plugin's `TextureShareResourcesProxy.cpp` calls
`ImmediateFlush(FlushRHIThreadFlushResources)`. Its interprocess step barriers
coordinate CPU participants. The reviewed public plugin and SDK interfaces
expose resource exchange and frame synchronization without an explicit
GPU-completion or consumer-read fence contract. Keep this route unqualified
for release of a reuse lease. No Epic exchange was executed in this increment.
See [Epic Texture Share](https://dev.epicgames.com/documentation/en-us/unreal-engine/texture-share-in-unreal-engine).

## Windows experiment

[Fixture source](../../tools/ue_wrapper/gpu_exchange_probe.cpp). Build x64 from
a Visual Studio developer prompt at the repository root.

```cmd
mkdir artifacts\ue-foundation\gpu-exchange
cl /nologo /std:c++17 /EHsc /W4 /WX /O2 /Foartifacts\ue-foundation\gpu-exchange\gpu_exchange_probe.obj /Feartifacts\ue-foundation\gpu-exchange\gpu_exchange_probe.exe tools\ue_wrapper\gpu_exchange_probe.cpp d3d11.lib d3d12.lib dxgi.lib
artifacts\ue-foundation\gpu-exchange\gpu_exchange_probe.exe
artifacts\ue-foundation\gpu-exchange\gpu_exchange_probe.exe --check-disconnect
```

The DX12 producer shares one set of RGBA8 UNORM, R32_FLOAT and R32_UINT
16×16 textures and two fences. It passes exactly five unnamed handles to
its child through the inherited handle list. The D3D11 child selects the
adapter by the producer's LUID, verifies descriptors and opens the same
resources and fences. The producer clears all planes on the GPU with
different values each frame, including opaque black. The child queues a GPU
wait, copies all planes and signals its acknowledgement. The producer
waits for that acknowledgement before reusing the slot. CPU pixel readback
exists only in the child fixture to verify the completed transfers.
See [Microsoft sharing handles](https://learn.microsoft.com/en-us/windows/win32/api/d3d12/nf-d3d12-id3d12device-createsharedhandle)
and [shared fence import](https://learn.microsoft.com/en-us/windows/win32/api/d3d11_4/nf-d3d11_4-id3d11device5-opensharedfence).

Five four-frame runs passed on the RTX 4070 Ti, LUID 00000000:00016223.
All 15,360 pixel values matched. The early-disconnect run observed child
exit before any acknowledgement and did not reuse the slot. An initial
one-shot diagnostic Map returned DXGI_ERROR_WAS_STILL_DRAWING despite the
observed acknowledgement. The fixture now retries the nonblocking staging
Map within a bounded diagnostic deadline. Logs and executable remain under
`artifacts/ue-foundation/gpu-exchange/`.

This establishes Windows interop on this machine. The tiny synthetic pixels
do not qualify UE render-target export, real physical depth or packed owner
coverage, two-slot policy, timing under real load, resize, or stop with a GPU
read in flight. No SFC game files or clients were used.

Next, connect one actual UE DX12 target through public RHI into a shared
texture and verify the producer's GPU completion before admitting its
matching D3D11 output. Keep the fixture as the independent transport oracle.

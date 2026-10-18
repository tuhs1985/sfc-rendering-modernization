// Backend-specific adapter, NOT part of the SFC capture/scene contract.
#pragma once
namespace sfc_remix_adapter {
// Run37/BLENDER-UV-COMPARE-001: captured/accepted OBJ coordinates sample a
// bottom-origin image; our pinned Remix SDK + unchanged DDS samples top-origin.
// Convert exactly once, only while constructing Remix SDK vertices. Keep raw
// packets, live-mesh.bin, OBJ, source images and other backend inputs unchanged.
// A future D3D9/D3D12 adapter MUST qualify its own convention, not inherit this
// rule merely because it uses DirectX. This is adapter policy, not a Remix bug.
constexpr float textureV(float capturedV) noexcept { return 1.0f-capturedV; }
}

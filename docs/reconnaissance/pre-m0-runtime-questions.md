# Pre-M0 Runtime-Question Backlog

This backlog prepares later, sponsor-authorized experiments. It does not
authorize runtime probing, executable patching, hooks, or wrapper installation.

## Priority 0 — resolve the legacy render boundary

1. **What are the exact COM interface identities at wrapper offsets
   +0x30..+0x4C?**  
   Static target: constructor/release 0x006A7C20/0x006A7C60, manager setup
   0x0069D3F0. Success criterion: map every queried IID and vtable method
   without relying on offset-name guesses.
2. **Which function owns BeginScene, EndScene, primitive submission, and
   presentation?**  
   Static candidates: 0x006A84B0, 0x006A8500,
   0x0069EB90–0x0069EFFF, 0x006B38C0, 0x006B3A30. Success criterion:
   establish call order and per-frame frequency for flip and blit modes.
3. **Who invokes mSwapBuffers or mCopyToFront each frame?**  
   Static direct calls are absent, suggesting method-table dispatch. Success
   criterion: identify the dispatch owner and mode-selection condition.
4. **Which function submits ship geometry?**  
   Trace backward from the confirmed/candidate COM draw methods and forward from
   the ship/model clusters. Success criterion: one corroborated call chain from
   a known ship instance to a draw call.

## Priority 1 — map scene identity and state

5. **Where does a gameplay ship become a renderable object, and does stable
   identity persist across frames?**  
   Start at 0x0041C271 and model parser 0x0042FEF9; compare object pointers
   observed at candidate submission calls.
6. **Where are model and material pointers attached?**  
   Correlate the 0x0042D6EC–0x00430367 model/material cluster with
   submission-time object state and documented .mod LOD/material semantics.
7. **Where are view/projection/world matrices assembled and cached?**  
   Start from camera control 0x0048CA35 and D3D manager arrays at
   +0x3C58/+0x3D54/+0x3E50; do not assume those arrays are matrices without
   observing writes and device calls.
8. **How is z-buffer state created and attached?**  
   Start from 0x0040AD35, surface creation 0x006B3BC0, and buffer
   initialization 0x006B4540. Determine format, lifetime, and device linkage.
9. **Where does Q3 sprite data become batched/drawn effects?**  
   Follow the confirmed loader at 0x006770A0 through its caller families to
   the graphics wrapper.

## Priority 2 — resilience and alternate paths

10. **Which conditions select hardware D3D, GDI/software, flip, or blit paths?**
    Correlate configuration with 0x006B2520–0x006B2FFF,
    0x006B38C0, and 0x006B3A30.
11. **How do display changes and device/surface loss alter object lifetime?**
    Exercise only in a disposable, approved runtime copy; observe
    0x006B4360, 0x006B4460, and the restore branches.
12. **Which transform, lighting, texture, and material states are redundantly
    cached by the large manager?**  
    Begin only after interface identity is established; classify writes rather
    than guessing from the object size.

## Recommended experiment order after CDD baseline

First reconstruct the wrapper interfaces and vtables statically. Then perform a
minimal non-mutating call-order trace at scene/present candidates. Only after
that should work trace a single known ship and one sprite effect forward to
submission. This sequence answers whether CTE-1 has a stable legacy render
access boundary before any architecture decision is considered.


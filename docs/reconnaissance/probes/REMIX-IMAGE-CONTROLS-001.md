# REMIX-IMAGE-CONTROLS-001 — offline image-control qualification

Question: which pinned native tone-mapping controls affect FINAL_COLOR, and does
the narrow host GPU fallback provide missing local grade/gamma without changing
original SFC rendering, source assets, alpha, depth or picking?

Tools: pinned Remix1.5.2/SDK0.6.4 (existing dependency manifest), VS2026 C++20,
D3D11 hardware GPU, Python3.12; Windows11/RTX4070Ti/driver617.42 tested baseline.
Source: image_controls_probe.cpp, remix_image_controls.h, remix_image_adjust.h.
Build: tools/remix_runtime/build_image_probe.ps1. Prepared offline runner:
`python tools/remix_runtime/run_image_probe.py --execute` (no SFC).
Use established elevated parent if sandbox GPU/process access requires it; no
new UAC workflow/global policy change. Hidden owned window; no Toolkit.

Starts immediately with deterministic GPU colour/alpha tests, then a fixed
synthetic emissive triangle through actual Remix FINAL_COLOR. Seventeen bounded
cases compare startup/local/global, manual/automatic exposure, brightness, EV,
contrast, saturation, gamma and restored baseline.64 rendered frames per case,
16 measured samples; central16x16 average only. No game data/continuous screenshots.
Native exposure and brightness are NOT asserted equivalent to changing lights.

Controls BEFORE execution: host60s internal cap, runner75s wall cap,16MiB warning,
32MiB hard output cap,250ms polling; owned-process kill/wait on timeout. Logs and
JSON only under ignored artifacts/remix-runtime/runs/<UTC>-image-controls; expected
under100KiB, no full-frame dumps. Never enable unrestricted Vulkan/GPU tracing:
those mechanisms can produce multi-GB output rapidly and are unnecessary here.
Existing broader live qualification keeps its own60s/32MiB case bounds and image
budget; repeated texture derivatives are not an image-control requirement.

Analyze recorded RGB statistics against neutral/manual baselines and expected
direction/greyscale, not SDK success alone. Native global grade and local fallback
are different implementations; do not claim pixel identity of different tone
mapping modes. Preserve last-good config and source/binary hashes in result.

Cleanup: runner owns only its child probe and hidden window. Normal probe drains
GPU/retirement and calls SDK Shutdown; existing SDK40 warning remains separate.
On timeout stop/wait only owned child. Keep small logs/results; do not remove
active sessions or archives. No SFC hooks/proxies/game files installed by probe.
Gameplay validation, if requested later, uses existing light-tuning runner and
90second normal diagnostic profile or explicit30minute tuning profile. No new
geometry hook/capture, no changes to source light/material configuration.

## Live transport and return-path regression

Worker validates config/image.toml on a500ms poll; packet48bytes:
little-endian6uint32 (magic0x31474D49,version1,enabled,localMode,autoExposure,
brightness),4float32 (EV,contrast,gamma,saturation),FNV1a64 of first40bytes.
Atomic pending→bin rename; malformed/incomplete/nonfinite/out-of-range files keep
last-good state. Max256 accepted revisions;16snapshots plus latest,100messages.
Host polls only after GPU completion and receiver releases output lease. D3D9
copy completes before optional D3D11 image pass; D3D11 event fence completes before
publication. No new shared resources, no texture/material recreation on image edit.

Native brightness option is rejected by actual DLL; use supported exposure
mapping. A native option failure restores old set then stops optional host rather
than continuing with a half-applied profile. Initial disabled file does not issue
native options. Disabling after edits restores pinned native startup defaults.

`python tools/remix_runtime/qualify_image_pipeline.py` repeats13 existing bounded
return cases plus the actual image probe. Each return case60s/32MiB with existing
128MiB image-output cap; driver waits at most85s per child. Thirteen-case list:
direct/callback/slow/disconnect,visible,textured+one-shot image,textured slow/dead,
native light wiring/light types/project fill/material reload/image reload. No SFC.
Image reload case verifies local gamma→invalid last-good→global native grade→disabled
restoration on the actual production host. No unbounded telemetry added.

## Pinned primary-source basis

All URLs below refer to dxvk-remix commit
`b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4` (release-associated public source).
Downloaded read-only reference files remain under ignored deps, not redistributed.

- [Tone mapping dispatch](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_context.cpp): dispatchToneMapping selects local/global and supplies auto-exposure.
- [Global options](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_tone_mapping.h) and [local options](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_local_tone_mapping.h): independent namespaces/defaults; no exposed gamma slider.
- [Global shader](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/shaders/rtx/pass/tonemap/tonemapping_apply_tonemapping.comp.slang): optional linear contrast/saturation before sRGB conversion.
- [Exposure options](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_auto_exposure.h): default enabled; influences both tone mappers.
- [SDK option lookup](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_remix_api.cpp): SetConfigVariable returns failure for unknown key. Actual binary acceptance AND pixel effects are required; source association alone is insufficient.

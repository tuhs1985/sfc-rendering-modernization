# Run163 — initial material readiness investigated; no fast fix promoted

## Outcome

**PARTIAL / current dynamic-material boundary unresolved.** Six bounded native
controls completed. NVIDIA texture/shader waiting options and initial-library
ordering do not provide a qualified fast, correctly materialed first output.
Do not call this a startup fix or keep lowering bootstrap counts blindly.

Started clean at fd79ce5. Read authoritative handoff/probe and exact pinned vendor
source; Fuel Guard existing hook attached. No helper, subagent, SFC or Toolkit.
No production source/binary/config/runtime/client changed. Normal host remains
SHA5e59d67ece5c34101c98c7326062c6099dfb4bbe32f6877647347b10ef2b1314.

Probe and receipts:
[definition](../reconnaissance/probes/REMIX-INITIAL-READINESS-001.md),
[curated results](../reconnaissance/evidence/20261024-initial-material-readiness.json).
Full comparisons, image SHA multisets and job receipts remain under
`artifacts/initial-readiness/analysis.json` and the six referenced run folders.

## What the controls establish

| Control | Discovery to first cohort GPU output | Early window |
| --- | ---: | ---: |
| Accepted24 startup | 5.170s | 595/600 |
| One startup Present | 2.578s | 446/600 |
| One + vendor texture wait | 6.355s | 595/600 |
| One + vendor shader-finalization wait | 5.182s | 593/600 |
| One + explicitly disabled replacements | 2.661s | 460/600 |
| Complete library before device + synchronous initial asset loading | 5.857s | 595/600 |

First matching game-frame screenshots, NOT the usual delayed sample, accompany
settled screenshots. Fast one-Present first image versus explicitly disabled
replacements differs only0.217RGB/255 (16 ship pixels differ by>3); settled
comparison differs22.394RGB/255. This is a meaningful negative control: initial
enhanced material response is absent, not merely a different denoiser history.
Ordinary diffuse textures still exist in that first image; do not say no textures.

Against accepted24 first pixels, texture-wait differs13.724RGB/255,
shader-wait6.716, complete-before-device10.498; settled residuals about2.0–2.2.
These controls are not first-pixel parity qualifications. Their differences alone
do not locate every remaining material/lighting/history stage. No option promoted.

All six: same432 original/derived image SHA multisets and same visual settings;
all4owners/3contents ACK, no asset partials, ONE initial material publication,
normal owned-job exit0/remaining0. Thus these failures are not late-shuttle
arrivals, image changes, an omitted owner or accidental appearance retuning.
Existing vendor common-device-object disposal warnings persist; exit0 is not
proof of leak-free vendor shutdown. Timing is GPU output, not physical display.

## Supported mechanism versus missing interface

Pinned NVIDIA source describes initial mod loading in `RtxInitializer::loadAssets`
and `SceneManager::initialize`. Our early device starts against an EMPTY mod;
the later completed library is a file change, not a new initial-load operation.
`UsdMod` has a1000ms file-watch worker and reloads on a subsequent frame end.
Disabling `rtx.enableReplacementAssets` suppresses replacement use; it does not
make publishing a file an explicit load-completion barrier. This is a verified
project sequencing relationship, not a newly proven NVIDIA defect.

CONFIRMED source and negative control support late material availability.
STRONG HYPOTHESIS file-watch reload contributes to first-use interruption.
Not proven: every millisecond is watcher latency, or one undocumented GPU/compiler
operation is the sole bottleneck. Do not turn one-second source polling into a
new fixed one-second wait in our host.

The public pinned API0.6.4 has no dynamic USD-mod load-completion/readiness query
or explicit synchronous reload call. Internal `areAllReplacementsLoaded` and
initializer flags are NOT public functions we may call by guessed addresses.
GPU query completion only covers work submitted before that query; it cannot
prove a later watcher-triggered load has happened.

NVIDIA's documented `CreateMaterial` returns a material handle; SDK mesh surfaces
can carry it. That alone does NOT establish binding it to our ordinary D3D9
draws: the pinned source separates external material handles from USD replacement
lookup. Switching geometry to CreateMesh/DrawInstance would alter the present
ordinary-D3D9 proof boundary. Do not disguise that as a settings fix or promote
candidate1.6.1 silently. Existing API texture-prefetch experiments already failed
to establish this missing boundary; do not repeat them as a new solution.

References: exact pinned
[initializer](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_initializer.cpp),
[USD mod](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_mod_usd.cpp),
[texture manager](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_texture_manager.cpp),
[initializer options](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_initializer.h),
[public API](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/public/include/remix/remix_c.h),
[asset replacer](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_asset_replacer.cpp),
[SDK usage](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/documentation/RemixSDK.md).

## Reproduction and validation

Ignored `artifacts/initial-readiness/run_control.py MODE` uses the existing
`artifacts/interface-cleanup-first-frame/first_frame_fixture.exe`, not a new
capture system. Modes reference/single/texture-wait/shader-wait/single-disabled/
initial-library were executed; combined mode exists but was not run or claimed.
The isolated host source copies current production and changes ONLY bootstrap
count24to1; all ongoing live frames stay one. Include directories are normal
tools/d3d9_proof and pinned artifacts/remix-runtime/deps; standard x64 VS18
`/std:c++20 /EHsc /W4 /WX /O2 /fp:precise` and normal host link libraries.
Source/binary/fixture hashes recorded per run. Child environment only; no global
variables/UAC/security-policy edits. Existing private-channel GPU work used scoped
outside-sandbox execution. No experiment can certify normal production receipts.

All504Python tests PASS7.568s. Normal Performance read-only preflight PASS;
exact-source normal receipt remains current. Normal native host hash unchanged.
Final whitespace/path checks pass; no owned renderer/fixture remains. Existing
20GB aggregate and32MiB supervisor bounds retained; total17,159,051,086bytes before
small documentation overhead. No source/assets/captures deleted. Raw six-run
evidence retained; normal gameplay/settings untouched. Documentation only remains
unstaged/uncommitted; no push.

## Decision required before implementation expands

Smallest missing capability: explicit consumption/readiness for dynamically
published material replacements on ordinary D3D9, separate from GPU-copy ACK.
Retain accepted24 behavior rather than expose known incomplete first pixels.

Exact next action: sponsor chooses whether to preserve this D3D9 route and seek
upstream-supported dynamic material readiness/binding, or authorize an isolated
backend material-delivery investigation that may require SDK mesh submission.
No upstream issue/message has been posted and no alternative renderer selected.

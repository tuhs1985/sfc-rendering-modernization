# Run190 — startup presentation wait tied to material publication; not a GPU draw-rate limit

Task: examine the remaining draw/Present stage after Run189. Fuel Guard attached;
credits remain authorized. No SFC launch, production source/binary/configuration
change, runtime patch, architecture switch, staging, commit or push.

## Findings and confidence

**CONFIRMED:** retained Run188 controls spend only1.79–1.83ms issuing all24startup
draws. Their largest Present-plus-admission intervals are2239/2398ms; all admission
callbacks total only15.6/8.6ms. Draw issuance is asynchronous: this does not measure
all rendering/GPU work. Run189's live bootstrap aggregate remains2838ms.

The host creates ordinary D3D9Ex with an invisible `WS_POPUP`, immediate presentation,
one backbuffer, then registers that device for supported output copying.
Registration retains the device; it does not replace its swapchain. Do not apply
the external-swapchain resume-semaphore explanation to this path. Source:
[pinned device registration](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_remix_api.cpp#L1269).

The pinned ordinary presentation path flushes queued work, waits for frame latency
and prior submission, acquires a presentation image, and queues rendering/presentation.
A slow Present can expose earlier queued work. It is not proof that copying pixels,
VSync, our10ms sleep, or the ship's triangle count consumes those seconds.
[NVIDIA normal Present implementation](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/d3d9/d3d9_swapchain.cpp#L1033).

**CONFIRMED source behavior:** the USD watcher checks the master file's modification
time; a signaled change invokes unload/load and synchronous `processUSD`/stage-open.
At frame end, a changed replacement library causes a scene clear. These are
whole-library/scene operations, not a promise of incremental material insertion.
[Pinned USD reload](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_mod_usd.cpp#L958),
[frame-end scene reset](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_scene_manager.cpp#L441).

Our `flush_enhancements` drains up to four ready groups per coordinator cycle;
`retry_publication` rewrites asset stages and the master. There were43master writes
in the retained normal-publication control and28in the new deferred replay.
**A write count is not a measured reload count**: the watcher may coalesce writes.

**STRONG HYPOTHESIS:** material-library consumption/reloads are a substantial source
of startup and later delivery stalls. Source plus the controlled publication delay
below support this; no internal stack capture assigns every millisecond to USD
parsing, texture upload, shader finalization, or a particular wait primitive.

## Isolated experiment and full-interval result

Versioned probe:
`docs/reconnaissance/probes/20261025_present_publication_probe.py`.
It imports the existing bounded standalone fixture and changes only the current
Python process's `flush_enhancements`. Prepared enhancements are held until the
native live-input selected word becomes nonzero. Source inspection confirms that
word is initialized to0 and set by `LiveOwnerInput::start` only after bootstrap
output/receiver ACK. Owner-rebind applies subsequently. No new render callback,
native flag, artificial sleep, thread, GPU synchronization bypass or game hook.
Base publication/preparation,24Presents,10ms sleeps, image bytes and settings remain.
This diagnostic is explicitly ineligible for production qualification; normal build
locks were removed from diagnostic results and preserved under a diagnostic label.

| Observation | Retained normal publication220919 | Deferred publication224552 |
| --- | ---: | ---: |
| Bootstrap wall time, first begin→last Present mark | 3374ms | **888ms** |
| All24draw-issuance calls | 1.788ms | 2.022ms |
| Present-plus-service aggregate | 3130ms | 646ms |
| Largest Present-plus-service | 2398ms | 281ms |
| First matching output, from first discovery | 6.107s | 3.816s |
| Post-start omitted returned layers | 79 | **238** |
| Longest omission run / recorded time span | 78 /1.309s | **164 /2.804s** |
| Later600-frame delivery window | 594/600 | **520/600** |

These are separate standalone runs, not a controlled physical-display benchmark or
an improvement claim against Run189's two-ship game. Native code/runtime and final
asset bytes match, but scheduling/caches and material publication cadence vary.
The deferred first cohort draw/Present was1.294ms. Bootstrap query1.194ms,
post2.372ms, receiver/ACK302.545ms; total asset-service time9.338ms. After release,
the first large omission gap starts about34ms later and spans2.804s. A second
73record gap spans1.235s. The trouble moved into live delivery; it did not vanish.
The native render loop's internal durations during those gaps were not instrumented,
so do not call the2.804s gap a measured individual Present call.

**Final content:** all381selected geometry/texture/material files are byte-identical
to the retained initial-data control, with no unexplained differences. The late
comparison image contains the expected three distinct textured contents; paired
shared-owner behavior is recorded separately. Late ship-region mean absolute pixel
error is0.258/0.253/0.250per255RGB, not bit-exact. This is one late sample, not proof
that the correct enhancements were present during the entire interval. Four owners
acknowledged, no asset rejection/partial, native HUD/scene exact, state_errors0,
resize/recreate and normal owned exit pass for the deferred run.

New deferred evidence:
`artifacts/remix-runtime/runs/20261025-224552-119514-return-fixture`.
Full reproducible analysis:
`docs/reconnaissance/probes/20261025_present_publication_analysis.py` →
`artifacts/present-stall/analysis.json`.

## Separate failed control — do not hide it

The new unchanged-publication control224644terminated with native renderer exit
**3221225477/0xC0000005** after17.016s. The guard reported no time/output stop and
zero remaining owned children. The supervisor reported renderer exit followed by
the secondary missing additive-pool error. No call stack establishes the crashing
module or cause. Deferred native diagnostics were lost with the process; it supplies
no usable startup split or final-pixel pass. This is an external replay failure,
not a new SFC crash. Raw logs/result and recoverable generated assets remain.

The isolated successful deferred run also retains the existing runtime teardown
message `[40] common device objects were not disposed of`, seen in Run188. Process
exit0/no owned children does not prove perfect internal runtime resource disposal.
No vendor fix is claimed. Do not repeat controls indefinitely or promote this policy.

## Bounds, validation and repository state

Both probes used existing100s standalone/32MiB non-image evidence limits and1GiB
image-output reservation. Deferred native21.625s/63079console bytes; failed native
17.016s/31451console bytes. No continuous screenshots or image dumps. Existing two
bounded fixture screenshots retained. Generated asset trees143656642+143656645B
were ZIP-archived with per-file SHA256 verification before removing only those loose
duplicates:17816011B combined archives, receipts under`artifacts/present-stall/`.
Logs, original packets, screenshots and failed results remain; current normal221209
qualification/golden222711fixtures were not archived or changed. Aggregate after
archive~18.733GB<20GB; exact final inventory in curated evidence.

Fast validation: two actual standalone graphics attempts above; analyzer rerun from
archives, Python AST parse, JSON/reference checks and`git diff --check`. Existing615
Python/native qualification tests are previous evidence, not rerun/relabelled here.
Normal native host/runtime/source hashes unchanged by both probes. No game launched;
no client artifacts modified. Installed Nsight requires an OS-admin launch under the
previous process-only trace procedure; current process is not elevated even with
filesystem escalation. No system-wide injection/security workaround attempted.
This is not blocking the next bounded publication control, so no sponsor action
is required now. Do not reuse the old1.6.1candidate trace as current1.5.2evidence.

Changed this run: this record, curated JSON, the two versioned probe/analyzer files,
`docs/HANDOFF.md`, `docs/STATUS.md`, and the matching Obsidian snapshot. Generated
probe/analysis/archive receipts remain under artifacts. All prior uncommitted work
preserved. HEAD`9ff2d3d`, all changes unstaged/uncommitted; no push. No owned process
or shared channel survives. M1 integration/performance work continues; no new formal
TRL or sub2s/seamless result.

**Exact next action:** test a standalone transaction that publishes each completed
enhancement revision once, instead of repeated four-group master-file refreshes,
while displaying base-textured geometry immediately; measure the full delivery
interval and final pixels before changing the normal/progressive launcher.
Do not merely delay publication, remove readiness waits/24bootstrapPresents blindly,
scrub accepted material maps, patch NVIDIA internals or resume the parked API route.

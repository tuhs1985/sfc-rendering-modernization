# Native scene insertion — boundary and readiness observation

Status: metadata-only implementation prepared; actual SFC ordering/readiness unmeasured. Run222, 2026-10-29.

Startup/recovery correction, Run223 (2026-10-31): the first checkout failed before recording because disabling the presenter also omitted the native-required replacement ledger. The receiver now prepares a passive Priming ledger with matching session/PID and no suppression/commit. Its independent observation veto remains. Recovery recognizes this probe's verified full-support transaction and the copied installation is restored. Native tests now295 per architecture; startup/recovery Python tests13. See [repair record](../../runs/2026-10-31-codex-native-observation-startup-recovery.md). Use the same launcher; earlier timing is still unmeasured.

## Question

At the player fixture's existing visual/model boundaries, which native colour/depth targets are bound, which native queue flush reaches D3D11, and is an output from the same source-frame number already available? This does not authorize replacement: asset, camera, transform, generation, GPU ownership and completion still need matching before any insertion.

The latest live failure is documented in [Run221](../../runs/2026-10-29-codex-native-insertion-reassessment.md). Shield extraction/replay is parked. Existing native depth compositor remains unused in SFC; this probe does not install it.

## Supported relationship and observation method

- Reuse existing scene begin `0069E300`, owner-qualified model entry `0042E4B2`, polygon observation `006AC5A0`, and visual mainline exit `0042FDD5`. No additional engine hooks; diagnostic geometry hook remains off.
- Model entry uses the established mainline caller/vtable/owner tests. `ModelEnd` means the existing visual exit marker, **not proof that the native shared batch has completed**. Manager depth-write changes flush conditionally; `006AB380` is shared and cannot be treated as owner-exclusive.
- Source publication is observed after the existing persistent update at the polygon wrapper. It is an offered scene/camera observation, not a whole-scene seal.
- Existing ReShade draw notifications supply immediate-context observations before the actual downstream draw. Query bound RTV, DSV, view/resource formats, dimensions, samples, and depth state. Capture one bounded 16-address stack sample per phase, retaining the first native EXE return address only. No instruction or pointer dereference from stack metadata.
- Observe before-selected, inside-selected, after-selected and other-model phases. At most two draw observations per phase transition. These samples identify candidate draw order; they are not an exhaustive inventory of effects or a GPU-completion fence.
- Peek validated output metadata at sampled draws and Present. Return idle ownership without reading any output pixels. Import-worker acquisition can temporarily hide a ready slot; absence in one sample does not prove that output was never available.

The relevant D3D11 contract is the [output-merger stage](https://learn.microsoft.com/en-us/windows/win32/direct3d11/d3d10-graphics-programming-guide-output-merger-stage) and [depth/stencil processing](https://learn.microsoft.com/en-us/windows/win32/direct3d11/d3d10-graphics-programming-guide-depth-stencil). Merely moving a Present callback earlier does not establish correct native render-target ownership, draw ordering or matched output readiness.

## Transport and safety

`tools/native_insertion/probe_wire.h`: version1, 128-byte header and 256 × 128-byte committed records (32,896 bytes), at `replacement::Offset + 16384` within the existing reserved 64KiB section of the current-user/session mapping. This does not overlap the 4,416-byte replacement ledger or the parked foreground notice section.

One native render thread produces; an external Python worker consumes at 10ms polling intervals. This polling interval does not limit rendering/publication. Full storage drops new metadata and increments a counter, without overwriting unread records or waiting. Per-record ordinal is committed before producer cursor advancement; consumer acknowledges only after copying. Header magic is committed after initialization. Session, producer PID, thread and cursors are checked. Callbacks use preallocated storage, bounded stack work and graphics getters: no disk access, allocation, decoding, image copy, GPU readback or waits.

Both sides explicitly disable picture changes: M1 skips suppression even if a control permit were mistakenly active; receiver skips replacement authorization, history allocation and presentation. Original ship, shields, weapons, text and UI continue normally. Existing private renderer/assets/settings are retained to measure actual output availability. Output metadata is **not** authorization, even when frame/owner/revision numbers agree.

Evidence: `NATIVE-INSERTION-001.events.bin` capped at 8MiB; summary continues after detailed saturation. No additional geometry/image dumps. Existing 90-second tactical window, 285-second workflow, combined log/project budgets, process cleanup and unchanged-client checks remain. Stop/join the evidence worker before closing its mapping. Native callback drain/hook restoration precede source shutdown.

## Checkout

Use the prepared elevated parent:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\d3d9_proof\start_d3d9_native_insertion_observation.ps1"
```

Use the usual unique F-CA versus a different enemy model. Original game picture only; no extra/replaced ship is expected. Play normally, change camera, fire weapons/show shields and briefly pause/unpause. Keep SFC open through restoration and exit only after the two low beeps. No manual timestamps. The observation starts at the tactical gate without waiting for a visible copy, leaving the existing 120-second semantic watchdog its cleanup margin. Premature process exit is not proof of controlled unload.

## Offline evidence and decision

286 native checks per architecture: ring capacity, ordering, thread/session rejection, stopped producer, original RGBA8-typeless/linear-view 8MSAA/D32 state and pixels, invalid/wrong-owner output and metadata-only release. Actual M1 recorder test: 13 checks including suppression veto despite an active permit. Six Python tests cover decoding/acknowledgement, timing summary, malformed commits, session and cursor rejection. Existing transaction regressions pass (32 checks per architecture) and light worker qualification passes. Actual installed observer/addon and isolated candidate host were rebuilt; launcher read-only preflight passes. No SFC launch or full replay GPU campaign this increment.

The new gate certifies a **metadata-only observation**, not renewed shield or replacement qualification. Older source-locked rendering receipts remain historical/stale; do not relabel their success. Review the real run for matching visual exit/flush/target/output timing before connecting the native depth compositor. If current-frame output is unavailable at the required boundary, preserve that result and address the scheduling/retained-command requirement explicitly; never insert an older pose into a newer native scene.

# One-ship replacement — admission and depth insertion

## Current — 2026-10-27 Run209: READY for sponsor player-replacement test

Final-source replacement, existing overlay/material/tuning qualifications and
both read-only launcher preflights pass. Current sponsor settings preserved.
[Run209](../runs/2026-10-27-codex-player-replacement-qualified.md) records results,
including one rejected late-loading control and its accepted identical repeat.
The [version1 transaction](player-replacement-transaction.md) is implemented;
SFC gameplay suppression/unload/visible replacement are still pending. Use the
separate player-replacement launcher with F-CA versus a different model.


## Historical — 2026-10-27 Run208 PAUSED; transaction implemented, final qualification pending

The [whole-picture transaction](player-replacement-transaction.md) now stages
native source and matching Remix output offscreen before committing. Final-source
standalone steady600/600and bounded miss/recovery tests pass. Capture-first
player-fixture suppression is default OFF; no SFC replacement test or final
launcher qualification yet. Sponsor paused overnight; [Run208](../runs/2026-10-27-codex-player-replacement-transaction.md)
and newest handoff control resumption. Current user settings preserved.



## Historical — 2026-10-27 Run207: suppression candidate tested; presentation recovery BLOCKED

Sponsor accepts current depth and previous successful model alignment; do not
repeat those discovery proofs. [Run207](../runs/2026-10-27-codex-player-replacement-boundary.md)
verifies zero-count wrapper candidate offline (225x86checks) but reproduces a
missing-output hole with the actual existing GPU History in32/64bit (10checks each).
Current receiver restores source BEFORE confirming composition. Additive safety
relies on the original mesh still being in that source; readiness alone cannot
justify suppressing it. Original drawing stays enabled. No new runtime launcher.
Next: qualify replacement presentation commit/rollback, including first frame,
miss/reset/disconnect; only then wire capture-first player suppression. Depth and
alignment remain the accepted baseline. Older exact-current/SDK/late-ImGui and
30Hz descriptions below are historical, not current pipeline authority.

## Historical design and evidence

Status: **PARTIAL — offline building blocks qualified; SFC replacement NOT enabled.**
2026-10-19, [Run65](../runs/2026-10-19-codex-replacement-depth-foundation.md).
Authority: sponsor requests replacement under the existing two-gate in-game
Remix integration plan. No requirements, maturity gate or architecture change.

## Separate from the accepted additive path

Sponsor clarification after Run67:original-ship fallback is a last-resort safety
contingency,not the steady-state synchronization solution. Playable replacement
remains governed by CDD KPP-3. Qualify capture/render/transfer/present timing and
frame correspondence under motion;static cached-result reuse alone is insufficient.
No frame-time requirement is waived to avoid output gaps,and no blocking lockstep
or stale-image strategy is accepted without measured playability/correspondence.

Run66 adds an opt-in depth-only additive diagnostic;see
[probe](probes/REMIX-SCENE-DEPTH-001.md). It reads native scene depth and filters
the extra copy at the EXISTING display callback. Sponsor observed that copy under
UI;do not relocate the callback based on an unsupported HUD-overwrite assumption.
Actual grid policy and all suppression predicates below remain unqualified.
Depth mode may blink even stationary because it refuses unmatched frames;it is
not a production replacement policy. Default additive mode remains unchanged.

The accepted textured return remains unchanged. Its version4/mode2 policy admits
up to100ms-old output for an offset extra ship and deliberately ignores changing
frame/pose/camera in its identity comparison. This is NOT suppression authority.
It must not be enabled for replacement just by setting the offset to zero.

New `ship_replacement_contract.h` is a process-local admission policy,not a new
shared-memory protocol or installed hook. It requires qualified current/returned
keys,zero diagnostic displacement,identical full identity and exact frame,
supplied/composed/view/projection/viewport words,corroborating pose/camera hashes,
finite numeric state and fresh GPU completion. Coverage,retained-scene visibility,
pre-UI order and actual target qualification must ALL be explicitly supplied.
All default false. A consumed sequence cannot authorize another suppression.
Commit requires successful composition submission and a second current-state
adjudication. Refusal means original rendering,not a cached replacement.

These predicates are obligations,not runtime findings. No production caller sets
them and no original draw is suppressed. Exact-frame admission may reject every
asynchronous request under motion;that is safe refusal,not proven practical timing.
No stationary-state frame-reuse exception has been qualified/implemented.

## Depth insertion building block

`ship_replacement_compositor.h` constructs shaders/resources before drawing.
It accepts a matching full-resolution color/depth/picking triplet and native
BGRA8 8MSAA target with R32_TYPELESS/D32_FLOAT depth,matching the observed client
configuration. Other formats/sample counts/dimensions/devices/read-only DSVs
decline rather than convert or silently relax. No image scaling is introduced.

Only pixels with matching raw uint picking ID and finite normalized depth/color
are drawn. Black is legitimate surface color,not transparency. Pixel shader
writes returned native-equivalent normalized depth with LESS_EQUAL/depth writes
enabled. Near retained geometry wins;later farther geometry loses;later UI can
remain on top when actually drawn afterward. Deferred command execution requests
full immediate-state restoration. No game-side readback,file I/O or GPU waits.
The synthetic fixture alone reads back a64x64 resolve for assertions.

This does NOT identify a safe SFC insertion boundary,prove real shield/weapon
ordering,prove complete per-sample silhouette parity,or suppress any original.
Returned coverage is still single-sample;8MSAA target compatibility is not a claim
of eight independently recovered Remix coverage samples. It does not override
the existing native-Z calibration's unresolved edge/material observations.

## Narrow static review and rejected shortcut

CONFIRMED static in the retained exact-build disassembly:

- `0042E4B2..0042E64D` updates manager render state,sets vertex/source bindings,
  submits primary list at`0042E557`/return`0042E55D`,may build/submit secondary
  geometry at`0042E620`/return`0042E626`,restores state,then returns`ret10h`.
- `006AC5A0` wrapper also changes manager state before polygon preparation;
  primary path returns`ret0Ch` at`006AC60B`.
- `006AB380` flushes queued manager geometry and resets shared batch counters;
  native indexed submission is`006AB3C0`. Its batch is not proven owner-exclusive.
- `0069E3D0` conditionally flushes at`0069E40B` before the native scene-end call
  at`0069E41B`. A CPU scene name alone does not prove pre-HUD insertion.

Therefore reject an early whole-Model0 return or indiscriminate native draw skip.
Both can discard state maintenance,secondary work or other owners' batched data.
The existing successful source/list substitutions are not a suppression proof.

## Remaining integration question

At a selected,validated owner invocation,where can a ready matching triplet be
inserted into the actual retained native scene target/depth while preserving
both batching order and tactical UI/effects? Existing late ImGui composition is
not that qualification. Historical broad capture found599frames ending in two
depth-unbound draws;that pattern alone does not identify the HUD boundary.

Exact next action: implement and offline-validate a default-off,read-only
owner-boundary observation joining the existing wrapper scope to native target,
depth and draw ordering;then prepare that narrowly bounded runtime test before
arming suppression. Do not repeat appearance,depth-conversion or return-path
proofs,and do not ask the sponsor to play before this probe is ready.

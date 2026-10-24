# Second live-interface audit — Run161

## Verdict and scope

**Cleaner, but not a clean-interface signoff.** Run160's resource/upload correction
and removal of unused live work survive source review. Remaining coupling is
project-owned, not established as a requirement of NVIDIA's interface.

Review only: no implementation, binary, configuration, dependency, qualification,
client or capture-policy changes; no game, GPU fixture or profiler launched.
HEAD `fe2eaf7`; existing dirty work preserved, index empty. Authority: newest
HANDOFF, Run159 audit, Run160 implementation/evidence, retained-multiship contract
and pipeline modes. Historical results below are not newly executed experiments.

## Previous findings rechecked

| Finding | Second-pass disposition |
| --- | --- |
| IF01 resource pools/uploads | Corrected: DEFAULT VB/IB/textures; SYSTEMMEM staging with UpdateTexture. Test-only readback stays out of Performance. Native x86/x64 resource/reset/recreation evidence exists; see recovery limitation below. |
| IF02 serial return relay | Still open: host waits for receiver copy/completion/ACK before reusing its one source surface set. ACK is necessary for this topology; do not delete it. |
| IF03 single-owner gate | Still open: `LiveOwnerInput::next` validates bootstrap vertices before coherent multi-scene lookup, then `MultiSceneRuntime::draw` repeats a projection oracle per instance. Native rows still cross the backend boundary. |
| IF04 bootstrap policy | Still open and honestly labeled transitional: first iteration uses 24 Presents; normal subsequent live iterations use one. This is not a vendor readiness signal. |
| IF05 material lifecycle | Still open: catalog admission, material-file publication, runtime consumption and correct first pixels remain distinct. |
| IF06 unused work | ACK formatting suppressed in Performance; unused vendor picking-retention request gated off additive mode; union-coverage naming corrected. Functional live-mode selection still uses a timing-named environment variable. |
| IF07 interop portability | Still pinned-runtime qualified, not universal native D3D9Ex or future D3D12 qualification. |
| IF08 safeguards | Still required: coherent source/camera identity, bounded resources, GPU completion/read leases, private channels and cleanup. No evidence justifies weakening them. |

## Additional findings

### IF09 — live rendering has an iteration-count stop (P2, CONFIRMED)

`tools/d3d9_proof/d3d9_direct_host.cpp:141` limits live execution to 6,001 loop
iterations, including bootstrap. Only `LiveOwnerInput::next` implements the
separate 110-second game-output watchdog; the outer counter can finish first.
Early `continue` paths consume iterations too. This is not a 6,000-image guarantee
and not a frame-rate limiter: it is a renderer lifetime ceiling.

At a sustained 60 consumed iterations/s, 6,000 iterations span about 100 seconds;
at 120/s, about 50 seconds. A rate above about 66.7/s can exhaust it inside the
formal 90-second observation. These are conditional arithmetic examples, NOT
measured rates or proof this caused either observed hiccup. The independent
receiver watchdog remains 130 seconds (`output_receiver.cpp:41`). Normal loop
exhaustion reaches finish/shutdown rather than reporting a distinct cap reason.

Correction direction: use explicit source-stop/cancellation plus the existing
elapsed-time safety deadline for live lifetime. Keep finite iteration limits in
offline replay tests. Verify fast input and repeated omitted/rejected frames do
not terminate a healthy live session early; retain bounded evidence separately.

### IF10 — standard qualification does not certify first-image readiness (P2, CONFIRMED acceptance gap)

`tools/remix_runtime/qualify_multiship.py:119` obtains a settled delivery window;
its gates check admissions, coherent pairing, independent draws, HUD/state,
cleanup and configuration/build identity. Those are useful but not a first-image
material-appearance oracle. Native texture equality proves upload bytes, not
Remix's eventual material interpretation or residency.

Run160 already supplies the counterexample: the one-Present experiment could
pass a settled 600/600 window while its first-image/early window had incomplete
appearance and only 433 deliveries. All four owners were initial, with one
material publication; do NOT describe that as a late-shuttle event. Normal startup
was restored to 24 and the experiment was not promoted.

Correction direction: extend the existing qualification boundary with first-valid
output/early continuity and matched first/settled material-response evidence
before using it to retire bootstrap policy. Do not invent a fake ready flag or
claim admission ACK establishes vendor readiness. Current receipt is not invalid
for its narrower preparation purpose.

### IF11 — resource recovery capability is not host recovery (P2, CONFIRMED limitation)

`tests/d3d9_resource_policy_tests.cpp` demonstrates release/rebuild and native
classic/Ex reset/recreation using the shared Renderer. The production host creates
its Ex device once (`d3d9_direct_host.cpp:73`) and checks PresentEx failures at
line164; it does not contain a Reset/ResetEx/device-recreation recovery loop.
Exceptions take its shutdown path. Fixture `resized=1 recreated=1` checks the
consumer/compositor, not recovery of the Remix host's registered Ex device.

Therefore Run160 establishes a valid rebuildable resource policy, not seamless
backend recovery from device loss. Safe omission/termination remains distinct
from automatic recovery. Do not add generic COM resets: the pinned runtime's
registration, aliases, output generations and Shutdown ownership must be honored.

### IF12 — later asset admission still shares the render worker (P2, CONFIRMED topology; cost unproven)

`MultiSceneRuntime::assets` prepares one pending asset on a std::async worker,
but consumes the future and constructs `Renderer` (VB/IB/texture staging/uploads)
on the host worker used for drawing. Its `LiveOwnerInput::idleWork` callback runs
inside the input-wait path. Thus background CPU preparation is real, but GPU
admission is not independent of frame servicing. One pending future and at most
one admission per iteration are deliberate current bounds, not NVIDIA mandates.

This is a potential late-asset stall boundary, not proof it caused the independent
non-arrival hiccups. Do not make Ex device calls concurrently on the current
device without qualifying its threading contract. Prefer existing vendor
loading/upload mechanisms and measured bounded admission; retain geometry sharing.

## Documentation backing and distinctions

- [Microsoft D3DPOOL](https://learn.microsoft.com/en-us/windows/win32/direct3d9/d3dpool)
  and [UpdateTexture](https://learn.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9-updatetexture):
  the corrected Ex pool/upload policy follows the documented contract. DEFAULT
  resources require explicit lifecycle handling; this does not itself implement it.
- [Pinned NVIDIA API0.6.4 header](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/public/include/remix/remix_c.h)
  and [matching API source](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_remix_api.cpp):
  ordinary-device registration and queued output copy are supported; the project's
  receiver process, 24-Present bootstrap and 6,001-iteration ceiling are not API
  requirements. Copy acceptance is not cross-process GPU-read completion.

Current-user shared mapping security does not make legacy shared GPU handles an
isolation boundary against malicious same-user code. Union coverage is not
per-owner picking and cannot authorize selective original-ship suppression.
Source review does not prove a new race, leak, or cause for the steady hiccups.
No API-pointer portability issue is promoted as an actual pinned-runtime failure.

## Validation and next action

- All 504 Python tests PASS, 7.825 seconds. Existing Pillow deprecation warnings;
  no failures. Native resource/GPU results remain Run160 evidence, not rerun here.
- Performance read-only multiship preflight PASS; no game/renderer started.
- Documentation paths and diff whitespace checked at closeout. Only this audit,
  Run161 record and newest handoff section added/updated by this turn.
- No staging, commit, push, cleanup or new evidence-heavy run; 20GB cap unchanged.

Exact next action: correct the live iteration-count lifetime ceiling with a
deterministic fast-input/omission regression, preserving elapsed watchdogs and
source-stop semantics. Then resume the existing first-image material-readiness
investigation before removing 24-Present startup or serial output ownership.

# Run221 — live shield repair failed; native scene insertion next

Sponsor reports replacement still covers shields AND native pause text.
Sponsor confirms the desired direction is native scene insertion and rejects
further separate shield extraction/replay as overcomplicated.

## Actual run and corrected assumptions

Reviewed artifacts/remix-runtime/runs/20261029-055718-417633-in-game:
5014 original-mesh suppressions,4997 returned commits; native foreground captured0,
replayed0,retained bytes0,setup rejects0.5014 eligible frames include an empty-
foreground interpretation and are NOT proof of shield replay. Final64 owner
notices contain a selected owner/thread/nonzero native shield pointer; pointer
presence alone does not prove a visible shield. No per-guard counters establish
which producer qualification lost native draws. Do not invent that diagnosis.

Normal game exit and renderer0; foreground-hook restore ACK1. Accepted client
files and proxy rollback unchanged. Controller exit8:Target exited before
controlled component removal. Controlled semantic unload was NOT confirmed.
No project/game processes remain at review. Process-exit reclamation is distinct
from controlled unload.

The active call is return_addon.beforePresent -> Receiver.step ->
replacementStep. History has captured finished native colour and resolved depth;
replacement is applied to that saved picture. Before ReShade effects does NOT
mean before native shields or text.

Historical shield samples have depth testing ON,depth writes OFF,additive ONE/ONE.
They can intersect/wrap/occlude correctly against native geometry without leaving
their own depth in the final buffer. Late colour/depth insertion cannot recover
their blended contribution. Pause-text overlap exposes a broader ordering issue.
The actual pause-text producer/state is not joined in this capture:do not invent
a specific text Z value or assert all UI disables depth.

The previous isolated fixture proved its synthetic replay algorithm,not real
SFC shield capture. The latest gameplay result fails the intended fix.
Run220 remains offline mechanism evidence; game-readiness claims are withdrawn.

## Direction and reuse

PARK the shield-replay branch/launcher as an experiment. Preserve its source and
evidence;do not expand it or give the same launcher back as a new repair.
No source/renderer/settings/binaries/receipts were changed during this review.

Retain fresh mesh/resources,simulation/camera tracking,prepared materials,
ordinary-D3D9/Remix rendering and shared colour/physical hull depth/coverage.
Insert returned colour AND depth into the actual native scene target and depth
buffer at the selected mesh rendering boundary. Let original native effects,
targeting,other geometry and UI continue afterward. ReShade may still provide
callback access;late Present composition must no longer define scene insertion.
This is native D3D11 downstream of dgVoodoo,not a claim that the renderer adapter
has stopped being D3D9 or that SFC is now a native D3D9 client.

Existing ship_replacement_compositor.h::DepthCompositor already writes SV_Depth
to a native8MSAA D32 target;tests/ship_replacement_tests.cpp already checks later
far/near native geometry and depth-disabled UI ordering. Reuse that building block.
It is NOT a qualified SFC boundary. Its BGRA-only/native raw device-pointer
checks need review against newer RGBA8/typeless evidence and wrapper identity.
Do not silently relax view/format/device checks.

Static native order is preserved in run221/native-order-excerpts.txt:
- Owner visual call0041655A precedes004103E2 and shield call004165AA.
  Earlier effect inventory already identifies004103E2 as a generic attached-
  trait dispatcher;it is not a newly unknown/dedicated shield function.
- Model0 restores state at0042E626..0042E643 after primary/secondary lists.
  The+C4 setter0069EC60 flushes only when state changes. A model return alone
  does not prove the pending native batch completed.
- Shared flush006AB380 submits native draw006AB3C0 and resets shared counters.
  Its batch is not owner-exclusive;do not suppress it indiscriminately.
- Scene-end0069E3D0 flushes before native EndScene. This name is not pre-UI proof.
  Historical opaque work follows per-owner shield draws;no global phase assumed.

Exact next work:qualify selected mesh -> completed native batch -> native
colour/depth target boundary AND matching output readiness there. Preserve exact
frame/owner/revision/camera association. Do not use N-1 pixels on an N native
scene,move a callback by name alone,or introduce an unmeasured blocking wait.
Existing source-to-Present timing does not prove earlier-boundary readiness.
If live evidence is missing,prepare a narrow metadata-only boundary/readiness
probe excluding model/image payloads. No general combat survey. Fix the separate
controlled-unload failure before another sponsor checkout. No new launcher ready.

## Scope, evidence and documentation

Read-only source/run/static review plus documentation;no SFC or GPU fixture run.
No staged changes or commit/push. Existing20GB bounds/current appearance remain.
Evidence:../reconnaissance/evidence/20261029-native-insertion-reassessment.json.
Original captures and qualification receipts retained;not relabeled successful.

Microsoft API basis:
- https://learn.microsoft.com/en-us/windows/win32/direct3d11/d3d10-graphics-programming-guide-output-merger-stage
- https://learn.microsoft.com/en-us/windows/win32/direct3d11/d3d10-graphics-programming-guide-depth-stencil
- https://learn.microsoft.com/en-us/windows/win32/api/d3d11/nf-d3d11-id3d11devicecontext-omsetrendertargets

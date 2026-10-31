# Run218 — bounded native foreground resource retention

Authority: sponsor says proceed after Run217. Implemented the first isolated
resource-lifetime/producer-boundary unit of the approved shield-first sequence.
No new SFC session, production hook, launcher or settings change.

## Completed

- New `tools/native_foreground/retained_resources.h`: preallocated exact-layout
  GPU resource copies; fixed slots/4MiB cap; session/frame/owner/revision matching;
  complete-only publication; immediate-context/device checks; event-query reuse.
- New `producer_scope.h`: excludes entry depth-state flush, includes restore
  flush, rejects unknown resources/states and nested ownership ambiguity.
- New standalone `retained_resources_tests.cpp` and README contract/limitations.
- Rechecked existing Federation/Romulan survey metadata: shield candidate
  texture256x256/format27, helper textures1x1/format28, VB737280B,IB16384B.
  These are historical resource layouts, not a new runtime producer-to-view join.

## Validation

Strict x64 MSVC C++20 `/W4 /WX /O2 /fp:precise` build passed. Standalone hardware
D3D11 fixture passed53checks. Saved vertices/indices/constants/texture produce
expected additive pixels after the originals are overwritten. Wrong session,
frame, owner epoch and revision cannot access a packet. Partial capture, capacity,
in-flight overwrite, GPU retirement, unsupported images and deferred-context
retirement are exercised. Native-size synthetic packet occupies1,015,808bytes.
The earlier29check result was an intermediate build, superseded by53checks.
Final executable/hash/test output recorded under `artifacts/player-replacement/run218`.

Microsoft's CopyResource/GetData documentation supports the exact-copy and
asynchronous-query mechanism; links are in the implementation README. Readback,
Flush and bounded waiting exist only in the standalone test. Production source
hashes/receipts are not changed or renewed; no broad GPU campaign was needed.

## Remaining (not claimed complete)

This is resource-version retention, not arbitrary draw replay or a shield fix
installed in SFC. Full original shader/input-layout/sampler/SRV/CB binding capture,
live native-resource-to-translated-view qualification and same-frame masked/depth
foreground assembly remain. Mip layouts and mapped-resource conditions need
qualification; unsupported data must not authorize suppression. Current output
budget remains126.5625MiB; no extra full-resolution plane is allocated here.
No occlusion/shield-image success, new gameplay PASS or milestone claim.

The existing working replacement and current physical hull-depth repair remain
unchanged. All prior dirty work preserved; index empty, unstaged/uncommitted.
No process/server must survive this isolated fixture. No sponsor action needed
for the next offline step.

**Exact next action:** extend the isolated fixture to preserve original draw
bindings and assemble retained foreground only over replaced hull pixels,
qualifying front/back occlusion and an output-resource reuse scheme before
connecting native shield hooks to the production replacement transaction.

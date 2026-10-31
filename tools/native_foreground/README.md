# Native foreground preservation — parked shield replay experiment

## Current direction — Run221,2026-10-29

Actual SFC ordering failed:shield captured0/replayed0;ship also covers pause text.
Shield replay is PARKED. Offline proofs below are historical mechanism evidence,
not an in-game repair. Target returned colour+physical depth insertion into the
native scene before effects/text,with exact-frame readiness and qualified batch
ownership. [Run221](../../docs/runs/2026-10-29-codex-native-insertion-reassessment.md). The later [Run224](../../docs/runs/2026-10-31-codex-native-insertion-timing-review.md) measured the earlier insertion timing gap; it does not qualify this replay branch.


Historically, Run220 qualified the isolated mechanism before the failed SFC checkout. See
[Run220](../../docs/runs/2026-10-28-codex-native-shield-connected.md) and
[handoff](../../docs/HANDOFF.md). Native original draw state and mutable resource
versions are paired with the same saved background/Remix hull. Shader creation
qualification rejects incompatible MSAA semantics. Wrapped device identity and
teardown/mapping lifetimes are qualified through actual ReShade/Remix fixtures.
286focused GPU/17ABI/583Python checks pass; steady599/600 and fault recovery pass.
This does not establish exact8MSAA edge equivalence, arbitrary native effects or
in-game shield appearance. Settings and126.5625MiB output footprint unchanged.

The sections below describe the earlier Run218 resource primitive; they are
historical where superseded by Run219. No blanket claim of installed shield
preservation or complete arbitrary native-draw support is intended.

`retained_resources.h` freezes exact GPU resource contents, rather than merely
holding a COM pointer to mutable data. Setup creates all storage before capture.
Capture queues `CopyResource` on the same device's immediate context. Buffer
sizes must match exactly; textures must be single-mip, single-sample 2D RGBA8
or RGBA8 typeless, at most256x256. Other layouts are rejected explicitly. The
historical survey establishes dimensions/formats, not live mip counts or every
shader binding; these restrictions are not a claim of complete live coverage.

Each packet has18buffer slots (enough for VB/IB and16constant buffers) and
3image slots, with a4MiB aggregate cap. Slots are provisioned explicitly; this
does not allocate18maximum buffers automatically. Every provisioned slot must
be copied before seal. A packet carries session/frame/owner epoch/revision.
Only matching sealed packets can expose resources for replay. GPU event-query
completion gates reuse; polling uses DONOTFLUSH and returns immediately. No
capture-side file access, conversion, CPU readback, allocation or wait is coded.
Calls must stay on the immediate-context owner thread; there is no thread-safe
arbitrary cross-thread context use. The final query must be queued AFTER every
command consuming this packet, including an abandoned partial capture's copies.

`producer_scope.h` excludes the flush occurring on entry to the native
depth-write-disable setter and includes the flush inside its restoration call.
It requires matching identity/resource, tested depth, no depth writes, additive
ONE/ONE and indexed triangles. Nested owner spans reject the whole ambiguous
span. This is a state-machine implementation derived from the pinned native
setter, **not proof that a live translated texture has been joined to the native
resource ID**. It does not install a hook or identify a texture by filename.

Validation: `retained_resources_tests.cpp` builds a standalone D3D11 fixture.
The fixture intentionally overwrites original vertices, indices, constants and
texture before drawing from retained versions. It checks actual additive pixels,
wrong identities, partial packets, retirement and busy storage, plus native-size
VB737280B/IB16384B/256x256typeless texture copying and producer-boundary cases.
The pixel test uses synthetic shaders; it does not reconstruct SFC shaders.
Fixture readback/wait/Flush are test-only and absent from the retention primitive.

Next: retain actual native VS/PS/layout/samplers/SRV descriptions and all bound
constant-buffer versions with the qualified producer, then prove same-frame
foreground assembly including front/back occlusion and no doubling outside
replacement coverage. The existing126.5625MiB output footprint still needs
qualified reuse/reduction before an additional full-size layer is allowed.
No production output resource, presentation order, light/material setting or
suppression contract changes in this increment. No sponsor test requested yet.

Microsoft API basis:

- [CopyResource](https://learn.microsoft.com/en-us/windows/win32/api/d3d11/nf-d3d11-id3d11devicecontext-copyresource): GPU asynchronous exact-size resource copying.
- [GetData](https://learn.microsoft.com/en-us/windows/win32/api/d3d11/nf-d3d11-id3d11devicecontext-getdata): immediate-context query completion.

The application checks supported layouts before copying. Source resources must
not be mapped when copied; integration must qualify that condition at the draw
boundary. Device removal invalidates the session; this primitive is not a full
device-loss/recovery manager. Shader views must be prepared outside callbacks,
using original view formats (a typeless texture alone is not a shader view).

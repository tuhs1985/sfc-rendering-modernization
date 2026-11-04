# Renderer interface exposure — current implementation

**November4 update:** the subsequent damage increment now exposes per-owner
current scalar/family in version3 coherent scene snapshots and a separate native
damage mapping channel. Source geometry/UVs/images stay canonical; Remix-specific
row conversion/material/decal treatment stays in its adapter. See [live damage
results](../runs/2026-11-04-codex-damage-live-confirmation.md). Statements below
about damage not yet joining the live protocol describe this audit's earlier
snapshot. Future effect callbacks and a stable public SDK remain open.

November3,2026, Run285. Source review at commit `91627e5`, after the Run284 damage
observation. This is a map of existing integration and extension points, not a
stable public SDK specification. No renderer, protocol, settings or runtime
behaviour changed. The renderer-independent boundary gate remains open.

## What the work buys us

The reusable foundation is substantial: fresh assets and original image
associations, independent owner/asset identity, persistent simulation transforms,
camera/projection, coherent scene submissions, GPU ownership and correctly ordered
native replacement. Another renderer should not need to rediscover those SFC
relationships. They are broader than a fix for Remix.

Much of the later appearance and material-readiness work is Remix integration:
its texture convention, generated material libraries, consumption notifications,
runtime initialization, light types and image controls. Some fixes, such as
parallel preparation, resource reuse, early passive processes and shared-memory
startup tickets, improve the whole pipeline while their current implementations
still live in a Remix-oriented coordinator. A percentage of engineering effort
would require time accounting; counting files or lines would give a misleading
answer.

| Work area | Reusable contribution | Current adapter-specific part |
| --- | --- | --- |
| Ownership, geometry and image associations | SFC semantic source adapter; preserved positions, corners, groups and original image identities | SFC hooks/addresses stay game-specific; backend-generated resources are separate |
| Simulation tracking, camera and scene state | Persistent instance identity and coherent model/view/projection updates | Native96word rows still need the existing SFC decoder; they are not generic graphics matrices |
| D3D9 submission | Real VB/IB, texture bindings, world/view/projection and indexed triangle draws | Current production host creates its device through pinned Remix and uses vendor output APIs |
| Loading and performance | Shared geometry, parallel independent preparation, caching, early process creation and explicit readiness | Material USD publication/reload and runtime preparation are Remix-specific |
| Lighting | Native position/direction/RGB/activation observations and frame association | Remix light creation, radius/radiance approximation, user gains and dome interpretation |
| Materials and image quality | Original images and associations remain reusable | Roughness derivation, emission interpretation, tone mapping, bloom and quality controls currently target Remix |
| Replacement and return | Acquire/commit decisions, source/owner/asset identity, suppression ordering and resource leases | Current transfer/compositor use Windows D3D11 resources; target acquisition uses ReShade |
| Damage investigation | New SFC capability: per-owner selector/family, original pairs, generated mapping and first-use lifecycle | Live damage transport/submission is not implemented; its rendering blend must be adapted faithfully |

## The actual attachment points

```text
SFC semantic source adapter
  |-- fresh mesh / original image associations
  |-- persistent owners / simulation transforms / game camera
  |-- native light observations
  `-- damage observations (probe only so far)
          |
          v
Existing source IPC + SFC decoding + scene preparation
          |
          v
Ordinary D3D9 geometry submission
          |                          Remix-only side paths
          |<------------------------ material library + light/config APIs
          v
Pinned Remix renderer / completed output
          |
          v
Current D3D11 GPU transfer + native insertion adapter
          |
          v
SFC continues shields, effects and UI
```

The neutral scene view and source IPC are different boundaries. The former is
an existing offline/replay representation; the live path still carries SFC
rows and project coordination. There is not yet one portable public consumer
object that hides all those details. Do not add another redundant format merely
to rename that problem.

### Source and scene consumers

- [Fresh mesh capture](../../tools/m1_component/m1_mesh_export.h) preserves
  source positions, corner indices/normals/UVs, groups and material-resource words.
  Texture IDs/native addresses are same-session provenance, not durable asset IDs.
- [Persistent scene](../../tools/scene_bridge/persistent_scene.h) keeps simulation
  owners distinct from visibility and reusable geometry.
- [Scene preparation](../../tools/scene_bridge/scene_bundle.py) creates the
  existing replay `Scene` from capture packets, with original image provenance.
  [Scene view v1](scene-contract-v1.md) documents geometry, groups, matrices and
  replay files. Its original offline proof deliberately excludes lighting parity.
- [Live state decoder](../../tools/d3d9_proof/live_owner_decode.h) translates the
  qualified native17word arithmetic to effective column matrices. Native units,
  viewport and coherent camera remain explicit; no claim of metre-calibrated units.
- [Live multi-scene wire](../../tools/d3d9_proof/multi_scene_wire.h) carries coherent
  registry rows and asset catalog entries. Current capacity definitions are in
  [scene_capacity.h](../../tools/scene_bridge/scene_capacity.h):256owners,
  1,024asset slots. These are bounded implementation budgets, not unlimited coverage
  or the historical32owner limit in older documents.

### D3D9 consumer versus Remix consumer

[d3d9_replay.cpp](../../tools/d3d9_proof/d3d9_replay.cpp) defines the existing
`Vertex`, `Group`, `Frame`, `Scene` and `Renderer` types. Its renderer uploads
geometry/textures and calls `DrawIndexedPrimitive`. The plain system-D3D9 proof
already demonstrates a consumer without Remix; this supports reuse of the source
geometry and camera work, not full modern-material or live-output parity.

The D3D9 draw path deliberately disables fixed-function lighting and secondary
texture stages and submits primary textures. Native lights are **not all exposed
as ordinary D3D9 SetLight calls**. Roughness, recovered emission and other enhanced
material definitions are **not a complete D3D9 material interchange**. They reach
Remix separately. A consumer watching only D3D9 draws would miss that richer scene
meaning and the original per-owner damage selector.

[d3d9_direct_host.cpp](../../tools/d3d9_proof/d3d9_direct_host.cpp) is a combined
D3D9/Remix host: it registers the device, configures the runtime and copies vendor
output. It cannot be turned into an arbitrary backend by replacing one DLL or
renaming its executable. The [parallel asset coordinator](../../tools/remix_runtime/parallel_assets.py)
and [multi-scene relay](../../tools/remix_runtime/multi_scene_relay.py) also know
Remix coordinate policy, hashes, generated libraries and publication lifecycle.
These are the main remaining seams to isolate behind backend operations.

### Light consumers

[effect_lights.h](../../tools/scene_bridge/effect_lights.h) exposes a frame-keyed
native bank:64records, enable flags, global gate and capture time. This is free
of Remix SDK types but still contains SFC records requiring interpretation. The
known position/RGB/range/type semantics are not a fully calibrated physical-light
standard or a weapon-ownership API.

[effect_light_wire.h](../../tools/d3d9_proof/effect_light_wire.h) explicitly puts
conversion/configuration in `remix_effect_lights`.
[direct_effect_lights.h](../../tools/d3d9_proof/direct_effect_lights.h) creates,
draws and destroys actual Remix spheres. Preserve that distinction: source colour,
position and on/off state are reusable; sphere radius, power interpretation and
user gains belong to the chosen rendering adapter. Native spatial range is not
a duration or an inferred physical wattage. Scene directional/fill controls use
the existing separate light binding path; do not promise identical semantics
for all raw light types.

### Output and native replacement consumers

[gate_contract.h](../../tools/native_insertion/gate_contract.h) already defines a
versioned same-process `Dispatch` interface with acquire, commit and cancel;
tickets bind source identity and owner/model state. This is a real reusable
integration boundary. It still contains source-specific manager/list references
for native suppression, so it is not a general cross-process renderer ABI.

[cohort_contract.h](../../tools/native_insertion/cohort_contract.h) binds completed
scene membership to independent owner epochs. The current
[physical hull pass](../../tools/d3d9_proof/physical_hull_depth.h) supplies first-hit
hull depth and per-owner pixel coverage for supported opaque rigid geometry;
do not repeat the earlier audit's union-mask-only limitation for this mode.
That pass is adapter-owned D3D11 work, separate from Remix's reflected/refracted
surface-depth interpretation. Cloaking and arbitrary transparent geometry remain
unqualified by opaque hull coverage.

[output_channel.h](../../tools/d3d9_proof/output_channel.h) and
[game_output_wire.h](../../tools/d3d9_proof/game_output_wire.h) carry identity,
sequences, resource epochs and GPU handoff states. Today's handles/formats and
ownership implementation are Windows/D3D11-specific. D3D12 requires an explicit
transfer implementation; it cannot reinterpret these handles automatically.
ReShade supplies target/callback access through the
[return add-on](../../tools/remix_runtime/return_addon.cpp); it is not the source
of ship data or the ray-traced renderer.

## What other developers can use today

Developers can inspect and extend the published source, consume preserved mesh
packets with their matching associations, use the existing scene decoder/replay,
and study the qualified owner/transform/camera/transaction contracts. The plain
D3D9 proof is the smallest independent-consumer reference. Assets and runtime
dependencies must be supplied legally; proprietary captures are not in Git.

This is not yet a supported drop-in plugin SDK. Live startup is tied to the
project's session mapping layout, launcher environment, qualified process paths
and source-native records. There is no public stable capability negotiation,
complete backend lifecycle facade, independent live-renderer example or portable
installation. Documentation of source symbols does not silently establish those
guarantees. See the repository README's setup limitations before trying a runner.

## Exposure that still needs work

The smallest useful packaging increment should wrap existing operations rather
than create a new engine or an extra mandatory conversion stage:

1. Document one supported consumer entry over existing decoded assets/scene
   updates: canonical asset and owner identities, original images, geometry,
   coherent transforms/camera, lifecycle and source provenance. Keep original
   content identity distinct from Remix-derived cache keys.
2. Give backend operations an explicit home: prepare/cache assets, update owners,
   apply supported source lights/material state, submit, acquire completed output,
   release and stop. Move Remix material/startup assumptions behind those
   operations incrementally. This list is proposed work, not an existing API.
3. Document completed-frame semantics independently of native handles: colour
   encoding, dimensions, physical depth, per-owner coverage, source identity,
   completion and lease ownership. The current Windows transfer remains one
   implementation. Do not remove synchronization to make an interface look simpler.
4. Provide a small independent consumer/example against the same supported input,
   starting with existing plain-D3D9 replay and synthetic fixtures. It should not
   need SFC reverse engineering or a full second renderer to validate the boundary.
5. Publish a capability/support matrix. Unsupported lights, effects, transparency,
   deformation and partial observations must be explicit; opaque native words
   are provenance, not interpreted material features.

These are follow-up engineering steps. None was implemented by this review.
Performance mode must keep optional diagnostics/readback out of frame servicing.

## Damage and future effect triggers

The new damage evidence is reusable SFC work. It must become per-owner source
state, not only a hidden Remix material switch. [Run284](../runs/2026-11-03-codex-damage-observation-review.md)
qualifies standard F-CA selector/family, original pairs, independent mapping and
first-use ordering. At present it exists in the separate observation decoder;
it is **not published by the production live scene protocol**.

When implemented, retain the raw/current selector and family, selected severity,
owner/asset revision and source sequence. State changes can expose previous and
current values for optional downstream effects. This is proposed interface data,
not a newly implemented event schema. Initialization/re-entry should establish
state without fabricating a hit. A consumer must handle missed/coalesced updates
and the observed selector decrease; not every change means a fresh weapon impact.

The sponsor requests this extension point for additional damage effects later.
Current evidence does not supply per-hit location, weapon attribution, hardpoint
ownership or impact normals. Sparks at a specific impact point require more
source data. Damage illumination/blending must preserve original black-key intent
within this layer and leave ordinary black hull markings intact. Geometry reuse
must not merge different owners' damage states.

Damage display, destruction/break models, optional LOD and the broader effects
families remain distinct capabilities. Classified historical survey activity is
not the same thing as live transport/submission support for all those families.

## Disposition

The D3D9 foundation is real and much of the difficult game-facing work transfers.
The richer material/light/output path remains partly Remix/Windows-specific.
The exposure is sufficient to continue implementation from known source data;
it is not sufficient to advertise a stable renderer-agnostic SDK to other users.

Keep [SFC-07 / the renderer boundary gate](../decisions/2026-10-18-renderer-independent-boundary-gate.md)
open. Use this map before extending damage, and before freezing an alpha-facing
developer interface. No new SDK, rendering architecture, runtime refactor or
milestone closure is implied. Review only; no tests/GPU/gameplay runs were needed.

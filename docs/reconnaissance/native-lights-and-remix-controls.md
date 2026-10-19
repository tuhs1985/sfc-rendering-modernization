# Native lights and per-light Remix controls — active increment

2026-10-18;sponsor:identify in-game lights and feed them to Remix;provide editable
per-light controls,including strength and requested ray-tracing participation.
Implementation/evidence goals,not new CDD requirements or milestone exit criteria.
Baseline2fa8032;accepted textured additive return remains available unchanged.

## Sequence and boundaries

1. Observe native light bank at existing qualified owner/manager seam. Preserve
   raw types,enables,colour/scalars,position/direction,object-local derivatives,
   supplied transform and view,plus session/owner/model/frame. No new broad hook.
2. Classify actual active contiguous prefix and distinguish stable scene light
   from transient/owner-related sources. Slot0 is NOT assumed to be the sun.
   Compare camera-only and ship motion with captured transforms. Unknown native
   fields/types remain raw;do not invent photometric meaning or physical units.
3. Assign reviewed logical IDs backed by observed signatures/role evidence;store
   unresolved sources as session/bank/slot/generation identities. Raw pointers
   must not become cross-session config keys. Same bank observed under two owners
   is corroboration,not automatically two different lights to submit to Remix.
4. Add native-to-Remix light mapping only for qualified types/coordinates. Remove
   provisional inspection light only when native illumination is qualified.
5. Bind validated per-light config to that adapter,record applied values and
   capabilities. Config edits affect only returned Remix picture,not SFC memory.

## Config controls / capability rule

Planned user controls:enabled,intensity multiplier,RGB multiplier,position offset,
direction override,source size/angular size as appropriate,and requested per-light
ray-tracing/shadow participation. Support differs by light type/backend. Native
type0 record+28 is a multiplier;type1 +28 is distance/falloff,not universal power.
Initial brightness conversion is documented provisional,never physical calibration.

Pinned Remix1.5.2/SDK0.6.4 remix_c.h LightInfo/shape extensions expose radiance,
shape/location,size,volumetric scale and USD intensity/exposure parameters. **No
per-light shadow/non-raytraced toggle is exposed by this inspected public ABI.**
This establishes an interface gap,not impossibility in every future runtime.
`raytracing="renderer_default"` is the only currently qualified request. `off`
must fail validation clearly until a genuinely supported alternative exists.
Omitting a light removes its entire Remix contribution;that is enabled=false,
NOT the same as retaining illumination without ray-traced shadows. No silent
no-op field,global shadow change masquerading as per-light,or Remix-internals patch.
Future D3D9/D3D12 backends must qualify their own capabilities/units independently.

`tools/remix_runtime/config/lights.example.toml` is initially a validated schema
example,NOT active live controls. No fake native-light entries or guessed roles.
Runtime binding follows actual identification;reject unresolved IDs,duplicate
IDs,unknown fields,nonfinite/out-of-range values and incompatible shape controls.

## Discovery bounds / evidence

Proposed observer5Hz per owner,max2owner epochs,max900snapshots90s. Fixed raw
snapshot6156B,total<=5,540,400B before small file header;8-slot preallocated queue.
Stable double-read at qualified callback,skip inconsistent/busy;no waits,allocation,
disk access or SDK calls there. Worker emits bounded binary/provenance/summary;
16MiB combined new discovery evidence hard cap,8MiB warning. Existing32MiB overall
nontexture log and128MiB texture/five-minute workflow caps remain binding.
No continuous screenshots,geometry transcript or image dumps. Short<200ms lights
may be missed;first probe cannot claim exhaustive weapon-light coverage.

Run41 integrates a dedicated observer variant and tested launcher through
[NATIVE-LIGHTS-001](probes/NATIVE-LIGHTS-001.md). Accepted component binary remains
unchanged. Discovery launcher is ready;actual game-light evidence remains pending.

Success for discovery:numeric light records/enables correlate to actual owners,
direction/position transformations and on/off changes;unsupported semantics explicit.
Success for controls:per-light edits demonstrably change only mapped Remix lights,
logged application/reversal and normal game operation;unsupported ray controls
reported honestly. No native-light fidelity or formal TRL claim from a screenshot.

## Exact next implementation action

CurrentRun43:first two freshly observed type0lights wired to Remix in explicit
normal90s `start_light_wiring_session.ps1`;last-good live controls in config/lights.toml.
Offline qualified,actual wiring runtime pending. This supersedes discovery-only
next action below. Sponsor's second pass is longer,minimal recording,ending on
their normal exit;gated by first-pass review and NOT currently prepared.
No type5weapon lights or GI mapping silently added.

Run `tools/remix_runtime/start_light_discovery_session.ps1` from the established
elevated parent;familiar skirmish with brief camera/movement/fire,exit at two-beep
request. Adjudicate native values before enabling controls or supplying game
lights to Remix. Three-lights/GI remains a hypothesis,not a capture filter.

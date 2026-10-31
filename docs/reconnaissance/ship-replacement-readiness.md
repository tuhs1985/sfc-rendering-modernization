# One-ship return integration — readiness at 2026-10-17

## Current — Run215 physical hull depth, 2026-10-27

Returned colour remains Remix-rendered, including reflections. The existing R32
normalized-depth and union-coverage outputs now come from an adapter-owned
physical hull pass over the same cached meshes/poses; vendor PSR virtual depth
is not a physical hull mask. Full-output projection precedes the existing native
viewport mapping once. No wire layout,source-frame matching,suppression,lease or
fallback-policy change. New depth buffer is included in the128MiB output budget;
auxiliary cached geometry is charged to256MiB resident budget. Opaque rigid
triangles only. [Run215](../runs/2026-10-27-codex-physical-hull-depth-fix.md) records
captured-pixel/native/GPU/recovery qualification; sponsor visual checkout pending.
Older statements assuming exported Remix depth always means hull are superseded.


## Current — Run213, 2026-10-27: temporary fallback and automatic return

Initial player replacement was observed in gameplay; ordinary camera/delivery
gaps no longer permanently disable it. Protocol2 restores intact native drawing,
then automatically primes fresh paired output at a new generation and resumes.
Explicit shutdown remains disabled. Exact matching and resource ownership stay.
[Run213](../runs/2026-10-27-codex-player-replacement-auto-recovery.md) and
[v2 transaction](player-replacement-transaction.md) supersede old ordinary-failure
latch descriptions. Offline/native/GPU/legacy/tuning gates pass; sponsor recovery
and controlled-unload checkout remain pending. Same launcher/current settings.


## Historical — 2026-10-27 Run209: READY for sponsor player-replacement test

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

## Current — 2026-10-19 depth runtime PARTIAL

[Run67](../runs/2026-10-19-codex-scene-depth-runtime-review.md):native depth access
confirmed3646/3652frames;extra display only1060frames,severe sponsor-observed
flicker. Fix per-frame fresh-output-only delivery using safe raw-result caching
and current-depth filtering before retest. Low-placement suspicion unresolved.
Normal exit/unload/rollback/client hashes PASS;originals ON,no replacement claim.

## Historical — 2026-10-19 depth-first additive test READY

[Run66](../runs/2026-10-19-codex-scene-depth-preparation.md) and
[probe](probes/REMIX-SCENE-DEPTH-001.md):default-off native-depth filtering of the
extra copy,originals ON,existing UI callback retained.66native checks per arch,
283Python,14existing return gates and3depth callback cases PASS;preflight PASS.
Sponsor's UI/grid descriptions are direct observations;grid mechanics remain
unqualified. Extra may blink from fresh-output refusal even stationary. This is
depth diagnosis,NOT original suppression,steady replacement or milestone PASS.

## Historical — 2026-10-19 replacement started; offline foundation only

Sponsor authorizes replacement. [Run65](../runs/2026-10-19-codex-replacement-depth-foundation.md)
and [contract](ship-replacement-contract.md):exact-state admission and native8MSAA
depth compositor pass55checks in each architecture. NOT installed into SFC;
no original suppressed. Actual owner/batch-safe insertion and pre-UI/effects
ordering remain open. Existing stable1920x1080 textured additive output and R2
appearance baseline are preserved. Historical Run28 coarse/flicker description
below is no longer the current quality checkpoint. No new sponsor test ready yet.

## Historical — 2026-10-18 visible additive ship return demonstrated

[Run28](../runs/2026-10-18-codex-offset-copy-runtime-review.md):actual SDK ship
reaches SFC display,285visible submissions and sponsor sighting.953published,
667rejected;heavy flicker/coarse256² appearance. Normal exit/cleanup/hashes PASS.
No original suppression/replacement or milestone claim. Sponsor confirms original
scene/HUD not blurred;stable delivery and scene/UI visibility must
be addressed before suppression. Do not redo private/corner return demonstration.

## Historical — 2026-10-18 corrected beside-original copy READY

[Run27](../runs/2026-10-18-codex-world-offset-display-correction.md):sponsor rejected
inset. -VisibleShip now maps SDK output to native camera viewport,using existing
world-offset model position,so copy appears beside original. Original stays.
Offline projection/pixel IoU0.994603,69native eacharch/199Python,five GPU gates
and preflight PASS;new visible_camera_qualified guard. Actual gameplay test
pending. No source/pose/frame relaxation,scene-depth composition or suppression.

## Historical — 2026-10-18 first visible ship inset READY

[Run26](../runs/2026-10-18-codex-visible-ship-preparation.md):real private retest
continued OFF→ON,no old stall;947outputs/20matches still sparse. Sponsor directs
visible progress. Default-off-VisibleShip displays fresh masked magenta ship in
proven upper-right image-return region,not another window or world-aligned copy.
Original ships ON. Five offline GPU gates including actual visible512pixel check,
197Python/62native eacharch PASS;source/binary qualification and preflight PASS.
Actual sponsor sighting/HUD/control validation pending. No suppression/scene-depth
or smooth replacement qualification. Exact source-frame/pose rules NOT relaxed.

## Historical — 2026-10-18 publication recovery prepared;private retest READY

[Run25](../runs/2026-10-18-codex-publication-retry.md):producer retries Busy
publication without losing completed output;5s bound,exact frame unchanged.
62request/65triplet nativechecks eacharchitecture,195Python,four GPU gates PASS.
Read-only preflight PASS;fresh qualification pinned. Next90s private retest must
show continued progress beyond10s and after reenable. No on-screen copy yet.

## Historical — 2026-10-18 real private return PARTIAL;publication recovery required

[Run24](../runs/2026-10-18-codex-private-return-runtime-review.md):fresh FCA,
202published/68 exact-current private draw attempts,134 rejected,0 private failures.
Progress freezes near9.72s with one cancelled publication/Rendering lease1.
Publish-contention/unconditional inflight-clear defect is a STRONG HYPOTHESIS;
add deterministic regression and recover producer publication before more gameplay.
Normal gameplay reported;exit/restoration/unload/hash checks pass. No pixels exposed
to backbuffer,no original suppression. Sustained motion/OFF→ON recovery unproven.
SDK40 remains;52 component semantic rejections separate from private validation.

## Historical — 2026-10-18 fresh PRIVATE return ready for real-game timing test

[Run23](../runs/2026-10-18-codex-fresh-private-return.md) and
[contract](ship-live-return-contract.md):fresh asset/SDK host/current-state native
receiver implemented,actual copied-proxy callback qualified offline.41native
checks eacharchitecture,195Python,private GPU maskIoU1.0,slow/disconnect gates PASS.
Rebuild/qualification/preflight verified. Next sponsor -PrivateShip workflow
uses90s with automatic cues;NO visible copy expected. Source frame/pose equality
not weakened to display old pixels. Original ships/HUD remain untouched.
Actual SFC deadline,normal behavior/cleanup and moving-pose output fidelity remain
pending;on-screen offset composition/UI/occlusion are subsequent gates. SDK40 open.
No replacement or milestone PASS. Older readiness/qualification text below is
historical;current probe's source/binary guards govern launch.

## Historical preceding step — offset and opaque masked composition qualified offline

[Run22](../runs/2026-10-17-codex-ship-offset-compositor.md) and
[REMIX-OFFSET-001](probes/REMIX-OFFSET-001.md):actual world-offset FCA output
passes projection/depth and x86 masked compositor checks;source geometry/camera
unchanged. Wirev3 explicitly identifies diagnostic offset.65nativechecks each
architecture,22GPUchecks,188Python PASS;slow/exit faults refuse reuse. No addon
adoption/live requests/UI ordering/scene occlusion or suppression qualified.
Original ships ON. No game test ready;next adopt receiver with fresh state and
offline lifecycle/UI validation. Default fixture material dark,not appearance
proof. SDK teardown warning persists;no milestone completion claim.

## Historical preceding step — coherent64bit→32bit triplet transfer qualified offline

[Run21](../runs/2026-10-17-codex-ship-triplet-return.md),
[contract](ship-triplet-return-contract.md):actual Remixcolor/mask/nativeZdepth,
12/12plane deliveries exact into separate32bit10_1consumer across2poses/two
sequences each. Versioned source+return session/owner/revision/frame/pose/camera/
resource identity;ACK only after receiverGPUcompletion. Slow/exit faults give
no accepted packet/no overwrite. Native56checks botharchitectures,184Python PASS.
Next adopt default-off receiver in copied-game presentation path with original
ships ON;qualify state/lifecycle and live output timing before gameplay/suppression.
No real-addon/fullsize/resize/visibility/UI/composition PASS yet;SDK40warning open.

## Historical preceding step — corrected native-Z replay qualified through actual runtime

[Run20](../runs/2026-10-17-codex-native-depth-conversion.md):three fresh captured
FCA poses replayed with corrected SDKnear=b/a. MaskIoU1.0all3,medianZerror
<4.33e-7. Deliberately oldnear keeps mask but reproduces.01237depth mismatch.
72/72GPUtransfers,24/24IDdecodes;no SFC launch. This closes the depth-conversion
question for this supported camera/asset,not visibility/occlusion or replacement.
Next bounded multi-output/frame-valid return contract into game-side consumer;
keep original rendering enabled. No repeat gameplay or light/appearance tuning
needed for conversion. SDK40warning remains open despite normal process exits.

## Historical preceding step — contemporaneous capture demonstrated;native depth conversion identified

[Run19](../runs/2026-10-17-codex-present-calibration-runtime-review.md):both fresh
KFF/FCA owner/model/camera records pair to3native depth/color submissions with
same engine frame/thread/session. Normal operation,exit/removal/rollback/hashes
PASS. FCA projected outline aligns and~98%interior matches native depth;KFF is
too small for reliable interior measurement. Native depth follows screenZ,not
old SDKhalfZ+.5. Algebra derives near=b/a≈1.99993 instead of≈1.0,samefar;next
test this through actual pinned SDK offline before suppression. No new gameplay
or appearance tuning needed now. Residual~2%,MSAA/other-content/UI/effects and
visibility remain unqualified. Warnings54/67/40open;no milestone PASS.

## Historical preparation — contemporaneous calibration READY,not yet live-proven

[Run17](../runs/2026-10-17-codex-present-calibration-preparation.md) and
[REMIX-CALIBRATION-001](probes/REMIX-CALIBRATION-001.md) prepare3paired native
depth/color plus fresh owner/model/camera records. Current-frame table bypasses
30Hz stream sampling;draw/Present/session/thread/revision provenance checked;
stale or ambiguous state rejected. Offline10_1 GPU/provider and producer tests,
170Python regressions,current-source native callback/depth qualifications PASS.
Run `start_return_image_session.ps1 -Calibration`,not unmodified -DepthSnapshots.
Original draws remain visible;no Remix/Toolkit/suppression needed. Live alignment,
occlusion/UI/fallback and synchronized output remain unproven;warnings67/40 open.

## Historical preceding step — standalone runtime ship coverage/depth + camera conversion qualified

[Run16](../runs/2026-10-17-codex-remix-depth-coverage.md) directly renders captured
FCA geometry through SDK (no Toolkit). Native10_1 GPU transfer and shader ID-bit
decode verified;color/depth/picking share one produced frame. Normalized depth,
background and controlled owner retirement/reappearance qualified. Historical
native model/camera replay exactly matches projected478pixel mask and median
depth within1.8e-7. See [qualified contract](remix-depth-coverage-contract.md).
Not textured appearance,material/cull fidelity,live synchronization or suppression.
Need ONE same-live-frame selected owner/model/camera/native-depth calibration
capture;Run15 has no paired semantic fields. Preserve original renderer until
that and frame-matched output/coverage/UI handling are qualified. No new gameplay
runner prepared this step. Runtime40-object and native67-reference warnings open.

## Current — actual tactical depth contents demonstrated

[Run15](../runs/2026-10-17-codex-depth-content-runtime-review.md):three paired
SFC depth/color captures show ship silhouette+grid matching camera change;
native depth state and valid nonuniform values corroborate use. Normal behavior,
exit/rollback/hashes and bounds passed;reference warning67 remains. This resolves
"is there usable-looking tactical depth content?",NOT safe original-ship suppression.
Next offline test must qualify selected-ship Remix coverage/depth plus projection/
coordinate/frame relationship before replacement. Keep HUD/effects/other-owner
coverage and8sample handling explicit;no pixel-exact registration claim from
half-size diagnostic PNGs. No further broad discovery run needed now.

## Latest — corrected10_1 reader ready for sponsor retry

[Run14](../runs/2026-10-17-codex-depth-fl101-correction.md) replaces probe compute
with a compatible private pixel-shader pass,not a new game renderer. Exact10_1
native/callback tests passed including8sample and XY gradient checks;152Python
regressions pass. Original mode/settings remain unchanged. -DepthSnapshots retry
prepared;actual SFC content still unqualified,one-ship suppression not authorized
by this evidence. Older no-retry disposition below applies to the superseded
SM5 reader,not this qualified correction. Native warning67 remains unresolved.

## Current result — depth probe compatibility correction required

[Run13](../runs/2026-10-17-codex-depth-snapshot-runtime-review.md):actual test
saved no images,one GPU failure before submission. SFC requests feature level
10_1,but probe shader needs11_0-class capability. Exact API/HRESULT unlogged;
shader-creation rejection is STRONG HYPOTHESIS,compatibility mismatch CONFIRMED.
Next offline qualification must explicitly use10_1 and a compatible read-only
extraction path. Do NOT rerun unchanged depth or broad capture. Normal exit,
rollback and hashes passed;native warning67 remains open. No suppression justified.

## Latest preparation — focused content test READY,not runtime proof

[Run12](../runs/2026-10-17-codex-depth-snapshot-preparation.md) and
[REMIX-DEPTH-001](probes/REMIX-DEPTH-001.md) prepare three paired depth/color
snapshots plus actual native depth-state observations. Synthetic distinct8sample
content and actual full-support callbacks passed;original state restored,negative
case emits no guessed depth images. No SFC launched. Next action is prepared
`-DepthSnapshots` run and image correspondence analysis,not repeated broad logging.
Depth direction/coverage,ship visibility,owner association and suppression remain
UNPROVEN. Native SFC cleanup warning67 remains open.

## Current conclusion — broad event discovery supersedes narrow getter work

[Run11](../runs/2026-10-17-codex-broad-depth-runtime-review.md) actual182017 run
found persistent1920x1080/8sample/R32_TYPELESS depth resource,D32_FLOAT view and
R32_FLOAT shader-readable view. Bound during67,290draws;unbound at all600Present
notifications. 599complete frames have2later non-depth draws before final
presentation;their HUD/composition identity is not proven. Earlier bound-getter
absence cannot establish depth was destroyed or unavailable by retained identity.

Next smallest step:one bounded read-only content snapshot plus static depth-state
observation,with explicitMSAA handling and fresh lifecycle discovery. No generic
full-rate trace repetition needed. Depth values,ship/camera correspondence,
coverage,HUD ordering and safe owner suppression remain unqualified. Full-support
cleanup reference warning67 open. No one-ship replacement or milestone PASS.
Older "current smallest experiment" below is historical/superseded,not an active
instruction to repeat late/early getters or replace proxy again.

Authority: approved In-Game Remix Integration plan, gate2 only after additive
returned image. Sponsor authorized cleanup edits and proceeding. This document
narrows execution to missing relationships, not a new renderer architecture.

## Evidence-supported path and limits

CONFIRMED: semantic owner004162B9 ->visual0042FD3F ->tModel0 mesh0042E4B2,
selected-child return0042FDD5. Existing observer preserves registers/flags/FPU/
SIMD with pushad/pushfd/fxsave/fxrstor and ALWAYS jumps to original trampoline.
It does NOT already implement a qualified suppression branch. Returning early
from model rendering would need explicit ABI/stack and state-side-effect review;
do not infer it from the existing successful tint or private data-copy test.

CONFIRMED: fresh mesh/assets/lifetime32owner transport and camera alignment work
in separate viewer. Contract is ASYNCHRONOUS sampled30Hz,not a matching whole
render-frame replacement contract. New returned-image v2 carries only diagnostic
sequences/device epoch,not ship owner/asset revision/pose/view/projection/viewport.
The working triangle cannot be resized over a ship and called replacement.

CONFIRMED: pinned SDK enumerates CopyRenderingOutput DEPTH and OBJECT_PICKING
(remix_c.h741; implementation rtx_remix_api.cpp1434). These are runtime-return
capabilities,not qualified transferable SFC-depth surfaces. First object-picking
request merely enables retained output and returns success without a current
copy; API return0 alone is NOT valid coverage evidence. Format conversion,
empty/background sentinel,output freshness and owner ID must be tested.

CONFIRMED: installed limited ReShade permits supported overlay/runtime callbacks
but blocks external application draw/depth-binding events (pinned
addon_manager.cpp572). Do not bypass that restriction or replace proxy silently.
Our callback adds a noninteractive UI-background image late in presentation.
It currently has no qualified tactical-depth/coverage input and no proven
pre-HUD insertion/occlusion control. Native immediate-context getters are
available read-only within that allowed callback; determine what survives there
before proposing another interception point.

## Minimal replacement contract to satisfy, not assumed implemented

Same session,owner epoch,asset revision AND complete supplied/composed/view/
projection/viewport signature; output-device epoch and GPU-readiness must match.
Frame sequence joins semantic observation to output. A stationary test can
reuse only explicitly identical state, not merely a recent30Hz record. Movement
requires current accepted state; on miss retain original, never old pixels.

Runtime ship coverage must come from qualified geometry/ID/depth,not black RGB
or bounding-box cutoff. Retained scene visibility and tactical UI need a proven
composition boundary/depth relationship. Shields,weapons,explosions,other ships
remain explicit uncertainties. Suppress only a qualified matching ship when
replacement and visibility pass together; any missing predicate leaves original.
No generalized renderer or appearance work needed to answer these questions.

## Current smallest experiment

Default-off eight read-only DSV descriptor samples at late overlay after tactical
gate, using existing copied-install runner `-InspectVisibility`. See probe
REMIX-RETURN-001. This avoids speculative GPU interception just to see whether
the existing insertion point already exposes useful depth. No SFC originals
modified and no original ship suppression. Positive descriptor still does NOT
qualify depth contents; zero observations of bound depth mean inspect ONE earlier
scope,not declare no depth exists or rebuild translators. Offline fixture checks
bounded no-depth case before sponsor gameplay. Stop for that runtime evidence;
do not offer an unsafe replacement build while this relationship is unknown.

Status: RETURN PATH DEMONSTRATED; one-ship replacement NOT demonstrated.
ADDITIONAL BOUNDED EVIDENCE REQUIRED, not architecture infeasibility or milestone
completion. Cleanup warning investigation separate from this visibility question.

Runtime update2026-10-17: [late-depth review](../runs/2026-10-17-codex-late-visibility-runtime-review.md)
confirms8checks/0boundDSV in actual skirmish,normal sponsor gameplay. Late bound
DSV route not available in this sample. Next locate an earlier supported scope
and establish ordering before probing; no inference that SFC has no scene depth.
No repeated unchanged late probe,original suppression or black-background cutout.

Earlier-scope preparation2026-10-17: public addon_event::present runs before
ReShade effects (not necessarily before SFC HUD). Offline known depth8/8 and
no-depth8/0 corroborate exact active-device/window/backbuffer filtered getter;
descriptor is still not scene-depth qualification. See
[preparation record](../runs/2026-10-17-codex-early-depth-preparation.md).
Next SFC run uses -InspectEarlyDepth -ObservationOnly: no Remix load/triangle,
read-only control channel. Default full-runtime regression hit intermittent
nvoglv64.dll617.42+0xF10CF4 crash even with default material; unresolved renderer
stability risk,not hidden by passing read-only tests. No ship suppression until
visibility/frame qualification and renderer stability are addressed.

Actual early runtime150957-452095:8samples/0DSV,normal sponsor gameplay,control
host/game/controllerexit0,unchanged hashes. Both presentation getters now negative;
do not repeat unchanged tests. [Adjudication/next candidate](../runs/2026-10-17-codex-early-depth-runtime-review.md)
identifies engine scene-end call0069E41B after flush0069E40B as a materially
different sampling candidate. No new hook installed or next runner prepared;
safe getter connection/ABI review required before that runtime observation.

Expanded search2026-10-17 now prepared/offline-validated: [record](../runs/2026-10-17-codex-expanded-depth-search.md).
-SearchDepth watches six engine/presentation phases for full90s,counts missing/
skipped calls and retains32resource/view descriptors without owner/size/name
filters. CPU/FPU/mid-call stack and concurrent detach tested in native stand-in;
actual SFC path untested. Still not exhaustive native binding/resource inventory,
nor usable depth/visibility proof. Next sponsor test has no visual change and
no Remix load; original rendering and diagnostic geometry-off policy preserved.

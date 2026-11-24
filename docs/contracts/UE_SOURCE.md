# UE retained source consumer

Experimental backend adapter upstream of D3D9. The source DLL, original assets
and Remix adapter remain unchanged. This is not a stable public SDK or native
insertion authorization. See the [interface control document](../D3D9_INTERFACE_CONTROL.md)
and [GPU export contract](UE_EXPORT.md).

## Existing source boundary

`source_scene_view.h` and `source_scene_channel.h` open the existing protocol4
16 MiB mapping with FILE_MAP_READ, holding the source process through a
SYNCHRONIZE-only handle. The version3 frame store, immutable asset catalog and
512-byte owner-state slots keep their existing layouts. Native tests compare
the consumer types and offsets against the actual writer. No UObject or GPU
type enters those shared records, and game addresses are opaque labels.

Common protocol4 word 3 is worker status (0 passive, 1 running, 2 stopped,
3 failed), **not the game PID**. Exact process identity comes from the scene
store's PID and the held process handle. See the
[live-startup correction](../runs/2026-11-23-codex-ue-worker-status.md).

A coherent frame supplies source frame/sequence, original model/view/projection
and viewport. Preserve native units and column-vector matrices. UE's documented
basis/transposition conversion runs only in the world adapter. Neither Remix's
UV conversion nor generated materials enter this reader.

**Sponsor observation, November 23:** UE's first textured live view has exactly
the same flipped appearance as the initial Remix integration. This is evidence
for a shared SFC UV/image-origin convention at the source-to-renderer boundary.
The precise cause (UV convention, decoded image row origin, or their interaction)
is not established. The historical description "Remix-specific" records where
the original correction was applied; it does not establish that Remix alone
requires normalization. Qualify each adapter against native appearance and keep
original UVs/images unchanged in the neutral interface.

Sponsor clarification: the conversion is already available from the accepted
Remix work: U unchanged, V = 1 - V, or equivalent vertical image-row reversal.
Reuse that known conversion once inside the UE adapter and verify its output;
another conversion-discovery pass is unnecessary. Do not apply both UV and
image-row reversal or alter the neutral source data.

Implemented policy: `ue_texture_origin.h` performs the once-only row reversal
into UE's transient texture upload buffer. Source UV arrays and original image
bytes/files stay unchanged; there is no additional shader or UV correction.
The existing Remix adapter is unaffected. See the
[native and packaged GPU qualification](../runs/2026-11-23-codex-ue-texture-origin.md).

Catalog slot guards publish assets. **Header `asset_ready` is a downstream
admission receipt, not a producer notice.** Waiting for it bootstraps the consumer
from its own acknowledgement. The reader scans unseen immutable slot guards at
source-consumer rate and validates each published descriptor once. It never
writes an acknowledgement or waits for SFC. The selected backend owns the
meaning of its prepared resource fingerprint; ordinary D3D9 and UE are not
simultaneous catalog consumers in the intended live parent.

Camera visibility never ends object lifetime. State=2 retires the source epoch.
The pinned producer also reassigns a state slot only after its prior owner
retires (`m1_live_scene.h`, owner-table allocation). A changed epoch in that
same slot therefore retires the previous epoch even if the intermediate state=2
was coalesced away. Source identity remains session plus owner epoch; reused
model/source labels do not inherit an old actor or pending work.

## One-time asset admission

The neutral Python facade preserves original arrays and image associations.
`scene_definition.py` publishes the existing local UE definition schema,
atomically, after base images exist. The first definition contains original
geometry and decoded BGRA images. Further owners of that same content publish
only their owner/revision, source binding, initial frame and a sibling
`asset_reference`. No geometry or image payload is rewritten per frame.

References are one level, within the same directory and source session/content.
A cold consumer resolves the referenced definition. A consumer that already
owns the content loads only binding metadata, without geometry decoding or
image I/O. This is private backend working data, not a changed source wire or a
saved ship template. Original image identities and primary/secondary associations
remain available; only primary colour is rendered in this UE increment.

The native descriptor and local definition must agree on session, source PID,
owner epoch, revision, opaque model/source identities and content. Admission
does not depend on assertions. A rejected asset leaves previously admitted
objects intact and does not terminate the source game.

## Session and world ownership

`USFCSessionSubsystem` owns the live reader, retired epochs, bindings and
GC-tracked geometry/texture/material resources. Geometry identity is independent
of material content. Decoded texture identity includes hash, width, height and
format. Material revisions bind original group IDs to the retained mesh's
section slots; enumeration order is not a material-slot identity.

`USFCWorldSubsystem` owns actors and the source camera. Each living owner keeps
its own pose and requested/applied revision while sharing cached resources.
An unavailable revision or explicitly unqualified source pose is ineligible
until its exact binding or qualified pose arrives; it does
not destroy the owner or block unrelated eligible actors. Readiness checks only
eligible actors. Later material arrival updates bindings without rebuilding
geometry. World recreation disposes actors and reuses session resources and
retirement knowledge. Retiring one owner preserves assets shared by others.

The public `USceneCaptureComponent2D::CaptureScene()` in the pinned UE 5.8.4 calls
`World->SendAllEndOfFrameUpdates()` before submitting its capture. The adapter
uses that established path instead of an added flush, guessed warm-up count or
source refresh cap. Resource admission remains on the game thread; CPU source
receipt does not access UObjects.

## Qualification scope

Development and Shipping replay verify independent shared owners and camera/pose motion,
offscreen return, delayed material revisions, retirement, stale work, pointer
reuse, source-session rejection, state-slot reassignment and world recreation.
Actual pixels are compared against an independent source-space rasterizer;
matching receipts alone do not qualify output. Synthetic texture-view and group
order cases test cache identity without editing original images. Fourteen stages
also cover binding-only admission and an actual captured break-piece geometry
revision. That derived revision has no invented parent relationship across captures.

The [November 23 record](../runs/2026-11-23-codex-ue-retained-scene.md) separates
verified lifecycle results from representative-count timing and live-parent work.
GPU return to the native game pool remains a later boundary.

## Explicit read-only live parent

The separate inspection window displays the tactical target as opaque RGB using
public Slate `IgnoreTextureAlpha`, centered with uniform aspect-fit scaling.
Its black panel masks the unrelated default UE viewport. This is presentation
only: capture inverse-opacity alpha, source viewport offsets, camera and native
GPU output semantics remain unchanged. `SFCInspectionCheck` is an explicit
diagnostic actual-widget pixel test; it adds no readback to normal inspection.
See the [inspection record](../runs/2026-11-23-codex-ue-inspection-display.md).

`source_service.py` is selected only by the development UE observation launcher.
It reuses the ordinary session's startup, verified copied-game process, native
component/configuration, transactional proxy restoration and recovery. The
existing neutral Receiver consumes/acknowledges transfers; the service prepares
one original base definition per binding, then publishes its immutable catalogue
entry. UE itself remains FILE_MAP_READ. There is no active D3D9/Remix renderer,
game-pool output, native insertion authorization or suppression in this mode.

The existing cohort producer needs an explicit scheduling anchor before it can
publish frames. The parent selects one admitted, live owner/revision through
the existing aligned selection cell. This is a scheduling anchor, **not** player
identification or replacement authorization. It changes only when that binding
no longer has a live row. The UE-selected catalogue's replay fingerprint is the
original packet SHA-256 prefix; the image fingerprint hashes original decoded
SHA identities. Ordinary D3D9 prepared-file fingerprints are not substituted.
The definition is fully published before its catalogue guard becomes ready.

`-SFCParentPID` holds an additional public UE process handle. Supervisor exit,
source exit or source stop ends inspection without waiting for an asset. Exit
and Escape remain available. The source parent treats unexpected UE exit as
unavailable even when the OS exit status is zero; it never enables native output
or suppression. Normal shutdown requests source stop before releasing the view.

The read-only preflight and actual transfer-to-Shipping fixture pass. Three
fresh process sessions cover passive cancellation, supervisor death and immediate
relaunch. Actual live source/camera continuity still needs sponsor checkout;
task 3.5 stayed open until that result was recorded. The final sponsor checkout,
UTC-named `20261124-011346-171859-in-game`, now passes aligned textures and
centered viewer presentation, with 3042 source observations and verified normal
cleanup/restoration. Task 3.5 is complete; native game-pool return remains next.

## Native return preparation — November 23

The read-only source facade now exposes the existing native target notice
independently of assets. Its layout is compared against the native writer;
reads use bounded sequence/checksum/PID/session checks and never mutate the
mapping. Live snapshots preserve complete source-frame seals, selected anchor/
revision and original camera/pose hashes for the output adapter. A row-state hash
is not interchangeable with the sealed-frame checksum required by native gate
tickets. Original poses remain unchanged by diagnostic world translation.

SFCGameOutput and the owner-only world capture helper are compiled foundations
for task 4.2, not yet connected to the live inspection loop or qualified as
in-game insertion. The parent must select the unique configured player fixture,
not infer player identity from the existing first-live scheduling anchor.

## Cancellation before native attachment — November 23

The existing session-owned stopped flag is honoured while the worker is still
passive or its native PID remains unclaimed. A passive stop requires the existing
valid same-session header and zero-or-matching PID. Running wrong-PID or wrong-
session input remains rejected. No new layout, flag or ownership is introduced.
This prevents a failed controller startup from leaving the UE reader waiting
until the parent forcibly terminates it. Actual packaged additive lifetime tests
cover both pre-attachment states, ordinary passive cancel, parent death and
fresh-session relaunch with no source assets.

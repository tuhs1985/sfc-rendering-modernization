# Fresh private return — experimental contract

**Durable architecture constraint:**the sponsor-directed
[renderer-independent boundary gate](../decisions/2026-10-18-renderer-independent-boundary-gate.md)
is OPEN. This experimental contract is not yet a validated renderer-neutral
baseline. Isolate SFC scene capture from Remix/backend details before architecture
freeze;DX12 is not a mandatory intermediate. Current bounded return tests continue.

2026-10-18;[probe](probes/REMIX-LIVE-RETURN-001.md),
[Run23](../runs/2026-10-18-codex-fresh-private-return.md).
## Current correction — world-offset copy in native camera viewport

**2026-10-18 actual visible return demonstrated:**[Run28](../runs/2026-10-18-codex-offset-copy-runtime-review.md)
records285visible submissions/sponsor sighting,heavy flicker/coarse256² output;
953published/667rejected. No smooth delivery,retained-scene occlusion or
suppression claim. Sponsor confirms only added ship coarse,not original scene/HUD;normal
exit/restoration/client hashes confirmed. Remaining contract limitations below
still apply;this is not one-ship replacement or milestone closure.

[Run27](../runs/2026-10-18-codex-world-offset-display-correction.md):sponsor rejects
inset placement. Optional-VisibleShip now scales the COMPLETE rendered SDK camera
image to captured native viewport(x,y,w,h),not a corner or whole-window fit.
No new2D displacement. Existing explicit key.worldOffset is already applied by
SDK DrawInstance to original native model pose;copy projects beside original.
Offset is fixed WORLD translation chosen at first qualification,not screen-fixed.
Bounds validated against actual display;unsupported rectangles omitted. Original
owner/source/camera/pose/current-frame/lease rules and transparent target unchanged.

Visible qualification now requires matching camera projection (IoU>=0.95),not
just corner pixels. Independent oracle honors nonzero viewport and bilinear alpha
sampling. Five gates requalified;actual game placement pending. Original ships
remain enabled. Additive copy has no retained-scene depth or HUD-annotation
occlusion qualification;not owner suppression/replacement or milestone closure.

## Historical / superseded inset implementation

**Visible diagnostic inset was prepared,not executed in SFC.**
[Run26](../runs/2026-10-18-codex-visible-ship-preparation.md):private retest
continued both enabled windows (947outputs/20admissions),no old stall. Sponsor
authorizes first visible ship despite sparse strict-frame admissions.
Optional-VisibleShip uses late ReShade image stage to draw private RGBA SRV
in same256square upper-right region as accepted triangle. Background alpha0,
picked finite-Z ship pixels alpha1;no rectangle cutout/scene occlusion claim.
Display key/time retained from actual admission;late callback independently
rechecks current source identity/frame/pose/camera. No accepted-frame relaxation,
stale image hold or retarget. Original ship remains. Default private mode still
has no backbuffer output. New visible callback/pixel gate required for visible
workflow;both modes require matching source/binary qualification. This inset is
not a spatially aligned copy,full-scene representation or replacement contract.

Historical recovery preparation:
[Run25](../runs/2026-10-18-codex-publication-retry.md) distinguishes transient
Busy publication from cancellation/invalid state. Producer retains completed
surfaces and pending ownership on Busy,retries outside SFC up to existing5s
request deadline;does not re-render or overwrite. Cancellation releases pending;
invalid lease is explicit failure. Legacy bool publish API retained for older
fixtures;wire layout unchanged. Native forced-contention regression corroborates
mechanism;actual SFC stall cause and sustained recovery still require retest.

## Roles / scope

Existing unchanged x86 semantic observer supplies per-frame calibration mailbox
and protocol3 asset/worker bridge. Geometry firehose OFF. Python worker receives
new asset packets,validates owner/model/source/revision and prepares one corner
mesh/seed. Actual game mode has no old Klingon/template fallback;offline synthetic
qualification intentionally uses recorded geometry as fixture input only.

New x64 ship_live_host uses pinned Remix1.5.2/SDK0.6.4,reads current mailbox,
draws one fresh revision with diagnostic magenta material/fixed sphere light and
returns color/depth/picking. NOT original lighting/textures or appearance proof.
New SFC_LIVE_RETURN x86 addon uses existing copied proxy's public pre-Present
callback and independently checks current same-process state. Draws to ONE
PRIVATE256square target,never game RTV/backbuffer/ImGui. Original ships/HUD stay ON.
One revision/run;unsupported,too-small/clipped assets are partial,not substitutes.
Model/source/LOD change stops eligibility;no deforming-mesh/universal coverage.

## Layout / engineering adjudication

Current-user4096B GUID mapping passed explicitly:control256B at0;tripletv3
Wire496B/Key152B at512;new version1 Command592B at1024;Registration184B at1792.
Command carries QPC,key,96native DWORDs,counters. Seed176B binds source-session/
PID/owner epoch/revision/contentSHA/model/source/LOD and prepared-mesh FNV. Native
model/source words are opaque identity comparisons,not external dereferences.

Try-Interlocked guards only,never cross-process SRWLOCK. Calibration header's
older same-process comment describes Run19 use. This increment deliberately
qualifies an external reader of its aligned shared-memory Interlocked guard.
Windows documents cross-process use for shared variables:
[Interlocked variable access](https://learn.microsoft.com/en-gb/windows/win32/sync/interlocked-variable-access).
x86/x64 tests and cross-process GPU fixtures corroborate it;failed locks skip.

Snapshot header/reserved/count/session,selected current owner/frame/thread,
model/source/revision/LOD,finite data and math dispatch must qualify. Key/row must
agree on owner/revision/frame and raw hashes. Native17word affine flag is honored,
not cast to a standard matrix. SDK camera retains Run19/20 basis and near=b/a.

Exact frame/pose/camera equality is NOT relaxed for stationary ships. IDLE only
reservation;all3copies plus producerGPU EVENT before READY. Native receiver pins
resources/LUID,claims exact CURRENT key,draws picking bits/valid nativeZ privately,
ACKs after consumerGPU completion. Changed/expired state rejected. Native source
frame and SDK latency logged separately. Private target cleared each attempt.

No files,readback,conversion,shader compilation or waits in game callback. Resource
creation at runtime init,before tactical capture. Deferred command-list work may
entail normal driver allocation,not a zero-driver-allocation claim. Producer
process opened once;nonblocking liveness check stops admission on disconnect.
Pending GPU completion can drain after stop. No hot-unload:normal teardown/exit
only. Device recreation stops channel rather than reopening old epochs silently.

## Evidence / remaining uncertainty

CONFIRMED offline:real SDK output into x86 private draw;512pixel mask matches
independent shifted native projection(IoU1.0). Actual copied-proxy callback uses
same receiver/preserves tested topology;Run22 covers broader compositor state.
Synthetic frame initially held,then advanced to test rejection. This is NOT the
real SFC frame budget or continuously moving-pose pixel-provenance proof.
Retirement means no NEW private draws,not on-screen hiding. Reenable precedes
final retirement;retired epochs never resurrected.

C material bug:alphaTestType0 rejected ray-traced surfaces while picking survived;
7 restored color/depth. Runtime A/B supports local SDK helper/implementation:
[official helper](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/public/include/remix/remix.h).
Only pinned C header compiled. Added light alone did not fix it;no SFC light data.

Real-game timing/admissions,normal behavior/exit and lifecycle remain next test.
Zero timely images is PARTIAL,not permission to accept stale pixels. UI/scene
occlusion and actual offset ship insertion remain subsequent gates. No milestone
completion or replacement claim.

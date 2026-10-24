# D3D9 retained multi-ship increment — implementation contract

## CURRENT launch-time initialization / comparison policy — Run130,2026-10-23

[Mode/activation contract](pipeline-modes.md) and [Run130](../runs/2026-10-23-codex-launch-time-renderer-baseline.md)
supersede startup-only-after-assets statements below. Verified copied-game launch
starts the SAME real native renderer; no-scene device/output initialization then
idle wait, followed by immutable session-bound activation after full initial
material publication. No dummy assets or earlier discovery. Performance skips
additional native upload readback comparisons; Test retains them. Essential
identity/bounds/fences unchanged. Existing24bootstrapPresents and asset-dependent
runtime work remain; total sub2s not achieved. No visual baseline change.

## CURRENT evidence policies / budget accounting — Run128,2026-10-23

[Performance/test mode contract](pipeline-modes.md) supersedes always-on evidence
and per-asset whole-history scanning described below. Performance is the public
launcher default; Test is explicit. Functional identity/scene/lights/GPU fences and
cleanup remain, appearance unchanged. One pregame historical inventory plus
session reservations/actual committed-byte ledger replaces worker global scans.
Sub2s end-to-end remains unachieved; earlier discovery deferred. No safety waiver.

## Work classification and performance audit — Run127, 2026-10-23

See [pipeline work/safeguards/diagnostics audit](pipeline-work-and-diagnostics-audit.md)
for the active-path inventory, actual vs proposed disable controls, mixed evidence
dependencies and measured historical-inventory/lock bottleneck. This documentation
does not change any runtime flag, safety bound, appearance baseline or CDD gate.
Earlier discovery is deferred; current target is sub2s fresh-asset readiness, not
an asserted achieved result. Do not turn off core live-mode flags to suppress logs.

## CURRENT startup/preparation — Run125,2026-10-23

Four bounded Python worker threads now identify/prepare/hash independent captured
assets outside SFC and outside the receiver coordinator. At most four tasks are
executing;at most64small job descriptors,with decode results prioritized into
preparation before more large decode jobs. Content qualification is committed in
first-observed order;duplicate content coalesces onto one conversion with no worker
waiting on another worker. One coordinator owns material conflict checks,ledger,
catalog publication and owner aliases. D3D9 device work remains on its owning
native worker;no new work in game callbacks and no artificial render-Hz cap.

The observed initial set seals after >=750ms with >=200ms without a new identity,
or after2seconds maximum discovery interval. This is NOT loading-screen inventory:
objects not yet offered by the render seam are unknown. Wait for this set's
preparation with25second watchdog inside existing30second first-image/285second
workflow limits. Prepared additional entries may join the initial publication if
ready before launch;unready late arrivals do not extend the startup set forever.

All initial material layers are finalized under gpu/assets/<id>;the aggregate
library is written atomically ONCE before starting Remix. Immutable same-volume
bootstrap hardlinks avoid another geometry/image copy. An explicit64-bit initial
catalog mask is passed to the native host;only fresh matching output is admitted
after every initial catalog entry has resolved GPU admission. Failed GPU entries
remain explicit PARTIAL,not an infinite wait or substituted ship. Existing wire
layout/version unchanged;legacy mode defaults to no initial mask.

Four256MiB in-flight disk reservations protect concurrent primary/derived writes
under the same authorized20GB aggregate allowance;these are not1GiBVRAMallocation.
Converters and native resident bounds unchanged. Frozen gate/run-metadata.json
records the same capture session independently of mutable runner reports. Budget
inventory tolerates atomic latest-light file renames. Stop closes receiver service,
stops the owned host,joins/cancels preparation before transport storage release.

High-resolution QueryPerformanceCounter timings record identification,full
preparation(including proof hashing),worker overlap,initial publication and runtime
startup. Initial rendering no longer starts with a partial initial library.
Genuinely late unique materials STILL require the known runtime library rewrite
and may stall;same-content late aliases do not. No earlier engine loader hook,
vendor patch,appearance change,stale image hold or original suppression introduced.

See Run125 for final exact-build offline initial/late fixtures and pending sponsor
runtime acceptance. Earlier single-worker/start-immediately wording is historical.

## CURRENT corrections — Run123,2026-10-23

Sponsor authorizes confirmed shared-owner fix and removal/audit of obsolete test
limits. At the model callback use validated incoming ship/epoch/visual context,
with native shipvtable and ship+0x88link rechecked. Without context permit only
one unambiguous active visual owner;stale/mismatched epochs never select another
ship. Shared content remains reusable,but each native owner receives its own
capture/catalog qualification and persistent simulation state.

The old SCENE-WIDE128MiB original/derived image budget and256unique-image count
are retired for multi-ship mode,including conservative estimator,actual accounting,
game supervisor,standalone supervisor,qualification and owned-process guard.
Images use the authorized20,000,000,000byte project output allowance and disk
availability,with32MiB evidence reserve;checked by asset worker before/after
preparation,not by rescanning the project in rendering callbacks. Aliases reuse
resident geometry/images and do not consume another physical conversion.
Legacy single-ship/offline diagnostic workflows retain their original bounds.

Finite parser/memory bounds remain:128MiB decoded primary images per ASSET,
256resources per ASSET,4096² image dimensions,256MiB conservative pending plus
resident CPU/managedGPU backing,32living owners/64session asset revisions/four
2MiB transfer slots. These are explicit supported-format/resource safeguards,
NOT a promise of arbitrary mission capacity;hitting one remains reported PARTIAL.
User20GB allowance is disk output,not authority to allocate20GBVRAM. No silent
model substitution or unsupported transparency/deformation introduced.

Inherited camera-recovery action cues suppressed in multi-ship mode;only start/
exit instructions relevant to normal play remain. Normal worker strips inherited
offline fixture/backbuffer diagnostic flags. No automatic magenta/on-off effect,
FCA selector,artificial30Hz rendering throttle or per-frame geometry export in
this active mode. Camera-left placement/originalshipsON,90second capture,
120second entry wait and285second total workflow deliberately retained.

Run123audit in docs/runs/2026-10-23-codex-shared-owner-and-resource-fixes.md
distinguishes removed test limits from retained qualification boundaries. Earlier
scene-wide image-limit wording below is historical where it conflicts here.

## Delivery repair — Run117,2026-10-22

The complete tracked-set packet is now committed BEFORE its selected-anchor
notification. Source callback still has fixed storage/no waits or IO. The
previously reserved final header DWORD now carries `closed_frame`:the actual
buffered compositor marks N-1 consumed at callback N. Layout/version/size remain
unchanged;legacy writers leave zero and legacy mode keeps its2ms admission.
New multi-ship workers require the source-locked matching repaired compositor.
Multi-ship admission accepts only current/adjacent source frames newer than that
watermark,with the existing50ms history guard. No new output buffer or fixed-Hz
deadline;exact source sequence/camera/full-cohort hashes still gate composition.

One backend CPU future prepares/validates immutable scene/image bytes while the
rendering worker continues;D3D9 resource creation stays on its owning thread.
Pending+resident conservative backing remains256MiB,one pending asset maximum.
No repeated disk/hash pass during renderer construction. Stop drains the future
before backend destruction. Aggregate stage reasons and per-asset timings are
retained in the bounded run report.

Late material-list rewrite is NOT yet seamless. An explicit offline-only
`--isolate-late-material-reload` negative diagnostic skips that rewrite,records
the exception in its result and cannot qualify the normal workflow. It is never
enabled in the game runner. It is not a proposed substitute for original materials.
Current settings and normal material-layer publication remain unchanged.

## CURRENT diagnostic placement — Run115,2026-10-22

Sponsor requests returning to the previous camera-left distance to judge flicker
without coincident originals. `tools/d3d9_proof/multi_ship.toml` fixes the common
translation at15.897722721099854nativeunits,exactly the accepted FCA offset from
run20261022-042653-754380. This is a diagnostic placement constant,NOT an asset
selection/template or model scale. Every returned instance gets the SAME
camera-left world translation;relative positions,worldheight,scale/source rows
unchanged. No extra buffer,delivery optimization or original suppression.
Lighting/material/image baselines unchanged. Zerooffset aligned result below
is historical Run113/114 evidence,not the next test's expected placement.

Current source/binary/config gate checks the configured float32 transport
distance;malformed/negative/nonfinite/excessive distance rejected. Changes to
placement configuration require requalification,not live tuning in this test.

## Original increment and aligned-overlay record

2026-10-22, Run113. Sponsor authorizes accepting fresh geometry/textures from
different models and rendering multiple retained ships. Test wording is
**skirmish with different models**, not “mixed race”: previous fixtures already
had different races. No requirement amendment, final architecture,
new broad reverse engineering, appearance tuning or commit/push authorized.
Sponsor addition:make this the first replacement-or-overlay test. Selected
**aligned overlay**,not original suppression:draw returned ships at their actual
positions with originals still underneath. This is not a replacement PASS.

## Starting point and chosen boundary

CONFIRMED current baseline d40f8f2: persistent32-owner registry, fresh supported
mesh/resource capture, qualified simulation pose and camera, ordinary D3D9
renderer, material/light/image policy and bounded one-frame GPU return. Current
display assumes one selected FCA and one-owner coverage. Toolkit multi-ship
evidence does not itself qualify D3D9 multi-asset display.

Extend default-off, retain the single-FCA diagnostic baseline. Publish a coherent
snapshot of the current qualified registry rows once per scene frame using the
same validated camera and simulation sampling. This is a tracked-set snapshot,
NOT a claim to capture every SFC object or a complete engine scene seal. Reuse
the existing selected-anchor publication for scheduling/provenance while binding
returned output additionally to the entire tracked-set hash. Asset readiness can
omit unsupported/unprepared objects; never substitute another asset.

Retained assets are qualified by fresh capture owner/epoch/revision/model/source
and geometry/group/original-image content, not filenames or native resource IDs.
Worker prepares supported assets off the game thread; host retains D3D9 buffers,
shares identical content and draws each current qualified instance with its own
world transform before a single Present. Same camera/common origin for the
cohort;default overlay haszerooffset. An optional offset diagnostic may use one
common camera-left shift,not separate per-ship shifts. Original SFC drawing stays ON.

Returned coverage is explicitly the union of the qualified submitted set, with
scene/anchor provenance; it is NOT a per-pixel native owner map. This additive
proof cannot claim owner-specific suppression/replacement. Frame/camera/depth
and GPU lease synchronization remain mandatory. In-place deformation without a
qualified asset revision,unsupported formats/alpha/material conflicts and actual
destructor qualification remain explicit partial conditions.

## Bounds and validation

32 retained owners,64 asset revisions,existing four2MiB fresh capture slots,
16MiB current-user mapping. New tracked-set/catalog structures occupy an explicit
unused region below the native-light region, with compile-time overlap checks.
Exact new block:15MiB−128KiB through107072bytes;existing source-timing block
occupies12MiB through12MiB+2621568bytes. Both lower/upper overlaps statically
rejected. An early standalone fixture caught the initial12MiB collision;that
experimental layout never reached SFC.
No game-callback allocation,IO,image conversion,renderer call orwait. Busy
transport postpones/drops evidence rather than blocking original rendering.
No imposed30Hz refresh cap;sample once per qualified scene frame.

Existing image dimensions4096²,256unique resources,128MiB original/derived image
budget and256MiB retained backend asset budget;output resource128MiBcap unchanged.
One returned cohort image,not separate output hosts/surfaces per ship. Bounded
evidence32MiB combined,warning16MiB,90secondtactical/five-minuteworkflow. No
continuous image dump or diagnostic geometry hook. Bounded admission/instance
failure counters and source/content manifests must identify unsupported objects.

Offline must exercise two genuinely different assets,shared content/distinct
owners,late admission,revision/lifetime/pointer reuse,asset mismatch,malformed
packets and limits;read back actual D3D9 arrays/material assignments and verify
new tracked-set provenance through the actual return path. Preserve existing
Python/native/buffer regressions and original client hashes. CONFIRMED standalone
installed runtime loaded a second material-only sublayer after the first ship
was already displayed;new asset search paths and image loads are in runtime logs.
This does not establish native lighting fidelity or instant appearance readiness.

One scheduling anchor is not a player flag or asset identity. Anchor changes
must preserve fresh light context;its retirement must not prevent the backend
worker from admitting other owners' assets. Each actual draw separately matches
owner epoch/revision/model/source against immutable content-qualified catalog.
Sharing additionally verifies path/replay/texture hash provenance. Retained
budget conservatively counts both CPU and managed GPU backing,not just one.

No Python per-image bytewise hash loop in normal admission:bounded native
`asset_hash.exe` computes the same wire checksums off the game thread. Mesh,
original image and derived image SHA provenance remains. Bounded sampled raw
tracked-set evidence retains at most120 full12328-byte frames (one per60 source
frames),plus final107072-byte stopped store;existing per-owner diagnostic records
and immutable asset manifests remain. Full-rate submission is NOT full-rate disk
tracing. No continuous screenshots/image dumps.

CONFIRMED offline boundaries:wire malformed/identity/camera/retirement rejection,
shared-content distinct-owner proposal,actual native120-update/one-capture worker,
two distinct historical packet assets through ordinaryD3D9,actual GPU buffer bytes
and texture row readbacks,post-startup admission,HUD/scene/state preservation,
resize/recreation and clean shutdown. Runtime fixtures use explicitly SYNTHETIC
poses;they do not prove fresh multi-model SFC behavior. Actual death,Remix removal
of all retired-instance pixels,arbitrary deformation,large-mission performance
and all-model coverage remain unqualified;first sponsor fixture keeps ships alive.

First sponsor test: familiar skirmish using different ship models (not FCA-only),
both ships should receive aligned returned overlays (not offset copies). Move/turn
and switch cameras normally;exit at final two LOW beeps. Review before stress
mission. No “any model” or formal milestone claim from one successful fixture.

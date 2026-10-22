# Run73 — approved64bit ordinary D3D9/output alternative

Date2026-10-19 America/New_York;UTC artifact folders20261020.
Authority:sponsor YES to bounded64bit D3D9 helper qualification after Run72's
normal32bit bridge lacks output APIs. SFC capture remains32bit,unchanged. No
SDK mesh registration,no game launch,suppression,appearance tuning or TRL claim.
HEADd29111f7 unchanged,index0;all Run65–72 dirty work preserved,no commit/push.
Fuel Guard exact-thread hook verified,no new daemon/helper/agents. Credits
available;earlier sponsor asks checkpoint near5%remaining. Gate3 live scheduling
is a separate unstarted work unit;do not consume closeout on an unrecorded start.

## Implementation

New`d3d9_direct_host.cpp` reuses EXACT parser/Renderer from`d3d9_replay.cpp` via
types-only compile guard;no geometry/UV fork. Newx64 build verifies pinned header.
Loads frozen `.trex/d3d9.dll` as AMD64 PE32+,calls ordinary Direct3DCreate9Ex and
CreateDeviceEx. Uses output API initialization/device registration ONLY,not
CreateMesh/CreateMaterial/DrawInstance/SetupCamera or API-created D3D9 device.
Header0.6.4 SHA verified against pinned release manifest. Pinned source inspected
for registration ownership,output copy and Shutdown:registered device ownership
passes to Shutdown after all local resources drain/detach;never double-release.

Native D3D11 consumer GPU matches renderer LUID. Three fixed shared textures:
BGRA8 final color,R32_FLOAT depth,R32_FLOAT bit-preserved picking. Same-process
API boundary proven first;not an authenticated cross-process/live wire contract.
Renderer event query completes before consumer reads;consumer event completes
before staging Map. Five-second waits and CPU readback are OFFLINE diagnostics
only,never proposed for SFC callbacks. One output set,<=128MiB resource limit.
Inherited common Renderer checks uploaded VB/IB/texture bytes against source.

Runner`run_direct64.py` owns tree with90s/128MiB scratch/2MiB console,100s outer
watchdog,private-generated64MiB limit;128MiB reservation within10GB combined
evidence. Standard original captured BINs/resources,not MOD conversion. Three
coherent captured snapshots per real asset. Optional synthetic control is clearly
labelled,not substituted SFC evidence. Detailed automatic capture/screenshot is
default-off,one12/20frame diagnostic only when requested.

## Actual outcomes — not API success alone

Initial024243-514882 exited0 but returned all-zero triplet:PARTIAL,not success.
Added explicit process-local raytracing/preset environment,Windows message
processing and24presents/snapshot with10ms offline warmup,plus bounded ordinary
backbuffer diagnostics. Subsequent outputs valid. Changes not individually
isolated;do NOT assert which alone explains first empty result or production
readiness. No inheritance of warmup/sleep/readback into live scheduling.

KFF diagnostic024717-672750:452tri/5groups captured through ordinary D3D9 and actual
GPU output returned. Synthetic025019-125516:known translation/rotation/camera
controls. FCA025141-248593:6370tri/58groups,without auto capture enabled. All jobs
exit0,ownedchildren0,output API Shutdown0. Runtime disposal warnings37/40persist.

Actual camera/output finding:Remix renders FULL FRUSTUM to960x540,not into SFC's
offset viewport embedded in1920x1080. Returned ray-tracer samples at half-pixel
centers;native D3D9 oracle uses integer centers. Independent known control verifies
half-pixel convention;do not inherit arbitrary half-pixel fix into captured data.
Map output to source viewport(x200,y30,w1720,h1020) explicitly at composition.
With full-frustum/.5pixel oracle,KFF/synthetic silhouettes match exactly(IoU1.0);
FCA>=0.9997397866 (one boundary pixel differs in first snapshot,others exact).
No FOV/model/UV changes,USD reconstruction or image fitting. This resolves actual
runtime projection question for these snapshots independently of omitted USD
vertical aperture. Not general live/camera-mode or UI composition qualification.

Picking0 occurs on valid visible surfaces while also being background ID. It is
NOT the prior SDK explicit owner-picking contract. For this isolated ONE ship,
coverage uses valid normalized depth versus explicitly configured -1234background
sentinel,corroborated against complete geometry. No black-color cutout or rectangle.
No claim this separates multiple overlapping owners. Synthetic depth expected.9;
returned error<2e-7. FCA normalized-depth errors<1e-6 against independent oracle.
Actual color images produced;appearance/secondary-lighting parity unqualified.
Synthetic plate is black under provisional lighting but validates geometry/depth;
do NOT count it as a passed texture-color control.

## Final qualification / limitations / closeout

Final KFF025637-591642 disables ordinary backbuffer CPU diagnostic AND automatic
capture;GPU output still matches all3snapshots exactly,normalized depth<=3.28e-7.
Thus the return does not require CPU backbuffer pixels between rendering and
D3D11 consumer. CPU staging remains only the independent verification endpoint.
Earlier FCA/synthetic proofs used optional ordinary backbuffer diagnostic;final
host defaults it OFF. Pinned code/EXE hashes in
[curated receipt](../reconnaissance/evidence/20261019-direct64-d3d9-output.json),
[experimental output contract](../reconnaissance/d3d9-direct64-output-contract.md).

313Python regressions PASS4.192s,including4new raw-image/sample/depth tests.
Final source-hashed native reference025443-326239 PASS4.859s after shared C++
types-only guard and optional oracle extensions. Default native convention remains
integer-centered/embedded viewport;new full-frustum/.5mode only explicit analysis.
No relaxation of original masks/UV checks. Current x64 host build /W4 /WX PASS.

Six direct64payloads179,655,221B ->8,148,493B ZIP,all decompressed hashes verified;
final native65,669,351B ->2,079,711B ZIP. Logs/manifests/PNGs/analysis remain loose;
source captures/original images unchanged. Restore exact named generated ZIP to
matching case before reanalysis. Current combined outputs~9.772GB/10GB.

Disposition:DIRECT64 OFFLINE OUTPUT SUBPROOF CONFIRMED. Gate2 continues because
the consumer is still within the producer process;standalone cross-process/x86
surface ownership,live cadence,stale/lifetime/device-loss behavior and appearance
are unqualified. No game test requested,no maturity/boundary-gate closure.
Do NOT call this a full live return or treat raw picking0 as absence of ship.
Initial empty result and runtime common-object warnings remain explicit findings.

Exact next action:standalone32bit D3D11 test consumer opens this64bit producer's
shared triplet using explicit bounded source-frame/completion/ownership metadata;
prove pixels and disconnect/retirement,then offline source-cadence scheduling.
No SFC request until these tests pass. Original ship suppression stays excluded.

## Final handoff checks

PowerShell parser,doc links,source/pixel receipts,all6ZIP hashes and every pinned
runtime input hash PASS. git diff --check PASS(line-ending notices only). Both
client EXEs remain SHA256
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
Four sponsor appearance TOMLs have no diff. No owned renderer/probe/bridge,SFC,
SDKhost or Toolkit process left;no unfinished capture/build/export. Combined
counted outputs9,771,697,475B/10GB;next128MiB reservation fits after compaction.
Git13modified tracked/56untracked individual files,index0,HEAD unchanged,no push.

New files:d3d9_direct_host.cpp,build_direct64.ps1,run_direct64.py,
analyze_direct64.py,test_d3d9_direct64.py,this run,output contract,curated receipt.
Modified:d3d9_replay.cpp(types-only guard),run_offline.py(explicit oracle modes/
accounting),archive_intercept.ps1(exact direct64 targets/generated patterns),
README,HANDOFF,scene contract,execution/transition progress. All earlier dirty
work preserved;no production game-facing component changed in this run.

Fuel Guard advised4%five-hour then5%weekly remaining;additional credits available.
Complete this bounded output unit and checkpoint as sponsor requested,not an
unrecorded new live scheduling implementation. No technical failure claimed from
allowance. Further approved work remains resumable from the exact next action.

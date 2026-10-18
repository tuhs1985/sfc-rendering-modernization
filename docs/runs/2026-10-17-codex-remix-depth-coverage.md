# Codex run — runtime ship depth/coverage and camera replay

Run SFC-RETURN-20261017-16,2026-10-17 EDT. Sponsor "Go" authorizes next bounded
offline depth/coverage alignment work. Read HANDOFF,approved M1/current gate
disposition,Run15,readiness,existing output/return contracts,output host/SDK/probe
source and historical fresh scene/camera records. Starting/final HEAD e96765a,
indexempty,existing dirty work preserved. FuelGuard actual-thread hook attached,
no daemon/helper/delegation/new gameplay/staging/commit.

## Executive result

**CONFIRMED standalone:Remix directly renders captured SFC geometry and exposes
fresh owner masks and projected depth through native D3D11 GPU resources.**
Recorded SFC model/camera replay matches independently projected native geometry
478/478pixels (IoU1.0),median depth error1.8007762153660067e-7 at256square.
This bypasses Toolkit/USD,not original SFC rendering. No original ship suppressed.
Live same-frame SFC depth/semantic correspondence remains unproven;no replacement
or milestone PASS. See [contract](../reconnaissance/remix-depth-coverage-contract.md).

## Engineering decisions / limits

Pinned public SDK CopyRenderingOutput DEPTH/OBJECT_PICKING was starting evidence,
not proof. Inspected pinned rtx_remix_api.cpp1434..1498:initial picking call only
enables retention;subsequent commands copy primary outputs. Inspected camera
conversion498..530 and SetupCamera1062..1090. No new dependency or runtime patch.
Known synthetic planes separate viewZ,ray-distance and D3D projected depth.
Raw picking bit IDs distinguished from float-valued IDs;validated GPU shader
asuint decoding,not just CPU reinterpretation. No coverage inferred from black.

Native10_1 consumer allocates3shared textures,BGRA8+R32_FLOAT+R32_FLOAT;
Remix imports via D3D9Ex CreateTexture. EVENT completion then native CopyResource
and readback all-byte comparison:18/18images exact. Local fourthR32_UINT target
proves6/6pixel-shader ID decodes exact. No CPU pixel uploads to GPU outputs.
This extends compatible output-format evidence,not cross-process/SFC multi-output
transport qualification. Existing image-return v2 contract unchanged.

Historical fresh FCA asset2 from20261016-223535-enabled:6,370triangles,
19,110corner-expanded vertices,58groups. Positions/normals/UV unchanged,
indices preserve triangle order;group assignments in manifest,default opaque
material for diagnostic SDK mesh. No original images/emission/alpha roles claimed.
Control ship uses documented center/uniform scale only;replay uses original
model transform/no fit/no rotation repair. Current provisional control light
makes replay color dark;mask/depth,not visual appearance,is acceptance.

Strict same-frame asset/camera selection initially failed BEFORE launching any
runtime:asset captured frame4,updates at3/5/8 due existing34ms publication limit.
Did NOT invent frame4camera or join by guessed timestamp. Existing rigid reusable
asset semantics allow same revision2,owner2,model/source with frame5model/camera
observed together. Both frame numbers recorded. Unsupported in-place deformation
remains unqualified. Preparation failure retained at200307-858156-coverage.
First successfully replayed200340run then final acceptance run200529below.

Camera conversion reuses validated native17word logic and camera_state;SDK LH
basis inverse-view right/up/negative-forward. Source native viewport
[200,30,1720,1020],30degreeFOV,aspect1.6862745351512323,
near1.0000000596026588/far30013.910554561717,native composition error
3.356795991749095e-5pixel. Off-axis projections rejected. Independently project
all original mesh vertices with native composed matrix,normalize viewport to
256square,rasterize triangles at pixel centers and convert clipZ `.5*z+.5`.
Compare to actual runtime ID29 coverage/depth. It does NOT compare Run15 SFC
GPU depth with another run's semantic state as if contemporaneous.

## Exact provenance / final runtime evidence

Final artifacts/remix-runtime/runs/20261017-200529-953300-coverage.
Native process0,SDK Shutdown0,3.593s total,96rendered frames,6triplets retained.
All6qualification flags true (IDs,normalized depth,background,native GPU transfer,
shader ID decode,historical camera projection). Color/depth/picking262144B/plane.
Source packet SHA256D28CD7F0A4259B7DAB215349E63EC0D3E751514A44112741DA83DC62A03A5C04;
referencesDA093CDEEAF6CD03ECADF7FDD56B7A64A3185631A84DD7716DBA16A67D5A801E;
updatesA4400F1ABDD13A7D101934402A42BA0E04658E7E567B00AF5B182C78FB1C19A6,
line4,epoch2/frame5/revision2. Native output host executable
4D6FDA99BEE9CE01B24B28B946386D43B4AFF17A14E813C27319402C49DFDE00.
Runtime SHA F7C310821AA98BCDFDEC120330B0A89457B7C5EBA58D21464AF32639611C809F;
SDK header E623E4956A76894EEEF02361334C7C0458D4EC8BF49F729EC9038C36128BBF47.
SDK0.6.4/Remix1.5.2 matching dependency manifest unchanged;binary suffix source
identity caveat remains. VS2026 18.7.3,x64 C++20 /W4 /WX,Python3.12.14,
RTX4070Ti/driver617.42;process-local NRC/DLSS/RR OFF as existing ENV.

|Phase/final native frame|Output IDs / pixel counts|Discriminating result|
|---|---|---|
|0/15|7:903,11:392|Two objects distinguished,Z6/Z9|
|1/31|7:512,11:392|7moves toZ8;new depth/coverage,11unchanged|
|2/47|11:392|7absent,no stale7pixels|
|3/63|13:903,11:392|Reappearance under newID,no reused7|
|4/79|23:829|Captured FCA geometry at documented control fit|
|5/95|29:478|Original historical model/camera,exact native-projection silhouette|

IDs are test owner labels,not native pointers/epoch numbers. PickingR32F contains
raw uint bits,not floating7/11/etc;all background IDs0. Depth background-1234
checked at EVERY background pixel,nonfinite0. Known-plane normalized-Z errors
below2e-5;view-distance/ray-distance rejected. Fouroutput GPU surfaces<=1MiB,
CPU diagnostics<2MiB,fixed frames/poses,no continuous screenshots. Final whole
run5,416,771B<32MiB;warn16MiB not reached. Input geometry<2MiB,120s cap,
overall10GB coexistence preserved. Native GPU waits only in owned standalone
process;no game callback waits proposed by this implementation.

Prior195446private outputs,195654native shared transfer,195842shader decode,
200307preparation failure and200340first replay preserved,not hidden. All tests
except preparation refusal normal process exits;no SFC launch in any run.

SDK warning persists verbatim:`[40] common device objects were not disposed of.`
Retirement fence/process0/API0 do NOT establish warning-free cleanup or zero leak.
No new nvoglv driver crash observed here;historical crash unresolved. Native SFC
reference warning67 remains separate/open. No sponsor-visible gameplay evidence
generated or requested this execution.

## Files / commands / verification

New tools/remix_runtime/coverage_probe.h,run_coverage_probe.py;
modified output_probe.cpp (new opt-in mode) and build_output_probe.ps1
(D3DCompiler link). Existing return host/addon,semantic hooks,game runner and
image-return protocol not modified. New tests/test_remix_coverage_probe.py.
New probe,depth/coverage contract,this record,curated evidence;HANDOFF/readiness
updated. Original captures/assets and raw generated results unchanged.

```text
tools/remix_runtime/build_output_probe.ps1
python tools/remix_runtime/run_coverage_probe.py --execute
python tools/remix_runtime/run_coverage_probe.py --analyze <exact-completed-run>
python tools/remix_runtime/run_coverage_probe.py --archive <up-to8-exact-coverage-runs>
python -m unittest discover -s tests -p test_*.py
git diff --check
```

python is bundled dependency executable;project artifacts/test-temp for TEMP/TMP.
Strict native build and30output-contract tests PASS. Python160tests PASS2.653s,
covering ID-bit vs numeric conversion,retirement/stale IDs,invalid depth/background,
missing GPU proof,malformed planes,raster reference and archive target rejection.
No helper used. Script/default mode never launches game;--execute only owned
native probe,120s/32MiB watchdog. Scoped external execution for build/GPU tests
does not change user security policy or request routine UAC.

Archive artifacts/remix-runtime/archives/20261017-200555-380640-coverage.zip:
1,470,629B,173entries,25,309,676Bselected source,CRCverified,SHA256
2CC8B1F5187E8957E09715470D29D03173F094FF7FF1425175CFD9825059A490.
Raw small runs retained,no deletion. No original client files modified;verify
frozen critical hashes against accepted/copied previous runtime manifests.

## Next exact action / bounded remaining gap

Prepare one contemporaneous selected-owner/model/camera/native-depth calibration
capture with explicit frame/session/revision provenance,then compare native GPU
depth against this qualified runtime output at that same state. No broad capture
needed. That evidence must precede owner suppression,UI/effect occlusion claims
or synchronized replacement contract. Current30Hz preview stream is not promoted
to that contract. No gameplay runner for this new paired capture prepared here;
existing -DepthSnapshots alone lacks semantic fields and should not be repeated
unchanged. Implementation risk/old cleanup warnings remain durable open items.

Final HEAD e96765a,indexempty,current/prior changes unstaged/untracked,no commit.
No active game/owned probe/session must survive restart. Standalone success is a
bounded prerequisite result,not one-ship replacement or formal TRL/milestone PASS.

# Run83 — camera-left placement and current lighting/material performance

2026-10-20. Sponsor clarified 'effects' means existing lighting and material mapping,
authorized proceeding with camera-left correction and remaining-cost profiling.
Preserve all four appearance TOMLs. No weapons/effects capture expansion,renderer
replacement,buffering/stale holds,requirements change or helper use authorized.
HEADd29111f7,index empty,prior dirty work preserved. Fuel Guard attached. Read
HANDOFF,Run82,current source and latest actual run before changes.

## Latest game evidence — 225915

`artifacts/remix-runtime/runs/20261020-225915-758446-in-game`:
selected owner2/revision2 FCA;player-fixture selection correction CONFIRMED.
Sponsor says height appears correct,offset behind is hard to locate,still flicker;
intentionally exited early. Launcher0/normal_game_exit true,controller8 means
process-exit reclamation,NOT controlled live hook removal. Owned renderer0;
accepted/copied critical files/launcher settings unchanged,proxy rollback restored.

1,883draws/2,438pool publications (~77.24%),531stale,22unclaimed replacements,
1not-ready,zero invalid/resource/depth/busy errors.2,439transfers,one light omission.
408fresh native light packets,zero invalid/busy. Actual configured slot0radiance1.5,
slot1.25,project dome.12 applied. Current image/quality policy accepted. Material
manifest58groups/139derived images;mesh/textures uploaded once,not per frame.
Current illumination/roughness/metallic/image settings not removed to gain speed.

Median end-to-end13.837ms,p9518.937ms,max37.452ms. Median/p95 input queue1.054/
2.372ms,light update.129/4.312ms,render+transfer12.287/14.780ms. Typical native
source lead~15.5ms. Confirms late-tail delivery still FAILS steady display even
though materially better than first run. More identical gameplay is not requested.

## Bounded implementation

Prior offset used world X,not camera-left. New camera_left.h uses qualified
orthonormal world-to-camera row0:delta_world=-distance*view_row0. Then
R*delta_world=[-distance,0,0]:no camera-up or depth displacement. Raw source mesh,
UVs,transforms unchanged;separate diagnostic parent only. Both producer and game
derive same displacement from the exact matching source row. Pool version2,
same576B/slot ownership;camera-space scalar replaces old static world-vector field.
Mismatched versions reject. Current player-fixture filter unchanged.

Remove unused per-frame Remix OBJECT_PICKING copy in additive mode only. It was
overwritten by depth-sentinel-qualified semantic owner coverage anyway. Preserve
color/depth copies and qualified owner coverage;ordinary offline picking proofs
retain original three-output behavior. No lowering output resolution,lighting,
denoising,texture/material policy or image settings. Worker fences/identity rules
unchanged. Added output-copy submission/render-completion/postprocessing timing
columns and final light-creation change count,within existing logging limits.

Files: new tools/d3d9_proof/camera_left.h;modified game_output_wire.h,
game_output_writer.h,d3d9_direct_host.cpp,direct_lights.h,
tools/remix_runtime/d3d9_game_receiver.h,live_owner_timing.py,
tests/d3d9_game_output_tests.cpp;this record and handoff/contract/probe as evidence
matures. Native builds29wire/18timing/31pool checks PASS;rotation/negative-distance/
invalid-basis tests corroborate left-only displacement.360Python tests PASS.

WIP: current standalone600-frame fixture profiles new path. No SFC launched.
Old additive qualification stale by design;do not use gameplay launcher until
source/binary/placement/pixel/state/deadline review. Runtime/tool state:standalone
fixture may still be active. Next action:finish/profile that test,retain current
appearance policy,decide whether any further bounded cost reduction is justified
or whether synchronized buffering needs separate sponsor approval. No stage/commit.

## Final authoritative checkpoint — READY FOR CHANGED SPONSOR TEST

Earlier WIP superseded. No SFC launched by Codex. Player-fixture selection retained;
camera-left and current lighting/material optimization implemented and offline
qualified. Actual in-game flicker correction still requires sponsor observation.
No synchronized buffering/prediction/stale ship hold or original suppression added.

First actual-proxy fixture231055:578/600fixed-window images;median10.654ms,
p9515.757ms,max23.209ms. Render completion wait7.583/8.599ms median/p95;
postprocessing.350/.680ms,receiver.274/.722ms. Only3light descriptors changed total,
yet light-update stage still had multi-ms tails. IO remained in per-frame critical
worker,not necessary light recreation. Removed picking copy preserved depth/coverage,
16,325changed pixels,graphics state/border/resize/normal owned exit. Not yet a
demonstrated performance cure;fixture retained as intermediate evidence.

Additional correction:DirectLights owns one fixed~1008B light/shape cache and
background reader,10ms polling,no API calls. File reads occur outside a brief
snapshot lock;render worker try-locks/copies and retains original full packet
validation. Original observed timestamp unchanged:wrong owner/session/source,
future frame,expired data,invalid checksum or shape revision reject as before.
No substitution of historical lights in gameplay. Reader joined before API
shutdown and on exception. Legacy RemixLiveLights signature defaults retain old
file-read behavior;new optional loaded packet/shape inputs share validation/API path.
Current material/illumination/roughness/image controls never disabled for speed.

Final `artifacts/remix-runtime/runs/20261020-231447-298644-return-fixture`:
599/600frames displayed in fixed~10s window (~99.83%).600total submissions,
602publications,zero stale/invalid/resource/depth/busy/overwrite errors.782raw
inputs,783transfers(includes bootstrap),zero omitted light joins.942exact source
pairs/1884records,no invalid/drop/wrong-thread.16,120independently changed pixels,
original border untouched,state_errors0,resized1,recreated1. Normal host/fixture/
receiver exits0,API shutdown0,no owned processes. Vendor warning40still unresolved.

Final measured delivery median9.8595ms,p9510.9348ms,max13.9169ms. Light stage
median.0041ms,p95.0051ms,max.1893ms;descriptor changes3,cache reads1182/failures2,
validation/freshness remain authoritative. Median/p95 render-ready wait7.692/8.245ms,
postprocess.302/.616ms,receiver.258/.704ms. Most remaining cost is GPU render/output
completion,not texture/material regeneration. Source lead~16.8ms synthetic and
lights replayed:do NOT claim actual SFC contention or no-flicker PASS from this.

Independent captured-view calculation confirms offset projects left;camera delta
[-23.846584,0,-.000001],normalized depth change~1.98e-10. Native identity/yaw/
negative-distance/invalid-basis checks independently corroborate. Raw17word game
payload unchanged;pool version2 prevents old world-offset interpretation.

Validation:360Python tests PASS;native29wire/18timing/31pool checks PASS;11new
loaded-light tests pass without GPU/file input (unchanged descriptors reused,
checksum/session/future/expiry/missing-shape reject). Legacy SDK ship_live_host
compiled into separate ignored cache-compat folder,not installed or executed.
Native current add-on build/existing37/13/14/22regressions PASS. Source/binary/config
qualification refreshed using final fixture;test executables included in gate.
Read-only launcher preflight PASS. No settings/client changes. JSON/link/parser/
diff checks PASS. No claim that startup preparation delay is fixed.

One intermediate test was correctly refused before process launch because192MiB
reservation no longer fit10GB. Recoverably compacted exact finished historical
021153fixture generated textures (61,712,858B→5,208,887BZIP),decompressed hashes
verified;original game assets untouched.231055and231447generated binary/image
inputs likewise archived,logs/manifests/raw source captures retained.
Final archive:
`artifacts/remix-runtime/archives/20261020-231447-298644-return-fixture-binaries.zip`,
199entries/6,859,974B,SHA256
9F6CF2367EC0E2317536BB7F463795D461FA3EC0FD0E0197682ABC70C3F0B6D4.
Final result SHA256 FB97DB8040A3DB1E4A706657DC1CF8BE4B334E7DC5ADE9C299CA45220ABD3A56.
Aggregate9,754,639,428B/10GB;192MiBnext-run reservation fits. No cap increased.

Additional changed files beyond initial list:tools/remix_runtime/remix_live_lights.h,
tools/d3d9_proof/build_direct64.ps1,tests/remix_loaded_light_tests.cpp,
tools/remix_runtime/additive_qualification.py plus current contract/probe/evidence/
handoff. No helper/agents/staging/commit/push. HEADd29111f7,index empty,prior dirty
work preserved. Accepted/copied clients unchanged SHA256
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
Four appearance TOMLs unchanged. No owned processes/tool sessions left running;
fresh session required after restart. M1 CONTINUES,requirements unchanged.

Exact next action:sponsor runs same Federation-cruiser offset launcher,observes
left placement/current lighting+material mapping and follows cues/normal exit.
Codex compares actual delivery with225915before any new rendering work. Full-frame
buffering still requires separate sponsor approval if remaining real tail misses.

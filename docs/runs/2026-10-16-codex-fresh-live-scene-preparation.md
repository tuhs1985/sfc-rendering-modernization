# Codex run — fresh multi-ship scene preparation

Run/date:2026-10-16-fresh-live-scene-preparation /2026-10-16 EDT. Active task:
sponsor-approved Fresh Live Assets increment,not aggregate milestone completion.
Question: construct multiple separate-renderer ships from fresh semantic mesh/
resource packets instead of the imported Klingon,retaining live state/camera.
Sponsor chose all visible mainline ships;first fixture two different classes.

Starting HEAD fee152f137a55a3efeb47a5c236ebf9e3e1951cb,index empty,large inherited
dirty source/evidence tree preserved. No cleanup/staging/commit. Read newest
HANDOFF/operating convention,approved M1 disposition/gate amendment,CDD v1.0
authority/scope,prior camera runtime/preparation/probe/contract and current capture/
transport/Kit/runner/test source. CDD SHA remains
BF5384D2586601AAA28DB36970937A3B40F598E12002B3450BF2E7D9562FA352.
No requirement/threshold/objective/renderer-architecture changes or new RE.

## Implementation decisions / interfaces

Component0.20 supports explicit protocol3 in addition to old protocol2. New
start_live_scene_session.ps1,old single-ship entry preserved. No changed ABI/hook
sites or state-saving stubs. Existing owner table capacity32 (default config8
unchanged);fresh runner requests32. Legacy512polygon collectors/exporters remain
default;templated bounded collectors admit8192triangles/32768corners for fresh mode.
Added missing pre-copy corner-cap check required by expanded storage.

Four preallocated mesh/reference staging slots,one capture attempt/frame,32latest
owner slots,64successful asset revisions,16MiB user-only mapping/four acknowledged
2MiB transfer slots. Failed/busy publication never waits for viewer;busy asset
storage defers capture. Model/source/list/count/LOD changes require new capture.
Retired owner slots reuse monotonic sequence plus NEW owner epoch;raw pointer reuse
alone insufficient. Capture QPC maximum retained. Worker drains/joins before unmap;
timeout refuses unsafe unload. Unsent assets on disconnect reported,not hidden.

Fresh mode skips unrelated legacy one-mesh OBJ analysis/export (not needed for
live display),records fresh probe/budgets in existing runner metadata,and still
performs established exit/restoration/proxy-removal/client-hash workflow. No SFC
client/asset/config edits,game launches or routine elevation prompts this run.

Viewer starts EMPTY scratch USD,authors mesh/materials only in anonymous session
layer,reads geometry/UV/normal/index/group/material bindings back. Resource filenames
come from fresh same-epoch association;original images hashed/copied/decoded on
one worker outside SFC callback. PNG+uncompressed DDS derivatives verified pixel-
exact;DDS is Remix input. Content keys exclude native pointers/IDs,include actual
geometry/groups and image hashes. Shared internal USD asset references,separate
owner instances,one common origin/scale100/proven camera. Camera checks each
matching packet and actual USD hierarchy;newest frame camera restored afterward.

Only primary contribution applied;secondary associations preserved,roles not
guessed. Alpha/native blending,untextured paths,in-place deformation/damage without
identity change,and unsupported/non-mainline categories remain limitations.
No face/normal/UV/orientation correction,lighting extraction/appearance tuning,
live frame return,helper/subagent,vendor/global/security edits or gate claim.

## Reproduction / capture definition

[Probe](../reconnaissance/probes/LIVE-SCENE-001.md),
[wire contract](../reconnaissance/live-scene-contract.md). Tools VS2026/MSVC14.51
x86 C++17,PS7.6.5,Python3.12.14/Pillow12.3.0,Toolkit
1.6.0-dev+main.30229.3f23f80a.gl. Commands from workspace:

```
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/m1_component/build_m1_component.ps1
python -m unittest discover -s tests -p test_*.py
python -m unittest discover -s tools/remix_ingest -p test_*.py
python tools/remix_ingest/run_live_bridge.py --fresh-scene --replay
pwsh -NoProfile -ExecutionPolicy Bypass -File tests/test_mesh_export_workflow.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File tests/test_texture_export_workflow.ps1
git diff --check
```

Use bundled Python/PS paths from launcher,PYTHONDONTWRITEBYTECODE=1,TEMP/TMP=
artifacts/m1/test-temp. Actual current-user IPC/Kit tests run host-context because
restricted sandbox token cannot open protected mapping;DACL not weakened. Builds
and pure/project tests normal sandbox. No new daemon;Fuel Guard exact-thread
recent hook verified,directsandbox denied/quota unknown.

Bounds:90s tactical,300s prepared workflow after builds,32owners/30Hz/2700 detailed
updates each;16MiB native+16MiB viewer state logs=32MiB combined,warn8+8=16MiB.
Summary after saturation.64revision packets<=2MiB each;256unique image contents/
4096square/128MiB original+derived image output,warn64MiB. Conservative logical
viewer asset reserve256MiB,not total process/GPU working-set proof. Existing
Kit256MiB scratch/8MiB console guard/process-only NRC-off retained. No firehose.

## Validation / evidence / deficiencies

Final native build/regressions/exports PASS.93 project Python/52 preview+IPC tests
PASS. Mesh/texture policy/forwarding tests,four modified PowerShell parsers,diff
check PASS. Windows PowerShell5->7 handoff fixture also PASS against the new entry.
That fixture initially cannot bind PSCommandPath inside its extracted scriptblock;
entry now follows existing explicit visualEntryPath convention,then fixture passes.
This was an offline fixture/context issue,not a failed game launch.
Tests cover two different shapes,content reuse,common origin,LOD
recapture,retirement/owner-slot reuse,corrupt packet/association/path/image limits,
actual x86 worker,current-user mapping acknowledgements/torn records,bounded
slow/disconnected receiver and worker shutdown. Empty preparation passes with
nonexistent old job. Legacy single-ship regression suite still passes.

Preserved native synthetic capture proof:
artifacts/m1/test-temp/fresh-scene-proof-20261016,exit0,eight fresh captures/eight
transfers/zero capturefail/invalid/overflow/unsent/iofailure,worker stopped;
one intentional busy-mailbox drop. Max synthetic capture283ticks at10MHz
(28.3microseconds):tiny fixture ONLY,not real8192triangle latency evidence.
Disconnected-receiver test stops with4shared+4unsent fixed slots,no allocation
growth or wait for ack;this is safe partial shutdown,not complete asset delivery.

Final actual-Kit SYNTHETIC sessionaed0a2be4866449a82a0acd314058fb8,preview
C:/Project/RemixJobs/preview-20261017-022917Z-07ca35d4 (UTCfolder,Oct16 EDT).
196 accepted camera/ship updates,zero rejects/camera rejects/asset failures,
three owner/revision epochs,two unique mesh assets,one hide. Max actual USD
projection error.000055529524pixel;all geometry/material readbacks PASS,
template_loaded=false,original image hashes unchanged. Image output3842130B,
viewer log71739B,logical asset reservation6111232B,no warning/saturation.
Supervisor16.656s,Kit16.546s/exit0/stop_reason0,console23848B,
peak scratch4532113B,remainingowned0. Single comparison screenshot copied to
docs/reconnaissance/images/20261016-fresh-scene-offline.png. Inspected supported
DDS rehearsal shows two textured ships;not sponsor/game fidelity acceptance.
Shapes are genuine saved captured mesh plus explicitly synthetic width variant,
NOT a newly captured second game class. Native fixture uses synthetic memory;
actual SFC0.20 two-class proof remains pending.

Early rehearsal8c6d19f... exposed Sdf.AssetPath normalized/resolved equality issue,
corrected with path readback and transactional removal of incomplete assets.
Early PNG rehearsals1bd6.../10b48... produced white ships and repeated unsupported
image errors despite numeric mesh success. Their REPLAY_PASSED status predates
added renderer-error adjudication and is SUPERSEDED,not textured proof. Changed
to lossless DDS and added fatal unsupported-texture gate. Third-owner cache path
had previously exposed partial asset creation;no incomplete mesh is now cached.
One test's no-op corruption and space-containing scratch-root fixture corrected;
one aliased legacy test main needed explicit return0 under /WX. No game failure
or new engine hypothesis inferred from these offline implementation deficiencies.

Prepared componentSHA83F8FAB1F8ADC7F38AA14084C679F87BF9A057BCECB89B1318EFF42F5D506E20,
proxySHA FC42DDC86B19DFB1E86E3945BAB284DF95A77014EE7105E1420CB314327C1EB8.
Runtime launcher rebuilds;future actual runtime metadata takes precedence.
Installed client independently rehashed unchanged:
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
No owned proxy/config left in game directory,no active SFC/controller.

## Files / final checkpoint

New:tools/m1_component/m1_live_scene.h,start_live_scene_session.ps1;
tools/remix_ingest/live_scene.py,fresh_mesh_usd.py,kit_live_scene.py,
replay_live_scene.py,test_live_scene.py;tests/m1_live_scene_tests.cpp;
docs/reconnaissance/probes/LIVE-SCENE-001.md,live-scene-contract.md;
this record and copied offline screenshot.
Modified:tools/m1_component/m1_component.cpp,m1_mesh_export.h,
m1_texture_references.h,build_m1_component.ps1,start_m1_enabled_session.ps1,
run_m1_increment_a.ps1;tests/m1_mesh_export_tests.cpp;
tools/remix_ingest/live_bridge.py,run_live_bridge.py,run_mesh_preview.py,
kit_mesh_preview.py,README.md;docs/HANDOFF.md,
docs/reconnaissance/live-bridge-contract.md. No original evidence overwritten.

Result: READY FOR SPONSOR RUNTIME TEST. CONFIRMED offline fresh construction/
content association/transport/lifetime mechanisms;actual multiple SFC classes and
gameplay/latency/lifetime correctness remain runtime questions,not proven here.
Archive details below. Raw useful evidence retained,no
deletion. HEAD unchanged/index empty,inherited work preserved,nothing committed.
No active worker/mapping/game/session/server needed to survive restart.

Verified final archive artifacts/remix-ingest/evidence/
20261016-fresh-live-scene-offline-final.zip contains118entries,including final
entry shim,selected native/rehearsal evidence,sources/configs/manifests/images and
single final comparison. Previous pre-shim archive retained,not overwritten;
portable/shader caches excluded. Entry SHA verification PASS. Final archive
1326621bytes,SHA256
D330446CB97B1FFC078BF09804E052F3CB5CA1E6FC5C5A48FE712FAFF998CF3B.
No raw evidence deleted.

Exact next action: sponsor runs start_live_scene_session.ps1 from existing
elevated parent,enters two different-class ships (prefer non-Klingon enemy),keeps
both visible briefly,changes camera,moves/turns,exits on request;then adjudicate
fresh asset packet/source hashes,scene correlation,visible behavior and cleanup.
Do not start broader mission/light/return work or call synthetic rehearsal runtime.

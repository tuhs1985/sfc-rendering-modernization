# Run105 — one bounded delivery-efficiency pass

2026-10-21 America/New_York. Sponsor authorizes one improving pass,then moving
on rather than endless Remix-harness polishing. HEAD0fc1300,branch
codex/github-sanitized,index empty;Run103/104changes already pending. Read
HANDOFF,persistent contract/probe,Run104actual recordings and native host/
receiver/grade/coverage/fence code. Fuel Guard recent trusted-hook attachment
confirmed. No helper,agent,new SFC gameplay,staging,commit or push.

## Evidence and implementation decision

Joined second actual Run104(025321-515918)source/input/completion/audit data in
its recorded QPC/session.41nonmatching audit clusters;largest96records spans
frames4428–4523,1.583182s between audits. This is NOT measured visible gap:
later compositor can still draw. Example4428completion5.587ms after Present
audit;301completion1.894ms late. Some intermediate inputs were never rendered
by latest-state consumer. No owner/geometry churn. Deadline hypothesis remains
strong;no exact camera-switch-to-visible-pixel duration claim.

Selected:combine final colour grade and depth-sentinel owner coverage into one
worker-owned D3D11 multiple-render-target fullscreen draw. Same grade arithmetic,
alpha,owner bits,depth predicate,scratch copy and completion fence. No new image
resource or transport;neutral/disabled grade retains coverage-only path. No
changes to appearance settings,resolution,semantic hooks,identity/freshness,
lifetime or original rendering. No stale-camera hold or game-thread waiting.

Rejected:lowering quality,holding old pictures,timeout-only fixes,new translator,
architecture redesign and weakening safety checks. Also rejected flush-once/
zero-flag-only D3D9 query polling:Microsoft explicitly warns it need not progress:
https://learn.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3dquery9-getdata

## Exact files changed this pass

- `tools/remix_runtime/remix_image_adjust.h`:shared unchanged HLSL arithmetic,
  optional MRT shader/views and drawCoverage;legacy draw remains available.
- `tools/d3d9_proof/d3d9_direct_host.cpp`:combine active nonneutral grade with
  isolated owner coverage;COMBINED_POSTmarker;neutral path avoids extra copy.
- `tests/d3d9_combined_post_tests.cpp` (new):actual GPU equivalence/timestamps.
- `tools/d3d9_proof/build_direct64.ps1`:build/run GPU test,explicitUTF8log.
- `tools/remix_runtime/additive_qualification.py`:require actual combined-route
  fixture marker and hash-locked65-check GPU test receipt.
- `docs/reconnaissance/persistent-scene-contract.md`,
  `docs/reconnaissance/probes/PERSISTENT-SCENE-001.md`:bounded pass disposition.
- This run record,curated evidence JSON and newest `docs/HANDOFF.md` checkpoint.

## Reproduction and validation

Existing bundled Python/modernPowerShell,VS18Community,x64C++20
`/O2 /W4 /WX /fp:precise /Brepro`;existing pinned runtime/SDK unchanged.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/d3d9_proof/build_direct64.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/remix_runtime/build_return_probe.ps1
python -m unittest discover -s tests -p 'test_*.py'
python tools/remix_runtime/light_discovery.py
python tools/remix_runtime/run_return_fixture.py --d3d9-additive --persistent-scene --rebind-owner
python tools/remix_runtime/qualify_persistent_scene.py --fixture artifacts/remix-runtime/runs/20261022-031459-406014-return-fixture
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/d3d9_proof/start_d3d9_persistent_scene_session.ps1 -CheckOnly
git diff --check
```

415Python tests PASS. Native direct/light11/deferred/private-wait tests PASS;
return37/depth13/broad14/calibration22 builds/tests PASS;native light worker
requalified,persistent actual worker120frame/reuse/removal/stop tests rerun PASS.
Actual GPU test65checks PASS at1920x1080:four neutral/tuned/extreme parameter
sets,four owner IDs,EXACTcolour includingalpha,EXACTcoverage and independently
expected depth0/.2/1accepted,-1/2/NaN/Infexcluded;zero owner rejected.

Eight alternating32-draw GPU timestamp batches per route:median separate45.595us,
combined38.368us,15.85%less for THIS SMALL STAGE. One earlier two-batch repeat had
53.885usoutlier;bounded repeat count increased,not discarded as false failure.
This is not a whole-renderer/gameplay15.85%gain and not proof of fewer blips.

Actual final Remix fixture031459-406014:595/600fixed-window delivery,596total
draws,152367changed pixels,border untouched,state_errors0,resize/recreation,
ACK3/reject0,resident owner transitions and normal owned exit PASS. Source1928
records/964exactpairs,all source anomaly counters0. COMBINED_POSTmarker present.
Prior031146-627028also595/600. Delivery unchanged. Uncontrolled earlier fixture
postprocess median512.5vs487us,p95680vs670us is supportive context,not a causal
whole-frame speedup. No SFC gameplay run by Codex this turn.

Qualifier first failed because PS5Tee-Object emitted UTF16test log;explicitUTF8
fixed it. WindowsPowerShell archive lacked ZIPtype and stopped before deletion;
established modernPowerShell retry succeeded. No security settings weakened.
Vendor40common-device-disposal warning remains unresolved.

## Retention, limits and final state

Both completed fixtures'199generated copies each were recoverablyZIPcompacted
after decompressed hash checks,82,188,024bytes each;raw logs/packets retained:

- `artifacts/remix-runtime/archives/20261022-031146-627028-return-fixture-binaries.zip`,
  6,861,857bytes,SHA25665B41B8980A7609DB3326F569DCE96846C00B9C43376525C2432730EF93043E4.
- `artifacts/remix-runtime/archives/20261022-031459-406014-return-fixture-binaries.zip`,
  6,861,857bytes,SHA25691AC7BE30A9B51B6D978788FC023CE992141BF5432A4F2E1A885C6B876CDA66C.

Existing90stactical/five-minuteworkflow,32MiBlogs,128MiBimages/outputresources,
20GBaggregate,current-user maps/fixed surfaces unchanged. No continuous readback
in production;GPU unit-test readback is standalone bounded validation only.
Original/copied clients SHA2564D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29
unchanged. No owned game/renderer/receiver left running. Index empty;all prior/
new changes unstaged/uncommitted on0fc1300,no push. Probe/contract paths exist,
curated JSON and PS parser/diff/preflight checks PASS.

READY for ONE sponsor comparison with same persistent-scene launcher and cues.
Expect same textured offset player ship/settings,not a new effect. Modest
processing improvement,NOT seamless-return guarantee. First-launch3.6msbudget
versus~6msrender remains unresolved;do not report fixed by this small pass.
Actual death hook and multi-object display remain pending. After comparison,
review evidence/regressions then move on per sponsor's bounded-pass decision;
do not start another optimization loop without approval.

Exact next action:sponsor runs persistent-scene launcher once,camera swaps at
cues,normal exit at twoLOWbeeps;review continuity/misses and safety afterward.

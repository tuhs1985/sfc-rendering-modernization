# Codex run — prepare contemporaneous semantic/depth calibration

Run SFC-RETURN-20261017-17,2026-10-17. Active task:approved in-game return-path
investigation,next bounded calibration after Run16. Sponsor "Go" authorizes
preparation;no new gameplay executed. HEAD e96765a1a34c15212ed22f11edeb9a708b9fc18d,
index empty,prior dirty/untracked return-path work preserved. FuelGuard attached
to actual current thread;no sandbox daemon,helper,subagents,staging or commit.

## Authority / starting evidence

Read newest HANDOFF and its operating instructions,approved M1/current amended
gate disposition,Run16,REMIX-COVERAGE-001/DEPTH-001,coverage contract/readiness,
actual semantic observer/live-scene producer,depth reader/addon,runner/controller,
offline fixtures and camera/mesh decoders. Run15 native depth has no semantic
fields;Run16 historical replay matches478pixels but cannot be treated as Run15's
pose. Existing30Hz records are deliberately asynchronous. Do not reopen proven
seam,repeat broad reconnaissance,select renderer architecture or hide any ship.

## Result / engineering adjudication

**READY FOR SPONSOR RUNTIME CALIBRATION.** CONFIRMED offline:fixed current-frame
semantic mailbox bypasses30Hz throttle,paired GPU/worker sidecars preserve
QPC/Present/resource epoch/session/engine frame/thread identity;stale/conflicting
observations rejected. Three known10_1 GPU snapshots carry distinct synthetic
engine frames2,43,84. Actual SFC scene/frame/depth correspondence remains
unproven. No replacement,occlusion/UI composition or milestone/aggregate TRL PASS.

Selected design:reserved scene-mapping space,not cross-DLL exported accessor or
another game hook. The addon holds an independent mapping handle;no call into
an unloading observer DLL. Nonblocking try-lock around fixed storage;contention
drops evidence. At native draws record current semantic frame;at Present reject
mixed/repeated/stale frames,require qualified semantic rows from same native
render thread,check frame again before submission. Different submodel/source/
revision/pose/camera within one owner/frame becomes explicit ambiguity,not last
callback wins. Eight fresh asset revisions maximum in calibration mode;ordinary
live-scene behavior remains default-off/unchanged. Matching rigid asset may have
been captured earlier in same session;no in-place deformation claim.

Full proven observer replaces the one-shot gate DLL for this mode ONLY;never
install both over the same ship entry. Its named tactical event arms20s depth
window;controlled stop at24s restores/drains/unloads before exit cue. Geometry
006AB410 hook/private copy/tints/shading OFF;existing wrapper read-only capture ON.
M1Stop deactivates mailbox immediately before recorder drain;worker stop also
deactivates before joining. Reader mapping stays valid independently until addon
shutdown. No ABI/calling-convention changes;existing trampolines preserve state.
Those live execution assumptions require the prepared run,not a decompiler claim.

Rejected:nearest-timestamp joins,old geometry/pointer reuse from another process,
additional callback hooks,owner suppression before measurement,Toolkit preview,
continuous screenshots,forcing feature11_0 or changing original translator.

## Exact changed files this run

Added:

- tools/m1_component/m1_present_calibration.h
- tools/remix_runtime/present_calibration.py
- tools/remix_runtime/qualify_present_calibration.py
- tests/present_calibration_tests.cpp
- tests/test_present_calibration.py
- docs/reconnaissance/probes/REMIX-CALIBRATION-001.md
- docs/reconnaissance/evidence/20261017-present-calibration-offline.json
- this run record.

Modified:

- tools/m1_component/m1_live_scene.h (opt-in mailbox/pre-throttle records/8revision cap)
- tools/m1_component/m1_component.cpp (scene frame publication/immediate stop disable)
- tools/m1_component/build_m1_component.ps1 (full semantic DLL /Brepro)
- tools/remix_runtime/depth_snapshot.h (optional paired semantic sidecar)
- tools/remix_runtime/run_return_game.py (concurrent semantic capture instead of duplicate gate)
- tools/remix_runtime/start_return_image_session.ps1 (-Calibration forwarding)
- tools/remix_runtime/build_return_probe.ps1 (new22check native test)
- tools/remix_runtime/prepare_full_reshade.py (current-source dependency coverage)
- tools/remix_runtime/archive_broad_evidence.py (retain explicit semantic/fresh-asset packets)
- tests/depth_snapshot_gpu_tests.cpp (opt-in deterministic provider)
- tests/m1_live_scene_tests.cpp (pre-throttle/worker-stop checks)
- tests/test_remix_visibility_cli.py (reject unsupported calibration launch)
- docs/reconnaissance/ship-replacement-readiness.md
- docs/HANDOFF.md.

No reference original,accepted installation,launcher settings or old evidence
overwritten. Generated binaries,captures,qualifications,archive remain ignored.

## Validation / reproducible commands

VS2026 18.7.3 strictx86 /W4 /WX builds PASS. Full M1 native contract,tint/shading,
corner,surface,mesh,proxy/export regressions PASS;new producer test separately
passes capture,bypass of30Hz throttle,frame identity,thread and worker close.
Return native37wire+13search+14bounded-trace+22mailbox checks PASS.
Python170tests PASS2.768s;PowerShell launch parser PASS;git diff --check PASS
(existing LF→CRLF advisories only). Final shutdown tightening rebuilt full semantic
DLL+producer test and reran producer/GPU qualification;earlier full suite ran before
that two-line deactivation addition. Native cleanup behavior is not silently claimed
tested by stale binaries. No actual SFC run in this session.

Commands (python = bundled Python3.12.14;PS7 = bundled7.6.5):

```text
PS7 -NoProfile -File tools/remix_runtime/build_return_probe.ps1
PS7 -NoProfile -File tools/m1_component/build_m1_component.ps1
python -m unittest discover -s tests -p test_*.py
python tools/remix_runtime/run_return_fixture.py --depth-snapshots --observation-only --graceful [--with-depth]
python tools/remix_runtime/run_return_fixture.py --broad-capture --observation-only --graceful [--with-depth]
python tools/remix_runtime/qualify_present_calibration.py --execute
python tools/remix_runtime/prepare_full_reshade.py --qualify artifacts/remix-runtime/runs/20261017-202025-867803-return-fixture artifacts/remix-runtime/runs/20261017-202038-122832-return-fixture
python tools/remix_runtime/qualify_depth_snapshots.py artifacts/remix-runtime/runs/20261017-201921-364957-return-fixture artifacts/remix-runtime/runs/20261017-202007-572543-return-fixture artifacts/remix-runtime/runs/20261017-202333-678699-calibration-fixture
python tools/remix_runtime/run_return_game.py --depth-snapshots --observation-only --calibration
git diff --check
```

Last command is READ-ONLY preflight without --execute:PASS,no game/renderer
started. Both current-source qualifications and pinned component/addon binary
checks PASS. Runner uses prebuilt qualified observer to keep5minute envelope;
it rebuilds existing return tooling and checks resulting reproducible binary.
Full observer reproducibility independently verified before final stop change
(A2B361...→same);final binary SHA recorded below,not claimed twice rebuilt.

Sandbox first build failed replacing existing generatedreshade_registration.lib
with LNK1114/error5. Scoped external build/test execution resolved file replacement;
no security settings/UAC policies changed. Build/GPU fixture tool escalations
are not an assertion of a persistent elevated sponsor token.
Tests use artifacts/test-temp for TEMP/TMP. Initial native/implementation fixtures
preceded new runbook;that timing is explicit. Runbook finalized before gameplay.

## Evidence / bounds

- Positive depth201921-364957:951frames,state_errors0,normal exit,3known images.
- Negative depth202007-572543:953frames,state_errors0,normal exit,no images.
- Broad positive202025-867803:592frames,state_errors0,drops0,resize/recreation PASS.
- Broad negative202038-122832:593frames,same clean bounds/state/lifecycle.
- Final calibration202333-678699:3known GPU+semantic pairs,frames2/43/84;
  producer regression PASS. Earlier202120-660066 retained as development evidence.
- AddonSHA A9515D19F4BB926714E45B457190DE493EC98078A6809085341E653129EB2C29.
- SemanticDLL SHA BCC3BB19276A740E514D5CA4C0A1CF09ACF0169416251C1F552384AE069B8FE1.
- Detailed current-source/build provenance in curated JSON/global ignored qualifiers.

Probe definition documents tool versions,launch,privileges,triggers,filters,
limits,expected volumes,cleanup and analysis. 3depth/color pairs64MiB (warn32),
ancillary32MiB (warn16),whole96MiB;20s capture/24s observer/300s prepared workflow.
Mapping16MiB,8asset revisions,37392bytes added sidecars;no polygon firehose or
continuous images. Offline native fixture limited30s/1MiB GPU output;producer10s.
Bounded public broad fixture is only regression,not another SFC broad pull.

Archive20261017-present-calibration-offline.zip366584bytes,104entries,
15,415,907Bsource,CRCverified,SHA3856557EBCDA66983D400761ACB5C7541C84C077E2E914AD86694FDCD0F43149.
Selected6exact run folders using archive_broad_evidence.py;semantic0..2 and
asset1..8 packets explicitly included. Raw retained,not removed,well under10GB.

## Remaining uncertainty / final state

Actual same-thread/frame ordering,qualified camera projections/native GPU ship
depth and foreground/UI/effects still require runtime/calibration adjudication.
Known warnings67(SFC) and40(separate SDK) remain unresolved;no new claim of their
absence because no game/Remix host was run. Native synthetic state restoration is
CONFIRMED,not proof of original game resource lifetime. No ship suppression.

Both accepted/copied client SHA4D65761D... matches baseline;all7critical files in
both installations equal Run15's accepted final records. No active SFC,controller,
host or fixture remains. HEAD e96765a,indexempty,implementation/evidence
unstaged/untracked,prior work preserved,nothing staged/committed.

**Exact next action:**run prepared -Calibration from established elevated parent;
ordinary two-ship fixture,hold initially,one small camera move at single cue,
normal exit only at double cue. Analyze paired fresh records before suppression.

# Codex run — earlier supported depth observation

Run SFC-RETURN-20261017-05,2026-10-17 EDT. Task: locate one earlier supported
scope after eight late-overlay samples found no bound DSV. HEAD e96765a,index
empty,existing unstaged/untracked work preserved. FuelGuard actual-thread recent
hook verified,no daemon/helper/delegation. Read HANDOFF,ship readiness and latest
late-visibility runtime review; approved return-path execution remains authority.
No requirements change,original suppression or new renderer architecture.

## Source adjudication before implementation

Pinned ReShade8cf85bd12d56697d756d4fcb45e501f5d1b540fa:
- source/dxgi/dxgi_swapchain.cpp905-913 invokes public addon_event::present for
  D3D11 BEFORE present_effect_runtime. Earlier than effects/UI,not proven pre-SFC
  HUD. This public event is permitted by limited build's addon_manager.cpp572
  range check (present itself is not blocked).
- source/runtime.cpp546 captures application state;759 invokes reshade_present
  AFTER restoring it,so that similarly named event is NOT the earlier callback.
- Late reshade_overlay is inside GUI/effect processing; absence there does not
  adjudicate original application's DSV. Do not rename it as original state.
Official URLs:
https://github.com/crosire/reshade/blob/8cf85bd12d56697d756d4fcb45e501f5d1b540fa/source/dxgi/dxgi_swapchain.cpp
https://github.com/crosire/reshade/blob/8cf85bd12d56697d756d4fcb45e501f5d1b540fa/source/runtime.cpp

CONFIRMED source ordering; actual installed-build dispatch and safe descriptor
capture require native fixture corroboration. STRONG HYPOTHESIS: earlier callback
can inspect app-bound DSV unavailable after ReShade changes OM state. Not a claim
SFC retains useful scene depth at Present,or that descriptor proves visibility.

## Prepared experiment / limits

New defaultOFF -InspectEarlyDepth / --inspect-early-depth. Same copied installation,
runtime/component/launcher/gate/90s/300s/32MiB bounds as REMIX-RETURN-001. Eight
descriptor checks>=1s apart after tactical arm; no new geometry hook,copies,
readbacks,rebinding,disk access,waits or retained COM references in callback.
Filter by active runtime's device,window AND current backbuffer identity. Preserve
existing -InspectVisibility late path independently; never run both together.
Optional visibilityScope2 at reserved176,mandatory v2 prefix256B unchanged.

Before gameplay run stand-in with explicit synthetic D24S8 DSV bound before
Present,depth testing disabled. Require eight positive earlier observations,
exact descriptor and normal graphics-state/image/cleanup checks. Also run early
mode without DSV and ordinary default path. Synthetic attachment proves getter/
ordering/dispatch only,NOT meaningful depth values or SFC scene provenance.
Test/probe definition updated BEFORE runtime; outcomes/final files recorded below.

## Implementation / material decisions

- New -InspectEarlyDepth flag selects public addon_event::present; registered
  ONLY when explicitly requested. Filter active runtime device/window/current
  backbuffer,then existing bounded read-only descriptor getter. No restricted
  draw/depth-binding events,proxy replacement,native vtable interception or shader
  injection. Original rendering always continues; diagnostic geometry hook OFF.
- Preserve old late -InspectVisibility and default image workflow; arguments
  mutually exclusive. Mandatory v2 block256B unchanged,scope2 at176 and separate
  DSV view-format at180 in formerly reserved bytes,remaining72reserved.
  Classification explicitly EARLY_* and always unqualified scene-depth semantics.
- Fixture binds known D24S8 view; first harness expected resourceformat45 but
  observed44/bind72. Independent fixtureGetDesc corroborates actual typeless
  R24G8 resource behind D24S8 view45,not mismatched sampler. Corrected harness
  compares exact independently logged resource AND view descriptors. Do not
  infer why proxy/driver chose representation from observed numbers alone.

## Experiments / new defect

All artifacts under artifacts/remix-runtime/runs,UTCfoldernames; localdateEDT.

-143713-170204:8early samples/8DSV,468frames,state_errors0,imagephasesPASS,
  but orchestrator rejected incorrect typed-resource expectation. Test-harness
  assertion defect,not engine/observer failure. Preserved rejected evidence.
-143835-609840: corrected full-runtime positive8/8,resource44/view45/bind72,
  1024x768/samples1 exact native match;11.406s,host/fixtureexit0,468frames,
  state_errors0,all5imagephasesPASS.
-143909-190743: full-runtime no-depth8/0,11.375s,host/fixtureexit0,467frames,
  state_errors0,all5imagephasesPASS. Thus public earlier callback dispatch and
  bound/unbound discrimination CONFIRMED offline,not SFC depth qualification.
-143920-741724: ordinary default image regression FAILED,do not call all
  regressionsPASS. Hostexit3221225477(0xC0000005),WindowsApplication1000 confirms
  nvoglv64.dll32.0.16.1742(driver617.42),faultoffset0xF10CF4,PID3440.
  Same offset as earlier custom-material test but NOW default material; reject
  any claim the fault requires custom material. No early callback registered in
  this mode. Cause NOT adjudicated; no driver update/runtime patch/automatic
  repeated fault retries. Event read initially denied in sandbox,read-only host
  access succeeded with approval. Original stand-in continued1485frames,
  state_errors0;missing image caused intended self-test exit1 after25s.
  This is a renderer stability risk before actual ship replacement,not evidence
  our depth getter failed or that game drawing froze.

## Bounded pivot: isolate read-only question from renderer

Depth-binding observation needs NO Remix image. Added --observation-only with
--inspect-early-depth,host --observe-only creates same secure4KiB channel but
branches before runtime load/window/device creation. Scalar control only; no
new graphics architecture or CPU-frame bridge. Component's existing bounded
512KiB buffers remain allocated but image flag0,zerooutputcopies/draws. Eight
read-only observations through public callback. Runtime branch remains available
but is NOT certified stable by control-only tests or recommended for next run.

This change and exactlimits/procedure documented before testing:
-144223-961088: observation-only known-depth8/8,10.921s,411frames,
  state_errors0,resize/recreate1,host+fixtureexit0,zeroimagecopies/draws.
-144236-165845: observation-only no-depth8/0,9.219s,412frames,state_errors0,
  resize/recreate1,host+fixtureexit0,zeroimagecopies/draws.
  Both host logs MODE OBSERVATION_ONLY no_runtime_loaded=1,OBSERVATION_STOP
  samples8/bounded1. No SDKShutdown/clean-runtime claim because runtime not loaded.

## Validation / files / final state

Native build_return_probe.ps1 VS2026x86/x64 /W4 /WXPASS,native37wire checksPASS.
Full106Python testsPASS1.610s,projectTEMP/TMP to avoid restricted defaultTemp;
new tests cover distinctscope/fieldoffsets and reject ambiguous CLI modes before
file access/child launch. PS parsersPASS,read-only early/observation-only preflight
PASS,git diff --checkPASS(lineendingwarningonly). Existing semantic source and
M1 ABI hooks untouched. No SFC run this execution. No owned host/fixture/loader/
game/controller at final check. Original+copied clientSHA unchanged:
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.

Files modified this run: tools/remix_runtime/{return_addon.cpp,return_wire.h,
return_channel.py,return_host.cpp,return_fixture.cpp,run_return_fixture.py,
run_return_game.py,start_return_image_session.ps1}; tests/remix_return_wire_tests.cpp,
tests/test_remix_return_channel.py; new tests/test_remix_visibility_cli.py;
probe REMIX-RETURN-001,contract/readiness,HANDOFF,this runrecord. Preserve all
prior uncommitted files. No references/client/proxy/requirements/helper edits.
HEAD e96765a,indexempty,unstaged/untrackedonly,NOstaging/commits.

## Result / exact next action

READY FOR SPONSOR READ-ONLY RUNTIME TEST,not ship replacement. Use established
elevated parent,start_return_image_session.ps1 -InspectEarlyDepth -ObservationOnly.
Usual two-ship skirmish,briefly both visible,play normally,exit aftertwo beeps.
No triangle/appearance changes expected. Adjudicate8early SFC descriptors; if
none,report missing earlier access before changing interception approach. Positive
DSV still needs content/convention/visibility qualification and matching-owner
contract. Keep renderer crash +40common-object warning open before any suppression.

Final archive: artifacts/remix-runtime/archives/20261017-early-depth-preparation-evidence.zip,
144092B,selected JSON/log/text/BMP from six experiments above. Binaries excluded;
original small evidence retained,no deletion. Final diff/preflight repeatedPASS,
index still empty. New gameplay not executed by analyst; prepared test awaits
sponsor. Earlier default-image regression failure remains recorded,not erased
by the passing control-only tests.

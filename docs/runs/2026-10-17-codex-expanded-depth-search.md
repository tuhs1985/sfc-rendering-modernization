# Codex run — expanded read-only depth search

Run SFC-RETURN-20261017-07,2026-10-17 EDT. Sponsor explicitly requests expanding
and modifying search after narrow getters proved negative. HEAD e96765a,index
empty; preserve existing unstaged/untracked work. FuelGuard actual-thread recent
hook verified,no daemon/helper/delegation. Read HANDOFF,current probe,source and
prior engine scene-end disassembly. No requirements change or ship suppression.

## Question / design before execution

Can currently bound depth be observed across engine scene construction,final
flush and presentation—not just8samples at presentation? New default-off SearchDepth
observes four exact-build engine sites plus existing allowed DXGI/overlay events.
Full tactical90s counters,not a startup8second sampling window. Fixed32resource
descriptor rows; no owner/name/resolution/resource-ID filter. Device/context
scope and explicit skipped/missing/overflow counts prevent false exhaustive claim.
Native-context calls only on its verified creation thread; mismatches reported.

Engine sites0069E300,0069E3D0,0069E41B,0069EB90 from existing M0/static evidence.
Startup Detours installation only after copied process path/hash verification,
expected bytes and main-image owner checks. x86 naked observers preserve flags,
GPRs,DF,FPU/SIMD and original stack,then resume original execution. Mid-call
0069E41B covers FF5128/85C0; do not reinterpret as function entry/early return.
Install before cliententry; restore on owned worker at stop using thread-enrolled
Detours transaction,verify bytes and mask. Failure remains fail-open and is PARTIAL,
no hot unload while hooks/storage active. Original on-disk artifacts untouched.

No native D3D11 method patch,blocked ReShade event,proxy swap or renderer change.
Read-only DSV getters may STILL miss bindings entirely inside translator calls,
unbound retained resources,other devices/deferred contexts. Pointer labels are
process observations,not stable resource lifetime or semantic-owner identity.
No claim descriptor alone is usable depth/coverage or ship-replacement readiness.

Protocol search extension occupies bytes256..2559 of existing4KiB same-user
mapping (2304B),own version/magic; main v2prefix unchanged.32resource rows,
6phase counters,32MiB runhard/16MiBwarning,full90s until stop,300s total.
No per-draw transcripts,images,readback,allocation/disk/waits in observation.
No Remix loaded; existing observation-only host used. Offline synthetic four-site
fixture must verify state/stack,positive+negative descriptors,overflow bounds,
all6phase activity and clean byte restoration before sponsor gameplay.

Implementation/results/finalstate recorded below. No new game launched yet.

## Implemented scope / contract

New depth_search.h and depth_search_wire.h,depth_search_channel.py. Main return
v2prefix untouched; expanded4KiB mapping extension independently validated at256,
2304B. Six32byte counters plus32x64byte resource/view observation rows. Each phase
records calls,missing/found,no-context,wrong-thread,invalid,busy,lastTick. Global
window,start/endTick and phase-age checks prevent claiming full temporal coverage
from a brief startup burst. Tableoverflow retained as counter,never grows.
Pointer labels plus context epoch identify observations only; pointer recycling
within epoch not qualified as object lifetime. All resource formats/sizes admitted,
no selected-ship/model/resource-name filter. Not a GPU resource inventory.

Source arguments -SearchDepth (PS) / --search-depth --observation-only (Python)
are explicit defaultOFF. PS implies observation-only; Python rejects renderer
mode. Four hooks installed in newly created verified test process before entry;
same engine original bytes verified,not reference originals patched. Existing
006AB410diagnostic hook OFF. Profile captures full90s (does not stop at the old
60s image-disconnect phase). Counter/table evidence only; output remains32MiB.
After90s signalstop,wait<=8s for worker detach/byte verification BEFORE exit cue.
No hot unload. Any restore/header/scope/capacity failure recorded PARTIAL.

### ABI/lifecycle adjudication

Entries0069E300/3D0 stolen bytes53568BF157 preserve caller execution;0069EB90
prefix568BF18A86283C0000 includes full instruction. Mid-call0069E41B FF5128/85C0
already has COMthis on stack; collector must neither return early nor consume it.
Observer saves flags/GPR/DF/FPU/SIMD,then replays original indirect CALL+TEST in
resident DLL code and resumes0069E420. This prevents an in-flight native call
returning into a Detours trampoline freed during detach. Generic prologue hooks
contain no CALL in stolen bytes. No geometry or parameters modified.

Offline synthetic phase2 mirrors actual call/test and stdcallthis/HRESULT stack;
each frame verifies ESP,flags and512B FX state around four originals. Additional
slow originalcall test requests detach while fake EndScene sleeps2s; DLL return
path remains valid after hooks restore. This mechanical corroboration is NOT
actual SFC ABI/runtime success (game test still pending). Worker enrolls process
threads in Detours transaction outside rendering/loader callbacks; failure aborts,
reports error and keeps DLL/storage resident. Original drawing always forwarded.

## Validation / exact experiments

Artifacts/remix-runtime/runs (UTCnames;localdateEDT):
-161921-932114 positive expanded:429frames,state_errors0,all6phases,3resource
  observations across resize/recreation,restoredMask15,error0,host/fixtureexit0.
-162054-055735 negative expanded:426frames,0resources,all6phases/restoration,
  state_errors0,normalexits.
-162103-473715 prior narrow observation-only:8/8knownDSV,411frames,
  normalexits and resize/recreation preserved. Legacy path not removed.
-162208-881470 +162403-317099 positive rebuilds:429/428frames,all6phases,
  state_errors0,restored15,normalexits; added malformed-table and temporal guards.
-162627-460621 slow-test harness read header before DLL init; header mismatch
  correctly rejected,not an engine failure. Fixed harness to wait for ready before
  handshake read. Preserved failed evidence,not represented as passing.
-162721-538839 slow in-flight teardown:234frames,all6phases,state_errors0,
  restored15,error0,handshake2(originalreturned),7.840s,normalhost/fixtureexit0.
-162729-548353 final negative:435frames,state_errors0,all6phases,restored15,
  normalexits. No Remix/runtime-driver reruns or new SFC gameplay this execution.

Build_return_probe VS2026x86/x64 /W4 /WXPASS;37return-wire+13search-wire checks
PASS. Search-wire covers fixedsize,merging phase records,capacity32/overflow,
epoch distinction and malformedheader. Python full113testsPASS (final check),
layout/limits/partialverdicts,temporalcoverage and CLI guards. PS parse/preflight/
diff checksPASS; exact final results recorded below. Driver617.42+0xF10CF4 and
40common-object warning unchanged open risks; observation-only avoids renderer.

## Files / repository / next action

Modified return_addon.cpp,return_fixture.cpp,run_return_fixture.py,run_return_game.py,
start_return_image_session.ps1,build_return_probe.ps1; new depth_search.h,
depth_search_wire.h,depth_search_channel.py,tests/depth_search_wire_tests.cpp,
tests/test_depth_search_channel.py; extended test_remix_visibility_cli.py;
updated probe,readiness,contract,HANDOFF,this runrecord. Existing client/semantic
source/proxies/requirements/helper untouched. HEAD e96765a,indexempty,
all existing/new work unstaged/untracked; no staging/commit. Original/copied
clientSHA256 remains4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.

READY FOR SPONSOR RUNTIME TEST. Existing elevated parent:
start_return_image_session.ps1 -SearchDepth. Familiar two-ship skirmish,play
normally for90s,normal exit at two beeps. No triangle or changed ships. Full-window
counts/resource descriptors now cover six identified CPU scopes; still miss
bindings entirely inside translator calls,retained-unbound resources,other
devices/deferred contexts. Wrong-thread/no-context/tableloss yield explicit
PARTIAL,not false "no depth anywhere". No ship suppression or milestonePASS.

Final reproduction: bundledPowerShell7.6.5 -File tools/remix_runtime/build_return_probe.ps1;
bundledPython3.12.14 tools/remix_runtime/run_return_fixture.py --graceful
--search-depth --observation-only [--with-depth] [--slow-end-scene];
Python -m unittest discover -s tests -p test_*.py (projectTEMP/TMP);
run_return_game.py --search-depth --observation-only WITHOUT --execute for
read-only preflight. Final113testsPASS1.755s,PSparse/preflight/diffPASS,50native
wire checksPASS. No owned process at final inventory; no-match status is not a
failed game exit. Final client hashes unchanged,indexempty.

Selected JSON/log/config evidence archived to
artifacts/remix-runtime/archives/20261017-expanded-depth-search-evidence.zip;
compiled binaries excluded,small original evidence retained,no deletion. No
continuous screenshots or multiGB traces. Final prepared runner awaits sponsor,
not automatically launched. No new runtime-driver stability claim.

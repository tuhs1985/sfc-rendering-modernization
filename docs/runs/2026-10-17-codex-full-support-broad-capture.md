# Codex run — full-support broad discovery capture

Run SFC-RETURN-20261017-09,2026-10-17 EDT. Sponsor explicitly approved qualifying
full-add-on-support ReShade offline and ONLY in isolated test copy after run08
identified blocked public application callbacks. Starting HEAD e96765a,index
empty,existing uncommitted return-path work preserved. No helper/delegation,
staging or commit. Authority: HANDOFF,approved M1/current gate disposition,
REMIX-RETURN-001,run08 and existing expanded-search evidence. FuelGuard exact
thread recent-hook verified;no daemon started.

## Pinned dependency and implementation

Official https://reshade.me/downloads/ReShade_Setup_6.7.1_Addon.exe downloaded
with Referer https://reshade.me/; restricted-shell DNS failed,approved network
escalation succeeded. Package SHA256
FC55C5C62D0BC43BF02C40EC9AEF69E0B74F22A6017403AF1897EC32E5CD0E8F.
Archive inspected/extracted,installer NEVER executed. Full x86 ReShade32.dll
SHA256 A1BA732B5E31E0405CDE322CC5EC62CF972B3FBAEFBB6CBDC8A24DA00D58AE24;
product6.7.1,file6.7.1.2131 versus existing limited6.7.1.2133. Pin actual
difference,do not assert identical binaries. Existing SDK API18/ImGui19250
headers retained;actual external registration and event delivery tested.

New default-off broad_events.h/broad_trace.h use allowed public resource/view/
device/command lifecycle,target binding,draw/indexed counts,clear,copy/resolve,
viewport,pipeline/state,execute and Present events. No owner/name/size/format
selection filters;no native D3D11 patch or blocked-event bypass. Explicitly NOT
all API events/GPU trace: shader/resource contents,vertex/index bytes,descriptor
tables,buffer data,indirect draws and deferred replay reconstruction absent.
Lifecycle plus target bindings/reset start during startup;other detail gated by
existing tactical hook. Geometry006AB410 hook stays OFF;no engine search hooks
installed in broad mode. No Remix renderer/triangle/ship suppression.

128B version1 records,128B header,16MiB preallocated ring. Producers use try-lock
only against other producers;single consumer uses acquire/release queue indices
and never locks callbacks out for disk writing. Any concurrent-producer/ring
loss is counted and makes resultPARTIAL. Active-callback counter drains before
worker finalization. Resident storage,normal-process-exit lifecycle,no hot unload.
Only worker creates/writes file;CREATE_NEW;batch byte reservation includes file
header;strict2,000,000,000B hard/warn1,000,000,000B;10s after tactical gate;
285s internal watchdog. Queue saturation/error stops detail,not original drawing.

Shared status in unused mapping bytes256..383;legacy256B prefix unchanged.
New streaming analyzer bounds resource/view maps65536,contexts4096,depth rows4096,
exports at most512candidate summaries;raw records preserve all retained details.
Devices+creation sequence distinguish lifetimes;unknown associations remain
unknown. Bound-during-draw metadata is NOT proof of depth testing/usable depth.

Runner -BroadCapture uses verified copy process path/client hash,ordinary automatic
tactical gate,observation-only host. Temporarily swaps only copied dxgi.dll after
hash-verified backup,using verified same-directory staged atomic replacement.
After normal game exit restores copied proxy/config and records hashes;never
restore/unload while game is alive. Interrupted transaction retains exact backup
and reports deferred rollback. Original installation/translator/launcher paths
untouched. Full-support qualification manifest and source hashes required before
runtime. Exact commands and final validation/evidence follow after qualification.

## Offline iterations (preserve failures)

- Initial restricted build could not overwrite elevated-owned import library:
  LNK1114/error5. Existing elevated workflow rebuild succeeded;no ACL changes.
- Python initial tests hit sandbox TEMP permissions,not assertion failures;
  rerun with project artifacts/remix-runtime/test-temp TEMP/TMP passed.
-174541-277908 positive fixture:592frames,state_errors0,normal exit,transient
  depth captured,but20dropped records. PARTIAL;worker/producer lock contention
  fixed using separate queue indices,not ignored.
-174913-340458 positive:591frames,zero state errors/drops,resize/recreate/exit0.
-175012-202638 negative:587frames,zero state errors/drops,exit0;harness rejected
  missing resource notification because no explicit non-depth resource existed.
  Added16square color resource;not represented as a collector success then.
-175322-282048 positive and175328-191106 negative:extra zero-count draw check
  introduced without a complete graphics pipeline;both failed Present,ReShade
  log reports DXGI_ERROR_DEVICE_REMOVED / DXGI_ERROR_DEVICE_HUNG. No SFC launched.
  Cause attribution not proven solely by this sequence;replaced incomplete
  synthetic draw setup with valid VS/PS/index buffer before further qualification.
  These are preserved failed GPU fixtures,not passing regressions.

Latest completed offline suite before final valid-scene fixture:123Python tests
PASS;native37return+13search+14broad checks PASS,VS2026x86/x64 /W4 /WX.
Broad native checks cover exact128B layouts,overflow-safe budget math,4KiB cap,
loss after cap and invalid output-path fail-open status. Final qualification,
dependency rollback checks and runtime readiness recorded below when complete.

## Files and work state

New broad_trace.h,broad_events.h,broad_capture.py,prepare_full_reshade.py;
tests/broad_trace_tests.cpp,test_broad_capture.py. Modified return_addon.cpp,
return_fixture.cpp,build_return_probe.ps1,run_return_fixture.py,run_return_game.py,
start_return_image_session.ps1,test_remix_visibility_cli.py;docs/probe,dependency
manifest/run/HANDOFF updated at closeout. Generated binaries/captures ignored.
No accepted-client modification,no actual SFC run yet;all work unstaged.

Historical in-progress checkpoint: final valid-scene qualification was pending
here. Superseded by the completed closeout below;never use a stale source-hash
qualification after changing the collector.

## Completed qualification / final validation

Valid VS/PS/index-buffer fixture replaced incomplete zero-count draw setup.
MSVC /WX also caught a shadowed test-only local;renamed before successful build.
Initial valid fixtures175622-412183 positive (582frames/12,765records/1,634,048B)
and175642-884245 negative (575frames/12,641records/1,618,176B) both passed with
zero drops/state errors and normal exits. Final code review then guarded failed
header-seek before rewrite so a seek failure cannot append beyond cap;analyzer
now retires device-scoped maps on device destruction and explicitly reports
truncated candidate summaries. New native source was rebuilt/requalified:

|Final run UTC suffix|Result|
|---|---|
|180332-043697 positive|582frames,12,785records,1,636,608B,3creation-distinguished DSVs;zero drops/state errors;resize/recreate;host/fixture0|
|180344-409639 negative|579frames,12,709records,1,626,880B,0DSVs;zero drops/state errors;resize/recreate;host/fixture0|
|175834-505185 isolated rollback|No game launch;copied proxy oldSHA -> fullSHA -> exact oldSHA;verified backup retained|
|180139-723636 legacy early getter|Unchanged limited proxy;412frames,8/8DSV observations,zero state errors;resize/recreate;host/fixture0|

All synthetic draws use valid shaders/index data,original public callbacks
return false and native drawing continues. Fixture binds DSV during draws then
unbinds beforePresent;post-Present sentinel verifies it is unbound. Thus event
coverage sees what presentation getter cannot. Depth testing deliberately OFF:
this is NOT usable tactical-depth proof. Actual SFC full-support behavior pending.
The previous driver617.42/nvoglv64 fault and40-object warning remain unresolved;
this observation-only host does not load Remix and does not test those defects.

Final VS2026Community18.7.3/MSVC19.51.36248 x86/x64 /std:c++20 /EHsc /W4 /WX
build PASS. Native37return+13search+14broad checks PASS. Last4KiB cap case retained
exact4096B,11,112expected skipped/dropped events,zero writer errors;no GPU needed.
Final Python3.12.14 full127tests PASS2.027s (projectTEMP/TMP):binary parser,
creation/device/pointer reuse,malformed/partial/oversized records,rollback and
independent-change guard,archive CRC/raw preservation,CLI,existing regressions.
Existing native M1 contract and WINMM forwarding tests PASS. Initial forwarding
invocation omitted required DLL path and was rejected;corrected invocation with
artifacts/m1/bin/winmm.dll passed. No native live-bridge/scene executable test
claim here (those require separately created channels);existing Python suite ran.
PS parsers/read-only broad preflight/diff/path checks PASS at closeout.

prepare_full_reshade.py --qualify records both final native fixtures and hashes
for twelve component/runner/preparation/archive sources. Broad preflight refuses
changes until requalification. Durable copy:
docs/reconnaissance/evidence/20261017-broad-offline-qualification.json.
Generated runtime qualification stays in ignored dependencies;no live session,
server or mapping is required to persist across restart. No owned process survives.

## Reproduction / capture / archive

Use bundled PowerShell7.6.5 and Python3.12.14 under
C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies.
All paths below relative to repository except explicit launcher command:

```text
python tools/remix_runtime/prepare_full_reshade.py
pwsh -NoProfile -File tools/remix_runtime/build_return_probe.ps1
python tools/remix_runtime/run_return_fixture.py --graceful --broad-capture --observation-only --with-depth
python tools/remix_runtime/run_return_fixture.py --graceful --broad-capture --observation-only
python tools/remix_runtime/prepare_full_reshade.py --qualify <positive-run> <negative-run>
python tools/remix_runtime/qualify_broad_rollback.py
python -m unittest discover -s tests -p test_*.py
python tools/remix_runtime/run_return_game.py --broad-capture --observation-only
```

Last command is read-only preflight WITHOUT --execute. Actual sponsor entry from
established elevated parent (no routine UAC or execution-policy/global changes):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\remix_runtime\start_return_image_session.ps1" -BroadCapture
```

Enter usual two-ship skirmish,briefly both visible,play normally. One beep arms
detail;after~10s two beeps/console request normal exit. No visual change expected.
Original rendering continues if logging fills/fails;no original ship suppressed.
Strict2GB trace plus32MiB ancillary watchdog,10GB overall including archive copy;
no images or geometry dumps. Actual game byte rate remains unmeasured;the~1.6MB
offline fixtures are NOT predictions of SFC rate. Storage/failure behavior and
exact events/limits/rollback in docs/reconnaissance/broad-capture-contract.md.

After analysis archive_broad_evidence.py <ZIP> <exact-run> compresses transcript
and JSON/log/INI,excludes binaries,checks source-plus-archive allowance,verifies
CRC and records SHA. It does NOT delete raw;any later exact-file cleanup requires
recorded verified archive and no unresolved rollback. No evidence deleted now.
Archives already verified:

- artifacts/remix-runtime/archives/20261017-full-support-broad-offline.zip:
  470,956B,53entries,6,825,424Bsource,SHA256
  176A6C3FEA5E63C1CBA2BCAE2ED3EB7D26C523CBB6C56A1062C2C52B512F8DA2.
  Includes failed/partial iterations,not mislabeled passing evidence.
- artifacts/remix-runtime/archives/20261017-full-support-broad-final.zip:
  246,750B,20entries,3,439,369Bsource,SHA256
  DFE44FACBC10618A6447814F86780A395CE2EE081AFD07C62D5FF36A41D8B7C7.
  Final two fixtures,rollback and legacy check. Small raw originals retained.

## Final files / state / decision

Additional files beyond initial list:qualify_broad_rollback.py,
archive_broad_evidence.py,broad-capture-contract.md,
evidence/20261017-broad-offline-qualification.json. Updated dependency manifest,
probe,HANDOFF and this record. Client/original source assets untouched. Both
clients remainSHA2564D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29;
copied dxgi restoredE35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7.
HEAD e96765a,indexempty;all existing/new work unstaged/untracked,no commit.

**READY FOR SPONSOR RUNTIME TEST.** Public full-support event access and bounded
offline logging are CONFIRMED;actual SFC depth usefulness/gameplay equivalence
remain unproven. Exact next action is launch prepared -BroadCapture session,
then review resulting metadata before any ship suppression/replacement work.

Final allowance refinement:preflight counts ALL existing runtime runs/archives
(387,596,530B measured) plus worst-case new raw/ZIP/ancillary reserve,not just the
new run;disk-free check added. Archiver checks existing output before reserving
ZIP room. Unit test verifies existing output can refuse admission. Qualification
source hashes refreshed for Python runner/helper changes;native fixture revision
unchanged. Exact current qualification copied to versionable evidence JSON.

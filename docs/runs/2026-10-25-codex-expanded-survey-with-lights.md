# Run171 — expanded rendering survey with same-run light metadata

## Authority and result

Sponsor authorizes a broader pull, excluding model/texture contents, with2GiB
maximum and explicitly adds light data. **READY FOR SPONSOR RUNTIME TEST.**
Current work remains SFC-15 characterization; API stays parked. No gameplay,
renderer integration, suppression, image return or milestone claim this run.
This supersedes Run170's next-implementation wording with the broader prepared
survey; its existing atlas findings and the three raw captures are preserved.

## Changes and coverage

- `tools/render_survey/survey_trace.h`: wireversion2;2016MiBraw cap plus32MiB
  ancillary =2GiBtotal.16MiBpreallocated ring,90second tactical/five-minute
  prepared supervision and fail-open loss accounting retained.64-bit byte math
  and record alignment retained; no2GiB allocation or per-callback disk access.
- `survey_extra.h`: existing supported draw/state/resource events already ran
  full-rate without ship-family exclusions. Increase call-origin sampling from
  every64thdraw/max8perPresent to every8th/max64perPresent,32addresses. This is
  a bounded stack-walk cost, not a blanket all-path/all-frame claim.
- New `survey_native_contract.h` and `survey_native.h`: pinned MicrosoftDetours
  hooks for light setter0x006A9AB0,enable0x006A9C40,global gate0x006A9C20 and
  global-effects dispatcher0x004ECFB3. Exact prologues checked. Three methods
  use thiscall, dispatcher cdecl; original stack cleanup verified in disassembly.
  Original arguments/returns/LastError/exceptions retained. Existing geometry
  diagnostic0x006AB410 stays OFF. No original client/asset writes.
- Light setter/enable/gate observations at call rate: shared QPC time base,
  thread/caller/manager/token, all16raw words, enable/global-gate values. Initial
 64slot baseline for each first-seen manager, max8banks. Double-read light
  records rejects inconsistency. Type/units/unknown tail fields are not mapped
  to DirectX or Remix by guess. Float-bit diagnostic values do not establish
  physical semantics for the copied tail fields. Direct writes bypassing these
  setters are not independently observed after the initial baseline.
- Pre-dispatch census walks at most4096global-list nodes, retaining concrete
  vtable/draw target/raw flags/next/object address. Preallocated8192-entry cycle
  table and try-lock; overflow/busy/read errors explicit. This is list membership,
  not proof a visibility test drew it, a lifetime epoch, ship owner, exact weapon
  or coverage of separately attached effects. Does not reuse the fx0-only filter.
- `survey_addon.cpp`: native worker installs/detaches4hooks, drains callbacks,
  checks original12entry bytes and atomically writes `broad.bin.native.json`.
  Hook storage remains process-resident; no hot unload. Worker is independent
  from rendering. Native errors stop evidence collection, not original drawing.
- `survey_capture.py`: backward-compatible v1 parser and version2events35–38;
  streaming light-fragment/type census analysis with bounded summary examples.
  Completed stacks are released instead of overflowing a64Kretained-stack table
  during a broader run. Raw records remain the authority beyond summary samples.
- `game_driver.py`: require native-cleanup receipt before exit cue; warning and
  total-output checks agree with2016+32MiB envelope. `run_survey.py` locks new
  native inputs/pinnedDetours and records explicit capture scope. `qualify.py`
  checks BOTH exact-source fixture controls plus light/type/cleanup coverage.
- New `survey_native_fixture.h`, `tests/native_tests.cpp`; updated
  `survey_fixture.cpp`, `tests/trace_tests.cpp`, `tests/test_capture.py`,
  `build.ps1`, `start_render_family_survey.ps1`, README/probe/map/STATUS/HANDOFF.
  No source/binary/config change to the normal renderer or narrow effect probe.

All native events and downstream graphics metadata share the capture's QPC
clock, but this alone does not prove one-to-one light/effect/D3D11/pixel ownership.
No image, shader, constant-buffer, vertex/index/UV/normal payload reads. No Remix
or Toolkit process. No model/file conversion or texture decoding in the survey.

## Validation

- Strict x86 buildPASS. Native ring/cap/writer tests21checksPASS, including
  actual2016MiBdeclared maximum without producing a huge file, oversized-limit
  rejection, exact cap arithmetic and deliberate saturation/expected drops.
- Native light/census119checksPASS: actual4detours, arguments/returns/LastError,
  initial64slots, invalid-pointer/index observations, originalSEH propagation and
  drained callbacks, cyclic list termination and original flow, exact restoration.
-13parser testsPASS1.051s, including historical bounds/new combined envelope,
  raw light fragments/incomplete data/read faults, type census, malformed records
  and5000completed stacks without accumulating a retained-origin overflow.
-504existing Python testsPASS9.536s. Normal Performance read-only preflightPASS;
  no game/renderer started. Four actual client prologue prefixes match pinned PE.
- Standalone actual-proxy short fixture
  `artifacts/remix-runtime/runs/20261025-050635-693778-return-fixture`:
 10seconds/588frames/21,995records/2,815,488bytes;1,238complete light records,
 64initial slots, two types,147complete stack samples. Zero loss/read faults/
  busy/overflow; resize/recreation/state/childexit0 and4hook-byte restorationPASS.
- Actual-proxy endurance fixture
  `artifacts/remix-runtime/runs/20261025-050717-941853-return-fixture`:
 90seconds/5,341frames/194,291records/24,869,376bytes;10,744complete light
  records,64initial slots,two types,1,335complete stack samples. Same zero-loss/
  state/resize/recreation/normalexit/4hook-restorationPASS. No SFC gameplay claim.
- Qualification `OFFLINE_SURVEY_EVENTS_STATE_CLEANUP_PASS`, exact current
  component SHA256
  `FAF0FC56194F60DD43714C3C90795C7B2B3FDC1EBB74BEAE61E1B871E31AC509`.
  Sponsor launcher's read-only preflightPASS. JSON/path/source/whitespace checks
  passed. No staging/commit/push.

An initial sandbox fixture failed WinError5 before launching its child;
`20261025-050208-312181-return-fixture` retained. Scoped outside-sandbox repeat
passed; no UAC/security-policy change. Earlier short positive
`20261025-050224-182660-return-fixture` is superseded by final source-matched
short/endurance fixtures, not reused to certify newer source.

## Storage admission and recoverable archival

Before expansion:19,001,892,446governed bytes, insufficient for new source plus
archive reservation4,311,744,512bytes under existing20GBaggregate. Added separate
dry-run-default `archive_completed_images.ps1`: selects only completed owned
runs and exact generated DDS paths; rejects reparse/escaped targets/active owned
processes, verifies decompressed and unchanged source SHA256, writes per-run
restore manifest, removes exact loose duplicates only. No recursive broad delete.

Archived85completed runs:4,039,649,856source bytes ->195,901,086ZIPbytes;
**3,843,748,770bytes saved**, all recoverable. Each exact run contains
`survey-admission-images.zip` and `survey-admission-images-archive.json` with
entry hashes and restore instructions. Original game images, source mesh packets,
logs, traces, prior three effects captures, source and settings were NOT removed.
Restore archived generated images before replaying an old GPU input that needs
those paths. Existing stored qualification receipts are not rewritten as new runs.

After new tests:15,213,970,424governed bytes before small final docs;
plus4,311,744,512reservation =19,525,714,936 <20,000,000,000. Admission is
rechecked at each launch. No cap increase to total project storage. Archive is
not automatic during gameplay. Final capture should also be analyzed/archived
under the normal evidence discipline rather than retained as disposable bulk.

## Sponsor workflow and exact next action

From the established elevated PowerShell, launch
`tools/render_survey/start_render_family_survey.ps1`. No new install/UAC/build.
Enter a normal skirmish. Brief quiet view/camera movement is useful, then fight:
weapons, shield hits and destruction if practical. No need to keep both ships in
view or follow exact cue timing. Exit normally at the final two-beep request after
90seconds. Expect unchanged appearance, no extra Remix ship. Afterwards report
what occurred and any gameplay/HUD/control issue. One run, then review coverage.

**Exact next action:** sponsor runs the prepared expanded survey once; then
classify concrete types, light changes and representative graphics families from
the new record before selecting any interface extension. Do not repeat old fx0
capture, claim universal coverage or resume parked API work.

Final state: HEADfd79ce5/indexempty; all prior dirty work preserved, new changes
unstaged/uncommitted, no push. FuelGuard attached existing trusted hook; no helper/
agent/game launched. No active owned fixture/channel/server remains. Current
checkpoint is durable in repository docs, not dependent on chat.
The existing Obsidian tracker was compared against the repository, showing only
our Run170/171 updates; refreshed with a concurrent-edit SHA256 guard and verified
identical afterward. No sponsor-authored tracker edits were overwritten.

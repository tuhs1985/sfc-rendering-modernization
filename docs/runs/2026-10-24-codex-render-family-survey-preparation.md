# Run165 — broader rendering-family characterization; survey ready

## Authority and outcome

Sponsor parks the API experiment and authorizes current-evidence rendering-
interface characterization: sprites/weapons/beams/shields/explosions/damage/
backgrounds/tactical UI, excluding already-characterized bulk ship geometry and
texture payloads. No new renderer support, requirements, backend selection or
replacement implementation authorized or performed.

**READY FOR SPONSOR GAMEPLAY DISCOVERY CAPTURE.** Existing evidence mapped;
separate metadata-only observer implemented and offline-qualified. The actual
SFC-family map remains provisional until representative gameplay is captured.
Do not describe synthetic fixture families as discovered SFC effects.

Fuel Guard attached existing trusted hook. No helper/subagent or SFC/Remix/
Toolkit launch. All existing Run163/164 uncommitted work preserved, including
the isolated API backend and its evidence. Nothing staged, committed or pushed.

## Evidence review and family map

[Current map](../reconnaissance/rendering-family-map.md) consolidates current
semantic proof, original broad runtime metadata and static string/function
anchors. Historical static unknowns about ship/camera identity are superseded;
unknown effect ownership remains genuinely open.

Actual older broad run20261017-182017:141,285records/18,084,608bytes,10.0002s,
zero drops;67,290depth-bound/1,205unbound draws;599frames have exactly two unbound
tail draws. Four depth-path pipeline handles, one63,524draws. No evidence those
counts uniquely identify ships, UI or sprites. Previous observer omitted texture
bindings, static state descriptors and call origins; repeating unchanged would
not answer the new question.

Static anchors preserved with confidence: Q3read0x006770A0, sprite acquisition
0x004D3DD3; shields image references0x0040C37A/0x00426116; sky references
0x0040B6E7/0x004D891A; damage-image cluster0x0042DEF5; explosion trait/settings
references listed in map. These are not recovered rendering-owner symbols or
runtime resource-to-draw proof. Keep CONFIRMED references distinct from STRONG
HYPOTHESIS/SPECULATIVE family interpretation.

## Implemented observation path

Separate `tools/render_survey/` and `artifacts/render-survey/` outputs, not normal
capture/renderer binaries. Read [operating/wire contract](../../tools/render_survey/README.md)
and [probe](../reconnaissance/probes/RENDER-FAMILY-SURVEY-001.md).

- `survey_trace.h`, `survey_events.h`, `survey_extra.h`, `survey_addon.cpp`:
  fixed-ring scalar metadata observer using pinned full-support ReShade public
  callbacks on D3D11. All bool interception callbacks return false. Original
  rendering is never suppressed, rebound or copied by the observer.
- Full-rate enumerated lifecycle/draw/target/state/copy events; descriptor/SRV/
  sampler and buffer identity/stride/range, scalar pipeline creation state,
  scissors, descriptor-table identity and constant-range changes. No shader,
  geometry, texture/image or constant payload reads. Ship draws remain visible
  as metadata; filtering known geometry contents does not filter unknown paths.
- Sample every64th admitted draw, up to8stack walks/Present,32addresses, with
  empty/eligible/captured/skipped and QPC-cost counters. Module ranges collected
  off-callback in bounded JSONL. No callback symbol lookup or stack scanning.
  Native own x86 frame pointers retained. Actual upstream game ownership is not
  fabricated when translation/deferred execution hides the caller.
- `survey_capture.py`: streaming parser with bounded resource/view creation
  epochs, retirement/reuse/reset handling, draw-state families, five-second
  windows, exact sampled-draw origin joins and observed module-range annotation.
  Summary512families/16state examples/4origins per family/512total, hard16MiBJSON;
  truncation explicit, raw retained.65,536resource/view/origin and4,096context/
  family analysis tables; saturation is PARTIAL. No effect labels from counts.
- `game_driver.py`/`fixture_driver.py`: isolated restricted snapshots of verified
  launch/supervision/rollback logic. Observation-only broad mode required. New
  survey qualification replaces inherited legacy-broad source receipt, not the
  normal gameplay renderer qualification. Exact per-run `survey-control.json`
  freezes source/binary/header/proxy hashes and payload exclusion.
- `run_survey.py`, `qualify.py`, `start_render_family_survey.ps1`, `build.ps1`,
  `survey_fixture.cpp`, `survey_fixture_launcher.cpp`, tests and README: bounded
  standalone validation plus explicit sponsor execution. No build at live launch.

Backing: pinned local ReShade6.7.1/API18 event declarations/SDKcommit
8cf85bd12d56697d756d4fcb45e501f5d1b540fa; supported Microsoft
[CaptureStackBackTrace](https://learn.microsoft.com/en-us/windows/win32/debug/capturestackbacktrace).
The public API returns finite available return addresses, not guaranteed game
owners across every optimized translator. No vendor patch/new graphics wrapper.

## Bounds and exclusions

90second tactical observation from existing automatic gate;16MiBring;
256MiBtrace/warn128MiB;4MiBmodule-sidecar;32MiBancillary envelope;
20GBaggregate with source+archive reservation. Existing285second prepared and
300second game-launcher limits retained. Gate-only observer selection wait
bounded120seconds, then existing hook restoration/unload. Diagnostic geometry
hook, mesh/texture exporters, semantic payload receiver, Remix and Toolkit OFF.
No continuous screenshots or asset copies; observation does not need OBJ/USD.

No indirect-draw transcript, shader interpretation, constant values, full deferred
command replay, sampler-retirement reconstruction, descriptor-table resolution,
resource filenames or OS cursor composition. Those are explicit coverage gaps.
No semantic owner is guessed from a native pointer, texture or same-thread time.

Original accepted client/install assets, normal D3D9/Remix source/settings/pins,
launchers and qualification receipts are unchanged. The copied game's proxy is
backed up/restored by existing verified transaction only during the actual test;
no game installation was touched during this preparation. Safe stop means normal
exit before proxy replacement; no hot unload/storage free or routine UAC.

## Offline validation and corrected test scaffolding

- Strict x86 `/W4 /WX /O2`, observer/fixture `/Oy-`, deterministic link builds PASS.
- Native ring14checks PASS: schema, overflow-safe bounds, byte-cap/drain and
  writer failure; intentional cap-test drops are not real-capture drops.
- Existing504Python tests PASS7.935s; eight new parser tests PASS0.024s:
  unknown classification, view/resource reuse, command reset, retired view cannot
  self-rebind, drop/cap partial, exact origin/module join with owner unresolved,
  constant-range/no-payload and invalid schema/sequence. Process-local workspace
  TEMP used, no security-policy change.
- First short fixture011400-074254 preserved: graphics/state/resize/exit passed,
  but all19stack walks empty. `/Oy-` correction recovered19/19 in011529-880486.
- First90second attempt011711-515332 hit inherited native25second fixture loop;
  next011856-190739 hit inherited fixture-launcher60second wait. Both retained as
  failed/partial tests, not SFC failures. Owned fixture jobs closed. Separate
  fixture and fixture-only launcher now bounded100seconds; normal game launcher
  and game timers NOT changed. New fixture launcher rejects `--game`.
- The copied game driver's first read-only preflight correctly refused stale
  legacy-broad collector source receipt. Replaced only its isolated admission
  with its own actual-proxy exact-source qualification. Normal receipts untouched.

Final actual-proxy qualification:

| UTC directory suffix | Duration | Records / raw bytes | Origin samples | Result |
| --- | ---: | ---: | ---: | --- |
| 20261025-012827-509941-return-fixture |10s|15,829 /2,026,240|19captured/0empty|PASS |
| 20261025-012115-831179-return-fixture |90s|139,531 /17,860,096|167captured/0empty|PASS |

Both zero capture drops/analysis overflow, nine synthetic graphics families,
resource/view/descriptor/pipeline-state events, actual application stack recovery,
graphics state preserved, resize/recreation and normal host/fixture exits0.
90s rawSHA A17E66BF32A92F79D8AE7088F0FCFDAAD79DDE6E8E2CE011628B318606CD43C5;
short214CC8B4B80C215F2265EF2CAD3071437D343675418883B62310C4897F1BDF82.
90s stack-walk accumulator987ticks at10MHz (~0.099ms total); not a measurement
of total observer overhead or a prediction of SFC performance.

ObserverSHA71538710B8CEA0586A5DBB42CA43F076ED487CE8D7875A23798211846C7522B4;
isolated fixture495A0A89284EA284B22C1561A562A048CC02EA7BCED7E146C9349D48B538E69D;
fixture launcher6C3D90CC59130B4D87B679C9D78B15802E1D753F9AFBCCEE565ABE1353B3EE25.
Current qualification in `artifacts/render-survey/qualification.json` binds exact
source/binaries/headers and both fixtures. Raw/intermediate evidence preserved.

Survey read-only preflight PASS; normal multi-ship Performance read-only preflight
PASS. No game/renderer started by those checks. No owned fixture/observer host
remains. Governed evidence including isolated API/survey builds ~18.395GB before
small final documentation;20GBcap unchanged. No archive/delete needed here.

## Files, tracker and next action

Added family map/probe/this run/curated evidence and `tools/render_survey/` files
listed above. Updated `docs/STATUS.md`: SFC-01API PARKED with exact restart action,
SFC-15survey current; future long survey remains distinct. Updated historical
survey need with current90second scope/20GBcap and authoritative HANDOFF. Obsidian
snapshot refreshed separately while preserving unrelated user text. No source
evidence overwritten; no normal rendering implementation changed.

HEADfd79ce5/indexempty/priorRun163–164workpreserved/allunstaged/uncommitted/no push.
There is no live mapping/tool session to resume. Build lock becomes stale after
any survey code or dependency change; do not bypass qualification at launch.

**Exact next action:** sponsor runs `tools/render_survey/start_render_family_survey.ps1`
from the established elevated parent. Quiet initial view, then camera motion,
then ordinary combat/shield impacts/explosion where practical; exit at final
request. Analyze actual resource/state/origin changes and update family map
before recommending/implementing any rendering support extension. No manual
timestamps, RE, appearance tuning or API-resumption work requested.

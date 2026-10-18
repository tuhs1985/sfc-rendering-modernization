# Codex run — restore the agreed beside-original ship display

Run SFC-RETURN-20261018-27;2026-10-18 America/New_York.
Authority:sponsor rejects upper-corner inset,confirms intended offset beside
original ship,and says "Go". **READY FOR SPONSOR OFFSET-COPY RUNTIME TEST.**
Run26 inset was an analyst scope error,not the agreed visual placement. It is
superseded,not deleted. No actual inset game test supplied or launched here.

## Starting state / technical question

HEAD e96765a1a34c15212ed22f11edeb9a708b9fc18d;97 starting porcelain entries,
indexempty;prior work preserved. Read HANDOFF/current contract/probe,Run26,
receiver/addon/current-key/offset producer and actual pixel fixture. Approved
return-path scope unchanged;no new CDD,architecture,lighting or suppression work.
FuelGuard attached actual thread via hook;no daemon/helper/subagents.

Question:can genuine freshly rendered offset ship pixels be displayed at the
same native camera projection/scale as SFC,instead of fitted into an inset?

## Correction and supported behavior

- `tools/remix_runtime/ship_live_request.h`:pure validated displayRect maps the
  complete SDK image to its captured native viewport. It does NOT fit to the
  whole window or add another pixel displacement. Reject unsupported/nonfinite/
  out-of-display rectangles;native payload/ABI unchanged.
- `ship_live_receiver.h`:late display rechecks exact current source key as
  before and returns native viewport rectangle with the SRV.
- `return_addon.cpp`:late AddImage spans that rectangle,not a corner. Existing
  private output alpha0 background/picking-qualified alpha1 ship retained. ReShade
  late image stage/state preservation unchanged;no direct pre-Present buffer draw.
- `run_return_game.py`:same -VisibleShip mode now explicitly describes world-
  offset copy in original camera view;manifest/console no longer promise inset.
- `ship_live_gpu_fixture.cpp`:visible callback fixture uses1920×1080 matching
  recorded native view and saves ONE bounded2,073,600B binary changed-pixel mask.
  This is offline-only readback,not a game screenshot loop.
- `qualify_live_return.py`:compares actual displayed pixels against independent
  native geometry/camera projection with diagnostic WORLD translation,then native
  viewport placement and bilinear alpha sampling. IoU>=0.95 required.
- `live_return.py`:requires visible_camera_qualified AND matching source/binaries;
  obsolete inset qualification cannot authorize this test.
- `tests/ship_live_request_tests.cpp` and `tests/test_live_return.py`:native full
  and nonzero viewport/bounds checks,plus independent mask placement regressions.

The existing producer already applies a documented fixed WORLD translation
chosen along initial camera-right toward the roomier side,nominal20% viewport at
initial owner depth. This remains unchanged. Copy retains original pose/model
scale/current camera;as camera rotates,the offset projects naturally rather than
staying a fixed distance left in screen pixels. No double translation,no geometry
rotation/UV/normal edits. Model may be whichever qualified owner,not necessarily
enemy. Fixed magenta diagnostic material/light,not recovered appearance.

Source view in the fixture is **x200,y30,w1720,h1020**,not whole1920×1080window.
Copy is displayed in that native rectangle;this avoids shifting/scaling camera
results into window margins. Low256² source output upscaled to native viewport
can look coarse. Do not tune appearance during this correction.

## Offline findings / rejected hypotheses

Two failed fixtures163207 and163325 preserved. Both native callbacks/exits passed
and showed14238magenta pixels,but initial analysis incorrectly compared them
to a whole-window projection (IoU0.102),then a nearest-sampled viewport projection
(IoU0.829). Their actual centroid[818.56,714.86] was near correct camera projection;
differences were oracle viewport/filter assumptions,not permission to move mesh.
Explicit bilinear alpha sampling predicts interpolation-edge coverage;IoU0.994603
on retained pixels,then reproduced with fresh final fixture. Threshold strengthened
from prior inset0.85 to0.95,not lowered to force PASS. No pixel/image displacement
was introduced to improve the score.

**CONFIRMED offline:**actual SDK/native/proxy displayed geometry agrees with
native viewport+world-offset projection;no corner placement. **Unproven:**actual
SFC sponsor sighting,smooth frame rate,all HUD/scene overlap and moving-pose pixel
fidelity. Run26's947outputs/20strict matches remain baseline;no frame/pose
relaxation or stale-image hold. Original ships remain ON. This is an additive
camera-aligned diagnostic copy,NOT suppression,replacement or scene-depth
composition. Its pixels can overlap retained scene content;depth ordering versus
effects/other objects/HUD annotations is not qualified. Sponsor should keep both
ships near the central scene initially and report any obstruction/control issue.

## Tools / commands / validation

Pinned Remix1.5.2/SDK0.6.4,VS2026Community18.7.3 C++20 /W4 /WX,
PS7.6.5,Python3.12.14,NRC/DLSS/RR process-local OFF unchanged.
Scoped approved isolated build/GPU execution;no routine sponsor UAC/security change.

- PS7 `-NoProfile -File tools/remix_runtime/build_live_return.ps1`:PASS,
  **69native checks eachx86/x64**;wire496B/Key152B/Command592B unchanged.
- TEMP/TMP=artifacts/test-temp;Python `-m unittest discover -s tests -p test_*.py`:
  **199PASS/4.355s**. Parser/JSON/references and git diff --check PASS.
- Python `qualify_live_return.py --execute --addon --visible`,then separate
  --execute/direct,--addon,--slow,--disconnect. All final five gates PASS:

| UTC run suffix (-live-private) | Gate | Seconds | Attempts | Mask IoU |
|---|---|---:|---:|---:|
|20261018-163501-123418|camera-aligned visible callback|10.829|108|0.994603|
|20261018-163512-325797|private direct|7.921|66|1.0|
|20261018-163520-613185|private callback|8.610|66|not read back|
|20261018-163529-593175|slow/no overwrite|9.281|64|1.0|
|20261018-163539-222260|terminated producer|7.547|2|1.0|

All fixture exits0/private failures0;host0 except intentionally terminated host1.
State/topology,retirement and disabled-admission tests pass. Recorded fixture pose,
not actual new gameplay. Pixel comparison excludes top96rows solely for observed
ReShade startup banner as Run26;all remaining frame background compared to
predicted masked ship. No scene-occlusion or UI-completeness claim.

`qualify_live_return.py --qualify` with four private directories then visible
directory regenerated qualification,SHA256
`3DDACA7B1C6E76203E1F001DA244B8C743B3F336C3E6C842C69924B4A7A89535`.
`run_return_game.py --visible-ship` WITHOUT --execute:read-only preflight PASS.
Repeated isolated build preserves source/binary qualification (verified before
handoff);no game/renderer launch by preflight.

AddonSHA `F534CC2BA47D6EB02E2A281CEA30DC1BFD54B1AFAA4DA442FB00750C963A62EE`;
fixtureSHA `EB90E0E85F015BF58B3F3E53E1BD12A3CB5955657B275772199AA5132DE274AB`;
hostSHA unchanged `D2DDFDEA5DFB5AC02D673C3DFCEF54EB5E60DBA682F81E432CFFA4183207CE1F`.
Accepted semantic binary and normal return-bin untouched. Both installations'
seven critical hashes rechecked unchanged;client
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
SDK40 common-object warning persists;normal exit does not resolve it.

## Output bounds / preservation / final state

Unchanged90s tactical/285s prepared workflow;32MiB logs,16MiB warning;one in-flight
triplet,4output surfaces≈1MiB;no game readback/images/continuous geometry logs.
Offline60s/32MiB per attempt. Seven attempts total41857545B;largest8.84MB.
All seven including failed analysis archived to
`artifacts/remix-runtime/archives/20261018-world-offset-display-preparation.zip`,
11610680B,SHA256 `3B477B55E2F33C60AD31B17D3839CEF3625F26D72910F83E2920619032E6E652`.
CRCverified,raw retained. No cleanup deletion or reference-original changes.

Updated authoritative HANDOFF,probe,contract/readiness;added this run/curated
evidence. Exact implementation/test files listed above. Old inset docs preserved
as superseded history. All changes unstaged/untracked;indexempty,no commit.
No SFC launched this run. No owned game/host/fixture/controller remains;no
transient session required. No milestone claim or additional architecture scope.

**Exact next action:**sponsor runs existing -VisibleShip command,usual two-ship
skirmish,holds starting camera briefly and looks BESIDE ships for intermittent
magenta copy;follows movement cues/exits at two beeps. Review actual position/
size/normal gameplay and fresh visible submissions before any suppression work.

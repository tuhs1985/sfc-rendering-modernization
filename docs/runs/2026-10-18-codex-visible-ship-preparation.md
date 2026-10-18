# Codex run — private retest review and first visible ship inset

Run SFC-RETURN-20261018-26;2026-10-18 America/New_York.
Authority:user supplied completed private test,then directed "get it good enough
and lets add the ship in". **READY FOR SPONSOR VISIBLE-SHIP RUNTIME TEST.**
Not owner suppression,replacement,full-scene integration or milestone PASS.

## Baseline and private runtime adjudication

HEAD e96765a1a34c15212ed22f11edeb9a708b9fc18d;95 starting porcelain entries,
index empty,large prior work preserved. Read authoritative HANDOFF/Run25 and
existing probe/receiver/addon/compositor/runner/fixtures;approved plan disposition
unchanged. FuelGuard attached exact thread via hook;no helper/subagents.

Reviewed `artifacts/remix-runtime/runs/20261018-145137-528549-in-game`:
manifest,result,host/controller logs,semantic summary/worker. Sponsor reports
extra movement and Alt-Tab to inspect console;no specific gameplay fault reported.
Do not infer exact focus timestamps or a separately confirmed full HUD checklist.

**CONFIRMED direct runtime:**90s tactical/157.64s runner;fresh FCA owner2/revision2,
no saved template,host D2DDFDEA...07CE1F as qualified.947 outputs/20 private
admissions/926 late-or-mismatch rejections/0 private invalid/0 private failures/
0 cancellations. First ON interval627published/7admissions;OFF counters held;
second ON resumed to947published/20admissions by60s;planned producer stop60–90s.
Earlier10s stall NOT reproduced. publication_busy=0:actual lock contention was
not observed,so this run does not independently prove the original stall cause.
Final READY947/ACK946 is an unconsumed output at intentional shutdown,not a
Rendering stall or outstanding Reading lease. All game renderer/controller exits0;
hook bytes restored,component removed/unloaded. Source5516frames;geometry hook OFF.
Worker3711records/2427973bytes,2transfers,0drops/failures/saturation. Separate
semantic2588rejections in two buckets (1294each,2524examples omitted) and known
00509843 count5520 remain separate from private invalid0;not blamed on Alt-Tab.
No observed presentation-resource clear during sampled run (clearCount0,width1920).
Alt-Tab timing/cause of mismatches NOT identifiable from current counters.

First100 detailed request/GPU-completion samples:min1.9457ms,median4.0624ms,
max139.1875ms,QPC10MHz;not end-to-end or all947 latency. Only20/947 (~2.1%)
admitted,so smooth replacement is NOT proven. This is enough for an opt-in,
intermittent ADDITIVE image demonstration with originals retained,not suppression.
SDK warning40 persists. No native light snapshot/lighting interpretation added.

Both installs' seven critical hashes independently rechecked unchanged;launcher
settings unchanged. ClientSHA256
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
No game/host/controller left or transient component files in test root.
Runtime7143603B compressed to `artifacts/remix-runtime/archives/20261018-private-retry-runtime.zip`,
1507640B,SHA256 `C8CD683BDAC3B858381A041AAD7BAAA793C7A8C0178E9F0BA5576F8A3851991D`.
Raw retained;CRCverified. Immutable result pending-sponsor field is superseded
by this run record,not rewritten.

## Bounded visible implementation

Selected smallest supported intervention:reuse the already demonstrated late
ReShade image-return stage and upper-right256square diagnostic area. Genuine
fresh SDK ship color is masked using exact picking/native-Z into a private RGBA
target with transparent background. Default-off -VisibleShip shows that target
inside SFC (not a desktop overlay). Original ship/HUD drawing remains ON;this is
an inset,NOT the world-aligned/offset replacement. World-offset SDK input remains
explicit as in Run23;image appearance is diagnostic magenta,not original textures.

- `tools/remix_runtime/ship_live_receiver.h`:private target gains SRV;stores last
  admitted key/time and exposes currentDisplay only with same current owner/frame/
  epoch/revision/pose/camera,active producer/enabled/freshness. No stale-pose reuse,
  cross-owner cache or frame-equivalence relaxation. Resource preparation at init;
  no render callback waits/files/readback/shader compilation.
- `return_addon.cpp`:opt-in environment flag;late overlay AddImage in exact same
  rectangle as triangle proof:(width-272,96)..(width-16,352),800–1920wide and
  600–1080high only. Outside/missing output omitted;transparent background. ReShade
  handles draw state as in accepted triangle path;underlying private compositor
  retains ExecuteCommandList(TRUE). No original ship suppression/depth composite.
- `run_return_game.py`/`start_return_image_session.ps1`:mutually exclusive
  --visible-ship/-VisibleShip route through unchanged semantic/current-frame
  producer and auto gate. PS5 forwards correctly toPS7;routine elevated parent
  unchanged. Manifest records visible purpose;game result distinguishes submitted
  visible work from missing visible submissions. No fabricated sponsor PASS.
- `live_return.py`/`qualify_live_return.py`:visible mode requires extra current
  source/binary-matched callback PIXEL qualification;four private gates retained.
- `ship_live_gpu_fixture.cpp`:offline-only backbuffer staging verifies actual
  magenta ship pixels and background,state/lifecycle. Not used in game.
- `tests/test_live_return.py`:mixed-mode rejection and missing visible gate tests.

## Offline failures retained / resolved

Four failed fixtures150051,150155,150300,150359 are preserved,not hidden.
Initial direct pre-Present game-buffer draw was overwritten by presentation
processing (draw counter advanced but0magenta pixels observed). Abandoned that
approach in favor of proven late image-return stage;no translator/SDK patch.
Background comparison also flagged56940pixels confined to rows8..80,consistent
with ReShade's own startup banner.5s warmup alone did not remove it. Final fixture
explicitly excludes top96rows from BACKGROUND assertion (inset starts96),checks
all remaining outside-inset pixels and documents this limit. This is not a claim
the banner itself was verified unchanged. Native compositor/state tests and fixed
viewport support isolation;actual SFC HUD/control observation remains required.

## Final validation, exact tools and reproducibility

Same VS2026Community18.7.3,C++20 /W4 /WX,PS7.6.5,Python3.12.14,
pinned Remix1.5.2/SDK0.6.4/process-local NRC/DLSS/RR OFF. No proxy swap.
`PS7 -NoProfile -File tools/remix_runtime/build_live_return.ps1`:PASS,
62native checks eachx86/x64. Scoped approved GPU/build execution required by
sandbox;no sponsor UAC/security changes. Python with TEMP/TMP=artifacts/test-temp:
`-m unittest discover -s tests -p test_*.py`:197PASS/4.362s. Runner PS parse PASS.

Bundled Python `qualify_live_return.py --execute --addon --visible` plus four
separate --execute modes(direct,--addon,--slow,--disconnect) passed:

| UTC run suffix (-live-private) | Gate | Seconds | Private attempts |
|---|---|---:|---:|
|20261018-150547-475320|visible callback/pixels|10.734|108|
|20261018-150620-179453|direct|7.766|65|
|20261018-150628-309859|private callback|8.641|64|
|20261018-150637-308423|slow/no overwrite|9.187|64|
|20261018-150646-862989|terminated producer|7.484|2|

Visible512magenta pixels,outside_changed0 below96,topology preserved;
retired/disabled admissions stop;private failures0. Direct/slow/disconnect mask
IoU1.0. Fixture exits0;host0 except deliberately terminated disconnect host1.
These use recorded fixture geometry and held source frames,not actual SFC motion
or visibility/occlusion proof. Native SDK40 warning remains unresolved.

`qualify_live_return.py --qualify` with four private directories then visible
directory above generated current five-gate qualification:
SHA256 `9F3D9DDAA5EE4A9FE91E540BAA4053F904E77738C2E40B0C89061FAE6AD81E11`.
`run_return_game.py --visible-ship` without --execute:read-only preflight PASS.
New addonSHA `5D491FF530ABDDC59C08D855D2C1FFCB07FA1423380349CB77D1F7140349E115`;
fixtureSHA `1118315DE3E15214E07338F96F08D2B58ECBE86C4FB8E6EF982E05E80C135EFA`;
host unchanged fromRun25. Repeated build/readonly preflight checks pins before
sponsor run;never bypass stale qualification. Normal return-bin/observer untouched.

All9offline attempts48916350B archived including failures to
`artifacts/remix-runtime/archives/20261018-visible-ship-preparation.zip`,
16705148B,SHA256 `CDACB0697BDB9503A63E09335751C84D072F1F7CDD836CCEFCAD601CA5C9CF8A`.
CRCverified,raw retained;32MiB/60s each,16MiB warning,no uncontrolled dumps.
Actual90s/285s,32MiB log cap and1MiB four output surfaces unchanged. Only offline
fixtures use bounded readback;no continuous screenshots in game.

## Handoff / repository

Updated HANDOFF/readiness/contract/probe,added this record and curated evidence.
All implementation changes above unstaged/untracked;indexempty,no commit;
existing dirty work preserved. No actual SFC launch during implementation.
Both installs' seven critical hashes unchanged after offline tests. No owned
test/game/host/controller left running. No transient session required to resume.

**Exact next action:**sponsor uses prepared -VisibleShip command in the probe,
enters familiar two-ship skirmish;looks for intermittent magenta ship copy at
upper right,plays per cues and exits at two beeps. Review actual drawCount,
provenance/cleanup/hashes and sponsor visibility;no more private-only rerun first.

# Run44 — live light tuning launcher

Date: 2026-10-18 America/New_York (artifact UTC folders may say October19).
Active task: additive Remix lighting controls, not ship replacement/TRL completion.
Starting HEAD2fa8032; existing Run40–43 work unstaged/untracked, index empty.

## Starting evidence and question

Sponsor reports first wiring works, directions aligned, strength and shadows need
tuning. Sponsor wants softer shadows and a low-recording session ending on normal
game exit. `angular_diameter_degrees` controls apparent source size/shadow softness;
not brightness. No config value is changed for sponsor without a request.

Actual `artifacts/remix-runtime/runs/20261019-002556-575382-in-game`:
SDK receipts slot0=.75 RGB, slot1=.125 RGB, revision1; observer544 captured/written,
no drops/rejections/queued/IO failure; host1151produced/1150drawn/failed0,
API shutdown0; controller removed/restored/unloaded true. Sponsor direction match
is CONFIRMED by observation; physical intensity calibration remains unresolved.
Final report PARTIAL due `UnboundLocalError` calling `analyze` instead of imported
`analyze_lights`. Corrected call; original partial result preserved, not rewritten.
Launcher log lacks a retained CHILD_EXIT line: do not fabricate full normal-exit
verification for this historical run. Existing SDK warning40 persists.

## Implementation / reproduction

Explicit `start_light_tuning_session.ps1` -> existing PS5-to-PS7 launcher,
`run_return_game.py --light-tuning`. No automatic UAC; elevated parent required.
Normal wiring workflow remains90seconds. Tuning mode uses30minute tactical ceiling,
33minute runner/host ceiling including startup; start-up must still fit existing
readiness/gate timeouts. Exit normally whenever done; at ceiling controlled removal
and an exit cue apply. No game launch performed by Codex.

Native dedicated observer only: fixed8record queue,5Hz/two owner epochs,18000record
attempt ceiling. Worker atomically replaces one6156B latest snapshot per owner;
no per-frame append trace. Shared latest scene state keeps publishing up to30Hz;
only100 detailed scene rows per owner are retained. Python presentation history5s,
config polling2Hz; first16config revisions retained and last-good config overwritten.
Duplicate latest snapshots never refresh observation time. Existing500ms light
freshness/100ms image request limits and original-renderer fail-open remain.
Config/light file operations stay outside rendering callbacks.

At normal game exit Windows reclaims the target process; controller8 is accepted
ONLY for tuning after observed process exit. This is explicitly NOT a live-hook
restoration or DLL-unload proof. Timed removal retains existing restoration checks.
No live worker/storage unload is attempted on a dying process. Source/launcher
hash checks still run; renderer stop/cleanup still checked. No security weakening.

Files changed this run: native_light_observer.h, m1_live_scene.h,
ship_live_host.cpp, live_lights.py, run_return_game.py, start_return_image_session.ps1,
live_return.py, light_discovery.py, return_launcher.cpp; native_light_observer_tests.cpp,
m1_live_scene_tests.cpp, test_live_light_wiring.py. Added tuning launcher, probe,
this record, build_tuning_launcher.ps1; configREADME/HANDOFF updated. Existing
active lights.toml retained. Scoped launcher build changes only the explicit
tuning child wait to33minutes; fixture60s/default game300s stay unchanged. Launcher
source/build script included in qualification pins. No detached launch workaround.

## Validation and evidence

Tools: VS2026 Community18.7.3/C++20/W4/WX/Brepro x86/x64, Python3.12.14,
bundled PS7; same pinned Remix1.5.2/SDK0.6.4. No dependency changes.
Commands: build_light_discovery.ps1; build_live_return.ps1;
`python -m unittest discover -s tests -p test_*.py`; standalone
qualify_live_return.py fixtures and source-matched receipt; read-only
`run_return_game.py --light-tuning`; PowerShell parser and git diff --check.
Initial sandbox build denied shared mapping and import-library overwrite; scoped
unsandboxed rebuild used, not a product-code defect or global ACL change.

Python243PASS; native core9/observer13 each architecture, includes beyond90s and
30minute/sample limits. New actual worker latest-only test verifies two6156B
files and an observation after100000ms. Duplicate snapshot freshness regression
PASS. Native request89/UV14/lightwire19 checks per architecture PASS.
First GPU batch preserved but superseded after console-only source edits and a
transient Windows PermissionError replacing live-lights.bin while SDK reader held
it open. Relay now counts busy replacements and retries next poll without waiting
or refreshing native observation time; dedicated regression PASS. Private fixture
config now deterministic rather than inheriting sponsor tuning values. Sponsor's
master.25/angular1degree settings retained untouched. Final GPU/preflight results
recorded below after completion.
Additional passing GPU batches were deliberately not accepted as qualification
after final early-error initialization/launcher timeout edits changed source pins.
Source mismatch guard correctly rejected mixed snapshots; no receipts forged or
historical manifests rewritten. Final source frozen before last complete batch.

Final nine GPU gates PASS, from20261019-004651-905522 through
20261019-004848-398796-live-private; exact folders in live-return qualification.
Light hot-reload fixture PASS22.390s, actual SDK .75/.125 then .375/.0625.
Qualification SHA256 FB04FF38C322B000DF7905E280E6D2EFC9FEC333C07A8EBA0F391DFCAF1A440F.
Host SHA256 D6EAEE3F663487DD8B8505277A9EEF3DC954DCC64D98D9D272092ACF02E130D1.
Read-only --light-tuning preflight PASS; no game/renderer launched. Parser and
git diff --check PASS. Archive36,238,608B, CRCverified, raw retained:
artifacts/remix-runtime/archives/20261018-light-tuning-qualified.zip,
SHA256336040403493310F7B1CAF31D4F5675F48BA7310DEAF86B488A44DB2B7C3D9FD.
Total retained evidence5,440,444,583B below10GB. No deletion or stage/commit.

Both client SHA256 unchanged:
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
No new sponsor runtime yet; long gameplay/normal-exit branch remains runtime
validation pending. No claim of general weapon-light mapping, GI recovery,
universal brightness calibration, or controllable per-light RT shadow switch.

## Bounds / final state

32MiB combined non-image evidence warning16MiB,128MiB images warning64MiB,
existing10GB overall retained. Latest light files remain constant size rather than
multi-GB traces. Existing archives/raw preserved; no cleanup/deletion necessary.
No staging/commit. Prior unrelated/baseline work preserved. No active process is
required to resume. Exact next action: sponsor starts tuning launcher, edits and
saves config, exits SFC normally, then Codex reviews result/cleanup.

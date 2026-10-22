# Run100 — ship-local offscreen-position probe prepared

2026-10-21 America/New_York. Sponsor go authorizes next targeted run after
Run99:resolve observation/lifetime coupling,not another speed-only test.
Read authoritative HANDOFF and operating convention,Run99evidence,approved
amended M1/additive scope,existing LIVE-BRIDGE-001and camera map,Run98code and
current runner/worker/qualification contracts. Existing technical gate allocation
unchanged,no formal TRL claim. Fuel Guard attached via trusted recent-hook
receipt,no sandbox daemon. HEADd29111f7a513c4510c4d33aeeda2c355d98443a5,index
empty,large prior dirty work preserved. No helper/agents,stage,commit or push.

## Engineering decision / exact narrow evidence

Prior render observer changes epochs on brief absence;Run99same-address return
and enemy displacement strongly support offscreen simulation. Missing fact is
fresh ship-local position DURING render-observation absence. Do not implement
persistent renderer identity or simply bypass retirement without that evidence.

Inspected only existing exact disassembly00419DD2..00419E47and00413B34..00413BBE.
00419E1C/26/30use x87FLOAT32loads from ship+EE/+EA/+E6;00419E3Cpasses values to
0069C940. Twelve exact supported-PE prefixes corroborated,including+9C4cache,
angle/additional matrix reads and base translation loads. No broad engine RE,
new hook/ABI judgment,live function call or executable modification. Static
source relationship CONFIRMED;offscreen behavior still runtime question.

Chosen smallest reversible mechanism:default-off external read-only sampler
using normal already elevated parent and path-verified game PID. It retains
OSprocess handle with query-limited+VM_READ only. Fresh validated captured
packets seed two native ship addresses;checks vtables and visual link before/
after double-reading known fields. Reads original position inputs,base/cache/
raw rotation comparison and existing native cache counter. No game thread calls,
suspension,writes,renderer inputs or shared manager polling. Client has already
validated its assets;probe doesn't load images or recreate them.

Memory-reading API is safe against unmapped memory without dereferencing inside
SFC;this does NOT prove engine allocation lifetime. Observed identity/read failure
quarantines diagnostic track. Same-vtable ABA between samples remains possible;
no sample is sent to renderer. Cached matrix existence isn't freshness. Three
changing external positions within source-QPC-confirmed render gap demonstrate
that observation only—not native death/removal or continuous render submission.

## Files created/modified

Created:

- `tools/remix_runtime/offscreen_position.py`:bounded read-only process reader,
  seed validation,sampler,cleanup,QPC/source lifecycle analyzer and cue phases.
- `tools/remix_runtime/qualify_offscreen_position.py`:source-locked receipt,
  exact original-PE checks,owned synthetic external-process test with30s bound.
- `tools/d3d9_proof/start_d3d9_offscreen_position_session.ps1`:dedicated launcher,
  PS5-compatible CheckOnly and existing elevated-parent workflow.
- `tests/offscreen_position_child.py`:owned synthetic low-address memory fixture,
  no SFC import/launch;writes only its OWN memory.
- `tests/test_offscreen_position.py`:12reader/worker/analyzer/cue tests.
- [Probe](../reconnaissance/probes/OFFSCREEN-POSITION-001.md),this record,
  [curated preparation evidence](../reconnaissance/evidence/20261021-offscreen-position-prepared.json).

Modified:`tools/remix_runtime/run_return_game.py`,`start_return_image_session.ps1`
for default-off flag,source qualification,90sphases,sampler start/stop/result;
`docs/HANDOFF.md`. Native capture/D3D9host/shaders/quality/material/light settings
UNCHANGED. No requirements changes. Older camera-return launcher retained.

## Bounds and validation

External<=20Hz/ship,two ships,120smaxfrom tactical gate,2700rows/ship,8MiBdetail,
existing8asset revisions. No catch-up bursts. Existing90sformal/five-minute
workflow/120ssemantic watchdog/32MiBcombined evidence/128MiBimage budget/20GB
aggregate preserved. Thread joins and process handle closes before restoration;
failure cleanup also stops reader,no unmapping dependency. Original drawing ON,
high-volume geometry hook OFF. No new default-on observer.

Repro from root using configured bundled Python and PowerShell runtimes:

```powershell
python -m unittest discover -s tests -p 'test_*.py'
python tools/remix_runtime/qualify_offscreen_position.py
python tools/remix_runtime/light_discovery.py
python tools/remix_runtime/qualify_lifecycle_capture.py
python tools/remix_runtime/run_return_fixture.py --d3d9-additive --rebind-owner
python -c "import sys;sys.path.insert(0,'tools/remix_runtime');import additive_qualification as a;a.qualify('artifacts/remix-runtime/runs/20261021-115840-152608-return-fixture')"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/d3d9_proof/start_d3d9_offscreen_position_session.ps1 -CheckOnly
git diff --check
```

Actual Python path
`C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`;
pwsh under same dependency root `native\powershell\pwsh.exe`. Qualification runs
with approved ordinary host access for test-child Temp/process access;no sponsor
UAC/security-policy changes. No dependency installation or new native build.

-410Python regressions PASS,including12new external-reader/analyzer tests.
  Actual ReadProcessMemory across processes sees motion with unchanged cache;
  races/NaN/wrong path/identity rejected;handle closes after worker join;byte cap
  stops collection without stopping synthetic target. Synthetic source/session
  join demonstrates interior gap analysis,constant data remainsPARTIAL.
-12original-PE source anchors PASS with supported unchanged client hash.
- Replayed discovery against existing Run97packets only (no live process reads):
  identifies distinct KFF/FCA native ships,3/2fresh observer labels respectively,
  neither quarantined. Not a new game result.
- Existing actual native normal/tuning/shared-light worker and lifecycle queue/
  cleanup qualifications rerun PASS;native binaries unchanged.
- Actual ordinary-D3D9/Remix/proxy standalone replay115840-152608:595/600fixed
  delivery frames,152697changed pixels,ACK3/reject0,782inputs invalid0/
  unqualified0,normal owned exit,state/resize/recreation PASS. Overall draw596,
  stale2andgpu_busy596retained,not zero-loss claim. Admission expired0. Synthetic
  light replay remains explicit,not actual game light proof. Vendor40warning
  remains unresolved. This is regression coverage,not offscreen SFC evidence.
- PS5parser of both changed/new scripts PASS;CheckOnly PASS starts no game.
  Source receipts refreshed and lock current code. Diff check PASS.

Standalone generated fixture copies199files/82,188,024bytes recoverably archived
to `artifacts/remix-runtime/archives/20261021-115840-152608-return-fixture-binaries.zip`,
6,861,804bytes,SHA256953154EFF9EB9522ED94EA4B1B7A78A4B9751B37ADF3484F49BBB1CD49EA93CC.
Exact targets/hash/decompressed hash verified before removal;raw logs/packets
retained. No earlier partial game evidence removed. Aggregate artifacts
11,951,058,098bytes<20GBallowance.

## Prepared runtime / final state

READY FOR SPONSOR RUNTIME TEST,not a flicker/lifetime fix or formal gate PASS.
Use existing Federation FCA/different enemy fixture,keep both alive. At timed
15ssingle beep accelerate OWN ship and leave it moving;two HIGH25sswitch to
enemy camera leaving own ship out of view;three HIGH40sreturn;single50sgently
turn;two HIGH60slook away;three HIGH75sreturn;single80shold. Exit only on two
LOWbeeps after restoration. No timestamps/RE/admin dialogs. New probe is invisible;
existing textured extra copy stays on its prior behavior. Report own movement
while offscreen and game/control behavior. Don't judge by extra copy alone.

Both original/test client hashes remain
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
No active game/owned renderer/receiver/fixture after validation. No actual SFC
runtime collected. HEAD unchanged,index empty,all prior/new edits unstaged and
uncommitted. Local receipts/ignored raw evidence may not survive another checkout;
versionable probe,run record and handoff provide reproducible state.

Exact next action:sponsor runs the NEW offscreen-position launcher and performs
the moving-camera-away fixture;analyze native position changes INSIDE measured
render gaps before choosing persistent lifetime/visibility implementation.

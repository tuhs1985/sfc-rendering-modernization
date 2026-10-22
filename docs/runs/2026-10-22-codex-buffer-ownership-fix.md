# Run108 — correct buffered output ownership and GPU-read retirement

2026-10-22 America/New_York. Sponsor authorizes “ok, make the fix”. HEAD0fc1300,
branch codex/github-sanitized,index empty;Run103–107 changes already pending.
Read HANDOFF,Run106/107,buffer contract/probe,actual failing run040533-028542,
receiver/writer/qualification and native tests. Fuel Guard recent trusted hook
confirmed. No helper/agent,new SFC gameplay,stage,commit or push.

## Reproduce, implement and adjudicate

CONFIRMED standalone reproduction BEFORE native correction:
`20261022-041110-375397-return-fixture`, new explicit early-ready mode uses
~16.45ms source lead rather than old short~3.5ms lead.298/600draws reproduces
the alternating failure without SFC. Result also flags incomplete resident
rebind acknowledgement; retain partial evidence,not a cleanup/qualification
PASS. Native fixture itself exits0/state0;useful failed integration evidence.

Chosen correction retains two output slots and unchanged128MiB image budget:

1. Buffered writer reserves idle slots only. Queued READY images must survive
   until consumed/rejected. Full pool skips a publication;never blocks SFC.
2. Buffered game compositor signals a per-slot D3D11 GPU fence AFTER sampling
   that image. Existing import worker polls fence completion and frees the
   finished read BETWEEN Presents,without using the game immediate context.
   Merely forbidding overwrite without earlier retirement would just drop new
   images every other frame;both corrections are required.
3. Explicit buffered mode is passed to renderer/output-worker children,not just
   the game. Intermediate041648-319202 achieved590/600with worker retirement
   but6overwrites/retain_ready=false;analysis exposed missing child propagation.
   Corrected and rerun;this intermediate result is not the qualified final build.
4. Separate early/late qualification requires actual worker release counters,
   zero overwritten outputs and protected-ready policy. Unbuffered latest-wins
   and EVENT-query path remain unchanged. No original drawing suppression.

Considered/rejected:third output image slot exceeding conservative128MiB budget;
polling the immediate context from another thread;render-thread waiting/flushing;
relying on next-frame draw callbacks to retire reads (publication can precede
those callbacks);disabling exact identity/fences or holding stale pictures.
No simulation/render hook/ABI/asset/material/light change or new renderer API.

## Exact implementation files

- `tools/d3d9_proof/game_output_wire.h`:optional retainReady reservation policy,
  defaultfalse;wireversion2/576byte layout unchanged.
- `tools/d3d9_proof/game_output_writer.h`:explicit mode,protected reservation,
  policy receipt in reserved word3.
- NEW `tools/remix_runtime/game_gpu_read_lease.h`:monotonic,atomic GPU read lease,
  D3D11Device5/context4 support;unsupported/invalid/signal/device-loss errors.
- `tools/remix_runtime/d3d9_game_receiver.h`:buffered worker-only fence completion,
  release counter reservedword0;game-thread Signal;old unbuffered query intact.
- `tools/remix_runtime/live_owner_timing.py`:explicit child mode and policy/
  worker-release summary readback after stopped capture.
- `tools/remix_runtime/run_return_fixture.py`:`--buffer-early-ready` requires
  buffered mode;phase recorded;default short-lead fixture preserved.
- `tools/remix_runtime/qualify_synchronized_buffer.py`:mandatory separate early
  andlate evidence,current return binaries,zerooverwrite/policy/worker receipts.
- `tests/d3d9_game_output_tests.cpp`:649checks including protected full pool,
  pending-read safety,600-step deterministic early-ready replay.
- `tests/d3d9_synchronized_buffer_tests.cpp`:33checks/architecture,including
  actual GPU fence signaling,repeated values,duplicate-signal rejection and
  independent worker completion polling (no immediate-context access there).
- `tests/test_synchronized_buffer.py`:early/late gate/false policy rejection.
- Contract/probe,HANDOFF,this record,newcurated evidence updated/created.

Synchronization basis:Microsoft official
[Signal](https://learn.microsoft.com/en-us/windows/win32/api/d3d11_3/nf-d3d11_3-id3d11devicecontext4-signal),
[GetCompletedValue](https://learn.microsoft.com/en-us/windows/win32/api/d3d11_3/nf-d3d11_3-id3d11fence-getcompletedvalue),
[CreateFence](https://learn.microsoft.com/en-us/windows/win32/api/d3d11_4/nf-d3d11_4-id3d11device5-createfence).
Only the game thread calls the immediate context. The worker polls a device
child,not that context. NoWait/SetEventOnCompletion/noextraimagebuffers. Fence
interfaces are explicitly qualified on this hardware;unsupported systems omit
buffered insertion,not silently select a weaker synchronization path.

## Reproduction and validation

Same bundledPython/modernpwsh,VS18x86/x64 `/O2 /W4 /WX /fp:precise /Brepro`,
pinned Remix1.5.2 and existing copied installation. Scoped host elevation only;
no policy/security changes. Before/after client hashes unchanged. Commands:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/d3d9_proof/build_receiver.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/d3d9_proof/build_synchronized_buffer.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/remix_runtime/build_return_probe.ps1
python -m unittest discover -s tests -p 'test_*.py'
python tools/remix_runtime/run_return_fixture.py --d3d9-additive --persistent-scene --rebind-owner --synchronized-buffer --buffer-early-ready
python tools/remix_runtime/run_return_fixture.py --d3d9-additive --persistent-scene --rebind-owner --synchronized-buffer
python tools/remix_runtime/run_return_fixture.py --d3d9-additive --persistent-scene --rebind-owner
python tools/remix_runtime/light_discovery.py
python tools/remix_runtime/qualify_persistent_scene.py --fixture artifacts/remix-runtime/runs/20261022-042011-310157-return-fixture
python tools/remix_runtime/qualify_synchronized_buffer.py --fixture artifacts/remix-runtime/runs/20261022-041923-373411-return-fixture --early-fixture artifacts/remix-runtime/runs/20261022-041830-729796-return-fixture
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/d3d9_proof/start_d3d9_buffered_scene_session.ps1 -CheckOnly
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/d3d9_proof/start_d3d9_persistent_scene_session.ps1 -CheckOnly
git diff --check
```

425Python tests PASS;native reservation649checks,x86/x64actualGPU33each PASS.
Return wire37/depth13/broad14/calibration22 build/tests PASS. Final builds and
light/persistent/both-phase bufferqualifications/read-only preflights PASS.

| Fixture | Fixed window | Total paired | Overwritten / busy | Worker releases |
| --- | --- | --- | --- | --- |
| Old early041110-375397 |298/600|partial|old policy|none|
| Final early041830-729796 |589/600|590|0 /3|590|
| Final late041923-373411 |588/600|589|0 /5|589|
| Final unbuffered042011-310157 |595/600|legacy exact-current|legacy|not enabled|

Both final buffered runs:threeowner/revision epochs retained/rebound,exact saved
native scene/HUD pixel check,border untouched,zero auditfailed/dropped andzero
invalid/resource errors,state0,disable/re-enable/resize/recreation safe,normal
owned fixture/renderer exits. Early audit604records:590paired,7withoutship,
5warmup,2reset,max43.901ms;late599records:589paired,4withoutship,4warmup,2reset,
max31.893ms. Some window omissions include deliberate disable and rebinds;
do not claim100% delivery,physical latency or a controlled full-game benchmark.
Native source anomaly counterszero. Actualdevice-removal injection notperformed;
existing safe recreation tests and sentinel/failure guards are not equivalent.

CONFIRMED offline:alternating overwrite/retirement regression reproduced and
corrected;no queued outputs overwritten on final runs. STRONG HYPOTHESIS:
removes constant alternating SFC flicker. Actual corrected SFC continuity and
control feel PENDING. No prediction/replacement/seamless/formalTRL claim.

## Limits, retention and final state

No extra image surfaces. Two output triplets,two color/depth history slots,
33,177,600history bytes,116,121,600conservative total unchanged. 8192auditrecords,
one adjacent frame/50msexpiry,90second tactical/five-minute workflow unchanged.
Logs/capture bounded;originalshipsON,diagnostic geometryhookOFF. Existing
firstlaunch/actualdeath/multiobjectdisplay/vendor40warning limitations remain.

Original/copied executable SHA256
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
No actual SFC run launched this task;all observed rendering was standalone.
Fixture generated copies recoverably archived using existing hash-verified
archive workflow;raw packets/logs/results retained ignored. Archive receipts
in each run directory record exact ZIP hashes/sizes. Prior failed evidence
preserved and never promoted. Final cleanup/status details in authoritative
handoff. Allsource/docs unstaged/uncommitted on0fc1300,indexempty,nopush.

Final artifact inventory12,606,421,165bytes<20GB. Five fixture-generated sets
ZIP-compacted (about6.87MBeach),rawresults retained. Archive SHA256receipts:

- 041110-375397:D706F0C3ABE0527EFFFDB9F842A7B4C4128504A2363E0F3D695F41A3574748E3
  (partial,notpromoted).
- 041648-319202:835A0BFB6E0F1655CF4492D4E6EC2EFC4C9AA6640B65D4D006698FAC00A57FD4.
- 041830-729796:E88D43CB9FD4C299F304CA9CE179149D6BA1625B1CF756E593059D6C27C94ADE.
- 041923-373411:9E6790A1E12715A4A644D653779CB30AE721513529EFD2DD59DD8C68DC02500C.
- 042011-310157:B76DFB3181D01087C0CEF2493407D0DEF9835DD3B67936AFCA07AA9CD8614AE8.

Current copied proxy E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7
confirmed restored. Noownedgame/host/receiver/fixtureprocess. Referenced paths,
JSON,PSparser and whitespace checks PASS. This checkpoint does not depend on
an active tool/mapping/session;next launcher creates fresh session identities.

Exact next action:sponsor repeats SAME buffered-scene launcher once,freeform
camera/movement,normalexitatfinaltwoLOWbeeps;review corrected actual run before
any broader expansion. No new discovery or appearance tuning required.

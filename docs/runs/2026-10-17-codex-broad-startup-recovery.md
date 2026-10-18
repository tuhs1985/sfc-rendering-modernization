# Codex run — broad startup failure and deferred rollback recovery

Run SFC-RETURN-20261017-10,2026-10-17 EDT. Sponsor reports three failed attempts;
only first started SFC. Continue approved broad capture preparation,not rendering
implementation. HEAD e96765a,indexempty;preserve all existing uncommitted work.
Read HANDOFF,approved broad contract/run09,actual failed logs,runner/controller.
FuelGuard exact-thread recent-hook verified;no daemon/helper/delegation/commit.

## Actual failure evidence

Only actual new game run:artifacts/remix-runtime/runs/20261017-181008-941125-in-game.
Launcher verified copied PID35940 suspended path/client hash and preloaded project
DLL. Gate controller14784 exited5 within total1.078s,log verbatim:

```text
target_md5=2BE8F713F81B1C68D50EAD6088C32886
Remote LoadLibraryW failed: 24
```

Result final ready0/epoch0,armed0,produced0,gate clean false. Broad file128B only,
0records,gateQpc0,error0,reason3externalstop. CONFIRMED:no tactical evidence;do not
interpret empty capture as no depth/resources. First failure was gate loading,
not file cap,ABI observer failure or proven graphics incompatibility.

STRONG HYPOTHESIS:early loader/module-list mutation. Runner attempted gate before
graphics ready;controller remote_module_base called CreateToolhelp32Snapshot only
once. Error24 is ERROR_BAD_LENGTH. Microsoft's documentation describes target
loader initialization/module changes and recommends retrying this specific error:
https://learn.microsoft.com/en-us/windows/win32/api/tlhelp32/nf-tlhelp32-createtoolhelp32snapshot
Original error logging did not distinguish every LoadLibrary substep,so precise
failing API is not dynamically CONFIRMED. Never retry an already-attempted remote
call/injection blindly;retry only the read-only snapshot operation.

Runner left game alive and correctly deferred proxy restoration. It stopped the
observation-only host,terminated its waiting launcher parent (not SFC),then saved
PARTIAL. Copied proxy retained fullSHA A1BA...AE24 rather than oldSHA E35E...CAB7;
later two invocations stopped at preflight before creating a new run/game. This
was not three independent graphics failures. Deferred rollback lacked a usable
automatic recovery path and failed startup offered too little time for normal
exit. First result stays immutable;recovery recorded separately.

ReShade recovery log independently shows full6.7.1.2131 registered API18,created
the native graphics environment after abort and finished exiting14:10:21 EDT.
Warning `Reference count for ID3D11Device0 object ... is inconsistent (58)` present
at exit;meaning/cause unresolved,not a byte count or established leak. Do not
claim warning-free runtime cleanup. Existing Remix40-object/driver risks remain
open;this run did not load Remix. Original critical files/launcher settings were
unchanged in failed result. No normal game exit code was retained after launcher
parent termination;later process absence is not a substitute for that evidence.

## Recovery actually performed

Native inventory confirmed no StarFleetOP process. Verified exact saved rollback
SHA E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7,
configuration backup hash against manifest,and every other copied critical file.
Restored ONLY copied dxgi.dll/ReShade.ini using same-directory verified staging;
preserved post-run configuration and ReShade log. New recovery.json confirms all
copied critical hashes match original manifest. Original result/packets untouched.
No game killed/launched;no original-install mutation or security-policy change.

Existing tasklist command returned `ERROR: The user name or password is incorrect.`
in restricted execution context. Replaced credentials-dependent shell discovery
with read-only native Toolhelp process inventory;errors propagate,never imply
absence. Actual native inventory successfully permitted recovery. A recovery-only
admin-token check was unnecessarily restrictive and removed;recovery needs valid
inventory and file rights,not injection privilege. Runtime injection STILL requires
the established elevated parent. Unsandboxed tool approval is not an admin token;
no UAC prompt/security weakening introduced.

## Changes and tests

- m1_controller.cpp/module_snapshot_retry.h:only ERROR_BAD_LENGTH snapshots retry,
  max100attempts with99x10ms pauses (~990ms plus API time). Fatal access/architecture
  errors not retried. Log attempts/last transient error. No remote-call/ABI changes.
- New build_m1_controller.ps1 rebuilds only controller+retry unit test;normal
  prepared runner invokes it. Native212deterministic checks PASS /O2 /MT /W4 /WX:
  success,1/99transient failures,bounded100failure exhaustion,fatal immediate exit.
  Test-only constant-lambda unreachable-code warning fixed,not suppressed.
- wait_component_ready before gate:explicit PID/startup verified/restored/ready
  handshake,max60s inside overall five-minute watchdog;exit/error/timeout fail
  without gate injection. Gate/controller hashes now recorded in manifest.
  Historical first manifest lacked controller binary hash;do not invent it.
- Failed workflow allows up to30s within remaining budget for requested normal
  game exit;records observed exit code when available. If still running,leaves
  DLL/proxy in place. No forced SFC termination or hot DLL swap.
- recover_broad_session.py:exact transaction provenance and baseline hashes,
  native process absence,verified backups,atomic restore;preserves recovery log.
  Explicit recovery command and automatic unique-pending recovery before executing
  next broad preflight. Ambiguous/changed/invalid backups fail closed. Read-only
  preflight WITHOUT --execute never mutates/recoveries.
- windows_processes.py:read-only Toolhelp process names,correct pointer-sized
  PROCESSENTRY32W,all inventory failures propagate. Used by game/recovery/rollback.
- Python full135tests PASS1.983s,projectTEMP/TMP:readiness/error/exit/timeout/wrong
  PID,live-game refusal,unique pending recovery/marker,ambiguity,discovery failure,
  existing cap/parser/rollback/archive/camera/transport regressions.
- Native collector/source untouched;last actual positive/negative fixtures
  180332-043697/180344-409639 remain applicable. Qualification source hashes were
  refreshed to include new controller/recovery policy and current Python tools.
  This does NOT claim the revised gate has passed an actual SFC runtime yet.

Files:this record,HANDOFF,probe/contract/readiness notes,durable qualification;
tools/m1_component/m1_controller.cpp,module_snapshot_retry.h,build_m1_controller.ps1;
tests/m1_module_snapshot_tests.cpp,test_return_startup_safety.py;
tools/remix_runtime/windows_processes.py,recover_broad_session.py,run_return_game.py,
start_return_image_session.ps1,prepare_full_reshade.py,qualify_broad_rollback.py.
No geometry capture,hook selection,log cap or rendering-path behavior change.

## Reproduction / result / final state

Executed bundledPython3.12.14:

```text
tools/remix_runtime/recover_broad_session.py artifacts/remix-runtime/runs/20261017-181008-941125-in-game
tools/remix_runtime/prepare_full_reshade.py --qualify artifacts/remix-runtime/runs/20261017-180332-043697-return-fixture artifacts/remix-runtime/runs/20261017-180344-409639-return-fixture
-m unittest discover -s tests -p test_*.py
tools/remix_runtime/run_return_game.py --broad-capture --observation-only
```

Recovery run succeeded with normal file access after native absence check;builder
used approved unsandboxed file access for prior elevated-owned output. Last
command is read-only preflight,not gameplay. PowerShell7.6.5 built controller via
tools/m1_component/build_m1_controller.ps1. PS parsers/diff/hash checks repeated at
closeout. Same sponsor command -BroadCapture remains next action;no additional
administrative step or manual cleanup required. Test instructions unchanged:
usual two-ship skirmish,keep both visible briefly,normal exit at two beeps~10s.

Result:STARTUP/RECOVERY FIX OFFLINE-VALIDATED;READY FOR ANOTHER SPONSOR ATTEMPT.
No broad tactical evidence or replacement PASS claimed. Capture remains10s/2GB
hard/1GB warning,16MiB ring,32MiB ancillary,10GB overall including archive reserve.
Archive/recovery/hash/final status recorded below after closeout;no staging/commit.

Closeout:135Python tests repeated PASS2.380s;native212snapshot checks PASS;
PowerShell wrapper/controller-builder parsers,read-only preflight and git diff
--check PASS. Source changes qualified for next attempt;collector binary/GPU
fixtures not changed. New durable qualification JSON contains current source
hashes. No StarFleetOP process by native inventory. All seven accepted critical
hashes still match failed run's pre-state;all copied critical hashes restored.
Original/copied clientSHA256
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29;
copied proxySHA256
E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7.
HEAD e96765a,indexempty;HANDOFF/controller tracked edits and all other existing/new
files unstaged/untracked. No commit,cleanup deletion or new SFC launch.

Verified archive artifacts/remix-runtime/archives/20261017-broad-startup-recovery.zip:
14,668B,12entries,53,683Bsource,SHA256
E62D832C922C4EB728102F8837A31FDA8F2150F180FEE4218D4B616AA3BD858E.
Includes original failed evidence,recovery audit and actual recovered ReShade log;
CRC verified. Excludes binaries/rollback originals;those remain intact. Small
raw evidence retained. No meaningful capture was lost or represented as success.

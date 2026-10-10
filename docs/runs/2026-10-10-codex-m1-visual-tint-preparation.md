# Codex Run Record — first bounded visual intervention preparation

## Identity and authority

- Run ID/date: `CODEX-20261010-M1-VISUAL-TINT-PREP`, 2026-10-10.
- Active task: M1 diagnostic visual-control increment following the semantic
  sub-gate PASS; sponsor authorized continuation with “Begin.” Approved CDD
  v1.0/active M1 plan remain unchanged. No formal TRL 4 claim.
- Baseline: `b115260`, five semantic hooks validated in M1-A-RT-003. Starting
  tree contained only the three untracked 2026-09-19 handoff/analysis/run docs;
  they were preserved. No source changes were present initially.
- Question: can one ship's primary mesh receive a reversible source-color
  substitution through the semantic component while the original renderer and
  other owner continue? Runtime remains unexecuted.

## Evidence and decisions

Read the handoff, approved M1 plan, latest stutter record/probe, risk register,
integration contract, semantic maps, component/controller/runners, and retained
exact-build dumpbin disassembly. Traced only mode/source/color/batch paths.
Rejected manager `+0x1ECC` mode mutation because a deferred path reads shared
state. Characterized polygon source indices, 36-byte stride, RGB bytes
`+4/+5/+6`, prepared vertex colors and copying into the known generic batch.
Exact addresses and confidence are in
`docs/m1/m1-b-visual-control-analysis.md`.

Selected a fixed, component-owned source copy with magenta RGB for one validated
owner epoch. Preserved logical source identity in existing records; added
effective pointer, copy extent, original sample RGB, application time and
release evidence. No shared model/source asset is edited. Existing hook
thunks/sites are unchanged. Geometry hook is prohibited for this mode.

Stop now prevents new substitutions and drains active copies through visual
exit before removing hooks. Guarded reads, bounded list/index/extent checks,
thread consistency, conditional pointer restoration, and failure counters
bound the risk. Row-size checks precede file writes to enforce a strict cap.
The controller can wait for an automatic tactical event before starting its
active timeout. This prevents menu time from consuming the on/off test.

## Tools, parameters, and reproducibility

- Fuel Guard attached via the instructed global command. Hook receipt was
  confirmed; direct daemon/quota query was sandbox-denied. No daemon started.
- Visual Studio 2026 18.7.3, x86 toolset 14.51.36231. Build:
  `& tools/m1_component/build_m1_component.ps1`.
- Python 3.12.14 at the explicit bundled runtime path recorded in the probe.
  Tests: `-m unittest tests.test_analyze_m1_log tests.test_analyze_probe_log
  tests.test_analyze_m1_visual_tint -v`.
- PowerShell parser checks for all four edited/new build/runner scripts;
  `tests/test_m1_process_image_path.ps1` and
  `tests/test_probe_elevation_policy.ps1`.
- Bundled Git at
  `C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe`
  used for final `diff --check`, status, cached-status and ignore checks.
- Applicable runtime definition: `M1-B-RT-001`. Prepared command:
  `& tools/m1_component/start_m1_visual_tint_session.ps1` from a verified scoped
  elevated parent. Limits: 600-second gate wait, 60-second active window,
  3,000 epochs/50,000 events, eight owners, 16/32 MiB warning/hard event cap;
  five seconds normal, ten seconds admitted tint, then original source.
  Copy bounds: 4,096 polygons, 256 entries/9,216 bytes per thread.
- Generated build SHA-256:
  - DLL: `5D5398D723561C45522F1987B99AAEEA5F20EEC81F6220C47AD5B929E1D764A3`.
  - Controller: `6B35B7BBCB7CF7069970892C79FE3768D0921AD9EC3E8486E829F2F49B75706D`.

## Files changed

Modified tracked files:

- `tools/m1_component/m1_component.cpp`
- `tools/m1_component/m1_controller.cpp`
- `tools/m1_component/build_m1_component.ps1`
- `tools/m1_component/run_m1_increment_a.ps1`
- `tools/m1_component/start_m1_enabled_session.ps1`

Added implementation/tests:

- `tools/m1_component/m1_visual_tint.h`
- `tools/m1_component/analyze_m1_visual_tint.py`
- `tools/m1_component/start_m1_visual_tint_session.ps1`
- `tests/m1_visual_tint_tests.cpp`
- `tests/m1_visual_tint_component_tests.cpp`
- `tests/test_analyze_m1_visual_tint.py`

Documentation: updated existing untracked `docs/HANDOFF.md` and
`docs/m1/m1-b-visual-control-analysis.md`; added
`docs/m1/probes/M1-B-RT-001.md` and this run record. The untracked
`docs/runs/2026-09-19-codex-m1-visual-control-analysis.md` was not edited.

## Validation and deficiencies

- Final x86 build passed `/W4 /WX`. Contract, source-copy/bounds/release,
  production recorder/stop lifecycle, and WINMM forwarding tests passed.
  Production fixture used synthetic objects only, never real SFC addresses.
  It verified automatic ship gate, stack-source substitution, unchanged
  original storage, second-owner and exception exclusion, original-pointer
  release, and drain after a stop request. Forced 1,024-byte event-log cap
  stopped at a complete-row boundary without exceeding the cap.
- Four Python analyzer tests passed. The tint analyzer rejects cross-owner or
  unreleased evidence and leaves visible effect explicitly UNADJUDICATED.
- PowerShell parsing, image/exit test, and elevation-policy regression passed.
- Bundled Git `diff --check` passed; generated binaries/test temps are ignored.
  Local links and untracked-file whitespace were checked after documentation.
- Initial Python tests hit `PermissionError: [Errno 13] Permission denied`
  in the sandbox's automatic temporary directory. Repeated successfully with
  process-local `TEMP` and `TMP` pointing to ignored
  `artifacts/m1/test-temp`; no system environment/security setting changed.
- Program Files Git `diff` returned verbatim:
  `fatal: this operation must be run in a work tree` despite status/rev-parse
  succeeding. Bundled Git passed; repository configuration was not changed.
- Current shell and a read-only outside-sandbox privilege check both returned
  `parent_is_admin=False`. No appropriately scoped elevated parent was
  established in this run, and no UAC prompt was requested. The visual entry
  point refuses non-elevated launch. Runtime start is parked until this
  administrative prerequisite is supplied through the approved workflow.

## Result and checkpoint

**Visual build/offline validation: READY FOR SPONSOR RUNTIME TEST.** Workflow
not launched/armed; elevated-parent prerequisite remains unresolved. Static
color path and synthetic behavior are established; actual tint strength,
coverage, timing, live owner targeting and non-interference remain
**STRONG HYPOTHESIS / runtime unconfirmed**. No gameplay evidence was generated.

Both installed and reference client MD5 matched
`2BE8F713F81B1C68D50EAD6088C32886`; SHA-256 matched
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
Restored launcher SHA-256 matched its frozen value. No SFC/launcher/controller
was running and no game-directory proxy/config was observed. New bulk output
is limited to ignored build/test artifacts; no runtime archive/cleanup is due.

Final tree: five tracked files modified and eleven untracked files (including
the three preserved prior docs). Nothing staged or committed; HEAD remains
`b115260`. No renderer architecture, asset replacement, helper invocation,
requirements change, or unrelated cleanup occurred.

Exact next action: provide a verified scoped elevated parent and start the
prepared M1-B-RT-001 runner; only then ask the sponsor to enter the two-ship
fixture and report the normal/magenta/normal sequence and other-owner/UI behavior.

## Runtime readiness recheck — 2026-10-10

Sponsor reported readiness. Rechecked the prepared DLL/controller SHA-256
values; both match the build hashes above. Current analyst process reported
`parent_is_admin=False`; no SFC, launcher or controller process was found.
Read-only `Get-ScheduledTask` filtering task name/path for `SFC|Codex`
returned no matching rows (not proof that no elevated process exists).
Searched the M1 tooling/runbook for existing elevation/broker mechanisms;
the visual entry point requires an elevated parent and intentionally does
not use the older neutral runner's `RunAs` fallback.

No runtime launch, injection, capture, security-policy change or UAC request
occurred. **CONFIRMED:** this execution context cannot meet the entry point's
admin check. Runtime proof remains unexecuted, not a failed visual experiment.
One-time establishment of a scoped elevated PowerShell parent is required;
subsequent probe launches should inherit it rather than request routine UAC.

Execution-policy follow-up: sponsor reports scripts blocked in their shell.
Read-only `Get-ExecutionPolicy -List` in Codex returned MachinePolicy,
UserPolicy, Process and CurrentUser `Undefined`, LocalMachine `RemoteSigned`;
effective policy `RemoteSigned`. This does not establish the sponsor shell's
policy or exact error. Documented a dedicated `powershell.exe -NoProfile
-ExecutionPolicy Bypass -File <prepared entry>` invocation from the elevated
parent in M1-B-RT-001. It is process-only, not an elevation mechanism or
persistent security change; enforced policy must not be circumvented.
No runtime was launched or system policy changed. This follow-up also modifies
`docs/m1/probes/M1-B-RT-001.md`; nothing staged or committed.

## Windows PowerShell launch compatibility correction — 2026-10-10

Sponsor supplied exact failure at `run_m1_increment_a.ps1:175`:
`You cannot call a method on a null-valued expression.` at
`[void]$startInfo.ArgumentList.Add([string]$argument)`.
**CONFIRMED:** Windows PowerShell's .NET Framework ProcessStartInfo lacks
ArgumentList; this exception precedes Process.Start, hence this attempt did
not start the controller/injector. No visual outcome is adjudicated.
The previous analyst launch instruction incorrectly assumed modern .NET.

Added an entry-only runtime shim: on PowerShell <7, re-execute the reviewed
visual entry in the installed bundled `dependencies/native/powershell/pwsh.exe`
with `-NoProfile -ExecutionPolicy Bypass -File <entry>`. It inherits the parent
token, propagates nonzero failure, and refuses a missing runtime before game
startup. No UAC request or persisted policy change is introduced. Existing
component binaries, ABI, hooks and capture bounds are unchanged.

Files modified: visual entry, this record, HANDOFF and M1-B-RT-001. Added
`tests/test_m1_visual_entry_runtime.ps1`, which extracts the production shim
and re-executes a harmless fixture rather than gameplay. Initial test fixture
used automatic PSCommandPath inside a dynamically created scriptblock (null);
corrected to the explicitly captured entry path. Final regression command
`powershell.exe -NoProfile -ExecutionPolicy Bypass -File tests/test_m1_visual_entry_runtime.ps1`
passed, and bundled Git `diff --check` passed (existing LF/CRLF warnings only).
Analyst process query found no SFC/controller. No new runtime evidence,
client mutation or hash claim was produced by this compatibility correction.
Final HEAD unchanged at b115260; five tracked modifications and twelve
untracked files, nothing staged or committed. Exact next action: sponsor exits
any old game normally, retries the documented elevated launch, then enters
two-ship fixture only after successful startup.
No new source/configuration changes or test reruns were needed because build
hashes matched. Files changed by this recheck: this record and `docs/HANDOFF.md`.
HEAD remains `b115260c32b28bfff5b148f940cf29317fda747c`; the existing five tracked
modifications and eleven untracked files remain, nothing staged or committed.

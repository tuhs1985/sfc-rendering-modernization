# Codex Run Record — M1 automatic tactical gate and disabled baseline

## Run identity and scope

- Run ID/date: `CODEX-20260905-M1-BASELINE-GATE`, 2026-09-05.
- Active package: M1-01/M1-03 harness hardening; obtain clean disabled baseline.
- Starting commit: `51ab372`; existing reviewed Increment-A work and runner-fix
  records were unstaged/untracked. No unexpected staged or tracked changes.
- Question: can the harness open capture automatically on meaningful tactical
  ship rendering, then record a bounded disabled two-ship baseline and exit?
- Explicit boundary: no neutral semantic component test, visual modernization,
  helper invocation, staging, or commit.

## Evidence and gate decision

Reviewed the approved M1 plan, M0 report/semantic maps, M0-RT-003 definition,
current component/controller/runners, prior partial baseline, client hashes and
module-enumeration error.

Selected `tEntityShip::render` entry `0x004162B9`, validated by ship vtable
`0x00796F0C`, visual pointer `+0x88`, and visual vtable `0x007985A4`.
M0 ownership and two-owner runtime linkage are CONFIRMED. Absence from menus and
timing at tactical entry are STRONG HYPOTHESIS pending this run. Later visual and
model functions were less early/specific; generic geometry/draw signals were
rejected.

## Implementation and configuration

Created a standalone one-hook `M1_GATE_ONLY` build, exact gate definition, and
disabled-baseline/elevation runners. The gate records at most one event, signals
the controller, restores exact bytes, is independently checked, and unloads
before telemetry. Manual signal-file fallback is bounded and explicitly labeled.
Exit detection now polls the selected PID at 250 ms and distinguishes exit from
timeout. The scoped elevated workflow launches the hash-verified original SFC
Launcher and directly injects the gate DLL; it adds no game-directory files.

Files created/modified and final runtime evidence will be listed after execution.

## Offline validation to date

- Client MD5 `2BE8F713F81B1C68D50EAD6088C32886` and SHA-256
  `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`
  matched before runtime preparation.
- MSVC x86 builds, contract tests and standard proxy forwarding test passed.
- Gate and component exports passed; PowerShell parser checks passed.
- Image-query tests passed; missing/live PID exit classification and a real child
  normal-exit observation passed.
- Python M1 analyzer and M0 analyzer regression passed; `git diff --check` passed.
- A first offline auto-run attempt stopped before launch because ordinary user
  access could not write the game directory. No file was installed. This exposed
  the privilege condition and led to the direct-injection elevated-parent design,
  eliminating game-directory writes from the disabled baseline.

## Runtime result — PASS for the clean disabled-baseline objective

Executed `M1-A-BASELINE-002` run `20260905-094407-disabled-auto-gate` with the
two-ship skirmish fixture. The scoped workflow required one UAC transition,
verified/launched the restored launcher, discovered PID 7692 at 09:45:31.954 ET,
and opened the gate automatically at 09:45:44.410. The sponsor supplied no scene
timestamp.

The retained event was `ship_owner` at `0x004162B9`, ship `0x1CE6A1D8`, linked
visual `0x1CE62140`, with exact vtables `0x00796F0C` and `0x007985A4`. Two hook
calls occurred before the controller stopped; only one event was retained and
the second owner exceeded the configured one-owner detail cap. There were no
rejected semantics or log truncation. This is consistent with the two-ship
fixture and demonstrates that the gate condition is semantic rather than a
generic graphics call.

Controller output confirmed component enable, detail-bound stop, exact hook-byte
restoration, and gate-DLL unload. Baseline telemetry started at 09:45:44.726,
after removal, and retained 119 samples through 119.289 seconds. The process
disappeared after the sponsor's normal exit action and was classified `exited`.

Final MD5/SHA-256 matched the starting client. The runner added zero files to the
game directory. Run-directory output totaled 13,489 bytes including the result;
event CSV was 522 bytes and telemetry 9,524 bytes. The output remained far below
the documented limits. Evidence confidence: automatic semantic gate, restoration,
unload, bounded capture, process disappearance and client preservation are
**CONFIRMED for this fixture**.

The sponsor reported normal in-game behavior with no noted issues across
rendering, HUD, cursor, targeting, camera movement, and controls. Combined with
the direct runtime evidence, the clean disabled baseline and automatic scene gate
are accepted. Manual timestamping is unnecessary for the tested fixture.

This result completes only the harness/disabled-baseline objective. M1 remains
**CONTINUES**; the next execution step is the separately bounded enabled neutral
semantic pass-through run paired to this baseline. It cannot establish formal
TRL 4 PASS by itself.

Module enumeration denial is documented and deferred because it did not block
process-image attribution, gate detection, or elevated controller access.

## Repository state

Files created in this run: `m1_gate.def`, `run_m1_disabled_baseline.ps1`,
`start_m1_disabled_baseline.ps1`, this record, and `M1-A-BASELINE-002.md`.
Files modified include the shared component/controller/build scripts, process
image/exit module and test, manifest, component runbook, and future enabled/direct
runner exit handling. Generated binaries/evidence remain ignored.

All current M1 implementation, documentation, tests, and run records remain
unstaged/uncommitted. No implementation commit is authorized.

Final validation repeated the process-image/exit tests and both Python analyzer
tests successfully. All component PowerShell files parsed; build/test/export
checks had passed immediately before the runtime run; whitespace/diff checks
passed. Final client hashes remained exact. No `winmm.dll` or
`m1-component.ini` was present in the game directory. Git showed only the
expected untracked Increment-A files listed above, with nothing staged or
committed; HEAD remained `51ab372`.

# M1 Increment A Neutral Component Runbook

## Tool and purpose

- Tool ID/version: `SFC-M1-A-COMPONENT 0.1`
- Controller: `tools/m1_component/m1_controller.cpp`
- Component: `tools/m1_component/m1_component.cpp`
- Build: `tools/m1_component/build_m1_component.ps1`
- Runner: `tools/m1_component/run_m1_increment_a.ps1`
- Preferred no-extra-UAC session runner:
  `tools/m1_component/run_m1_proxy_session.ps1`
- Analyzer: `tools/m1_component/analyze_m1_log.py`
- Contract: [M1-A-CONTRACT-001](../m1-a-integration-contract.md)

The component observes the confirmed ship/model/mesh chain and then executes the
original instructions through private trampolines. It does not render, replace a
renderer, alter game state, or patch the client on disk.

## Build and offline validation

From an ordinary PowerShell shell:

```powershell
pwsh -NoProfile -File .\tools\m1_component\build_m1_component.ps1
python -m unittest tests.test_analyze_m1_log -v
```

The build targets x86, treats warnings as errors, runs the C++ contract tests,
and verifies the `M1StartW`/`M1Stop` exports. Outputs are ignored under:

```text
artifacts/m1/bin/
  m1_component.dll
  winmm.dll
  m1_controller.exe
  m1_contract_tests.exe
```

Do not manually copy either DLL into the SFC installation. The proxy session
runner controls the temporary local loader and refuses pre-existing conflicts.

## Privilege and launch preparation

### Disabled automatic-gate baseline

`M1-A-BASELINE-002` uses `start_m1_disabled_baseline.ps1`. Its scoped elevated
process verifies and launches the original SFC Launcher, so the sponsor receives
the same single UAC transition required by the normal launcher workflow. The
elevated parent injects standalone `m1_gate.dll`; no DLL/configuration is copied
to the game directory. On the first validated ship-render event the controller
restores the one touched entry, verifies all known hook bytes, unloads the gate
DLL, and only then starts disabled telemetry.

```powershell
pwsh -NoProfile -File .\tools\m1_component\start_m1_disabled_baseline.ps1
```

Automatic gate timeout is 600 seconds. Manual fallback uses `-GateMode Manual`;
the runner prints a run-specific signal-file path and waits at most 600 seconds.
Manual mode is fallback evidence and must be identified as such. Exit detection
polls the selected PID at 250 ms intervals and reports either `exited` or
`timeout-running`; it does not rely on `Wait-Process` access to an elevated PID.

Full gate definition and output controls: [M1-A-BASELINE-002](M1-A-BASELINE-002.md).

Preferred routine operation uses the reversible WINMM loader session. Run it from
the ordinary Codex shell before the sponsor launches SFC. The loader starts the
controller as a child of the game, inheriting the elevation already required by
the normal SFC Launcher. It causes no second UAC prompt and grants no persistent
administrative capability.

Preferred command, run before launching SFC:

```powershell
Set-Location 'C:\Project\SFC-Modernize Engine'
pwsh -NoProfile -File .\tools\m1_component\run_m1_proxy_session.ps1 `
  -MaxSeconds 300 -WaitForClientSeconds 600 -WaitForExitSeconds 600
```

The session refuses to replace an existing game-directory `winmm.dll` or
`m1-component.ini`. It copies the verified proxy/configuration before launch and
removes both after normal exit. The proxy forwards exactly the client's three
WINMM imports to the 32-bit system WINMM.

Direct injection remains a fallback only from a narrowly scoped already-elevated
parent using `run_m1_increment_a.ps1 -Mode enabled`; do not generate an extra UAC
prompt merely to use it.

Where ordinary access cannot create the temporary proxy in the game directory,
use `start_m1_enabled_session.ps1`. It verifies the frozen launcher, creates one
scoped elevated parent, launches SFC, and waits inertly for the workspace-local
`artifacts/m1/enabled-tactical-arm.signal`. Create that signal only when the
sponsor reports tactical entry. The runner then injects directly into the exact
PID and retains the component's automatic first-valid-ship gate. The signal is
bounded by `ArmTimeoutSeconds` (600 seconds by default) and is removed on success
or failure. This path adds no game-directory files.

The runner waits for exactly one launcher-created `StarFleetOP.exe`. If more than
one exists, stop and pass `-TargetPid` only after identifying the correct client.

The direct/disabled runner resolves the selected PID's actual image using
`ProcessImagePath.psm1`: `OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION)` and
`QueryFullProcessImageNameW`. This avoids the stronger access required by
`Process.MainModule` when the launcher elevates SFC. No assumed installation-path
fallback is allowed. If the limited query is denied, the runner reports the
Windows error and stops before capture. MD5 and SHA-256 must both match the
supported client. Metadata records the path-query method. This performs one
bounded path query (32,768-character buffer), emits no trace, and closes its
handle on success or failure; no cleanup or additional UAC is required.

Regression check: `pwsh -NoProfile -File tests/test_m1_process_image_path.ps1`.
The self-process and missing-PID checks do not establish elevated SFC access;
that remains part of the next `M1-A-BASELINE-001` runtime retry.

## Enabled start/stop behavior

1. Runner validates the exact client MD5/SHA-256, installs only the temporary
   proxy/configuration, and waits for the launcher-created client.
2. Proxy forwards WINMM and starts the controller with the game's existing token;
   controller calls `M1StartW` on the already-loaded component.
3. Component validates all six live instruction sequences before changing any.
4. Other target threads are suspended only for the bounded patch transaction.
5. First confirmed ship-owner event opens the tactical gate.
6. Detailed capture stops after 120 frames or 10,000 events. By default this
   signals the controller to remove the component immediately.
7. Controller calls `M1Stop`; the component becomes inert, restores all bytes,
   writes bounded output, and remains loaded but detached from the render path.
8. Controller independently reads all hook sites and requires exact restoration.
9. Runner asks the sponsor to exit SFC normally and records whether the process
   exits within the bounded wait.
10. After process exit the runner removes and records removal of the exact proxy
    and configuration files, then rehashes the client.

For later endurance-only work, `-ContinueAfterBurst` keeps the hooks active and
summary counters running until `-MaxSeconds`; detailed records remain saturated.
Do not use that option during M1-A-RT-001.

Do not terminate the runner/controller while hooks are active. If tooling becomes
unresponsive, exit SFC normally; process exit discards all in-memory changes.
Then remove `winmm.dll` and `m1-component.ini` only after verifying they are the
recorded M1 files; never remove a pre-existing local DLL.

## Disabled baseline

```powershell
pwsh -NoProfile -File .\tools\m1_component\run_m1_increment_a.ps1 `
  -Mode disabled -MaxSeconds 120 -WaitForClientSeconds 600
```

Disabled mode loads no DLL and changes no target memory. It records exact hashes,
modules, and once-per-second process telemetry for the bounded duration.

## Capture filters and hard limits

- Exact executable MD5 only: `2BE8F713F81B1C68D50EAD6088C32886`.
- Exact six hook addresses/byte sequences in M1-A-CONTRACT-001.
- Gate: first ship with `tEntityShip` vtable, valid `+0x88` visual pointer, and
  `t3DVisual_Model` vtable.
- Detailed frames: 120 maximum.
- Detailed events: 10,000 maximum.
- Active detailed owners: eight maximum.
- Event file warning/hard thresholds: 16/32 MiB.
- Runner duration: 2,100 seconds (35 minutes) maximum.
- Queues: fixed memory; no hook performs output I/O.
- After detailed saturation: summary counters only.

For `M1-A-RT-002`, component 0.2 counts every downstream geometry call but
retains only the configured per-owner/per-frame and uncorrelated-per-frame
samples. Its reviewed envelope is 6,000 scene epochs, 100,000 total retained
events, one geometry sample per owner per epoch, one uncorrelated sample per
epoch, 90 seconds, and the unchanged 32 MiB hard event-log stop. Semantic and
lifetime events remain detailed.

For stutter attribution, `-DisableGeometryHook` leaves `0x006AB410` unpatched
while retaining the five semantic/lifetime hooks. The controller still checks
the geometry address during final byte verification. This mode intentionally
does not generate new downstream-correlation evidence; it must be interpreted
with the already-confirmed `M1-A-RT-001/002` correlation.

Unbounded breakpoint or draw-call capture can generate multiple gigabytes rapidly.
Never remove address filters or numeric bounds to obtain more frames. Any increase
requires a revised probe definition and sponsor-visible rationale.

The sponsor authorized a 10 GB absolute temporary-output ceiling on 2026-09-05,
provided raw output is compressed or removed after analysis. This ceiling does
not replace the probe-specific limits above and is not a capture target. Prefer
sampling, counters, and early saturation; any probe needing more than its current
limit must document the smaller bound it will actually enforce and its cleanup.

## Expected output and volume

Each run creates an ignored directory:

```text
artifacts/m1/runs/YYYYMMDD-HHMMSS-enabled/
  run-metadata.json
  loaded-modules.csv
  process-telemetry.csv
  m1-component.ini
  controller.stdout.txt
  controller.stderr.txt
  M1-A-events.csv
  M1-A-summary.json
  M1-A-component.log
  M1-A-analysis.json
  M1-A-evidence.md
  run-result.json
```

Expected detailed CSV volume is below 4 MiB; 32 MiB is an enforced hard stop.
Module/metadata/summary outputs should remain below 1 MiB combined. Telemetry at
one row/second remains small even for 35 minutes.

## Analysis and evidence mapping

The analyzer groups opaque owner epochs, checks expected RTTI vtables, requires a
ship/visual/Model0 chain with correlated `0x006AB410` activity, checks both
component and controller restoration, and verifies the configured bounds. Its
`ONE_OWNER_INTEGRATION_CONFIRMED` result is generated evidence only; Codex must
also review the raw sequence, client hashes, sponsor-visible behavior, and normal
exit before classifying the M1 claim.

## Cleanup and rollback

- Normal: wait for `component_state=removed` and
  `hook_bytes_restored=true`, then exit SFC normally. The proxy session removes
  its exact local loader/configuration after exit.
- Delete/rebuild ignored binaries and raw run directories only after their curated
  evidence has been recorded. They contain no client originals.
- Never copy, replace, or edit `StarFleetOP.exe`.
- If restoration is not independently confirmed, stop further runtime testing,
  exit SFC normally, verify on-disk hashes, and adjudicate the run as failed.

## Known hazards

- Incorrect ABI or trampoline behavior can crash the live client. This is why the
  one-owner run gates all broader testing.
- Controller loss before controlled stop can lose buffered evidence.
- The inert DLL intentionally remains mapped after removal; forced unmapping is
  avoided because it could race a departing hook thunk.
- Pointer identity is valid only inside one process and one non-retired epoch.

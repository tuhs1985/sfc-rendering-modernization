# M1 Increment A Development Test Manifest

## Authoritative baseline disposition — 2026-10-14

Sponsor: "the baseline is what 'ships' in the community edition. I dont' want to
mess with it atm until needed". Accepted baseline is the existing supported
Community Edition installation/launcher configuration, including its bundled
graphics add-ons. Do not strip, disable, upgrade, replace or tune dgVoodoo/ReShade
merely to obtain a wrapper-free baseline. A future necessary change needs an
explicitly scoped proposal and before/after baseline record.

This resolves the scope/documentation discrepancy below: native-launch means the
existing launcher workflow, **not absence of wrappers**. Retain exact client
2.5.6.4/hash and recorded dependency versions; no expansion to other Community
Edition builds. Sponsor attestation establishes accepted baseline scope; source
archive provenance of each installed file was not independently verified.
Missing historical disabled-run dependency hashes remain a comparison limitation,
not a new blocker or reason for a repeat endurance run. No capability waiver or
final rendering-architecture selection follows from accepting existing packaging.
Actual loaded inventory, current hashes and postexit snapshots below are retained.

## Current scope correction — 2026-10-14 endurance

[M1-CLOSE-ENDURE-001 evidence](evidence/M1-CLOSE-ENDURE-001-20261014.md) records
actual game-local dgVoodoo/ReShade DLLs loaded in the tested configuration.
Original dependency statements below are historical and **must not be used to
claim wrapper-free rendering**. Project's semantic component uses no third-party
detour library; that does not imply the installed game has no graphics wrappers.
No wrapper installed/changed/removed by this execution; no architecture adopted.

Loaded paths in run005117 `loaded-modules.csv`; current on-disk product/hash
verification at adjudication (not an in-memory hash or prior baseline hash):

| Game-local file | Product/version | Bytes | SHA256 |
| --- | --- | --- | --- |
|DDRAW.dll|dgVoodoo2.8.6.5 / file4.7.1.3000|257,024|62F1E1B2AC5196F4A74B35B898BA8644322F976026324E2F767A4096BFB58748|
|D3DImm.dll|dgVoodoo2.8.6.5 / file4.7.1.3000|209,920|F51507ACBB1C5510AB72881EEFDE5E4DFE6376667546E86DDCF62E6A9EE4923F|
|DXGI.DLL|ReShade6.7.1 / file6.7.1.2133|4,014,360|E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7|

All under `C:\Games\Taldren Software Inc\Starfleet Command Orion Pirates`.
Their timestamps predate testing, but timestamps alone do not prove prior loaded
configuration. Configuration files have current runtime modification timestamps;
the writer is not established by timestamps, and no prior config hashes were
frozen. Accepted disabled10s capture lacks equivalent module inventory.
Reconcile baseline before final M1 closure; preserve successful endurance result
for actual stack, do not remove dependencies or automatically repeat endurance.
Actual analyst runtime verified Python3.12.14/PowerShell7.6.5; historical Python
version below does not identify current analyzer. Sandbox OS CIM query denied;
do not infer current OS build from historical manifest alone.

## Manifest identity

- Manifest ID: `M1-A-MANIFEST-001`
- Frozen: 2026-09-04
- Planning baseline: commit `51ab372`
- Active work: neutral semantic observation/pass-through
- Status: active development manifest; runtime fixture details are completed in
  each probe run record

## Supported client

- Product: Starfleet Command: Orion Pirates Community Edition
- Executable: `StarFleetOP.exe`
- File version: `2.5.6.4`
- Product version: `1.0z`
- Size: 4,812,800 bytes
- Installed path used for development:
  `C:\Games\Taldren Software Inc\Starfleet Command Orion Pirates\StarFleetOP.exe`
- MD5: `2BE8F713F81B1C68D50EAD6088C32886`
- SHA-256:
  `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`
- Last-write time observed: 2019-06-29 20:09:05 UTC

The controller and component refuse any process whose on-disk image does not
match the MD5. Runtime records repeat both hashes before and after testing.

## Launch and configuration

- Required launcher:
  `C:\Project\SFC-Modernize Engine\Game Assets\SFCLauncher 2.1.0.22.exe`.
- Launcher size: 219,136 bytes; MD5 `5974EA36E3C4E3DFE4F8E243607FC3CF`;
  SHA-256 `84D3A5F89A922C4BEE6815CF0614538C3565C4BDB7DB3AA187C552CB727EF890`.
- Authenticode status: unsigned original restored from the sponsor's source ZIP.
  A briefly re-signed copy was rejected before evidence capture and replaced.
- Game configuration: launcher-created native `StarFleetOP.exe`; no renderer
  replacement is selected by M1.
- M1 component state must be recorded as `disabled`, `enabled`, or `removed`.
- Module inventory is attempted where access permits. Its denial in the first
  disabled attempt does not block semantic gating, client attribution, process
  telemetry, or the later elevated controller; it is deferred unless integration
  evidence shows it is needed.

## Host environment

- OS: Microsoft Windows 11 Home, version `10.0.26200`, build `26200`, x64.
- Physical GPU: NVIDIA GeForce RTX 4070 Ti.
- NVIDIA driver: `32.0.15.9636`, dated 2026-04-22 UTC.
- Other enumerated display adapters:
  - SudoMaker Virtual Display Adapter `1.10.9.289`;
  - Sunshine Virtual Display Driver `1.4.4.0`.
- PowerShell: `7.6.5`.
- Python: `3.14.6`.
- C/C++ toolchain: Microsoft Visual C/C++ `19.51.36248`, x86 target, Visual
  Studio 2026 Community developer environment `18.7.3`.

The active display adapter/output and resolution are recorded per runtime run
because adapter enumeration alone does not establish which output SFC uses.

## Component and dependency baseline

- Component source: `tools/m1_component/m1_component.cpp`.
- Controller source: `tools/m1_component/m1_controller.cpp`.
- Preferred loader: three-export local WINMM forwarder built from the same
  component source and removed after game exit.
- Disabled-baseline scene gate: standalone `m1_gate.dll`, injected by the scoped
  elevated workflow, with one semantic hook restored and the DLL unloaded before
  baseline telemetry begins. It writes nothing to the game directory.
- Shared contract logic: `tools/m1_component/m1_contract.h`.
- Build/runner/analyzer revisions are the working-tree versions associated with
  the runtime run record; implementation changes are not committed without later
  sponsor authority.
- Runtime dependencies: Windows x86 APIs and the static MSVC runtime only.
- No external renderer, helper model, or third-party detour library is used.
- The loader temporarily adds `winmm.dll` and `m1-component.ini` beside the game
  executable only for an enabled run. It refuses to replace existing files and
  verifies/removes exactly those two additions after normal exit.

## Fixtures

- `M1-A-FIXTURE-01`: smallest valid tactical setup, a two-ship skirmish. The
  sponsor confirmed that SFC skirmish cannot be configured with fewer ships.
- `M1-A-FIXTURE-02`: two distinguishable visible ship/model classes with camera
  and object motion plus an enter/leave condition.
- `M1-A-FIXTURE-03`: representative mission for the later 30-minute neutral
  stability run.

Fixtures 02 and 03 are not executed until Fixture 01 is stable. These are
development fixtures, not a new CDD verification-fixture definition.

## Default capture envelope

- automatic tactical gate: first confirmed ship-owner event;
- detailed frames: at most 120;
- detailed events: at most 10,000;
- detailed owners: at most eight;
- event-log warning: 16 MiB;
- event-log hard stop: 32 MiB;
- formal runtime: at most 35 minutes;
- downstream validation: bounded counters and detailed events only inside the
  active burst;
- after saturation: counters continue; detailed records stop;
- raw output: ignored `artifacts/m1/runs/<timestamp>/`.

Unrestricted tracing can grow to multiple gigabytes rapidly and is prohibited.

## Disabled baseline

`M1-A-BASELINE-002` run `20260905-094407-disabled-auto-gate` is the accepted
Fixture-01 disabled baseline. The automatic semantic gate opened on a validated
`tEntityShip::render` owner/visual event, restored and unloaded before telemetry,
and required no sponsor timestamp. The run retained 119 telemetry samples over
119.289 seconds, recorded normal process disappearance, added no game-directory
files, and preserved both client hashes. The sponsor reported normal rendering,
HUD, cursor, targeting, camera movement, and controls with no noted issues.

Paired enabled runs `M1-A-RT-001/002/003` subsequently confirmed neutral semantic
operation, two-owner differentiation, retirement/fresh reappearance, and prior
downstream correlation. The `0x006AB410` diagnostic hook caused a reported
3–5-second initial stutter while processing 32.4 million calls; the same semantic
component without that optional hot hook produced no reported stutter across
3,000 scene epochs. The semantic integration sub-gate is therefore PASS while M1
remains CONTINUES. The geometry hook is diagnostic-only and disabled for routine
semantic operation.

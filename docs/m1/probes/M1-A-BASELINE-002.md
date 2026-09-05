# M1-A-BASELINE-002 — Automatic Tactical Scene Gate and Disabled Baseline

## Runtime question and hypothesis

Can the harness distinguish tactical 3D model rendering from launcher, loading,
and menu activity without a sponsor timestamp, then collect a clean disabled
baseline and reliably observe process exit?

Hypothesis: the first call to `tEntityShip::render` at `0x004162B9` whose `this`
has vtable `0x00796F0C` and whose `+0x88` visual has vtable `0x007985A4` is a
cheap semantic indication that a tactical ship model has entered rendering.

## Evidence basis and confidence before execution

- **CONFIRMED:** M0 static RTTI identifies `0x004162B9` as the ship render owner,
  vtable `0x00796F0C`, visual field `+0x88`, and visual vtable `0x007985A4`.
- **CONFIRMED:** M0-RT-003 correlated two distinct tactical owners through the
  visual/model/mesh chain and downstream rendering.
- **CONFIRMED for the tested fixture:** run `20260905-094407` discovered the game
  at 09:45:31.954 ET and did not gate until 09:45:44.410. The accepted event had
  the exact ship and linked-visual vtables; the sponsor had entered the two-ship
  skirmish. Broader non-tactical screens remain unobserved rather than assumed.
- Plausible false positive: an unobserved non-tactical screen could instantiate
  and render a real `tEntityShip`. If seen, add the smallest adjacent condition;
  do not promote a generic draw signal.

`t3DVisual_Model::render/LOD` (`0x0042FD3F`) and `tModel0::render`
(`0x0042E4B2`) were considered. They are later and may serve non-ship model
owners. `DrawIndexedPrimitive` and `0x006AB410` were rejected as generic signals.

## Tool, version, and exact mechanism

- Probe ID/version: `M1-A-BASELINE-002` / gate component `0.1-gate`.
- Source: `tools/m1_component/m1_component.cpp` with `M1_GATE_ONLY`.
- Build: `tools/m1_component/build_m1_component.ps1`, MSVC x86 `/W4 /WX /O2
  /MT /arch:SSE2`.
- Gate DLL: ignored `artifacts/m1/bin/m1_gate.dll`.
- Controller: `artifacts/m1/bin/m1_controller.exe` with
  `--stop-on-burst 1 --already-loaded 0 --unload-after-stop 1`.
- Runner: `tools/m1_component/run_m1_disabled_baseline.ps1`.
- Entry/elevation wrapper: `tools/m1_component/start_m1_disabled_baseline.ps1`.

The gate DLL validates exact bytes `55 8B EC 83 EC 50`, installs one x86 entry
trampoline at `0x004162B9`, preserves EFLAGS, general registers and FPU/SIMD
state, and validates both vtables before accepting an event. It records one
event in fixed storage, signals completion, becomes inactive, restores the exact
bytes, and unloads. Disabled telemetry begins only after controller confirmation
of restoration and unload. The neutral six-hook component is not enabled.

## Launch, privileges, gate, and stop conditions

1. Ensure no `StarFleetOP.exe` is running.
2. Run the elevation wrapper command in the shared runbook. Approve the one UAC
   transition that replaces normal launcher elevation.
3. The elevated parent verifies both launcher and client hashes, builds, launches
   the restored launcher, discovers exactly one client, and verifies its actual
   process image plus both client hashes.
4. Sponsor selects a normal two-ship skirmish. No timestamp message is required.
5. Automatic gate waits at most 600 seconds for the validated ship event.
6. After hook restoration and DLL unload, record process telemetry for 120
   seconds. Sponsor may play and move the camera normally.
7. Runner requests normal exit and waits at most 600 seconds, classifying
   `exited` or `timeout-running`.

Manual fallback: run with `-GateMode Manual` and create only the run-specific
`manual-scene-gate.signal` printed by the runner after tactical entry. The same
gate and exit timeouts apply.

## Filters, limits, outputs, and volume

- Address filter: only `0x004162B9`.
- Semantic filter: exact ship and linked visual vtables.
- Detailed gate events: one; owners: one; frames: one.
- Gate timeout: 600 seconds; capture: 120 seconds; exit wait: 600 seconds.
- Component warning/hard file limits: 16/32 MiB; fixed event capacity is one for
  this configuration. Expected gate evidence is below 8 KiB and telemetry below
  16 KiB. Total expected output is below 32 KiB plus build transcript.
- Output: ignored `artifacts/m1/runs/<timestamp>-disabled-auto-gate/` containing
  metadata, one gate event, summary/component log, controller output, process
  telemetry, and result. Elevated wrapper transcript is under `artifacts/m1/`.

Unfiltered tracing can create multi-gigabyte output quickly. This probe cannot:
it has one exact address, one accepted record, fixed storage, a 32 MiB hard file
cap, bounded waits, and counters are unnecessary after its one-shot stop.

## Analysis, cleanup, and hazards

Accept the automatic gate only if its semantic event is valid, no earlier menu
false positive is observed, restoration and unload precede telemetry, output is
bounded, client hashes remain exact, and the sponsor reports normal tactical
rendering/controls. Compare gate time, process discovery, telemetry interval and
exit outcome in metadata/result.

The automatic path adds no game-directory files. Generated outputs are ignored
and may be removed after evidence curation. If the game exits before controller
removal, record the failure and do not reuse the run. Do not terminate SFC while
the gate hook is active; exit normally if possible. The controller validates
restored bytes before unloading. No security control is disabled or weakened.

Module enumeration denial is deferred: this probe identifies the actual process
image and hashes it, while the elevated controller obtains the access required
for the one hook. Revisit module inventory only if later integration attribution
requires it.

## First accepted runtime evidence

Run `artifacts/m1/runs/20260905-094407-disabled-auto-gate/`:

- process discovered 09:45:31.954 ET; automatic gate 09:45:44.410;
- one retained `ship_owner` event at `0x004162B9`: ship `0x1CE6A1D8`,
  linked visual `0x1CE62140`, vtables `0x00796F0C` and `0x007985A4`;
- two total ship-hook calls occurred before controller removal, consistent with
  the minimum two-ship fixture; detailed storage remained capped at one;
- exact entry bytes restored and controller independently confirmed them;
- gate DLL unloaded before telemetry began at 09:45:44.726;
- 119 telemetry records through 119.289 seconds; process exit classified
  `exited`; client MD5/SHA-256 unchanged;
- run-directory output 13,489 bytes, including the 546-byte result; 522-byte
  event CSV; no truncation and no game-directory files added.

Automatic gating and bounded cleanup are **CONFIRMED for this fixture**. Visual,
HUD, cursor, targeting, camera movement, and controls were reported normal by
the sponsor with no noted issues. The disabled baseline is accepted.

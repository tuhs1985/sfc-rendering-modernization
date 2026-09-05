# M1 Increment A Experimental Integration Contract

## Contract identity and purpose

- Contract ID: `M1-A-CONTRACT-001`
- Schema: `m1.semantic.v1`
- Status: approved-plan implementation contract; experimental, not a production
  renderer API
- Question: can a reversible project-controlled component occupy the confirmed
  semantic seam and return control to the original renderer without changing
  tactical behavior?

## Selected observation points

| Event | VA | Overwritten complete instructions | Resume VA | Purpose |
|---|---:|---|---:|---|
| scene begin | `0x0069E300` | `53 56 8B F1 57` (5 bytes) | `0x0069E305` | automatic tactical/frame gate |
| ship owner entry | `0x004162B9` | `55 8B EC 83 EC 50` (6 bytes) | `0x004162BF` | explicit `tEntityShip this` and visual field |
| visual-model entry | `0x0042FD3F` | `55 8B EC 83 EC 0C` (6 bytes) | `0x0042FD45` | ship/visual/model-source/LOD identity |
| Model0 entry | `0x0042E4B2` | `55 8B EC 83 EC 38` (6 bytes) | `0x0042E4B8` | selected mesh/source owner and parent return |
| visual-model exit | `0x0042FDD5` | `5F 5E C9 C2 0C 00` (6 bytes) | terminal return | bound mainline owner-to-geometry scope |
| geometry anchor | `0x006AB410` | `83 EC 14 53 8B D9` (6 bytes) | `0x006AB416` | downstream generic-submission correlation |

These bytes are **CONFIRMED** by the exact-build retained dumpbin disassembly
and must match live memory before installation. No hook is installed if any byte
differs. The third-party-free inline detour copies whole instructions into a
trampoline and writes an in-memory relative jump. It never patches the file.

## ABI and state-preservation adjudication

- All targets are 32-bit x86 code in the exact `2.5.6.4` image.
- Entry points use MSVC member-function behavior: `ECX` carries `this`; callee
  stack cleanup is visible at the function returns.
- `t3DVisual_Model` calls `tModel0` through vtable slot `+0x08`; the confirmed
  mainline return address is `0x0042FDD5`.
- At visual entry, preserved `EBX` contains the parent `tEntityShip`; this was
  dynamically correlated in M0 and is corroborated by the static parent path.
- At mainline Model0 entry, preserved `ESI` contains the parent visual model;
  stack arguments provide manager and source identity.
- Hook thunks save and restore EFLAGS, all x86 general registers, and the full
  FXSAVE/FXRSTOR x87/MMX/XMM state before executing the original instructions.
- Trampolines replay the exact overwritten instructions and jump to the first
  untouched instruction. The visual-exit trampoline replays the complete
  epilogue and returns normally.

These ABI conclusions are Codex engineering judgments supported by exact static
instructions plus M0 runtime register/pointer evidence. Runtime non-interference
is still required before promotion to **CONFIRMED** integration behavior.

## Minimum semantic record

Each detailed event contains schema/component version, monotonic sequence,
elapsed time, frame epoch, event kind, thread ID, origin and return address,
captured register identities, per-process opaque owner ID, ship/visual/Model0
pointers, vtables, source, selected LOD fields, manager, and whether a geometry
event occurred inside a confirmed mainline owner scope.

Raw pointers are evidence for one process only. They are not serialized as stable
cross-launch identities.

## Identity and lifetime rules

1. A valid ship association requires the expected `tEntityShip` and
   `t3DVisual_Model` vtables plus matching ship `+0x88` visual pointer where
   readable.
2. The first valid pointer observation receives a monotonically increasing
   per-process opaque owner ID.
3. An owner not observed for two completed tactical frames is retired.
4. Reappearance of a retired raw pointer starts a new identity epoch and receives
   a new opaque ID. This intentionally avoids assuming pointer continuity.
5. At most eight raw owners are detailed. Additional owners increment an overflow
   counter without expanding the table or blocking rendering.
6. A Model0 event is mainline-associated only when its return address is
   `0x0042FDD5` and its visual parent matches a live owner association.
7. Geometry is owner-associated only while that thread has an active confirmed
   mainline Model0 scope. The visual-exit hook clears the scope.
8. Model0 calls returning to `0x00509843` are counted as the known exception and
   are not assigned to the last ship by temporal guess.

## Capture and correlation behavior

The first valid ship-owner event activates the tactical gate. Scene-begin events
then advance the bounded frame epoch. Detailed capture ends at 120 frames or
10,000 events, whichever comes first. Total per-event-kind and correlated versus
uncorrelated geometry counters continue until removal.

The downstream claim is correlation, not one draw per owner: a detailed geometry
event records the active semantic chain and `0x006AB410` caller/arguments; summary
counters show continued downstream activity after detailed saturation.

## Fail-open and bounds

- Recording uses a fixed-capacity in-process buffer; no hook performs file I/O.
- If the buffer, owner table, or file-size envelope saturates, detailed evidence
  stops and original rendering continues.
- Invalid/unreadable semantic pointers increment rejection counters under guarded
  reads; they do not abort the renderer.
- Output is written only during controlled stop/removal.
- The component log refuses to write past 32 MiB and marks truncation.
- Hook handlers do not wait on a writer or external consumer.

## Installation, removal, and rollback

The preferred launch path places a temporary three-export `winmm.dll` forwarder
beside the client before launch. SFC already imports only `timeGetTime`,
`timeKillEvent`, and `timeSetEvent`; the proxy forwards those calls to the exact
32-bit system WINMM. On the first forwarded call it launches the controller as a
child of the already-elevated game, so the controller inherits the token created
by the normal launcher UAC and causes no second prompt. The controller finds the
already-loaded component and calls its exported start routine. An already-elevated
analyst shell may instead use direct `LoadLibraryW` injection.

The DLL suspends other target threads only for the bounded patch transaction,
validates all bytes, installs all hooks, and resumes them.

Removal sets the component inert, waits for active recorders to leave, restores
all original bytes under the same bounded thread suspension, flushes evidence,
and verifies restored memory. The inert DLL remains loaded until normal process
exit to avoid an unload race with a just-departed hook thunk. `removed` therefore
means absent from the semantic path, not forcibly unmapped.

After normal exit the runner removes only the temporary proxy and configuration;
it refuses to overwrite any pre-existing `winmm.dll`. On partial installation
failure, already-installed hooks are restored before the
start call fails. On controller loss, the game retains the loaded component; the
documented emergency procedure is to exit SFC normally, which discards all
in-memory changes. Do not terminate the controller while hooks are active.

## Confidence at definition time

- Hook addresses, bytes, vtables, and M0 chain: **CONFIRMED**.
- Calling convention/register roles: **STRONG HYPOTHESIS**, corroborated by exact
  disassembly and M0 runtime context.
- Inline pass-through safety and acceptable cost: **SPECULATIVE** until M1-A
  runtime evidence.

# LIVE-BRIDGE-001 — one qualified ship, separate live Remix window

Status: first live connection CONFIRMED; full acceptance remains PARTIAL.
Actual20261016-211253/component0.18:1851 viewer updates from verified ship,
89.937s, zero rejected/mismatch; native-to-USD matrices compare exactly, clean
exit/hooks/client hash. Sponsor confirms working but ship leaves fixed view and
view buttons mislabel orientation; nonblocking to feasibility, not repaired.
Camera independence and live retirement/reappearance NOT isolated/proven.
[Runtime record](../../runs/2026-10-16-codex-live-bridge-runtime.md).
Authority: sponsor-approved Live Bridge plan, 2026-10-16. No game-camera match,
picture reinsertion, renderer replacement, appearance tuning or milestone claim.

## Evidence checkpoint / ABI

Existing wrapper006AC5A0, mainline return0042E55D, validated owner/model scope.
No new hook/calling convention. Existing stubs preserve state unchanged. Ship
vtable00796F0C+6C resolves00419DD2;00416318 calls it with0,00416323 hands result
to manager+E4/006AA550. Getter builds ship-local cached transform+9C4 using
00413B34, ship rotation fields+92A/+92E/+980 and translation+E6/+EA/+EE.
006AA55D–570 copies17words to manager+6F4 BEFORE composing manager+628/+5E4
into+66C/+6B0 at006AA57C/58F. Scalar0069CA30 maps rows00/10/20 plus
translation0C/1C/2C. Source exact-build dump and original PE corroboration required.
Supplied ship transform rather than composed camera state: STRONG HYPOTHESIS;
runtime movement/camera independence still requires corroboration. Do not label
arbitrary native17words as standard4x4; word16 metadata not a float.

## Mechanism and interface

Default-off LiveChannel setting requires exclusive read-only mesh+texture mode,
geometry/interventions OFF. Creator allocates2MiB Local session mapping with
current-user-only DACL, unique UUID name, protocol version/session header checked
by all parties. No network/socket/listener or globally relaxed security controls.
Existing hook publishes fixed transform records through a nonwaiting mailbox at
<=30Hz; two immutable asset epochs maximum. Worker serializes assets and writes
shared-memory seqlock records, bounded JSONL evidence; render callback does no I/O,
allocation or wait. Receiver skips old records, never backpressures SFC.

Assets: only fresh validated kff.mod452poly mesh and ten registry-named images;
compare content/group/UV/normal records and image SHA against accepted textured
job, not live resource IDs. Original packet/reference evidence written separately
with hooks_restored=false during operation; final cleanup evidence independent.
No active snapshot is relabelled as post-cleanup evidence. Max two fresh epochs;
additional retirement/reappearance stays hidden and is reported partial.

Each record: session via mapping header, sequence, owner epoch, frame, elapsed,
active/retired state, model/source,17 supplied+17 composed words, dispatch words,
asset slot. Nonfinite/malformed data rejected. Hide after1s without fresh update,
explicit retirement, unqualified model/LOD or disconnect. Fresh asset qualification
required on reappearance. Translation relative first accepted origin; row-vector
USD matrix is transpose of explicit native column-vector affine map. No axis,
normal/winding/UV edit. Synthetic fixed camera with Frame ship control.

## Launch, limits and cleanup

Prepared start_live_bridge_session.ps1 from existing elevated parent; PS5 delegates
to bundledPS7.6.5; VS2026/MSVC14.51 x86 build/tests, Python3.12/Pillow, existing
Toolkit1.6.0-dev isolated process. Process-only execution-policy bypass, no routine
new UAC. Sponsor enters two-ship skirmish, initially holds still, observes selected
ship motion/turn, briefly moves game camera, exits normally on request. Enemy
selection permitted; never ask sponsor to move an enemy or inspect pointers.

90s tactical/<=2700 movement records,2MiB channel (<4MiB),8MiB bridge evidence;
existing120frames/10000events/eightowners/16MiB warning/32MiB log stop. Ten image
resources <=4096square,64MiB warning/128MiB image cap. Worker asset cap512KiB per
epoch; no per-frame geometry/images/screenshots. Viewer startup180s,total300s;
no uncontrolled multi-GB mechanism. Deadline closes owned preview; never kills
game/controller while hooks may remain; overrun parked explicitly pending cleanup.

Outputs: artifacts/live-bridge/<session>, existing M1 run directory, isolated
preview scratch; protocol/configuration, asset verification, <=2700 updates,
disconnect/counter summary and existing client/hash/hook restoration evidence.
On stop drain recorders, stop/join worker before unmap; worker timeout fails stop
without unloading live storage. Runner removes only owned proxy/config; originals
unchanged. Retain useful evidence ZIP, no caches/originals deletion. No commit.

## Analysis/acceptance

Native tests: bounded publication, worker stop, stale epoch/retirement, config.
Python tests: actual Windows transport, torn/malformed/slow/disconnected streams,
asset mismatch, epoch/pointer reuse, affine conversion, deterministic viewer replay.
Runtime: correctly textured selected ship updates repeatedly, movement/turn
correspond, camera motion does not masquerade as ship motion, no stale identity,
normal tactical operation, clean exit/restoration/client unchanged, bounded output.
Any missing element -> PARTIAL, never automatic gate PASS. No fidelity tuning.

## Offline result — 2026-10-16

Full native build/contracts/exports PASS;89 project Python/41 preview+IPC tests
PASS, mesh/texture PowerShell policy tests/parser checks PASS. Restricted sandbox
cannot reopen the user-only channel (Win32 access denied); host-context tests PASS
without weakening its ACL. Deterministic real-Kit replay accepted119 updates,
zero rejected/asset failures, two fresh qualified epochs, one hide transition,
matrix authored-value readback matched; exit0/no owned processes. This replay
does not prove actual ship movement/camera independence in SFC.
Final preparation/report: [run record](../../runs/2026-10-16-codex-live-bridge-preparation.md).
Byte layout, conversion/import scale and exact limits:
[experimental contract](../live-bridge-contract.md).

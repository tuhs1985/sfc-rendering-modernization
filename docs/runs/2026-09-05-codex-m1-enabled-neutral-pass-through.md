# Codex Run Record — M1 enabled neutral semantic pass-through

## Identity and scope

- Run ID/date: `CODEX-20260905-M1-ENABLED-NEUTRAL`, 2026-09-05.
- Active work: M1 Increment A, `M1-A-RT-001` neutral semantic pass-through.
- Starting commit/state: `4119d84`, clean.
- Question: can the project-controlled component occupy the confirmed semantic
  owner/model seam in the accepted two-ship fixture while preserving the
  original renderer and gameplay behavior?
- Non-scope retained: no CTE-2/CTE-3 modernization, renderer selection, helper
  use, broad reverse engineering, staging, or commit.

## Baseline and reviewed authority

Used the approved M1 plan, `M1-A-CONTRACT-001`, `M1-A-RT-001`, the component
runbook, and accepted disabled run `20260905-094407-disabled-auto-gate` (13,489
bytes total, normal behavior/exit, unchanged client, automatic ship gate).

Reviewed the six exact hook sequences, x86 member-call register assumptions,
whole-instruction trampolines, EFLAGS/general-register/FXSAVE preservation,
guarded reads, fixed buffers, fail-open behavior, and verified restoration.

## Tools, configuration, and validation

- Component/controller: `SFC-M1-A-COMPONENT 0.1`, schema `m1.semantic.v1`.
- Limits: 300 seconds, 120 frames, 10,000 detailed events, eight owners,
  16 MiB warning, 32 MiB hard event-log stop, stop on burst.
- Built with MSVC x86 `/W4 /WX /O2 /MT /arch:SSE2` through
  `build_m1_component.ps1`.
- C++ contract and WINMM forwarding tests passed. Python M1/M0 analyzer
  regressions and process-image/exit regression passed. PowerShell parsing and
  `git diff --check` passed before runtime.

The preferred proxy preparation stopped before launch when ordinary access was
denied while creating the local `winmm.dll`. No game file was created or
modified. The scoped elevated-parent fallback `start_m1_enabled_session.ps1`
verifies the launcher, waits for a bounded workspace-local tactical-arm signal,
then invokes direct injection against the discovered PID. The automatic
component gate remains active after injection.

## Runtime attempts and evidence

`20260905-095959-enabled` safely installed/restored the component and the sponsor
reported normal gameplay, but it armed at process startup and saturated before
the sponsor's announced tactical-entry time. It is rejected as the paired
tactical fixture and retained only as pre-tactical safety evidence.

Accepted run: `artifacts/m1/runs/20260905-100432-enabled`. The sponsor reported
two-ship tactical entry before the arm signal. The component then captured:

- two distinct ship owners: `0x1D05A1D8` and `0x1E498C90`;
- distinct visuals: `0x1D052140` and `0x1235BE58`;
- distinct Model0/selected-child identities: `0x1E3EC464` and `0x1E3EC0E0`;
- distinct sources: `0x0493365C` and `0x12355EB8`;
- shared graphics-manager handoff `0x04990038`;
- 12,632 owner-correlated and 156 uncorrelated `0x006AB410` events;
- two occurrences of the known `0x00509843` exception.

No semantic rejection, vtable mismatch, owner/thread overflow, or log truncation
occurred. The 10,000-event detail cap stopped capture after one completed frame;
the event CSV was 2,589,069 bytes and all run files totaled 2,606,146 bytes.
This was below both size thresholds. All six hooks were restored by the
component and independently verified by the controller. No game-directory proxy
or configuration remained. The sponsor reported no rendering, HUD, cursor,
targeting, camera, movement, or control issue. The selected process exited
normally and was classified `exited`.

Client after the run remained MD5 `2BE8F713F81B1C68D50EAD6088C32886`
and SHA-256
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.

## Adjudication

**CONFIRMED for the accepted two-ship fixture:** component occupation of the
semantic seam; two-owner differentiation; coherent owner/visual/Model0/source/
selected-child handoff; downstream `0x006AB410` correlation; original-path
continuation; bounded output; exact-byte restoration; normal exit; client
preservation; and sponsor-observed non-interference.

**Unresolved:** the safety-first detail bound saturated too quickly to observe
motion over multiple frames or owner retirement/reappearance. A later bounded
probe must reduce detailed geometry volume (sampling/counters) so lifetime can
be observed without increasing the established file limits. The known exception
remained finite (two calls) and did not invalidate this mainline result.

Decision: **M1 CONTINUES — additional bounded evidence required**. The next M1
step is a multi-frame/lifetime-focused semantic run, not visual modernization.

The sponsor subsequently authorized an absolute 10 GB temporary-output ceiling,
with raw data compressed or removed after analysis. This is a storage ceiling,
not a default capture allocation; probe-specific event/file limits remain and
the next probe should prefer sampling/counters over higher output volume.

## Files and repository state

Created `tools/m1_component/start_m1_enabled_session.ps1` and this run record;
updated `M1-A-RT-001.md` and the component runbook. Raw runs and binaries remain
ignored. No files were staged or committed. Final Git state is recorded after
validation.

Final validation passed all component PowerShell parser checks, the bounded
process-image/exit regression, both Python analyzer regressions, and
`git diff --check`. Exact client hashes matched; no game-directory `winmm.dll`
or `m1-component.ini` and no tactical-arm signal remained. Relative to
`4119d84`, two probe documents are modified and this record plus the enabled
wrapper are untracked; nothing is staged or committed.

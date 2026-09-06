# Codex Run Record — M1 semantic-component stutter attribution

## Identity and scope

- Run ID/date: `CODEX-20260906-M1-STUTTER-ATTRIBUTION`, 2026-09-06.
- Starting commit: `0334867`; expected unstaged M1-05 and helper-IOC work was
  preserved, with nothing staged.
- Active probe: `M1-A-RT-003`.
- Question: does the prior 3–5-second stutter remain when the downstream
  `0x006AB410` hook is omitted but all semantic/lifetime hooks remain active?
- Non-scope: no hook-architecture redesign, visual modernization, renderer
  selection, broad reverse engineering, helper invocation, staging, or commit.

## Implementation and validation

Added a configuration-controlled `EnableGeometryHook` option. The disabled mode
skips preparation/installation of only the geometry hook; the controller still
verifies that address with the other original byte sequences after removal.
Runners expose `-DisableGeometryHook` and record the mode in metadata/summary.

Probe bounds: 60 seconds, 3,000 scene epochs, 50,000 events, eight owners,
16/32 MiB warning/hard event-log limits. Offline MSVC x86 build, C++ contract and
WINMM forwarding tests, three Python analyzer regressions, process image/exit
test, PowerShell parsing, and `git diff --check` passed before runtime.

## Runtime result

- Evidence run: `20260906-155210-enabled`.
- Approximate active window: 28 seconds / 3,000 scene epochs.
- Geometry hook: disabled and never invoked; `0x006AB410` remained original.
- Two coherent owner chains spanned frames 0–2,999 with stable ship, visual,
  Model0, and source identities.
- Retained events: 29,998; event CSV: 7,815,321 bytes; total: 7,835,834 bytes.
- No semantic rejection, vtable mismatch, overflow, retirement, or truncation.
- Known exception: 3,001 finite/unassigned events, about one per epoch.
- Component restoration and controller byte verification passed.
- Sponsor observation: no initial or steady-state stutter and no other noted
  rendering/control issue.
- Exit: `exited`; exact client MD5/SHA-256 unchanged; no residual loader,
  configuration, or arm-signal file.

## Adjudication

The only material difference from the stuttering `M1-A-RT-002` path was omission
of the downstream hook that previously processed 32,409,660 calls. Its absence
removed the reported stutter while semantic activation/observation remained.
Therefore hot downstream diagnostic-hook overhead is a **STRONG HYPOTHESIS** for
the transient stutter. Frame-time magnitude is not directly measured, so the
claim is not promoted to CONFIRMED causation.

Combined evidence now satisfies the semantic integration sub-gate: the practical
semantic component operates neutrally; the downstream anchor correlation was
already confirmed separately; owner lifetime and reappearance are confirmed;
and the intrusive validation hook is not required in routine semantic operation.
Decision: **M1 CONTINUES — SEMANTIC INTEGRATION SUB-GATE PASS**. This is not
formal TRL 4 PASS and does not authorize CTE-2/CTE-3 implementation.

## Repository and evidence state

Raw output is compressed after analysis under the established 10 GB ceiling.
Archive path/hash, cleanup confirmation, final validation, and Git state are
appended after completion. No changes are staged or committed.

Final archive:
`artifacts/m1/archives/20260906-155210-enabled.zip`, 206,732 bytes, 12 entries,
SHA-256 `3162B63D6CE7FD87E874203A662A2EE598BC6C9D68B91BB880DFEA4E51494507`.
The archive was opened and checked for its event CSV and summary before the exact
7,835,834-byte raw run directory was removed.

Final validation retained the successful x86 build, C++ contract and proxy
tests, three Python analyzer tests, process image/exit test, PowerShell parser
checks, and `git diff --check`. Exact client hashes matched; no loader,
configuration, or arm signal remained. Git contains only the expected unstaged
M1 source/test/documentation changes, including the separately recorded helper
IOC test; nothing is staged or committed.

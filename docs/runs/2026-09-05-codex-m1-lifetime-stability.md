# Codex Run Record — M1 sampled lifetime and stability proof

## Identity and scope

- Run ID/date: `CODEX-20260905-M1-LIFETIME-STABILITY`, 2026-09-05.
- Active package/probe: M1-05 / `M1-A-RT-002`.
- Starting state: clean commit `0334867`.
- Question: can sampled downstream evidence preserve multi-frame owner/model/
  source/lifetime correlation during motion and disappear/reappear conditions?
- Explicit exclusions: no visual modernization, renderer selection, helper use,
  broad reverse engineering, staging, or commit.

## Implementation and validation

Component 0.2 counts every `0x006AB410` event but retains only one correlated
sample per owner per scene epoch and one uncorrelated sample per epoch. Semantic
and retirement events remain detailed. The reviewed run envelope was 6,000
epochs, 100,000 events, eight owners, 90 seconds, 16 MiB warning and 32 MiB hard
event-log stop. This remains far below the sponsor's 10 GB temporary ceiling.

Modified the component, contract helper/test, analyzer, direct runner, elevated
session wrapper, runbook, and probe definition. Offline MSVC x86 `/W4 /WX /O2
/MT /arch:SSE2` builds passed. C++ contract/proxy tests, Python analyzer
regressions, process image/exit test, PowerShell parsers, and `git diff --check`
passed before runtime.

## Runtime evidence

- Run: `20260905-101749-enabled`.
- Observation: about 56 seconds / 6,000 scene epochs.
- Complete geometry counters: 31,895,686 correlated; 513,974 uncorrelated;
  32,409,660 total.
- Retained geometry samples: 6,000 correlated; 6,001 uncorrelated.
- Retained events: 66,355; CSV 17,393,499 bytes; total run 17,417,214 bytes.
- Owner epochs: four from two raw ship pointers; three retirements; both pointers
  reappeared under fresh opaque IDs.
- Each epoch retained exactly one ship, visual, Model0, and source identity.
- No cross-association, mismatch, semantic rejection, overflow, or truncation.
- `0x00509843`: 6,001 finite, unassigned events, approximately one per epoch.
- Hooks restored by component and independently verified by controller.
- Exit outcome `exited`; client MD5/SHA-256 unchanged; no residual game files.

Sponsor actions included two-ship visibility, movement/camera change, temporary
off-screen framing and return. The sponsor reported one 3–5-second microstutter
near the beginning and no other rendering, HUD, cursor, targeting, camera,
movement, or control issue.

## Adjudication

Owner stability, retirement, fresh-epoch reappearance, semantic coherence, and
sampled downstream correlation are **CONFIRMED**. Stable association during
motion is confirmed; a decoded numeric transform snapshot remains outside the
evidence and is not claimed. The exception path is systematic but finite and did
not invalidate the mainline seam.

The microstutter prevents confirmation of enabled/disabled behavioral
equivalence. Component overhead is a **STRONG HYPOTHESIS**, supported by 32.4
million hot-path hook entries, but baseline tactical-entry loading remains a
credible alternative. Result: **M1 CONTINUES — additional bounded evidence
required**. Recommended next step: a narrowly scoped stutter-attribution/hot-path
cost reduction increment using atomic or windowed correlation, followed by one
paired validation run. Do not begin CTE-2/CTE-3 work.

A post-run reporting defect was corrected: synthetic retirement events were in
the CSV but did not increment the JSON summary's event-kind counter. The analyzer
used the three retained events, so the runtime conclusion is unaffected.

## Repository and raw-output state

No files are staged or committed. Raw runtime output is compressed after final
analysis and the exact archive path, validation, cleanup, tests, hashes, and
final Git state are appended below.

Final archive:
`artifacts/m1/archives/20260905-101749-enabled.zip`, 452,688 bytes, 12 entries,
SHA-256 `E74996A4435C00A4654B229B888B05D992ED5202DB94CBB7394B6373A90D7EF1`.
The archive was opened and checked for the event CSV and summary before the exact
17,417,214-byte source run directory was removed. Raw artifacts remain ignored.

Final validation repeated the full x86 build, C++ contract and proxy-forwarding
tests, both Python analyzer regressions, process image/exit regression,
PowerShell parser checks, and `git diff --check`; all passed. The installed client
retained the exact approved MD5/SHA-256. No game-directory proxy/configuration or
tactical-arm signal remained. The repository contains only the expected
unstaged M1-05 source, test, runner, analyzer, probe/runbook, and run-record
changes; nothing is staged or committed.

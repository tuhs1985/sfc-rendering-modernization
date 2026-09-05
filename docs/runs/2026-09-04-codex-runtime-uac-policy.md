# Codex Run Record — Runtime Privilege/UAC Policy Update

## Run identity

- Run ID: `CODEX-20260904-RUNTIME-PRIV-001`
- Date: 2026-09-04
- Active milestone/task: post-M0 runtime-tooling policy hardening
- Starting baseline: commit `38d57fd5889b2f641e8a396d7c1d66bd90c6759b`
- Result: complete

## Technical question

How should routine runtime probes receive the privilege needed to debug the
launcher-created client without making the sponsor approve administrative
dialogs or weakening Windows security?

## Change and rationale

Routine runs now require a narrowly scoped, already-elevated PowerShell parent
session prepared before sponsor gameplay. The runner checks parent elevation
and launches the native probe by inherited privilege, avoiding a per-run
`runas` request. It stops with a clear preparation message when invoked from
an ordinary shell.

`-ElevateProbe` remains an explicit fallback for recovery and historical
reproduction; it is not the routine sponsor workflow. The documentation
prohibits disabling UAC, weakening global consent policy, broad auto-elevation,
or persistent administrative grants.

## Tools, commands, and files

- Inspected privilege and launch behavior with `rg` and PowerShell
  `Get-Content`.
- Updated `tools/m0_probe/run_probe.ps1`.
- Updated `docs/m0/probes/m0-probe-capture-runbook.md`.
- Updated `docs/m0/probes/M0-RT-002.md` and `M0-RT-003.md`.
- Historical M0 run records were not rewritten; they continue to describe the
  actual UAC prompts observed during those completed runs.

No runtime probe was executed and no evidence capture was generated. This
change affects launch administration only; address filters, hit/time/file
limits, evidence fields, cleanup, and client validation are unchanged.

## Result and confidence

- **CONFIRMED:** routine runner logic uses inherited elevation when its parent
  is elevated and does not request `runas`.
- **CONFIRMED:** an ordinary parent stops before waiting for or attaching to
  the client unless the explicit fallback is selected.
- **CONFIRMED:** sponsor procedures now contain gameplay actions only.
- Unresolved blockers: none.

## Repository state

- Files modified: runner, shared runbook, M0-RT-002, M0-RT-003, and this record.
- Raw captures, client files, and reference originals were not modified.
- Nothing was staged or committed during this run.

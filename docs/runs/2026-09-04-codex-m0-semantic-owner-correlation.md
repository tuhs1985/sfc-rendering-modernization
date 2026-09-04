# Codex Run Record — M0 Semantic Render-Owner Correlation

## Run identity

- Run ID: `CODEX-20260904-M0-002`
- Date: 2026-09-04
- Active milestone/task: M0 / TRL 3 Critical Function Proof — semantic render-owner correlation
- Result: **PASS**
- Decision: **M1 JUSTIFIED — TRL 3 semantic seam proven sufficiently to plan integrated validation.**

## Technical question and starting baseline

Question: what stable engine-side owner or ownership chain feeds confirmed generic
submission function `0x006AB410`, and how far upstream do useful ship, model,
mesh/LOD, source, and transform semantics survive?

The starting baseline was the prior M0 PARTIAL result. It had confirmed the
graphics-manager path through `0x006AB410`, `0x006AB380`, native
`IDirect3DDevice3::DrawIndexedPrimitive`, scene completion, and presentation,
but had shown that the arguments crossing `0x006AB410` were generic and no
longer carried ship, model, or material identity.

## Sources and tools

- Existing Pre-M0 subsystem/function maps, normalized landmarks, RTTI, imports,
  and exact-build static evidence.
- Prior M0 report and M0-RT-001 evidence.
- `tools/m0_probe/m0_probe.cpp`, probe version 0.4.
- `tools/m0_probe/build_probe.ps1` and `tools/m0_probe/run_probe.ps1`.
- `tools/m0_probe/analyze_probe_log.py`.
- Microsoft Visual Studio 2026 18.7.3 x86 toolchain; Python 3.14.6.
- SFCLauncher 2.1.0.22 and exact SFC OP client 2.5.6.4.

Material parameters were `-ProbeProfile m0-rt-002` and
`-ProbeProfile m0-rt-003`, with launcher-aware waiting, elevation for the
probe, exact-image and original-byte checks, one tactical reproduction, and
normal process-exit stop. Probe definitions contain the complete commands,
addresses, UAC behavior, cleanup, and analysis procedures.

## Runtime probes and capture limits

### M0-RT-002

- Question: which stable model/mesh owner feeds the manager polygon path?
- Limits: 5,212 total accepted samples, 180 seconds, exact-address filters,
  independent hit caps, expected under 1.5 MB, hard operating safeguard 2 MB.
- Run: `artifacts/pre-m0/runs/20260904-103417`.
- Result: 5,212 samples in 84.734 seconds; `stop_reason=process_exit`.
- Raw CSV: 1,155,344 bytes.
- Evidence: three stable `tModel0`-like owners, source calls reached only from
  `0x0042E527` and `0x0042E534`, and polygon calls reached through
  `0x006AC6D6` and `0x006AC71F`.

### M0-RT-003

- Question: can distinct ship owners be correlated through visual-model and
  mesh/LOD ownership into the confirmed generic submission path?
- Limits: 6,364 total accepted samples, 120 seconds, exact-address filters,
  independent hit caps, expected under 1.6 MB, hard operating safeguard 2 MB.
- Run: `artifacts/pre-m0/runs/20260904-104217`.
- Result: 6,364 samples in 64.718 seconds; `stop_reason=process_exit`.
- Raw CSV: 1,412,572 bytes.
- Executed probe SHA-256:
  `AB1E590C3256C0C19875EF4527888D56CE48F790E30235E2F60511BA805135AC`.
- Post-run rebuilt/smoke-tested v0.4 SHA-256:
  `41ECA78CFA561981E90EB9B6B0A137EC2EA48C531C6F233B3CF4325BAC407946`.
- Evidence: two distinct stable `tEntityShip -> t3DVisual_Model -> tModel0`
  chains converged through manager `0x04980038` into 1,500 generic submissions,
  1,000 batch flushes, and 1,000 native indexed-draw call sites.

Both captures remained below their 2 MB safeguard. Removing hit caps or using
an unbounded per-frame, instruction, or API trace can create multi-GB output
rapidly and is not an approved operating mode. Safe operation requires exact
address filters, independent saturation, duration and file-size limits, and one
bounded tactical reproduction.

## Files created or modified

- Updated `tools/m0_probe/m0_probe.cpp`, `run_probe.ps1`, and
  `analyze_probe_log.py` for the bounded owner and semantic profiles.
- Created `docs/m0/probes/M0-RT-002.md` and `M0-RT-003.md`.
- Updated `docs/m0/probes/m0-probe-capture-runbook.md`.
- Created `docs/m0/m0-semantic-ownership-map.md` and
  `docs/m0/m0-semantic-function-map.csv`.
- Updated `docs/m0/m0-trl3-critical-function-proof.md`.
- Generated ignored raw logs, module lists, JSON summaries, and evidence
  packets beneath the two run directories above.
- Created this run record.

## Evidence adjudication

Static RTTI and vtable evidence identifies `tEntityShip`, `t3DVisual_Model`,
and `tModel0`. Static field access and virtual-call reconstruction show the
ship visual pointer at `+0x88`, model source at `+0x158`, LOD selection and
child array, and the mesh/source handoff to the graphics manager. Runtime
pointer identity independently corroborates two stable, distinct ship/model/
mesh chains and their convergence into the already confirmed low-level path.

Result: the composite semantic seam is **CONFIRMED** for class identity,
stable runtime ownership, call relationships, source identity, and downstream
convergence. Exact material-object layout and the full non-ship exception
taxonomy remain open.

Rejected or bounded hypotheses:

- `0x006AB410` itself is not a semantic seam; it remains the downstream anchor.
- Manager source state alone is not a ship owner; it retains source/count
  identity after the parent relationship has fallen away.
- A third `tModel0` path returning to `0x00509843` was not labeled as a ship;
  it is recorded as a finite, unclassified exception.
- The run distinguishes two ship owners but does not assign player versus
  target identity; that assignment is not necessary for the TRL 3 proof.

## Unresolved questions

- Exact material and texture-owner structures between `tModel0` and manager
  state.
- Classification of the finite non-ship `tModel0` entry and other effect/UI
  owners.
- Direct player/target labeling for the two observed ship pointers.
- Detailed transform layout and the precise loss point for individual material
  groups.

These affect integrated validation scope, not the existence or usefulness of
the demonstrated semantic ship/model/mesh seam.

## Repository state

- Exact client files and reference originals were not modified.
- Client MD5: `2BE8F713F81B1C68D50EAD6088C32886`.
- Client SHA-256:
  `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
- No files were staged.
- No commit was created.
- Generated bulk evidence remains ignored; curated documentation and tooling
  remain versionable for sponsor review.

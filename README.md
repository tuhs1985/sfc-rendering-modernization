# SFC Orion Pirates Rendering Modernization

This repository is the controlled engineering workspace for technical discovery
and, after requirements review, possible rendering modernization of *Starfleet
Command II: Orion Pirates Community Edition*.

The governing capability requirements are the approved *Starfleet Command
Rendering Modernization Capability Requirements* v1.0 (approved 2026-09-03).
Existing wrappers, patching techniques, and community tools remain evidence and
candidate approaches—not requirements or architecture decisions.

## Preservation boundary

- `Game Assets/` is a working game installation. Initial investigation is
  read-only.
- `References/` contains archival/original-source artifacts. Preserve it
  unchanged.
- Both directories are intentionally excluded from Git.
- Generated captures, dumps, extracted files, and tool databases belong under
  ignored local work areas such as `artifacts/`, `analysis/`, or `captures/`.

Start with [the first-pass project report](docs/reconnaissance/project-reconnaissance.md)
and the [bounded Pre-M0 engine report](docs/reconnaissance/pre-m0-engine-reconnaissance.md).

## Controlled workspace

- `docs/reconnaissance/` — evidence-backed discovery reports.
- `docs/decisions/` — future reviewed decision records; none are implied yet.
- `tools/recon/` — small, read-only inspection helpers.
- `src/` — reserved for implementation after requirements and architecture review.
- `tests/` — reserved for repeatable verification assets that can legally be tracked.
- `artifacts/` — local generated evidence; ignored except for its policy file.

No files have been staged or committed by the initial reconnaissance pass.

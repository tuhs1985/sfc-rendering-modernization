# Staged repository migration

The [repository map](REPOSITORY_MAP.md) describes current ownership. This roadmap
orders later work; it is not permission to relocate code or delete evidence.
Follow the [contributor workflow](../CONTRIBUTING.md) and create a separate scoped
change for each affected component.

Organization also covers the [external project-workspace inventory](REPOSITORY_MAP.md#project-workspace-outside-this-repository):
game copies, publishing clone, backups, Remix jobs and vendor archives under
`C:\Project`. They are not additional Git branches and are not rolled back with
source. Future consolidation must account for their active path consumers,
unique settings/source, recovery state and provenance. No move/deletion is
included in this foundation; unrelated projects in the parent folder remain out
of scope.

## Baseline already secured

`35fda1b` records production separation and the profiling-independent startup
correction. `fe17b8d` records OpenSpec and this foundation's plan. GitHub `master`
was verified at `fe17b8d` before the sponsor-authorized creation of
`codex/organize-repository-foundation` on November 9, 2026. There is no need to
merge divergent local `master` or recreate the earlier checkpoints.

Those commits preserve the working source baseline. The private alpha remains a
qualified local test copy with separate manifests/settings; it is not a public
ZIP. A documentation branch does not upgrade its release-readiness status.

## Phases and exit evidence

| Phase | Deliverable | Required evidence / boundary |
| --- | --- | --- |
| 0. Foundation, this change | Contributor conventions, current map, documentation ownership and this roadmap | Links/classification/strict OpenSpec checks; unchanged source/package inputs. No source moves |
| 1. Checkpoint the foundation | Focused reviewed documentation commit; integrate when explicitly requested | Inspect changed/staged paths and exclude unrelated files. This roadmap does not authorize commit, push or merge |
| 2. Separate release tooling | A later change maps build-time tools versus the portable runtime/bootstrap boundary and proposes exact destinations | Review consumers of `bootstrap.py`, `session_recording.py`, `runtime_context.py`, launcher sources and release builders; do not move an entire folder by name |
| 3. Relocate one production component | Later component-specific changes move source and update consumers together | Focused native/Python and actual affected package/process checks; equivalent behavior and rollback |
| 4. Improve historical navigation | Indexes and supersession links; physical evidence moves only if justified | Verify provenance and links; dated conclusions remain intact, useful raw inputs remain available |

**Recommended next change:** scope `separate-release-tooling` around the portable
entry point and its build-time/runtime split. `tools/release/` has 20 tracked
files at the baseline, but only two of its Python modules are shipped. This is a
smaller boundary than relocating the coordinator, asset pipeline and GPU adapter
at once. Exact source/destination paths and compatibility entry points belong in
that change's design before moves begin; no wholesale new source layout is
prescribed here.

The runtime/shared protocols, observer/controller, D3D9 adapter/receiver and
appearance/preparation modules are later candidates. Choose one by dependency
ownership, not by how old its folder looks. Do not combine their relocation with
new rendering behavior, D3D12 work, appearance tuning or vendor pruning.

## Checklist for each later source migration

Before writing code:

1. Identify the exact accepted source/commit and supported runtime configuration.
   Preserve any unrelated working files; do not use a reset to obtain cleanliness.
2. List source/destination paths, direct and dynamic imports, native includes,
   exports/defines, entry points, subprocess invocations and current directory
   assumptions. Distinguish neutral data contracts from Remix conversions.
3. Identify affected build scripts, generated outputs, source-hash qualifications,
   the production module allowlist, release staging/recipes and installed roles.
   A stale source qualification is a finding to resolve through its documented
   process, not a check to disable merely because a file moved.
4. Define whether old launch/import paths need compatibility shims. Keep a shim
   only for a documented consumer, not indefinitely for hypothetical use.
5. Select verification and rollback for that boundary; record what requires a
   sponsor gameplay checkout and what can be established offline.

During the change:

- Move only the selected component. Update its consumers, package inputs and
  documentation together; do not create a second renderer implementation.
- Keep the source allowlist, reviewed recipe, generated immutable package
  manifest and actual loaded/executed paths consistent. Never recursively copy
  the development workspace into the alpha.
- Keep diagnostics off in the normal path. Profiling and diagnostic imports
  must not become prerequisites for readiness, activation or rendering.
- Preserve original capture data, game assets, identity, synchronization,
  suppression/fallback, GPU ownership, cleanup and user settings unless a
  separately approved behavior change explicitly alters them.

## Verification matrix

| Affected boundary | Proportionate checks |
| --- | --- |
| Documentation/navigation only | Links, ownership, classification, strict plan validation and focused diff; no gameplay or GPU campaign |
| Pure development tool | Its actual CLI/file boundary and relevant tests; confirm it remains absent from the production payload |
| Python runtime/import relocation | Import/use through the reduced installed module set, actual captured-data preparation where relevant, and package integrity; source-tree imports alone can hide omitted dependencies |
| Native compilation/interface | Focused builds/tests for exports, calling convention and wire/interface layout, plus affected process boundary |
| Launcher/renderer startup or output receiver | Actual extracted-package launcher preflight plus real host/receiver readiness, late activation and GPU completion/transfer with startup profiling off; cancellation, normal shutdown and relevant relaunch/recovery |
| Scene/input/insertion path | Relevant deterministic transport/GPU checks and sponsor gameplay for changed camera, lifetime, native effects or frame matching |
| Public artifact assembly | Test the exact extracted ZIP without development-tree/runtime access; preserve checksum/provenance/notices and the separate clean/second-machine approval gates |

Do not repeat every historical test after every move. Reuse unchanged evidence
where applicable; broaden checks when a failure or changed boundary warrants it.
Report source tests, standalone GPU results, installed execution and sponsor
observations separately. The earlier 749-regression/GPU record is baseline
evidence, not a new result of reorganizing Markdown.

The November 9 profiling-off failure is the reason for the startup-specific
check: CPU asset preparation and integrity preflight passed while an old native
warm-up condition prevented output. See the
[regression and correction](runs/2026-11-09-codex-production-module-separation.md#gameplay-regression-and-correction).

## Rollback and completion

A later migration must retain its reviewed pre-move source and accepted package
outside the deployment transaction. Revert only that migration's changes when
requested; preserve unrelated work. If installation files are switched, use the
existing journaled recovery only after SFC exits, retain resources until leases
drain, and stop only helpers owned by that run. Do not test rollback by modifying
the accepted installation.

For this foundation, rollback is only a review/reversion of its documentation
edits. No game recovery, process kill or package restoration is necessary because
this phase does not modify those inputs. Branch creation was separately
authorized by the sponsor; branch deletion or remote changes are not implied.

Remaining limits are explicit: mixed native header ownership, exact destination
paths, legacy helper-method separation, complete vendor/VC++ dependency closure,
clean/second-machine package qualification and broader model coverage. A tidy
repository or completed task list does not resolve those engineering questions
or approve a release.

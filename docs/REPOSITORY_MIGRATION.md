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

**First concrete separation:** `separate-release-tooling` now moves the five
launcher inputs to `src/launcher`, leaving release/build tools behind. See its
[design](../openspec/changes/separate-release-tooling/design.md) and
[verification record](runs/2026-11-09-codex-release-tooling-separation.md).
The next scoped change, `separate-session-coordinator`, relocates the coordinator
and its exit/report helpers to `src/session`, with development-only compatibility
entry points. It preserves diagnostic branches; extracting those branches is
separate from physical source ownership. See its
[record](runs/2026-11-09-codex-session-coordinator-separation.md).
The remaining runtime source islands are still separate future changes.

**Next concrete separation:** `separate-session-diagnostics` extracts the
coordinator's optional modes into development tools while keeping one shared
application startup, fallback and cleanup lifecycle. Normal installed imports
are guarded against diagnostic modules. See the
[implementation and qualification record](runs/2026-11-09-codex-session-diagnostic-separation.md).
The sponsor accepts the new playable checkout as passing; the prior six-minute
acceptance remains separate evidence for the previous organized build.

**Shared runtime support:** `separate-runtime-support` moves six functional
helpers to `src/runtime`, preserving unshipped developer compatibility and a
60-module production list. Startup, restore and installed dependency checks pass;
sponsor accepts the separate gameplay checkout, noting perceptible loading stages. See the
[record](runs/2026-11-10-codex-runtime-support-separation.md). Remaining asset and
renderer support islands are separate future work; no wholesale relocation.

**Asset preparation:** `separate-asset-preparation` moves nine helpers and extracts
neutral mesh decoding into `src/assets`, separating explicit review/comparison
tools and retaining existing behavior. Package/standalone checks pass; sponsor
reports gameplay checkout complete and requests the commit. [Record](runs/2026-11-10-codex-asset-preparation-separation.md).
The [renderer/transfer ownership review](reconnaissance/2026-11-10-renderer-transfer-ownership.md)
identified the two remaining application boundaries in the main reorganization.

**Scene transport and renderer startup:** `separate-scene-transport-and-renderer`
moves scene receipt, shared data and buffer ownership to `src/transport`, then
renderer startup and backend selection to `src/rendering`. Detailed renderer
reports remain developer tooling. The sponsor completed the private gameplay
checkout for the source separation. See the
[record](runs/2026-11-10-codex-transport-renderer-separation.md).

**Original recommendation:** scope `separate-release-tooling` around the portable
entry point and its build-time/runtime split. `tools/release/` has 20 tracked
files at the baseline, but only two of its Python modules are shipped. This is a
smaller boundary than relocating the coordinator, asset pipeline and GPU adapter
at once. Exact source/destination paths and compatibility entry points belong in
that change's design before moves begin; no wholesale new source layout is
prescribed here.

The native observer/controller, D3D9 adapter and output receiver retain their
existing source and build locations. Further relocation, D3D12 work, appearance
tuning and vendor pruning are outside the main source reorganization.

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

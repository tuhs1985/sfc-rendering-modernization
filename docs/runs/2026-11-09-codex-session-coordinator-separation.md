# Session coordinator source separation

November 9, 2026. Sponsor requested committing the previous increment and beginning
this one. Committed only the reviewed launcher/release separation as `8e69c93`
on `codex/organize-repository-foundation`; no push/merge. This session increment
remains unstaged/uncommitted. Unrelated attachments and memory audit are untouched.

## Scope and mapping

| Previous implementation | Canonical application module |
| --- | --- |
| `tools/remix_runtime/run_return_game.py` | `src/session/coordinator.py` |
| `tools/remix_runtime/session_exit.py` | `src/session/exit_monitor.py` |
| `tools/remix_runtime/run_report.py` | `src/session/reports.py` |

Old paths contain only forwarding tools, for documented existing development
launchers and probe imports. Import aliases share canonical module objects,
including mutable report state and exception identities. The old CLI calls the
canonical exception-reporting entry point. There is one implementation.

The installed bootstrap imports coordinator directly. The 59-module production
allowlist replaces three entries; no compatibility wrappers ship. Staging and
test consumers agree with the new installed paths. Source-only qualifier
inventories now track implementation files, rather than just the old wrappers.
No qualification receipt was silently renewed or verification disabled.

Diagnostic CLI modes/branches still coexist inside the canonical coordinator.
Their later extraction is not claimed by this physical ownership move. Renderer,
textures, controls, scheduling, cleanup and user preferences are unchanged.

## Verification

- **752 regression tests pass**, 12.704 seconds, with appropriate normal Windows
  process access: `artifacts/alpha/session-separation-regressions.txt`.
- Three new focused tests exercise direct and legacy CLI admission/rejection
  in isolated subprocesses outside the repository, shared module/report state,
  and production exclusion of the old wrappers. No execute flag/game launch.
- All original top-level function/class ASTs are unchanged: 11 coordinator
  functions, five exit-monitor definitions and two report functions. Only import
  wiring and a new CLI entry wrapper differ. UTF-8 source comparison receipt:
  `artifacts/alpha/session-separation-equivalence.json`.
- Static import-superset discovery succeeds across both source roots (104 files;
  this intentionally includes inactive diagnostic imports, not the shipped list).
- Actual native/bundled-Python preflight succeeds on fresh reduced fixture
  `artifacts/alpha/preflight-fixtures/20261109-223315-408060`, first at a
  space/Unicode path, then after moving it. Its installed coordinator preflight
  also passes. 3,649 immutable files; 59 Python modules. Source game-copy protected
  files unchanged. Log: `artifacts/alpha/session-separation-preflight.txt`.

No SFC or GPU renderer launched. The fresh fixture is deliberately not a playable
game or distributable ZIP. Existing private alpha, native binaries and appearance
settings were not updated. No gameplay launcher is issued for this fixture.

## Existing development preflight limitation

Before any coordinator edits, the development normal play preflight already
failed its native-cohort receipt at `tools/d3d9_proof/live_light_binding.py`.
Evidence: `artifacts/alpha/coordinator-before-preflight.txt`. This is not caused
by the relocation. New source paths and forwarding files also change qualifier
inputs, so old diagnostic/source receipts must not be treated as current.
Installed preflight uses its own generated manifest and passed independently.

Next: review this source increment; use the established qualification workflows
to resolve stale development receipts before claiming developer gameplay ready.
Any hands-on package checkout must first assemble an actual playable package with
its matching manifest, bootstrap and coordinator. Preserve the existing alpha
until that explicit replacement is prepared. Remaining diagnostic extraction and
shared runtime components remain separately scoped organization work.

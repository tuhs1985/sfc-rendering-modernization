# First source separation — portable launcher versus release tools

November 9, 2026. Parent `f12b6fd`, branch
`codex/organize-repository-foundation`. Sponsor requested planning and execution.
Implementation is unstaged and uncommitted; no push, merge, tag or release.

## Delivered boundary

Five inputs moved from `tools/release` to `src/launcher`: `bootstrap.py`,
`session_recording.py`, `launcher.cpp`, `SFCRemix-Launch.cmd`, `Troubleshoot.cmd`.
Recording and CMD contents are unchanged. Bootstrap changes only its explicit
import search paths; C++ changes only the packaged bootstrap location.

The native build now consumes `src/launcher/launcher.cpp`. The exact 59-module
production allowlist replaces two paths without adding modules. Installed Python
now uses `code/src/launcher`; manifest coordinator role, staging, test imports
and ZIP assembly agree. ZIP validation rejects non-allowlisted inputs anywhere
under `code/`, covering the new source location as well as legacy tools.
There are no compatibility shims or duplicated launcher implementations.

Development tools, inventory, release-document input and qualification sources
remain in `tools/release`. Shared runtime context, renderer, observer, coordinator
and remaining production islands stay at their existing locations. Folder READMEs,
the repository map and current release notes describe this limited migration.

## Validation

- Strict native launcher build passes with existing C++20 `/W4 /WX /O2 /MT` flags.
  Built SHA256: `be5069bbff81882c37f70b1cbc9b48d0d815d465efe80efb5b466445414c6989`.
- All **749 Python/native regression tests pass** in 13.188 seconds with normal
  Windows process access. Log:
  `artifacts/alpha/release-separation-regressions-desktop.txt`.
  The restricted-process attempt had six failures and three access/IPC errors;
  none remained in the same suite run with appropriate Windows access.
- Fresh fixture `artifacts/alpha/preflight-fixtures/20261109-215518-017663`
  runs the actual new native launcher and bundled Python with `-I -B`.
  Both original `Game é space` and relocated `Moved portable game é` paths pass
  immutable manifest/profile/native-launch preflight (3,649 immutable files).
  Prepared installed coordinator read-only preflight also passes. Its code tree
  has 59 Python modules and no `code/tools/release` directory.
- The fixture verifies protected source game-copy files unchanged. Read-only
  launcher preflights created no settings or data; later explicit preparation
  wrote only into the disposable fixture. The first restricted fixture also
  eventually completed all three checks successfully; desktop repeat is retained
  as the primary package-boundary result.
- Byte/text comparison against parent source confirms the five moves contain
  only the two documented path edits. Summary:
  `artifacts/alpha/release-separation-summary.json`.

No SFC or GPU renderer was launched. Prior renderer/receiver and sponsor gameplay
qualification remains historical evidence for unchanged components, not a new
result. This fixture is not a distributable ZIP, complete dependency closure,
clean-machine test or release approval.

## Compatibility, rollback and next step

The existing `C:/Project/SFC-Alpha-Checkout` and its settings/manifest/launcher
were not updated. New launcher and new installed layout must be delivered as a
pair; do not copy the rebuilt executable alone into an old package. Rollback is
the inverse five-file source move and corresponding consumer-path edits.

The next organization increment should select one remaining production component
by ownership and dependencies. No wholesale `tools` move is authorized by this
record. A future reviewed package build must use the new paths, rebuild its
manifest and complete its own release/gameplay gates. Vendor closure and public
alpha approval remain open independently of this refactor.

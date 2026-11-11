# Design

## Boundary

`src/launcher` owns `launcher.cpp`, `bootstrap.py`, `session_recording.py`, `SFCRemix-Launch.cmd` and `Troubleshoot.cmd`. `tools/release` retains all development-only build and packaging tools, their inventory and release-document inputs. Other production modules still under `tools` are explicitly outside this first migration.

## Installed contract

The native entry uses `code/src/launcher/bootstrap.py`. Isolated Python explicitly adds the bootstrap's own directory, then the existing runtime module directories. The immutable manifest identifies the new coordinator path. No old-location forwarding modules are shipped. The production allowlist remains exact; ZIP validation checks all `code/` inputs, including `src`, against it.

## Compatibility and performance

The new native launcher and new package layout must ship atomically; mixing an old launcher with a new package is unsupported. Existing installed packages remain untouched and continue using their own old launcher. No per-frame work, diagnostics, renderer configuration, recovery rules or output behavior changes. Build-generated artifacts remain ignored.

## Validation and rollback

Build with the existing strict compiler settings. Exercise launcher options and an isolated installed preflight in a fresh space/non-ASCII path, then move it and repeat. Run the prepared coordinator's read-only preflight without development sources, focused/full Python regressions and whitespace validation. A source-only relocation needs no new gameplay acceptance claim. Preserve existing gameplay/standalone-GPU qualification; do not claim a new rendering result from preflight. Rollback is the inverse five-file move plus paired build/manifest changes; existing alpha needs no restoration because it is not modified.

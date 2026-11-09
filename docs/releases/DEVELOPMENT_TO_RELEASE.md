# Development-to-release process improvement

Sponsor direction, November 8, 2026: make production delivery a normal part of
development rather than a separate cleanup exercise. Recent private-alpha
failures show that development-tree success and a passing import/manifest check
do not establish installed startup success.

## Immediate working principles

- Keep one production launch path shared with development. Make environment and
  paths explicit; avoid separate implementations that drift.
- Declare executable, module **and data-file** dependencies. Separate immutable
  package inputs from settings, caches, logs and recovery records.
- Treat normal play as the baseline. Diagnostics are opt-in and should not be
  prerequisites for release startup or add default timing/storage overhead.
- For a change, verify the boundary it affects: packaged startup for startup
  changes, real file recovery for transaction changes, GPU transfer for output
  changes. Use focused checks before broad regression runs.
- Before sponsor checkout, build/stage from a known source state, exercise the
  installed entry point without development-tree dependencies, and check normal
  shutdown plus immediate relaunch. Separate offline evidence from gameplay.
- Identify each candidate by source/build state, dependency pins, manifest and
  qualification receipts. Preserve editable settings and a tested rollback path.
- Turn each release defect into a targeted automated regression where practical.
  Do not compensate with repeated manual sponsor runs or unnecessary validators
  in the rendering path.

## Follow-up to formalize

After the private alpha launches correctly, audit current build/stage/test
commands and consolidate a repeatable candidate workflow. It should produce a
clear result for build, dependency closure, installed startup, recovery/relaunch
and sponsor-only gameplay checks. Define a small change checklist and automate
the repetitive checks; do not introduce a second renderer, duplicate harness or
large test campaign merely to improve process.

The current manifest/stager and scene-profile checks are starting points, not
proof this workflow is complete. Clean-directory and second-machine qualification
and final redistribution review remain release gates. No CI or automated release
pipeline is claimed by this note.

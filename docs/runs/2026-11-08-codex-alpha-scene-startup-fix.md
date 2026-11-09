# Private alpha: game starts without Remix

Sponsor run `20261108-190045-365408-in-game` created the verified copied
SFC process but stopped in startup: `multi_ship.toml` was missing from the
installed Python code directory. No scene controller or GPU folder was created;
the observation host reported zero samples. Original drawing remained available.
Rollback was correctly deferred while SFC was running.

## Correction

The import-only package closure missed non-Python resources. The two existing
project-authored scene profiles, `multi_ship.toml` and `offset_ship.toml`, now have
explicit inventory entries, required manifest roles and immutable hashes.
Installed preflight parses them at their expected locations before starting
SFC or switching graphics files. No renderer/appearance policy was changed.

A deeper installed startup check exposed the generated environment cache under
immutable runtime. It now maps to `data/cache/environment`. The check-generated
DDS was moved only after verifying its filename matches its content hash.

After verifying SFC had exited, recovered the interrupted graphics transaction
through `recover_pending`. Updated the private package's bootstrap, manifest
verifier, runtime context, two profiles and package manifest. Settings/assets
preserved; local rollback copies under `artifacts/alpha/scene-profile-rollback`.

## Verification

- Exact installed CMD `--preflight`: PASS, 4,145 immutable files.
- Three new profile tests: PASS, including missing/malformed/redirected inputs,
  spaced/non-ASCII paths and explicit non-Python resource closure.
- Bundled Python exercised actual relay construction/passive scene preparation,
  including real native image/hash helpers and damage texture preparation, up to
  the renderer process-launch boundary. Executable/runtime paths exist. Only the
  final owned guard launch was intercepted; no SFC or renderer started. Receipt:
  `artifacts/alpha/installed-scene-preparation.json`.
- Desktop-session Python regressions: 734 PASS. Restricted-session IPC/environment
  tests failed; those boundary tests passed in their required desktop session.
- `git diff --check`: PASS.

Next: retry `C:\Project\SFC-Alpha-Checkout\SFCRemix-Launch.cmd` and verify enhanced
ships in a skirmish. Packaged gameplay acceptance remains unverified. No public
ZIP, tag, commit or push. Elevation, appearance, ExtraFrame and fallback unchanged.

# Private alpha: asset activation used the development light path

Run `20261108-191427-451898-in-game` reached tactical capture and prepared FCA
geometry/materials. Renderer/receiver started passively. Recovery service then
failed opening `code/tools/remix_runtime/config/lights.toml`. The light-binding
constructor still built a development-tree path instead of using the shared
runtime context. Receiver cancelled before activation/first output. Sponsor saw
only native SFC. Game exit was normal; proxy restoration passed. No active SFC
process remained before the package update.

## Fix and verification

`live_light_binding.Binding` now reads `CONTEXT.setting('lights.toml')`. Development
keeps its established location; installed play uses editable package settings.
No additional profile copy, lighting change or renderer change. The verified
private package was updated with one Python module and refreshed manifest hash;
rollback preserved under `artifacts/alpha/live-light-context-rollback`.

The previous smoke check stopped at passive renderer preparation and missed the
later asset-activation constructor. Expanded it to reuse this run's captured FCA
asset in disposable data storage and execute actual `prepare_initial_context`,
including actual light binding, shape generation and shared effect-light policy
publication. Final process launch remains intercepted: no SFC or renderer started
by this check. Captured assets/settings unchanged. Receipt:
`artifacts/alpha/installed-scene-preparation-light-binding.json`.

Added a regression constructing the real binding with installed settings and no
development config folder. All 735 desktop-session Python tests PASS; exact CMD
preflight PASS with 4,145 immutable files. Review of normal light/material settings
consumers found this remaining direct path; historical light replay and qualifier
scripts remain development-only and are not claimed portable gameplay paths.

Next: retry the same `C:\Project\SFC-Alpha-Checkout\SFCRemix-Launch.cmd`.
Gameplay acceptance remains open. Changes unstaged/uncommitted; no public release.

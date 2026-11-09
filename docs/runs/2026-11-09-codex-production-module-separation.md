# Production module separation — initial implementation

Sponsor authorized: commit the current alpha/audits, then begin the 48-file
production cleanup. Checkpoint committed as `49373fd` (112 source/test/doc files);
746 baseline tests and installed preflight passed. No push. Attachments and the
unrelated memory note remained untracked. Changes below are **uncommitted**.

## Delivered boundary

- Added an explicit **59-module production allowlist** at
  `tools/release/runtime_modules.json`. Staging no longer ships the static
  all-branches import superset; ZIP validation rejects non-production modules,
  including case-variant attempts. Developer tools remain in the repository.
- Excluded all 48 audited files from the private alpha: 45 Python modules, two
  diagnostic TOMLs and the legacy texture-hash EXE. Added one production helper
  module, so authored payload changes **118 → 71 files**, not 118 → 70.
- `runtime_files.py` owns shared paths/hash/file-size helpers previously imported
  from an offline fixture. Recovery uses the same production game-root context.
- Shared native replacement offset now lives in the existing transport capacity
  definitions. Native cohort/gate parsing no longer imports player-test tooling.
- The progressive relay injects its real Pipeline into the base constructor;
  the displaced PreparationQueue is no longer instantiated then discarded.
- Moved qualification imports inside the actual non-multiship branches. Depth
  search imports are diagnostic-only. Release startup verifies the semantic
  component through its manifest without importing the light-observer campaign.
- Zero-offset native replacement no longer reads placement/model-test profiles.
  Those profile roles and the old texture-hash role are no longer prerequisites;
  production still checks executable, graphics profile and all retained inputs.
- Kept the existing native checksum DLL and actual progressive image/material
  path. No geometry, UV, shader, original image or lighting parameter change.
- Installed startup profiling is off. Actual material/runtime preparation stays
  enabled. Task execution retains results/errors but no longer collects task
  clock/thread span records in installed play. Development timing stays available.
- Untimed native completion reads cohort state without dumping its raw BIN/JSON;
  installed play no longer writes the redundant play-session-summary file. The
  final transactional result remains until verified restoration/retention cleanup.
- The guard accepts an explicit zero scratch-quota argument only in installed
  untimed play. Development capture limits and parent-death/resource ownership
  remain; real free-space/per-asset limits remain. No new timer or refresh cap.

## Private deployment and evidence

Freshly staged, moved non-ASCII/spaced package passes installed native and actual
coordinator **read-only preflight** with the excluded files absent. No game or
renderer started. Receipt: `artifacts/alpha/refactor-production-fixture.txt`,
fixture `20261109-174757-741450`.

An isolated CPU fixture then used the reduced package to decode a previously
captured raw FCA geometry packet and read original images from the controlled
copy. It ran actual Pipeline workers, base geometry/texture production, enhanced
material generation/publication and light binding: **19,110 vertices, 58 groups**.
It asserts excluded toolchain modules were not imported, task spans stayed empty,
and installed startup profile was off. It uses an explicitly synthetic CPU-only
material-prime receipt; **not GPU acknowledgement or gameplay acceptance**. No
saved geometry template or `.mod` conversion was used. The fixture supplies the
normal prewarm material directory without launching a renderer.

After confirming SFC absent, updated only code, guard and manifest in
`C:\Project\SFC-Alpha-Checkout\SFCRemix`. All old affected files/manifest retained
under `artifacts/alpha/production-module-rollback/20261109-175532`; the deployment
script restores them if verification fails. Settings, defaults, vendor packages
and copied-game profile preserved. Removed the now-empty legacy helper directory.
Installed manifest now lists **3,848** immutable files. Installed preflight and
the same actual CPU asset/light test pass after deployment:
`artifacts/alpha/refactor-installed-assets.txt`.

## Checks

- **748 Python regressions PASS**. One obsolete diagnostic-profile prerequisite
  test was retired while tests now cover production-only settings/module roles.
- Real x86 guard process test covers zero-quota installed play, oversized working
  data/log saturation, plus the development quota control. Installed play exits
  normally; development control still enforces its quota.
- New task test proves successful values and failures propagate without invoking
  the diagnostic clock or collecting spans. File helper test preserves SHA256
  case and vanished-packet behavior.
- ZIP tests reject developer modules, including upper-case path variants.
- Actual installed Unicode-path preflight, native role integrity, fresh CPU
  material/light production and copied-game profile checks pass.
- `git diff --check` PASS. No additional appearance tests or broad GPU campaign;
  native rendering/insertion code is unchanged apart from the guard quota contract.

## Limits and next action

This is a **production file-boundary cleanup**, not a claim all inactive methods
inside retained modules have been refactored away. Shared relay inheritance and
some stage-completion timing metadata remain. Development qualification locks
correctly become stale after source changes; their checks were not bypassed.
The normal release manifest covers the new helper; development source inventory
also includes it. The separate MSVC clean-machine dependency gap remains open.

Next sponsor checkout: same `SFCRemix/launcher.exe` (or root CMD), brief ordinary
play with ships/materials/lights/damage, camera switches, normal exit and immediate
relaunch. This checks actual renderer activation, native insertion and retention
cleanup with excluded files absent. **Gameplay after this change is unverified.**
No further commit, push, tag or public prerelease has been made.

## Gameplay regression and correction

Sponsor's first reduced-package checkout showed no enhancements. This invalidates
the earlier implication that CPU preparation/preflight alone was sufficient to
hand over a working renderer. Run `20261109-194448-097868-in-game` prepared the
correct FCA and textures, but produced zero returned frames; its receiver stayed
passive and cancelled before activation. SFC exited normally and protected
client/profile checks passed. Renderer teardown reported a worker timeout.

Root cause: `async_material_checkout.configure_child` now correctly supplies
`SFC_D3D9_STARTUP_PROFILE=0` for installed play, but the existing x64 host's
`render_prewarm::run` explicitly required `profile.enabled`. That requirement
turned a diagnostic flag into a functional startup prerequisite. The CPU fixture
never ran the host and therefore could not expose the coupling.

Removed only that prerequisite in `render_prewarm.h`; private triangle warm-up,
GPU completion/state restoration and readiness publication are unchanged.
`StartupProfile.mark` already becomes a no-op with profiling disabled. Added a
regression guard and the development-only `qualify_production_prewarm.py`, which
uses a synthetic native target/ticket, the actual installed runtime/receiver,
previously captured geometry and real GPU resource transfer. It is excluded from
the production module allowlist and disables bytecode writes into installed code.

Controlled GPU checks (all under `artifacts/alpha/`):

| Check | Result |
| --- | --- |
| `prewarm-regression-old-off-2` | Original packaged host, profiling off: no startup readiness in10s; bounded cancellation/owned-job termination |
| `prewarm-regression-old-on` | Same original host, profiling on: ready in2.875s; normal pre-output cancellation and zero owned processes |
| `prewarm-regression-fixed-off-2` | Rebuilt host, profiling off: ready in2.828s; real late activation; one bootstrap output, colour/depth/owner bytes identical in producer and receiver; normal exits |
| `prewarm-regression-fixed-cancel` | Rebuilt host, profiling off: ready in2.953s; pre-output cancellation, normal exits, zero owned processes |

The first bootstrap is never shown in SFC. It can be black before a live lit
scene is submitted; this fixture verifies startup/transfer rather than rendered
ship appearance. One initial fixture assertion incorrectly required a nonblack
bootstrap; it was corrected, not counted as a product pass. The failed initial
invocation and subsequent successful records remain local. Synthetic notices
and tickets do not prove native insertion or gameplay. These readiness times are
passive startup measurements, not first-ship loading latency; do not compare them
to the sub-two-second ship target.

Strict x64 build passes. **749 regressions PASS** (`prewarm-fix-regressions.txt`).
Installed renderer SHA256:
`1bf0045d64b2cb6283bb20e9476b64e16c436e45b1ccd6e860377d3e2e53c16b`.
Updated only the private renderer and immutable manifest, after checking no SFC;
rollback `artifacts/alpha/prewarm-fix-rollback/20261109-195609`. Settings and game
profile remain unchanged. Installed native EXE `--preflight` passes with3,848
immutable files. The48-file exclusion/71-authored-file payload remains intact.
The standalone tool initially generated16 bytecode files inside installed code;
only those unlisted generated files were removed, and bytecode writes disabled
before subsequent use. No game assets, private settings or vendor files changed.

Sponsor subsequently confirmed that enhancements work again with the corrected
private alpha. **No SFC was launched by Codex.** Immediate relaunch/cleanup was
not separately reported; clean-machine release qualification remains open. No
push or public release was performed.

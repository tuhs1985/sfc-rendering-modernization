# Alpha release preparation

**Current November 8 checkpoint:** [live FCA destruction succeeded](../runs/2026-11-08-codex-live-break-success.md).
Two parent lifetimes/eight pieces rendered and suppressed correctly, with cached
sharing and normal gameplay by sponsor report. All four required alpha feature
areas now have scoped gameplay evidence; no universal model-coverage or packaged
release claim. BRK stays opt-in until baseline promotion. Next delivery work is
the dependency inventory and portable installation configuration described below.
The earlier pending/failure paragraphs preserve assessment history.

Assessment: November 7, 2026. **Planning and local implementation audit complete;
no distributable package or alpha-readiness declaration yet.** Existing dirty
implementation work is preserved. No game, renderer, installer or dependency
download was started for this assessment.

**November 8 update:** the first live BRK checkout exposed an intact-only decoder
left in the active parallel worker. Four valid debris captures pass dedicated
admission but never reach renderer admission. [Failure review](../runs/2026-11-08-codex-live-break-failure-review.md).
The functional gate now requires that correction and a retry, rather than merely
reviewing an outstanding run. Copied-install recovery is complete.

**Worker correction complete, November 8:** [fix record](../runs/2026-11-08-codex-break-worker-fix.md).
Actual failed-run captures now complete CPU preparation for all four pieces;
51 targeted tests and read-only preflight pass. Only the live retry remains
pending for this identified blocker; downstream gameplay acceptance is still open.

**Second checkout correction:** [receiver-to-worker review](../runs/2026-11-08-codex-break-receiver-fix.md)
found the same intact-only admission left in the upstream receiver. It is now
explicitly BRK-aware, with66connected-path/regression tests passing. Latest real
captures pass both stages. Live fragment insertion still awaits retry; neither
failed run established debris renderer admission.

## Release we should prepare

Prepare a versioned Windows test package for the already-supported SFC client,
using the existing ordinary D3D9 → Remix → native insertion architecture. Users
provide their own game. The package prepares an independent test copy, uses
their local original assets, and leaves their accepted installation and saves
alone. It must not require the Toolkit, Codex, Obsidian, Visual Studio or source
editing to play.

Recommended rollout: first validate the package on a clean directory and a
second machine, then offer an explicitly labelled alpha to testers. Broader
publication follows that evidence and sponsor approval. This is a delivery
sequence recommendation, not a new product requirement or release authorization.

The [approved alpha feature scope](../decisions/2026-10-27-alpha-release-scope.md)
requires replacement, weapon lighting, damage textures and fast destruction/break
models. LOD is optional. A settings GUI, supersampling, complete weapon-effect
replacement, D3D12, new assets and a renderer-independent public SDK are not
being added as alpha blockers. Preserve their separately tracked work.

The [CDD](../requirements/README.md) and approved amendments remain governing.
An experimental alpha is not proof of every KPP, formal milestone completion or
Initial Usable Capability. In particular, tested ship replacement is not full
3D-rendered-state coverage. KSA-3's clean-baseline deployment demonstration is a
useful existing criterion; a new installer framework is not required to meet it.

## Feature evidence and what remains

| Area | Current evidence | Release work / disposition |
| --- | --- | --- |
| Supported multi-ship replacement | Native colour/depth insertion before shields/text, capture-first suppression, shared assets and independent owners have gameplay evidence | Freeze the exact build/configuration and preserve ordinary native fallback. Repeat a focused smoke test from the staged package, not another connection-discovery campaign. |
| Weapon lighting | Visible phaser/photon illumination, moving native effect lights, configurable sphere proxies | Include current accepted settings and document approximate brightness/radius conversion. Exact weapon-name attribution and every weapon's lighting are not proven; do not claim universal coverage. [Light evidence](../runs/2026-11-03-codex-effect-radius-and-moving-lights.md). |
| Damage textures | KDD/FCA application and first-use transparency correction visually confirmed; repair/removal proved offline | Exercise live repair/decrease and representative damage during the final checkout. Preserve the unresolved camera-angle-dependent KFF gray-wing report as a finding, not a diagnosis. [Damage baseline](../runs/2026-11-04-codex-damage-baseline.md). |
| Destruction/break pieces | Live FCA checkout: two parents/eight fragments with native insertion/suppression and shared content; sponsor confirms correct motion and normal gameplay. First-group GPU admission approximately0.4safter first capture-frame start, not first visible pixels | **FCA feature demonstrated.** Broader break files remain unqualified; integrate into the staged alpha candidate and qualify package launch/exit. [Live result](../runs/2026-11-08-codex-live-break-success.md). |
| Campaign/long play | Approximately 21 minutes across three missions; one observed replacement dropout, normal game/renderer behavior otherwise | Recheck mission exit/reentry, early exit and immediate relaunch using the final package. Existing minimal counters cannot identify the old dropout's exact cause. [Three-mission review](../runs/2026-11-04-codex-three-mission-play-review.md). |
| Fleet/fighter load | ExtraFrame stress review: 63 owner/revision records, 15 loaded assets; all retained owners inserted at some point, no post-startup deadline misses | Does not establish 63 simultaneous visible ships or unlimited capacity. Existing tables admit 256 owners/1,024 revisions. Preserve explicit capacity handling and native drawing for unsupported instances. [Stress comparison](../runs/2026-11-02-codex-extraframe-stress-comparison.md). |
| Cloak/transparency and other unsupported paths | Earlier cloaked Romulan admission is unresolved | Qualify native retention and tactical fidelity. If cloak correctness fails, resolve or explicitly exclude the affected configuration; do not advertise universal Romulan/cloak support or allow opaque stale replacements. |
| Startup/performance | Fast first insertion exists in recorded fixtures; larger initial sets and occasional hitches remain workload-dependent | Report first native observation → first base replacement, enhanced-material readiness, all initially observed assets ready, and frame-time distribution separately. No universal sub-two-second readiness or FPS promise from the existing evidence. |

## Supported baseline to freeze

Start with the observed Windows 11 x64 / NVIDIA RTX configuration and Community
Edition client labelled 2.5.6.4, executable SHA-256:
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
This is an exact-build integration. nxreliant's modified 2.5.6.5 executable is
not automatically compatible; do not relax hash/address checks to accept it.

The current path uses fixed 1920×1080 output/viewport assumptions in
`tools/remix_runtime/d3d9_game_receiver.h`; do not claim arbitrary resolutions,
ultrawide, HDR, resize/device-recovery or other GPU support without qualification.
Freeze the actual wrapper/display profile, adapter, driver and configuration
used for the release checkout. Determine the compatible minimum driver from the
pinned binary's requirements rather than presenting this workstation's driver
as a universal minimum.

The active multiship renderer uses pinned Remix 1.6.1 / public API 0.6.5, through
`runtime_candidate.py` and `async_material_checkout.py`. Current development
bootstrap/preflight still requires legacy 1.5.2 files. The old
`remix-return-dependencies.json` describes a historical diagnostic baseline;
it is not a complete release bill of materials. Produce a separate final
release manifest; do not overwrite historical evidence to disguise that split.

ExtraFrame is standard. Normal play is untimed with bounded recording; no
routine timing-policy selector or 90-second stop belongs in the user launch.
Keep diagnostic startup warm-up, completion/light traces and continuous image
capture off by default. Required synchronization/lifetime/asset bounds remain.

## What the local audit found

| Delivery gap | Concrete current implementation | Required packaging treatment |
| --- | --- | --- |
| User-specific runtime paths | `start_native_multiship_session.ps1` invokes PowerShell/Python inside the Codex cache | Resolve project-owned managed prerequisites or documented installed runtimes; no Codex installation required. Python remains needed unless separately packaged; do not silently rewrite the coordinator in C++. |
| Fixed game/copy locations | `run_return_game.py`, `run_return_fixture.py`, `prepare_test_install.ps1` use this PC's game and test folders | One installation record supplies game, independent copy, package, cache and settings roots. Preserve exact executable validation, path checks and launcher routing. |
| Generated validation data | `native_cohort.require_qualification` opens ignored local receipts; candidate build checks broad source fingerprints including tests | Release-time tests generate an immutable release manifest for shipped inputs. Installed preflight verifies that manifest and machine prerequisites without demanding every test source/EXE or rerunning qualifications. This is separation, not disabling validation. |
| Legacy bootstrap dependency | `preflight()` requires 1.5.2 runtime, `return_host.exe`, old gate binaries; active async backend selects 1.6.1 | Establish the actual bootstrap/control dependency closure. Keep necessary files until a regression-tested release bootstrap removes a dependency. Do not delete 1.5.2 merely because geometry is rendered by 1.6.1. |
| Temporary proxy mutation | Normal workflow installs qualified full-support ReShade then restores the copied proxy | Package owns a transaction journal and rollback files for the test copy. Verify game exit before restoration, protect unknown preexisting proxies and support repair after interrupted launch. Never modify an arbitrary user's original stack. |
| Mutable config vs package integrity | Appearance is intentionally editable; game-saved player names have an accepted exception | Separate immutable shipped inputs from user settings, game preferences and generated caches. Preserve last-good controls and the sponsor baseline; updates do not reset settings. |
| Elevation | Runtime runner currently requires the established elevated parent | Document the current requirement and keep same-user IPC/process ownership. Do not promise elevation-free operation or add security-policy changes. Evaluate privilege reduction separately once package launch works. |
| Security/startup behavior | Local Defender waits and a sponsor-scoped mission-script exclusion have evidence | Keep Defender enabled. No automatic exclusions, restored detections or protection changes in setup. Test a real downloaded release artifact; signing/reputation decisions follow observed results, not a guarantee that signing eliminates stalls. |
| Bounds and retention | Normal play is timerless but assets/cache/evidence remain bounded; preparation can fail when aggregate storage is full | Separate user cache from optional diagnostic captures. Before launch show required space and actionable cleanup, preserving useful evidence and never demanding deletion of saves or game assets. Define cache retirement explicitly for multi-mission play. |

## Proposed package contents

Use an explicit allowlist. **Do not zip this repository, the test installation or
the entire artifacts folder.** Final membership must be measured by running the
staged package with development folders unavailable.

Project runtime candidates identified by the existing launch path:

- `return_launcher.exe`, `SFCRemixReturn.dll`, `m1_controller.exe` and the selected
  semantic component (normally `m1_component.dll`; verify the effective mode).
- `d3d9_direct_host.exe` built for the pinned 1.6.1 header/runtime;
  `output_receiver.exe` and `bounded_job.exe` for the existing transfer/lifetime
  architecture.
- `return_host.exe` and legacy gate inputs while still required by the bootstrap.
  Distinguish files actually executed from files merely demanded by preflight.
- The coordinator's transitive Python modules, Pillow/NumPy and any required
  image-conversion helpers such as `texture_hash.exe`; confirm actual runtime
  imports/executions before calling this list complete.
- One normal launch entry point, read-only system check, repair/uninstall
  instructions, accepted `rendering.toml`/`lights.toml` baseline plus separate
  restore examples, release manifest and third-party notices.

Compiled project helpers are small relative to the vendor stack. The pinned
1.6.1 archive is 557,087,446 bytes; the locally recorded extraction has 192 files,
including alternate-architecture DLLs and optional vendor components. These are
observations, **not** the final download/install size or permission to trim it.
Avoid reconstructing a minimal runtime by guessing which DLLs can be removed.

Recommended first packaging route: project binaries plus a controlled launcher
and managed Python 3.12 environment with pinned packages, alongside separately
obtained pinned graphics dependencies. A portable directory/ZIP with a setup
step is sufficient for initial testing; an MSI, auto-updater or settings GUI is
not required. The supported Python distribution and its notices still need to
be selected; a copy of the Codex runtime is not a release dependency.

Never include SFC EXEs/assets, captured meshes/images, generated ship/material
caches, saves/campaigns, private settings, chat/desktop captures, original
rollback files, local logs or development receipts containing machine paths.
Users generate their own caches from their game. Do not bundle the Toolkit,
Nsight, disassembler outputs, test executables or the full research corpus just
to satisfy development-era checks.

## Dependency and licensing work

No project source license is currently selected in the README. Selecting that
license is a sponsor decision before publication; this assessment does not
grant rights or choose one. Public GitHub visibility alone is not a dependency
redistribution decision.

| Component | Evidence / disposition |
| --- | --- |
| ReShade SDK/runtime | Pinned SDK source has a [BSD-style license](https://raw.githubusercontent.com/crosire/reshade/8cf85bd12d56697d756d4fcb45e501f5d1b540fa/LICENSE.md) with binary notice requirements. Audit the actual full-support runtime package and required shader presets separately. |
| Microsoft Detours | [Pinned 4.0.1 MIT license](https://raw.githubusercontent.com/microsoft/Detours/v4.0.1/LICENSE.md); retain required notices for incorporated code. |
| RTX Remix and bundled components | [Pinned source root license](https://raw.githubusercontent.com/NVIDIAGameWorks/dxvk-remix/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/LICENSE) is not an inventory of the binary bundle's terms. Local `runtime/LICENSE.txt` and `ThirdPartyLicenses-dxvk.txt` include additional notices/SDK terms. Review complete package terms before bundling; separately obtained official downloads avoid silently republishing our dependency tree. |
| dgVoodoo | Installed test-copy DDraw/D3DImm version is 4.7.1.3000 by Dégé. [Official project](https://dege.freeweb.hu/dgVoodoo2/). Exact package provenance/terms and compatibility configuration need release inventory; do not assume wrapper files can be repackaged from the user's game. |
| Python/Pillow/NumPy and Microsoft runtime | Choose supported deployment mechanism and preserve its notices; audit native imports to identify actual CRT requirements. Current development versions are evidence, not a completed redistributable manifest. |
| SFC and community assets/presets | User supplied. No redistribution in our package. Ship project-authored/sanitized configuration only after checking origin and local paths. |

## Execution order and exit gates

1. **Finish functional evidence:** review the pending live BRK checkout. Resolve
   any transition/lifetime/loading blocker and review damage/repair and cloak
   handling against advertised scope. No new broad discovery trace by default.
2. **Make setup portable:** centralize installation/runtime/cache/settings roots
   and remove dependence on the Codex runtime. Preserve the current renderer,
   IPC, early startup and source data; no unrelated architecture rewrite.
3. **Separate release and development entry points:** retain the existing
   diagnostic tools. Ship a narrow untimed normal launcher and a cheap preflight
   based on immutable package hashes, supported game/device/profile and writable
   storage. Keep full qualification in the build pipeline, not each user's launch.
4. **Stage the allowlisted package:** generate exact file hashes/versions,
   settings schema/defaults, dependency sources/notices and a reproducible build
   identifier from a sponsor-requested reviewed commit. No unreviewed work is
   staged or committed merely for packaging.
5. **Prove deployment:** clean directory and second-machine runs without the
   development tree, Toolkit or developer cache. Cover first launch, short
   skirmish, early exit/relaunch, interrupted recovery and removal. Verify game
   hashes/preferences, native fallback and owned-helper cleanup.
6. **Alpha checkout/release:** representative mixed models, fighter additions,
   destruction, damage/repair, camera/shields/text, and mission transitions.
   Freeze settings, collect compact timings and list known limits. Then obtain
   sponsor approval for the concrete versioned artifact and publish it.

Stage 2 can proceed while the sponsor defers the BRK run; publishing alpha cannot
claim destruction qualification until its evidence is reviewed. Start with a
read-only dependency/path inventory and a single installation configuration
contract, then migrate the existing launch/recovery code in small checked steps.
Do not combine portability changes with more material/renderer experimentation.

For each candidate record: exact Git/build/package/config/dependency IDs, test
machine/driver, supported game hash/profile, first-base/enhancement timings,
frame distribution, visible findings, repair/uninstall result and known limits.
Report game-frame timing separately from callback ages or optical latency.

## Remaining sponsor decisions

Choose project source/binary distribution terms, final tester audience and
permission to publish the reviewed artifact. These decisions need not interrupt
the current audit or portability work. A product name, installer brand and exact
alpha number can wait until a reproducible candidate exists.

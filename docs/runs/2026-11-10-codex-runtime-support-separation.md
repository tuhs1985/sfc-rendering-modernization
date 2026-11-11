# Application runtime support separated from developer tools

November 10, 2026, America/New_York; parent `09bbeea` on
`codex/organize-repository-foundation`. Sponsor authorizes implementation and a
separate gameplay checkout before committing. Sponsor accepts the checkout and
now requests this increment be committed. No push, merge, release or automatic
SFC launch.

## Ownership and compatibility

| Application file | Responsibility / old development location |
| --- | --- |
| `src/runtime/runtime_context.py` | Development/installed package paths and immutable context; formerly `tools/remix_runtime/runtime_context.py` |
| `src/runtime/release_manifest.py` | Package integrity, recognized game profile, seeding editable defaults; same old basename under tools |
| `src/runtime/windows_processes.py` | Native process inventory and fail-closed game-presence checks; same old basename under tools |
| `src/runtime/runtime_files.py` | Existing runtime paths, environment constants and bounded/race-safe file helpers; same old basename under tools |
| `src/runtime/copied_preferences.py` | Existing protected-file and game-owned preference rules; same old basename under tools |
| `src/runtime/session_recovery.py` | Interrupted graphics transaction recovery; formerly `tools/remix_runtime/recover_broad_session.py` |

Five implementations are identical to their parent sources after line-ending
normalization. Recovery retains its checks and file operations, adds a callable
CLI and imports `atomic_copy` directly from the existing application
`graphics_transaction` helper. The old recovery-only import of `broad_capture`
was a latent installed dependency defect: that diagnostic module no longer
ships. Normal startup had not exercised this interrupted-recovery branch.

Bootstrap and standalone coordinator put `src/runtime` on their search path
before importing these helpers. Installed recovery imports `session_recovery`.
Old development paths remain compatibility entry points; same-name forwarders
use standard importlib loading and register the canonical public module before
execution. This preserves dataclass/module identity and shared patched state.
The old recovery CLI forwards to the new implementation. Compatibility files
are not installed.

The production list remains **60 Python modules**; six inputs change ownership
without adding modules. Build/qualification inventories include the new source
directory. The static import audit resolves explicitly owned application modules
ahead of intentional developer forwarders; unrelated ambiguities still fail.
Static closure still includes inactive development branches and is not claimed
to represent loaded normal-play modules.

No renderer, material, timing, synchronization, appearance or native source was
changed. Rebuilt renderer still matches the fixed accepted alpha hash
`1bf0045d64b2cb6283bb20e9476b64e16c436e45b1ccd6e860377d3e2e53c16b`.
Native fallback, ExtraFrame, untimed play, recording defaults and all game/profile
checks are retained. Tester graphics preparation remains parked.

## Verification

- **761 regressions pass.** Added isolated legacy/application-first module identity
  checks, actual temporary-file recovery with diagnostic imports rejected, live
  game refusal and repeated recovery admission. Existing manifest, path, process,
  preferences and recovery tests pass unchanged.
- The normal coordinator lifecycle fixture now exits before first output, restores
  actual temporary graphics files, and immediately launches a second session
  against the same files. Error cleanup also passes. These are controlled process
  doubles, not real gameplay or universal relaunch acceptance.
- Native light worker qualification passes. Both existing 600-frame Strict and
  ExtraFrame multi-owner GPU fixtures pass with lights/damage, independent pixels,
  owner receipts and native state restoration. Source receipts renewed through
  existing qualification procedures; normal and completion/light diagnostic
  read-only preflight pass. Old recovery CLI `--help` works.
- New private package has **3,849 immutable files**, including 60 project Python
  modules. Original, moved Unicode/space and final-path native preflights pass;
  installed normal coordinator preflight passes without developer receipts.
- Rejecting import guard passes installed normal preparation/preflight and actual
  receiver creation/closure. All six helper implementations resolve from
  `code/src/runtime`; old forwarders and diagnostic modes are absent. Recovery
  remains free of broad-capture/test imports.
- In the new private checkout only, installed the qualified full-support proxy
  using the real graphics transaction, saved the original configuration and
  journal, then simulated interruption. Its actual `launcher.exe --restore`
  exited zero, restored immutable-profile graphics hashes and exact SFC INI
  baseline, removed off-mode working data, and passed two immediate native
  preflights. No pending recovery remains. The first test incorrectly expected
  restore console text in the parent's redirected pipe; it was absent across
  native elevation. Postchecks verified actual files/cleanup instead. No product
  code or permission checks were changed to accommodate this harness assumption.
- Installed CPU asset/material/light preparation passes with captured F-CA data:
  19,110 vertices, 58 groups, base/enhanced publication, no diagnostic task spans.
- Profiling-off installed GPU output and pre-output cancellation pass. Three
  colour/depth/owner planes match, and both jobs leave zero owned processes.
  Bootstrap readiness **3.141 s** is standalone initialization, not gameplay
  first-ship timing or an improvement claim.
- Package rendering/light defaults and seeded settings match the existing source
  configuration exactly. Accepted installation, developer game and previous
  alpha/organized/diagnostic-split checkouts were not upgraded.

Local evidence (ignored): `artifacts/alpha/runtime-support-*.txt`,
`runtime-support-source-equivalence.json`, `runtime-support-installed-gpu/`,
`runtime-support-installed-cancel/`. Stager record:
`preflight-fixtures/20261110-050252-805245/result.json`; its paths precede the
verified final move. GPU fixtures:

- `artifacts/remix-runtime/runs/20261110-050128-947471-return-fixture` — Strict.
- `artifacts/remix-runtime/runs/20261110-050225-606515-return-fixture` — ExtraFrame.

## Gameplay checkout accepted

New private copy: `artifacts/alpha/runtime-support-game`. Contains game assets
outside SFCRemix; never distribute this directory or use it as release ZIP input.
No SFC gameplay was launched by Codex. Sponsor reports this new copy looks good.
Recording is off and appearance is unchanged.

```cmd
cmd.exe /d /c call "C:\Project\SFC-Modernize Engine\artifacts\alpha\runtime-support-game\SFCRemix-Launch.cmd"
```

Sponsor observes the original ship, then the base replacement, then enhanced
materials, completing within roughly three seconds. The stages are individually
perceptible even though each appears fast. This is approximate visual timing, not
a measured breakdown, a newly attributed bottleneck or authorization for a loader
redesign. Record for later startup review; no loading behavior changed. Specific
early-exit/immediate-relaunch gameplay actions were not reported, so do not infer
that coverage from acceptance. Automated results above remain distinct.

Sponsor explicitly requests returning to this visible delay to determine its
reason. Parked in the existing Obsidian Parking Lot as "Visible
original/base/enhanced startup transitions". Reopen for the next startup
performance review after this organization increment. First use existing timing
and evidence to separate capture/base readiness, first replacement presentation,
enhancement publication, renderer consumption and enhanced presentation. Do not
attribute it to validation, asset preparation, Remix or presentation without
evidence; do not conflate it with the earlier 20-second Defender launch stall.

Prior acceptance of `diagnostic-split-game` remains separate evidence.
No repeated timing study is requested. Other specialized historical diagnostic
receipts are not blanket renewed. Public vendor/dependency closure and
second-machine release gates remain open.

# Session diagnostics separated from normal play

November 9, 2026, America/New_York. Evidence directories use November 10 UTC.
Parent checkpoint `4a0ce1e` committed on sponsor request before implementation.
Branch `codex/organize-repository-foundation`; sponsor accepts the new gameplay
checkout as passing and requests this increment be committed. No push, merge,
tag or publication requested.

## Actual normal path and ownership

`launcher.exe → src/launcher/bootstrap.py → src/session/coordinator.Session`
owns untimed native multi-ship play. ExtraFrame remains standard; current
appearance, weapon lights, damage and supported debris remain enabled by the
installed bootstrap. Identity, readiness, native fallback, protected-file checks
and interruption recovery remain functional application behavior.

| Responsibility | Current owner / shipped status |
| --- | --- |
| Normal arguments, startup, receiver/renderer preparation, source controller, native-play observation | `src/session/coordinator.py`; shipped |
| Verified child path, passive startup ordering, worker stop, graphics restoration, output-map lifetime, protected-file checks | Shared application `Session` methods, inherited by development modes |
| Game-exit monitor and bounded working-report state | `src/session/exit_monitor.py`, `reports.py`; shipped |
| Qualified proxy backup, atomic replacement and restoration | New `src/session/graphics_transaction.py`; shipped, with original transaction checks preserved |
| Semantic component qualification | New `src/session/component_qualification.py`; shipped; manifest in installed context, existing source/worker receipts in development |
| Broad/depth captures, private SDK/offset experiments, image/offscreen readers, tuning/test options, timed cues and capture analysis | `tools/session_diagnostics/modes.py`; development only |
| Old developer command path | `tools/remix_runtime/run_return_game.py`; lazy dispatcher, not shipped |
| Disk inventory and development build-input fingerprints | `evidence_storage.py`, `source_inventory.py`; narrow helpers without importing offline replay/GPU qualification runners; not shipped |

Normal play uses fresh semantic geometry/resources, retained assets, source
timing and native light state. Names such as `SFC_D3D9_SOURCE_TIMING` and
`SFC_NATIVE_LIGHT_DISCOVERY` also enable required functional IPC; removing those
would break the pipeline. Detailed completion/light recording remains false.
The normal loop contains no broad/depth/image capture selection, guided phases,
timed exit cues or historical relay-selection branches.

The legacy CLI routes explicit untimed performance/native play to the app without
loading development modes. Other existing options route to `DiagnosticSession`.
Legacy imports by diagnostic probes expose their established shared helpers.
Diagnostics retain their own preparation, limits and analysis, while verified
launch/restoration/mapping cleanup have one application implementation.

`broad_capture` reexports the extracted transaction functions for compatibility;
normal recovery imports `graphics_transaction` directly. Source qualification
inventories include both the app helpers and new diagnostic implementation, so
moving code cannot silently evade stale-source checks.

## Package boundary

The explicit production list contains **60 Python modules**, previously 59:
remove `broad_capture.py`, add the two functional application helpers. This is
ownership/dependency separation, not a claim that every mixed-purpose runtime
module has been split. Functional `present_calibration`, retained asset and
transport modules still coexist with dormant helpers. Further decomposition
belongs in another scoped increment.

New private playable checkout:

`C:\Project\SFC-Modernize Engine\artifacts\alpha\diagnostic-split-game`

It has **3,849 immutable manifest files**, 60 project Python modules, the existing
native launcher and matching fixed renderer hash
`1bf0045d64b2cb6283bb20e9476b64e16c436e45b1ccd6e860377d3e2e53c16b`.
Recording is off. The accepted installation, developer test game, original
`C:\Project\SFC-Alpha-Checkout` and sponsor-qualified `organized-game` were not
upgraded. The new copy is private, contains game assets outside the package and
must never be used as public ZIP input.

## Validation performed

- **758 regressions pass**. Real temporary-file rollback checks exercise normal
  exit and failure, early prewarming, untimed controller configuration, shared
  cleanup ordering, mapping closure and protected-file restoration.
- Diagnostic tests exercise actual parser/configuration behavior for broad and
  depth captures, source timing, Strict/ExtraFrame completion modes and tuning.
  Effect, early-model and damage probe entry points resolve their legacy imports.
  Existing invalid-combination tests and legacy/direct help remain passing.
- Existing completion/light diagnostic command and normal developer command
  pass their actual read-only preflight. No game is launched.
- Rebuilt native renderer matches the fixed accepted hash. Actual light worker
  tests pass, including untimed performance mode with no diagnostic sample files.
- Actual **600-frame Strict and ExtraFrame** multi-owner GPU fixtures pass:
  three owner receipts, two mesh resources including sharing, changing poses,
  independent colour/depth checks, native effects/text, state restoration, current
  lights and damage. Native policy qualification renewed from those results.
- Original, moved Unicode/space and final-path package preflights pass.
  Installed native coordinator preflight also passes without development receipts.
- A rejecting import guard verifies installed normal preparation/preflight and
  actual receiver creation/closure without requesting `modes`, `broad_capture`,
  `light_discovery`, depth search/snapshot analysis, offscreen/insertion capture,
  offline replay, return fixtures or asset diagnostic recording. These files
  are absent from the installed package where expected.
- Installed CPU asset preparation passes for captured F-CA data: 19,110 vertices,
  58 groups, base/enhanced image/material publication and actual light binding.
  Excluded diagnostic modules remain absent; no task spans are recorded.
- Profiling-off installed GPU startup/output passes: identical host/receiver
  colour, depth and owner planes; no owned processes remain. Bootstrap readiness
  was **3.219 s**. This is not gameplay/first-model latency or appearance evidence.
- Installed pre-output cancellation also passes: zero output frames and zero
  owned processes remaining after teardown.

Evidence: ignored `artifacts/alpha/diagnostic-separation-*.txt`,
`diagnostic-session-lifecycle.txt`, `diagnostic-split-gpu/` and package stager
`preflight-fixtures/20261110-034316-531950/result.json` (its path fields precede
the verified final move). GPU fixture directories:

- `artifacts/remix-runtime/runs/20261110-034124-322685-return-fixture` — Strict.
- `artifacts/remix-runtime/runs/20261110-034214-334022-return-fixture` — ExtraFrame.

Initial non-desktop regression execution hit shared-memory access denial and
Windows file-replacement denial. The proper desktop-session rerun passed; no
Defender exclusions, security changes or material workaround was introduced.

## Gameplay checkout accepted

Sponsor reports, "ok this one passes, commit", accepting gameplay in the new
diagnostic-split checkout. No additional symptoms reported. This is manual
gameplay acceptance; no new instrumented timing, cleanup or specific scenario
coverage is inferred. The prior six-minute acceptance remains separate evidence
for the previous build. The accepted checkout launches with:

```cmd
cmd.exe /d /c call "C:\Project\SFC-Modernize Engine\artifacts\alpha\diagnostic-split-game\SFCRemix-Launch.cmd"
```

External tester graphics preparation remains parked. Historical diagnostic
qualification receipts are not all renewed: stale specialized probes must use
their existing qualification procedures, not bypass their checks. Vendor
redistribution and second-machine release gates remain open.

# Scene transport and renderer startup separation

November 10, 2026. Parent `48b3766` on `codex/organize-repository-foundation`.
The asset-preparation checkout was accepted before this work. This increment
completes the main source reorganization.

## Ownership

- `src/transport` owns scene receipt, channels, catalog publication and
  acknowledgement, geometry and texture payload leases, light transport,
  startup tickets, owner rebind and the worker lifecycle.
- `src/assets/asset_content.py` owns reusable content identity.
- `src/rendering` owns the existing relay hierarchy, backend pin verification,
  child configuration and renderer lifecycle.
- Template comparisons, present calibration, detailed renderer reports and
  runtime acquisition remain in development tools. Existing tool entry points
  and imports forward to the application modules where applicable.

The installed allowlist contains 62 project Python modules. The comparison with
the parent found 100 unchanged function bodies, including receipt, buffer
handling, startup and stop paths. The four detailed finish methods delegate to
development reports. Backend input construction calls the relocated verifier
with the existing package and development pin checks. Shared layouts, native
source, timing policies and appearance configuration were preserved.

## Verification

1. Intermediate and final fresh packages exercised the real Windows scene and
   catalog mappings. A wrong owner left the scene slot unacknowledged. The
   valid owner received acknowledgement, and the independent peer read exact
   geometry and texture bytes. The catalog acknowledgement released payloads
   that were retained before consumption. Worker join and both mapping closures
   passed.
2. All 764 Python regressions passed. The native renderer build retained its
   SHA-256 `1bf0045d64b2cb6283bb20e9476b64e16c436e45b1ccd6e860377d3e2e53c16b`.
   Both 600-frame native insertion fixtures passed. Each verified three
   visible owners, exact fixture pixels and correct depth/text ordering.
   The fixtures included effect lights and damage, with the cohort receipt
   refreshed for both policies.
3. The functional package passed preflight before and after a move through a
   path containing spaces and a non-ASCII character, and again at the final
   checkout location. The manifest verified 3,851 immutable files. The
   installed CPU path prepared the captured F-CA with 19,110 vertices and 58
   material groups, including base/enhanced images and light binding. Normal
   imports excluded the diagnostic modules.
4. Installed standalone startup verified GPU output with all three planes
   identical between host and receiver. A separate run cancelled before
   first output. Both runs retired all owned processes with profiling off.
   The packaged lights and rendering defaults matched the existing profile.

Local evidence is under `artifacts/alpha/renderer-separation-*`. The native
fixture records are under `artifacts/remix-runtime/runs/` in
`20261111-043517-922922-return-fixture` (Strict) and
`20261111-043552-728314-return-fixture` (ExtraFrame). Fixture readiness is
standalone evidence. Gameplay startup timing remains unmeasured.

## Private checkout

```cmd
cmd.exe /d /c call "C:\Project\SFC-Modernize Engine\artifacts\alpha\renderer-transport-game\SFCRemix-Launch.cmd"
```

The checkout instructions covered replacement in a skirmish, early exit and
immediate relaunch. The sponsor reports the checkout complete and requests the
commit. No individual scenario results or timings were reported. The launcher
uses normal untimed play with recording off. The private checkout and prior
accepted copies are retained.

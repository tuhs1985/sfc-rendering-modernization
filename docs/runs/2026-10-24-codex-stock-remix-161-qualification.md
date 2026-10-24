# Run145 — stock Remix1.6.1 isolated qualification; materials prevent promotion

Interpretation update: [Run148](2026-10-24-codex-full-library-factor-controls.md) demonstrates the basic two-asset full library and emission work on stock1.6.1. The larger cases below remain unqualified, but their full/empty similarity must not be generalized into blanket replacement incompatibility. Historical measurements and decisions retained.

## Outcome

**PARTIAL — GPU return path compatible; accepted material binding NOT qualified.**
User authorized Run144's isolated runtime qualification/A-B, not a normal-path
upgrade or new architecture. Read current handoff, M1 gate disposition, Run138
loading results and Run144 NVIDIA/source review. FuelGuard attached through
trusted hooks; no task daemon/helper/subagent. Starting/current HEAD fe2eaf7;
prior cleanup/research documentation preserved unstaged. No commit/push.

[Curated dependency/test evidence](../reconnaissance/evidence/20261024-stock-remix-161-candidate.json).
No SFC/Toolkit launch. No accepted/test client mutation, normal dependency
replacement, driver/security policy change, appearance tuning or vendor patch.
Normal gameplay remains on1.5.2; do not offer the experimental candidate as an
approved sponsor launcher or claim sub2s/complete-material performance.

## Pinned dependency and isolated adapter

Official [release](https://github.com/NVIDIAGameWorks/rtx-remix/releases/tag/remix-1.6.1)
API supplied asset size/hash; outer release's runtime gitlink identifies
`0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0`. Downloaded only the x64 release
package557,087,446 bytes/SHA256
`7dd1d44492a609050e44b0e3581cec31135d1ed88b4a91123b4faae91955716a`.
Pinned [header](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/public/include/remix/remix_c.h)
API0.6.5/SHA25626a5607a07e8718298c35519e53bbc71d526186a947e5a2a5b613a0d6db04f3a.
Package DLL reports `remix-main+5a7eec84`; record both identifiers, do not pretend
the release-source gitlink independently attests the binary's build commit.
Actual API negotiation/required output registration/copy/defaults/light calls
and graphics tests succeeded against the published binary.

Dependency directory `artifacts/remix-runtime/deps/candidate-1.6.1`; full
192-file expanded inventory1,195,949,692 bytes with size/SHA256 manifest retained.
New x64 package has a small architecture dispatcher, `d3d9_x64.dll` and ARM64EC
renderer, not old package's `.trex` layout. Initial acquisition assumed `.trex`
and stopped after extraction; no runtime executed. Corrected using actual
archive layout, reverified every existing file against the pinned ZIP before
finalizing. Real x64 DLL SHA256
`c05c552e3f44597960891eff6c8482efcbde8573b15c2b900d3dc360e6cc1ad9`.
All package dependencies retained; no manual DLL stripping or managed-install use.

Candidate host compiles the SAME `d3d9_direct_host.cpp` with candidate header,
`/O2 /fp:precise /W4 /WX`, inherited compiler-option variables cleared, output
`artifacts/remix-runtime/candidate-1.6.1-bin`. Build receipt verifies host/header
and current source set. Normal host/header/binaries are untouched. No API-table
casting or mixing the Minecraft0.16header with this package.

`--runtime-candidate 1.6.1` exists ONLY on the standalone fixture and requires
multi-ship/prewarm. Changes module references in that supervisor process only;
no global environment or persistent runtime selector. Results carry full
dependency/host provenance. `qualify_multiship.inspect` explicitly rejects
experimental-runtime results as production qualification.

## Tests and useful measurements

All successful GPU cases use the actual bounded fixture/proxy/receiver with
three historical captured assets FCA/RCA/FDD plus a separate shared-FCA owner.
Fresh-process synthetic state, not a new SFC capture. Same current driver621.01,
frozen settings and unchanged native geometry/images. Sequential GPU execution.

| Fixture20261024 prefix | Runtime/case | Discovery → first matched composition | Steady draws/600 |
| --- | --- | ---: | ---: |
|162734-744847|1.6.1 initial|19.4430073s|594|
|162844-899263|1.6.1 late asset|3.0357646s|596|
|163311-033444|1.5.2 late control|4.5227150s|595|
|163513-020996|1.6.1 initial repeat|3.1037394s|594|
|163849-680806|1.5.2 normal Test regression|not promoted as a speed comparison|594|

Successful cases have all four instances admitted/ACKed/drawn, no asset partial,
identity/decode/projection errors, synchronized-buffer failures zero, preserved
native HUD/background/border/state, resize/device recreation, host/fixture/job
exit0 and zero owned children left. Existing vendor common-object teardown
warning remains (40old/43new observed); clean process shutdown is not proof of
all internal objects being freed. Runtime matching is not physical display
latency or settled/full-material readiness.

Five seconds after late-library publication: old control293audit records,
211paired/82without ship (82consecutive); candidate290records,287paired/
1without ship (plus reset/warmup). Promising continuity observation, but NOT
equivalent-material speedup because the material comparison below fails.
First candidate startup19.44s remains unexplained; subsequent faster runs do
not prove cold-cache cause. No cache clearing or statistical benchmark performed.

## Why the faster image cannot be accepted as equivalent

All432generated native-image/DDS files have identical SHA256 multisets across
the first candidate, candidate late case, old late control and candidate repeat.
Geometry signatures and frozen image/quality settings agree. Original maps,
material constants, normals, UVs and Remix-only row correction were not changed.

Late snapshots visually show differences in glow/material response. Over31,314
ship-region pixels, candidate vsold mean absolute RGB difference22.6455 on
0–255scale. This alone would not distinguish defaults/convergence/binding.
Three bounded diagnostics were therefore used:

| Candidate diagnostic | Fixture prefix | Mean absolute late RGB difference from ordinary candidate |
| --- | --- | ---: |
|Existing intentional empty material library|164252-930244|0.0577803 (16pixels differ by>3/channel)|
|Enable stock replacement setting BEFORE device creation|164453-663570|0.0629005 (12pixels>3)|
|Existing equivalent flat library instead of nested layers|164750-431954|0.0590471 (18pixels>3)|

All diagnostic runs completed the transport/graphics/cleanup test, but are NOT
appearance or normal-path qualifications. First/late BMPs remain available.
CONFIRMED: supplied library has no observable intended material effect in these
comparisons. STRONG HYPOTHESIS: candidate replacement binding/loading is inactive
or not matching our uploads. NOT CONFIRMED: exact failing hash/material resolver,
unsupported map, or native lighting equation. Do not blame texture conversion,
retune materials, discard emission/roughness maps or call this a shader fix.

Bounded release-source checks: `remixapi_SetConfigVariable` writes the User layer;
replacement-enable is a supported option. Texture upload still uses XXH3 by
default, with obsolete hashing false. Process environment did not contain
`DXVK_DISABLE_ASSET_REPLACEMENT`; no such setting introduced. These checks and
the startup-enable/flat tests rule out the simplest proposed fixes, not all
binding causes. Packaged-build/source difference remains a provenance caveat.

## Storage safeguard repair and evidence preservation

Two old-runtime fixtures163008-484211 and163602-483214 failed because the
authorized20GB reservation refused one asset, not because of renderer speed.
Preserve both partial reports; exclude them from A/B claims. Old fixture
preflight reserved192MiB final output but converter workers reserve256MiB each.
Now the OFFLINE fixture requires1GiB headroom for extended resources,768MiB
for ordinary multi-ship; other additive modes retain192MiB. The20GB total,
per-asset and log limits remain unchanged. A subsequent low-space diagnostic
was rejected BEFORE startup as intended; no additional partial run created.

Archived generated image bulk from15completed fixtures using existing exact-path,
decompress-every-entry/SHA256-verified procedure. Each432files/162,619,600 bytes
became10,051,597byte ZIP; net2,288,520,045bytes recovered before receipt overhead.
Source captures/packets, geometry, manifests, logs/results and comparison BMPs
remain unchanged. Each owning run has `generated-images-archive.json`, including
exact restore paths and hashes; ZIPs under `artifacts/remix-runtime/archives`.
This is recoverable generated-image cleanup, not deletion of the only evidence.
Dependencies are separately recorded, not charged as new runtime capture data.

## Files and verification

Added `tools/remix_runtime/runtime_candidate.py`,
`tools/d3d9_proof/build_candidate_runtime.ps1`,
`tests/test_runtime_candidate.py`, this record and curated evidence.
Modified `run_return_fixture.py`, `qualify_multiship.py`, HANDOFF.
Prior cleanup/research/README edits remain preserved. All unstaged/uncommitted.

495Python tests PASS (7.141s final full run), candidate x64 build PASS. Initial
unit invocation without workspace TEMP hit sandbox temp permissions; rerun with
existing `artifacts/test-temp` TEMP/TMP passes, not a code-quality failure.
Final normal-source fixture, qualification, preflights and final storage below.

Final-source normal fixture `20261024-164956-518231-return-fixture`: all4owners
840draws each, no partials, steady592/600, HUD/border/state/resize/recreation/
normal exit PASS, buffer failures0, native jobexit0/owned0. Both actual native
collector/worker modes passed through `qualify_multiship`; current-source normal
qualification refreshed from this NORMAL1.5.2 run, not a candidate result.
Performance and Test read-only game preflights PASS. Build PowerShell parser and
`git diff --check` PASS. Final governed evidence18,774,010,065bytes<20GB. Protected
managed/pinned runtime hashes remain unchanged. No GPU fixture or game left
running; process inventory requires read-only outside-sandbox access because
ordinary sandbox CIM query was denied (not a process-cleanup failure).

Exact next action: trace ONE known material's native texture hash through the
stock1.6.1 replacement lookup and resolved USD material, proving emission and
roughness respond before any gameplay promotion or speed claim. This is a narrow
compatibility question; no sponsor action, new model discovery or architecture
pivot is required. Normal game launcher stays on1.5.2.

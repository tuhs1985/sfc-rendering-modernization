# Run136 — qualify Remix's built-in loading route

Date: 2026-10-24 America/New_York. Work package: ordinary-D3D9 retained multi-ship startup performance; not replacement or a TRL/milestone claim. Sponsor authorized investigating/testing upstream asynchronous facilities. Read Run135 and authoritative handoff; FuelGuard attached through recent trusted hook (no daemon spawned). Starting HEAD `d40f8f230fc7504023e4a052c99a81b5a08ce6b4`, branch `codex/github-sanitized`, empty index; extensive prior uncommitted work preserved. No staging, commit, push, helper, new game capture or SFC launch.

## Question and supported findings

Can the pinned Remix1.5.2 built-in asynchronous mechanisms remove the remaining material-related first-image delay while keeping accepted geometry, image data and material interpretation?

Pinned source authority is commit `b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4` from the existing dependency manifest, not current upstream defaults:

- [Initializer](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_initializer.cpp) and [initializer settings](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_initializer.h): initial USD loading can run on a separate thread; shader prewarming/finalizing are built in.
- [Runtime settings](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_options.h): async asset loading and shader compilation default true, forced texture waiting defaults false. Async compilation can omit rendering until shaders finish; a responsive host is NOT proof of a complete image.
- [Scene manager](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_scene_manager.cpp), `onFrameEnd`, and [USD mod loader](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_mod_usd.cpp), `checkForChanges`: later material-file changes take an unload/load route from frame-end processing, with a1000ms change watchdog. The initializer's asynchronous thread is not automatically a separate asynchronous reload thread.
- [Texture manager](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_texture_manager.cpp): texture reuse is keyed by asset hash; preloading can schedule synchronous staging even when `alwaysWaitForAsyncTextures` is false. Our generated DDS files have one mip, so blindly disabling `preload_textures` does not establish an equivalent asynchronous pipeline or a fix.
- [Supported material API](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_remix_api.cpp), `CreateMaterial`: queues texture preparation on Remix's command stream and returns before completion. Its external material registry is distinct from ordinary-D3D9 replacement lookup. Shared underlying texture-cache reuse is a candidate, NOT qualified here; path normalization/hash identity and actual processing/completion must be verified before relying on it. No SDK mesh submission added.

CONFIRMED local configuration correction: the fixture's old `ENV` dictionary supplies `RTX_ENABLE_ASYNC_COMPILATION=False` to its observation wrapper, but `Relay.start_on_launch` creates the actual native-renderer environment from `os.environ`, not that dictionary. New `gpu/loading-inputs.json` receipts in baseline and experimental runs confirm the actual renderer inherited NONE of the four relevant overrides. Therefore the earlier suspicion that this test dictionary disabled the native renderer's asynchronous compilation is not supported. No production fix was justified by deleting that wrapper setting.

The native host starts with an empty material library, sleeps without Presents, then receives a complete changed library. Static code plus runtime texture-ingestion messages support the STRONG HYPOTHESIS that we encounter the later reload/staging path rather than gaining full initial-load overlap. This is not an exact attribution of the entire stall to USD traversal, staging, GPU allocation or shader work. `enableReplacementAssets=False` controls replacement use; it must not be assumed to prevent every initializer load.

Correction: Run135's318distinct entries are generated native-image/DDS file-content entries, NOT318distinct materials.

## Implementation and probe definition

All normal startup, source assets, material/light/image/quality TOMLs, hooks and UI behavior remain unchanged. New experiments are explicit standalone flags, require `--startup-profile --prewarm --multi-ship`, and cannot satisfy normal qualification:

1. `--loading-policy async`: supplies the pinned options explicitly to the ACTUAL renderer, with matching supported environment overrides. Asset loading, shader prewarming/finalizing and compilation on; forced texture waiting off. `blocking` control is implemented/tested offline at the configuration level but NOT GPU-executed this run. `inherit` changes nothing.
2. `--material-library flat`: supplies the same generated material definitions in one master file, rebasing image paths into existing worker directories. Does not modify/copy images, captured UVs, normals, geometry, material values, glow interpretation or the Remix-only DDS orientation correction. Duplicate material definitions must match, paths remain within the owned GPU directory,64layer/256group/report/metadata bounds enforced. Normal layered publication unchanged.
3. `--native-log-level error`: tests upstream logging overhead on the native host, retaining errors. Normal logging unchanged; this is NOT a promoted Performance setting.
4. Optional startup fixtures save ONE1920x1080-or-smaller BMP from the existing one-shot compositor readback after cohort settlement. No additional rendering-thread capture, continuous screenshots, Toolkit or game screenshot work. `fixture-ship.bmp` is sampled output, not a claim that every earlier first-arrival pixel was ready or pixel-perfect.

Files created: `tools/remix_runtime/loading_policy.py`, `tools/remix_runtime/material_library.py`, `tests/test_loading_policy.py`, `tests/test_material_library.py`, this run record and curated evidence JSON. Files modified preserving earlier edits: `tools/remix_runtime/multi_scene_relay.py`, `tools/remix_runtime/run_return_fixture.py`, `tools/remix_runtime/qualify_multiship.py`, `tools/remix_runtime/return_fixture.cpp`, `tests/test_startup_profile.py`, `docs/HANDOFF.md`, `docs/reconnaissance/pipeline-modes.md`.

## Controlled offline results

All cases use SAME three captured contents/four synthetic owners,60s menu-like idle, frozen accepted settings, no private warm triangle/empty-frame experiment. Full end-to-end clock starts at first fixture asset discovery and ends at first status1 matched compositor audit; it is NOT physical monitor latency. Separate processes/runs are subject to cache/driver/system variation; one sample per experimental configuration is not a statistical comparison.

| Case / UTC run prefix | Activation to first matching image | Discovery to first matching image | Largest bootstrap Present |
|---|---:|---:|---:|
| Normal inherited052333-179147 |3.020377s|5.110562s|2.108550s|
| Explicit async052518-243208 |3.623017s|5.721108s|2.621502s|
| Async + flat material library052832-362697 |2.990352s|5.096850s|2.238171s|
| Async + error-only native logging053101-681968 |3.407724s|5.458297s|2.651796s|

CONFIRMED: neither explicit asynchronous options, removal of USD sublayer composition, nor suppression of vendor informational/warning logging eliminated the multi-second stall. Do not infer that asynchronous loading is harmful from these single samples. Error-only case reduced native console88KB→53KB, but still blocked2.652s. No speed fix promoted; sub2s target remains OPEN.

Each case drew all four owners840–841times, had no asset partials, preserved exact synthetic background/HUD markers and untouched border, passed resize/recreation/state checks, and exited with native/fixture code0, guard stop_reason0, zero owned leftovers. Steady600frame windows delivered600/592/600/595matching returned draws respectively; misses must not be hidden by saying universally seamless. No SFC gameplay claim was made.

All432generated DDS/native-image files retain the same SHA256-content multiset (318distinct suffix/content entries); original material configuration is unchanged. Full-library images each had31315changed pixels against the known blue fixture background. Against inherited baseline, covered-region mean RGB absolute differences are0.075async/0.759flat/0.089error-only on a0–255scale;27/552/51pixels differed by more than3 in any channel. Thus not bit-exact, not a dropped-material speed trick, and not proof of universal appearance fidelity. Images retained ignored for inspection; async image visually inspected and showed expected textured FCA/RCA/FDD scene. Shared fourth owner has its own draw/ACK evidence, not an assumption that four silhouettes must be visible in this synthetic framing.

## Reproduction, limits and safeguards

Bundled Python `C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`; bundled pwsh `C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe`; VS2026x86 existing fixture build. TEMP/TMP=`C:\Project\SFC-Modernize Engine\artifacts\test-temp`. Pinned runtime/header manifest unchanged. Network read of the pinned GitHub tree was needed to locate the supported API implementation; no remote writes.

```text
pwsh -NoProfile -File tools/remix_runtime/build_return_probe.ps1
python -m unittest discover -s tests -p "test_*.py" -q
python tools/remix_runtime/run_return_fixture.py --multi-ship --multi-ship-resources --pipeline-mode performance --prewarm --startup-profile --menu-idle-seconds 60
# Same command plus, separately:
--loading-policy async
--loading-policy async --material-library flat
--loading-policy async --native-log-level error
# Final normal qualification control:
python tools/remix_runtime/run_return_fixture.py --multi-ship --multi-ship-resources --pipeline-mode test --prewarm --startup-profile --menu-idle-seconds 60
```

Native mapping/GPU tests ran through approved outside-sandbox execution, no security changes/UAC/game operations. Initial sandbox rebuild could not replace an existing generated import library (`LNK1114`, error5); same build succeeded outside sandbox. Existing wire37/expanded13/broad14/presentation22 native checks passed. Full Python suite482PASS, including bounds/path conflict checks, offline-only refusal, qualification refusal and unchanged source-image tests. No full Python suite concurrent with GPU fixtures. Existing285s owned native guard/100s long-idle fixture/20GB aggregate bounds retained; actual game90s/tactical/selection/workflow rules unchanged. No additional source capture or0x006AB410 hook.

## Storage and durable provenance

Before additional fixtures, recoverably compressed ONLY generated `.dds` and `texture-N.bin` files in completed Run135 fixtures044939-816883,045226-553264,045536-004234,045933-109500. Exact resolved files remained under each selected `gpu` directory; each archive was fully decompressed and every entry SHA256-checked before removing individual generated originals. Per run:432files/162,619,600bytes→10,051,597byte ZIP; total610,272,012bytes recovered. Archives: `artifacts/remix-runtime/archives/<full-run-name>-generated-images.zip`; each run retains `generated-images-archive.json` with per-entry relative paths/bytes/hashes and archive hash. Logs, results, packets, metadata, original assets, input captures and latest normal qualification050416 were not removed. Restore entries relative to the corresponding run directory. Not NTFS compression, not memory/VRAM savings.

## Decision and next exact action

No one-switch solution demonstrated. Keep all experiments off the gameplay path. The next smallest engineering action is qualify the pinned public `CreateMaterial` texture-preload/cache route with the SAME generated resources while individual assets finish preparation, WITHOUT SDK geometry or vendor patching. First prove underlying texture-cache identity/reuse (including resolved path spelling) and queued-work completion; API success alone is insufficient. Then measure the complete discovery→correct matched image clock. Do not add another dummy-scene warm-up, disable maps, alter appearance or count incomplete pixels as fast loading.

Final normal qualification, hashes, artifact budget, Git/index and process checks are appended below after completion. No sponsor gameplay is requested merely to repeat these offline findings.

## Final verification and additional upstream control

- Final-source NORMAL Test fixture `20261024-053427-819810-return-fixture`: all4owners802draws each/3contents, no asset partials,610paired records,594/600steady draws, exact synthetic HUD/background markers, border/state/resize/recreation PASS. Native/fixture exit0, guard stop_reason0, owned leftovers0. Post-activation first matching0.711248s, full3.018139s, bootstrap0.356749s/largestPresent0.041023s. This normal control has NO experimental loading/library/logging flags. It reinforces intermittence, not a speed fix from new experimental code. Result SHA256 `e24bc08dff2587f642c92aabcee91df61a3f8d827623080cfd20a66fdda8947a`.
- Additional upstream-only experiment: same async/layered/full-image configuration plus process-local `RTX_PREWARM_ALL_VARIANTS=1`; no source change or default alteration. Native log confirms `rtx.shader.prewarmAllVariants=True`. Run `20261024-053736-954145-return-fixture` did NOT complete: `Fixture time/output cap; Live fixture: Owned live GPU workflow failed to retire normally`. Supervisor elapsed110.079s including teardown; retained folder111,929,442bytes, below the32MiBnon-image output allowance after image exclusion, supporting TIME as the cap. No first matched image/clean API-shutdown or `gpu/job-result.json` receipt; only2prepared content directories/3admitted owners appeared. Do NOT include as a valid timing comparison, claim complete input equivalence, declare shader prewarming the proven cause, or promote this setting. Partial asset-preparation/retirement details are unavailable because failed superclass finalization prevented the richer multi-scene report. This evidence deficiency is recorded, not repaired by inventing a successful teardown. Result SHA256 `4c5973bbbc157d9ebc4a3bbe48bda3021138fb3b86cfa2c8265401e6a862ec4c`. Approved outside-sandbox process inventory after cleanup found NO owned host/receiver/fixture/guard or SFC processes left; forced cleanup is not normal graphics teardown.
- Reproduction of that extra experiment: set `RTX_PREWARM_ALL_VARIANTS=1` only in the child PowerShell environment before invoking the explicit async command above. Do not set it globally. All-variant prewarming is officially higher-cost and unnecessary variants are intentionally off in normal operation. No blind repeat requested.
-482PythonPASS; exact-source normal multi-ship qualification refreshed from053427, native light queue/decoder/shared-worker checks PASS. Both Performance/Test read-only game preflights PASS without launching any game. Initial native build checks37/13/14/22PASS; existing native64host binary unchanged by this increment.
- Accepted/copy client SHA256 `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`; copied proxy `E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7`, unchanged. No accepted installation, game settings, images or light/material baseline files edited.
- After the four successful Run136 comparison cases were analyzed, their generated images were archived using the SAME exact-path/per-entry-decompression/hash verification procedure described above. Each432files/162,619,600bytes→10,051,597byte ZIP; a further610,272,012bytes recovered. One-shot BMPs/logs/results/manifests remain directly available; archived DDS/native-image files restore via each run's `generated-images-archive.json`. Total across8completed experiments:1,220,544,024bytes recovered, all recoverable. Latest normal053427 and failed all-variant053736 raw output kept intact. Artifact inventory18,763,498,782bytes<20,000,000,000; no allowance increase.
- HEAD/index unchanged, all prior/current work unstaged/uncommitted, no push. `git diff --check` PASS. Raw/generated images ignored. No active owned game/test/renderer at finish. The next exact action remains the public material API texture-cache reuse qualification above; still no gameplay or broader rendering implementation required.

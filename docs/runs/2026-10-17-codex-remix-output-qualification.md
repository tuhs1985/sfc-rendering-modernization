# Codex run — standalone Remix output and prepared return-path qualification

Run ID SFC-RETURN-20261017-01; date2026-10-17 EDT. Active task: approved
In-Game Remix Integration, first prerequisite gate ONLY. Starting HEAD e96765a;
index empty; inherited uncommitted HANDOFF and October16 authorization checkpoint
preserved. No SFC interception, copied-install modification, suppression or
Toolkit development authorized before this gate passes. No staging/commit.

Sponsor resumed with credits. Fuel Guard attach attempted using actual thread;
no task daemon spawned. Prior quota checkpoint is historical, not a technical
failure. No local-coder-helper, delegation, requirements change or driver update.

## Authority / inputs

- docs/HANDOFF.md, docs/runs/2026-10-16-codex-return-path-execution-checkpoint.md
- docs/m1/m1-trl4-integrated-component-validation-plan.md and current amendment
- docs/reconnaissance/live-scene-contract.md / probes/LIVE-SCENE-001.md
- Completed fresh-scene evidence referenced in authoritative handoff; not rerun.
- Official pinned SDK and implementation sources listed below; source names are
  not evidence that runtime output actually contains rendered geometry.

## Dependency and environment baseline

Official release remix-1.5.2, rtx-remix tag commit
26a8fdc7a0574d8ec9d438b05be4667d18dc11aa. Its dxvk-remix submodule and peeled
dxvk-remix release tag both identify b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4.
Release archive231778218B; SHA256
cc424be4dd1a0c6fd922bc6a7f8e5f6582baea7043a38afa6686d8b6faabad01.
SDK0.6.4 remix_c.h SHA256
E623E4956A76894EEEF02361334C7C0458D4EC8BF49F729EC9038C36128BBF47.
x64 .trex/d3d9.dll SHA256
F7C310821AA98BCDFDEC120330B0A89457B7C5EBA58D21464AF32639611C809F.
Runtime reports remix-1.5.2+68edea01; that suffix is not a resolvable public
dxvk-remix commit (API422). Do not claim binary reproducible from the public
source commit. Official release association plus successful API initialization
establishes the pinned release/SDK association, not binary/source identity.

GPU NVIDIA GeForce RTX4070Ti, driver617.42 (native nvidia-smi). VS2026 Community
18.7.3 x64 vcvars64/cl C++20 /EHsc /W4 /WX; vendor example C11 /W3. PowerShell
7.6.5 and bundled Python3.12.14. Accepted client independently read SHA256
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29,
unchanged from accepted baseline; no game process launched or binary written.

Dependencies stored only in ignored artifacts/remix-runtime/deps, not installed
in game or Toolkit. Initial GitHub dxvk-remix/releases/latest404 corrected to
official rtx-remix release repository; not evidence of runtime infeasibility.

## Question / experiment definition

Can SDK-rendered output be exposed through a reusable GPU resource to native
D3D11 with explicit ownership/synchronization? Probe REMIX-OUTPUT-001 records
configuration, trigger, cleanup, limits and progressive changes BEFORE use.
Standalone probe only; reverse-direction import is a public API alternative,
not a translator switch or runtime patch.

Material static findings:
- CopyRenderingOutput enqueues a blit only if internal source image exists;
  success does not establish produced pixels.
- D3D9 common texture exports OPAQUE_WIN32_KMT, and its metadata helper uses
  SharedGpuResource device IOCTLs. Native Windows sharing must be tested.
- API D3D9 device exposes no public Vulkan device/queue export through its
  QueryInterface. Raw external-swapchain VkImage/semaphores are not transferable
  Win32 handles; no unsupported cast or private offset access attempted.
- RtxContext skips ray tracing during asynchronous shader compilation.
- Pinned C++ opaque material defaults alphaTestType=7; our initially zeroed C
  material used0/NEVER with useDrawCallAlphaState=false. Corrected before treating
  black output as evidence against the runtime. No architecture conclusion from
  those early black snapshots.

## Material commands / files

From repository, using bundled PowerShell7 -NoProfile -File:
1. tools/remix_runtime/prepare_runtime.ps1 (host network required)
2. tools/remix_runtime/build_output_probe.ps1
3. tools/remix_runtime/run_output_probe.ps1 -Mode sharing or -Mode rendering
4. tools/remix_runtime/run_vendor_example.ps1 (unmodified SDK control)

Host-shell permission needed for network/desktop GPU, not a security-policy
change or sponsor UAC action. Native process runner uses hidden launch;
rendering diagnostic can show its own nonactivating window. No desktop overlay
or separate window is counted as in-game integration.

Created/modified: tools/remix_runtime/{prepare_runtime.ps1,output_probe.cpp,
build_output_probe.ps1,run_output_probe.ps1,run_vendor_example.ps1}; probe
docs/reconnaissance/probes/REMIX-OUTPUT-001.md; this record and HANDOFF.
Generated binaries/source downloads/caches/results under ignored artifacts.

## Observed evidence (UTC directory IDs)

All directories under artifacts/remix-runtime/runs; exact exe/DLL hashes,
exit statuses and durations in result.json; detailed steps in stdout/vendor log.

| Run | Question / result | Confidence |
|---|---|---|
|20261017-040910-965|Remix-created RGBA8 shared texture accepted; native D3D11 OpenSharedResource E_INVALIDARG0x80070057. Exit1,19.43s.|CONFIRMED|
|20261017-041123-970|Actual triangle attempt with default AI settings lost GPU device after four successful Presents. VK_ERROR_DEVICE_LOST; watchdog terminated owned probe at120.24s.|CONFIRMED failure; cause unproven|
|20261017-041335-977|RGBA8/BGRA8/RGBA16F forward exports all rejected; native D3D11 sharing control passed. Native-created BGRA8 imported into Remix successfully; no pixel validation yet.|CONFIRMED API results only|
|20261017-041415-810|Native-created shared BGRA8, imported by Remix, GPU-written three changing sentinel colours, read by independent D3D11 device. Exact BGRA139,71,19/38/57,255. D3D9 EVENT completion before D3D11 consumption; reused same allocation. Exit0,2.34s.|CONFIRMED same-process GPU reuse; not Remix ray tracing/cross-process|
|20261017-041442-844|DLSS/RR off, first snapshot black; later abnormal exit0xC000041D. Early material alpha-test defect still present.|CONFIRMED observation, not runtime limitation|
|20261017-041601-627|Visible window/message loop/light/pacing,32frames; snapshots still black; abnormal exit0xC000041D.|CONFIRMED, alpha defect still present|
|20261017-041708-788|Explicit indexed mesh and window-before-unload order; black snapshots, same abnormal exit.|CONFIRMED, alpha defect still present|
|20261017-041846-449|Synchronous shader compilation; black snapshots, same abnormal exit. Shader readiness alone did not fix earlier probe.|CONFIRMED, alpha defect still present|
|20261017-041945-596|Corrected alpha-test and restored owned window procedure before Shutdown; crashed during fifth scene submission,0xC0000005,9.52s. Windows Application event1000 identifies nvoglv64.dll617.42, offset0xF10CF4.|CONFIRMED fault site; driver vs input/runtime cause unresolved|

Earlier0xC000041D events identify pinned Remix d3d9.dll offset0xFFCDA, with
preceding0xC0000005 entries. Restoring the owned procedure addresses a host
teardown risk but is not yet independently verified as the complete fix.
Vendor-control outcome pending at this intermediate checkpoint.

Limits: each standalone run120s/32MiB,16MiB warning, no unbounded transcript.
Native private renders retain at most two256square BMP verification snapshots,
262198B each; not a CPU image-return mechanism. Largest completed per-run output
so far556145B including snapshots; no multi-GB trace. Dependency archive221MiB
plus expanded vendor files are setup artifacts, not a runtime capture. Vendor
DLL hardlink190838384B is immutable dependency, excluded from evidence/log budget.

## Validation / current adjudication

Native x64 strict build passed after fixing shell quoting and a local brace
error. A rebuild while the prior owned probe was active correctly failed to
overwrite its locked EXE; rebuilt after watchdog exit. Existing Python93tests
PASS with TEMP/TMP directed to ignored project scratch; initial system sandbox
temp location caused55 permission errors, not test assertion failures.

Preliminary result: useful public reverse-import route demonstrated, but FIRST
OUTPUT GATE NOT PASSED. No cross-process proof, verified actual rendered pixels,
game copy/compositor, returned-image proof or ship replacement. Driver/library
fault and actual rendered output remain unresolved. Do not promote colour-clear
sentinel to ray-traced provenance. Do not run SFC or suppress native ships yet.

Final validation/state and next action will be appended after the bounded
vendor control is adjudicated. Implementation/evidence remain unstaged.

## Continued execution — first prerequisite demonstrated

- Unmodified official example20261017-042137-854-vendor exited0 after32frames,
  15.44s. Thus rejected hypothesis that all SDK rendering fails on this machine.
  No pixel claim from vendor process exit alone. Source hash869A06EA...F23EF7.
- Default-material project control20261017-042319-762 produces real green
  triangle,7442green pixels in both snapshots with distinct hashes, exits0.
  Custom-material crash is a separate unresolved input/runtime/driver issue;
  not a general absence of rendering/output capability. No AI setting fix alone
  established. Actual default-material output is corroborated by copied pixels.
- Cross-process20261017-042903-415 passes: actual SDK final-colour blit into
  consumer-created BGRA8, explicit EVENT completion, publication, independent
  D3D11 GPU copy/read verification, exact hashes2940567784554992920 and
  10556254945323023720,7442green pixels, centroidX97->158. Same allocation reused,
  child cleanly exits, host Shutdown returns0/exit0. Two readbacks per process
  are bounded diagnostics, NOT CPU pixel transport or production screenshots.
- Added tests/remix_output_contract_tests.cpp and output_channel.h.30native
  checks cover header/version/size/dimensions/format/sequence, busy/stale ACK,
  disconnect, actual one-ACE current-user SID DACL and same-user reopen. Restricted
  sandbox same-user reopen failed; NORMAL HOST account passes all30, without
  relaxing ACL. This is consistent with existing IPC sandbox policy, not a
  reason to broaden permissions.
- Fault20261017-043456-123 delays consumer6s against5s ACK wait, rejected;
  fault20261017-043505-805 exits consumer during first transfer, rejected. Both
  log disconnected/timeout/error and SDK Shutdown0, parent exits1 as EXPECTED.
  Fresh recovery20261017-043509-524 exits0 with exact joins and X97->158 again.
  These are meaningful fault outcomes, not renderer success for the fault runs.
- Core standalone output prerequisite CONFIRMED for this finite diagnostic:
  genuine rendered pixels, reusable GPU transfer, current-user IPC, independent
  process, producer/consumer completion, failure and recovery. Not the in-game
  returned-image gate or replacement gate; device-loss/resize/compositor-specific
  handling still requires implementation/testing before game proof.
- Original accepted client SHA reread unchanged. Windows11Home build26200;
  accepted ReShade6.7.1.2133 SHA256
  E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7.
  Matching ReShade tag source8cf85bd12d56697d756d4fcb45e501f5d1b540fa; read-only
  exports/log/source inspection supports candidate addon32 path. No proxy edited.
- Read-only launcher discovery found HKCU SFCLauncher/Paths Client2Op and
  Server2Op point to accepted installation. Test-copy launcher must NOT be
  assumed relocated. No registry write performed. Entire accepted tree5781files,
  3063787385B; no copy made at this checkpoint.
- Host process inventory after tests has no owned output_probe/vendor/game
  process. Current build scripts require normal-user host for the actual IPC
  test (not the restricted sandbox token); no UAC/security-policy changes.

Implementation now additionally includes output_channel.h and native contract
tests, plus output contract documentation. ReShade headers/source downloads are
ignored inspection inputs only; no ReShade addon implementation yet. Current
exact next action is isolated-copy launch qualification plus supported compositor
preparation. Scope remains approved return-path work; no renderer architecture
switch, original suppression, helper invocation, requirements change or commit.

## Continuation — standalone gate passed; additive game proof prepared

Earlier paragraphs are chronological checkpoints, superseded where noted here.
Standalone x64 Remix -> x86 native consumer20261017-044740-621 passed exact
GPU pixel joins, establishing game-bitness consumer compatibility. Independent
test copy C:/Project/SFC-Remix-Return-Test:5781files/3063787385B, no hardlinks.
Ignored test-install/manifest.json and source-copy-files.json preserve inventory
and hashes; original/copy clientSHA unchanged. Read-only scoped launcher IL
confirms global configured Paths targets original; native copied client is
launched directly instead, with path/hash checks before resume. Actual SFC
startup/gameplay qualification remains pending, not inferred from offline fixture.

ReShade ABI20261017-044931-572 passed API18/ImGui19250 against copied unchanged
6.7.1.2133 proxy. Official source proves limited build intentionally skips
automatic addon32 discovery; fixture20261017-050102-615502 confirmed no image.
Pivot to SUPPORTED external registration of startup-loaded SFCRemixReturn.dll,
allowed init/destroy/overlay events only. Never replaced proxy or enabled
restricted application events. ImGui background image has no input widgets.

Own DllMain128KiB thread-entry stack caused offline stack overflow; fixed bounded
1024char process-attach helper, staticCRT thread notifications intact. Fixture
050513-575921 optional bounded trace/minidump88717B corroborates own __chkstk
RVA0x5827; no SFC exception handler/debugger installation. Corrected fixture
050652-241585 passed all5phases,353frames,state_errors0. Not an SFC/engine defect.

Official Detours4.0.1 source e4bfd6b03e50de46b47abfbd1e46b384f0c5f833,
archiveSHA FEF0B17C5C3C9356FB8BA7366A3B196149DAADD131FB6A92ABEDA1CB4D3B9B85,
used ONLY startup process-memory import/restore. `return_launcher.exe` verifies
whitelisted client path+SHA/componentSHA, creates suspended, verifies actual
child path+clientSHA, resumes. No adopted process, disk-client patch or hot
callback registration. Fixture051414-393789 passed startupRestored/Verified1,
228frames,state_errors0,allphases. Native source /W4/WX built with pinnedSDK.

Hardened v2 state256B/4KiB user-only mapping: monotonic producer/ACK, new resource
epoch,renderEpoch/presentedEpoch, native resource lease+descriptor validation,
nonblocking consumer GPU-fence ACK, resource recreation discards old-generation
output. Two256square textures524288B. Latest fixture052545-410229:
223frames,state_errors0, enabled7425green,disabled0,resized7425,recreated7429,
disconnected0, original blue region preserved throughout. Hostexit1 INTENTIONAL
owned-renderer crash test,fixtureexit0. FinalREADY0,error0,clearCount3;
all5phases11111. Three successful fixtures do not prove hardware driver-loss
recovery. Native header/freshness/dimensions/DACL tests pass; malformed guards are
not claimed as GPU resource-exhaustion injection. Custom material/driver fault
remains unresolved; minimal default-material diagnostic avoids it legitimately.

Prepared run_return_game.py defaults read-only. --execute requires existing
elevated parent, absent existing game, matching frozen copy/runtime; noUAC or
global settings. start_return_image_session.ps1 PS5->PS7, bounded build+run300s.
Automatic existing one-shot semantic gate004162B9 restored/unloaded before
arming;90sON30/OFF15/ON15/renderer-stopOFF30, then two-beep normal-exit request.
Copied client starts with normal existing compatibility layer process-local,
explicitly refuses RUNASINVOKER. Accepted installation read-only throughout.
Default diagnostic geometry hook OFF, no original draw suppression. Runner
records source/copy hashes, registry paths, phases, sequences and controller
cleanup state; timeout NEVER force-kills SFC or responsible gate controller.
Actual UI corner appropriateness/normal exit/disabled+removed game behavior
are pending sponsor runtime evidence. Contract/runbook document exact bounds.

### Reproduction and files

- tools/remix_runtime: prepare_runtime.ps1,build_output_probe.ps1,output_probe.cpp,
  output_channel.h,output_consumer.cpp,run_output_probe.ps1,run_vendor_example.ps1,
  prepare_test_install.ps1,inspect_launcher.ps1,prepare_reshade_sdk.ps1,
  reshade_abi_probe.cpp,build_return_probe.ps1,return_wire.h,return_channel.py,
  return_host.cpp,return_addon.cpp,return_fixture.cpp,run_return_fixture.py,
  prepare_detours.ps1,reshade_registration.def,return_addon.def,
  return_launcher.cpp,run_return_game.py,start_return_image_session.ps1.
- tests: remix_output_contract_tests.cpp,remix_return_wire_tests.cpp,
  test_remix_return_channel.py,test_remix_return_launcher.py.
- Curated docs: REMIX-OUTPUT-001.md,REMIX-RETURN-001.md,
  remix-output-contract.md,remix-return-contract.md,this record,HANDOFF.md.
  Inherited2026-10-16authorization checkpoint preserved. All dependency/source
  downloads, compiled outputs, native dumps/captures/testcopy manifests ignored.
- Commands (repo root, bundled executables): prepare_runtime.ps1;
  prepare_reshade_sdk.ps1;prepare_detours.ps1;prepare_test_install.ps1;
  build_output_probe.ps1;run_output_probe.ps1 -Mode crossprocess;
  build_return_probe.ps1;python tools/remix_runtime/run_return_fixture.py;
  python tools/remix_runtime/run_return_game.py (NO --execute;preflightPASS).
- `python -m unittest discover -s tests -p test_*.py`:97testsPASS before3new
  launcher negative cases; those3alsoPASS (original-install/wrongSHA/mode refusal,
  nochild). TEMP/TMP set to repo artifacts/remix-runtime/test-temp due restricted
  defaultTemp access. Full final count recorded in validation follow-up below.
- All new PowerShell parsed successfully; git diff --checkPASS (LF/CRLFwarning
  only). Native build_return_probe /W4/WX, return-wire tests and latestfixturePASS.
  Existing M1 native build/regressions running at this checkpoint; final result
  recorded below. No original semantic-hook architecture redesigned.

### Decision / limits

CONFIRMED finite standalone prerequisite and offline same-proxy compositor.
READY FOR SPONSOR RUNTIME TEST, not in-SFC RETURN PATH DEMONSTRATED, not ship
replacement and not formal TRL completion. No gameplay launched during this run.
Exact next action: prepared runner -> two-ship skirmish -> observe diagnostic
image and ordinary controls -> exit at cue -> adjudicate evidence/report.
Only after actual returned-image gate may owner suppression/coverage/depth be
investigated. NoToolkit polish,appearance tuning,renderer switch or helper use.
HEAD e96765a; all authored changes UNSTAGED, no index entries, NOcommits.

## Final offline validation / park

- Existing tools/m1_component/build_m1_component.ps1 exited0: contracts,tint,
  tint lifecycle,shading-off,corners,fresh-copy bounds,surface schedule and
  cleanup,mesh serialization/pass-through,WINMM forwarding allPASS; gate and
  controller rebuilt. No M1 semantic source changes.
- Full Python100testsPASS,1.603s with project TEMP/TMP. New3launcher cases
  reject originalinstall,wrongSHA and invalidmode before verified child creation.
- Read-only game-runner preflightPASS after final rebuild. All newPS parsesPASS;
  native return /W4/WX and wire testsPASS; latest GPUfixture all5phasesPASS.
  No owned host/fixture/loader/consumer/game/controller running at final inventory.
- Added versionable remix-return-dependencies.json with exact source/runtime/
  proxy pins, environment, process-local settings and manifest locations.
- Archived139selectedJSON/log/text/BMP/minidump files10412505uncompressedB to
  artifacts/remix-runtime/archives/20261017-return-qualification-evidence.zip,
  465540B. Vendor binaries/shader caches excluded. Original small evidence kept
  for review; no material evidence deleted. No continuous screenshots or multiGB
  capture generated. Test copy3.06GB deliberately retained, not a trace dump.
- Final Git HEAD e96765a,index empty; HANDOFF modified plus new source/tests/docs
  listed above, inherited October16checkpoint retained. No staging/commit.
  Accepted/copied client SHA reread unchanged. `git diff --check` passes,
  only harmless Git line-ending warning. No original game artifact modified.
- Remaining sponsor action: execute prepared test once, enter familiar skirmish,
  observe green image+normal game and exit after two beeps. No ship-replacement
  implementation authorized by this offline success. READY FOR SPONSOR RUNTIME
  TEST is the current result; actual returned-image gate remains pending.

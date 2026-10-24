# Run135 — actual rendering warm-up and material-loading isolation

Date:2026-10-24 America/New_York. Active work: bounded D3D9 retained multi-ship startup performance, not milestone/replacement completion. Sponsor authorized testing actual render-pipeline warm-up before fresh ship data arrives. Read Run134 authoritative handoff/startup profiler contract and results. FuelGuard attached through trusted hook; no task daemon/helper/subagent. Starting HEAD `d40f8f230fc7504023e4a052c99a81b5a08ce6b4`, branch `codex/github-sanitized`, index empty; extensive prior work preserved unstaged/untracked. No commit/push authorization.

## Question, scope and implementation

Can initializing actual rendering, rather than only the devices, remove the intermittent first-picture stall without changing captured geometry, images or visual settings?

Added `tools/d3d9_proof/render_prewarm.h`, an explicit experimental external-host-only warm-up. `--render-prewarm empty|triangle` is available only on the standalone fixture with `--startup-profile --prewarm --multi-ship`. Normal game relay strips its environment flag. Exact-source qualification rejects either experimental mode even if other GPU checks pass. No normal startup/appearance change or warm-up promotion.

- Empty:24clear/BeginScene/EndScene/Present frames, no geometry.
- Triangle:one private3vertex/96byte ordinary-D3D9VB and1x1white texture;24triangle frames then32empty retirement frames. No saved ship/template, source identity or semantic packet substituted. Shared game receiver is not created until AFTER warm-up; no warm-up image published. State block restored and GPU completion queried before idle/activation.10sloop bound plus existing owned-job bound; no game-thread wait, disk/image conversion or new game hook. GPU-side retaining of a warm primitive across all future cases is NOT universally qualified; another reason not to promote this experiment.
- Both run under existing frozen image/quality settings, with actual ship material library still empty/disabled. Same original24asset-dependent bootstrap Presents/10ms sleeps remain after activation. Thus experiments do NOT silently remove any readiness check or claim output correct because some pixels arrived.
- Added diagnostic-only `--isolate-initial-material-library`: builds the SAME assets and images but retains an empty master material stage instead of publishing its imports. It deliberately changes rendering, is guarded offline-only, recorded in receipt and rejected by normal qualification. It is NOT a performance preset or proposed visual compromise.
- Extended existing optional startup profiler by4points around the first fully qualified multi-ship Draw/Present/copy/ACK, separate from its single-asset bootstrap. This distinguishes early output from the actual cohort; no steady-state trace added, capacity remains128.

No light/material/image/quality TOML changes, no new discovery, original suppression, vendor patch, wrapper switch, proxy-forwarding change, supersampling or architecture selection. Scene capture remains original validated path. Experimental flags OFF by default; no new game launcher option for warm-up.

## Results and confidence

All experiments use the established3captured contents/4synthetic owner instances, frozen settings and60s menu-like idle; they never launch SFC. Timings are QPC, not physical display latency.

| Standalone case | Pre-idle warm-up | Post-activation to first matching compositor image | Discovered asset to first matching image |
|---|---:|---:|---:|
| Empty044939-816883 |0.571502s|2.897230s|5.073285s|
| Private triangle045226-553264,full materials |0.482726s|3.205893s|5.509865s|
| Private triangle045536-004234,material library withheld |0.472225s|0.717925s|2.869380s|
| Normal startup045933-109500,full materials,no warm-up |none|3.404932s|5.757902s|

CONFIRMED:

- Empty frames did not trigger the logged ray-tracing GBuffer initialization before ship activation. Its post-activation bootstrap still took2.581191s, including one2.065632sPresent block.
- The private triangle DID trigger ray-tracing initialization before the minute idle and ship data. It still suffered a later2.473487sPresent block; post-activation bootstrap2.890921s. Merely warming the rendering core is not a sufficient fix in this case.
- With the same private warm-up but empty material master stage, bootstrap0.388866s/largestPresent0.033354s, post-activation first matching output0.717925s. All432generatedDDS/nativeimagefiles have the SAME SHA256-content multiset as the full-material triangle case (318distinctsuffix/hash entries). Conversion/image production was not skipped to manufacture this timing. The intentionally withheld runtime material publication is the isolated path difference; OS/cache conditions remain uncontrolled.
- The withheld case's sampled changed-pixel count170015 differs from normal31315. It loses the accepted material policy; transport still functions but it is NOT acceptable appearance or a speed acceptance result. Its total2.869s also still exceeds2seconds. Do not promote it or claim universal primitive-retirement fidelity.
- Full-material cases rendered4owners841times each, no asset partials, native/fixture normal exit,0owned leftovers; normal HUD/border/resize/device recreation checks passed. Full-material image samples remain31315changedpixels with untouched border. This is fixture-scope evidence, not pixel-perfect fidelity of the first actual game frame.
- Private native memory after triangle warm-up~4.19GiB versus~2.21GiBdevice-ready;~4.47GiBat later activation. Early warm-up holds more memory during menus; it is not free. No peak/leak or Run131allocation-cause conclusion.
- Normal full-material control045933 had only0.568161sbootstrap but3.404932spost-activation to matching output. Therefore the expensive work can occur AFTERbootstrap when later cohort assets are first used. Do not attribute every3second gap exclusively to the24initialframes.

STRONG HYPOTHESIS: initial generated USD/material/texture ingestion or first-use work is a major contributor to the remaining stall. Direct comparison and vendor texture-ingestion logs support narrowing to that path. Exact share of USD traversal, texture upload/format preparation, shader work, logging or presenter synchronization is NOT isolated. Intermittent fast full-material cases from Run134 remain counterexamples to a fixed mandatory load time. No unsupported claim that any one vendor setting fixes it.

The present material bridge produces per-asset material stages with `inputs:preload_textures = true`, generated diffuse/emission/roughnessDDS and a single committed master import stage after the initial batch is prepared. Runtime API enablement is fast but NOT a completion fence. Correct first-image acceptance must not be replaced with an early image that lacks requested materials.

## Tools / commands / bounds

Bundled Python `C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`; bundled pwsh `C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe`; VS2026x64 existing `build_direct64.ps1`; pinned Remix1.5.2/current SDK and existing native D3D11/ReShade standalone fixture. TEMP/TMP=`C:\Project\SFC-Modernize Engine\artifacts\test-temp`. Approved outside-sandbox current-user mapping/GPU tests only; no Windows security changes or unrelated app termination.

```text
pwsh -NoProfile -File tools/d3d9_proof/build_direct64.ps1
python -m unittest discover -s tests -p "test_*.py" -q
python tools/remix_runtime/run_return_fixture.py --multi-ship --multi-ship-resources --pipeline-mode performance --prewarm --startup-profile --render-prewarm empty --menu-idle-seconds 60
python tools/remix_runtime/run_return_fixture.py --multi-ship --multi-ship-resources --pipeline-mode performance --prewarm --startup-profile --render-prewarm triangle --menu-idle-seconds 60
python tools/remix_runtime/run_return_fixture.py --multi-ship --multi-ship-resources --pipeline-mode performance --prewarm --startup-profile --render-prewarm triangle --menu-idle-seconds 60 --isolate-initial-material-library
python tools/remix_runtime/run_return_fixture.py --multi-ship --multi-ship-resources --pipeline-mode test --prewarm --startup-profile --menu-idle-seconds 60
```

Analyze via `startup_profile.analyze(folder)` and firststatus1 `D3D9-SYNC-BUFFER-001.bin` record. Complete result/console/fixture/job logs retained ignored; small curated evidence versionable. Existing32owners/64revisions/four2MiBslots/256MiBbacking/20GBdisk/128pointprofile limits retained; no continuous image dump or diagnostic geometry hook. Each standalone long-idle experiment100s bound, ordinary fixture60s; actual SFC workflow/tactical limits unchanged. No expensive full Python tests concurrent with GPU.

Files created:render_prewarm.h,thisrecord,newcuratedJSON. Files modified preserving prior edits:`tools/d3d9_proof/d3d9_direct_host.cpp`, `tools/d3d9_proof/startup_profile.py`, `tools/remix_runtime/multi_scene_relay.py`, `tools/remix_runtime/run_return_fixture.py`, `tools/remix_runtime/qualify_multiship.py`, `tests/test_startup_profile.py`, `tests/test_asset_preparation.py`,handoff/modecontract. No engine ABI, capture-hook or client asset changes. Existing minimal Relay unit fixture needed its newdefaultfalsefield initialized; initial fullsuite failure was missing test stub state, fixed without weakening production code.

## Decision and next exact action

Rendering-core warm-up works technically, but does NOT remove the material-path delay and increases menu-time memory. Keep both warm modes and material withholding experimental/off; no normal appearance change, speed fix, sub2s or milestone claim. Next engineering action: inspect/qualify a supported way to preload/cache the generated material resources concurrently with preparation (or avoid repeated material-stage ingestion) while retaining the exact accepted material policy. First isolate which material-loading substage costs the time; do not remove glow/roughness, disable preloading blindly, return unqualified pixels or redesign the semantic/D3D9 interface. Earlier game-asset discovery remains deferred.

Final-source verification and repository state are recorded in the newest handoff/curated evidence. No SFC gameplay was needed; no sponsor action requested to reproduce the offline finding. Source/evidence remain unstaged/uncommitted,HEADunchanged,indexempty,no push. Generated local qualification receipts must be refreshed after source changes. No active owned job should survive completion.

## Final verification

-475Python tests PASS, including optional warm interval, first-complete-cohort timing, isolation-before-receiver and refusal to qualify either diagnostic. Loadedlight11/deferred/WorkerPoll/combinedGPU65 checks PASS on rebuiltx64host. One existing Relay unit stub initially lacked newdefaultfalseattribute; updated stub,fullsuitePASS. No production safeguard weakened.
- Final-sourceNORMALTest050416-088363(noexperimentalwarm/noisolation):4owners/3contents,788drawseach,596/600steady,598paired,0invalid/rejected/partial;normalnativejobexit0/remainingowned0,HUD/border/resize/recreationPASS. Changedpixelcount31314(thissample) vs31315earlier,notpixel-perfectbeautyclaim. FirstcompletecohortDraw+Present2.9616ms/copy10.8533ms/ACK1.7043ms;activation->matchingoutput0.9559149s,end-to-end3.3919779s. Fastcaseconfirmsvariability,NOTspeedfixfromexperimentalwarm-up(allOFF).
- Exact-source qualification uses050416fixture; native persistent/light checks and both Performance/Test read-onlypreflights PASS. Existingordinarylauncherremainsready;noexperimentalflagpromoted.
- Accepted/copyclientSHA `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`,copiedproxy `E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7`,unchanged. JSON/result-hash/path/numericchecks,gitdiffcheck/indexemptyPASS. HEADunchanged,no commit/push. No activeownedgame/test/renderer.
- Artifactinventory18,959,296,830bytes<20,000,000,000. Rawcaptures/generatedexperimentsretainedignored,none deleted;~1.04GBremaining. Archiveconsumedgeneratedbulkwithverifiedprovenancebeforeadditionalbulkfixtures,doNOTtreatdiskallowanceasVRAMorraiseblindly.

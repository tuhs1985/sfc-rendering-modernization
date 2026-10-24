# Run117 — multi-ship delivery repair

2026-10-22 America/New_York. Sponsor authorizes Run116 repair plan:publish complete
tracked-set before notification,admit against actual synchronized presentation,
separate late-asset preparation/measure stalls,offline validate before sponsor run.
HEADd40f8f230fc7504023e4a052c99a81b5a08ce6b4,all prior Run113–116 work already
unstaged/untracked,indexempty. FuelGuard trusted-hook attached;no helper/agent.
Reviewed HANDOFF,Run116,collector/source/cohort/host/admission/history/receiver,
wire/native tests,relay/material policy,qualification/build/fixture runners.

In progress;not a runtime success claim. No original suppression,appearance change,
camera rediscovery,new proxy/renderer architecture,staging,commit or push.

Selected implementation:

- Split selected-anchor preparation/commit. Collector stamps all current rows,
  publishes the complete checked cohort,then exposes the prepared anchor input.
  Existing single-owner offer remains prepare+commit. Standalone producer follows
  the same ordering. Callback uses fixed stack storage,never waits/allocates.
- Reuse cohort header's formerly reserved DWORD as actual compositor closed-frame
  watermark. No mapping enlargement/extra output surface. Multi-ship admission
  accepts current/adjacent source frames only while the compositor has not consumed
  that saved scene;existing50ms history wall-age guard remains. Legacy2ms policy
  unchanged. Exact full-cohort/camera/hash matching at composition unchanged.
- One bounded background CPU asset preparation:read/validate geometry/images
  before renderer-side admission. Prepared texture bytes feed the existing
  renderer without another disk/hash pass. D3D9 calls remain on its owning thread.
  Pending+resident conservative backing must fit256MiB. Future drained on shutdown.
- Add aggregate lookup/decode/projection and two-stage admission reason counters;
  per-asset CPU/GPU admission timings. Runtime GPU warmup is not claimed fixed by
  moving CPU preparation. Keep material-layer policy unchanged pending evidence.

Validation pending strict builds/native publication/deadline tests,full Python,
actual early/late two-model D3D9/Remix return fixtures,hashes/source-lock refresh,
read-only preflight and documentation/handoff. No game launched by Codex.

Exact next action:build/test repaired publication/admission and exercise actual
late asset delivery;measure against Run116 before returning sponsor launcher.

## Final checkpoint — repair prepared, late-material stall remains

CONFIRMED offline:434Python tests PASS. Multi-scene native45checks per32/64-bit
architecture,including a forced pause between preparation/cohort commit/input
notification and actual-watermark/age/old-frame rejection cases. Legacy live-owner
51checks×2,ingress142×2,sharedlights9×2,persistent18×2,GPU history33×2,slot649,
combined post65,loaded lights11,source18,return37,search13,broad14,calibration22,
normal M1 collector/mesh/stop/forwarding tests PASS. Strict host/receiver/addon/
component and dedicated light-observer builds PASS. Actual synthetic native
collector:120changing updates,one capture,retirement/stop/checksum PASS.

Final frozen-build normal-material actual D3D9/Remix/D3D11 fixtures:

- `20261023-033707-223604-return-fixture`:595/600 steady window;749total paired,
  FCA/RCA owner draws825/939,zero cohort lookup/decode/projection rejections,
  zero input admission rejections. Late asset CPU1.912ms,GPU creation0.578ms.
- `20261023-033751-568413-return-fixture`:600/600 steady;722total paired,
  owner draws804/906,same zero-stage failures. Late CPU2.234ms,GPU0.330ms.

Both use synthetic poses and two genuinely different historical capture packets,
two asset ACKs,91,506,338imagebytes,configured previousleftoffset,normal images/
material/light policy. Exact native HUD/scene pixels,border,state/resize/recreation,
owned process exit and bounded raw evidence PASS. Deliberate disable/re-enable and
pre-steady startup/late-load observations remain in logs;the600-frame steady
window is NOT the entire run. Actual SFC flicker improvement is **not yet tested**.
The old>=90%gate was not lowered;updated gate additionally requires zero incomplete
cohort lookups and presence of actual buffered admission counters. Native-light
receipt refreshed by real tests;normal fixture source/binary/config locks verified.

### Isolated remaining blocker

Normal material-list rewrites reproducibly cause a separate output-query stall:
final fixtures1113.801/1123.745ms. Earlier repaired normal runs032929/033021
show1129.679/1104.242ms. CPU file preparation and GPU resource creation are far
smaller. Offline negative A/B `033158-986947` delivered the same late geometry/
ordinary image data but skipped ONLY late material-list publication:maximum output
GPU stage20.296ms,no>50ms waits. Its material appearance is deliberately unqualified;
the result is prominently marked and `qualify_multiship.inspect` rejects it.
This exception is NOT available in the game launcher and is not the repair.

CONFIRMED experimental attribution:the current material hot-reload path triggers
the second-long interruption in these fixtures. STRONG HYPOTHESIS for precise
vendor internals,corroborated by official release-tagged source:USD reload stops
a watchdog before unloading/reloading;the watchdog sleeps1000ms and stop joins it.
No profiler stack directly identified that join in the shipped binary.

Narrow official-source review only;no vendor files changed:

- [Remix1.5.2 USD reload](https://raw.githubusercontent.com/NVIDIAGameWorks/dxvk-remix/remix-1.5.2/src/dxvk/rtx_render/rtx_mod_usd.cpp),
  `Impl::checkForChanges`996–1003,`unload`967–974,watchdog127.
- [Remix1.5.2 watchdog](https://raw.githubusercontent.com/NVIDIAGameWorks/dxvk-remix/remix-1.5.2/src/util/util_watchdog.h),
  sleep50–59 and stop82–89.
- [Material lookup/change processing](https://raw.githubusercontent.com/NVIDIAGameWorks/dxvk-remix/remix-1.5.2/src/dxvk/rtx_render/rtx_asset_replacer.cpp),
  `getReplacementMaterial`61–73,`checkForChanges`81–92. New mod-directory discovery
  is not assumed to provide automatic live addition;manager refresh is distinct.

Thus **seamless admission of previously unseen material bindings remains blocked
on a nonblocking material publication path**. Do not patch Remix,disable normal
materials,scan/convert the entire installation,return to SDK mesh submission or
hide the pause with old pixels without separately adjudicating the approach.
The frequent-update repair is useful independently;do not call all flicker fixed.

### Reproduction and exact changed files

Bundled modern pwsh and Python paths unchanged (see repository launcher). Builds:
`tools/d3d9_proof/build_multiship.ps1`,`build_direct64.ps1`,`build_receiver.ps1`,
`build_persistent_scene.ps1`,`build_frame_ingress.ps1`,`build_synchronized_buffer.ps1`;
`tools/m1_component/build_m1_component.ps1`,`build_light_discovery.ps1`;
`tools/remix_runtime/build_return_probe.ps1`. All existing strict compiler options
retained. Python commands from repository root:

```text
python -m unittest discover -s tests -p test_*.py
python tools/remix_runtime/light_discovery.py
python tools/remix_runtime/run_return_fixture.py --multi-ship
python tools/remix_runtime/run_return_fixture.py --multi-ship --buffer-early-ready
python tools/remix_runtime/run_return_fixture.py --multi-ship --isolate-late-material-reload
python tools/remix_runtime/qualify_multiship.py --fixture artifacts/remix-runtime/runs/20261023-033707-223604-return-fixture
python tools/remix_runtime/run_return_game.py --multi-ship
```

Last command is read-only preflight PASS,NOT `--execute`;no game launched by Codex.
Use actual bundled Python,not an assumed system interpreter. Normal scope retains
90-second tactical return,existing enclosing workflow/resource/log caps,diagnostic
geometry hookOFF,no new surfaces or stale hold. Source/copy client SHA256 both
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`;
copied baseline proxy restored `E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7`.

Source files modified this run(relative to already dirty Run116 starting state):

- `tools/d3d9_proof/live_owner_wire.h`,`multi_scene_wire.h`,`input_admission.h`,
  `live_owner_input.h`,`multi_scene_runtime.h`,`d3d9_direct_host.cpp`,
  `d3d9_replay.cpp`,`multi_scene.py`.
- `tools/m1_component/m1_live_scene.h`.
- `tools/remix_runtime/d3d9_game_receiver.h`,`source_timing_fixture.h`,
  `live_owner_timing.py`,`multi_scene_relay.py`,`run_return_fixture.py`,
  `qualify_multiship.py`.
- `tests/d3d9_multi_scene_tests.cpp`,`tests/test_d3d9_multi_scene.py`.
- This run record,new curated repair evidence,retained-multiship contract,HANDOFF.

No TOML baseline changed. No on-disk game binary changed. All prior work preserved.
No staging/commit/push;HEAD unchanged,indexempty. No active fixture/game process,
mapping or worker required to resume. Pinned runtime shutdown diagnostic about
40common objects persists;not silently claimed fixed.

### Recoverable evidence compaction

Six completed Run117 standalone fixtures032929,033021,033158,033513,033707,033751
compacted with existing `archive_fixture_binaries.ps1 -PartialGeneratedInputs`.
Exact dated directories validated;each ZIP entry decompressed and hash-verified
before removal of its duplicate generated input.493,254,096bytes of loose copies
became41,231,508bytes of recoverable ZIPs under`artifacts/remix-runtime/archives/`.
Original capture packets,logs,manifests,raw observations and nested late assets
retained. Final fixtures still qualify after compaction. Inventory16,214,551,555
bytes of20,000,000,000cap. No actual-game capture or original game files removed.

Exact next action:if sponsor wants to assess the frequent-flicker repair now,
use unchanged`tools/d3d9_proof/start_d3d9_multiship_session.ps1`;expect original
ships plus left copies,existing appearance,no replacement. New material arrival
may still cause one long pause. Otherwise adjudicate a supported nonblocking
material-binding strategy before claiming seamless new-object delivery.

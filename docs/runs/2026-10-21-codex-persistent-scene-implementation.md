# Run103 — persistent simulation scene implementation

2026-10-21 America/New_York. Starting clean HEAD `0fc1300`, branch
`codex/github-sanitized`, index empty. Sponsor authorizes implementation from
the verified Run101 offscreen findings. No new discovery gameplay, requirements
change, helper, agents, staging, commit or push. Fuel Guard recent trusted-hook
attachment confirmed; no task daemon spawned.

## Reviewed authority and evidence

Read HANDOFF, approved amended M1 plan, Run101/102, offscreen-position probe,
owner-rebind/additive execution contracts, live bridge/camera map, existing
native semantic/live-scene/source/receiver/light code and prior run
`artifacts/remix-runtime/runs/20261022-001430-318823-in-game`. Narrow static
review used existing exact client dump only: getter/base-getter/trig/matrix
arithmetic and ship deleting-wrapper/destructor path. No broad engine survey.
Run101 position updates (24/28/94) are accepted; raw historical automated
PARTIAL remains unchanged. Future analyzer now uses moving base translation,
not the additional E6 term alone.

## Implementation decisions

See [contract](../reconnaissance/persistent-scene-contract.md) and
[probe](../reconnaissance/probes/PERSISTENT-SCENE-001.md).
Fixed registry32, simulation arithmetic rather than render-cache polling,
actual supplied-matrix admission oracle, retained geometry/revision/lifetime,
default-off destructor notification, source protocol2, once-per-qualified-scene-
frame pose publication and existing D3D9/Remix return path. This is not a30Hz
pose path. Diagnostic logs retain their sampling cap. Current camera comes
from the qualified active wrapper, not a guessed independent camera pointer.
Native light bank raw provenance stays separate from derived world-directional
target context. No appearance/configuration or original-drawing change.

No callback allocation/disk/conversion/renderer wait; no remote getter calls,
object writes or game refcount changes. Destruction-hook ABI remains Codex's
engineering judgment supported by exact static bytes and existing state-save
machinery; actual game destruction invocation still needs corroboration.
Backend display remains one selected FCA asset; registry architecture covers
other qualified ships but all-object rendering is NOT claimed.

## Exact files created

- `tools/scene_bridge/persistent_scene.h`
- `tools/scene_bridge/simulation_pose.py`
- `tools/d3d9_proof/build_persistent_scene.ps1`
- `tools/d3d9_proof/start_d3d9_persistent_scene_session.ps1`
- `tools/remix_runtime/qualify_persistent_scene.py`
- `tests/persistent_scene_tests.cpp`
- `tests/m1_persistent_scene_tests.cpp`
- `tests/test_simulation_pose.py`
- `docs/reconnaissance/persistent-scene-contract.md`
- `docs/reconnaissance/probes/PERSISTENT-SCENE-001.md`
- `docs/reconnaissance/evidence/20261021-persistent-scene-prepared.json`
- This run record.

## Exact existing files modified

- `tools/m1_component/m1_component.cpp`:opt-in destruction hook, registry update
  at current semantic wrapper, visibility-independent lifetime retention.
- `tools/m1_component/m1_contract.h`:retain living simulation identity/removal.
- `tools/m1_component/m1_live_scene.h`:registry admission/full-rate publication,
  stop/join summary, version2 channel enforcement.
- `tools/d3d9_proof/live_owner_wire.h`:explicit version2 source acceptance.
- `tools/d3d9_proof/live_light_binding.py`:qualified world-bank association and
  unchanged-publication cache;raw evidence not rewritten.
- `tools/remix_runtime/d3d9_game_receiver.h`:same-frame invalidation check.
- `tools/remix_runtime/live_owner_timing.py`:persistent source initialization.
- `tools/remix_runtime/run_return_game.py`:qualification, child-only flag,
  moving camera-switch cues, native result collection.
- `tools/remix_runtime/start_return_image_session.ps1`:PS5/modern forwarding.
- `tools/remix_runtime/run_return_fixture.py`:actual version2 synthetic fixture.
- `tools/remix_runtime/offscreen_position.py`:future base-position criterion.
- `tests/test_offscreen_position.py`:zero-additional/moving-base regression.
- `docs/HANDOFF.md`:new authoritative checkpoint;older evidence preserved.
- `docs/reconnaissance/probes/OFFSCREEN-POSITION-001.md`:historical criterion
  correction and link to the new persistent probe;raw run evidence unchanged.

## Validation and reproducibility

Python is the established bundled Python at
`C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`.
Builds use VS18 Community x86/x64 C++17 `/W4 /WX`, established deterministic
build flags and project dependency pinning; no runtime/library version change.

```powershell
python -m unittest discover -s tests -p 'test_*.py'
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/d3d9_proof/build_persistent_scene.ps1
python tools/remix_runtime/qualify_persistent_scene.py --fixture artifacts/remix-runtime/runs/20261022-010604-302271-return-fixture
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/d3d9_proof/start_d3d9_persistent_scene_session.ps1 -CheckOnly
git diff --check
```

Run existing native-light/core/component, direct64, return addon/fixture and
output-receiver builds before the qualifier after source changes. Requalify
native light/lifecycle workers with current binaries. Exact source/binary locks
and PE8 anchors: `artifacts/d3d9-proof/persistent-tests/qualification.json`.
Standalone GPU fixture uses existing additive live-owner mode plus
`--persistent-scene --rebind-owner`; no actual SFC gameplay started.

Results: 415 Python tests PASS; registry18 checks each x86/x64 PASS; actual native
worker120 consecutive synthetic offscreen frames, one capture/generation,
120 publications, explicit removal/no stale publication, stop/join PASS.
Native-light core9/observer17 each architecture, component workers/lifecycle
qualifications PASS; direct64 light11, return37/depth13/broad14/calibration22,
receiver output29/source18/game44 and associated builds PASS. PS5 parsers,
launcher CheckOnly and diff checks PASS. No ignored test result is a gameplay
or formal gate claim.

Actual new GPU fixture:
`artifacts/remix-runtime/runs/20261022-010604-302271-return-fixture`.
595/600 fixed-window delivery, 1896 source rows/948 exact pairs, no source
anomaly counters, state/resize/recreation and normal owned exit PASS; ACK3,
reject0. Prior fixture010339 failed because output_receiver.exe still accepted
only v1. Rebuilding that receiver against current header fixed the actual
repeat. The failed fixture remains partial evidence, never promoted.
Other mechanical build issues (DWORD/uint32 array conversion and /WX local
shadowing) were corrected before PASS. Sandbox import-library/map ACL errors
were resolved through normal approved host execution, not weaker security.
Final sandboxed Python rerun also hit temporary-directory PermissionError
(195 errors); the identical suite rerun with normal approved host permissions
passed all415 tests in5.358s. This is an environment failure, not hidden test
success. No project security setting was altered. Final CheckOnly again PASS.

## Performance and limitations

Actual timed native update loop: 2757 ticks/121 invocations, frequency10MHz,
mean2.2785 microseconds, max6.6 microseconds for ONE synthetic owner. No32-owner
performance claim. Whole test loop including checks is about5 microseconds.

Uncontrolled GPU-fixture comparison, excluding first10 timing rows:
baseline112631 draw/present p50/p95321/501us, ready-wait6855.5/7930us;
new010604 draw/present335.5/521us, ready-wait7358/8936us. Delivery594/600 vs595/600.
These runs do not establish a speed improvement or causal GPU regression.
Live-game overhead and remaining blip frequency require the prepared run.

Static/full-pose arithmetic plus synthetic transport are CONFIRMED at their
respective evidence levels; seamless SFC camera transition, actual destructor
notification, gameplay death paths, multiple displayed instances and all-object
coverage remain unconfirmed. No current camera publication when there is no
qualified semantic wrapper; no stale-camera replay. Vendor shutdown warning40
remains. Same-format in-place mesh changes remain outside qualification.

## Evidence retention and final state

Fixture-generated inputs, not source/raw evidence, were ZIP archived with
decompression/hash verification:

- Failed010339:`artifacts/remix-runtime/archives/20261022-010339-773260-return-fixture-binaries.zip`,
  6,861,838 bytes,SHA256905716ABC82FC6743D861D823D94DA37BE1D1734803625D0631ACE1D73472C31.
- Passing010604:`artifacts/remix-runtime/archives/20261022-010604-302271-return-fixture-binaries.zip`,
  6,861,857 bytes,SHA2563CBB0B521725281331F659FBB099E1754A648DA3FE56E459D5B56D7078F05367.

Original and copied executable hashes remain
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
No game was launched or game files/proxies installed by this implementation run.
Final implementation/docs are unstaged/uncommitted on0fc1300;index empty,no push.
Generated outputs remain ignored. No owned game/renderer/worker left running.
Final artifact inventory12,065,695,473bytes,below20,000,000,000byte authorization.

Next exact action:sponsor executes the new persistent-scene launcher, follows
its moving own/enemy-camera cues, exits at twoLOW beeps; review native summary,
identity/asset continuity, exact-frame timing, observed blips and cleanup before
extending the resident backend to multiple displayed objects.

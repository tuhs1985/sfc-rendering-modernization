# Run164 — isolated direct Remix API scene/material submission

## Authority and disposition

Sponsor chose **Api path** after Run163's documented dynamic-USD readiness
boundary. Began from fd79ce5 plus the unstaged Run163 documentation. Read the
handoff, approved project context and readiness evidence; Fuel Guard attached
to the existing hook. No helper, subagent, SFC, Toolkit, driver/runtime upgrade,
public message, stage, commit or push.

**ISOLATED API SCENE DELIVERY DEMONSTRATED; STARTUP/PARITY PARTIAL.** The real
pinned runtime rendered captured ships through explicit SDK materials/meshes,
with emission response in the first returned image, shared geometry, late asset
admission and clean owned-process exits. This is NOT ordinary-D3D9 draw
qualification, sub2s readiness, gameplay migration or milestone PASS.

## What changed

- `tools/remix_api_proof/api_host.cpp`: isolated host snapshot using existing
  parser, retained owner registry, raw camera/state, light/image/quality adapters,
  SDK output copy, fences, receiver and whole-frame compositor. No normal launcher
  selects it. Ordinary D3D9 geometry draws are replaced ONLY in this experiment
  by SDK CreateMaterial/CreateMesh/SetupCamera/DrawInstance. Registered Device9Ex
  still provides presentation/output plumbing.
- `api_renderer.h`: exact corner position/normal/UV submission, group-local
  index rebasing, one material per group and one reusable mesh per unique asset.
  Native model3x4 retained; transpose SDK camera arrays and fold source viewport
  into full-target projection. Finite/count/checksum/group/path checks and
  mesh-before-material retirement. No extra UV flip, native-pointer identity,
  guessed model, altered DDS or GPU-ready claim from handles.
- `material_packet.py`: bounded version1 API association sidecar, derived from
  accepted generated manifest; original geometry/images/settings unchanged.
- `run_fixture.py`: explicitly offline-only fixture wrapper with independent
  build provenance, replacement lookup disabled and NO dynamic USD root
  publication. Optional emission-off and withheld-third-asset controls. Existing
  asset-local USD generation is preserved for image equality, but unused here.
- `build.ps1`, `build_record.py`, `tests/api_renderer_tests.cpp`,
  `tests/test_material_packet.py`, `README.md`: isolated strict native build,
  independent locks, tests and operating/rollback instructions.
- Probe `docs/reconnaissance/probes/REMIX-API-SCENE-001.md`, curated evidence
  `docs/reconnaissance/evidence/20261024-api-scene-proof.json`, this run, HANDOFF.

Normal `tools/d3d9_proof`/capture/return implementation, source assets, settings,
runtime pins and normal qualification receipt were NOT edited. Experimental host
SHA256 BF8E0118D50DFCA948739C181485E8680C836E933E855CFADE5B0C63CFC52A82.
Normal host remains5e59d67ece5c34101c98c7326062c6099dfb4bbe32f6877647347b10ef2b1314.
Host snapshot duplication is intentional isolation, not a new portable interface
or permanent final architecture. Do not migrate/factor normal code prematurely.

## Documentation and lifecycle decisions

Pinned NVIDIA [SDK instructions](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/documentation/RemixSDK.md)
support SDK submission alongside an existing registered D3D9 device. Exact
[API implementation](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_remix_api.cpp)
defines queued material/mesh/camera/instance behavior and matrix storage. Use
existing Remix1.5.2/API0.6.4, not current upstream headers or isolated1.6.1.

Two initial real-GPU experiments rendered correctly but failed retirement:
000946-406742 exceeded normal retirement wait; 001325-195259 reached SDK Shutdown
but bounded child exited0xC000041D. Supervisor fixture `host_exit=0` refers to its
outer host, NOT successful renderer exit; its error/job result remain decisive.
Both are preserved as PARTIAL, not silently counted as clean passes.

The pinned SDK Present wrapper gets a swapchain while providing resize handling;
the reviewed path lacks a corresponding Release. This source finding is NOT
proof that the packaged DLL caused either observed failure. No runtime patch,
manual reference-count repair or longer shutdown allowance was introduced.
Use the accepted registered-device PresentEx instead, retaining SDK scene calls,
then one unpublished retirement frame and GPU drain after mesh/material teardown.
Four subsequent actual GPU runs exited0, owned children0, retirement failures0.
The vendor's `common device objects were not disposed of` warning remains; it
also exists in Run163's ordinary-route reference. Do not claim leak-free vendor
internals from clean process exit.

## Real GPU controls

Evidence directories under `artifacts/remix-runtime/runs/`, date20261025UTC
(still20261024local). FIRST matching frame and600frames-later BMPs retained.

| Suffix | Control | Discovery to initial cohort GPU | Delivery in first600 | Cleanup |
| --- | --- | ---: | ---: | --- |
| 001516-802029 | SDK scene + Device PresentEx | 4.217s | 594/600 | exit0/owned0 |
| 001836-570929 | Same, API emission scalar0 | 4.228s | 594/600 | exit0/owned0 |
| 002105-217957 | Repeat normal API materials | 4.244s | 592/600 | exit0/owned0 |
| 002148-667336 | Third content withheld until existing120draw trigger | 3.227s initial subset | 564/600 | exit0/owned0 |

Late-case time covers initial subset, NOT all-three-content completion; do not
compare it as faster full-cohort startup. Initial full cases native device init
2.318/2.375/2.329s; activation-to-cohort1.844/1.761/1.791s. Device/CPU preparation
overlap, so these spans must not be blindly summed. No physical-display latency
or sub2s claim. Run163 accepted24reference5.170s, but rendering projection differs
between routes, so this is a measured experimental timing change, not exact
quality-equivalent performance acceptance.

All four current-route controls: four owners/four ACKs, three unique contents,
no asset partials, same432source/generated image SHA multiset as Run163, identical
user-setting hashes. Only negative control's API emission scalar changed5to0.
Three meshes/110group-material registrations; instance calls3133/3141/3137/2788;
ordinary geometry draws0. Shared FCA owners independently submitted783/785/784
times in full cases; late case owner draws753/528/753/753, including delayed FDD.
These are submission counts, not independent per-owner picking/occlusion proof.

HUD/native scene/border preservation, state restoration, resize/recreation and
normal bounded cleanup passed. Late introduction still incurs omissions; no
seamless late-admission claim. Existing asynchronous30Hz limits are not added by
this backend, and the retained source timing/return behavior is not redesigned.

## First-image material evidence and limits

Within-API full ship-region mean difference: normal vs emission-off7.824RGB/255
first,4.568settled; repeat vs off4.177first,4.505settled. Normal-repeat variation
4.305first,0.754settled demonstrates substantial first-image convergence noise;
the broad scalar difference alone is NOT exact material parity proof.

Posthoc fixed FCA nacelle region x405:610/y780:855 isolates recognizable blue
illumination. Predicate B>R+35, B>G+20, B>80 yields normal422/429blue pixels FIRST,
negative234; settled441/440, negative322. The first normal images visibly have
blue nacelle illumination absent/dimmer in the negative control. This supports
first-output emission response beyond7pixel normal-repeat variation; it does
not establish every scalar/map is fully settled or match ordinary-route pixels.
Original image hashes and unchanged UV arguments exclude substituted textures.

**Open camera discrepancy:** current API output positions/scales ships differently
from ordinary interception (e.g. FCA x~410–666 vs~233–521). The source viewport
fold is algebraically verified, but SDK versus intercepted camera interpretation
has not been matched with the projection oracle. Do not silently delete the fold,
rescale ships or claim pixel-identical comparison across these routes. First and
settled controls above use the SAME API conversion and region.

## Validation, evidence and repository state

- Strict x64 native host/mock build `/W4 /WX /O2 /fp:precise /Brepro` PASS.
- Actual accepted-input mock354747checks PASS: vertex/index/normal/UV/group and
  material arguments, independent transforms/inactive instances, camera matrix
  transpose/viewport equivalence, failed registration cleanup, mismatch rejection
  and original scene preservation. Mock explicitly makes no GPU claim.
- Five new Python association tests PASS0.018s; existing504tests PASS8.040s.
  Initial sandbox-temp invocation failed permissions; rerun with process-local
  TEMP/TMP pointing inside project artifacts passed. No policy/security change.
- Normal Performance read-only preflight PASS; no SFC/renderer launched by it.
  No normal qualification rewritten. Final build-lock and whitespace/path checks
  PASS at closeout (UTF-8 document inspection); no staged changes. No owned API
  host/receiver/fixture/job remains.
- Full analysis and reproducible fixed-run analyzer retained ignored under
  `artifacts/remix-api-proof/`; raw six runs, packets, logs and comparison BMPs
  retained. Existing20GB governed cap/32MiB supervisor envelopes unchanged.
  Governed output plus isolated API build/reports18,305,414,545bytes; whole
  artifacts folder22.301GB also includes excluded dependency/install content.
  Do not confuse the established output cap with dependency storage. No deletion.
- Prior Run163 work preserved; all Run164 implementation/evidence/docs unstaged
  and uncommitted; index empty, HEADfd79ce5, no push. No active tool session or
  mapping needs survival across restart. Rebuild independent lock after code or
  setting changes; API files cannot certify normal D3D9 gameplay receipts.

**Exact next action:** qualify the API camera/viewport placement against the
existing captured projection oracle using this same offline fixture, then decide
whether to prepare an explicit opt-in gameplay backend. No sponsor run is ready
or required yet; no full API path, seamless replacement or readiness-resolution
claim. Do not repeat semantic discovery or change the accepted normal path.

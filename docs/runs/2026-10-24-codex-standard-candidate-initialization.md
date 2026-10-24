# Run151 — candidate initializer control in the standard offline harness

## Outcome

**Run150's material workaround survives the unmodified standard initial and
late-arrival native fixtures.** It is now an explicit offline candidate option,
not a supervisor monkeypatch. Normal gameplay remains pinned to1.5.2; no SFC or
Toolkit GUI launched, no runtime promotion, appearance tuning or milestone claim.
The two-second loading target is still unmet.

Read newest HANDOFF/Run150 and approved amended M1 plan before implementation.
Fuel Guard attached via existing trusted hook; no daemon/helper/agent. Existing
dirty work preserved, no staging/commit/push. User authorized implementing the
candidate-only setting and standard qualification, not changing normal gameplay.

## Implementation

- `tools/remix_runtime/runtime_candidate.py`: `configure_initialization` accepts
  inherit/synchronous, rejects unknown policy or synchronous use outside offline
  candidate1.6.1. Mutates only the supplied child environment dictionary and
  returns one option plus an auditable receipt; never global environment.
- `tools/remix_runtime/run_return_fixture.py`: adds explicit
  `--candidate-asset-loading synchronous`; default inherit. Requires the existing
  `--runtime-candidate 1.6.1 --multi-ship --prewarm` gate; rejects combination
  with broader `--loading-policy` experiments. Records requested policy in
  result.runtime_candidate.asset_loading and configures the relay instance.
- `tools/remix_runtime/multi_scene_relay.py`: defaults unchanged; candidate-only
  relay policy appends `rtx.initializer.asyncAssetLoading = False` and matching
  child `DXVK_ASYNC_ASSET_LOADING=0` before native process creation. Receipt in
  gpu/loading-inputs.json has nested candidate_initialization override; outer
  loading-policy fields describe the preceding generic inherit inputs. Actual
  runtime log confirms False/0. Shader/texture controls and four preparation
  workers remain unchanged. No callback, mesh, texture or native code change.
- `tests/test_runtime_candidate.py`: four new tests cover unchanged defaults,
  exact one-option mutation, production/unknown-policy rejection without side
  effects, and invalid CLI combinations refusing before launch.
- `tools/d3d9_proof/README.md`: documented isolated option, commands, receipts,
  limits and no-production-promotion rule.

Also added this run record, curated evidence and newest HANDOFF checkpoint.
All modifications remain unstaged. Earlier uncommitted candidate implementation
and cleanup documentation retained; do not attribute their entire diff to Run151.

## NVIDIA basis and scope

Rechecked release-linked NVIDIA [initializer source](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_initializer.cpp).
This selects the initial asset-loader thread behavior independently of shader
prewarming. It is not a GPU-residency barrier, a new loader, or disabling all
asynchronous work. Run150's STRONG HYPOTHESIS of initializer/publication ordering
persists; exact vendor defect remains unproven. Packaged5a7eec84 versus public
source/header0a6cd5b/API0.6.5 discrepancy remains explicitly qualified.

## Standard fixture runs

All under `artifacts/remix-runtime/runs/20261024-<identifier>-return-fixture`.
Existing native fixture binary used unchanged; no pre-arrival diagnostic copy,
Python monkeypatch, generated scalar override, extra image or custom loader.

| Identifier | Runtime / loading | Fixture | Steady paired draws |
| --- | --- | --- | ---: |
| 192321-567045 | candidate1.6.1 / synchronous | initial three contents/four owners | 592/600 |
| 192359-283071 | candidate1.6.1 / synchronous | late FDD arrival | 594/600 |
| 192447-814961 | unchanged1.5.2 / inherit | initial three contents/four owners | 600/600 |
| 192531-008390 | unchanged1.5.2 / inherit | late FDD arrival | 594/600 |
| 192617-907043 | candidate1.6.1 / inherit | late FDD negative control | 593/600 |

Every case: four independently ACKed/drawn owners, FCA/RCA/FDD three distinct
contents, no asset partials, state_errors0, preserved HUD/border/source scene,
resize/device recreation pass, host/fixture/job exit0, job stop_reason0 and
remaining_owned_processes0. Separate final CIM check found no owned fixture,
renderer/receiver/job processes. Existing vendor common-object warnings remain;
do not infer leak-free vendor teardown.

Exact same432generated image/native files SHA multisets and six configuration
hashes across all five cases. Current standard snapshots occur after all assets
are ready: **do not call them pre-arrival evidence**. Run150 separately supplies
the true before-arrival/emission controls. Shared FCA instances can overlap in
the fixed diagnostic view; per-owner ACK/draw receipts establish four instances,
not a claim of four visually separated ship silhouettes.

[Curated pixel/identity/config/cleanup evidence](../reconnaissance/evidence/20261024-standard-candidate-initialization.json).
Finite ship ROI x150..1899/y700..999, actual-background union mask31,313pixels:

| Settled-image comparison | Mean absolute RGB difference /255 |
| --- | ---: |
| Candidate synchronous initial vs working initial | 2.386325 |
| Candidate synchronous late vs working late | 2.415504 |
| Candidate inherit vs candidate synchronous late | 22.509767 |
| Candidate inherit vs working late | 22.655244 |

Visual inspection of candidate settled image shows recognizable normally textured
FCA/RCA/FDD and luminous features. The workaround restores material response;
residual version/temporal differences are NOT exact parity, full roughness
qualification, universal model support or unchanged gameplay validation.

## Timing — not a sub-two-second result

Existing first-cohort-output QPC minus first preparation discovery, seconds:

| Case | Seconds |
| --- | ---: |
| Candidate synchronous initial | 4.434352 |
| Candidate synchronous late fixture's initial cohort | 3.539505 |
| Working1.5.2 initial | 5.676076 |
| Working1.5.2 late fixture's initial cohort | 4.720439 |
| Candidate inherit negative control | 2.899857 |

These are single runs with uncontrolled warm caches; initial batch sizes differ
between initial and late fixtures. They measure initial cohort GPU output, NOT
final-material readiness, physical display latency or late-asset latency. The
fast negative control has incorrect material application and cannot count as
an equivalent-appearance optimization. No performance victory/sub2s claim.

## Validation, bounds and cleanup

- Isolated candidate x64 host rebuilt with matching pinned header and existing
  `/O2 /fp:precise /W4 /WX /Brepro`; source/build receipt refreshed, normal native
  host/runtime untouched. Existing native return fixture/add-on unchanged.
- **499 Python tests PASS9.576s**, including11candidate tests.
- Normal late control192531 requalified current source, including native Test
  and Performance worker checks. Candidate remains rejected by production
  qualification; no bypass or source-lock weakening.
- Both Performance/Test **read-only launcher preflights PASS** after normal
  requalification; no game/renderer launched by preflights. Existing client/proxy
  integrity checks pass; no accepted/copy game file changes.
- Existing100s fixture/285s owned-job,32MiB supervisor and20GB aggregate limits
  unchanged. No continuous readbacks or additional image dumps.
- Three completed generated image sets (initial candidate, initial normal,
  negative candidate)432files/162,619,600bytes each archived to10,051,597bytes
  each, every decompressed entry SHA-verified before exact loose originals
  removed. Net457,704,009bytes saved before receipts. Recover via each
  generated-images-archive.json and artifacts/remix-runtime/archives. Both latest
  successful late candidate and late normal generated sets remain raw.
  All source captures, geometry, logs, receipts and comparison BMPs retained.
- Final governed evidence14,368,750,630bytes, below unchanged20GBcap;
  `git diff --check` passes and index remains empty.

Ignored analysis helper `artifacts/analyze_standard_candidate.py` writes the
curated JSON from explicit five run identifiers; native diagnostics unchanged.
No active session/channel or global setting is required after restart.
HEADfe2eaf7/indexempty/allunstaged/uncommitted/nopush.

## Exact next action

Use the now-correct candidate material path to split its remaining startup delay
into existing preparation/publication, native activation/first-use and returned
output boundaries on a matched initial fixture. Keep full materials and current
maps; retain normal1.5.2 pin. Do not promote the runtime or invent a loader based
on single timings. Sponsor gameplay is not needed for that bounded timing work.

# Run150 — isolated stock Remix 1.6.1 initial-loading workaround

## Outcome and scope

**A repeatable candidate-only workaround restores material response before and
after late ship arrival using NVIDIA's existing initializer option.** No new
loader, material flattening, asset conversion change or vendor patch was needed.
Normal game runtime remains pinned to 1.5.2. This is not runtime promotion,
roughness qualification, a sub-two-second result or a milestone completion.

Resumed Run149/148's exact next action after reading the handoff and run records.
Used the larger three-content/four-owner standalone fixture: FCA, RCA, shared
FCA owner31, then late FDD. No SFC or Toolkit GUI launched. Existing dirty work,
client/dependency files, normal native source/binaries and tuning preserved.
Fuel Guard attached to the existing trusted hook; no daemon/helper/agent used.

## Documentation and interpretation

NVIDIA's release-linked [initializer implementation](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_initializer.cpp)
separates shader preparation from `asyncAssetLoading`: this option chooses
whether initial asset loading runs on its own initializer thread. The
[USD mod loader](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_mod_usd.cpp)
also has worker/publication behavior. These sources support testing an ordering
control, not claiming a public GPU-texture-residency barrier.

The packaged candidate still reports `remix-main+5a7eec84`, whereas release-linked
public source/header is `0a6cd5b`/API0.6.5. The former commit was not available
through public lookup. Do not assert instruction-level packaged-source parity.

- **CONFIRMED:** setting `rtx.initializer.asyncAssetLoading = False` and its
  matching child-only `DXVK_ASYNC_ASSET_LOADING=0` input restores initial and
  subsequent material response in this fixture; runtime logs confirm False/0.
  These are two inputs for ONE option, not two independent interventions.
- **CONFIRMED:** emission-zero changes actual returned pixels before AND after
  late arrival with this option. Repeating the full-material test reproduces it.
- **STRONG HYPOTHESIS:** initial-library publication and asynchronous initializer
  ordering interact. Default loading logs first two search paths only with the
  later publication; disabled-async logs them before the initial snapshot.
- **UNPROVEN:** the exact missed watcher/cache/update or vendor defect. Do not
  blame late arrival alone: the failure already exists before it arrives.

All other shader, texture-upload and loading controls retain inherited values.
Project four-worker preparation remains enabled. This is not disabling all
threading or a recommendation to force texture-upload waits.

## Probe and matched evidence

[Probe definition](../reconnaissance/probes/REMIX-LATE-MATERIAL-001.md) and
[curated measurements](../reconnaissance/evidence/20261024-late-material-controls.json).
Existing native fixture's first saved image waited for all owners; therefore it
could not answer the pre-arrival question. An ignored diagnostic source/executable
copy adds exactly one pre-arrival readback. Production source/binaries untouched.

Run roots below are under `artifacts/remix-runtime/runs/`, dated20261024 and
suffixed `-return-fixture`:

| Time/identifier | Control | Result |
| --- | --- | --- |
| 182733-437991 | Initial extra-BMP attempt | PARTIAL: existing32MiB output cap; excluded from success comparisons |
| 182847-071751 | Candidate default | Clean completion; initial appearance essentially disabled |
| 182936-191641 | Candidate replacements explicitly disabled | Clean negative control |
| 183041-571859 | Candidate default, emission0 | Clean control; no restored initial material response |
| 183135-464895 | Working1.5.2 full library | Clean positive control |
| 183512-727036 | Candidate asyncAssetLoading=False | Clean; material response restored |
| 183616-964790 | Same, emission0 | Clean; response changes before/after arrival |
| 183700-832747 | Candidate async=False repeat | Clean; restored appearance reproduced |

All seven successful fixtures ACK four owners/three content assets, with zero
asset partials or state-restoration failures. Steady paired counts respectively
600,593,594,595,596,600,594 out of600. HUD/border, resize/device recreation,
normal exit, owned-job cleanup pass; independent final owned-process inventory
empty. Existing vendor common-device-object warnings persist (40 old/43 new);
do not claim leak-free vendor shutdown.

The true initial snapshot preceded late library publication by2.65–2.95seconds
in all controls, verified using the native QPC clock and supervisor publication
clock. This interval is NOT startup/render-ready time.

Mean absolute RGB difference on the union of ship pixels, channel range255:

| Comparison | Before arrival | Settled after arrival |
| --- | ---: | ---: |
| Default candidate vs explicitly disabled | 0.060758 | 1.106857 |
| Default candidate vs working1.5.2 | 25.008643 | 22.723374 |
| Candidate async=False vs disabled | 24.591362 | 22.517400 |
| Candidate async=False vs working1.5.2 | 2.376355 | 2.342669 |
| Candidate async=False vs same with emission0 | 4.541434 | 5.581494 |
| Candidate async=False vs repeat | 0.059652 | 0.894176 |

Fixed ship ROI excludes transient ReShade startup text and source markers.
Actual-background masks cover25,917initial and31,313post-arrival pixels.
Per-model emission response is recorded, including late FDD. All432generated
image/native files have identical SHA multisets across successful controls.
Residual temporal/version differences remain: close appearance is not exact
pixel parity or complete material/roughness correctness.

## Bounds, partial attempt and compaction

Existing100second native fixture/285second owned job,32MiB supervisor envelope,
20GB aggregate cap unchanged. First diagnostic attempt exceeded32MiB because
the added full-size BMP made three raw images. It stopped safely, preserving
partial evidence; host/fixture exit1 means NOT a clean fixture PASS, even though
owned-job cleanup reached zero processes.

Corrected only the supervisor diagnostic: after the completed one-shot BMP is
closed and renamed, losslessly encode PNG, verify decoded RGBA bytes exactly,
then remove that own BMP. No callback conversion or continuous readback.
Existing two post-arrival BMPs retained. Successful tests then fit existing caps.

Six completed generated image sets archived, each432files/162,619,600bytes to
10,051,597ZIP bytes; every entry decompressed and SHA-verified before loose
generated originals removed. Net915,408,018bytes saved before receipts.
Restore using each `generated-images-archive.json` and archive under
`artifacts/remix-runtime/archives`. Latest restored repeat remains raw; first
capped partial also retained. Captures, geometry, logs, config and all comparison
images preserved. No original assets or source evidence deleted.

## Validation and repository state

- Isolated x86 diagnostic fixture compiles `/W4 /WX`; seven native end-to-end
  fixtures and image/hash/sequence controls above completed.
- Full Python regression: **495 PASS,7.323s**.
- Performance and Test game-launcher **read-only preflights PASS**; no game or
  renderer started by those checks.
- Final governed evidence13,873,872,744bytes, below unchanged20GB cap;
  curated JSON and local document references valid; `git diff --check` passes.
- Candidate source/header/DLL/host pins unchanged. Normal fixture source
  SHA703B42ADB3D463AAB845D238DE04640C021D7F16B1B9C76A0545AF944B42031D.
- Current-run versionable changes: this record, probe, curated JSON, newest
  HANDOFF checkpoint only. Existing implementation/untracked work preserved.
  HEADfe2eaf7; index empty, changes unstaged/uncommitted, no push.
- No active test session, OS/global environment override or restart-sensitive
  channel remains. Isolated scripts/binaries are ignored artifacts, not required
  normal-launcher inputs.

## Exact next action

Expose this single initialization policy as an explicit candidate-only option in
the standalone qualification harness, then run its unmodified standard initial
and late-arrival fixtures against matched controls. Preserve normal1.5.2 and all
maps/settings; qualify final pixels before runtime promotion or gameplay.

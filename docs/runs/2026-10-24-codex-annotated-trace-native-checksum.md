# Run156 — annotated trace reviewed; bounded packet verification accelerated

## Outcome and authority

Reviewed Run155, the authoritative handoff, and sponsor's completed annotated
NVIDIA trace. No SFC launched in this run. Normal runtime remains pinned Remix
1.5.2; 1.6.1 remains an isolated candidate. No lighting/material/image retuning,
vendor changes, original-draw suppression, helper delegation or architecture pivot.
Fuel Guard attached the existing trusted hook; no sandbox daemon was started.

## Annotated trace: useful, but not the missing performance reproduction

Evidence: `artifacts/d3d9-proof/nsight-candidate-20261024-201958-4495912`,
fixture `artifacts/remix-runtime/runs/20261024-202001-789867-return-fixture`.
Exported read-only SQLite contains 365,086 events. Existing NVIDIA NVTX markers
now correlate host phases with the Vulkan trace:

- Host entry 0.129627s; device ready 3.741136s; activation 3.771778s.
- First bootstrap output complete 4.169153s; first cohort output 4.402268s.
- Slowest observed bootstrap Present boundary ~45.9ms, NOT the unprofiled
  ~1.2s first-use pause. Shader preparation happened before device readiness.
- Within that boundary, overlapping API thread time includes fence waits and
  allocations; these are not additive wall time. Do not sum overlapping calls
  or label shader compilation the proven cause of the unprofiled pause.

CONFIRMED: profiling changed the ordering and did not reproduce the target pause.
STRONG HYPOTHESIS: publication/initialization scheduling and contention matter.
Exact vendor-internal attribution remains unproven.

Profiler-only shutdown is still PARTIAL: even the diagnostic 60-second wait
expired; outer job exit 1, stop reason 0, remaining owned processes 0. Receiver
reported retirement, but inner native final audit is absent. Do not claim clean
native teardown or an exporter-only cause. Normal unprofiled controls exit cleanly.
Do not weaken normal cleanup or patch Remix based on this profiler-only failure.

Documentation basis remains the pinned NVIDIA initializer/options/texture-manager
and Nsight sources linked in [Run152](2026-10-24-codex-startup-boundary-investigation.md).
No new loader, texture-streaming policy, cache policy or warm-up system was built.

## Small implementation: same packet checksum without Python serialization

Read-only CPU profiling exposed an independent project-owned preparation cost:
the captured-packet FNV32 loop holds Python's interpreter lock for the entire
packet, despite four preparation workers. This is separate from the existing
native image identity hasher and NVIDIA material upload work.

The existing checksum is now calculated in a tiny native worker helper in
Performance mode. ctypes releases the interpreter lock during that calculation.
The same initial value, multiplier, byte order and zeroed checksum field are
retained. All count, finite-value, index, association, identity and content checks
remain. Test mode retains the Python reference. No SFC callback changes.

Exact implementation files added/changed in this increment:

- `tools/d3d9_proof/mesh_checksum.cpp`, `mesh_checksum.py`,
  `build_mesh_checksum.ps1`: immutable bounded input, x64 source/DLL receipt,
  first-load verification and cached native function.
- `tools/d3d9_proof/build_multiship.ps1`: build the helper with normal prerequisites.
- `tools/remix_ingest/live_scene.py`: optional checksum backend; reference default.
- `tools/remix_runtime/multi_scene_relay.py`: Performance identification worker uses
  the helper, outside rendering callbacks.
- `tools/remix_runtime/qualify_multiship.py`: lock helper and build receipt.
- `tests/test_mesh_checksum.py`: five differential, malformed-input, build-lock,
  immutable-buffer and concurrent-call tests.
- This run record, curated control evidence and authoritative HANDOFF checkpoint.

## Validation and measurements

Native build `/O2 /W4 /WX /LD /Brepro` PASS. All five new native tests actually
ran (not skipped). Full 504 Python tests PASS, 6.835s. An initial invocation used
the sandbox-owned default temporary directory and failed with permission errors;
rerun with the established workspace temporary directory passed. This was an
environment failure, not hidden as a passing first attempt.

Actual captured packet full-decode medians, alternating three unprofiled calls:
63,780 bytes 7.74→2.46ms; 586,836 bytes 74.19→24.53ms;
808,892 bytes 102.47→32.61ms; alias 102.61→33.74ms. Decoded dictionaries
are exactly equal. Evidence `artifacts/native-mesh-checksum-benchmark.json`.
These numbers do NOT imply the entire startup is three times faster.

Full candidate fixtures, identical settings and all 432 generated image hashes:

| Worker checksum | Run suffix | Preparation | First cohort GPU output |
| --- | --- | ---: | ---: |
| Native | 203234-522301 | 2.2024s | 4.4350s |
| Python reference | 203329-011816 | 2.4865s | 4.6536s |
| Native repeat | 203446-179120 | 2.0194s | 4.0980s |

Each admits four owners/three contents, all acknowledgements/draws, no asset
partials, HUD/border/state preservation, resize/device recreation and normal
exit; owned jobs exit 0/remaining 0. Delivery 596/600,596/600,595/600 respectively.
Candidate native/reference settled mean pixel difference 0.8964 RGB/255;
native-repeat residual 0.0675. Exact pixel parity is NOT claimed. The identical
decoded geometry and image files rule out a changed checksum interpretation.
The ~1.24–1.37s bootstrap pause persists; two-second end-to-end target NOT met.

Normal 1.5.2 native fixture 203405-713587 also passes, 594/600. Preparation
2.0543s, first cohort output 5.3916s, including a separate ~2.107s first-cohort
copy/presentation boundary. This is not a candidate-to-production speed claim.
Do not attribute that whole boundary to texture copying without a matched trace.
Normal/candidate image differences are cross-version and not checksum evidence.

Same normal runtime Python-reference control 203536-044906 passes, 593/600;
preparation 2.3353s and first cohort 5.6569s. Relative to native this is 0.281s
more preparation and 0.265s later output, but one pair is not a statistical
guarantee. Its main pause occurs at bootstrap Present14 (~2.417s), unlike the
native case's first-cohort boundary. Image hashes/settings/decoded assets match;
normal-native/reference post residual 8.1899, settled 2.1412 RGB/255. This
nonzero appearance difference is unresolved, not silently accepted as exact
visual parity. Sponsor regression should check ship texture and lighting as
well as startup/stability. See `20261024-native-checksum-normal-controls.json`.

Curated control report:
`docs/reconnaissance/evidence/20261024-native-checksum-controls.json`.
Phase receipts `artifacts/native-checksum-startup-split.json`.
Normal source qualification refreshed from the normal fixture; both Performance
and Test read-only preflights PASS. No SFC or game files were changed by fixtures.

## Live check and next work

After closeout, a normal gameplay regression is appropriate: usual skirmish,
observe ships loading and camera changes, then exit normally at the runner cue.
Use the existing elevated-parent multiship launcher with `-StartupProfile`.
This checks appearance/stability and measures real startup; it does not qualify
1.6.1, ship replacement, sub-two-second loading or formal milestone completion.

Next engineering action: use matched normal-runtime startup boundaries and
the sponsor run to target the remaining first-use cost. Keep the NVIDIA path
and accepted material content intact; do not build a replacement loader or
promote the isolated four-Present experiment without output qualification.

All earlier dirty work preserved. HEAD fe2eaf7; index empty; all changes unstaged
and uncommitted; no push. No persistent session state is needed to resume.
Four completed generated image sets were recoverably compacted: each
162,619,600 original bytes to 10,051,597 ZIP bytes, every decompressed SHA
verified before removal; net 610,272,012 bytes saved before receipt overhead.
Per-run `generated-images-archive.json` identifies restoration. Qualified normal
fixture remains raw. All captures/geometry/logs/comparison BMPs and both trace
reports/SQLite retained. Independent owned renderer/game/profiler inventory empty.
Conservative inventory across M1/runtime/ingest/D3D9 artifact roots totals
19,135,024,841 bytes before final tiny documentation overhead, below 20GB.
The next live run's established 384MiB reservation still fits. Do not start
another 1GiB standalone resource fixture without checking/compacting first.

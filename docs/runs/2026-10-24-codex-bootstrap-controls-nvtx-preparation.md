# Run155 — bootstrap controls; exact native phase correlation still missing

## Outcome

Finished a narrower read-only analysis of the saved Run154 trace and tested one
specific project-owned startup cost. **No two-second fix demonstrated.** An
isolated four-Present bootstrap saves only0.19–0.36s in these single comparisons;
the main first-use stall persists and pixel parity is unqualified, so no change
is promoted. Prepared an isolated NVIDIA NVTX-marker host and smoke-tested it.
An annotated correlation trace, not another broad discovery run, is now needed.

Read current handoff/Run154; Fuel Guard attached existing trusted hook/no daemon.
No SFC/Toolkit launch, normal source/native/tuning/client/runtime modification,
helper/agent, staging/commit/push. Normal1.5.2 remains pinned. All experimental
source/binaries/scripts are ignored artifacts, not production inputs.

## What the existing trace can and cannot establish

[Curated analysis, controls and marker build provenance](../reconnaissance/evidence/20261024-bootstrap-controls.json).
Ignored artifacts/analyze_trace_first_use.py opens the existing SQLite read-only;
deduplicates identical GPU intervals rather than summing repeated batch rows.
Renderer readiness maps to3.6559315s, first Vulkan Present3.842733s. In the next
three seconds, recorded Vulkan API calls exceeding10ms top out at39.125ms
vkWaitForFences; none independently accounts for the unprofiled1.2s PresentEx
stall. Vulkan Present is downstream of D3D9 PresentEx, not the same boundary.

Much pipeline creation predates readiness. Renderer stderr shows initial asset
search paths and replacement-image handling before readiness too. Thus this
profiled run's ordering is not interchangeable with earlier unprofiled QPC
measurements. **Do not say shader compilation explains the full later pause,
or infer no CPU work simply because no long Vulkan API call appears.** Missing
application phase markers prevent responsible exact attribution; deferred stdout
was absent from this capture. No CPU scheduler/file-I/O trace collected.

NVIDIA's [profiling guide](https://docs.nvidia.com/nsight-systems/UserGuide/index.html)
recommends NVTX annotations to label application phases on its timeline. Use
that supported mechanism rather than a new tracing protocol/vendor patch.
Pinned [texture manager](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_texture_manager.cpp)
still distinguishes initial preload from subsequent streaming; no documented
public material-ready signal or reason to remove all warm-up frames established.
Packaged5a7eec84 vs public0a6cd5b caveat persists.

## Single-constant bootstrap experiment

An ignored copy artifacts/candidate-bootstrap4/d3d9_direct_host.cpp differs from
normal source ONLY at initial presents24→4. Every subsequent live frame remains
one Present; original24 startup includes10ms sleep per iteration. Full normal
maps/materials/camera/light/image/quality settings and initializer policy retained.
Built isolated x64 /O2 /fp:precise /W4 /WX /Brepro against the candidate header,
never overwriting normal or original candidate host. Supervisor verifies the
exact one-constant source delta before use and records actual host/source SHA.
Candidate results remain ineligible for production qualification.

All standard initial fixtures below use three distinct content assets and four
owners, original native return fixture/add-on and existing bounds:

| Run20261024 identifier | Bootstrap | Discovery→first cohort output | Steady draw pairs |
| --- | ---: | ---: | ---: |
| 200451-376554 | 4 | 4.077438s | 594/600 |
| 200537-305687 | unchanged24 control | 4.440216s | 595/600 |
| 200652-993498 | 4 repeat | 4.246091s | 595/600 |

All4owners ACKed/drawn, no asset partials, HUD/border/state/resize/recreation and
normal fixture/host/job exit0/owned0. First-use Present still~1.20–1.42s in the
four-Present cases. Same432generated image/native SHA multisets/configs. Settled
ship-region difference four vs24~1.995/2.027RGB/255, repeat four vsfour~0.997;
temporal/convergence variation remains, not exact appearance equivalence. This
small saving does not justify adopting another magic fixed frame count, changing
normal startup, or claiming shader/material readiness. No promotion.

## NVIDIA marker host prepared and smoke-tested

Already installed official headers at:
`C:\Program Files\NVIDIA Corporation\Nsight Systems 2026.5.1\target-windows-x64\nvtx\include\nvtx3`.
No new package, driver or vendor DLL installed. Header SHA inventory in evidence.

Ignored artifacts/candidate-nvtx/d3d9_direct_host.cpp is identical to original
main source, including24startup Presents. Its isolated startup_profile.h adds
official nvtxMarkA with label:index at each existing enabled startup mark,
bounded by existing128points. External host only; no SFC callback markers, scene
changes, new allocation/copy path or normal header edits. Native build /W4 /WX
passes. SDK markers are expected to be inactive without a profiler; smoke test
validates normal rendering/cleanup, NOT successful NVTX capture yet.

Smoke200847-167491: all4owners/3contents/noassetpartials/HUD+state+resize+recreation/
exit/jobowned0,594/600; initial4.302574s, not a speed claim. Same image/config
hashes. Control24 vs marker host first snapshot difference0.08777RGB/255 and
settled0.89514, temporal variation retained. Curated host/header/SDK source hashes
make diagnostic provenance explicit; no original candidate source receipt faked.

## Exact prepared sponsor action

Ignored artifacts/profile_candidate_nsight.py accepts annotated mode; validates
the normal candidate pin first, then selects explicitly isolated marker host.
Adds --trace=vulkan,nvtx. Existing correction --wait=primary/--show-output=true
and only profiled guard's10s→60s retirement wait retained; this profiled cleanup
correction remains unverified until actual annotated run. Normal relay10s
unchanged. Outer180s/1GiB/2MiB, inner100sfixture/32MiB and20GB aggregate remain.

Python/PowerShell parsers PASS. Existing launcher now accepts -Annotated.
Sponsor opens Administrator PowerShell and pastes:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\artifacts\start_candidate_nsight_trace.ps1" -Annotated
```

No game launch or gameplay. Same15s narrow renderer-only trace with NVTX,
CPU sampling/context switches off, no system-wide injection. Expect under two
minutes/hard stop three minutes. **Not executed elevated this run.** This repeat
is justified by a specific missing correlation, not missing proof tracing works.

## Validation, compaction and repository state

- Four full native standalone fixtures above pass; current11candidate Python
  tests PASS0.200s and normal Performance read-only preflightPASS. Full499passes
  remain historicalRun151. Independent owned GPU process check empty.
- Three completed bootstrap generated sets verified ZIPcompacted: each432files/
 162,619,600bytes→10,051,597ZIPbytes, all entries decompressedSHAverified before
  exact loose-file removal. Net457,704,009bytes saved before receipts. Restore
  via perrun generated-images-archive.json and artifacts/remix-runtime/archives.
  Latest NVTX smoke raw, all captures/geometry/logs/BMPs/trace/SQL preserved.
- Governed evidence15,300,441,053bytes before final small doc overhead, below20GB.
  Existing vendor43common-device-object warnings persist, no leak-free claim.
- Only versionable additions/edits this run: this record, curated JSON, HANDOFF.
  HEADfe2eaf7/indexempty/previous dirtyworkpreserved/allunstaged/uncommitted/nopush.
  Parser/reference/JSON/diff checks at closeout. No active trace/channel/runtime
  state is needed to resume; elevated annotated capture is the next exact action.

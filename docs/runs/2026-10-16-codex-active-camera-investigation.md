# Codex run — locate active camera data using existing evidence

Run/date:2026-10-16-active-camera-investigation /2026-10-16 EDT.
Question: locate renderer-facing active view/projection/viewport data without
reconstructing camera modes or requesting another gameplay capture.
Starting HEAD fee152f137a55a3efeb47a5c236ebf9e3e1951cb, inherited uncommitted
work/index empty (previous run188 plus its new runtime record; status191 after
initial analyzer/test additions). No commits/staging authorized.

Read newest HANDOFF, latest real live-bridge run/probe/contract, MATH-001,
corner-transform qualification, input-gap/export contracts, Pre-M0 map/targeted
disassembly, manager vtable/current installed exact PE and sfc.ini dimensions.
No broad function enumeration/renaming, new hooks, process/renderer launch,
helper/subagent or requirements/milestone change. Fuel Guard recent exact-thread
hook verified; direct sandbox daemon access denied/quota unknown, no daemon started.

## Findings and material decisions

Direct manager view+628, projection+55C, viewport origins+75C/+760,size+764/+768;
combined +5E4=S*P*V and already-streamed +6B0=S*P*V*M. Table/setter/getter and
homogeneous divide evidence in active-camera-state-map.md. Exact36 selected PE
anchors match including .5/1 constants, vtable targets, viewport-Y flip, effective
fourth-row metadata and divide. No assumed plain4x4 from17DWORD metadata payload.

Existing real1854-record native log suffices to recover B=C*inverse(M), no additional
capture. Recomposition residual2.3283064e-10; candidate pinhole factorization
residual3.0552926e-8; excluded0. Principal point approximately1060,540 and focal
1903.346pixels stable while inferred camera center varies. Current1920x1080
config does not justify fullscreen viewport assumption: principal x is100px
off full-buffer center. Viewport rectangle/independent pixel and clip convention
still require qualification, NOT silently guessed or declared resolved.
Confidence: CONFIRMED static locations/numeric consistency; STRONG HYPOTHESIS
external camera interpretation pending independent native screen-point comparison.
Algebraic recomposition alone is not runtime camera/physical image proof.

Decisions rejected: using composed matrix as world pose; inventing virtual-call
identity from slot alone; camera-mode archaeology; guessing FOV/near/far or1920
viewport; new gameplay solely to locate already recoverable camera state; changing
preview camera/materials or installing a wrapper. This task finds data, not wires
an unapproved aligned render/return path.

## Implementation, commands and validation

New tools/m1_component/analyze_live_camera.py,verify_active_camera_bytes.py;
tests/test_analyze_live_camera.py. Analyzer is offline bounded/read-only (8MiB,
2700records,128KiB report/exclusive output), no rapid bulk output mechanism.
Exact commands and expected outputs in camera-state-map. Python3.12.14, no new
dependency. Existing native component0.18/bridge/preview unchanged.

```
python -m unittest discover -s tests -p test_analyze_live_camera.py
python tools/m1_component/analyze_live_camera.py artifacts/m1/runs/20261016-211253-enabled/LIVE-BRIDGE-001-updates.jsonl --output docs/reconnaissance/evidence/20261016-active-camera-recovery.json
python tools/m1_component/verify_active_camera_bytes.py "C:/Games/Taldren Software Inc/Starfleet Command Orion Pirates/StarFleetOP.exe" --output docs/reconnaissance/evidence/20261016-active-camera-bytes.json
python -m unittest discover -s tests -p test_*.py
git diff --check
```

Four new tests PASS;93 full project tests PASS with PYTHONDONTWRITEBYTECODE=1,
TEMP/TMP=artifacts/m1/test-temp. Initial full-suite invocation omitted configured
TEMP/TMP and55 cases errored on restricted sandbox temporary-folder permissions;
corrected environment, all93 pass. No security-control changes or broad cleanup.
An early glob/guessed subsystem filename lookup failed; actual Pre-M0 map found,
no evidence inferred from missing file. Diff/link checks PASS. No native rebuild
required/claimed because runtime code unchanged. Original client SHA independently
reverified unchanged4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.

Evidence: docs/reconnaissance/evidence/20261016-active-camera-recovery.json and
20261016-active-camera-bytes.json (curated/versionable); source raw log646336bytes
remains in existing verified20261016-live-bridge-runtime.zip. No new raw/capture
archive needed; no evidence/original/asset/cache deletion. Capture bounds and
cleanup references remain LIVE-BRIDGE-001, not a new executed probe.

Other new files: docs/reconnaissance/2026-10-16-active-camera-state-map.md,this run
record. Updated docs/HANDOFF.md only. Final HEAD unchanged/index empty; inherited
work retained, nothing staged/committed. No game/controller/Kit/session/server
started or left active by this run. No sponsor action required for this discovery.

Exact next action: prepare a bounded camera-aligned live-bridge increment from
identified fields with independent projected-vertex/viewport validation, before
claiming matched camera output. Do not rerun broad camera motion/appearance tests
or roll directly into ray-traced lighting/image reinsertion from this finding.

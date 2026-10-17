# Codex run — one-click offline saved-mesh preview

- ID/date:`2026-10-16-mesh-preview-launcher`, America/New_York. Sponsor authorized
  preparation after Toolkit menus offered no direct existing-asset Open action.
  Later sponsor recognized the visible ship ("yup") and corrected camera labels:
  "side is front, front is right side". No new SFC run/capture requested.
- Start HEAD`fee152f`,150inherited pending short-status paths, staged diff empty.
  Read HANDOFF, accepted real export/Remix evidence, source/versioned bounds and
  installed Kit/viewport/HdRemix APIs. No requirements/gate change or final renderer
  choice; this remains a diagnostic external-consumer qualification task.
- Fuel Guard attach verified recent trusted hook; direct sandbox access denied,
  quota unknown, no daemon started. No helper/subagents or vendor source edits.

## Implementation / exact reproduction

New `tools/remix_ingest/` sources: `start_mesh_preview.cmd`, `run_mesh_preview.py`,
`sfc_mesh_preview.kit`, `kit_mesh_preview.py`, `preview_renderer.conf`,
`test_mesh_preview.py`. New [probe](../reconnaissance/probes/MESH-PREVIEW-001.md),
this run record; updated README/HANDOFF and prior result/Stage B current status.
No existing capture/ingestion/native ABI/hook implementation changed.

CMD invokes configured bundled Python3.12.14 directly, no PS/UAC workflow. Custom
small Kit app loads installed uiapp/viewport/capture/HdRemix/resources dependencies;
**not** the normal Toolkit mod-project GUI. No extension downloads. Exact accepted
USD SHA256/nonfixture result/corner comparison gate; scratch copy only. Anonymous
session layer adds camera/dome/key, never Save/export or mesh data edits. Source
and scratch hashes verified, accepted evidence immutable. Known100x import scale
retained, camera fits world bounds. Surface fidelity/normal interpretation not
silently repaired. Grey materials are diagnostic, not recovered game textures.

Installed Kit110.1.1/Toolkit1.6.0-dev+main.30229.3f23f80a.gl. Each fresh
`C:\Project\RemixJobs\preview-<UTC>-<id>` records config/actual argv/scripts/Kit/
guard hashes, bounds/camera matrix/renderer request/readiness and process outcome.
Inherited Windows Job Object guard unchanged:180s total,120s after ready,
8MiB console,128MiB warning/256MiB25ms-polled scratch stop (possible overshoot).
One1024x640interactive PNG or3smoke PNGs,8MiB each post-write check; reports64KiB.
No video/firehose. Shared GPU/driver/system caches not wholly isolated/bounded.

```powershell
python tools/remix_ingest/run_mesh_preview.py --smoke
python tools/remix_ingest/run_mesh_preview.py
python -m unittest discover -s tools/remix_ingest -p 'test_*.py'
python -m unittest discover -s tests -p 'test_*.py'
```

Use bundled Python path from existing manifest; tests use process-local
TEMP/TMP`C:\Project\SFC-Modernize Engine\artifacts\m1\test-temp`,
PYTHONDONTWRITEBYTECODE=1. Scoped outside-sandbox launches used after known
sandbox startup stall; no global elevation/security/settings change.
Actual CMD prepare-only invocation from its directory (`cmd /d /c
"start_mesh_preview.cmd --prepare-only"`) PASS; an earlier nested-quote shell
invocation failed before batch execution, corrected without source change.

## Material experiments / adjudication

All jobs below under `C:\Project\RemixJobs`; full original inputs/scripts/logs
retained. Process-success labels are provisional, never a substitute for visual QA.

| UTC job suffix | Result / information obtained |
| --- | --- |
| `041715Z-3c31d4d3` |19.157s,exit2. PNG completion preceded disk flush; falsely reported missing image. File later present but black. Corrected capture drain to installed vendor test pattern plus10s bounded file wait. |
| `041840Z-bb067bde` |18.954s,exit0. Explicit renderer support SUPPORTED,3black PNGs; clean process exit did not qualify preview. |
| `041943Z-7851e3b5` |42s,exit1624301229. Actual separate window black; log NRC EndFrame failure then VK_ERROR_DEVICE_LOST. GPU loss CONFIRMED, underlying driver/runtime defect unisolated. Agent close attempt failed activation after window died; no successful close click claimed. |
| `042055Z-50be64fd` |16.594s,exit0. Stronger synthetic lights1000/10000 did not establish useful preview; NRC default active. This was started before GPU-loss log was identified, not a deliberate repeated fault run. |
| `042236Z-5cb3f07e` |16.969s,exit0. Process-only NRC-off reference mode log corroborated; visible but overexposed/bloomed mesh PNG. No face/vector repair. |
| `042343Z-5a7da8c7` |16.531s,exit0. Original low lights0.7/2.0 plus local bloom-off; actual mesh visible in3views, inspected directly. |
| `042423Z-132d647d` |127.625s,exit0,zero owned processes. Actual window visible via computer-use; sponsor recognized ship and used views; normal automatic close,24553console bytes/543498peak scratch. No logged NRC activation/device loss in this corrected run. |
| `042650Z-03673e0d` |16.641s,exit0,zero owned processes. Final corrected camera convention; angled/above/front PNGs,647768peak scratch bytes/24448console bytes. Above inspected with nose upward. |
| `042810Z-f706ec0c` |CMD --prepare-only PASS; no renderer process launched, not an active job. |

Final renderer process environment (not system/global preferences):
DXVK_GRAPHICS_PRESET_TYPE=4, RTX_INTEGRATE_INDIRECT_MODE=0;
DXVK_RTX_CONFIG_FILE points to job-local `preview_renderer.conf` with bloom off.
Installed settings_bridge.py confirms Custom4/ImportanceSampled0 and actual log
confirms mode activation. NRC default fault vs corrected run is differential
evidence; not universal proof NRC is broken, nor a final game lighting choice.
Vendor runtime logged automatic crash telemetry upload/global user-config write
on failure. Codex did not invoke upload UI or modify global preferences; do not
claim whole-machine write isolation or change security/privacy controls to hide it.

Camera mapping corrected **only for this sponsor-identified asset**: Front camera
at+X, Side at+Z, Above at+Y with camera-up+X. Config preserves view directions;
no90degree mesh/transform/normal rotation. Existing imported world alignment remains
unqualified. PNGs show recognizability, not a faithful shaded/textured SFC scene;
dark/open-looking face regions still require separate surface/handedness analysis.

## Computer-use / validation

Used computer-use26.1007.71326 skill after reading full guidance/confirmation/API
instructions; initialized `@oai/sky` in node_repl. Selected only unique returned
window title `SFC captured mesh - OFFLINE PREVIEW (not the game) 0.1.0`.
First actual window black. Corrected actual window visibly showed saved mesh.
Attempted Above click was rejected because user input intervened; refreshed state,
observed changed view, and left controls to sponsor. No automated terminal/Explorer
commands/security dialogs or unrelated window inputs; no successful agent camera
click claimed. Captures shown by skill, not decoded/resaved. Own viewport PNGs are
separate versioned capture outputs. Sky window handles are now stale; reobserve.

Final20ingestion/preview/native tests PASS, existing73Python tests PASS. Test coverage
includes exact accepted hash/fixture gate, minimal app registry-off, no mesh repair/
Save, process-only NRC guard, sponsor camera convention. Real rendering/GUI/exit
checks corroborate mechanical tests; source assertions alone do not prove images.
Syntax/links/whitespace/archive checks recorded at final validation.

## Evidence / hashes / repository state

Nine scratch directories total8852997bytes/222files before compression. Useful
jobs and source snapshot zipped to ignored
`artifacts/remix-ingest/evidence/20261016-preview.zip`,5105585bytes, SHA256
`A3DD6326D53F8736336EA2E0355E6ACC70EF7C429F487840B3F11969DC8FD353`.
Small raw jobs retained; no deletion/global cache cleanup. ZIP is execution evidence,
not a pre-run whole-repository backup. Captured native USD still SHA256
`59B9C57ADAD61BEF4244F34B631B833BD6C34416791D3108ADE0537A64592696`;
reference/installed SFC executables independently unchanged
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
No SFC process/game launch, probe injection or game-directory generated files.

Final validation:20tool/preview/native+73existing Python tests PASS; source syntax,
135local Markdown references and tracked/new-file whitespace PASS. ZIP CRC and
237member SHA256 comparisons PASS against actual jobs/source snapshot.
Final HEADfee152f,151pending short-status paths (150inherited+new run record;
preview definition is inside an already-collapsed untracked probes directory),
staged diff empty. No stage/commit or unrelated cleanup. All eight renderer jobs
ended with zero remaining owned processes, including failed baseline; prepared-only
directory is not active. No new persistent server/admin session; helper parked.

**Exact next action:** sponsor may reopen `tools/remix_ingest/start_mesh_preview.cmd`
to use corrected views. Do not repeat export/ingestion or default-NRC crash baseline.
Any subsequent fidelity work must separately adjudicate visible face/normal and
unit/handedness contract, not silently repair originals or claim live integration.

Primary references checked2026-10-16:
[upstream renderer option declarations](https://raw.githubusercontent.com/NVIDIAGameWorks/dxvk-remix/main/src/dxvk/rtx_render/rtx_options.h),
[configuration layers/environment](https://raw.githubusercontent.com/NVIDIAGameWorks/dxvk-remix/main/documentation/RemixConfig.md),
[bloom option](https://raw.githubusercontent.com/NVIDIAGameWorks/dxvk-remix/main/RtxOptions.md).
Local installed bridge/runtime log govern the pinned binary; upstream main defaults
may differ and were not substituted for observed behavior.

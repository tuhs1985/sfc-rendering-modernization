# Codex run — bounded Remix ingestion preflight

- ID/date: `2026-10-15-remix-ingestion-preflight`, America/New_York. Sponsor
  authorized remaining offline preparation while asleep. No SFC gameplay/capture,
  driver change, GUI manipulation, helper, staging or commit authorized/performed.
- Start: HEAD `fee152f137a55a3efeb47a5c236ebf9e3e1951cb`, 146 inherited pending
  Git short-status paths; staged diff empty. Preserve all inherited work. Read
  HANDOFF, mesh-export contract/probes/prior run records and source/analyzers.
  CDD/gate disposition unchanged: M0 PASS, amended M1 technical integration closure
  recommendation awaiting sponsor; no aggregate TRL 4 or live Remix claim.
- Fuel Guard attach attempted at start: recent trusted hook verified; direct
  sandbox connection denied. No daemon started. Quota health unknown.

## Question / evidence

Can the installed standalone Toolkit's official model-ingestion pipeline process
our bounded OBJ derivative in an isolated, reproducible job? Tonight qualifies
synthetic data only; real selected-ship capture remains NOT EXECUTED.

- CONFIRMED environment: NVIDIA RTX4070Ti driver **617.42** via nvidia-smi.
  Newest GUI log `C:\Users\rober\.nvidia-omniverse\logs\Kit\RTX Remix\1.6\kit_20261015_024536.log`
  lines3760/5957 report HdRemix.dll loaded. Supersedes prior596.36 rejection for
  this launch, not historical logs. User's GUI was not closed or manipulated.
- Installed development Toolkit `C:\Project\RTXRemix`,1.6.0-dev+main.3f23f80a,
  Kit110.1.1+production.305458.6312fa25. Source audit: vendor CLI bootstrap,
  in-Kit `omni.flux.validator.mass.core.cli.run`, AssetImporter schema and metadata
  writer. Schema SHA256 `1860E98CFA28A3D0D0686A96E2DDAFAB92CC9B84BCDB29B29783028CD910C878`.
  Vendor queued quit behavior is an implementation assumption to validate, not
  evidence of successful conversion. Process0 alone cannot qualify ingestion.

## Implementation / reproduction

New `tools/remix_ingest/` files: `bounded_job.cpp`, `build_remix_job.ps1`,
`run_remix_ingest.py`, `kit_ingest.py`, `test_bounded_job.py`,
`test_remix_ingest.py`, `README.md`. Modified HANDOFF and Stage B probe definition;
this new run record. No SFC component/hook/capture ABI changes in this execution.

- Native x86 C++17 helper creates an unnamed KILL_ON_JOB_CLOSE Job Object;
  PROC_THREAD_ATTRIBUTE_JOB_LIST assigns child atomically at creation, HANDLE_LIST
  restricts inheritance. Stops only its owned process tree, never Kit by name.
- Copied/pinned vendor schema retains all checks, only input/output context changes.
  Copies packet/receipt into fresh scratch, derives OBJ/MTL/manifest there; no
  vendor/source/client edits. Real-run entry requires clean normal exit and hash;
  explicit `--fixture` bypass is labelled synthetic and must not qualify gameplay.
- Work root `C:\Project\RemixJobs`, outside repo/game/vendor. Short paths avoid
  installed script-parser whitespace issues. Kit portable cache/data/log root
  inside each job; shared GPU/system caches not wholly isolated or size-bounded.
- Job180s including startup; vendor conversion120s; console hard cap8MiB;
  scratch128MiB warning/256MiB stop polled25ms (can overshoot, not disk quota).
  Geometry inspection2MiB; reports64KiB. Native limit tests intentionally exercise
  saturation without multi-GB output. Never clear global caches.
- Inspector requires affirmative vendor `validation_passed`, mesh topology and
  bounded arrays; records units/axis/local-world matrix/normals/UV/bindings.
  Comparator checks cyclic ordered triangles/native local coordinates rounded
  five decimals, no axes/scale/winding repair. Full attribute/world alignment and
  recognizable real-ship preview remain unqualified.

Tools: bundled Python3.12.14, PowerShell7.6.5, Git; MSVC14.51.36231 x86 via
VS2026 vcvars32, `/std:c++17 /EHsc /W4 /WX /O2 /MT`. Process-local TEMP/TMP
`artifacts/m1/test-temp`, PYTHONDONTWRITEBYTECODE=1, no global setting changes.

```powershell
pwsh -NoProfile -File tools/remix_ingest/build_remix_job.ps1
python -m unittest discover -s tools/remix_ingest -p 'test_*.py' -v
python -m unittest discover -s tests -p 'test_*.py'
python tools/remix_ingest/run_remix_ingest.py artifacts/m1/test-temp/mesh-component --fixture --execute
```

Use configured bundled executables, not assumed PATH installations. Stage B probe
records the exact workflow/limits; job-metadata.json preserves actual Kit argv.

## Validation / runtime result

- Native build PASS warnings-as-errors. Ten new offline/native tests PASS:
  normal/quoted child, console floodcap, scratch stop, timeout/descendant cleanup,
  unrelated process survival, schema-copy invariance, overwrite/size refusal,
  geometry/winding rejection, preserved deadline diagnosis and outer timeout
  result. Existing73 Python tests PASS. Native SFC component
  unchanged; prior offline component validation remains historical evidence.
- No gameplay or real ship ingestion performed. Final PowerShell parser PASS;
  Git whitespace/link/source checks as recorded below.

### Actual bounded jobs / adjudication

Job directories are UTC-stamped under `C:\Project\RemixJobs`:

| Job | Observation | Result / measured limits |
| --- | --- | --- |
| `20261015-065846Z-67cff6c2` | Restricted sandbox stalled at async-engine startup,573ms vendor log time. No conversion/inspection. | Guard reason22 deadline;180016ms,949 console bytes,94163 peak scratch bytes,zero owned processes left. |
| `20261015-070225Z-be1cca2e` | Same bounded workflow outside sandbox progressed;14 missing-plugin validation errors. Extensions catalogued but not enabled by settings merge. | Application exit2;1968ms,6348 console bytes,284685 peak scratch bytes,zero owned processes left. Not geometry rejection. |
| `20261015-070313Z-db1c59c8` | Explicit `--enable` for vendor-declared resource/context/check/selector/resultor plugins; copied schema unchanged. Official pipeline validation affirmative; one mesh/triangle. | SYNTHETIC_PREFLIGHT_PASS;exit0/reason0,4047ms,89717 console bytes,521317 polled peak scratch bytes,zero owned processes left. Final directory522255bytes. |

One environment retry separated sandbox constraint from local capability; one
materially justified configuration retry corrected our plugin startup. No blind
loops, increased limits, vendor edits or broad privilege/security changes. Sandbox
as cause of first stall is STRONG HYPOTHESIS from differential observation, not an
identified Windows root cause. Outside-sandbox execution used approved escalation
for this specific owned synthetic job, not a permanent elevated service.

CONFIRMED successful data: vendor `ship.usda.meta` validation_passed=true;
`geometry.json` records prim `/ReferenceTarget/XForms/World/ship/source_000`,
three points, one face with indices0/1/2 and unchanged local coordinates. Normals
+Z faceVarying; fixture UV allzero faceVarying, rightHanded; material bound.
Vendor queued post_quit followed by synchronous inspection worked in this test.
**A100x uniform local-to-world parent transform was authored**, metersPerUnit1,
Y-up. Do not label world-scale preservation qualified. Its underlying importer
unit interpretation and actual-ship attributes/preview remain unresolved; no
repair/normal flip/axis change applied. A neutral-grey synthetic triangle is not
a recognized ship or recovered texture/material success.

Successful USD3608bytes SHA256
`1E2052193823ADF904240A5D0D1757150326B576FF633E972EC4B7130CF930EB`.
Guard binary SHA256
`9EFBAAE31FE7A8E57BFFF76FCF51D80282E0FE192F742C6F9F04A3B0E895C807`.
Source/config/exact argv/metadata/logs remain in each job. Initial failed result's
generic missing-inspection error is superseded by its exact job-result deadline;
runner corrected/tested to preserve stop_reason before inspecting missing outputs.
Final runner also records source/Kit/tool versions and execution guard hash for
future jobs; prior runtime metadata retained unchanged, not backfilled as original.

### Preservation / final state

All three jobs plus the final source snapshot compressed to ignored
`artifacts/remix-ingest/evidence/20261015-synthetic-preflight.zip`,138012bytes,
SHA256 `BAF7E4FA188E5DC756D11AF21CE0844965B5BB396D056F30277414BAC6FD5E68`.
ZIP CRC and every member's SHA256 compared to source PASS:52files,934896 expanded
bytes. No material cache volume generated in these portable roots; no deletions
needed/performed. Raw small jobs retained. Archive is evidence/source snapshot,
not a pre-run backup of the whole dirty repository. No original/reference writes.

Both reference and installed SFC client hashes remain
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
CDD unchanged SHA256
`BF5384D2586601AAA28DB36970937A3B40F598E12002B3450BF2E7D9562FA352`.
No game files generated by this offline work, no hooks loaded/restored, no active
owned process, new server or persistent tool session. Sponsor GUI not disturbed;
reobserve it and desktop/sandbox/admin state next session.

Final Git HEAD fee152f,148 pending short-status paths (146 inherited + new tooling
directory/run record); empty staged diff. No staging/commit or unrelated cleanup.
Native binaries/evidence ZIP ignored; human-curated sources/runbook/checkpoint
versionable. Build,10new tests,73existing Python tests, PS parser, Python syntax,
122local Markdown path checks and tracked/new-file whitespace checks PASS. No
gate promotion or final architecture selection.

**Exact next action:** sponsor runs the prepared MESH-EXPORT-001 two-ship capture
once when available. Then validate/ingest the accepted saved packet, qualify
attribute/scale behavior and obtain a recognizable preview; no repeat gameplay
merely for conversion. Do not re-run synthetic preflight or reconstruct the old
D3D9 shim blindly.

## References

[NVIDIA Kit configuration](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/guide/configuring.html),
[Kit portable-root argument](https://docs.omniverse.nvidia.com/kit/docs/carbonite/latest/docs/Kernel/CommandLineOptions.html),
[Kit token/cache scope](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/guide/tokens.html),
[Windows Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects).
Official references checked2026-10-15; local installed source governs actual schema/API.

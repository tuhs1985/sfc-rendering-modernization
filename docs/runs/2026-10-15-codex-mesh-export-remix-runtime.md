# Codex run — adjudicate real mesh capture and import into Remix

- ID/date:`2026-10-15-mesh-export-remix-runtime`, America/New_York.
- Authorization: sponsor ran prepared MESH-EXPORT-001 entry after readiness
  instructions, then reported "done, no issues noted". Approved first test includes
  separate Toolkit ingestion. No new gameplay, renderer integration or gate change.
- Start HEAD`fee152f`,148pending short-status paths, staged diff empty. Read newest
  HANDOFF, Stage A/B probes, capture metadata/result/receipt/analysis, component log,
  summary/generated evidence, prior preflight and existing ingestion runner.
- Fuel Guard attach: exact thread recent hook confirmed, direct sandbox connection
  denied/quota unknown; no daemon/helper/subagents started.

## Question / result

Can the prepared semantic collector export a complete admitted primary mesh during
normal tactical play and can the bounded installed Toolkit consume it? **Capture/
OBJ PASS; actual geometry ingestion accepted, recognizable viewport preview still
pending.** [Curated result](../reconnaissance/2026-10-15-mesh-export-remix-result.md)
records adjudicated counts/provenance, attribute comparison and limits. No TRL or
full Toolkit Stage B PASS claimed.

## Exact execution / revisions

Sponsor ran `powershell.exe -NoProfile -ExecutionPolicy Bypass -File
"C:\Project\SFC-Modernize Engine\tools\m1_component\start_mesh_export_session.ps1"`.
Entry inherited elevated parent, built/tests, launched normal launcher workflow;
no routine UAC request by this analysis session. Two-ship fixture,90s automatic
gate,120detailed frames/10000events/8owners,16MiB warning/32MiB event-log hard cap,
hot geometry hook disabled. Mesh1packet/2attempts max/512polygons/2MiB cap;
actual1attempt/57744bytes. No special camera/movement phases requested.

Game run`20261015-190310-enabled`; metadata start19:03:10EDT, normal exit result
19:06:14EDT, PID5500. Runtime component0.14 SHA256
`C40D1A7774A7750A67EE95C17D8D6A98D950C8A71EF3971A80E93B98D127F78D`,
controller`C355C026D5E72521697DFA4633B621265A9D59D4C511100EBD1B803CBC653029`.
Rebuild hash recorded rather than assuming preparation binary byte identity.
No native source/ABI/hook change made by this execution.

Bundled Python3.12.14/PowerShell7.6.5/Git. Installed Toolkit/pinned schema/Kit and
guard hashes/argv in `C:\Project\RemixJobs\20261015-231057Z-19b131ce\job-metadata.json`
and execution.json. Outside-sandbox execution chosen because preflight established
restricted-startup stall; scoped approval, no permanent privilege/security change.

```powershell
python tools/remix_ingest/run_remix_ingest.py artifacts/m1/runs/20261015-190310-enabled --execute
python -m unittest discover -s tools/remix_ingest -p 'test_*.py'
python tools/remix_ingest/compare_obj_attributes.py C:/Project/RemixJobs/20261015-231057Z-19b131ce/input/ship.obj C:/Project/RemixJobs/20261015-231057Z-19b131ce/geometry.json --output C:/Project/RemixJobs/20261015-231057Z-19b131ce/corner-comparison-numeric.json
python -m unittest discover -s tests -p 'test_*.py'
```

Use configured bundled Python, PYTHONDONTWRITEBYTECODE=1 and process-local
TEMP/TMP`C:\Project\SFC-Modernize Engine\artifacts\m1\test-temp`. Initial full
suite invocation omitted that TEMP override:29PermissionError failures in sandbox
AC/Temp. Corrected invocation73/73PASS; no test/source change to resolve environment.
No attempt to weaken ACLs or clean inaccessible global sandbox directories.

One real Toolkit job, no retries:180s total/120s vendorconversion,128MiB scratch
warning/256MiB polled stop/8MiB console, bounded own process tree. Actual11.781s,
~1.18MB peak scratch, clean exit/no remaining children. No global cache deletion,
user GUI manipulation or game launch by Codex. Full actual limits/results in probe
and job-result.json; shared driver caches outside portable scratch not wholly bounded.

## Additional offline analysis / engineering adjudication

Added reusable `tools/remix_ingest/compare_obj_attributes.py` and
`test_obj_attributes.py`, no capture/ingestion behavior change. Bound<=512triangles,
inputs<=2MiB, output<=64KiB, refuse overwrite. Compare entire ordered triangle
corner tuples and neutral source binding, allow cyclic rotation only; explicitly
reject unsupported interpolation, UV/vector/group/winding changes. Four tests
including float roundoff threshold; total ingestion/native14tests PASS.

First exact five-decimal bins flagged5triangles; diagnostic printed expected vs
observed keys and isolated tiny normal rounding-boundary differences. Changed
comparison to explicit1e-6 absolute numerical tolerance and reports maximum error,
no geometry/data repair. Initial corner-comparison.json retained; subsequent
corner-comparison-numeric.json confirms all452 and maxnormalerror2.98e-8. Standalone
USD/data arrays unchanged. Existing runner result remains PREVIEW_PENDING.

## Files / preservation / final state

Created: two comparator/test sources above, this run record, curated result.
Updated: docs/HANDOFF.md, Stage A/B probe statuses and tools/remix_ingest/README.md.
All inherited dirty work preserved; no source/reference/vendor/game edits or
unrelated cleanup. Real capture/derived files and Toolkit outputs remain ignored.

Verified evidence ZIP includes complete capture, Toolkit job and current ingestion
sources: `artifacts/remix-ingest/evidence/20261015-real-mesh-remix.zip`,251983bytes,
SHA256`CB3B5BEAE6AFA00F7220AC270582BF7CCDECD9FEB649F735E9973F8E8878B6EA`.
Capture+job uncompressed1812460bytes before archive; small raw evidence retained,
no deletions needed/performed. ZIP member/content checks recorded at final validation.

Reference/installed client SHA256 independently checked unchanged
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
Game-folder owned winmm/component/config/gate files absent. Hooks restored and
normal exit confirmed by receipts/controller; sponsor no issues. No owned active
Toolkit job/server; user GUI state not assumed. M1/gate/requirements unchanged.

Final validation:14ingestion/native tests and73existing Python tests PASS; source
syntax,132local Markdown references and tracked/new-file whitespace checks PASS.
ZIP CRC and47input/output/code SHA256 member comparisons PASS; archived README
predates final documentation update, intentionally excluded from current-file
equality check. Actual packet/USD/code snapshot preserved; nothing deleted.
Final HEADfee152f,150pending status paths (148inherited+2new documents),
staged diff empty; nothing staged/committed. Exact next action: preview the saved
USD in Remix and recognize the selected mesh; no additional game capture needed.

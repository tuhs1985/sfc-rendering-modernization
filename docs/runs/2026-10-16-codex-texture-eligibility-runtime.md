# Texture fallback eligibility — runtime adjudication

Run ID/date: 2026-10-16-texture-eligibility-runtime / 2026-10-16.
Active task: offline texture recovery; no new implementation/gate advancement.
Starting HEAD fee152f137a55a3efeb47a5c236ebf9e3e1951cb; inherited uncommitted
work preserved, index empty. Sponsor said "ok, hopefully that is enough";
no explicit visual-behavior report inferred from that message.

## Question and result

Does the captured manager state qualify for the fallback secondary+primary route?
CONFIRMED captured inputs in fresh component0.17 run
`artifacts/m1/runs/20261016-171830-enabled/TEXTURE-EXPORT-001.json`:
status1, textures1, secondary path word511, multitexture0, validation mask3,
previous alpha-test flag0. Same-epoch kff.mod, five groups, ten live resource
IDs170–179 (process-local; do not substitute old pointers/associations).

Exact-build branch evidence remains in
`../reconnaissance/2026-10-16-texture-path-runtime-result.md` and probe definition
TEXTURE-EXPORT-001: mask bit1 set with prior flag0 requests modes2 then1.
Analyzer independently checks packet checksum/identity/source groups and reports
MODES_2_THEN_1_REQUESTED with no missing eligibility inputs. This closes the
instrumentation gap, rejects primary-only eligibility at this snapshot, and
supports the source-derived secondary+vertex-lighting then primary-multiply
interpretation. NOT direct GPU pass completion, physical emission calibration,
color-space fidelity or proof across every frame. Existing provisional preview
remains labelled; overall fidelity/texture result PARTIAL, no substitute textures.

## Runtime, bounds and safety

Existing start_texture_export_session.ps1 / TEXTURE-EXPORT-001, same two-ship
fixture/automatic gate,90s maximum;120 detailed frames/10000 events/eight owners,
16MiB warning/32MiB stop, ten resources/4096 squared/64MiB warning/128MiB image
limit. Geometry hook and all visual interventions OFF. No new hook/ABI change.
PS7.6.5/VS2026 x86 component0.17; build/test entry unchanged from preflight.

5395 frames observed;1180 detailed events;338289-byte CSV, no log truncation,
size warning, owner/thread overflow or rejected semantics. One57744-byte mesh,
2557-byte reference JSON; image manifest primary_images_ready true,
1177434 original/derived image bytes. No multi-GB output mechanism.
Known00509843 exception5399, preserved as bounded known category, not new failure.
Detailed capture saturation expected; summary continued. Do not interpret zero
geometry counters as missing rendering: diagnostic geometry hook intentionally OFF.

Normal exit observed, controller component_state=removed/hook_bytes_restored=true,
component hooks_restored=true. No active SFC/controller. Owned winmm.dll,
m1_component.dll,m1_gate.dll,m1-component.ini absent from game directory.
Installed client independently rehashed; matches before/after:
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.

## Reproduction, evidence, validation and repository state

Python3.12.14, bytecode disabled, TEMP/TMP artifacts/m1/test-temp:

```
python tools/m1_component/analyze_texture_path.py artifacts/m1/runs/20261016-171830-enabled --output docs/reconnaissance/evidence/20261016-texture-eligibility-review.json
python -m unittest discover -s tests -p test_analyze_texture_path.py
```

Six focused analyzer tests PASS. Existing full native/project/preview suites were
passed during preparation; not rerun/claimed here. git diff --check PASS.
Versionable derived analysis validates fresh packet SHA256
79726bc09b979209c0f1c944f0a2447b5c7da803dc79f8b264a0edd2b86d2eb5.
Useful run archived outside Git-tracked output:
artifacts/remix-ingest/evidence/20261016-texture-eligibility-runtime.zip,
863557bytes/43 files, all archive entry SHA256 values checked against originals.
No raw evidence/assets/cache deletion. No source/default-preview changes.

Files created: this record, curated texture-eligibility-review.json.
Files updated: HANDOFF.md, texture-path-runtime-result.md. Prior evidence retained.
Fuel Guard exact-thread hook receipt verified; direct sandbox access denied/quota
unknown; no daemon/helper/server spawned. No persistent runtime state remains.
HEAD unchanged, inherited work preserved; index empty, nothing staged/committed.

Exact next action: use the captured branch/algebra to review the existing provisional
preview's documented material mapping offline, without another gameplay request
just for these settings. Any fidelity claim still needs matched visual comparison;
no automatic brightness, normal, winding or UV correction authorized by this result.

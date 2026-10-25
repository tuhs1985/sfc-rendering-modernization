# Run167 — one concrete effects/resource route qualified offline

Date2026-10-24 America/New_York. Sponsor authorized proceeding from Run166's
exact next action: inspect producer/vtable callers of0x0041043B/0x004ED080.
Authority: newest handoff, approved rendering-family characterization/probe;
M1 plan's current gate allocation unchanged. API experiment stays parked.

## Completed / findings

- Narrow static inspection of observed call sites, referenced constructors,
  explicit vtable slots and resource initialization/finalization; no broad asset
  archaeology. Original pre-M0 disassembly, verified client PE and existing
  texture-registry authority used. No online/upstream capability claim needed.
- Concrete global-list vtable0x007AA050->draw0x004EFA4A, constructor0x004EF0BD:
  loads missile.mod and participates in the already observed0x004ED080chain.
  Same routine has a model render and separate four-corner textured branch.
- Resource initializer resolves fx0..fx6 via original registry, BMP then PCX.
  This draw selects live fx0 ID at0x0092F5FC; manager+134 stores it at+1F24;
  primitive finalizer reads it and mode7 submits four corners using instance
  UV variant+44. End/selected resource/native submission linkage confirmed
  statically. Actual successful filename/epoch/weapon/owner not captured yet.
- Global-list insertion/unlink provides candidate object epochs independent of
  visibility and GPU resource residency. Shared fx0 does not distinguish owners.
- Attached slot+8 dispatch0x0041043B is not a dedicated explosion draw. The
  explosion-related vtable routes slot8to update/side-effect work0x0041F5F5
  versus slot12to model rendering0x00413AC3. Generic trait type at the sampled
  call remains unknown; do not promote the late-run explosion hypothesis.

Detailed facts/unknowns: [effects path](../reconnaissance/2026-10-24-effect-resource-path.md).
Curated fields: [evidence](../reconnaissance/evidence/20261024-effect-resource-path.json).
This is **STATIC PATH CONFIRMED / RUNTIME INSTANCE JOIN PENDING**, not effects
rendering, replacement, universal coverage, milestone/TRL or explosion proof.

## Implementation / partial work

Added read-only verifier `tools/recon/verify_effect_resource_path.py`, reusing
inspect_pe.py. Exact client SHA required;38explicit instruction/string/vtable
anchors, file-backed256B maximum individual read and fail-closed mismatch.
No source asset file, image pixels, geometry payload or runtime memory read.
Added4unit tests in tools/recon/tests/test_effect_resource_anchors.py.

Defined [EFFECT-RESOURCE-JOIN-001](../reconnaissance/probes/EFFECT-RESOURCE-JOIN-001.md):
default-off concrete producer/resource/primitive metadata, constructor/unlink
epochs, selected ID/UV/branch scope and bounded registry filename snapshot.
Nested/delayed batches must remain unassociated unless provenance supports a
join. Definition explicitly **NOT IMPLEMENTED / NOT READY FOR GAMEPLAY**.
No executable hook/ABI assumption or runtime source lock was changed this run.
Four-corner geometry/state convention and exact effect type remain unqualified.

## Validation

- Actual verified copied client:38anchor checks PASS. Repro:
  `python -B tools/recon/verify_effect_resource_path.py <verified-test-client>`.
- Four new read-bound/file-section/mismatch tests PASS; all8offline reconnaissance
  helper tests PASS0.001s, including prior Run166 effective-state/lifecycle checks.
- Existing504Python regressions PASS7.655s (existing Pillow deprecation warnings).
- Survey and normal multi-ship Performance read-only preflights PASS; neither
  launched game or renderer. No native rebuild needed for read-only analysis.
- New Python parse, evidence JSON, document links and git diff --check PASS.
  Pinned normal renderer/config/survey qualification unchanged. Client hash
  checked directly; this run did not modify a game directory.

## Files / runtime / repository

Added verifier/test, effects-path document, probe definition, curated JSON and
this run. Updated family map/STATUS/HANDOFF and refreshed reviewed Obsidian
tracker with concurrent-edit hash guard. Run163–166dirty work preserved.
HEADfd79ce5/indexempty/allunstaged/uncommitted/no push. No deletion/archive or
large output; prior18.96GB/20GBdated evidence inventory remains approximately
unchanged. No SFC, Remix, Toolkit, profiler, helper or agent started. FuelGuard
attached via trusted existing hook; no daemon spawned. No live tool/channel/
process state is required to resume.

## Exact next action

Implement and offline-qualify only EFFECT-RESOURCE-JOIN-001's concrete producer/
resource observation, including ABI/original-flow preservation and delayed-flush
negative controls, before preparing its sponsor gameplay check. Keep original
effects/ship renderer/UI intact. Do not repeat the broad capture, resume API,
infer resource roles from names or implement new effects support at this stage.

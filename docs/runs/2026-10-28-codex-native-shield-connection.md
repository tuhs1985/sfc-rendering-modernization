# Run219 — native shield connection implemented; paused before full qualification

Sponsor requested connection, then authorized continued implementation, then
explicitly requested a safe pause for the night. This checkpoint is **PAUSED,
NOT READY FOR GAMEPLAY**. No SFC was launched and the complete Remix foreground
fixture has not run. Latest accepted gameplay remains Run216.

## Implemented

- `tools/native_foreground/draw_snapshot.h`: retains original native VS/PS,
  input layout, raster/blend/depth state, viewport/scissor, samplers and binding
  versions; freezes mutable VB/IB/CB/images through Run218's GPU-copy storage.
  Views are prepared outside the source draw. Supports bounded direct indexed
  triangle VS/PS draws, one VB, eight constant buffers per stage, sixteen PS
  views sharing at most three images. Other stages/ranges/predication/stream
  output/UAVs and unsupported layouts reject rather than reconstruct shaders.
- `masked_assembly.h`: replacement color/depth/stencil written together; native
  additive shield replay only on pixels the hull actually replaced. Preserves
  front/back occlusion and avoids doubled effects outside that coverage.
- Native history can opt into **R24G8/D24S8 instead of its R32 depth planes**:
  same four bytes/pixel, conservative total16planes/126.5625MiB unchanged.
  Native minimum of eight samples is resolved through the actual GPU shader.
  Invalid native depth retains stencil bit2; replaced hull uses bit0. D24 is an
  explicit precision conversion, not a claim of bit-identical R32 storage.
  Returned physical hull depth remains the Run215 float32 geometric output.
- `shield_scope_hooks.h`: x86 hooks for00426563 and0069EC60, caller004165AF;
  original native arguments/body maintained. Entry state flush excluded,
  restore flush included. Registers/flags and FP/SSE state protected around
  scope helpers. Native bytes checked/restored, callbacks drained. Add-on CODE
  is pinned for process lifetime to protect wrapper epilogues; GPU objects and
  hooks still release normally. Do not describe this as mid-process DLL unload.
- `source_notice.h`: separate4160B version1 extension at replacementOffset+8192
  inside the existing64KiB reservation; established4416B version2 ledger remains
  unchanged. M1 publishes selected owner/frame/generation/revision/native ship
  context. Entry-time ship+1BC is diagnostic, **not absence proof**. A completely
  observed frame and rejected/invoked markers distinguish no shield from lost
  capture. Rejects partial install frames, unknown selected-owner calls and
  nesting ambiguity. Native resource ID0 is not presumed invalid.
- `shield_controller.h`: three source-frame slots, eight draws each,32MiB
  GPU buffer/image cap. Worker prepares storage/views; no source-callback
  allocation/readback/waits/IO. Worker request event, nonblocking GPU completion
  checks. Original native shader resources, not a guessed FX material.
- Existing receiver pairs foreground/background/replacement on the same source
  frame. Incomplete foreground frames are not committed. Existing two extra
  complete-picture presentations and automatic native recovery are reused;
  a one-frame foreground preparation miss does not immediately force fallback.
- M1 stop requests foreground hook teardown and requires its bounded worker ACK
  before unloading semantic storage. Worker also responds to native_stop.
- Separate `start_d3d9_shield_replacement_session.ps1` and `--native-foreground`
  options added. Current appearance settings preserved. Launcher gates remain
  closed until genuine standalone qualification receipts exist.
- Fixture-only native shield producer/factory/verification in `shield_fixture.h`:
  original shader on an8sample native target, animated constants, two triangle
  batches (including restore flush), live captured resources and actual Remix
  output. Pixel verifier compares hull+native contribution and untouched outside
  against the SAME frame. Factory is restricted to the owned fixture path;
  not a synthetic output substitution in SFC. This FULL fixture is NOT RUN yet.
- Build fingerprints now cover `tools/native_foreground`; native focused build
  records compiler-reported transitive project dependencies.

## Validation and corrections

As-built focused GPU tests: **271 checks PASS**. Native x86 hook tests:
**17 checks PASS**, including argument/return/LastError, FP/SSE preservation,
flush boundary and original byte restoration. Python regressions: **583 PASS**.
M1 component/proxy/gate/controller and normal/live return builds passed.
`source-freeze.json` matches current source and native `build.json` input hashes
at pause. Binary timestamps follow their latest source edits. No full runtime
qualification or new sponsor result is implied by those builds.

Actual packed-history min8/invalid-sample path was tested, not only a CPU model.
Front shield, rear shield, native occluder, outside coverage and invalid depth
were exercised in the isolated hardware test. GPU/resource copy uses the
Microsoft CopyResource/GetData APIs recorded in Run218.

A prototype crashed after requesting only optional range outputs from the
context1 constant-buffer getter. Supplying full buffer outputs and releasing
their references corrected the fixture; current tests pass. Do not restore the
null-output variant. Restricted-context import-library/temp-file errors were
handled with normal approved Windows build/test access, not as code failures.

Reused the archived Federation/Romulan surveys without a new capture. Full
raw hashes verified;304 sampled shield-context records reviewed. One VB identity
per run; two IB variants in Federation include the previously excluded unbound
entry flush. No negative base vertices observed. Actual native shield candidate
is256x256 RGBA8 typeless, one mip, one sample; native color view is linear RGBA8
on an8sample typeless resource. Detailed derived records:
`artifacts/player-replacement/run219/historical-buffer-epochs.json`.
These remain context observations, not a universal FX ownership claim.

## Remaining / do not launch yet

The new path is connected in source but **not qualified end to end**. Before
running it, finish the native multisample compatibility review: replay is into
a single-sample target, while the original native target is8sample. Captures
show full sample masks, but the implementation still needs explicit unsupported
sample-mask/sample-frequency handling. Do not claim arbitrary native shader AA
equivalence. Microsoft `ID3D11ShaderReflection::IsSampleFrequencyShader` and the
existing ReShade pipeline-initialization bytecode are a possible supported
inspection route; no reflection cache has been implemented or decided.

Then run the new standalone foreground fixture (steady and fault profiles),
review its actual matching-frame pixel checks and teardown ACK, and generate
qualification through real tests. Refresh affected legacy build/launch gates
as required; never edit old receipts to claim unrun tests. Existing source locks
can reject even the old launcher while this new source is unqualified.

No full Remix foreground fixture, current-code player/tuning preflight, live
shield PASS, alpha readiness or milestone completion is claimed.

## Parked state / files

New files are under `tools/native_foreground` (snapshot, assembly, hooks,
controller, notice, fixture contract/producer, native tests/build), plus
`tools/remix_runtime/native_foreground_qualification.py`,
`tools/d3d9_proof/start_d3d9_shield_replacement_session.ps1` and
`tests/test_native_foreground.py`.
Modified integration files: `tools/m1_component/m1_component.cpp`,
`tools/remix_runtime/{scene_frame_buffer.h,replacement_presentation.h,
d3d9_game_receiver.h,return_addon.cpp,return_fixture.cpp,run_return_fixture.py,
run_return_game.py,additive_qualification.py}`. Run218 retention/scope/tests
also updated. Prior dirty work preserved; index empty; no commit/push.

Logs, exact source/binary/settings hashes and pause state:
`artifacts/player-replacement/run219/pause.json` and build/test logs.
`pre-build-binaries.zip` is a SHA-verified52-file **binary/receipt rollback**,
not a complete repository/source backup. Do not blindly restore it over current
source. No game/renderer/fixture/compiler job remains; no tool session must
survive restart. Existing Fuel Guard daemon is advisory and was not started
or stopped by this task. Both client EXEs and current lighting/rendering hashes
were rechecked unchanged at pause.

**Exact next action:** resolve native sample-mask/sample-frequency compatibility
for single-sample replay, then run the prepared standalone `--native-foreground`
fixture before any SFC checkout; rebuild only if that review changes code.

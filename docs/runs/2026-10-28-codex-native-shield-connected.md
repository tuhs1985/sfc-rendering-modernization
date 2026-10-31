# Run220 — native shield preservation connected; ready for sponsor checkout

Sponsor resumed Run219. The connection is **offline qualified and ready for a
player-ship game checkout**. No SFC was launched by Codex. Latest accepted game
result remains Run216 until this checkout is reviewed. This is not an alpha or
formal milestone completion claim.

## What changed

SFC still renders its background, tactical UI and effects. We retain the selected
player shield invocation at the characterized native boundary, including the
original shaders, state and exact mutable buffer/image versions. After the
matching Remix hull replaces its saved source frame, those native shield draws
are replayed only over the hull pixels that were overwritten. Native foreground
in front remains visible; back-facing/occluded work remains depth tested. Pixels
outside the replacement keep their original shield contribution without doubling.
No new shield material, texture conversion, colour subtraction or height shift.

Run219 supplied the bulk connection. Resumed review/qualification corrected:

- Original native8MSAA is replayed onto the single-sample assembled picture.
  Default-off native shader-creation observation uses ReShade init_pipeline and
  Microsoft reflection to qualify pixel-frequency shaders. Unknown/sample-frequency
  shaders, coverage/depth outputs, coverage inputs, partial sample masks and
  alpha-to-coverage reject. D3DDisassemble checks special coverage operands that
  may be absent from reflected signatures. All reflection/disassembly/private
  metadata creation happens at shader creation, not observed draw callbacks.
  This is a bounded supported subset, not exact8MSAA edge equivalence.
- Foreign/deferred context work inside the selected span invalidates that frame;
  it cannot silently become an empty shield. Wrong-thread callbacks are rejected
  before touching render-thread-owned recording state.
- ReShade may expose the wrapped device through GetDevice and the native device
  through get_native. Comparing those addresses prevented resource capture in
  the full fixture. Setup now applies a private, unique device tag through the
  standard D3D11 private-data interface; capture checks the same actual device
  through either wrapper. No internal unwrapping GUID or vendor patch.
- Teardown originally published again after Receiver closed its source mapping.
  Stop is idempotent and the controller is destroyed before unmapping. Hook
  restoration/drain ACK is cleared for a new device and issued only by its own
  stopped worker. Session counters survive graphics-device recreation.
- Synthetic fixture FX resources are now released/recreated with their device.
  The fixture no longer resolves an old device texture into a new backbuffer.
  Failed/intermediate runs remain recorded; their generated GPU data is archived
  with decompressed SHA verification and recovery receipts under run220.

All original settings/assets and the physical hull-depth fix remain unchanged.
Optional D24S8 history reuse retains the16plane,126.5625MiB controlled output
footprint; there is no new fullHD output plane. Three capture-frame slots, eight
native draws per slot,4MiB per packet and32MiB total snapshot allocation remain.
No callback wait, file access, readback or resource creation was added. Private
shader metadata has shader-object lifetime; device tags are removed at teardown.

## Validation

- **286 focused hardware GPU checks**, **17 x86 ABI/hook checks**, **583 Python
  regressions** pass. Native original shader/binding retention, mutable resource
  overwrites, front/back shields, native occluders, unchanged outside pixels,
  invalid/min8depth and unsupported shader cases are exercised.
- Genuine final Remix steady fixture: **599/600**
  measurement-window replacements. Three independent same-frame pixel checks
  compare actual returned hull colour plus animated native contribution. Native
  HUD/background exact, graphics-state errors0, resize/recreation and owned exits0.
- Final fault fixture proves one missed output resumes, sustained misses recover
  to native, generation advances and replacement resumes, source-gap recovery,
  and explicit stop stays native. **2 reactivations**, maximum
  **2** extra complete-picture presentations. Its382/600 window
  includes deliberate withheld output and the explicit stop; it is not a steady
  delivery measurement.
- Original hooks restored ACK1; setup rejects0. Both current replacement and
  native-foreground receipts issued through actual qualification functions.
  Dedicated native-light component rebuilt and worker/queue/decoder tests pass.
  Final fixtures record that actual new component hash, rather than editing old
  receipts. Normal and live add-ons compiled; launcher read-only preflight PASS.
- Both game EXE hashes and lighting/rendering files unchanged. No game process,
  renderer or fixture is required to stay running. Evidence 19,057,028,335 bytes
  below the20GB aggregate output allowance. Dependencies are outside that
  existing evidence-accounting scope. Index empty; no staging/commit/push.

Final evidence: [machine-readable record](../reconnaissance/evidence/20261028-native-shield-connected.json).
Exact source/binary locks, fixture locations, build and test logs are in
artifacts/player-replacement/run220/final.json and fixtures.json.

## Sponsor checkout

Run tools/d3d9_proof/start_d3d9_shield_replacement_session.ps1 from the usual
administrator PowerShell. Use your F-CA against a different model. Begin still,
let the enemy hit your shields, rotate/move, switch cameras away and back, then
play briefly. Look for one player ship, shields visibly covering the front of it,
solid registry lettering and normal controls/HUD. Exit normally when requested.
The tactical window remains90seconds and total workflow285seconds. No offset,
magenta, appearance tuning or repeated on/off sequence.

Review native draw/admission counters, output pairing/recovery, original-hook
restoration, normal semantic unload and unchanged files with sponsor observations.
Only then consider other foreground families or broader replacement. Existing
separate tuning/additive receipts were not renewed; do not claim this checkout
qualifies every historical launcher.

## API basis

- [Microsoft IsSampleFrequencyShader](https://learn.microsoft.com/en-us/windows/win32/api/d3d11shader/nf-d3d11shader-id3d11shaderreflection-issamplefrequencyshader)
- [Microsoft OMSetBlendState sample mask](https://learn.microsoft.com/en-us/windows/win32/api/d3d11/nf-d3d11-id3d11devicecontext-omsetblendstate)
- [Microsoft D3DDisassemble](https://learn.microsoft.com/en-us/windows/win32/api/d3dcompiler/nf-d3dcompiler-d3ddisassemble)
- [Microsoft device private data](https://learn.microsoft.com/en-us/windows/win32/api/d3d11/nf-d3d11-id3d11device-setprivatedata)
- [ReShade native pixel-shader creation callback](https://github.com/crosire/reshade/blob/main/source/d3d11/d3d11_device.cpp)

Bundled ReShade SDK init_pipeline signature/event contract was inspected locally;
upstream source is supporting explanation, not permission to change dependency.

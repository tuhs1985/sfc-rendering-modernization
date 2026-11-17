# Implementation tasks

## 1. Establish the current boundary

- [x] Branch from merged alpha `e450c30` and reconcile the family inventory with current ship, debris, damage and light implementation.
- [x] Record the exact fields an independent reader can recover from existing intact-ship and break fixtures. Identify raw values, adapter derivations and any missing source metadata.

## 2. Prove independent consumption

- [x] Reuse the current decoder and scene representation to expose an offline consumer view. Preserve original geometry, corner data, resource bindings, damage state and camera/instance identity.
- [ ] Demonstrate the view with a consumer that uses neither Remix nor D3D9. Check frame pairing, shared assets, offscreen transforms, retirement, missing capability and incomplete inputs.
- [ ] Verify that the existing D3D9/Remix path still consumes the same source state and that the tested alpha remains available for external testing.

## 3. Expand one observed rendering family

- [x] Qualify a single `fx0.bmp` quad path from archived evidence. If necessary, prepare one bounded observation for the missing producer, resource revision, state or order join.
  - The copied-game retry proved exact batch membership, texture binding, native state and engine presentation for one main quad. The offline reader verified those fields. Native texture orientation and pixel comparison remain open.
- [ ] Expose the verified transient draw with explicit frame provenance and a bounded lifetime. Exercise offline replay, slow consumption and native retention for incomplete observations.
  - Standalone x86/x64 fixtures admit the saved draw beside a synthetic retained frame through the production retained-frame reader. Real engine Present-to-source-frame association and live publication remain open. Pixel replay is deferred for this interface-only increment.
  - The exact same-run join verifier now passes x86/x64 fixtures. Collect the publisher, flush and Present stamps in a single capture-only game session for live qualification.
  - The isolated producer and `-Join` launcher now pass the injected shared-mapping fixture and copied-game preflight. One copied-game drone capture is pending.
  - The combined live run verified the retained-frame receipt and clean teardown. The missing texture filename reproduced in a forced-stop fixture. The final resource drain and independent receipt checks passed offline. One focused live capture needs both parts together.
  - The final copied-game checkout verified the exact retained frame, named texture binding and indexed draw together. Production transient publication and backend replay remain open.
  - Standalone D3D9 replay passed both captured main-quad samples with an independent sampling check, blend and depth controls. Native pixel parity and Remix submission remain open.
- [ ] Document what an independent consumer receives and verify the remaining pixel and ordering questions. Use a standalone Remix submission only if needed to validate the pipeline. Live Remix effect integration is deferred.
- [ ] Record remaining family coverage and the smallest next increment. Keep UE5 render/output qualification separate.

# Design and implementation plan

Use UE 5.8.4, changelist 58902052, installed externally. Keep authored project
source under `src/ue5_proof`. Stage and build a local project under
`artifacts/ue5-proof` so generated assets, captures and engine output stay local.
Execute this approved proof inline.

1. Add a preparation command in `tools/ue5_proof` that calls the existing
   independent reader, resolves original primary images, verifies their hashes,
   and writes the checked source view and top-row-first BGRA outside Git.
2. Create a runtime UE module with a game mode and procedural mesh actor.
   Preserve one vertex per source corner and one material section per group.
   Evaluate captured model and view using column-vector arithmetic, then map
   camera-space coordinates to UE forward/right/up as `(-z,x,y)`. Use the
   captured projection with explicit reversed-depth conversion for scene
   capture. Preserve source UVs. Disable temporal effects for the first
   reference. Display the capture in its tactical viewport using Slate.
3. Use an editor commandlet to generate the unlit source-texture material and
   empty proof map. Compile and cook with Epic's installed build tools. Keep
   the runtime consumer independent of editor modules in a packaged build.
4. Run the packaged executable against the Bird-of-Prey. Save one bounded
   screenshot and source/mesh/texture receipt. Compare projected landmarks,
   texture placement and material sections with the retained independent
   reference. Use a second, explicitly selected captured pose when available.
   State any missing visual or process qualification accurately.
5. Update the interface document, run record, handoff, repository status and
   dated Obsidian entry, and refresh the restart brief. Read back documentation.

The initial image uses original primary colour and diagnostic unlit material.
Lighting, damage, debris motion, live IPC, native SFC insertion and final
wrapper acceptance have separate qualification. The alpha package stays at
its accepted path. No engine or game assets are added to Git.

## Post-proof review — November 18

The sponsor requested a documented review before live integration. Findings,
Epic references and proposed qualification gates are in
`docs/reconnaissance/2026-11-18-ue-integration-review.md`.
The static proof remains its validated baseline. Camera-baked geometry,
GameMode ownership, section duplication, assertion-dependent I/O and diagnostic
readback must not be extended unchanged into a live wrapper. Next scope the
packaged world-space replay foundation as a separate implementation change.
This review adds no runtime behavior or authorization to wire live input.

# Run294 — Untimed three-mission review

Date:2026-11-04. Evidence:
`artifacts/remix-runtime/runs/20261104-060904-042345-in-game`.
Sponsor:stable across3missions,one observed ship rendering dropout;intermittent
grayish flat KFF wing surfaces,described as if something were overlaid.

## Observed execution

| Counter | Result |
| --- | --- |
| Workflow |1265.078seconds(~21minutes)|
| Fresh asset revisions |8qualified/8attempted;0partial/rejected|
| Reusable geometry |4loads,4shared;KFF/FFF/MSG/PCA filenames observed|
| Renderer |63027frames,123704ship draws;9omitted instance submissions|
| Native insertions |113481;132256suppressed list submissions|
| Gate |12misses,1355stale rejections;0invalid/partial/terminal errors|
| Per-owner unavailable |4,all owner21/KFF revision8|
| Damage |20220draws;0unqualified;9shared textures/2359296GPU bytes|
| GPU job |exit0,stop_reason0,remaining owned processes0|
| Receiver |63028frames,result0|
| Original installation/launcher |unchanged|
| Copied proxy |restored|
| Storage |124319681bytes overall;116743966GPU scratch peak|
| Console |234691bytes,no discarded bytes|

Counts have different scopes:one rendered scene can cover multiple owners and
one owner can submit primary/secondary lists. Do not divide insertions by source
requests as an FPS measurement. Stale-output rejection and unavailable counts do
not establish when or how long a visible fallback/dropout occurred. Minimal play
mode intentionally has no continuous timeline or screenshots. No timestamp can
be reconstructed for the sponsor's one event from these counters alone.

Preparation_seconds44.344is wall time from early preparation,including menu/game
entry;it is not a measured44-second first-asset conversion stall.

## Final result classification

Overall supervisor result is PARTIAL with `Copied critical baseline not fully
restored`. Comparison identifies only `sfc.ini` changed;the current accepted/test
INI diff is PlayerName. Do not copy actual preference values into public records.
The game saved a preference in its copied installation;original remained unchanged.
This is separate from renderer/capture/GPU cleanup failure. Preserve the user's
preference;no config rollback or verifier relaxation was performed in this review.
Normal process exit reclaims game-side hooks;controller exit8is not evidence of
controlled live unload. Renderer,receiver and owned job exited cleanly.

## Gray KFF wing finding

Both KFF observations resolve the same five original image pairs. No asset
rejection,unqualified damage state or terminal renderer error was logged.
Current material profile includes metallic0.4,generated roughness enabled and
denoising enabled. These are observations,not proof that any setting caused it.

Two candidate families remain:

1. Damage decal material blending/placement changing the apparent hull surface.
   Damage draws use a separate coplanar mesh submitted as a Remix decal;opaque
   hull depth is preserved. Source-state agreement does not prove every rendered
   material/placement on every flat surface is visually correct.
2. Broad view-dependent specular response on flat wings under the current
   roughness/metallic/light profile. Would tend to change with camera/light angle.

No image or per-frame material-state capture exists to separate them. Optional
sponsor recollection requested:after damage,or dependent on camera angle? If a
future comparison is needed,first use the same ship/settings with
`-NoDamageTextures`;do not start a broad trace or change several material controls
at once. No extra run is required by this review while recollection is pending.

## Outcome and next action

Multi-mission live play demonstrated under this tested setup,with one reported
dropout and unresolved gray-wing appearance. No universal campaign/model or
perfect-continuity claim. Preserve the current profile and evidence. Choose the
smallest visual comparison once gray-wing behavior is clarified;no rendering
code or settings changed. Changes remain unstaged and uncommitted.

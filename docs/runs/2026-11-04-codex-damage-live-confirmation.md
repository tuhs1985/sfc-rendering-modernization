# Run290 — damage blending visually confirmed

Sponsor ran two corrected damage checkouts and confirms first-use transparency is fixed. Reports improved blending and progression between damage stages. This supports the Run289 blend-state correction;do not claim individual attribution of every previously reported occasional glitch.

| Run | Models | Renderer frames | Hull draws | Damage draws | Unqualified damage | Rejected assets |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
|20261104-051513-742661-in-game|KDD,FCA|5185|10369|733|0|0|
|20261104-051734-716326-in-game|KDD,FCA|4247|8367|1699|0|0|

Both runs:error absent,normal game exit,original client/launcher settings unchanged,copied critical hashes restored,proxy restored. Receiver/host owned jobs exit0,stop_reason0,remaining_owned_processes0. Native gate timeouts/stale/invalid/dropped0;no terminal recovery condition. Current damage source is agreeing with native model arguments in these tested paths.

Overall supervisor result remains PARTIAL because normal process-exit reclamation does not produce PERSISTENT-SCENE-001.json or a clean in-process hook-unload receipt(controller8). Both observations finished the requested window and final reporting completed. This existing final-report/cleanup distinction is separate from a damage rendering failure;do not relabel entire runs PASS or change validation rules during a visual review.

Damage uses SFC's discrete current tiers and blends the selected decal over the original hull material. No invented temporal crossfade between tiers was implemented. Sponsor's smoother-transition report is visual evidence of the resulting material blend,not proof of continuous SFC damage interpolation. Damage reversal/removal is implemented and offline GPU-proven;live repairs were not separately confirmed in this message. Standard family demonstrated;starbase/organic and universal model coverage remain unqualified.

Outcome:DAMAGE LAYER / FIRST-USE TRANSPARENCY FIX VISUALLY CONFIRMED in tested KDD/FCA skirmishes. Existing geometry/UVs/original images,lighting/material settings unchanged. No new test campaign or code/config changes. Damage still opt-in;no alpha release/milestone completion claim. Diagnostic inventory stays in DIAGNOSTICS.md. Next alpha implementation item is fresh break-model/destruction support,after sponsor direction. Track process-exit summary limitation separately;do not let a missing post-exit summary masquerade as a rejected damage render.

No commit/push authorized. Local compact review:`artifacts/player-replacement/run290/review.json`.

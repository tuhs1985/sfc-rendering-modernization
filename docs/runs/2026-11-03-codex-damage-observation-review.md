# Run284 — real damage layer captured through all three severities

Sponsor completed the prepared observation. Actual run:
`artifacts/remix-runtime/runs/damage-20261104-031410-704610` (UTC directory;
November3local). Read-only analysis; no renderer/settings/game edits or new run.

## Observation result

`DAMAGE_LAYER_OBSERVED`, no decoder issues. Normal copied game exit, host0,
accepted/copied client and launcher settings unchanged. Observer reports206
retained records, zero drops, zero queued, zero faults/busy/uncertain/capacity
omissions. All ten hook entry bytes restored; active callbacks0, hooks remaining0.
The90second tactical window finished normally (gate to observer end90.061s).
Sponsor visual/gameplay behaviour beyond completing the run was not separately
confirmed; do not infer it from successful cleanup.

Metadata105,600bytes plus one755,484byte secondary mapping. Entire run folder
1,144,291bytes, including logs, DLL, manifest, inventory and result. No image dumps,
second mapping or diagnostic cap hit. Six owner births in the startup/lifecycle
trace are not six observed tactical ships: qualified model states are F-CA/KFF.

## Damage selection and original images

F-CA's selector begins0, rises through0.05833/0.075, then activates the secondary
layer at the first observed0.14166665. Later selections progress through all three
original image pairs. Times below are seconds after the automatic tactical gate,
not exact gameplay health percentages or a measurement of every boundary.

| First recorded stage | Time | Selector | Primary / companion IDs | Original files |
| --- | ---: | ---: | --- | --- |
| Light |25.076|0.14166665|8 /11|`light damage.bmp`, `light damage si.bmp`|
| Medium |42.871|0.375|9 /12|`medium damage.bmp`, `medium damage si.bmp`|
| Heavy |53.788|0.70833337|10 /13|`heavy damage.bmp`, `heavy damage si.bmp`|

Nineteen changed secondary-pass records retain their contemporaneous scalar and
selected pair. All use family0, flags0x23, white packed colour, scalar fields0.3,
1and0. The actual18entry runtime table resolves each pair uniquely to the Run282
pinned filename/slot inventory. IDs are specific to this process. Four opaque
manager words remain `[1,5,1,0x3F800000]`; they are not asserted D3D blend factors.

KFF's observed selector reaches only0.025641; no secondary submission is retained
for it. This is consistent with the qualified severity-selection code, not a
missing damage-layer capture. Starbase/organic families are not runtime-qualified
by this two-ship run. The scalar mostly increases but has one decrease from0.78333
to0.775; do not assume strict monotonicity or substitute a timer for native state.

## Mapping, geometry and first-use order

Captured F-CA damage mapping:3,493positions,6,370triangles,19,110corners, one material
group. SHA256 `9C0A6C9DE9303E2C1C2AB23AF036512B9830D282B95AA48F9BE31EEA7E589F4E`.
Portable mapping checksum, counts, indices and finite values pass.

Compared with the previously fresh-captured F-CA packet from
`20261103-041835-978830-in-game/gate/LIVE-SCENE-001-asset-2.bin`:

- All position bytes match, all6,370polygon counts and face normals match, and
  all19,110corner indices/normals match.
- All19,110corner UV pairs differ. Damage really uses a separate mapping; applying
  these images with ordinary diffuse UVs would be wrong.
- Every secondary polygon uses material group0.33opaque polygon word5values differ
  across the two historical captures; their semantics are unqualified. This is
  not a position/normal/topology discrepancy or authority to repair those words.

Only one damage list/mapping was created despite later severity/image changes.
There is no model/asset-epoch change between damage tiers. This supports caching
the mapping once and updating per-owner damage selection independently of hull
geometry and other owners.

The first damaged invocation, token3009, directly confirms lazy construction:

1. Model entry25.0733609s: secondary pointer0.
2. Primary wrapper25.0733750s: original hull submission.
3. Secondary wrapper25.0764057s: new secondary list, selected light pair.
4. Mapping snapshot receipt25.0771011s, unchanged native UVs.
5. Model-return observation25.0787391s: secondary pointer now populated.

The first secondary call occurs about3.031ms after the primary hook; that interval
includes original native work and instrumentation and is not a pure builder
benchmark. It confirms that the current early primary insertion cannot consume
an actual secondary snapshot first available later in the same invocation.

## Consequences for implementation

We have sufficient fresh evidence for standard F-CA selection, all three image
pairs and actual secondary mapping. Another unchanged observation run is not
needed for these relationships. Pure black transparency remains sponsor-established
for damage; intact hull black must remain solid.

The smallest next work is an adapter-side damage layer with separately cached
mapping, per-owner selector/family state and original image associations. Preserve
first-use preparation/source-frame ordering: either qualify equivalent mapping
preparation before primary insertion from the pinned native algorithm, or handle
the first unprepared damage invocation explicitly. Do not pretend a later snapshot
was available earlier or rebuild the whole hull on each hit.

Exact native companion contribution and alpha/blend/filter arithmetic remain to
finish from the pinned code and existing state path. The observation's opaque
manager fields do not establish them. These are narrower offline implementation
questions, not grounds for a new broad capture or an invented opacity formula.
Damage rendering through Remix is still unimplemented; no alpha-release closure.

Local ignored analysis: `artifacts/player-replacement/run284/damage-review.json`
and `geometry-comparison.json`. Original packets and images remain untouched.
No builds, gameplay launches, staging, commit or push during analysis.

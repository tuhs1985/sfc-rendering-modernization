# Secondary image — narrow role adjudication

## Newest disposition — eligibility captured; preview reviewed

Component0.17 run20261016-171830-enabled records validation mask3/previous
alpha-test0 with secondary word511/multitexture0/textures1. Runtime inputs plus
static branch select mode2 then1 requests; the historical missing-input blocker
below is closed, not a directly observed GPU pass-count claim.
[Offline material review](2026-10-16-preview-material-mapping-review.md) verifies
all ten input image hashes/group mapping and product term against the existing
preview. Modern emission remains an approximation: legacy clamps secondary+vertex
lighting before primary multiplication, unlike additive modern lighting/emission.
No automatic brightness/convention change; fidelity PARTIAL. No new gameplay
needed for branch settings; next useful comparison is matched ordinary views.

## Historical runtime result — fallback selected, eligibility then pending

[Fresh0.16 review](2026-10-16-texture-path-runtime-result.md) observed +3D58=511,
+8009=0 on selected kff snapshot: NOT combined multi-texture mode0; fallback
family selected. Conditional fallback code can produce the same primary-weighted
secondary term through two passes, but +800C validation mask/+3F54 previous state
were unobserved, so exact active pass sequence is not confirmed. Static intended
role remains supported; provisional preview is not automatically promoted.0.17
read-only extension prepared/offline validated, not run. Earlier statements that
both initial predicates are missing are now historical, not current.

## Newer sponsor disposition / provisional preview

Sponsor explicitly authorized code-informed offline implementation before game
verification ("Do what the code suggests. We can verify later"). A separate
[provisional preview](../runs/2026-10-16-codex-provisional-lighting-preview.md)
now demonstrates primary*secondary image products as assumed-intensity1 emission
on the five matching saved groups. This supersedes the earlier **implementation
hold only**, not the missing runtime evidence or confidence classification below.
Original clamping/color space/strength/active branch remain unverified; overall
recovery PARTIAL. Neither raw secondary-as-glow nor SFC fidelity is claimed.

2026-10-16; approved offline texture recovery. No glow enabled by this analysis.
Confidence labels refer separately to static intent and observed runtime use.

## CONFIRMED static relationship

Exact client SHA256
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
Source: `artifacts/pre-m0/raw/StarFleetOP-2.5.6.4.dumpbin-disasm.txt`;
fifteen selected instruction/vtable anchors checked independently against original
PE bytes (run record below). No new decompiler labels treated as evidence.

1.006AC0E2/F2 selects primary source+14 and secondary source+1C (flag20).
2.Wrapper006AC5D8 first tests feature bit20 from manager vtable+24
  (007B8D70 ->0069D3B0).0069D3B0–3C4 sets that bit iff manager+3D58 DWORD
  is nonzero. If zero, wrapper selects mode1 and skips the later predicate.
  Otherwise006AC612 uses manager vtable+D0 at007B8E1C ->0069F260, returning
  manager+8009. Nonzero selects preparation mode0 at006AC62D–631; zero uses
  the existing single-texture/fallback branches, not an equivalent assumed path.
3.Mode0 at006AC522–53A sends primary and secondary to006AB410.006AB467/485
  and006A8860 bind primary at texture stage1 and secondary at stage0 when
  +8009 is nonzero. Null IDs/disabled textures still have their established gates.
4.Initialization0069D9A9–DA47 programs Device3 vtable+A0 as follows:

| Stage | COLORARG1 | COLORARG2 | COLOROP |
| --- | --- | --- | --- |
|0|TEXTURE(2), secondary|DIFFUSE(0), interpolated vertex color|ADD(7)|
|1|TEXTURE(2), primary|CURRENT(1), previous-stage result|MODULATE(4)|

Installed Windows SDK10.0.26100.0 `um/d3d.h` method order corroborates Device3
SetTextureStageState+A0 and SetTexture+98; `um/d3dtypes.h` corroborates enums.
Also [Microsoft texture operations](https://learn.microsoft.com/en-us/windows/win32/direct3d9/d3dtextureop)
and [argument selectors](https://learn.microsoft.com/en-us/windows/win32/direct3d9/d3dta).
The later API documentation is enum/formula corroboration, not evidence the game
uses D3D9 or that an initialization call succeeded.

For that configured multi-texture path the intended RGB operation is:

`C = primary * clamp(secondary + vertex_lighting)`

This places the secondary **before** multiplication by the primary. In an
unsaturated algebraic decomposition the unlit contribution is primary*secondary,
not simply the secondary bitmap. Intermediate clamping matters. Color space,
physical emission strength, bloom and a modern renderer's lighting are not
established by this equation. Do not silently turn this into a faithful PBR claim.

## What existing runtime evidence does / does not prove

Accepted run20261016-010112-enabled proves same-epoch group/resource/file identity,
source flags35 on all five groups and textures_enabled1. The ten original images
are already recovered exactly. Secondary `kff_1_2i.bmp` is predominantly black with
localized bright marks (analyst viewed original); this is consistent with an
illumination mask, but file appearance/suffix is not its role proof.

ModelBrowser emissive toggle corroborates visible unlit markings in that program,
not the SFC runtime combiner. Old TEXTURE-EXPORT-001.json did **not** record +8009;
wrapper samples also do not contain either branch input (+3D58 or +8009).
Therefore active multi-texture branch for
that capture remains UNOBSERVED; do not relabel it as confirmed or reuse old live
resource IDs for a new process. No API-state readback has been performed.

## Smallest unresolved fact / prepared observation

Fresh selected-mesh snapshot must record manager+8009 AND manager+3D58 alongside
its own resources, and verify neither changed during observation. Both nonzero
are required to infer mode0; one flag alone cannot do so. Prepared collector0.16 adds
these five bytes/read-recheck and optional JSON provenance; default-off reference capture
and all established bounds/ABI remain. Missing historical field stays null/unknown,
zero remains zero; no automatic emission permission. Tests cover unreadability,
mutation, zero/nonzero and no native writes.

Follow [TEXTURE-EXPORT-001](probes/TEXTURE-EXPORT-001.md) unchanged90s two-ship
runner. This is the actual remaining gameplay dependency, not another softness,
geometry, texture-dump or visual-modification test. Appearance remains normal.
After evidence arrives, adjudicate the selected branch; investigate only a concrete
remaining state ambiguity if necessary. At this historical preparation checkpoint
no offline glow derivative existed; the newer sponsor-authorized provisional
implementation above supersedes that hold without changing runtime evidence.

[Preparation/run record](../runs/2026-10-16-codex-secondary-role-preparation.md).

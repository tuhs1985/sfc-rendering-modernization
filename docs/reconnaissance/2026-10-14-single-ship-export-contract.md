---
date: 2026-10-14
status: analysis-complete-export-not-implemented
scope: one-owner-selected-primary-mesh
---

# One-ship export — smallest complete mesh contract

Preparation update: [MESH-EXPORT-001](probes/MESH-EXPORT-001.md) implements this
bounded read-only packet in component 0.14 with offline tests. Gameplay export
remains unexecuted. The proposal/analysis below is retained as its design basis;
actual schema, measured synthetic storage/output and launch policy are in the
probe definition. No renderer integration or texture/camera qualification yet.

## Decision

Start with a **read-only, complete primary mesh from one selected ship owner at
one selected LOD**, not another tint or camera-motion experiment. Preserve SFC's
original rendering. This document defines the input qualification; it does not
implement or arm a capture, choose a renderer, or change milestone gates.

The existing seam provides a credible acquisition point. No complete portable
mesh packet exists yet. The previous whole-small-mesh copy is not that packet:
it preserves live native pointers and corner payloads for native consumption,
but does not serialize independent positions, UVs, materials and transforms.

"Complete" here means all primary polygons and their required data for the
selected Model0 invocation. It does **not** mean every LOD, secondary pass,
attachment, effect or rendered part of a physical ship. If that distinction
prevents a recognizable ship, record the missing part before expanding scope.

Authority remains the [approved M1 plan](../m1/m1-trl4-integrated-component-validation-plan.md)
and [gate amendment](../decisions/2026-10-14-m1-m2-gate-allocation-amendment.md).
This is sponsor-authorized research, not M2 implementation or a new requirement.

## Evidence examined

- [Semantic ownership map](../m0/m0-semantic-ownership-map.md): ship -> visual ->
  selected Model0 -> graphics manager; proven mainline identity and LOD association.
- [Field/transform qualification](../m1/m1-c01-corner-transform-qualification.md)
  and [numeric adjudication](../m1/evidence/M1-C01-MATH-001-20261012.md).
- [Isolated-list feasibility](../m1/m1-c01-isolated-corner-handoff-feasibility.md):
  primary/secondary routing and guarded argument-only intervention.
- [RT-010](../m1/evidence/M1-C01-RT-010-20261013-surface-lighting.md): complete
  452-polygon private primary graph, 1,356 corner vectors, intact/restored.
- Actual implementations: [corner sampler](../../tools/m1_component/m1_corner_snapshot.h),
  [private copy](../../tools/m1_component/m1_private_copy.h),
  [whole-small-graph copy](../../tools/m1_component/m1_surface_graph.h),
  [source snapshot](../../tools/m1_component/m1_visual_tint.h), and
  [component](../../tools/m1_component/m1_component.cpp).
- Existing ignored exact-build dumpbin file:
  `artifacts/pre-m0/raw/StarFleetOP-2.5.6.4.dumpbin-disasm.txt`. Only narrow
  Model0/LOD/position/source/preparation ranges were read. Reference and installed
  client hashes match; 42 existing anchors plus eight focused PE checks match.

## Available fields and their limits

All offsets below are hexadecimal; pointers/counts are native x86 values.

| Data | Exact source / corroboration | Classification and limit |
| --- | --- | --- |
| Owner tuple | Existing TLS ship/visual/Model0/manager/source, opaque epoch and thread | CONFIRMED mainline. Pointer reuse is not physical identity continuity. |
| Selected child | `0042FDB4`: visual + `160 + 4*selected`; `0042FDCB`: source +158 passed to child | CONFIRMED static and established runtime chain. Capture actual child; do not infer active LOD solely from cached +124 when override +120 may apply. |
| Position array | Model0 +8 count, +C base; `0042E517..521` passes both to manager; `006ABF92` stores base at manager +554 | CONFIRMED static/live sampled. Three 32-bit float fields per indexed position; full array not yet exported. |
| Primary polygon array | Model0 +10 count, +14 pointer list; wrapper caller return `0042E55D` | CONFIRMED static/runtime primary route. Secondary return `0042E626` uses Model0 +18 and must not be silently folded into primary geometry. |
| Polygon | +0 corner count, +4 source-group index, +8 face vector, +18 corner pointer; complete header 28 bytes | CONFIRMED access/copy. Other header bytes remain opaque. |
| Corner | 28 bytes: WORD position index +0, vector +4/+8/+C, UV candidate words +10/+14 | CONFIRMED static accesses and raw-copy layout; vector normal role corroborated. UV numeric range/orientation still unqualified. Preserve padding +2 and trailing +18 word without assigning meaning. |
| Per-corner attributes | `006AC2E6/2EC` reads +10/+14 for every corner, even after indexed-position cache hit | CONFIRMED static. Same position index can require different UVs/vectors in different polygons. Do not weld by position alone. |
| Source grouping | `006AC036/03F`: source + 36*polygon source index; manager +558 set at `006ABFB4` | CONFIRMED addressing. Existing 256-entry bound is tooling admission policy, not proven native allocation length. |
| Source contents | Flags +0, RGB bytes +4..6; +14 and conditional +1C read at `006AC0E2/0F2` | CONFIRMED accesses; resource meaning/ownership of +14/+1C UNKNOWN. Preserve as opaque words, never dereference as guessed texture pointers. |
| Transform handoff | manager +6F4 supplied / +6B0 composed, each 68 bytes; static setter `006AA550` and live/numeric evidence | CONFIRMED raw handoff, model-local interpretation STRONG HYPOTHESIS. Not an approved external world/view/projection contract or automatically a standard 4x4. |

Eight newly checked byte prefixes (read-only, not patch sites):
`006AC036=8D 0C C0`, `006AC03F=8D 1C 88`,
`006AC2E6=8B 50 10`, `006AC2EC=8B 40 14`,
`0042FDB4=8B 8C 86 60 01 00 00`, `0042FDCB=FF B6 58 01 00 00`,
`006AC0E2=8B 43 14`, `006AC0F2=8B 53 1C`.
These corroborate static instructions, not new dynamic semantic claims.

## Proposed consumer-neutral packet

1. Version, client/component identity, run/frame/thread/opaque owner epoch,
   selected ship/visual/Model0/source/manager identifiers, acquisition site and
   selected child/LOD evidence. Native addresses are provenance, not file links
   or identifiers reusable in another process/run.
2. All declared positions, raw float bits plus native index. Retain unused
   entries separately from the referenced set; only referenced geometry enters
   the completeness/finite-position test. Never invent missing positions.
3. Every primary polygon in original order: original ordinal, full header bytes,
   source-group index and complete ordered corner records. Each corner keeps its
   position index, raw vector/UV bits and opaque bytes. On-disk references use
   packet indices/offsets, not pointers requiring live process memory.
4. Referenced source-group records: full 36 bytes plus original group index.
   Record read ranges and opaque resource words, without claiming texture export.
   Avoid reading unreferenced intervening groups merely to fill a dense prefix.
5. Both raw 17-DWORD transforms, relevant existing math-dispatch identities,
   counts, hashes, validation status and omissions. Never normalize/change the
   native values in place. Any later derived normals/matrices record conversion.

No camera, light extraction, textures, GPU resources, renderer-specific objects,
live streaming or image reinsertion is needed to qualify this packet. A later
isolated shape preview can use an explicitly synthetic camera/material/light;
that would prove mesh usability, not faithful SFC scene reproduction.

## Acquisition and lifetime constraints for later implementation

- Reuse existing owner-scoped wrapper `006AC5A0`, at entry before native
  preparation, with exact primary caller `0042E55D`, manager/thread/Model0/list/
  count/source equality. Source/position setters have run at this point. Do not
  sample manager caches at Model0 entry and assume they already belong to it.
- Retain current hook architecture/ABI preservation. A future collector must be
  separately offline-tested and documented before gameplay; no new hot geometry
  hook. Unknown/unowned/secondary/reentrant calls pass through untouched.
- Copy into preallocated owned storage; no writes to native positions, lists,
  sources or corner data. Do not reuse the intervention graph as a portable file.
  End all native pointer dependence before leaving the capture scope.
- Re-read identity/count/list/positions/header/corner/source data and raw
  transforms before publishing; mismatch means discard, not a partially valid
  mesh. This detects observed change, not a universal atomic snapshot guarantee.
  Bound work; no waiting/retry loop on the render thread.
- Target one immutable owner epoch. Record retirement; do not retarget through
  recycled pointer values. Store transform changes separately in a future task,
  not repeated copies of the whole mesh each frame.

## Offline acceptance checks for that future collector/analyzer

- All declared primary polygons copied, zero omitted/truncated corners; every
  index in range. All referenced positions, vectors and UVs finite. Report zero
  vectors, non-unit lengths and degenerate triangles; never silently repair them.
- Preserve original ordered corners and source membership. Initially qualify
  triangles only for renderer-ready output. Preserve 4..8-corner polygons raw but
  report topology qualification required; no unproven triangle-fan conversion.
  Count outside the admitted range rejects the packet without truncation.
- Expand corners into separate render vertices initially; an offline derived
  triangle list may use sequential indices. Preserve native position provenance.
  Deduplication is unnecessary and could erase UV/normal seams.
- Report bounding box, referenced/unused positions, polygon/corner histogram,
  source-group membership, UV ranges, normal magnitudes and geometric face/vector
  alignment. Do not clamp UVs to 0..1: wrapping may be intentional. Do not infer
  winding/handedness solely from normal sign or force a consumer convention.
- Round-trip serialization independently, with no SFC pointer dereferences.
  Unit fixtures must cover split UV/vector corners, boundary indices, invalid
  reads/overflow/nonfinite data, changed inputs, unsupported counts, size limits,
  owner mismatch/retirement and nonmutation/fail-open behavior.
- Full native primary count is necessary, not enough to claim full physical-ship
  fidelity. Record excluded secondary path/LOD/attachments explicitly. Existing
  RT-010's 452 polygons / 1,356 corners is a fixture expectation, not a hardcoded
  selection rule or guaranteed count for another run/model.

## Proposed capture envelope — not an armed probe

One selected eligible owner, one accepted full-mesh packet, at most two capture
attempts total separated by a rendered frame; no same-frame retry. Existing
automatic tactical gate; at most 90 seconds to find an eligible primary mesh.
No magenta or shading changes. Geometry hook remains disabled.

Admission ceilings: 512 polygons, 3..8 complete corners per polygon, 65,536
positions, 256 source indices under guarded reads. Worst-case raw reservation:
`65,536*12 + 512*4 + 512*28 + 512*8*28 + 256*36 + 2*68 + 16,384`
= **943,240 bytes**, below 1 MiB. This is a calculated bound, not measured output.
Large models fail open; do not raise limits or export a prefix as complete.

Proposed packet reservation <=1 MiB; packet file hard cap 2 MiB (binary rather
than unbounded JSON expansion), separate summary <=64 KiB. Existing 16 MiB
warning/32 MiB semantic event-log hard stop remain unchanged. Whole bounded
packet serialization off the render thread, after copying to owned storage;
logging/output failure never blocks native rendering. Expected full-mesh file
under 1 MiB plus bounded existing telemetry; no per-frame mesh transcript or
multi-GB output. These are future limits requiring tests, not observed behavior.

A future probe definition must record actual tool versions, configuration,
launch/elevation, timing, outputs, analyzer, cleanup/removal and validation before
execution. Reuse validated workflow; no routine sponsor UAC/manual timestamps.
No runtime test is prepared or requested by this analysis.

## Open relationships and next action

- Full referenced UV numeric data is not in current exported snapshots; raw-copy
  preservation is not decoded/validated texture mapping.
- Source-to-texture/resource mapping and coordinate conventions remain open;
  camera/world alignment and image composition follow geometry qualification.
- A complete selected primary mesh may omit a separate native pass; observe and
  label that rather than broadening to the entire engine. Renderer bitness/
  version feasibility remains parallel research, not a selected architecture.

**Exact next action:** implement and offline-test the bounded read-only packet
collector/serializer/analyzer above, with a versioned probe definition, before
asking for a single tactical capture. This is the proposed next task, not work
performed in this analysis.

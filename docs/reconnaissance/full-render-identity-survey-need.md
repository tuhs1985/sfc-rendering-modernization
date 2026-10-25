# Full render-identity survey — recorded need

## Current bounded implementation — 2026-10-24 Run165

Sponsor now authorizes broader rendering-family characterization with bulk ship
geometry/images excluded. [RENDER-FAMILY-SURVEY-001](probes/RENDER-FAMILY-SURVEY-001.md)
and the [current family map](rendering-family-map.md) define the prepared90second
metadata-only survey. This addresses initial breadth, not a complete long-mission
survey or universal family coverage. API experiment parked; normal rendering path
unchanged. Existing20GB sponsor aggregate supersedes the historical10GB below.
Do not infer approval to remove the90second/five-minute safeguards or collect
model/image payloads. Broader/longer mission evidence remains separately bounded.

## Historical backlog definition

2026-10-20: sponsor requested a durable note for a future longer-mission survey.
Status: backlog / not implemented or scheduled. This does not replace the current
90-second shadow-timing test or authorize increasing its limits. No CDD change.

## Purpose

Inventory the rendering activity encountered throughout a representative longer
mission, including unfamiliar objects and paths, without transporting model
geometry or texture images. Establish coverage and identify the smallest targeted
captures needed next. “Full” describes the intended breadth, not a claim that any
single hook or mission observes every game category.

## Constraints for the eventual survey design

- Identity-only by default: session, owner/lifetime epoch where known, model/LOD/
  source/resource identity, resolved names where safely available, rendering-path
  identifiers, first/last observation, transitions and aggregate submission counts.
  No vertex/index/normal/UV payloads, image decoding/dumps or repeated asset copies.
- Native pointers and small resource IDs are process-local opaque labels, not
  persistent asset keys or proven semantic names. Track reuse and retirement;
  preserve unresolved associations explicitly. Use durable names/content identity
  only where independently supported; do not add full asset reads just to name them.
- Inventory broader bounded rendering anchors as well as the known semantic path.
  Preserve unassociated activity instead of filtering it out. State the observed
  coverage denominator and gaps; downstream submissions are not automatically
  distinct objects. No blanket “everything captured” claim.
- Summarize repeat observations with counters/time windows; retain bounded novelty
  and lifecycle records. Unknown categories must remain visible in summaries.
  Fixed-capacity identity tables, queues and logs; explicit duration/event/byte
  ceilings, warning thresholds, overflow/drop counters and safe stop are required.
  Saturation must be reported as incomplete coverage, never silently discarded.
- No allocation, file access, image work or waits on rendering callbacks. Worker
  drains must not delay SFC. Avoid the known stuttering diagnostic geometry hook;
  qualify any necessary broader observer offline before gameplay.
- Choose and document a longer duration and storage reservation separately before
  execution; retain the existing10GB aggregate ceiling unless explicitly changed.
  Do not simply remove current90s/five-minute runner safeguards. No unbounded
  full-rate transcript, continuous screenshots or multi-gigabyte geometry flood.
- Preserve original rendering, client hashes, hook restoration, normal exit and
  current-user session isolation. Sponsor handles gameplay only, not timestamps,
  administrative prompts or reverse engineering. Archive useful evidence after
  analysis; clean only validated generated duplicates, not original evidence.
- Report CONFIRMED observations separately from inferred categories and unknowns.
  Coverage discovery is not replacement support, universal model coverage, or a
  milestone PASS. Investigate unknown paths narrowly rather than broad engine RE.

Expected products when separately implemented: probe/coverage definition, bounded
identity inventory and novelty list, overflow statistics, run/environment record,
coverage gaps and selected follow-up captures. No implementation in this note.

Exact next action for this backlog item: after the current shadow-timing result is
adjudicated, specify the minimum broader observation points and explicit longer-run
budgets before implementing a separate default-off survey mode.

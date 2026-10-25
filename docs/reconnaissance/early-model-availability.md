# Earlier model availability — code-qualified candidates

Run177: [actual native timing measured](../runs/2026-10-25-codex-early-model-timing-result.md).
FCA90.8858msfull load/117.4186mslead to first semantic entry; KFF13.8198ms/
13.8709mslead. Clean named joins/normal gameplay/cleanup/hashes. This resolves the
initial timing question but not the downstream multi-second delay; no early mesh
copy or renderer change. Next focus is retained-scene first-correct-output/material
delivery, not another native discovery run. Earlier Run174/175 text below is
historical where it says timing is unmeasured or another sponsor run is needed.

Run175 update: [metadata timing observer prepared and offline-qualified](../runs/2026-10-25-codex-early-model-timing-observer.md).
No SFC run yet; static conclusions/unknown actual lead time below unchanged.
Next is the prepared sponsor measurement, not early geometry capture.

Newest:2026-10-25 Run174. Sponsor redirected the next investigation from effects
to earlier model delivery. **Confirmed static path; contemporary timing and safe
runtime capture remain unqualified.** API remains parked. No game launched,
loading intercepted, assets exported, backend changed or performance gate passed.

[Run and validation](../runs/2026-10-25-codex-early-model-availability.md),
[versionable evidence](evidence/20261025-early-model-availability.json),
[bounded follow-up definition](probes/EARLY-MODEL-AVAILABILITY-001.md).

## Result in plain language

We need not wait for a ship to become visible to learn its model name. The
examined ship-creation path already has that name, asks a shared cache for the
model, loads missing geometry and requests its textures, then attaches the result
to the ship. This supplies concrete earlier observation candidates, not a measured
startup improvement. A complete mission roster during ship selection is NOT proved.

The useful distinction is **name known → native model prepared → ship attached →
first visible draw**. Our current capture chiefly starts at the last stage.
Native preparation is not the same thing as Remix upload/shader/material readiness.

## CONFIRMED static relationships

All addresses refer to the pinned2.5.6.4client; offsets are hexadecimal. The
verifier checks49specific anchors,5vtable entries,2196instructions in explicit
ranges and52direct calls to the common visual factory. This is not an engine-wide
roster enumeration or proof every caller supplies a ship.

| Stage | Code / available data | Qualification |
| --- | --- | --- |
| Ship creation | 00409793 calls established ship constructor004146A7; first input becomes ESI at004097F5 | First input is a ship-definition-like record; caller's render-create flag at+10 controls the later visual setup |
| Early model name | 0040A555 takes address of input record+38;0040A55B passes it to004156F9 | Inline name available before common factory/load; not a filename recovered by reading .mod from disk |
| Visual request | 0041574B/0041574E pass that name to0042F39A | Factory has a special yellowsun alternative; do not assume every returned visual is t3DVisual_Model |
| Common model loader | 0042F39A→004304E4→0042F51A | Candidate request/completion observation point, not a new hook yet |
| Cache hit | 0042F543 walks008F5974; virtual+10 returns visual+14 via00435632; name comparison; virtual+8 increments reference; returns same object | Model is shared by name; owner instances remain separate. No claim of content-keyed or thread-safe cache |
| Cache miss | Allocate188bytes; constructor0042F858; parser0042FEF9 at0042F5D7 | Constructor publishes to cache BEFORE parsing; pointer presence cannot be a readiness test |
| Material/string tables | Parser dispatches STRS→004301BD and MATS→004301E9, writes visual+154/+158/+15C | Native string table,36-byte source groups and count; no texture role inferred anew |
| LOD geometry | MOD0→0042F121 creates tModel0; virtual+4→0042E26B; parser stores child at visual+160+4*index | Position/polygon/corner arrays are loaded upstream of rendering; supported triangular mainline still must be checked |
| Parser success | Filename copied to visual+14;00430367 postprocessing; AL=1 at0043015B | Parser completion alone is TOO EARLY for final texture associations/optional scaling |
| Texture acquisition | Outer loader iterates groups;0042F641→0042F756 writes primary ID+14; flag20 allows secondary path0042F685→group+1C | Uses existing registry008CC620, BMP/PCX candidates and native skip rules. Requests may fail or be skipped; do not declare all textures present |
| Optional geometry scale |0042F74C virtual+38→0042FBD4→child virtual+14→0042E650 | Can replace Model0+0C position pointer, retaining originals at+20; parser-return copy can be wrong/stale for final geometry |
| Prepared candidate | Nonzero return from0042F51A, after optional scale, via success0042F74F/common epilogue | Best asset-preparation candidate; structural/lifetime/texture validation still required, not a universal ready bit |
| Owner attachment |00415757→00413A8D writes ship+88 at00413A96 | Joins shared visual to actual ship; candidate completion is before first render, not necessarily before all other startup work |
| Secondary model |0041579D requests name with _BRK.mod suffix, then0053F2D6 | Distinct broken/damage asset; do not count as another living ship or silently replace primary asset |

The constructor publishes itself into008F5974 at0042F877 before even clearing its
model/source fields, then the loader calls the parser. The loader destroys failed
parse objects. A cache walk during loading could therefore see incomplete or
doomed objects. No new cache scan/poll is recommended as the primary trigger.

The Model0 parser also has allocation-failure paths and the outer parser can
store a null child. A nonzero outer return must not bypass count/index/finite/
supported-format checks. No guessed allocation size or old resource ID reuse.

## Existing runtime evidence — useful but not a modern timing result

Re-read two original bounded M0 CSVs and verified their pinned client MD5/base,
strict sample sequences and parser return0042F5DC. Their identities/hashes are in
the evidence JSON; no original trace changed.

| Historical run | Parser entry count / first–last ms | First observed generic drawing |
| --- | --- | --- |
|20260904-100033|17 /14828–15766|Indexed draw15250ms|
|20260904-100901|16 /11391–11735|Geometry/indexed draw11563ms|

These show real parser execution on the statically examined call path. Some
parsing overlaps already-observed drawing. They do NOT identify which filename
was parsed, its successful completion, current mission start, player identity or
first visible drawing of that same asset. Their breakpoint observer changes
timing. Do not report422ms/172ms as useful preparation budgets or extrapolate a
sub-two-second result from them.

## STRONG HYPOTHESIS — integration opportunity

Observing successful model-loader completion should permit the existing asset
pipeline to start before the first visible semantic invocation. An early request
can announce a name; completion supplies the native arrays/source associations;
attachment gives owner association. Identical visuals can reuse preparation while
each owner's current simulation transform remains independent.

This can hide some preparation behind normal loading; it does not remove the
underlying cost. Measure both total preparation duration and visible delay. No
claimed two-second improvement, arbitrary enemy coverage or change to the parked
API backend follows from this investigation.

## Runtime design consequences / remaining unknowns

- Existing mesh capture expects manager state at the render seam. Earlier loader
  completion has no qualified current graphics-manager/batch context. Reuse the
  array validation/serialization logic, but separate intrinsic asset data from
  render-only provenance; never fabricate a manager or call render just to fill it.
- Do not enqueue a raw pointer then assume it remains alive for a background copy.
  Capture a bounded immutable snapshot while valid or separately prove retention,
  mutation and destruction coordination. Never call SFC loader/refcount methods
  from our worker merely because their addresses are now known.
- Cache hits, recursive loads, failed loads, texture skips, secondary _BRK models,
  LOD selection and later model changes require explicit status. Filename is an
  early hint, not sufficient asset-content identity or a living-object epoch.
- Confirm elapsed times and actual thread ordering with one metadata-only observer
  armed before loading. The tactical gate remains a timing marker; installing
  this observer at that gate would miss the events being investigated.
- Unproven: mission-roster coverage/preselection timing, remaining lifetime/ABI
  details, registry/surface readiness at completion, exact lead time on today's
  multi-ship runner, and how much preparation can overlap safely.

**Exact next action:** implement and offline-qualify the metadata-only
EARLY-MODEL-AVAILABILITY-001 observer for request, successful/failed loader return,
owner attachment and first semantic draw. No early mesh copying until that timing/
lifetime relationship is qualified; no new discovery run for these static facts.

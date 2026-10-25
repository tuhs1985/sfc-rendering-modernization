# Run169 — three actual targeted effects captures reviewed

Date2026-10-25 America/New_York. Authority: Run168/EFFECT-RESOURCE-JOIN-001;
characterization only, API parked. Sponsor supplied three runs, reported the
first ended early and increased game speed for the next two. Follow-up confirms
normal rendering/HUD/controls across all three. No implementation change or new
runtime launch in this review.

## Results

Paths below are under artifacts/remix-runtime/runs.

| Run | Tactical observation | Trace | Finding |
| --- | --- | --- | --- |
|effect-20261025-041038-445910|35.2042674s|16,777,216B /131,071records /111drops|Byte cap reached; positive concrete producer/resource/native-quad association.|
|effect-20261025-041203-910238|90.0551437s|5,888B /45records /0drops|24global-list births/19retirements; no selected concrete draw.|
|effect-20261025-041407-812374|90.0502077s|10,112B /78records /0drops|42births/34retirements; no selected concrete draw.|

**Why first stopped:** final header reason2/hard byte cap, not lack of weapons,
enemy death, inactivity or a timer shortened by game speed. Worker uses QPC wall
time and has no minimum-weapons/quiet stop. First total workflow72.343s includes
startup/menu/exit; it is not the tactical duration. Later runs ended reason1/time.

## Confirmed first-run association

-544concrete0x007AA050draw scopes, caller0x004ED080. Every retained entry has
 fresh non-late epoch and valid scalar snapshot. One selected owner pointer
273528712/epoch5, UV variant3 and branch word0x101.
-2,488resource snapshots resolve live ID1 to **assets/textures/fx0.bmp** through
 one consistent registry/object/manager-entry/surface tuple. BMP acquisition
 actually observed; no need to assume PCX fallback. Worker filename output is
 four bounded chunks, no image pixels or source model conversion.
-All122,820retained native polygon records have four corners, ID1, flags3,
 matching owner/epoch/scope/manager and qualified resource flag. Full streaming
 recheck finds zero unmatched polygon contexts. They span26.1020–35.1459s,
 approximately nine seconds, and share the freshly resolved resource identity.
-Existing parser stores at most32,768polygon examples: its qualified count32,768
 is a bounded summary, **not the actual native polygon total**.90052summary-cap
 omissions are distinct from111capture drops. Raw trace retained every record
 counted above; no parser/runtime source was changed to obtain the streaming
 counter. Finalizer mode7 counts imply122,835quads; the15difference is consistent
 with the log ending within the final batch, not proof of lost game rendering.
-Finalizers include1,402full336-corner batches plus smaller/end batches. Thus
 repetitive per-quad metadata dominates the trace:122,820of131,071records
 (~93.7%). This is the recording bottleneck, not an absence of activity.

This proves **one native effect producer/resource/primitive linkage in SFC**.
It does NOT identify its exact weapon, prove every quad's visual role, record
full object retirement, or establish a one-to-one downstream D3D11/pixel join.
The constructor's missile-model association is static evidence; shared fx0/UV3
alone is not a universal missile, explosion or shield classification.

First file ends inside an active scope and has no room for Stopped/Statistics
footer; lifetime/final aggregate coverage remains PARTIAL. Header status3/error0
and the runner's worker/file-closed handshake report successful native shutdown,
but durable footer confirmation is absent. Do not conflate the separate gate's
byte-restoration proof with an independent byte audit of the effects detours.

## What the faster runs establish

Both observed global effects-list construction/unlink without faults, busy
identity operations or identity uncertainty in final statistics. Completed
Stopped records report detach error0/active callbacks0. There were980,239 and
124,792unscoped native finalizer calls respectively. These are call counts, not
object counts, frames, missed effects or weapons. Many native finalizer calls
occurred outside the selected0x004EFA4Aproducer scope; their primitive counts
were not recorded, so these totals alone do not prove nonempty drawing.

No Enter record means the chosen concrete routine/vtable was not observed, not
that no weapons fired or effects rendered. These observations cannot identify
the other concrete classes because the probe deliberately did not capture their
vtables at dispatch. Game-speed increase is sponsor context; causation for the
different path mix is unproved. Do not widen class labels from timing alone.

## Safety / verification / scope

All three: normal game exit=true, gate_clean_unloaded=true, host exit0, accepted
and copied critical hashes unchanged, launcher settings unchanged. Gate logs
confirm detail_bound trigger, hook restoration and unload; this detail_bound is
the automatic one-event tactical gate, **not** the effects observation stop.
No presentation proxy changed. Sponsor confirms no visible/gameplay issues.

Repeated existing parser independently against all three raw files; reports
match stored result.json exactly. Full first-run streaming counter separately
checked active owner/epoch/scope/manager/resource metadata and filename chunks.
Six parser regression tests PASS; effects and normal read-only preflights PASS;
new JSON/paths and diff checks PASS. No native rebuild or runtime changes needed
for read-only review. Original captures/manifests/results preserved unchanged.
Curated data: [three-run review](../reconnaissance/evidence/20261025-three-effect-surveys.json).

## Recommended next bounded increment

1. Replace repetitive native Polygon detail with per-finalizer counters and a
   bounded sample. Retain rich owner/resource/lifecycle/selection/variant changes
   and explicit loss/cleanup footer within the existing16MiB cap. Do not merely
   raise the cap or turn the broad geometry logger back on.
2. Add a bounded scalar concrete-type/call-target census at global-list dispatch
   before the virtual call, so unselected living effect types can be named from
   actual vtables/callers rather than inferred from birth counts. Review that
   call-site ABI offline and preserve original dispatch. No geometry/image dumps.
3. Qualify these observation changes offline before requesting another run.
   Keep the currently successful producer/resource association as comparison.

No repeat unchanged sponsor run needed now. No effects renderer/interface support,
API resumption, appearance tuning, replacement or milestone completion claim.

## Repository / handoff

Run169/curated evidence added; map/probe/STATUS/HANDOFF updated and reviewed
Obsidian tracker refreshed with concurrent-edit guard. All prior dirty work kept;
HEADfd79ce5/indexempty/allunstaged/uncommitted/no push. No helper/agent/SFC/GPU
renderer started. Fuel Guard attached existing trusted hook. No active owned
channel/session. No deletion; governed output19,001,892,446bytes before small
final docs/20GBcap retained. Check reservation before further runtime work.

**Exact next action:** implement/offline-qualify the bounded native-quad sampling/
counter change plus concrete effects-type census, then prepare one targeted run.

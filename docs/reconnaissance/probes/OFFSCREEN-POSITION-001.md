# OFFSCREEN-POSITION-001 — moving ship while camera looks away

Status:OFFLINE QUALIFIED / READY FOR SPONSOR;actual SFC result pending.
Authority:2026-10-21 sponsor go following Run99evidence review. This is a bounded
read-only diagnostic to separate ship simulation from render visibility,NOT a
new renderer input,persistent lifetime implementation or formal gate claim.

## Static evidence and safe method

Exact supported clientSHA256
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
Existing ship getter00419DD2builds ship+9C4cache,reads FLOAT32translation at
ship+E6/+EA/+EE and hands it to0069C940. Previously mapped getter/base helper
00413B34,not a decompiler pointer-name assumption. Twelve exact original-PE
anchors checked by `offscreen_position.verify_client`;raw disassembly corroborates.
CONFIRMED static reads/representation;offscreen update cadence remains unknown.

Default-off external Python worker opens ONLY the path-verified copied game's
PID with `PROCESS_QUERY_LIMITED_INFORMATION|PROCESS_VM_READ`(0x1010). Retained
OS process handle cannot silently retarget to a recycled PID. No VM_WRITE,
VM_OPERATION,remote thread,process suspension,game getter or new detour. No
change to original rendering,semantic epoch policy or shared-manager lifetime.
Existing elevated parent only,no UAC/security-policy change.

Seed at most TWO distinct native ship addresses from freshly captured packets
in this unique run directory. Decode/check packet/resource associations before
using addresses;never old run pointers. Existing first8revision bound. Repeated
fresh epochs at same address are provenance labels,not proof of persistent
allocation generation. No model/image dumps beyond existing capture.

Double-read known source fields;before/after check ship vtable00796F0C,ship+88
visual link,visual vtable007985A4andModel0vtable007983E8against fresh seed. Read:

| Ship offset | Size | Meaning / treatment |
| --- | --- | --- |
| +E6 |12|three FLOAT32position values consumed by ship getter |
| +34 |12|base getter's translation input,comparison only |
| +90 |6|base raw16bit angle words,not converted to degrees |
| +92A |6|raw words covering ship getter angle inputs,intervening word unassigned |
| +980 |68|getter's additional native transform input,raw |
| +98 |68|base transform cache,raw |
| +9C4 |68|ship render transform cache,raw;translation comparison only |
| +DC |4|base getter cache stamp,not a qualified simulation clock |
| absoluteC7C140 |4twice|native shared counter used by base getter,raw only |

Seventeenth matrix word remains metadata,not a float. Stable double reads are
NOT atomic engine snapshots. Reject races/nonfinite fields;quarantine that track
on read/identity failure or changed fresh visual/model identity. Do not revive
it merely because memory later becomes readable. Same-vtable ABA/reuse between
samples remains unqualified;therefore observations never drive displayed state.
No retained manager+6F4polling:that manager is shared between ships.

## Runtime and bounds

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\d3d9_proof\start_d3d9_offscreen_position_session.ps1"
```

`-CheckOnly` qualifies source/dependencies/hashes without starting SFC. Same
Federation FCA player/different enemy two-ship fixture;keep both alive,no firing
required. Existing textured camera-left extra ship remains;no new visual effect.
After readiness,follow timed cues:

| Time/cue | Action |
| --- | --- |
|15s /one|Accelerate own ship and leave it moving. |
|25s /two HIGH|Enemy camera;own moving ship out of view. |
|40s /three HIGH|Return to own ship,keep moving. |
|50s /one|Gently turn own moving ship,prepare another look away. |
|60s /two HIGH|Enemy camera again,own ship continues moving. |
|75s /three HIGH|Return to own ship. |
|80s /one|Hold view. |
|two LOW after restoration|Exit normally. |

Startup/readiness beeps are not the timed movement cue. No manual timestamps,
assembly inspection or target identity interpretation. Don't pause or destroy
ships. Report whether own ship was moving while its camera view was elsewhere,
whether it left view,and any game/control problems.

90sformal,120smaximum reader after tactical gate,<=20Hz/ship (50ms interruptible
wait,no catch-up bursts),2700rows/ship,8MiB extra detail;counts/size retained.
Existing five-minute workflow,120ssemantic watchdog,32MiBcombined evidence,
128MiBimages,20GBaggregate remain. Capture stops/joins before controlled removal
and again in failure cleanup;process read handle closes only after joined.
No dependence on receiver mapping for worker lifetime,no new per-frame image IO.
Limits/unsupported/failed read produce PARTIAL,not fallback poses or game writes.

## Evidence and acceptance

Run103 interpretation correction: future analysis uses the captured moving
`base_position` (+34/+38/+3C) rather than additional translation (+E6/+EA/+EE)
alone. Run101's original automated PARTIAL is preserved as historical evidence;
its curated review confirms24/28/94 changing base positions inside three gaps.
No repeat discovery run is required. The new persistent path/probe is
[PERSISTENT-SCENE-001](PERSISTENT-SCENE-001.md);this external reader is not its
live renderer input.

`OFFSCREEN-POSITION-001.jsonl`:external QPC before/after,frequency,PID,native ship
address,initial observer label,stable/rejected status,position/raw comparison
fields. `offscreen-position-worker.json`:fresh seeds/epoch provenance,counts,
quarantine,error,saturation,joined/closed state. Existing lifecycle events,
source-timing QPC records,packets and normal cleanup/hash evidence retained.
Analysis goes in normal `result.json.offscreen_position`.

Require same session/PID/clock source validation. For each old epoch retirement
and captured same-address reappearance,choose conservative interior window from
first recorded source offer at/after retirement to first returning-owner offer.
Require at least3stable same-seed external samples with changing positions INSIDE
that window and zero missing-ship render-source offers there. Constant readable
position alone does NOT demonstrate continued updates;other ship movement or
cached matrix presence does not substitute. Report cache/counter variants
separately,not as automatic proof of fresh simulation data.

Positive result:`OFFSCREEN_POSITION_UPDATES_OBSERVED_NOT_LIFETIME_PROOF`,plus
ordinary game/controls,normal exit,clean restoration/hash confirmation. This
establishes offscreen position observations for this fixture only. It does NOT
prove allocation generation,safe permanent lifetime,death detection,rotation
reconstruction,whole scene coverage or synchronized replacement. Missing window,
still ship,quarantine,infrastructure/capture loss or saturation remains PARTIAL.
Do not silently change existing epoch policy based solely on this test.

Offline qualification:actual owned synthetic process at low x86addresses,
real read-only process handle,position changes while cache is held constant,
malformed/unreadable/NaN/changing/wrong identity,wrong path,worker join,byte-cap
fail-open and deterministic QPC/session joins. No synthetic fallback in SFC.

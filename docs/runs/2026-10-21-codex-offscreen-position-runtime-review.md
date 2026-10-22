# Run101 — offscreen position changes CONFIRMED;automatic field criterion wrong

2026-10-21 America/New_York. Sponsor completed new probe,reports much faster but
still blips,asks what position evidence shows. Review only,no implementation,
new gameplay,helper,agents,stage,commit or push. Fuel Guard recent-hook attached.
Read HANDOFF Run100/probe/current collector/analyzer,actual result and raw records.
HEADd29111f7a513c4510c4d33aeeda2c355d98443a5,index empty,prior dirty work retained.

Actual run directory `artifacts/remix-runtime/runs/20261022-001430-318823-in-game`
(directory timestamp retained verbatim;client-facing review date above).

## Direct evidence and corrected interpretation

3741stable external double reads,21changing-during-read rejected,1881attempts
per ship,no identity quarantine,saturation or worker error. External evidence
2,793,501bytes. Worker joined and read-only process handle closed. Source process
43260and session/clock binding validated by original analyzer. Ship fields were
read outside SFC,no native getters/writes,no diagnostic state sent to renderer.

The automatic report remains PARTIAL because its sole movement field
`position`(ship+E6/+EA/+EE) stayed[0,0,0]. Previously inspected getter00419DD2
first copies base transform from00413B34,then applies additional rotations/
matrix and that translation input. Base getter FLOAT32translation source is
ship+34/+38/+3C. Treating E6alone as total position was an erroneous hypothesis,
not missing game motion. We ALSO captured base_position and ship-local+9C4cache,
so the experiment retained the necessary evidence;no repeated run is needed.

Rejoined existing lifecycle/source QPC conservative windows exactly as analyzer,
then examined ALLthree recorded translation fields,not only E6. FCAship341994416
(0x14626BB0)has same seed visual/model checks throughout,labels2→3→4→5.

| Observer gap | Conservative window | Stable external samples | Distinct base positions / cached translations |
| --- | --- | --- | --- |
|2→3,retire2357/return2429|1202.0702ms|24|24 /24 |
|3→4,retire2556/return2641|1419.1643ms|28|28 /28 |
|4→5,retire4284/return4567|4724.883ms|94|94 /94 |

Base positions first→last in each window:

-[-280.838654,200,0]→[-278.302124,200,0].
-[-273.231995,200,0]→[-269.838409,200,0].
-[-176.716751,175.067261,0]→[-158.834122,160.934067,0].

Ship-local cached translations changed in every sample too,same first/last values.
Maximum within-sample cache/base translation differences0.036896,0,0.084344native
units respectively. Do NOT claim atomic/bit-identical base/cache snapshots:stable
external reads can catch different engine update phases. Native shared counter
also had24/28/94variants,but that alone is not movement proof. No fresh source
offers for ANYFCAepoch were recorded inside those windows. Global source invalid2
and snapshot_miss4remain recorded:absence is absence from this observed path,
not exhaustive proof of no rendering elsewhere.

CONFIRMED:ship-local base-position ANDcached-translation values change while our
selected render observation has a gap. This is direct offscreen-update evidence
for this fixture,not merely before/after displacement or readable stale memory.
Sponsor's offscreen simulation interpretation is corroborated. It does NOT
establish native allocation generation/destruction signals,whole-scene coverage,
the cause of continued cache updates or continuous GPU drawing. Do not promote
same-address continuity into arbitrary pointer-reuse safety. Renderer still uses
existing current render observations and epoch policy;this diagnostic did not
fix that design coupling. Cached full rotation requires separate qualification.

## Renderer/cleanup/result boundaries

Sponsor faster-but-blips is human visual evidence,not a quantitative latency
measurement here.3actual resident rebinds,ACK4/reject0,no light omissions,busy0/
invalid0light packets;4835draws,75stale,39expired input admissions,5pool overwrites,
1input replacement,0invalid/unqualified renderer inputs. Do not assign all blips
to one counter without event timing. No stale-hold fallback added.

Normal game/renderer exits and controlled component removal/unload NOW CONFIRMED:
controller0,`component_state=removed`,`hook_bytes_restored=true`,
`component_unloaded=true`. Original critical files and launcher settings unchanged;
copied proxy restored. Original/test client hash remains4D65761D...20C29in result.
Recorded additive preparation5.922s;selected.preparation_seconds48.375uses broader
start clock and must NOT be called48sasset conversion. Source timing invalid2/
snapshot_miss4and automated offscreen PARTIALpreserved;no overall flawless PASS,
formal TRL advancement or rewritten raw result. Vendor warning remains prior risk.

Raw whole run95,523,749bytes retained;no cleaning of evidence or original files.
Key SHA256:

-result.json:1af0b6e5d080029b464aa6a2d5fd4989765a89f687cb55ae0fd3f87942a40119
-OFFSCREEN-POSITION-001.jsonl:1174ebc712ca579cf423ec26acb5264ffb5449730a9b0b072d922d269710f4c4
-worker:d91b62288cdc6cd895c1adf6f7712a02174a72a8d330e7f042bf7ac7ba9ee323
-source timing:8cb756166633fb688076424186770791d8350d7028b69282d7f5016eda3c0b60

Reproduction:parse original source HEADER/RECORD stage1rows;for each retirement
and next same-seed captured epoch choose min source.firstQPCinside frame gap and
first returned epoch.firstQPC. Filter stable external records whose entire
qpc_before..qpc_after lies STRICTLYinside. Count distinct base_position and
cache_translation,compare first/last and Euclidean cache/base difference. Original
analyzer already retains those windows/results;do not alter it during evidence
review or silently regenerate raw run result.

Docs only:this record and HANDOFF. Read-only analysis completed,diff check PASS;
no build/tests/client launch needed for documentation review. Index remains empty,
all prior/new work unstaged/uncommitted. Exact next action:correct the experimental
pose contract/analyzer's total-position interpretation against captured base/
cache evidence,then qualify persistent lifetime and full pose consumption—not
another same-path speed-only or offscreen-position gameplay capture.

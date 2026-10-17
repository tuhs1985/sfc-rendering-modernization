# M1-C01-RT-002 — partial corner/transform runtime qualification

## Result

**M1 CONTINUES — additional bounded evidence required.** Sponsor completed the
test without noticed gameplay issues, confirmed hearing cues and performing the
requested actions. Safe read-only observation/cleanup is corroborated, but input
qualification is incomplete. No enhancement or formal TRL4 PASS.

Two specific limitations, not seam failures:

1. Owner2's mesh has6,370 polygons. The read-only helper reused the tint helper's
   whole-model4,096-polygon guard and returned status2 before sampling corners.
   This is a probe policy limitation, not malformed geometry or a game regression.
2. Owner1 provided windows0–3 only; windows4/5 missing. No sampled orientation
   basis changed for either owner. Executed turn commands do not imply actual
   angular change was captured; visibility/lifetime or response latency remains
   unresolved. Sponsor did not separately attest whether an owner left view.

## Exact run and observations

- Source baseline HEADfee152f plus documented uncommitted preparation, component0.5.
  Run `artifacts/m1/runs/20261011-234849-enabled`, PID25952; metadata start
  `2026-10-11T23:48:49.9506124-04:00`, completion `23:50:02.2515474-04:00`.
- Probe45s after automatic tactical gate; snapshots intended0–30s in six5s
  windows/two owners; actual10 records. Geometry/tint/shadingoff, no substitutions.
  Detailed CSV1,180 records/338,255 bytes, saturated at120 scene epochs; total
  2,696 gated scene epochs. No presentation-time/FPS/performance claim.
- Owner1: ship1D69C778, visual1C36E8F0, Model01D62C518, source049F365C;
  254 vertices/452 polygons, first64 sampled/192 corners per successful snapshot.
  Windows0/1/2/3 at31/5000/10000/15000ms, status0, sample_truncated true as planned.
- Owner2: ship1D6B4B68, visual1C20AB78, Model01D62C20C, source1C1CE788;
  3,493 vertices/6,370 polygons. Allsix windows returned status2 with no corners;
  header/transforms/dispatch were read before the count guard.

| Finding | Evidence | Classification |
| --- | --- | --- |
| Stable raw corner/vector/position payload for owner1 | All four successful snapshots' corner arrays match exactly | CONFIRMED sampled runtime |
| Non-unit vector lengths | range0.6761772605..1.0000000132, finite sampled vectors/positions | CONFIRMED numeric observation; do not normalize blindly |
| Source groups span multiple corner vectors | sampled groups0/1/2 contain multiple vector bit patterns | CONFIRMED sampled sharing; no whole-model generalization |
| Supplied object basis | Gram error0 for both owners' captured matrices; basis constant | CONFIRMED sampled orthonormality, not a rotation test or general inverse guarantee |
| Owner1 translation | x300→298.0755→290.09467→275.97617, y200/z0; corner data fixed | CONFIRMED sampled translation independence |
| Owner2 supplied matrix | basis and translation(-300,200,0) unchanged in allsix samples | CONFIRMED no captured object motion, despite requested commands |
| Composed position matrices | owner1 changes across successful samples; owner2 changes in later requested-turn windows | CONFIRMED raw matrix changes; camera-only interpretation not fully isolated |
| Math dispatch globals | all three0 at each sampled point | CONFIRMED snapshot values; supports scalar-path interpretation with static branches |

Normal/model-local interpretation is strengthened (STRONG HYPOTHESIS) by static
lighting-vector flow plus unchanged sampled corners under object translation/
composed matrix changes. It is **not fully CONFIRMED across object rotation**.
The corner vectors are not uniformly unit-length; averaging/color-group-as-normal
or assumed normalization would change semantics without justification.

## Cues, cleanup and bounds

Recorded requested phase tones succeeded at23:49:03.8245 /14.3838 /25.2149.
These are cue emission times, not exact native gate boundaries or action times.
Sponsor confirms hearing/doing the actions. Stationary-start clarification: own
ship at rest during observation/camera; accelerate/turn at third cue. AI may move.
No manual timestamps used. Actual geometry evidence still decides captured motion.

Controller removed component, hook_bytes_restored=true; component summary agrees.
Zero rejected semantics/owner/thread overflows; zero interventions/live leases.
Known00509843 count2,700 vs2,696 gated epochs, finite/unassigned/unmodified.
Runner normal exit outcome=exited; no remaining game/controller observed.
Installed/reference client SHA256 both
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`;
MD5 recorded`2BE8F713F81B1C68D50EAD6088C32886`; game proxy/config absent.

DLL SHA256 `9C1489ED704DB458D3BE62F83939A951EF5DBA9F2C17F73309700B87C79AFD19`;
controller `DD345763785C15B28C03F4199801DD3E30F8488980FC92DBE20F35E18AF1822F`.
Packet75,949 bytes, analysis7,949; total15 files444,700 bytes. Verified archive
`artifacts/m1/archives/M1-C01-RT-002-20261011-234849.zip`,24,571 bytes, SHA256
`4D23C96932E8CC1A2FC88140438F942C78026608BD299FA7B4801DE6FF0A98DB`.
All15 archived files hash-match originals; small raw retained/ignored. No deletion
or multi-GB capture. General analyzer PARTIAL expected, no fresh downstream proof.

## Exact next action

Prepare a narrowly revised read-only definition/helper: decouple advertised total
polygon count from the fixed64-polygon read budget (do not weaken the tint guard),
and put later snapshots after the turn command has had time to take effect while
keeping ships in view. Preserve12 records/two owners/64×8 sampling/1MiB packet
and bounded runtime. No automatic limit increase, guessed normals or enhancement.
No implementation revision or repeat gameplay executed during this adjudication.

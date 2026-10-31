# Run217 — shield boundary and historical translated state characterized

2026-10-27 America/New_York. Sponsor authorizes next boundary investigation.
No SFC launch, hooks, renderer/settings changes, native builds or GPU tests.
Run215 implementation/qualifications stay intact; Run216 gameplay remains latest.

[Evidence](../reconnaissance/evidence/20261027-shield-native-boundary.json),
[next interface increment](../reconnaissance/native-foreground-preservation.md).

## Results

Pinned-client byte checks establish mainline visual call0x0041655A from owner+88,
then helper0x004103E2, then conditional shield state owner+1BC and direct
0x004165AA->0x00426563, returning0x004165AF. Shield function ends ret4 at
0x00426883. No undocumented role assigned to the intervening helper.
This is per-ship drawing, not proof of one global transparent pass.

The exact caller return, not only addresses inside the shield callee, supplies
the historical translated join. Initial callee-only search found no matches;
that negative result is superseded, not evidence that shields were absent.

| Existing Run172 capture | Context-matched sampled draws | Additive ONE/ONE, depth test ON/write OFF | Other flush state | Qualified contexts followed by opaque work before Present |
| --- | ---: | ---: | ---: | ---: |
| Federation141338 | 98 | 97 | 1 | 15 |
| Romulan141645 | 206 | 206 | 0 | 71 |

These are sampled flush/call CONTEXTS, not303exclusive shield batches, objects,
shots or full invocation counts. One Federation sample has no depth/blend and
is retained as an outlier. State lifecycle is reconstructed with the existing
analyzer's pipeline/dynamic-state rules. Exact parent draw sequences come from
the original stack records; the second pass checks order in the SAME command
context/device before its Present. Up to41/18later opaque depth-writing draws
occur in the respective captures. Do not claim all such work is another ship;
its precise owner remains unclassified. It does disprove a universal final
opaque draw preceding all shield work.

Both archived traces were streamed in1MiBblocks without extraction,geometry or
texture export. Full hashes match the accepted reviews: Federation
05B44A3801BC90A030C727F2043B2D95EF4E7CD4E45C104C849A558A9480A75C;
Romulan881982CE5E5333B25A6F9CC6548481E91D27926D915F4A3B56B8FD91DF6CB1F4.
Original bytes/reports unchanged. Small scripts and derived matched-sequence/
state/order records are under artifacts/player-replacement/run217.

## Adjudication

Historical shield drawing context and effective additive/no-write state are now
CONFIRMED together with the static resource/state route. This strengthens
Run216's cause assessment. Latest-run pixel provenance remains sponsor observation
plus same-client path, not a new live shield capture. Native resource IDs and
translated texture labels are not silently declared equivalent. Shared batch
ownership, mutable draw buffers and replayable resource lifetime remain to qualify.

Current late opaque paste occurs after shield colour is already flattened into
native RGB, and depth lacks that additive contribution. Correct physical hull
depth alone cannot preserve it. A focused arithmetic counterexample demonstrates
that clipped additive colour is not generally recoverable from final RGB/depth.

The next bounded implementation is native foreground preservation for the SAME
source frame, initially selected-player shields. Keep drawing native effects;
do not ask Remix to recreate them or move the ship. Earlier insertion alone is
not sufficient: output is currently paired to closed frames, and native opaque
and transparent work can interleave. The interface document gives ordered
qualification steps, resource-cap constraint and excluded shortcuts. This is an
integration extension to implement/qualify, not a completed shield fix.

## Validation / state

Five explicit static byte anchors checked against pinned client,full trace hash
checks,parent-draw counts/state/order consistency checks and saturation
counterexample pass. No broad suite/build/GPU renewals: implementation unchanged.
Run/evidence/interface notes,STATUS and newest HANDOFF updated; no commit/stage.
No new sponsor capture needed for boundary discovery. Next qualify bounded
same-frame native shield draw/layer retention offline before altering game
composition; source-frame pairing and128MiB output budget remain requirements.

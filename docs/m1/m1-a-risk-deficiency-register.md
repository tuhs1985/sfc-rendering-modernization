# M1 Increment A Risk and Deficiency Register

| ID | Finding | Evidence/classification | Disposition |
|---|---|---|---|
| M1A-DEF-001 | Inline observation at `0x006AB410` produced a sponsor-observed 3–5-second initial stutter while handling 32.4 million calls in about 56 seconds. | `M1-A-RT-002`; occurrence CONFIRMED, exact mechanism STRONG HYPOTHESIS. | Keep the geometry hook disabled in routine semantic operation. Use only bounded diagnostic windows; optimize hot-path work before reuse. No requirements waiver. |
| M1A-DEF-002 | Component JSON summary initially omitted synthetic retirement events from its per-kind counter although the CSV retained them. | Three CSV retirements versus zero summary count in `M1-A-RT-002`; CONFIRMED. | Source corrected after the run; analyzer evidence was unaffected. Verify on next relevant run. |
| M1A-OBS-001 | `0x00509843` occurs approximately once per scene epoch in the tested fixture. | 6,001/6,000 and 3,001/3,000 observations in `M1-A-RT-002/003`; CONFIRMED systematic finite exception. | Continue leaving it unassigned; it does not invalidate the mainline seam. No broader archaeology unless a later criterion fails. |

`M1-A-RT-003` retained all five semantic/lifetime hooks but omitted the downstream
hook. It showed no sponsor-observed stutter or other regression across 3,000
scene epochs. This rejects semantic activation/steady observation as sufficient
causes in the tested fixture and supports the practical semantic component
boundary. The semantic integration sub-gate is PASS; formal TRL 4 is not.

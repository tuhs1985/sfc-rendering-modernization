# M1-C-RT-001 — owner-specific lighting-off runtime evidence

## Executive result

**Later baseline update 2026-10-11:** sponsor reproduced the transient grid-like
loading-edge noise on manual launch. Independent client/launcher hashes still
match and temporary proxy/config are absent. Component-not-necessary attribution
is STRONG HYPOTHESIS; exact resolution/refresh cause remains SPECULATIVE, no
matched severity/module capture. Earlier "paired loading comparison first"
recommendation below is historical, superseded by baseline-associated monitoring
and remaining C-01 input qualification. This does not certify all assets/settings.

**CONFIRMED bounded lighting-control proof; M1 CONTINUES.** Sponsor observed the
enemy ship turn magenta, then lose shading, then return to normal shading, with
no other issues noted during skirmish. Runtime confirms eligible source flags,
owner-specific substitutions and releases, clean stop and unchanged client.
This is not a beneficial modernization, all-shading-removal or formal TRL4 claim.

**Open defect:** sponsor reported mild loading-screen glitching that disappeared
upon entering the session. Occurrence is CONFIRMED as a sponsor observation;
cause and component attribution are SPECULATIVE. Do not dismiss it because the
tactical result worked. No screenshots/presentation-time trace or paired loading
baseline was collected, so logs cannot locate the artifact or prove causation.

## Runtime identity and bounds

- Prepared source commit `fee152f`, component0.4, probe
  [M1-C-RT-001](../probes/M1-C-RT-001.md). Sponsor launched prepared elevated entry;
  automatic gate detected, controller duration stop. No analyst UAC or security change.
- Run `artifacts/m1/runs/20261011-180531-enabled`, PID35940; metadata start
  `2026-10-11T18:05:31.4794404-04:00`, completion `18:07:30.5761405-04:00`.
  Tactical schedule75s; last bounded sample75000ms;11,087 scene epochs observed.
  These are not measured presentation frame times/FPS.
- Geometry hookoff; semantic CSV120 epochs/10,000-event ceiling/eight owners,
  16MiB warning/32MiB hard cap; fixed96 summary samples, actual76.
  Detailed saturation after1,180 records did not terminate the off interval.
- Runtime DLL SHA256 `F85C9DFCB49796453A0E6DB4211903198FD9F650825DDD3B2E79AAD35F16D20A`;
  controller `4CE6D2086660DB74E1AA19A76E84688B83E17C4552BAB412BD30DBEE409E201E`.
  Entry rebuilt before launch; linker timestamps explain different preparation hashes.

## Semantic targeting and observed changes

| Evidence | Observation | Class |
| --- | --- | --- |
| All76 phase samples | owner1, ship `1E03AD88`, visual `082982E0`, Model0 `1DF7C518`, logical source `04A8365C`, manager mode5 | CONFIRMED runtime identity at sampled times |
| Source flags before/after | `0x23`; five referenced lighting-flagged entries | CONFIRMED runtime source participation/eligibility |
| Off samples13–57s | sample DWORD `0x23 → 0x21`, effective source `6020012C`, matching release1 | CONFIRMED source-copy vertex-light selector suppression |
| Off phase counters | 6,649 eligible/applied/released calls over45s | CONFIRMED bounded intervention/release |
| Identification cue | 428 applications/releases; sponsor identified enemy magenta | CONFIRMED runtime plus sponsor observation |
| Restored phase58–75s | 2,607 original-source Model0 observations; original flags return, no substitution; sponsor confirms shading returned | CONFIRMED runtime plus visible restoration |
| Early semantic CSV | two distinct coherent owner chains, no rejected samples | CONFIRMED bounded differentiation; not exhaustive untargeted visual coverage |

Owner2: ship `0C7C86C0`, visual `0C7C0E48`, Model0 `1DF7C20C`, source `08683D90`.
Total7,077 substitutions match7,077 restores, renderer-replaced0, rejected0,
restore-failed0, thread-mismatch0, active scopes0; semantic rejections and owner/
thread overflows0. Source originals remained available unchanged after each scope.
This run dynamically corroborates the vertex-lighting selector on this model;
the separate polygon-light bit0x04 was not exercised by this sample's flags.
No numeric normal/matrix-space recovery or universal lighting-pass claim.

## Cleanup, exception and limitations

Controller: `component_state=removed`, `hook_bytes_restored=true`; component
summary agrees. Storage remains mapped until exit as designed, not force-unloaded.
Runner classifies normal exit (`exit_outcome=exited`); no remaining SFC/controller
observed in analyst process query. Game-directory winmm/config not installed by
this direct-injection workflow; post-run absence checked.

Installed/reference client SHA256 both
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`;
run MD5 `2BE8F713F81B1C68D50EAD6088C32886`; launcher SHA256
`84D3A5F89A922C4BEE6815CF0614538C3565C4BDB7DB3AA187C552CB727EF890`.

`00509843`11,091 occurrences versus11,087 gated scene epochs: remains a finite,
unassigned exception, unmodified. General analyzer PARTIAL is expected because
downstream hookoff; no fresh006AB410 correlation claim. Five total retirement
counters are not fully detailed after saturation; no new retirement/reuse proof.

Loading attribution: semantic hooks are installed before the tactical gate and
may execute during loading. Visual source intervention is gate-timed and owner-
validated. This distinction does not prove that pre-gate hook overhead caused
the reported artifact; timing/composition evidence is missing. Previous stutter
record and this new loading artifact are separate observations.

## Raw handling and next action

CSV336,573 bytes; summary20,815; total13 run files415,692 bytes. Archived to
`artifacts/m1/archives/M1-C-RT-001-20261011-180531.zip`,19,954 bytes;
SHA256 `E9EC64E3773E493665E98AEB45C7F8264B802E41C030A5355A7171CD5B09DDCE`.
All13 archived file hashes independently match originals. Small raw retained,
all ignored/local; no material deletion, multi-GB trace or new capture mechanism.
Analyzer rerun has no issues; automated status stays visual-review-pending by
design. This curated adjudication adds sponsor confirmation without fabricating
automatic visual measurement.

Exact next action: prepare a bounded paired disabled/enabled loading-screen
comparison for sponsor review to resolve M1C-DEF-001 attribution before advancing
the enhancement. Do not broaden RE or silently waive this observation.

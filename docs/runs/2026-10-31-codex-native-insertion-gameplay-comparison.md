# Run227 — both native insertion policies pass sponsor checkout

Implementation parent remains `0c82e01`;changes remain unstaged/uncommitted. This is analysis and documentation only. No renderer/configuration change or further gameplay run was made.

Sponsor reports: **both seemed to work, with no noticeable impact**. On the specific occlusion check, sponsor confirms **shields and Paused text both looked correct**. This supplies the actual-game visual check that Run226's standalone effects/text fixture could not establish.

## Runtime evidence

| | Strict | ExtraFrame |
|---|---:|---:|
| Run | `20261031-060633-871969-in-game` | `20261031-061010-590335-in-game` |
| Recorded requests after first successful insertion | 5,265 | 5,180 |
| Matching inserted requests in that interval | 5,265 | 5,180 |
| Failed requests after first insertion | **0** | **0** |
| Gate wait median / p95 / p99 ms | 7.264 / 7.847 / 8.255 | 12.546 / 13.264 / 13.931 |
| Present-period median / p95 / p99 ms | 16.738 / 17.465 / 17.983 | 16.672 / 17.511 / 18.212 |
| Native continuation after insertion median ms | 2.643 | 2.919 |
| Source offer → Present callback median ms | 9.950 | 15.549 |

These were different manually played sessions. The longer measured ExtraFrame wait does **not** prove the policy itself adds a fixed5ms:it permits additional time but returns immediately when matching output is ready. Both runs stayed near60presentations/second during ordinary recorded intervals. Present callback timing is not monitor scanout or measured input latency.

Both sessions: normal exit;controller and renderer exit0;hooks restored/component unloaded;copied proxy restored;accepted client/critical files and launcher settings unchanged. No raw-ring drops, invalid tickets, partial flag, sequence reversals, or committed output with invalid readiness/order were found. At most one pending gate request;pending source slots sampled at Present stayed zero. Source age remained bounded over the run rather than growing steadily.

## Accounting and limits

The generic summary labels all non-inserted records as `measured_fallbacks`. That is too broad for these gameplay captures:

- Strict's116 non-inserted records all precede its first successful insertion. There is one deadline timeout during initial preparation. There are no failed gate requests afterward in the recorded interval.
- ExtraFrame's223 non-inserted records comprise104 initial records plus119 records,approximately1.97seconds,with **no selected-mesh gate request** at frames1355–1473. These are not renderer timeouts or evidence that an attempted replacement disappeared. Selected drawing resumes with successful current-frame insertion. Exact camera/action attribution is not independently recorded.
- Strict has a native source-frame jump881→928 across a568.483ms Present-observation interval. Its final native receipts exceed logged insertion records by46,the same number of source IDs absent inside that jump. No ring drops were reported. This is not evidence of46 deadline failures,but it prevents claiming every source invocation has a separate Present record. The exact cause of the gap is unqualified;do not label it a rendering stall, pause, alt-tab or camera event without evidence. One later31.941ms interval also occurred without a recorded failed replacement.
- Because the native scene counter is not established as a one-to-one display counter across that discontinuity,the negative Strict nominal60Hz schedule-drift value must not be interpreted as negative latency or recovered time. The stable rolling source-age distributions and bounded pending work support **no observed accumulating replacement backlog**,not a universal timing proof.
- Actual F-CA insertion records have one primary and zero secondary submissions. Synthetic component tests cover consistent suppression when both lists are submitted;this checkout does not independently prove an actual secondary-list scenario.

Original run results and raw records remain unchanged. Reproducible focused analysis and SHA256 provenance are in `artifacts/player-replacement/run227/analyze.py` and `review.json`. Sponsor feedback is recorded separately from the original machine results.

## Decision and next step

**Player-fixture native insertion demonstrated.** The replacement appears aligned and SFC's own shields and pause text now layer correctly,without shield replay or late whole-frame composition. Both timing policies passed the sponsor's perceptual check and the recorded steady gate requests.

Recommend **Strict** as the continuing default test choice:it achieved stable replacement here with the tighter admission deadline. Keep **ExtraFrame** available as the explicit comparison/headroom option. No launcher default,refresh cap,appearance setting or code was changed by this recommendation.

This closes the one-player return/insertion checkout. It does not complete arbitrary-scene replacement,the alpha release or a D3D12 adapter. The next contained implementation decision is extending the same committed-output authorization and suppression contract to other supported retained ships,with each owner's lifetime/asset identity preserved. Weapon lighting,damage textures and fast destruction/break-model handling remain tracked alpha requirements. Shared GPU-fence scheduling stays parked unless heavier scenes expose unacceptable waiting or missed deadlines. No additional discovery run is needed merely to repeat these two timing-policy checks.

# Run281 — Live effect radius checkout and moving-light review

Date: November3,2026 (sponsor local date). No renderer implementation changes in this review.

Sponsor: radius0.05 produced no visible light,1.0 was visible,2.0 worked and looked fairly close to SFC. Keep2.0 as tentative effect-radius baseline, not measured physical conversion. Intensity/color unchanged. The earlier synthetic Toolkit fixture does not prove equal runtime scale or actual hardpoint burial.

Reviewed three local light-diagnostic runs:

| Run | Submitted radius | Observed renderer frames | Active slot observations | Trace gaps/errors |
| --- | --- | --- | --- | --- |
| 20261103-051623-667642-in-game | 0.05 | 5376 | 1720 | 0 |
| 20261103-051907-463492-in-game | 1.0 | 5353 | 624 | 0 |
| 20261103-052208-777331-in-game | 2.0 | 5376 | 850 | 0 |

These counts are observations, not independent weapons or emitted photons. All recorded active light submissions were native type5. Latest trace802state-change records,645053bytes; zero omitted/invalid/unstable/unobserved-frame counts. Slots2..6 participated. Twenty-six contiguous slot/color stretches,25with changing positions. Same-color slot reuse can merge effects; these are not proven individual weapon lifetimes.

Latest radius2 run contains a distinct fast-moving orange-red contribution (native RGB1,.25,0), four stretches. Three have7/8/7samples across source frames3084..3090,4683..4690,4773..4779. Start-to-first-subsequent-off-or-color-change durations0.1141,0.1340,0.1160seconds; straight endpoint displacements14.207,16.751,14.141native units. The fourth is a single sample at3248with0.0179seconds until transition; movement cannot be established for that one. The three longer tracks are nearly straight: accumulated path length approximately equals displacement. This supports a brief moving-source interpretation; it does not identify photons by itself.

Other latest contributions: orange(.88,.55,0):15stretches/669samples; magenta(1,0,1):5/112; red(1,0,0):2/46. They too usually change position. Motion alone may include attachment to moving ships or slot reuse; no complete contemporaneous ship trajectories were retained in these performance runs.

Photon attribution remains unproven. Existing executable inventory identifies tFx_Photon draw0x00500C30 and photons-2.bmp resource acquisition0x00500862/select0x00500D6B. Inspected its local disassembly0x00500700..0x00501100; this is insufficient to connect the fast light's owner to that effect. Current submission trace has slot/type/raw record/frame/position/color/range but no weapon-owner/class or setter-call-origin link. Do not label a color as a weapon merely by visual resemblance. No additional gameplay run is required to confirm that moving lights exist; exact photon naming needs the smallest owner/call-origin association or a photon-only controlled comparison.

All three report error=null,normal_game_exit=true,renderer_exit=0,original_critical_unchanged=true. gate_clean_unloaded=false is present; do not claim that particular field passed. No new failure is inferred from that field without interpreting current cohort teardown semantics.

Analysis and detailed per-stretch data: artifacts/player-replacement/analyze_effect_run281.py and artifacts/player-replacement/run281/*.json. Output is original submission evidence, not proof of final visible pixel contribution. No settings beyond sponsor-requested radius were changed, no staging/commits.

## Sponsor slowed-game confirmation and publication

Sponsor slowed the game to speed1 before firing photons and could see the lights. This is visual support for photon-associated illumination, not a recovered code-level weapon/light owner association. Radius2.0 remains the tentative baseline. Sponsor authorizes commit/push and README Video2 link https://youtu.be/O-hdw14ai0E.

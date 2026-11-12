# November 12 rapid-pan colour and coverage investigation

The sponsor observed gray wing patches on a Klingon Bird-of-Prey during rapid camera pans. The retained gameplay evidence lacks synchronized image planes from the affected moment. A standalone replay reproduced a colour/coverage mismatch upstream of native SFC insertion. The connection to the exact in-game appearance remains to be checked.

## Replay and result

Replayed the captured 452-triangle KFF and its materials through the committed alpha host and pinned Remix runtime at 960×540. The replay used 15 frames with camera yaw `0,0,0,0,0,3,6,9,9,9,9,9,0,0,0`. Both paths received the same pose. The standalone cohort required a nonzero diagnostic offset, so it used `-0.00002` game units. No game, ReShade, or damage decals were involved. Each run exited normally with no owned process remaining and retained about 99 MB of evidence.

The table counts returned pixels with at least one RGB channel above 18/255. This threshold identifies a visible colour signal without using colour to determine coverage. The two mask columns can overlap.

| Replay frame | Signal pixels | In current owner mask | In previous owner mask |
| --- | ---: | ---: | ---: |
| 5, first 3° pose | 365 | 79 | 365 |
| 6, first 6° pose | 672 | 186 | 646 |
| 7, first 9° pose | 709 | 189 | 690 |
| 12, abrupt 9° return | 515 | 1 | 515 |
| 13, second frame after return | 804 | 752 | 752 |

Owner coverage and depth were identical between frames 7 and 11 at the same 9° pose. Of the 3,591 covered pixels, 493 differed by more than 24/255 in at least one colour channel. With the denoiser off, 695 pixels differed at the same threshold and the first frame after the abrupt return still had essentially no colour inside the new silhouette. Disabling the denoiser alone is therefore insufficient.

Local outputs are under `artifacts/player-replacement/rapid-pan-kff-profile-on` and `rapid-pan-kff-profile-off`, including the raw returned planes, `same-pose-analysis.json`, and the on-run `motion-alignment.json` and `motion-alignment.png`. Replay and analysis scripts are under `artifacts/alpha/candidate` as `run-kff-rapid-pan.py` and `analyze-kff-pan.py`.

## Localized fault and next action

The host presents the D3D9 scene, requests Remix `FINAL_COLOR`, then independently rasterizes depth and owner coverage from the current pose. It fences and labels the three planes together. The game receiver validates the cohort ticket and acquires the three views from one slot. This proves completion of the copies and agreement of their metadata. The replay shows that the colour pixels can still correspond to the prior pose.

The pinned `FINAL_COLOR` implementation gets swap-chain backbuffer 0 at the time of the request and enqueues a blit from that image. It returns no source-frame ID. The host uses `D3DSWAPEFFECT_DISCARD` and requests the copy after `PresentEx`. The next experiment should use alternating, distinguishable poses or frame markers to test whether the post-Present backbuffer selection accounts for the lag and qualify a capture point that returns the matching frame. Keep the native exact-cohort check and current fallback. Confirm colour, depth and coverage alignment in replay before an in-game rapid-pan checkout. [Pinned Remix output-copy implementation](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_remix_api.cpp#L1394-L1447).

No implementation, appearance profile, or alpha package changed during this investigation.

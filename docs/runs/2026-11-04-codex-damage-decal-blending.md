# Run289 — damage first-use transparency and unstable overlap

Sponsor reports three runs;focus on last050155 through damage stages. Ship turns transparent for several seconds on first application,then damage works with occasional glitches. This visual defect is accepted sponsor evidence;do not dismiss it because transport checks passed.

## Review

-043317:5341renderer frames,9566hull draws,1683damage draws,0unqualified damage states.
-050027:3164renderer frames,5891hull draws,0damage draws,0unqualified states. This run did not exercise the actual damage layer despite enabling its option.
-050155(last):2167renderer frames,4129hull draws,742damage draws,0unqualified states,2assets loaded/2owners,0asset rejections. Native gate requests2167,stale/invalid/timeouts0. Original-frame periods include startup and a tail with no pending requests;do not label every original frame a missed renderer deadline.
-All normal-exited,supervisor error absent,original client unchanged;process-exit reclamation remains separate from clean in-process hook unloading. Existing records do not retain every damage transition,so they cannot prove the exact duration/onset of the reported transparency or identify every later glitch.

The earlier damage getter fix is functioning:state no longer rejects the hull. There is no evidence of asset reconstruction on the first damage application;cached damage textures/VBs already exist. Renderer output contents,not missing ship submission,are the primary suspect.

## Documented interface violation

Pinned NVIDIA source `rtx_instance_manager.cpp::calculateAlphaState` lines819–824 explicitly requires blending for decals,through legacy or overridden state. Our material uses legacy alpha state and our draw set ALPHABLENDENABLE=FALSE. Therefore tagging decalTextures alone did NOT set isDecal. The duplicate full hull stayed an alpha-tested coplanar surface rather than receiving the intended decal handling/offset/material blend. This is a concrete configuration defect and a strong explanation for overlap corruption;the exact multi-second live symptom remains subject to sponsor retry.

References:
- https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_instance_manager.cpp#L819
- https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/src/dxvk/rtx_render/rtx_options.h#L215

## Focused correction

Remix adapter's damage draw now enables source-alpha/inverse-source-alpha ADD blending,retaining exact-black cutout/alpha test and disabling decal depth writes. It restores opaque blend/test/depth state afterward. No canonical geometry/UV/image changes,no custom offset,no waiting/prewarm delay,no altered source qualification or matching. No lighting/material/image settings changed. Blending is a backend requirement here,not a new claim about SFC's native alpha equation.

Actual ExtraFrame fixture050622:600frames/3owners,zero native pixel/state errors,clean process exits. Heavy damage now forms discrete marks over a solid hull instead of the previous speckled surface;repair clears it. Strict fixture050736 also passed600frames/3owners/native pixel/state checks.673Python tests pass.

The previous snapshot probe waited30frames,so it was inadequate for first-use inspection. Offline-only capture now additionally takes the first encountered damage-bearing output as sample6,and first light output as sample1. Asset preparation can start the fixture at medium/heavy,so the first light cycle alone is NOT a cold first-use proof. At most5bounded snapshots;ordinary gameplay readback remains off. All output budgets preserved.

Cold first-use fixture and final preflight results appended after completion. Live appearance/first-use transparency and occasional later glitches remain unverified until sponsor retry. Leave changes unstaged/uncommitted.


Final first-use proof:`20261104-051206-628339-return-fixture` uses an already visible undamaged scene before applying the first damage. Baseline sample0 output30/source200251;FIRST damage sample6 tier0/stage_age1/output47/source200268;next light sample1 output48;heavy and repair retained afterward. Visual inspection shows a solid complete hull on the first actual damage-bearing output;no settling window hides it. This addresses the fixture weakness. An earlier cold sample6 from050929 was BLACK at renderer startup before an intact scene existed and is NOT damage-transparency acceptance evidence. Retained explicitly as a diagnostic confound,not a pass.

Final fixture:600frames/3owners,zero native pixel/state errors,clean exits. Ordinary blend submission unchanged from successful Strict050736;only offline snapshot scheduling/test stages refined afterward. Current qualification/preflight refreshed from these proofs. Normal SFC readback remains0. Diagnostic register added to `docs/DIAGNOSTICS.md`,including counters with no independent toggle yet and functional checks that must not be mislabeled optional. Live recheck remains necessary;the later slight glitches may share the coplanar defect but are not individually attributed by existing logs. No universal resolution claim until sponsor observation.

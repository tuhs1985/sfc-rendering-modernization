# Run42 — first native-light capture reviewed

SFC-RETURN-20261018-42;2026-10-18 America/New_York. Sponsor "Done. What we got";
read-only runtime adjudication,not authorization for further code changes or
lighting overrides. HEAD2fa8032,indexempty,Run40/41 changes retained. Read HANDOFF,
newest run manifest/raw light bank/worker/hook/launcher/renderer logs and native
light map. FuelGuard actual thread hook attached;no daemon/helper/subagent.

## Result — native values confirmed;final workflow report PARTIAL

Runtime `artifacts/remix-runtime/runs/20261018-223855-130708-in-game` produced
641packed light snapshots,3,945,996B,533distinct frames,owner1=200/owner2=441,
47..89,984ms after tactical gate. Same native bank0x04D70038 observed under both
owners,NOT two independent copies of each light. Global lighting gate1 throughout.
All64slots retained. Prefix2 in635samples,3 in3samples,4 in3samples;no consumed
slot above3. No hypothesis-based3light filter. Worker641captured/written,0drops/
rejections,queue0,io_failed=false. Short pulses can still fall between5Hz samples.

**CONFIRMED:**two steady native type0 directional-response lights:

| Slot | Direction input | RGB contribution | Native multiplier |
|---|---|---|---|
|0|(0.98893636,0,-0.14834046)|(1,1,1)|1.5|
|1|(0,0,1)|(1,1,1)|0.25|

Direction,RGB and multiplier each have exactly1observed variant across641records.
Multiplier ratio6:1 is native response weighting,NOT calibrated photon/lumen or
visual brightness ratio;native channel clamp/other contributions still apply.
"Main" and "fill" are useful provisional labels,not recovered engine names or
proof slot0 is an astronomical sun. Native type0 software dot response already
statically corroborated;do not interpret native enum as DirectX enum.

View384variants,supplied transform508variants while input directions remain fixed.
Using established native_matrix conversion and transposed supplied3x3,all1282
direction comparisons agree with native object-local derivatives within
2.9794492206747236e-08 max absolute error. This directly corroborates native
direction-transform arithmetic with live values,not complete Remix axis/sign/
intensity qualification. Raw type0record changed383times because unused payload
positions vary across owners;DO NOT misclassify those raw-word changes as changing
light directions/intensities. Only type0-used fields establish stable light state.

**CONFIRMED transient slots:**2active6samples,61.141..89.375s extrema;3active3samples,
61.344..61.750s. Both native type5 special positional-response path. Slot2 includes
orange(0.88,0.55,0)and green(0.1,0.3,0)contributions;slot3orange. These are separated
observations,not proof of continuous on-duration. Type5unused direction words can
contain pointer-like/uninitialized values;do not pass them as physical directions.
**STRONG HYPOTHESIS:**weapon/impact/effect-associated sources. No event association
in this capture proves which weapon/effect,or faithful standard point-light mapping.

Sponsor's three-lights/GI hypothesis is not confirmed:observed two persistent
directionals plus up to two transients. Ambient/material self-light/native
software effects and Remix indirect illumination may be separate;no GI claim.
Current extra ship STILL uses provisional test light;native values not sent yet.

## Cleanup / missing report / exact evidentiary limits

Original runtime result.json is ABSENT despite retained raw evidence. No active
game/renderer/Python process remains. Root failure/exit trace not retained;do not
guess exception or manufacture successful original-run report. This is an open
final-report deficiency;native discovery itself remains usable/confirmed.
New curated review is distinct from missing original result.

Independent sources:launcher.log CHILD_EXITcode0;controller.log durationstop,
component_state=removed,hook_bytes_restored=true,component_unloaded=true;
M1-A-summary hooks_restored/gate_activated=true. Host1692produced/1691drawn,failed0,
SDKshutdown0;known SDKwarning40 persists. Independently rechecked all7critical
files in accepted/copied installations against recorded manifest and launcher
registry settings:all unchanged. Both executableSHA256 remains
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
Registry sandbox read denied;scoped approved read-only comparison succeeded.
No new sponsor-visible behavior checklist inferred merely from "Done".

## Commands / evidence / repository

Bundled Python3.12.14,numpy and existing decoder/analyzer/native_matrix only;
no build/new runtime. Decoded native-lights.bin6156B chunks with native_light_state;
light_discovery.analyze validates monotonic session/counts/enables. Then counted
active slots/types,unique type0direction/RGB/scalars,view/supplied variants and
computed max(abs(R.T@direction-local_direction)) on each direction sample.
First guessed module paths/imports failed harmlessly;corrected to
tools/m1_component/analyze_live_camera.py and run_return_game's source/hash helpers.
Original files read-only,generated disassembly/geometry not expanded.

Probe NATIVE-LIGHTS-00190s/5Hz/2epochs/900records,rawmax5,540,400B observed below
cap;no images/continuous screenshots,geometry hookOFF. Existing log/image/process
caps unchanged. Archive6,441,003B,CRCverified,raw retained:
`artifacts/remix-runtime/archives/20261018-native-light-discovery-runtime.zip`,
SHA256 `5E52C1BEF99A005B1DE5504D5C7D0613C02E0DC5D377C2999EC2BE8A5D19FC66`.
[Curated evidence](../reconnaissance/evidence/20261018-native-light-discovery-runtime.json)
records exact numbers/raw hash,independent checks and missing-report caveat.

Created this record/evidence;updated native-light map,HANDOFF. No production
source/config changes,stage or commit. Prior uncommitted preparation retained;
no active session needed. Targeted decoder/summary regressions and JSON/CRC/diff
checks performed. No new game run or requirements/milestone claim.

**Exact next action:**diagnose/fix missing final-report persistence with an offline
reproduction,then map the two demonstrated type0lights into Remix with explicit
coordinate/sign/strength normalization and per-light control binding. Do not
translate type5 as a generic point light or assume GI to avoid its unknowns.

## Same-run follow-up — active position changes and sponsor context

Sponsor reports weapons fire during this run;this corroborates the effect-source
interpretation,not a trace-level association with a specific projectile. Sponsor
interprets basic lighting as main/fill/dark regions;retain that working visual
interpretation without reopening self-shadow mechanism RE. Both steady sources
remain native type0;their angle98.53degrees,not180;fill is not proven GI.

Read-only recheck of ACTIVE samples only confirms both transient slot positions
change under the SAME owner2 with matching orange RGB. Slot2five consecutive
samples61.141..61.953s move from(-283.73468,162.83524,.17856)to
(-282.97327,160.81406,.47403). Slot3three61.344..61.750s move from
(-283.58319,162.25539,.17874)to(-283.25781,161.19257,.17891).
These are not merely stale disabled-slot values. Later green slot2at89.375s
must not be joined to orange trajectory:slot reuse/new source remains possible.
**CONFIRMED:**active position changes;**STRONG HYPOTHESIS:**moving weapon/effect
lights given sponsor observation. No physical speed calibration or proof of
persistent individual projectile identity. No production changes or new capture;
original raw hash unchanged,prior validation applies,indexempty,no stage/commit.

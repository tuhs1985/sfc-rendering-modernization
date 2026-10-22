# Run66 — depth first,existing display path retained

Date2026-10-19 America/New_York. Sponsor requests depth work and corrects grid/UI
description. Starting HEAD`d29111f7a513c4510c4d33aeeda2c355d98443a5`,sanitized
branch,index empty;Run65's2modified/7untracked files preserved. No commits/push.
Read current HANDOFF,operating convention,Run65,replacement/live/depth contracts,
native calibration evidence,collector/compositor/runner and qualification tools.
Fuel Guard exact-thread hook attached;direct sandbox query denied,hook verified;
no daemon/helper/agent. No SFC/Toolkit launched during development.

## Evidence correction and scope

CONFIRMED sponsor observations:accepted extra ship appeared under tactical UI;
normal grid lines appear through ships at a particular height. Neither visual
description is a hypothesis. World-plane interpretation/draw/depth policy remains
unconfirmed. Earlier assistant assertion that the existing image necessarily
covers HUD was unsupported. Preserve the working callback/UI ordering rather than
move it on that assumption. No claim every effect/UI overlap is already qualified.

Sponsor explicitly prioritizes depth before replacement. New default-off additive
scene-depth mode,originals always ON;no new engine hook/suppression. No grid
classification guess,appearance changes,renderer redesign or supersampling.
R2's four active TOMLs remain byte-identical to saved baseline (all hashes checked).

## Implementation / reproduction

[REMIX-SCENE-DEPTH-001](../reconnaissance/probes/REMIX-SCENE-DEPTH-001.md)
defines complete procedure,limits,provenance,rollback and sponsor instructions.
`ship_scene_depth.h` retains actual native8MSAA shader-readable scene depth at
public D3D11 draw callbacks. Requires current engine frame and one supported
resource,thread/dimensions;missing/mixed/unsupported/cleared-after-draw declines.
View creation once per resource epoch at pre-Present,not original draw callback.
Only small fixed counters;no raw geometry/image logging or game-side readback.

Existing private compositor optionally compares returned normalized depth to the
minimum of8 native samples. SDK-frustum pixels map through actual native viewport;
the historical fixture is(200,30,1720,1020),not a full-screen camera viewport.
Output/picking/native depth association remains explicit;current source camera/
supplied-pose hashes must match returned values. Current native scene frame must
match at filtering AND late display. Up to100ms identical-state reuse remains
diagnostic only,never suppression authority. Extra layer omitted on mismatch.

New128byte telemetry extension at2048;does not overlap triplet/command/seed/image
snapshot metadata. Existing late AddImage/UI path unchanged. Full-support pinned
ReShade used only in copied test installation for public draw/depth-clear events,
with existing verified rollback after exit. New independent source-matched depth
receipt avoids reusing stale broad-trace qualifications or a2GB trace reservation.

Prepared entry after qualification:
`powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\remix_runtime\start_return_image_session.ps1" -SceneDepth`.
90s tactical/<=5min prepared workflow,normal two-beep exit. Enter skirmish normally,
then sponsor manually PAUSES and holds camera so an enemy-selected ship is
stationary too;small camera change/hold,then unpause and move/turn when ready.
Existing10/20second cues are reminders,not forced phases. Extra image may omit while
state changes;originals/UI/controls must remain normal. No routine UAC,manual
timestamps,reverse engineering or requirement to control the enemy.

## Offline validation (completion recorded below)

Native build /W4 /WX x86/x64 successful. Existing material24,quality14,image22,
request89,RemixUV14,light25checks per architecture pass. Extended replacement/depth
GPU fixture66checks each pass:offset viewport pixel oracle,near/far depth,wrong-ID/
invalid-depth discard,legitimate black,sourceframe/mixed/cleared/epoch refusal,
state preservation and later UI. New non-1:1 viewport sampling also corrects the
unused Run65 depth compositor;no production replacement was previously deployed.
Full-state restoration uses D3D11 command-list API;tests enumerate OM/IA,not every
possible state slot. Single-sample returned coverage remains an edge limitation.

Python283tests PASS5.588s;targeted14CLI/telemetry/receipt tests PASS0.952s.
Existing Pillow deprecation warning retained. PowerShell parsing passes.
Actual first standalone full-support callback trial normal exit0:
`20261019-215940-883993-live-private`,hidden22frames/missing-depth18/restored11,
native1920x1080/8MSAA,qualified342,wrong-thread0/failed0. This development trial
precedes final clear/epoch guards;not reused as final source-matched authority.

Final14existing return gates plus3new depth normal/slow/disconnect gates and
read-only runtime preflight are required before READY. No SFC runtime depth
behavior,grid policy,original suppression or milestone/TRL advancement claimed.

## Output stewardship

Sponsor10GB allowance retained. Compacted95old safely completed exact Oct19
private fixtures' generated binary copies,plus completed new fixture copies.
`archive_fixture_binaries.ps1` validates resolved run/direct file paths,completed
result,manifest hashes/pinned proxy,reparse/size guards;ZIP then decompressed SHA
comparison before deleting ONLY copied fixture EXE/addon/proxy. All originals,
current build binaries,source,provenance,packets and logs remain. Per-run receipts
and recoverable archives retained. Existing texture compactor similarly used for
completed test images. Nothing removed from game installations or Git history.
This was necessary to reserve the next384MiB inside10GB;no cap increase.

## Files / state / next action

Production edits:live_return.py,ship_live_receiver.h,ship_triplet_compositor.h,
return_addon.cpp,run_return_game.py,start_return_image_session.ps1.
New ship_scene_depth.h,scene_depth.py,qualify_scene_depth.py;
qualify_live_return.py/ship_live_gpu_fixture.cpp add actual callback failure tests;
qualify_material_pipeline.py archives finished generated copies.
New archive_fixture_binaries.ps1,test_scene_depth.py;CLI tests extended.
Run65 native depth header/tests extended. Probe/this record/readiness/replacement
contract/HANDOFF updated;prior records preserved as historical.

Existing SDK40 common-object warning remains. Accepted/copied client hashes
checked unchanged`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
No active game/proxy installation;no staging/commit/push. Final state and actual
qualification receipt/evidence paths follow at completion. Exact next action is
the prepared90s sponsor depth-only test after all offline checks pass,not original
ship suppression or more appearance tuning.

## Final qualification / READY disposition

CONFIRMED:14existing return gates PASS and refreshed source-matched
`artifacts/remix-runtime/deps/live-return-qualification.json`. Three additional
actual Remix/full-support ReShade cases PASS:

- `20261019-221404-189523-live-private`:normal;hidden22/missing16/restored10.
- `20261019-221447-341911-live-private`:slow receiver;hidden18/missing16/restored10.
- `20261019-221531-830690-live-private`:renderer disconnect after depth phases;
  hidden21/missing16/restored1;fixture normal exit0,failed0,67drawn.

All directories under`artifacts/remix-runtime/runs/`. Exact source/binary/proxy
hashes and case paths preserved in
[curated receipt](../reconnaissance/evidence/20261019-scene-depth-offline.json),
byte-copy of`artifacts/remix-runtime/deps/scene-depth-qualification.json`.
`OFFLINE_SCENE_DEPTH_CALLBACK_PASS` is not a real-game success claim.

First final preflight correctly rejected stale native-light qualification after
runner edits. Native observer worker test failed inside sandbox;rerun with scoped
approved elevation PASSED and refreshed actual qualification,not a bypass/hash
rewrite. Both`run_return_game.py --scene-depth` and`--light-tuning` then read-only
preflight PASS,no game/renderer launched. Final unittest discovery283PASS5.767s.

Important limitation:depth mode clears display each frame and requires a newly
qualified output.30Hz asynchronous output versus faster game frames may blink
EVEN stationary. Holding an already filtered image could use obsolete native
depth,so this diagnostic deliberately refuses it. Default additive duty-cycle
gate remains intact;new depth mode does NOT claim steady replacement. Runtime
test may be PARTIAL if refusal prevents useful overlap observation. Do not suppress
originals or relax provenance merely to conceal this. No grid behavior is assumed.

Additional five completed044159/044211/044246/044323/044358 fixture binary copies
were ZIP-compacted recoverably for384MiB reservation headroom;same path/hash guards,
all provenance/logs/packets preserved. No accepted game files removed or changed.
R2 settings unchanged;client hashes both remain
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.

Final disposition:READY FOR SPONSOR RUNTIME TEST,not replacement. No game/owned
host active. HEAD unchanged,index empty;all prior/current edits unstaged and
uncommitted,no push. Exact next action is the probe's manual-pause depth test.

Final capture/archive storage9,589,352,873B;plus402,653,184B reservation fits
10,000,000,000B. R2 four-file hashes PASS. Final Git12modified tracked/15untracked,
index empty. Documentation link check found one historical link to the already
privacy-sanitized screenshot;marked removal explicitly instead of restoring it.
Changed-document links and`git diff --check` checked;no evidence overwritten.

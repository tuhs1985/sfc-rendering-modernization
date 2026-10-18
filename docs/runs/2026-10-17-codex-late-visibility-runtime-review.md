# Codex run — late visibility runtime adjudication

Run SFC-RETURN-20261017-04,2026-10-17 EDT. Task: adjudicate completed
REMIX-RETURN-001 -InspectVisibility skirmish. HEAD e96765a,index empty; prior
uncommitted work preserved. Actual-thread FuelGuard hook receipt verified,
no daemon/helper/delegation. Governing inputs: HANDOFF, approved return-path task,
[probe](../reconnaissance/probes/REMIX-RETURN-001.md),
[readiness](../reconnaissance/ship-replacement-readiness.md),
[preceding run](2026-10-17-codex-return-cleanup-and-ship-readiness.md).

## Question / exact evidence

Does a D3D11 depth-stencil view remain bound at the supported late ReShade
overlay insertion? Sponsor ran prepared elevated-parent workflow with
-InspectVisibility, then reports: "done , no issue noted". No new gameplay or
implementation during this adjudication. Read actual result.json,manifest.json,
host.log,launcher.log,gate-controller.log in
artifacts/remix-runtime/runs/20261017-061033-016248-in-game.

CONFIRMED eight observations,>=1s interval after automatic tactical gate,
depthPresentSamples0; depth descriptor fields all0. Extensionversion1,
visibility_observation=NO_DSV_AT_LATE_INSERTION. This rejects availability of a
currently bound DSV at this callback for the sampled fixture, NOT existence of
scene depth elsewhere. It does not qualify a depth texture, prove the game is
depthless, identify a replacement mask or authorize suppression. Prior late
snapshot hypothesis resolved negatively; do not repeat unchanged test.

Existing return path remained functional: produced=ACK=presented=copyCount662,
drawCount2712,staleCount0,error0.90s tactical;122.422s prepared run within285s.
15files/1079401B including retained small binaries; below16MiBwarning/32MiBhard.
No screenshots/image dumps. Sponsor no issues; no separate new claim about each
specific UI function beyond that report.

Verified copied-clientPID4712 before resume, startupRestored/Verified1;
gameexit0,rendererexit0/SDKShutdown0. Gate controller34192exit0,hook bytes
restored,component removed/unloaded. FinalREADY0/sharedHandle0/clearCount1;
no controller left running. Final process inventory finds no owned game,host,
launcher/controller; command no-match exit status is not a failed game exit.
Original critical hashes and launcher settings unchanged per runner; copied
client hash validated. Known40-common-device-objects warning persists after
HOST_RETIREMENT_DRAINED/Shutdown0; remains unresolved, not silently closed.

## Changes / validation / decision

Documentation only: this review, HANDOFF authoritative checkpoint,readiness and
probe findings. Raw machine results unchanged; sponsor report/verdict in curated
record. Read JSON/logs and process/Git state; no implementation changed, so no
unnecessary rebuild/repeated runtime. Final diff check and current client hashes
verified. Last implementation102Python/native36tests remain baseline, not rerun
or relabelled as new tests this review. No staging/commit; existing untracked/
unstaged implementation remains. No transport session may be reused.

RETURN PATH DEMONSTRATED remains confirmed. ONE-SHIP REPLACEMENT not
demonstrated; ADDITIONAL BOUNDED EVIDENCE REQUIRED for retained scene visibility.
Exact next action: identify one earlier supported rendering/presentation scope
and its ordering relative to tactical depth/HUD, then prepare a bounded depth
observation there. Do not assume an earlier callback retains depth, use blocked
ReShade application events, silently replace proxies or add a black cutout.
If no supported point exposes depth, report precise missing access and bounded
alternative before changing interception approach. No original ship suppression.

Selected JSON/log/config evidence archived after analysis to
artifacts/remix-runtime/archives/20261017-061033-visibility-runtime-evidence.zip;
compiled binaries excluded,original small raw evidence retained,no deletion.

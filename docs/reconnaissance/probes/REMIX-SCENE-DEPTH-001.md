# REMIX-SCENE-DEPTH-001 — depth-first additive check

Status: RUNTIME PARTIAL; do not repeat before delivery-cadence correction.
[Run67](../../runs/2026-10-19-codex-scene-depth-runtime-review.md):depth found,
but severe flicker prevents useful visual adjudication;placement remains unproven.
Historical preparation and source-matched offline qualification follow.
See [Run66](../../runs/2026-10-19-codex-scene-depth-preparation.md) and
[receipt](../evidence/20261019-scene-depth-offline.json). Actual SFC depth remains unproven.
Authority: sponsor requests depth first,2026-10-19. Original drawing stays ON.
This does not enable replacement,change UI insertion or set a tactical-grid rule.

## Observations and question

CONFIRMED sponsor observations:the accepted extra ship was under the UI;normal
game grid lines appear to pass through ships at a particular height. Those are
descriptions of observed behavior,not hypotheses. A world-height plane and its
depth policy remain implementation hypotheses. Earlier assistant implication
that existing output necessarily covered HUD was unsupported.

Question:can the accepted offset textured copy use actual native scene depth,
with the correct viewport mapping,without changing the original frame/UI path?

## Mechanism

Default-off `-SceneDepth` / `--scene-depth` sets child-only
`SFC_REMIX_SCENE_DEPTH=1`. Reuses fresh assets,semantic mailbox,texture/light/image
baseline,Remix runtime and original late AddImage callback. No owner suppression,
new semantic hook,geometry firehose,UI relocation or guessed grid classification.

The isolated test copy temporarily uses the already pinned official full-support
ReShade6.7.1.2131 (SHA`A1BA732B5E31E0405CDE322CC5EC62CF972B3FBAEFBB6CBDC8A24DA00D58AE24`)
for public native draw/depth-clear callbacks;accepted installation is untouched.
Existing verified atomic backup/restore workflow restores copied proxy/config
only after normal game exit. Source-matched standalone qualification is separate
from historical broad-trace receipts;no2GB trace is requested/reserved.

Read-only callbacks retain the actual D3D11 R32_TYPELESS/D32_FLOAT8MSAA,
shader-readable scene texture and observing engine frame. Different supported
textures/frames,unsupported depth,wrong thread,clear-after-draw or missing frame
observations refuse the extra layer. No stale source is silently reused. One
SRV is prepared per retained resource epoch at pre-Present,outside original draw
callbacks. No copy/readback/disk access/wait in these draw callbacks.

Existing private compositor samples all8 native depth samples conservatively
(minimum valid normalizedZ). Returned picking ID/depth determine covered ship
pixels;returnedZ farther than native nearest depth is discarded. Existing
viewport is NOT full screen:historical fixture has`(200,30,1720,1020)` inside
1920x1080. SDK pixel centers are mapped into that native rectangle before depth
lookup. Single-sample returned coverage and final bilinear display remain existing
limitations;this is not exact8MSAA coverage reconstruction.

Native depth frame must equal current semantic frame. Returned output must also
match current owner/revision/session/asset and supplied-transform/camera hashes,
and remain within existing100ms publication bound. Source/output frame IDs remain
distinct;identical-pose reuse is diagnostic ONLY,not a frame-exact suppression
contract. Extra image is omitted on mismatch,including while moving. Originals
remain visible. No automatic old-image hold or replacement authorization.

## Bounds / evidence / cleanup

Usual90s tactical and<=5min prepared workflow;32MiB non-image/log cap,16MiB warning;
128MiB existing original/derived image cap;384MiB aggregate storage reservation
inside sponsor10GB allowance. No new native image dumps/screenshots or geometry
transcripts. The retained native texture is an existing game resource,not a new
surface allocation. Existing output pool/resource limits unchanged.

128byte version1 counters at return mapping offset2048 (not scene transport):
header4uints;draw/found/missing/wrong-thread/ambiguous/unsupported/frame/qualified/
state-mismatch/displayed/resource-epoch/failed counters;nativewidth/height/samples/
engineframe;12zero reserved words. These are independent telemetry values,not an
atomic evidence packet. Existing per-sample history carries exact display/source
frame/QPC from original return protocol. Report normal exit,hook restoration/
unload,proxy/config rollback and both client hashes separately.

Owned standalone fixtures qualify normal/slow/disconnected renderer through
ACTUAL full-support ReShade callbacks and actual Remix output. Synthetic native
depth phases:far=show,near=hide,noDSV=omit,far=restore,then existing disable/
retirement checks. An independent64square GPU test checks offset viewport,
stale/mixed/cleared depth,resource epoch,exact pixels and original state. No SFC
launch during qualification. Finished fixture images/binaries compacted only
after decompressedSHA verification;provenance/logs/packets remain loose.

## Sponsor procedure (only after READY)

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\remix_runtime\start_return_image_session.ps1" -SceneDepth
```

Use the established elevated parent. Enter familiar two-ship skirmish normally,then PAUSE
the match using the normal game control;hold camera still and locate the extra
textured copy. This also holds an enemy-selected ship still without asking the
sponsor to control it. Make a small camera change,then hold the camera still with
the match paused;unpause and gently move/turn when ready. Existing10/20second
camera/motion cues are reminders,not forced measurement phases. Watch whether
nearer scene content hides the copy appropriately and report grid/UI appearance.
The extra copy may blink EVEN while stationary:the asynchronous output is30Hz,
whereas game frames can be faster. This test omits frames without fresh qualified
output rather than retaining a previously filtered image against newer depth.
Motion may cause further refusals. Steady delivery is NOT qualified by this mode.
Originals must stay normal throughout. If practical,briefly put the extra copy
partly behind an original ship to compare overlap;do not chase a particular angle.
Exit normally at the two-beep request. No firing requirement,manual timestamps,
UAC/security changes or sponsor reverse engineering.

Success is depth behavior with normal gameplay and clean bounds/exit;not ship
replacement or proof of native grid policy. Missing qualified depth,unexpected
UI/grid behavior or widespread refusal is PARTIAL with counters preserved.

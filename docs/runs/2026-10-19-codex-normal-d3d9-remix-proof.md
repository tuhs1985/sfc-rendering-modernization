# Run70 — normal D3D9 Remix interception; bounded partial qualification

Date2026-10-19 America/New_York;UTC output folders20261020.
Authority:sponsor “Resume work” after Run69,within reviewed D3D9 transition.
HEAD`d29111f7a513c4510c4d33aeeda2c355d98443a5`,branch`codex/github-sanitized`.
Index empty;prior Run65–69 dirty work preserved. No staging/commit/push.
No SFC launch,installation/proxy edit,Toolkit startup,SDK registration,helper,
subagents,security changes or new rendering architecture.

## Starting evidence / question

Reviewed HANDOFF,Run69,neutral scene contract,D3D9 transition and renderer-boundary
decision,offline consumer/decoder/tests,pinned runtime manifest,owned-job guard,
and official pinned bridge/capture/camera implementation where needed.
Question:does the SAME ordinary x86 D3D9 fixed-function VB/IB/texture/transform
submission expose actual reusable ship geometry to normal Remix interception?
Startup/Present/fullscreen texture alone cannot answer this.

Fuel Guard attached to exact current thread through recent trusted hook;direct
sandbox connection denied,no daemon spawned. Advisory only,credits available.
Prior5%handoff request retained;this run parks at bounded gate findings rather
than expanding into live integration while validation has unresolved failures.

## Dependency / probe / decisions

Pinned release`remix-1.5.2`,source commit
`b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4`.
Local ZIP`artifacts/remix-runtime/deps/remix-1.5.2-release.zip`,SHA256
`cc424be4dd1a0c6fd922bc6a7f8e5f6582baea7043a38afa6686d8b6faabad01`.
Private extracted inputs`artifacts/d3d9-intercept/deps/remix-1.5.2`;
all shipped bytes checked against ZIP before/after execution;manifest sibling.
No downloaded header/bundled DLL mismatch;no runtime source patches.

VS2026 x86 C++20 /W4 /WX /Brepro;Python3.12.14,Pillow12.3,NumPy2.3.5.
Read-only USD parser from installed
`C:/Project/RTXRemix/extscache/omni.usd.libs-1.0.3+6312fa25.wx64.r.cp312`,
USD0.25.11. Not USD ingestion or Toolkit rendering. NVIDIA4070Ti;
read-only driver query32.0.16.1742. Owned process guard is existing
`artifacts/remix-ingest/bin/bounded_job.exe`.

Source geometry remains historical LIVE-SCENE runtime packets from
`artifacts/m1/runs/20261016-223535-enabled`;MOD geometry is never loaded.
Original primary images alone resolved from copied installation associations.
Compile-time replay variant loads the verified absolute x86 bridge DLL;no
SDK symbols/mesh registration. Same positions,normals,raw UVs,groups and
world/view/projection as plain consumer. No inherited SDK-only V flip.
Corrected hidden-window client extent to960x540 for bridge presentation.

Process-local capture definition is generated`rtx.conf`/`bridge.conf` per runner.
Single-frame capture12(source snapshot0) or96(snapshot2);one diagnostic screenshot
at capture+8. `rtx.enableReplacementAssets=False` is NECESSARY for native capture;
defaulttrue caused explicit capture refusal even without mods. NRC/DLSS/RR off;
no sponsor lighting/material/image/quality TOML edits or appearance parity claim.
`RTX_CAPTURE_REMIX_CONFIGS=0` avoids captured machine configuration metadata.

All descendants owned before startup;90s job,100s outer watchdog,128MiB scratch,
2MiB console;private runtime generated extras64MiB/logs32MiB. Frozen507MB release
is input,not capture output. Combined evidence10GB ceiling,128MiB reservation;
reservation refusal worked. Runtime presents120–600 while draining explicit
export-complete marker. Never copy this file polling/wait into SFC callbacks.

## Execution / direct evidence

Ten bounded replay runs retained. First two exported nothing because replacements
were enabled;this is configuration evidence,not Remix geometry incompatibility.
One later-frame capture closed during async export and yielded incomplete USDA;
retained as partial. Added bounded export drain;subsequent captures complete.

Final source-matched cases:

|Run folder under artifacts/d3d9-intercept/runs|Input|Observed result|
|---|---|---|
|20261020-014701-350695|FCA6370tri/58groups,capture96,source frame5363|all groups,corners,primary images match;camera partial|
|20261020-014721-432618|KFF452tri/5groups,capture12,source frame4117|all groups,corners,primary images match;camera partial|

CONFIRMED:all XYZ/normal/UV corner data matches within numeric1e-5;all material
group assignments resolve to original decoded RGBA pixel hashes and dimensions.
USD exporter reverses winding/V convention;analysis normalizes that ONLY for
comparison. Captured input,asset files,D3D9 UVs remain unchanged. Earlier FCA
capture12 also matched;later capture96 verifies a different coherent snapshot.
No live owner-lifetime/multiple simultaneous-ship claim follows from these replays.

CONFIRMED:exported camera view error<=1.90e-5,horizontal projection coefficient
error5.82e-8. USD camera verticalAperture is NOT authored. Raw projection differs
by27.78px(KFF),66.69px(FCA late),67.23px(FCA early). Analysis-only viewport-aspect
reconstruction reduces max point projection error to0.000076/0.000136px.
That corroborates transform/view delivery,NOT a complete independent camera
export or proof the actual rendered output has correct viewport correspondence.
Do not silently repair capture files or tune FOV to hide this omission.

CONFIRMED:actual runtime post-tonemapping screenshot shows the cruiser rendered,
not just a flat fullscreen image/overlay. Original half-float DDS preserved in
archive;an earlier bounded clamped PNG inspection is diagnostic,not fidelity
evidence. No extracted light/secondary-image/appearance parity qualification.

All owned jobs exit0,stop_reason0,remaining_owned_processes0. Final client
device/API refs0. Runtime logs still report common-device disposal warnings:
37 in an earlier KFF run,40 in BOTH final runs. Clean process exit does NOT
resolve these runtime ownership warnings.

## Validation / new native-regression failure

Both finalized C++ variants build /W4 /WX PASS.296Python tests PASS4.214s,
including4new exporter comparison tests. Initial un-escalated suite failed169
temporary-directory permission operations;rerun with scoped normal permissions
passes. Permission failure is infrastructure evidence,not169 code regressions.

Current ordinary Windows D3D9 revalidation fails BEFORE drawing. Final receipt
`artifacts/d3d9-proof/runs/20261020-014807-215394` is PARTIAL;synthetic native log:
`HRESULT 8876086a D3D9_PROOF_FAIL windowed backbuffer compatibility`.
Initial attempt014340-353686 reached CreateDevice and failed8876086c. New
read-only adapter diagnostics identify NVIDIA4070Ti,mode1920x1080,format22,60Hz.
CheckDeviceType rejects windowed HAL compatibility. Window-sizing isolation,
opaque XRGB trial and normal versus constrained system-DLL loading did not
restore it;temporary format/window/loading experiments reverted. Current code
retains strict compatibility diagnostics and explicit system dependency search.
No software-renderer substitution or driver/security/config change.

Cause UNRESOLVED. Environment/display state is a HYPOTHESIS,not confirmed.
Read-only OS query lists NVIDIA plus installed SudoMaker/Sunshine virtual display
drivers;NVIDIA current1920x1200 differs from D3D9 mode. This does not establish
causality. Do not delete/disable adapters or weaken checks. Run69 PASS remains
historical for its source/environment;its receipt is NOT final-source regression
coverage after the common C++ file changed. Normal Remix can use Vulkan while
native D3D9 fails,so one passing path does not excuse the other.

## Files / preservation / disposition

New:`tools/d3d9_proof/build_intercept.ps1`,`run_intercept.py`,
`inspect_intercept.py`,`archive_intercept.ps1`;`tests/test_d3d9_intercept.py`;
this record and curated interception evidence. Modified common`d3d9_replay.cpp`,
`run_offline.py`(combined capture accounting),README,HANDOFF,transition plan and
boundary progress. All earlier dirty implementation/docs/tests preserved.

Ten finished interception payloads recoverably compacted:
303,241,287B ->44,054,283B ZIP bytes,archive/decompressed SHA256 checked before
removing loose generated payloads. Logs/manifests/results/comparison receipts
remain loose;source captures/original images unchanged. Exact generated ZIPs
under the same runs directory recover scene.bin,textures,captured USD/assets
and DDS. No proprietary assets published. Private runtime inputs unchanged.

Accepted/copied client SHA256 unchanged:
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
Four sponsor appearance TOMLs unchanged versus committed baseline. No SFC,
Toolkit,SDKhost or owned bridge/replay left active;no proxy deployed by this run.

Disposition:CONFIRMED normal-D3D9 geometry/primary-image delivery to Remix;
overall second-gate qualification PARTIAL. No formal TRL/milestone/boundary PASS.
Camera export omission,native regression and disposal warning remain explicit.
Presentation/cadence/depth/output/suppression architecture remains unselected.

## Final closeout

PowerShell parser(all five proof scripts),document links and curated JSON/source/
capture receipt cross-checks PASS;git diff --check PASS(line-ending notices only).
Combined counted outputs9,751,389,108B before two tiny failed-native compactions;
two partial fixtures also ZIP-compacted1240B->582B each. Ten bridge ZIPs and all
receipts retained. Frozen release input excluded from capture allowance,not
erased;source capture/client/configuration hashes unchanged.
Git13modified tracked/36untracked individual files,index0,HEAD unchanged,no push.
No active owned process,unfinished export or pending build. Native regression is
the explicit unresolved validation failure,not a clean all-tests-pass handoff.
Fuel usage at closeout54%five-hour/14%weekly remaining;credits available. No
needless work to consume remaining allowance while this gate is partial.

Exact next action:reproduce the native windowed-D3D9 compatibility failure with
display/session state recorded,resolve it without bypassing the plain baseline,
then qualify actual Remix camera/viewport output independently of USD's missing
vertical field before advancing the presentation architecture gate.

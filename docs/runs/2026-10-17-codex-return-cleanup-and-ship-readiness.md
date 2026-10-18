# Codex run — cleanup investigation and one-ship readiness

Run SFC-RETURN-20261017-03,2026-10-17 EDT. Sponsor authorizes investigate,
make edits and proceed to ship integration. HEAD e96765a, existing unstaged
implementation/evidence preserved; no stage/commit. FuelGuard actual-thread
recent-hook attach verified; no daemon/helper/delegation. Authority: approved
return-path plan, HANDOFF and previous runtime review. No requirements change.

Questions: what produces the40-common-objects shutdown warning; can fresh ship
assets be substituted with matching frame/coverage/depth and safe original
fallback? Existing returned-image success is not being re-proven in gameplay.

Starting evidence: REMIX-RETURN-001 runtime053407-630582, pinned SDK source
rtx_remix_api.cpp/register1365 andShutdown1620, d3d9_device.cpp/destructor,
official rtx_common_object.h at SDK commitb81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4;
existing live-scene contract/observer, approved M1 plan/amendment.

Confirmed source fact: warning counts runtime CommonDeviceObject instances still
alive at DLL/process exit, not40game objects nor a byte measurement. Source
Shutdown releases registered device/D3D9; do not independently double-release
SDK-owned pointers. DestroyMesh/Light queue work on command stream. Bounded
hypothesis: explicitly fence queued asset retirement before SDKShutdown may
improve teardown. Test against unchanged host before concluding a correction.

Prepared next offline experiment: same pinned host + native stand-in, add
graceful-stop variant instead of intentional host.kill. NoSFC. First baseline,
then bounded shutdown-fence edit if evidence supports. Existing100s/32MiB caps,
1BMP, same current-user mapping and NRC-off; nativefixture25s. Record exact
results and do not claim warning fixed from source inspection alone.

Implementation/test results,ship-blocking evidence and final state appended
below before handing off. No gameplay or original suppression authorized without
qualified replacement matching/coverage/visibility; successful additive output
is not sufficient to permit hiding original ships.

## Investigation results / edits

Baseline graceful fixture20261017-055203-041542 reproduces exact40-object warning
with no SFC. Both processesexit0,228frames,state_errors0,all5phases. Pinned
[CommonDeviceObject source](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4/src/dxvk/rtx_render/rtx_common_object.h)
lines58-85 corroborate counter/atexit meaning; not byte usage nor ship count.
Registration1365/Shutdown1620 source confirms special SDK-managed release loop;
do NOT copy that loop into client code or independently release stale pointers.

Added bounded5s D3D9 EVENT drain after DestroyMesh/DestroyLight in return_host.cpp,
because these functions queue retirement on CS stream. Correctness hygiene,
NOT a claimed leak fix. Fixture055243-303896 logs HOST_RETIREMENT_DRAINED and
Shutdown0,all5phases/state_errors0, but exact40warning persists. Reject hypothesis
that simply fencing our queued retirement resolves it. Do not repeatedly retry
the same idea or patch runtime internals. Count40 also existed after123.984s
game run; shorter standalone tests show same final count, NOT proof of bounded
memory across an arbitrary mission. Cause still unresolved; carry as explicit
runtime-internal-lifetime risk while continuing bounded integration, not declared
harmless or a technical blocker by itself. No SDK/private Release experiment.

Ship-readiness audit in ship-replacement-readiness.md identifies real next gap:
qualified retained-scene depth/visibility at composition. Pinned SDK exposes
DEPTH/OBJECT_PICKING, but first picking call only enables capture; none is yet
qualified as SFC-compatible coverage/occlusion. Limited ReShade blocks external
application/depth-binding events; supported late overlay remains usable for a
bounded immediate-context read-only descriptor check, not hidden event bypass.
Current semantic30Hz transport is not a synchronized replacement contract.
Existing hook always forwards; no qualified early-return suppression implemented.

Prepared defaultOFF -InspectVisibility workflow: eight late-binding descriptor
observations,>=1s apart, after automatic tactical gate; OMGetRenderTargets,
GetResource,GetDesc only; transient references, no rendering changes/waits/image
copies/readbacks. Optional visibilityVersion1 in reserved v2 bytes144..175;
mandatory256B prefix unchanged. Python classification never calls descriptors
qualified scene depth. Counters included in normal result, explicit limits/mode
in manifest. All original ship rendering remains intact. New mode needs one
minimal sponsor skirmish to answer a question the successful image test did NOT
record; no manual timestamps or RE requested.

### Validation

- build_return_probe.ps1 VS2026 x86/x64 /W4 /WXPASS; native36wirechecksPASS.
- Early optional sampler fixture055602-206056:3samples,0DSV,224frames,allphases,
  original state preserved. Tightened fixture to require all8 before stop.
- Final055648-235716 graceful+inspect:11.906s,8samples/0DSV expected for fixture,
  465frames,state_errors0,all5phases,host/fixtureexit0,error0,READY0. Enabled7430
  greenpixels,disabled0,resized7422,recreated7425,disconnected0. Job6384260B
  includes copied proxy/binaries and oneBMP; below16MiBwarning/32MiBhard cap.
- Full102Python testsPASS1.603s; caught/fixed a newly misplaced default-field
  assertion in test code before final pass (not a runtime failure). Includes
  layout/optional-off and conservative visibility verdicts. PowerShell parsers
  PASS; read-only --inspect-visibility preflightPASS. NoSFC launch this run.
- git diff --checkPASS (line-endingwarning only); no staged files. ClientSHA
  original andcopy unchanged4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
  Final inventory no owned host,fixture,launcher,game or controller left running.

### Files / disposition / exact next action

Modified existing uncommitted return_host.cpp,return_addon.cpp,return_wire.h,
return_channel.py,run_return_fixture.py,run_return_game.py,
start_return_image_session.ps1,tests/test_remix_return_channel.py; updated probe,
contract,HANDOFF; new this run record + ship-replacement-readiness.md. Prior
uncommitted implementation and evidence preserved. Native semantics/hook source,
approved requirements,accepted proxies/client and helper project unchanged.

RETURN PATH DEMONSTRATED remains valid. Ship replacement ADDITIONAL BOUNDED
EVIDENCE REQUIRED; no unsafe suppression implemented. Ready sponsor visibility
check: existing elevated parent runs start_return_image_session.ps1
-InspectVisibility, usual two-ship skirmish, keep both visible briefly, play
normally until two-beep exit. Same triangle sequence expected; no ship changes.
Exact next action is adjudicate those8depth-binding observations before choosing
one earlier capture scope or using any depth for occlusion. Head e96765a,
index empty, changes unstaged/untracked, no stage/commit.

Evidence archive after analysis:
artifacts/remix-runtime/archives/20261017-cleanup-visibility-offline-evidence.zip
(170054B), selected JSON/log/BMP/text from four offline runs above, excluding
copied binaries/dependencies. Original small evidence retained; no deletion.
Final read-only preflight/diff check repeatedPASS, index still empty.

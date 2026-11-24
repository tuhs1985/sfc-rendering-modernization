# UE additive native insertion preparation — November 23, 2026

Working tree: C:/Project/SFC-Modernize Engine, codex/ue-native-insertion,
pushed parent 1834379. Unstaged/uncommitted. This record qualifies standalone
insertion and the prepared launcher, not SFC gameplay or original suppression.

## Implemented boundary

The opt-in live registry now uses SFCGameOutput to capture the selected player,
export a coherent UE colour/depth pair and normalize into the existing native
GPU pool. The original source arrays, UVs and images stay unchanged. The source
service uses the existing unique configured F-CA selector, never encounter order.
A duplicate F-CA is ambiguous; retirement cannot silently rebind a different owner.
The fixed diagnostic translation is (-15.897722721099854, 0, 0) in native world
units, applied in UE only. It does not follow the camera or change source identity.

A discovered layout mismatch required a versioned extension: UE normalization
already positions its tactical crop within a full native-size image. Applying
the legacy camera-surface transform again misplaces that image. Version 4 plus
NativePixelsFlag explicitly requests direct native-pixel sampling. Version 3
and the default compositor argument preserve the existing Remix mapping.
Old version-3-only receivers reject version 4 instead of misinterpreting it.
Pool size, metadata, slot count, queue depth and ownership remain unchanged.

Original capture still precedes Acquire/Commit. The default-off additive hook
returns after successful insertion without zeroing either original list or
recording suppression. No mesh suppression is authorized by this checkout.

## Evidence and failures investigated

- Initial live-output fixture rejected a missing output sequence. Each submitted
  UE packet now carries Producer.Submitted + 1; source sequence remains separate.
- An odd 19x13 native-target regression reproduced 22 misplaced covered pixels
  under the legacy transform; explicit native mapping passes with zero errors.
- Actual source/registry/export/pool replay passes six alternating poses, retaining
  one geometry and 84 original images. Four independent source-image comparisons
  exceed 98.9% colour accuracy within three levels and depth p99.5 error below
  5.8e-7. Original arrays/UVs remain identical; first/last frame content agrees.
- Native effects replay checks all 889,542 pixels over six outputs with zero
  mismatches, including opaque black, far depth-tested effects, near additive
  effects and depth-disabled text. Graphics targets and states restore correctly.
- The first actual coordinator fixture used a D32-typed texture rather than SFC's
  R32-typeless resource with D32 view. The production adapter correctly refused
  commit. Correcting the fixture, without relaxing admission, resolves this.
  Failed attempts remain under gate-01 and gate-02.
- The existing gate event unit test intermittently failed its 2-3ms Sleep/thread
  assumptions within Strict's 16.667ms window. Event/stop/recycle cases now use
  the already-supported ExtraFrame policy; Strict expiry and both 600-frame
  arithmetic comparisons remain tested. No production deadline changed.
- An ad-hoc optimized build of the old standalone replacement Admission test
  fails check 25 with both baseline and changed headers. The accepted C++20
  unoptimized build passes 109 checks. This is not evidence of a new compositor
  regression; the production build configuration remains unchanged.

## Actual native coordinator gate

Shipping and Development were rebuilt with unchanged-source receipts, then run
serially through the real d3d9_game::Receiver Acquire/Commit implementation,
x64 output receiver and separate x86 native fixture. No SFC process is launched.
Both final runs produce 60 consecutive successful commits after initial startup,
zero subsequent misses, zero invalid tickets, zero partial results and zero
suppressed lists. Each checks two changing frames against the leased GPU
triplet, with zero pixel mismatches after ordinary native effects/text.

The final fixture uses 1280x720 RGBA8-typeless/linear-view 8xMSAA colour and
R32-typeless/D32 depth. It rejects wrong cohort, generation, frame and revision.
GPU output reads stay leased until completion. Source stop and UE exit are normal.
The frame loop has a synthetic 60Hz test cadence only; production retains the
existing ExtraFrame gate and no added cadence, wait, prediction or screenshot IPC.

Evidence: artifacts/ue-foundation/native-insertion/gate-shipping-final and
gate-development-final. The final 58 non-readback CPU frame bodies measure:

| Package | Median | p95 | Maximum |
| --- | ---: | ---: | ---: |
| Shipping | 5.582 ms | 6.692 ms | 7.069 ms |
| Development | 7.500 ms | 9.371 ms | 9.544 ms |

These include source publication, native admission/commit and synthetic effect
submission, excluding the fixture cadence. The first two correctness readbacks
cost roughly 176-179ms in the earlier run and are diagnostic-only. Neither these
measurements nor fixture step timestamps establish live SFC presentation/scanout,
startup latency or camera stability. No performance policy was relaxed to pass.

## Regressions and prepared runtime

- UE Python tests: 14; native gate analysis: 9; startup/recovery: 16, all pass.
- Native core: 1,216 checks each x86/x64; cohort wire: 193 each; pinned flush:
  12,300; actual capture/primary-secondary/additive recorder: 111, all pass.
- Corner snapshot/one-use/fresh-copy tests pass. Native capture and return DLLs
  rebuilt; previous DLLs retained in native-insertion/pre-native-layout.
- UE/native identity, target notice and world math pass x86/x64 (2,820 math checks
  each). Actual x64 writer/x86 consumer passes 6,051 GPU pixels and held-slot,
  busy-skip, target-generation and lease-drain cases with current version 4.
- Native component actual-worker/decoder qualification passes. Both source and
  additive launcher preflight are read-only; additive preflight passes current
  executable/profile, package/source/binary qualification and evidence reservation.

The prepared launcher is tools/ue_wrapper/start_additive_session.cmd, using the
existing test copy and transactional parent/recovery workflow. It keeps all
originals, uses the unique F-CA, standard ExtraFrame and current native dimensions.
It requests normal exit after 90 seconds of observed source activity, with the
existing 285-second workflow bound. Detailed gate recording is capped at 8MiB
inside the existing 32MiB logs allowance; required definitions/images are working
files. There is no continuous image recording or new full game copy. The UE
base-texture proof does not claim Remix lighting/material/damage/destruction parity.
Interrupted recovery accepts the explicitly qualified UE-ADDITIVE-001 transaction;
unknown probes or missing qualification remain rejected.

## Next action

Task 4.2 and preparation 4.3 pass; OpenSpec is 19/30. Gameplay 4.4 is pending.
Use an Administrator CMD window:

```cmd
cmd.exe /d /c call "C:\Project\SFC-Modernize Engine\tools\ue_wrapper\start_additive_session.cmd"
```

Enter the usual unique F-CA skirmish. Look for the extra textured player beside
the original. Rotate/zoom, move/turn, switch away/return, expose shields and pause
briefly. Exit normally at the two-beep cue. Review actual commit provenance,
camera misses, shutdown and unchanged protected files before any suppression.

## Follow-up — both first gameplay attempts stopped before capture

Sponsor attempts 20261124-042856-118605-in-game and
20261124-042933-959768-in-game (UTC filenames; November 23 locally) both ended
with Semantic controller exited before tactical gate. The actual controller
exited 2 and printed its argument usage. There were zero source assets/frames,
zero native gate requests and zero insertion commits. Both SFC exits were normal;
proxy restoration, original critical hashes and launcher settings checks passed.
These attempts provide no live rendering verdict.

Root cause: the additive checkout deliberately sets SFC_PLAY_SESSION=0 for gate
timing records but inherited --max-seconds 0 and MaxSeconds=0 from untimed play.
The controller explicitly rejects zero duration outside play mode. The bounded
additive checkout now writes its existing 285-second workflow duration to both
controller arguments and INI. Untimed normal play, controller validation,
render timing/deadlines and the 90-second sponsor cue are unchanged.

A regression first failed on the inherited zero argument. The corrected test
uses the actual installed controller against an impossible odd Windows PID:
parsing reaches OpenProcess and exits 3, rather than usage/exit 2, before any
DLL/target access. No SFC launch is needed for this boundary check.

The failed runs also exposed a cleanup defect: the native scene reader returned
Empty before inspecting a valid same-session stop request when no producer PID
had attached. UE consequently needed forced termination (exit 1). The reader now
honours session-owned cancellation before producer attachment, preserving wrong
PID/session rejection. Focused native tests reproduce the failure and pass on
x86/x64; there is no wire change. Both UE packages were rebuilt. Actual additive
passive cancellation, parent death, relaunch, cancel-before-attachment and
cancel-before-PID checks pass with normal UE exit and no assets/images.

Current Shipping native gate requalification again passes 60 consecutive
insertions, zero post-start misses/invalid/partial results and zero suppression.
Evidence: native-insertion/startup-cancel-shipping, startup-cancel-development
and startup-fix-gate-shipping. UE Python suite is now 15 passing tests.
Task 4.4 remains pending: retry the same CMD launcher. Standalone success and
corrected controller parsing do not substitute for that gameplay checkout.

## Successful sponsor checkout — November 23

UTC-named run 20261124-043925-000700-in-game ended with error=null after
69.797 seconds. Sponsor reports success and visually confirms the correct native
rendering depth. This is live additive UE insertion, not zero-offset replacement.

The retained source service observed 2,510 snapshots, two assets/definitions and
94 original images; the explicitly selected player was owner 2/revision 2.
The native gate recorded 2,703 frames and 2,270 successful commits. All 2,270
requested transactions committed: zero admission timeouts, invalid tickets,
partial results or terminal recovery conditions. Maximum pending gate requests
was one; output occupancy stayed within two slots. The diagnostic ring dropped
no records. Existing source-to-Present timestamps measure median 15.392ms,
p95 16.462ms, p99 16.970ms, maximum 21.037ms. Gate wait median 4.866ms,
p95 6.058ms, p99 8.994ms, maximum 15.941ms. These are callback timestamps,
not display scanout or measured input latency.

There are also 433 no-request native frames, all with entered=0 and sequence=0.
They are not timed-out acquisitions and must not be described as 433 failed
requested replacements, nor ignored when judging future seamless coverage.
The first commit begins 3.569s after the first recorded native frame; startup
and later no-request intervals remain distinct from the successful gate timing.
There are 221 stale output discards. The terminal native-present interval is
about ten seconds; its relationship to exit/menus or pausing is not established.
Before enabling suppression, inspect no-request eligibility under camera changes
rather than claiming this proves uninterrupted replacement or zero load delay.

SFC and UE exited normally (UE exit 0). Controller exit 8 means the game exited
before its controlled-removal step; the controller is no longer running and no
in-process module survives game exit. Proxy restoration, accepted critical files
and launcher settings all pass unchanged. Originals were never suppressed.

Tasks 4.4 and 4.5 are recorded complete for additive checkout/evidence; OpenSpec
is 21/30. Follow-on replacement still needs its own qualification. Sponsor
requested a commit and push as backup, explicitly forbidding merge. Back up
reviewed project source, tests, contracts and run summaries only; exclude local
attachments, unrelated notes, game assets, captures, binaries and generated files.

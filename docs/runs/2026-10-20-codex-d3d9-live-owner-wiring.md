# Run79 — fresh semantic owner wiring (READY FOR SPONSOR SHADOW TIMING TEST)

## Final authoritative result

Offline qualification CONFIRMED; actual SFC contention/timeliness remains untested.
Gate3 CONTINUES. No game image, original suppression or maturity advancement.
The implementation checkpoint below is historical and superseded by this section.

Fresh semantic observations now feed the ordinary D3D9/Remix host, a separate
x86 D3D11 GPU receiver, and an exact current-Present metadata audit. Completion
means receiver GPU acknowledgement, NOT composition into SFC. The native decoder
uses tested arithmetic, not a reinterpretation of the native17word payload.
Model/source labels must match the freshly prepared asset; epochs/revisions,
session, sequence, frame and state hashes must match. Legacy30Hz rows are used
only for fresh asset preparation, never live pose delivery.

Qualification: `artifacts/d3d9-proof/live-owner-qualification.json` pins sources,
binaries and dependencies. Final combined offline fixture:
`artifacts/remix-runtime/runs/20261020-124416-713021-return-fixture`.
Its raw source is explicitly replayed captured data with synthetic frame/time,
not a real-game result. Fresh asset preparation was1.453s;1288 publications,
1288 exact current-Present matches,1289 audits(one startup ineligible),zero
invalid/unqualified/rejected/dropped completions. Normal owned exit, zero
remaining GPU processes, API shutdown0; resize/recreation/state checks PASS.
Offer-to-receiver ACK median11.23115ms,p9512.40374ms,max13.8156ms under the
standalone fixture's deliberate source lead; NOT a promise of SFC performance.

Validation:31native live-owner checks each x86/x64;142inbox checks and100,000
concurrent offers each;64real captured positive rows plus6negative controls,
both architectures matching the Python conversion oracle. Full M1 native build,
capture-worker/throttle regression and return wire/proxy checks PASS.344Python
tests PASS. No-launch prepared-game preflight PASS. Initial corpus included a
legacy frame-zero row: correctly rejected; corpus and broker now explicitly
exclude pre-tactical frame0 without weakening decoder validation.

Reproduction: run `qualify_live_owner.py --execute` only for offline requalification
after source/binary changes. For gameplay use
`tools/d3d9_proof/start_live_owner_timing_session.ps1` through the established
elevated parent. It checks qualification without rebuilding.90s tactical capture,
five-minute prepared workflow,32MiB combined run evidence,12,000audit cap,
four bounded slots and existing asset/image limits remain. First supported owner
only; no saved USD/OBJ/template and no geometry diagnostic hook.

Generated fixture binaries/derived payloads were hash-verified into recoverable
ZIPs; original captures retained. Final fixture archive SHA256:
`7B97ADBC48C4B5947784C4BF83DBE5A6227A778D1EDB95904C47C37C823939AD`.
Fourteen rebuildable compiler OBJ files5,530,725B compressed to1,277,467B in
`artifacts/d3d9-proof/compiler-intermediates-20261020.zip`; every decompressed
hash verified before exact-file removal. ZIP SHA256:
`DFBB720DB5AAE1B79BF1F1D56DBBC49B2A3A3AC9F6407A699DA69EBBB3E1E12A`.
Counted generated evidence9,865,416,746B;128MiB reservation fits10GB.

Limitations: single owner/revision, supported rigid triangle assets only;
in-place deformation unqualified. Model/LOD mismatch is not substituted.
Output stays in a standalone receiver, not the SFC device. Vendor disposal
warning40 and1280x360 layout issue remain open. No appearance TOML changes.
Original and copied client SHA256 remain
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
No staging/commit/push; existing dirty work preserved.

Final checks: PowerShell parsers, receipt JSON, exact source/binary qualification
and `git diff --check` PASS (Git reports only existing LF/CRLF notices).
No active game/owned GPU processes. Final status:19modified tracked files,
68untracked status entries(including directory-grouped entries),zero staged.
New/changed implementation files:live_owner_wire.h,live_owner_decode.h,
live_owner_input.h,d3d9_direct_host.cpp,build_frame_ingress.ps1,
start_live_owner_timing_session.ps1;m1_live_scene.h,m1_component.cpp;
live_owner_timing.py,qualify_live_owner.py,source_timing_addon.h,
source_timing_fixture.h,return_fixture.cpp,run_return_fixture.py,
run_return_game.py,start_return_image_session.ps1,archive_fixture_binaries.ps1;
scene_bundle.py;d3d9_live_owner_tests.cpp,test_live_owner_timing.py,
m1_live_scene_tests.cpp. Documentation: this run, HANDOFF,execution-plan progress,
D3D9-LIVE-TIMING-001 probe and20261020-d3d9-live-owner-prepared.json receipt.
These changes coexist with earlier uncommitted work;no unrelated edits discarded.

Exact next action: sponsor runs the prepared shadow-timing launcher, enters the
usual two-ship skirmish, follows hold/camera/movement cues with both ships visible,
then exits normally on request. Expect NO new ship or changed picture. Review
actual current-frame misses before authorizing any additive composition.

2026-10-20,sponsor authorized wiring after Run78. HEADd29111f7,index0,prior
18modified tracked/93untracked individual files preserved. No helper/agents,
stage/commit/push or SFC launch. Fuel Guard attached through existing trusted
hook;credits continuation authorized. Read HANDOFF,active execution plan,
Run78 and existing semantic/camera/capture/renderer/runner code.

## Engineering decision

Publish immutable raw96word OWNER snapshots immediately at existing validated
semantic capture,BEFORE legacy34ms diagnostic throttle. Do not use that30Hz
diagnostic stream for live poses. First fresh supported asset is prepared outside
render callbacks using its same-capture mesh/resource associations and a validated
owner-table row;NO saved ship template/MOD conversion. Asset preparation row is
recorded separately. Capture geometry hook remains OFF.

New default-off SFC_D3D9_LIVE_TIMING mode reserves10MiB..~11.1MiB in existing
16MiB current-user scene mapping,below12MiBsource timing store. Fixed four432byte
raw-input packets,four72byte completions,12,000x96byte bounded Present audits;
store1,154,688bytes. Session128bits,publication sequence,owner epoch,revision,
source frame,canonical raw state hash,offer/ACK QPC. No source allocation,I/O,
conversion,waits or renderer calls. Worker decodes effective native17word affine
arithmetic and validates source-composed projection outside SFC.

Unused calibration words94/95 carry exact published sequence only in live mode.
Existing row/ABI sizes and source pose/camera fields unchanged. Sequence/hash
ties completion to authoritative current Present row. Conflicting/retired/
unqualified/missing rows fail eligibility;native scene-begin frame tracked
independently so a failed calibration begin cannot reuse an old frame. Failed
offer invalidates that frame. This seals an immutable OWNER observation,not an
entire multi-object engine scene. Original rendering remains untouched.

Native host reuses ordinaryD3D9Renderer plus supported output copy/x86 receiver.
No SDK geometry/Toolkit/OBJ. Emits completion only after receiver GPU ACK.
Present audit checks exact current sequence,frame,owner,revision and raw hash;
future completion not counted timely. NO image is composed into SFC in this test.

## Current implementation/validation checkpoint

Added live_owner_wire.h,live_owner_decode.h,live_owner_input.h,
d3d9_live_owner_tests.cpp,live_owner_timing.py. Modified semantic live observer,
scene-begin callback,source timing add-on,ordinary host,scene bundle fresh-record
preparation and native test build. Native wire25checks each x86/x64 PASS;existing
142inbox checks each PASS. No positive real-row conversion or integrated proxy/
GPU qualification yet;those are REQUIRED before gameplay. A semantic-component
build/native regression process was started;check tool/process state on resume.

Old source/binary-qualified launchers are now stale by design. Do NOT reuse old
source-timing/private-gameplay receipts. All on-disk clients/proxies/security/
appearance files unchanged so far. No actual combined runtime launcher prepared.

Remaining:corroborate native conversion against existing captured raw rows and
Python camera oracle;finish source fixture plumbing;integrate fresh-asset relay
with existing no-drawing runner;run actual-proxy+GPU offline combined fixture,
fault/malformed/current-frame tests,build/regressions/cleanup/hash/budget checks;
then create source/binary qualification and only then expose gameplay launcher.
Preserve raw partials,archive generated payloads within10GB. Last known counted
outputs9,841,731,678B;128MiB reservation was near limit. Do not increase cap silently.

Exact next action:finish offline synthetic source fixture through raw publication,
native conversion,D3D9/Remix GPU output and current-Present audit,without SFC.

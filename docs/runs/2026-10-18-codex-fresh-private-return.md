# Codex run — fresh private return prepared

Run SFC-RETURN-20261018-23;started Oct17,closed Oct18 America/New_York.
Sponsor "go" continues Run22 exact next action. Authority:approved in-game Remix
return-path investigation. **READY for sponsor private timing test;actual SFC
runtime pending.** No on-screen offset ship,original suppression or milestone PASS.

## Baseline / question

HEAD e96765a1a34c15212ed22f11edeb9a708b9fc18d,indexempty,large prior dirty/untracked
work preserved. Read HANDOFF/Run22,triplet/offset contracts,probe/readiness and
current observer/mailbox,camera,SDK host,addon/runner/fixture code. Existing M1
gate history unchanged;requirements not edited. FuelGuard attached actual thread
through recent hook receipt;no daemon/helper/subagents. Advisories did not block
authorized work. No game launched or administrative security settings changed.

Question:can a fresh current semantic owner request actual SDK geometry output
and a game-side component admit it only for the corresponding frame/state?
Engineering decision:qualify on a PRIVATE target first. Late output is omitted,
not pasted over a new pose/HUD. This is the next live timing gate,not another
Toolkit preview or a reason to loosen frame validity.

## Implementation / exact changed files

Added under tools/remix_runtime:

- ship_live_request.h — Command592B/Seed176B/Registration184B and exact binding.
- ship_live_camera.h — explicit native17word conversion and corrected camera.
- ship_live_receiver.h — current same-process guard/private GPU draw/process liveness.
- ship_live_host.cpp — x64 SDK fresh mailbox/asset producer,one source revision.
- ship_live_gpu_fixture.cpp — owned synthetic/native and actual proxy callback tests.
- live_return.py — actual fresh asset worker,provenance,telemetry,qualification guards.
- qualify_live_return.py — bounded four-gate offline runner.
- build_live_return.ps1 — isolated x86/x64 build and native tests.

Added tests/ship_live_request_tests.cpp,tests/test_live_return.py,
docs/reconnaissance/probes/REMIX-LIVE-RETURN-001.md,
docs/reconnaissance/ship-live-return-contract.md,
docs/reconnaissance/evidence/20261018-fresh-private-return.json,this record.
Modified tools/remix_runtime/return_addon.cpp(compile-gated private variant),
run_return_game.py,start_return_image_session.ps1,run_coverage_probe.py(optional
in-memory oracle input,avoids temporarily rewriting fixture manifest),HANDOFF.md
and ship-replacement-readiness.md. No m1_component/controller/observer source
changed this run. Previous dirty source edits remain untouched.

Game addon variant uses allowed existing proxy Present callback,not new engine
hooks or replacement proxy. Public callback ABI unchanged. Source PID/session/
owner/revision/model/source/LOD/current thread,frame,pose and camera validated.
Exact frame equality retained even for stationary states. Interlocked cross-
process mailbox reader is explicitly adjudicated in contract,not an SRWLOCK.
One fresh revision selected;unsupported/changed revisions never substitute assets.
GPU/receiver lifecycle and compiled module pins are separate from on-disk client.

Only runtime initialization creates resources/shaders. Private draw clears its
target,uses existing compositor,restores state and fences before ACK. Producer
liveness checked without wait;pending GPU completion can drain after disconnect.
No callback disk I/O,readback,image conversion or deliberate waits. Normal driver
command-list allocation is not claimed absent. No hot-unload/device recreation
support claim;experimental channel stops safely rather than reopening old handles.

## Investigation findings / rejected hypotheses

1. Initial host session used buffered wide stdout;runner never received startup
   identifier and hit its60s bound. Corrected to unit-buffered ASCII+stage log.
2. Initial cold GPU completion exceeded fixture's2s stationary hold (~28.45M
   ticks in040412 log). Fixture now has explicit <=15s cold qualification phase,
   then defined5s sequence. Production5s GPU/90s tactical limits NOT increased.
3. Picking512pixels arrived but private color stayed empty;depth=-1234 sentinel.
   Added coherent color/depth tests;did NOT call queued draws success. Added
   known coverage fixture's simple sphere light;that alone did not fix it.
4. C opaque material zero initialization left alphaTestType0. Local SDK C++
   helper defaults to7;runtime before/after confirms7 restores color/depth.
   This is CONFIRMED setup correction,not native SFC material/light recovery.
   Only pinned C header compiled;reference source/official links in contract.
5. First proxy callback test actually passed/child0/host0,but harness called
   host's normal stop during proxy teardown an error. Corrected classification
   requires explicit fixture-PASS marker and normal exits,not any early exit.
6. Fixture retirement semantics corrected:reenable precedes final retirement;
   no reactivation of a retired owner epoch. Labels now say private draws stopped,
   not on-screen hiding. Native keys reject a new epoch even with reused pointers.

No repeated broad trace,appearance tuning,helper,texture dump,requirements change
or guessed new native ABI. Actual SFC frame budget remains unresolved by synthetic
held frames;zero real admissions is a legitimate PARTIAL result.

## Validation / tools / evidence

VS2026Community18.7.3,C++20,/W4 /WX,/Brepro;PS7.6.5;Python3.12.14;Windows11Home
build26200,RTX4070Ti/driver617.42 from pinned manifest and actual proxy log.
Direct CIM query denied under sandbox;OSVersion read corroborated26200 instead.
Remix1.5.2x64/SDK0.6.4 pins unchanged;process-local NRC/DLSS/RR OFF. Scoped external
build/GPU execution used where sandbox denied generated library replacement.

Reproduction in REMIX-LIVE-RETURN-001. Native41checks EACHx86/x64 PASS;
Python195tests PASS4.416s(TEMP/TMP=artifacts/test-temp);parser/diff checks at close.
Close checks PASS:both PowerShell parsers,new Markdown links/evidence JSON,
current source/binary qualification,git diff --check(line-ending warnings only),
empty index and zero owned active processes.
Final rebuild reproduces qualification binary pins and read-only private preflight
passes. No gameplay launched by these commands.

Final four fixtures(all current source hashes;under artifacts/remix-runtime/runs):

| Folder | Gate / observed result |
|---|---|
|20261018-042305-359524-live-private|Direct GPU PASS,7.687s,88outputs,65private attempts,22late/mismatch,0failures,maskIoU1.0,2,938,081B.|
|20261018-042313-380163-live-private|Actual copied-proxy callback PASS,8.531s,87outputs,65attempts,22late/mismatch,0failures,child/host0,6,726,112B.|
|20261018-042322-255925-live-private|Slow1.5s PASS,no overwrite while READY;88outputs/65attempts/23late-mismatch,0failures,IoU1.0,9.125s,2,954,456B.|
|20261018-042331-720903-live-private|Owned renderer terminated after initial image;receiver stops admission/drains,fixture0,2attempts,0failures,IoU1.0,7.422s,2,929,024B. Host nonzero is intentional fault.|

Invalid counters28–30 in nominal fixtures are deliberately retired/inactive
snapshots,not unreported corruption. Attempt counters do not prove nonempty
pictures;direct fixture independently verifies visible magenta and exact512pixel
mask. Motion phase advances synthetic FRAME numbers with unchanged geometry;
continuous moving-pose pixel correspondence is NOT claimed. Real callback state
check covers topology;broader compositor state tests remain Run22 evidence.

Generated qualification binds16source hashes/3binaries/four gates,ignored path
artifacts/remix-runtime/deps/live-return-qualification.json,
SHA F2071F768D58EC5D2D7320183DF969A649CD24D043441131741C40E40398EB76.
Stale source/binary qualification blocks game launch. Original return-bin host/
addon and accepted semantic component remain unchanged. Exact new pins in curated
evidence. Runtime contract/hook addresses unchanged from prior semantic map.

All16development/final attempts retained,including failures. CRC-verified archive
artifacts/remix-runtime/archives/20261018-live-private-preparation.zip,
15,179,960B/340entries/56,216,395sourceB,
SHA937908E2F4501C663B3580AC66CB8F3E36EDF690050A2B661045E67A381137E0.
Archive via Compress-Archive of16exact *-live-private directories;PythonZipFile
testzip verified. Raw retained,overall under sponsor10GB allowance. No evidence
deleted. Bounds/logging/raw-volume/cleanup documented before gameplay.

SDK common-object warning40 persists;normal exits do NOT clear it. Existing SFC
54/67warnings not exercised. No actual UI/controls/performance or original exit/
hook cleanup claim for the new mode until sponsor run. Resize/loss/hot-unload and
on-screen ship visibility remain unqualified. No automatic follow-on composition.

## Repository close / exact next action

All7critical files in BOTH accepted/test installations match Run19 after hashes;
clientSHA4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
No active SFC,host,fixture,controller needed for resume. HEAD e96765a,indexempty,
all implementation/evidence unstaged/untracked;no commit,prior changes preserved.
Local ignored inputs/qualification may need restoring from archives in another
checkout;do not bypass missing gates. No tool/server state required to survive.

**Exact next action:**sponsor runs prepared -PrivateShip workflow,enters two-ship
skirmish,follows cues and exits normally. Review fresh admission/timing and normal
behavior before exposing the offset copy in the displayed frame. No image yet.

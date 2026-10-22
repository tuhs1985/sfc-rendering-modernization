# Run74 — standalone x86 receiver for ordinary-D3D9 Remix output

Date:2026-10-20 America/New_York. Status:OFFLINE CROSS-PROCESS SUBPROOF CONFIRMED;
not a live-game claim.
Authority:approved additive D3D9 execution plan,Run73 alternative approval,and
sponsor instruction to resume using available credits until stopped. Fuel Guard
attached exact thread via trusted hook;no new daemon. HEADd29111f7,index empty;
all earlier dirty work preserved,no stage/commit/push. No SFC or Toolkit launch.

## Question and implementation

Can an independent32bit native D3D11 process consume the actual64bit ordinary-
D3D9/Remix color/depth/picking triplet and safely acknowledge its retirement?
No OBJ/USD/template,SDK geometry registration,new translator or runtime patch.

Added output_channel.h,output_producer.h,output_receiver.cpp,build_receiver.ps1,
tests/d3d9_output_wire_tests.cpp and tests/test_d3d9_receiver.py. Modified direct64
host/build/runner and archive pattern only within this bounded proof.

One192byte current-user-SID-only,protected-DACL mapping,unique GUID session name.
Fixed128byte x86/x64 wire contains source frame,owner epoch,revision,source-state
hash,whole immutable scene hash,resource generation,sequence,GPU LUID,dimensions,
legacy shared handles,QPC and FNV integrity check. No CPU pixels in mapping.
FNV detects corruption,not hostile same-user authentication. Legacy GPU shared
handles are not NT handles/ACL-secured textures;mapping restricts handle discovery,
not a claim of malicious same-user isolation. No handle inheritance.

Producer completes D3D9 output before READY. Receiver atomically acquires,opens
GPU resources on matching LUID,verifies descriptors,copies with native D3D11,
waits for GPU completion,and only then ACKs exact session/generation/sequence.
Producer never reuses acquired storage before valid ACK;disconnect/rejection
retires generation and stops output writes while ordinary rendering continues.
Receiver ends before shared resources retire/API Shutdown. One surface set,
6,220,800shared image bytes at960x540;bounded offline staging in each process.

This is deliberately OFFLINE:held snapshots,blocking helper waits,CPU readback
for byte verification,not production scheduling. Never move waits,readbacks,
launches or file access into SFC rendering callbacks. No performance PASS.

## Reproduction and bounds

Build tools/d3d9_proof/build_receiver.ps1 and build_direct64.ps1 with installed
VS2026 x86/x64 tools /W4 /WX. Use pinned1.5.2 runtime/header unchanged.
Run Python tools/d3d9_proof/run_direct64.py --execute --asset 4 --receiver MODE
for normal,slow,disconnect,exit-acquired,stale-ack,invalid. Normal/slow actual
pixels additionally checked with analyze_direct64.py. Original local triplet and
receiver triplet must be SHA256-identical. Readbacks are verification endpoints,
not CPU image transport. Entire spawned tree belongs to bounded_job.

Existing90s owned process/100s outer watchdog,128MiB scratch,2MiB console,
10GB aggregate cap retained. Receiver hard60s lifetime,5s GPU/retirement limits,
producer10s acknowledgement limit. Slow test deliberately delays receiver200ms.
Generated payloads ZIP-compacted with decompressed SHA verification;logs,
provenance,analyses and original captures remain. No game installation changes.

## Evidence / adjudication

Initial041453-816122 normal receiver:all9images byte-identical,all3ACKs,receiver
exit0,output API Shutdown0,owned children0. Initial wire then enlarged from112
to128bytes to bind full source-state/scene hashes;final-source cases listed below.
First build rejected implicit alignment padding under /WX;explicit reserved wire
padding fixed it. No compiler warnings suppressed. Native21wire checks PASS on
x86;24targeted Python tests PASS. Full regressions/final receipts pending.

Runtime common-device disposal warning40persists;exit0 is NOT leak qualification.
Picking0still not owner absence. Full-frustum/half-pixel conventions unchanged.
No multiple-owner picking,frame sealing,live cadence,appearance or occlusion claim.

## Final-source results

All paths under artifacts/d3d9-intercept/direct64-runs,UTC20261020:

|Run|Case|Byte-identical images|Disposition|
|---|---|---|---|
|041655-409053|KFF normal|9|all3triplets/ACKs|
|041716-068789|KFF receiver200ms delay|9|all3triplets/ACKs;no overwrite|
|041736-707394|receiver exits after first ACK|3|generation retired,rendering continues|
|041756-442537|receiver exits while acquired|0|death observed before output retirement|
|041816-196917|wrong ACK sequence|3|ACK rejected,generation retired|
|041835-785024|invalid width1921|0|packet rejected before GPU import|
|041926-172072|larger FCA normal|9|all3triplets/ACKs|

All jobs exit0/ownedchildren0,receiver shutdown codes match expected(1for invalid
packet,0otherwise),output API Shutdown0. KFF normal/slow IoU1;FCA>=.9997397866;
depth errors remain<1e-6. Cross-process bytes identical for all retained images,
not just matching silhouette. Warning40persists across repeated clean jobs;
no resource-growth/leak-free conclusion. These tests do not simulate device loss.

Final host SHA256 EA133B75181D6E1D2C956C72D6738D385DBBBAB73C5CE0914CA4696599B21D18.
Receiver SHA256 E8F9E574EE15B8AACB601DE324EF31C99EA12D0E542BBA35AC7D1DEC5D0435AC.
Per-case result.json binds sources,input scene,pinned runtime and receiver hashes.
316Python tests PASS5.005s;21native wire checks PASS;x86/x64 builds /W4 /WX PASS.
Both original/copied client hashes unchanged at4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
git diff --check PASS;all evidence ZIP-compacted with decompressed hash checking.
Index remains0;no stage/commit/push or game/appearance/security changes.

Gate2 output ownership subproof CONFIRMED;gate overall CONTINUES. No original-rate
timing,source seal/display correspondence,continuous delivery,device recreation,
live owner lifetime or in-game occlusion qualification. Exact next action:test
one-present pose/camera correspondence before sustained scheduling.

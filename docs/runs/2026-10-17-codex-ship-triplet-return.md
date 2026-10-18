# Codex run — coherent three-output GPU return prerequisite

Run SFC-RETURN-20261017-21,2026-10-17 America/New_York. Sponsor "ok go" authorizes
Run20 next bounded return-contract/consumer step. Read newest HANDOFF/Run20,
return wire/host/addon,output host/consumer/coverage probe,SDK pins and tests.
HEAD e96765a,indexempty,prior dirty/untracked work preserved. FuelGuard attached
actual thread;no daemon/helper/subagents/game launch/staging/commit.

## Result / scope

**CONFIRMED OFFLINE:actual64bit Remix color+owner coverage+corrected depth reach
a separate32bit native10_1 receiver as one identity-checked GPU lease.** Two
captured FCAposes120/720,2sequences each,12/12cross-process plane deliveries
byte-identical. ACK/reuse only after receiverGPUcompletion. Slow/exit negative
tests show published1,ACK0,accepted0,no overwrite/no false success. No CPU image
upload or Toolkit. Thin x86consumer loads no Remix DLL.

**Not yet installed in SFC.** Reusable Consumer class produces SRVs and nonblocking
claim/poll;actual game addon/compositor adoption remains next step. Current game,
controller,observer,diagnostic-color return path untouched;original ships stay
enabled. No live deadline/latency proof,original suppression,UI/effects/occlusion
qualification,complete replacement or milestone PASS. See
[contract](../reconnaissance/ship-triplet-return-contract.md).

## Implementation / adjudication

Triplet protocolv2 in independent fresh current-user GUID envelope,extension464B
at512;Key136B. Reuses security/mapping code,NOT the one-color v2 semantics.
Key distinguishes return session from ORIGINAL semantic scene-session/PID,
owner epoch,revision,frame,pickingID,exact-word pose/camera hashes,full source
packetSHA256,viewport,resource epoch and nativeZ convention. FNV hashes are mismatch
identifiers,not cryptographic claims. Canonical packetSHA is same-session capture
identity,not a normalized all-model cache. Captured sourcePID38852 is separate
from actual x86fixturePIDs29904/28244. Fixture expected state is pinned from the
validated capture,NOT pretended to be a current live game request.

Three nativeD3D11shared leases,Remix imports,producerGPU EVENT before READY.
IDLE→RENDERING→READY→READING→IDLE. Reserve BEFORE output writes;no overwrite
until receiverGPU ACK. Changed request during render cancels publication;stale
READY rejected without exposing inputs. Receiver pins opened descriptors/LUID/
epoch;changed resources cannot be accepted through old SRVs. Unsupported handles
or formats fail closed. Legacy KMT handles are not CloseHandle targets. Current
key/frame equality,not1s freshness alone,determines eligibility.

Consumer constructor opens/validates/creates views outside callback. request,
claim,submitted,poll do not wait,allocate,read back,write files or bind graphics
state. Poll explicitly cannot ACK before submitted AND native EVENT completion.
Only standalone test pilot performs private staging/Map byte comparisons. This
test CPUreadback is NOT image transport and must not enter a game callback.
Actual game compositor must still preserve pipeline/UI state and fence its use.

One reusable triplet,not a growing queue;three shared outputs plus existing local
IDdecode target=four output allocations. GPU786432Btriplet at256square. Generic
bounds1920x1080/128MiB,ONLY256square qualified. Resource recreation/resize/device
loss integration not claimed tested by descriptor guards alone. Renderer failure
retains lease/no usable packet;no timeout authorizes reuse while GPU use unknown.

Early developmentv1Wire416B/Key112B succeeded;review identified need for original
source-session/PID,pinned descriptors and explicit submission guard. Added before
final qualification;v2size/version rejects old entries. Development evidence
retained,not silently promoted. Rejected approaches:three independently published
planes,unconditional ACK,old metadata on recycled resources,CPUimage uploads,
new game hooks or modifying the proven diagnostic path merely to make tests pass.

## Files / tools / commands

Added:

- tools/remix_runtime/ship_triplet_wire.h
- tools/remix_runtime/ship_triplet_consumer.h
- tools/remix_runtime/ship_triplet_consumer.cpp
- tools/remix_runtime/ship_triplet_fixture.h
- tools/remix_runtime/build_triplet_probe.ps1
- tests/ship_triplet_tests.cpp
- tests/test_ship_triplet_runner.py
- docs/reconnaissance/ship-triplet-return-contract.md
- docs/reconnaissance/probes/REMIX-TRIPLET-001.md
- docs/reconnaissance/evidence/20261017-ship-triplet-return.json
- this record.

Modified coverage_probe.h opt-in compile flag SFC_TRIPLET_PROBE,run_coverage_probe.py
explicit --triplet/--triplet-fault flags,readiness,HANDOFF. Existing native probe
binary preserved;new producer/consumer under artifacts/remix-runtime/triplet-bin.
Runtime metadata labels REMIX-TRIPLET-001 distinct from earlier coverage probe.

VS2026 18.7.3x64/x86 C++20 /W4 /WX,/Brepro;bundledPS7.6.5/Python3.12.14.
Pinned Remix1.5.2/SDK0.6.4 hashes checked;same NRC/DLSS/RR-off child environment.
Fresh asset/corrected camera from Run19/20. No driver/installation/security edits.
Build/GPU tests via scoped external tool execution;no routine sponsor UAC.

```text
PS7 -NoProfile -File tools/remix_runtime/build_triplet_probe.ps1
python tools/remix_runtime/run_coverage_probe.py --execute --calibration-run artifacts/remix-runtime/runs/20261018-025737-262069-in-game --snapshot 0 --owner 2 --native-depth --triplet
python tools/remix_runtime/run_coverage_probe.py --execute --calibration-run artifacts/remix-runtime/runs/20261018-025737-262069-in-game --snapshot 2 --owner 2 --native-depth --triplet
python tools/remix_runtime/run_coverage_probe.py --execute --calibration-run artifacts/remix-runtime/runs/20261018-025737-262069-in-game --snapshot 0 --owner 2 --native-depth --triplet --triplet-fault slow
python tools/remix_runtime/run_coverage_probe.py --execute --calibration-run artifacts/remix-runtime/runs/20261018-025737-262069-in-game --snapshot 0 --owner 2 --native-depth --triplet --triplet-fault exit
python -m unittest discover -s tests -p test_*.py
python tools/remix_runtime/run_coverage_probe.py --archive <the8exactfolders in curated evidence>
git diff --check
```

Fault commands intentionally return1 and retain expected-fault result,not normal
success. Existing runner raises generic Owned runtime probe failed;stage log
contains triplet child timeout/disconnect and release counters. Do not rerun these
as unexplained failures or treat them as provider denials. No missing user input.

## Evidence / validation

Final56native wire checks PASS on BOTHx64/x86,same464/136layout. Include all
identity dimensions,stale/future QPC,gating,changed request,sourceGUID/PID,resource
descriptor mismatch,overflow,content/handle/dimension bounds and ACK ordering.
184Python tests PASS3.486s,including exact136Brequest/source-session layout and
CLI rejection before launch. Native producer/consumer strict builds PASS.

|Final folder (UTCprefix20261018,localOct17)|Result|
| --- | --- |
|032340-400739-coverage|Frame120,two packets/sixplane hashes exact,host/child0;released2/ACK2/accepted2/IDLE;3.641s|
|032345-254877-coverage|Frame720,samecleanresult;3.610s|
|032349-966322-coverage|Slow6s,published1/ACK0/accepted0/READY at producer abort;expected fault;9.422s|
|032400-524942-coverage|Consumerexit9,same no-overwrite counters;expected fault;3.343s|

Positive SDKphase5frames7/15 yield two fresh three-plane copies;last ordinary
coverage files retain frame15only,not unbounded frame transcripts. Producer-local
GPU/IDdecode checks still pass;final source-frame projections remain qualified.
Receiver independently checks every pixel hash,IDs0/29,finite depth/sentinel and
cannot ACK by polling an unsubmitted event. Reusable resource leases open once,
reused after ACK. Full provenance/logs in each manifest/result/stdout.

ProducerSHA B09705BB561DC2A7A5C28CEEEC77187F40169805E68330057B5946287A271289;
consumerSHA9D57331C91F68F195ED5B310B3629A35A759F3919234B56A5D6B36D1E8CDE2D5.
Old native probeSHA4D6FDA99...unchanged,as are original/copy7critical files and
current calibration qualification. No current source asset was overwritten.

## Bounds / cleanup / final state

Eachrun<10s/<5.42MB,under120s/32MiB(warn16),96rendered frames max. One4KiB
current-user mapping,one3surface lease;no polygon firehose/continuous dumps.
Childownedjob kills only its own fixture on parent abort;no SFC process enrolled.
Nominal child drains/ACKs/closes before source leases release. Faults stop without
claiming successful output;no outstanding packet overwritten. All owned processes
gone at final inspection. Device-recreation/hot-unload real-addon lifecycle remains
future validation,not proven just by terminating a standalone test process.

SDK40common-object teardown warning persists in all positives/faults. Nominal
exit0 !=warning-free cleanup. SFC54/67warnings remain open/unexercised here.

Archive artifacts/remix-runtime/archives/20261018-032516-596505-coverage.zip,
2,009,064B/260entries/43,114,179Bsource,CRCverified,
SHA A00029F1C52FB3A287996D2592EF88ECF97C9BBC653D40A443C7C006DF3DD5A1.
Includes initial4development and final4runs,raw retained,overall<10GB. Generated
binaries/packets/captures/archives remain ignored;curated docs/source/tests versionable.
HEAD e96765a,indexempty,all implementation/evidence unstaged/untracked,prior work
preserved,no stage/commit. No active tool/session required for restart.

**Exact next action:**adopt this receiver default-off in copied game's presentation
path and first measure fresh matched output availability with original ships still
enabled. Prepare/offline-test state/lifecycle handling before sponsor gameplay;
do not suppress a ship based on this offline prerequisite alone. No30Hz stream
assumed synchronized;late frames must fall back to untouched original rendering.

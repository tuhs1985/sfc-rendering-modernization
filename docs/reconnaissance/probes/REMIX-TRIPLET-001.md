# REMIX-TRIPLET-001 — bounded multi-output return prerequisite

Current wire/compositor extension is [REMIX-OFFSET-001](REMIX-OFFSET-001.md),
version3/496B/Key152B. This document preserves the historical version2 prerequisite
and its evidence. Rebuilding now uses the current layout;do not expect old key
files to work or treat the standalone fixture as a current live-game producer.

Offline prerequisite QUALIFIED,2026-10-17:[Run21](../../runs/2026-10-17-codex-ship-triplet-return.md).
Final tripletv2Wire464B/Key136B adds original semantic-session/PID identity;
developmentv1superseded. Two captured poses each transfer2triplets exactly into
separate32bit consumer;slow/exit negatives reject without overwrite. Not yet SFC
addon adoption/live timing/composition/replacement. SDK40warning remains open.
Authority:approved in-game return-path investigation and
Run20 next action. No SFC gameplay,ship suppression or appearance change here.
Question:can actual pinned Remix color/owner-picking/corrected-depth outputs be
transferred as ONE coherent GPU lease from64bit host into a32bit native D3D11
consumer,with exact semantic identity and fail-open rejection?

## Contract / implementation intent

New opt-in triplet protocol,not an assumption that diagnostic v2 means replacement.
Reuse current-user-only GUID mapping envelope/security,independent fresh session;
new explicit magic/version/size extension at byte512 inside4096B mapping.
Three shared nativeD3D11textures(BGRA8/R32F/R32F),one reusable in-flight triplet,
fixed states IDLE→RENDERING→READY→READING→IDLE. No overwrite before consumerGPU
completion/ACK. Metadata carries session GUID,owner epoch,asset revision/content
SHA256,engine frame,pose/camera hashes,viewport,object-pickingID,resource epoch
and nativeZ convention. Identity mismatch/retirement/disconnect gives no usable
output,not a cached previous ship. No claim this alone supplies live frame timing.

Producer owns native shared leases and Remix imports;GPU EVENT completes all
three copies before READY.32bit consumer opens/validates descriptors/adapter and
creates SRVs as future compositor inputs. Poll/claim/finish are nonblocking;only
offline worker/fixture waits for its own tests. GPU EVENT confirms receiver use
before ACK/reuse. Legacy KMT handles canonically32bit,not Vulkan handles or NT
handles to CloseHandle. Unsupported handles/resources fail rather than guess.

No game addon modified until this prerequisite works. Same consumer implementation
is intended for later game-side adoption,not an external desktop-overlay trick.
Current test consumer uses private staging readback ONLY to verify every byte,
not as image transport. Actual image transfer remains GPU-side.

## Test/tool envelope (document before runtime)

Pinned Remix1.5.2x64/SDK0.6.4 pair and process-local NRC/DLSS/RR OFF from
REMIX-COVERAGE-001. VS2026x64 producer,x86 consumer,/W4 /WX,C++20;native consumer
explicit feature10_1. Separate triplet-bin binaries preserve prior probe binary.
Corrected near=b/a from fresh Run19FCApose,original geometry/model/camera.
Same96frame/six-phase fixture;triplet transfer only atphase5frames7/15,where
actual recorded semantic pose applies. Two sequences test ACK/reuse in one session.
Other phases stay producer-side diagnostics,not mislabeled semantic ship packets.

Native unit tests reject identity/frame/camera/pose/revision/session mismatches,
wrong versions/descriptors/handles/dimensions,early ACK,resource reset while leased,
and stopped sessions. Offline paired GPU fixture verifies three byte hashes,
ownerID bits/depth range/background,matching metadata and clean normal child exit.
Fault cases slow/disconnected consumer must not permit overwrite or usable stale
output. Only owned fixture child may be terminated,never an SFC process.

Per run120s/32MiB(warn16),96frames,at mostfour output allocations including
existing local IDdecode target;shared triplet at256square is786432B. Three
verification staging surfaces add786432B,not extra output pool members. Protocol
bounds1920x1080/128MiB reservation;only actually tested sizes are qualified.
Four KiB current-user mapping,one lease,no queues/growing image stores. Retain
only existing bounded coverage planes and summary logs,no continuous images.
Shared resources persist until child stopped and GPU use complete. Existing
SDK40-object warning remains unresolved,not excused by process exit0.

Source/configuration/build/launch and actual results will be recorded in Run21.
Reproduction:

```text
PS7 -NoProfile -File tools/remix_runtime/build_triplet_probe.ps1
python tools/remix_runtime/run_coverage_probe.py --execute --calibration-run artifacts/remix-runtime/runs/20261018-025737-262069-in-game --snapshot 0 --owner 2 --native-depth --triplet
```

Repeat snapshot2. Fault controls append --triplet-fault slow or exit;nonzero host
exit and EXPECTED_TRIPLET_RECEIVER_FAULT result are EXPECTED,not nominal PASS.
No SFC launch command prepared by this probe. See contract for exact wire fields,
receiver-poll behavior and outstanding lifecycle/latency gates.
No routine sponsor UAC/gameplay required;external GPU/build tool execution uses
appropriately scoped existing mechanism,not changed Windows security settings.
Archive exact generated folders with CRC check after adjudication;retain small
raw data under10GB allowance. Nothing staged/committed. Stop after bounded offline
contract/consumer qualification;original SFC drawing remains enabled.

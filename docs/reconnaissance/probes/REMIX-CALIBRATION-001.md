# REMIX-CALIBRATION-001 — contemporaneous ship/camera/native depth

Status: contemporaneous runtime capture DEMONSTRATED in
20261018-025737-262069-in-game (local2026-10-17). Both owners,3paired snapshots,
normal sponsor behavior/exit,hook restore/unload/rollback/hashes PASS. Projection
calibration PARTIAL:close FCA ~98%interior native-depth agreement;distant KFF
too small. Native screenZ matches directly,not previous SDKhalfZ+.5. Derived
SDKcamera depth conversion needs offline runtime qualification;no suppression.
See [Run19](../../runs/2026-10-17-codex-present-calibration-runtime-review.md).
Question: can fresh semantic owner/model/camera observations be paired with the
native depth/color submission without joining asynchronous samples by time?
This prepares measurement, not suppression, replacement or milestone PASS.

## Mechanism / provenance

Reuse LIVE-SCENE-001 semantic entry/wrapper hooks and read-only fresh triangular
mesh/resource capture. Geometry006AB410 hook,private copies,tint and shading
changes remain OFF. Existing30Hz bridge remains unchanged unless the explicit
child-process SFC_REMIX_CALIBRATION_SCENE matches its unique session name.

Opt-in mailbox occupies reserved bytes32768..45111 of the existing16MiB
current-user-only scene mapping. Version1 Snapshot is12336bytes:12uint32 words
(magic314C4143,version1,bytes,engine frame,session4words,row count,reserved3),
then32rows of96words. Separate busy/active LONGs precede it. No new exported ABI,
COM hook or injected game-thread call. Try-lock only: contention drops evidence.
Scene entry starts an empty engine-frame table; validated wrapper observations
populate it BEFORE30Hz throttling. Row47 records the observing native thread;
all other existing semantic fields retain their meanings. Different model,
source,revision,pose/camera or LOD within one owner/frame marks that row ambiguous.
Stale owners do not carry into a new frame. Calibration caps fresh revisions at8
(<=16MiB serialized packets),not the ordinary64revision live-scene envelope.

Default-off depth reader opens the explicitly named same-session mapping before
hook installation. Native candidate-depth draws record current engine frame.
At pre-effects Present require one nonzero,nonmixed engine frame across those
draws and the semantic table; qualified owner observations must originate on
the same native thread as Present. Reject reuse of a captured engine frame.
Check frame again before GPU submission. No nearest-time join and no claim
that an asynchronous worker or30Hz record is synchronized replacement state.

Existing REMIX-DEPTH-001 native10_1 vs_4_1/ps_4_1 reader saves3paired image
packets at >=2/7/12seconds. The worker adds semantic-0/1/2.bin,each12464bytes:
16uint64 stamp words followed by Snapshot. Stamp fields:magic31504353,version1,
bytes,QPC,nativePresent,depthResourceEpoch,engineFrame,drawEngineFrame,PID,TID,
reserved6. QPC/Present/resource epoch exactly equal the paired depth packet.
Fresh asset packet/refs are associated by session,owner epoch,model,source and
revision,with SHA256 provenance. Reusing unchanged rigid geometry across nearby
frames is explicit; in-place deformation is still unqualified.

## Tools / launch / privileges

VS2026 18.7.3,x86 C++17 semantic observer,C++20 add-on,/W4 /WX. NativeD3D11
feature10_1 and pinned full-support ReShade6.7.1.2131/SDK API18; existing
REMIX-DEPTH-001 and REMIX-RETURN-001 dependency/isolated-copy hashes apply.
Bundled Python3.12.14 and PowerShell7.6.5; WindowsPowerShell5 entry forwards
without changing system execution policy. No Remix/Toolkit process is needed.

Prepared launch (ONLY after all offline qualifications pass):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\remix_runtime\start_return_image_session.ps1" -Calibration
```

Use existing elevated parent; no new UAC prompt or security-policy changes.
Runner refuses existing SFC processes,checks exact copied executable path/hash,
temporarily swaps ONLY copied proxy/config under verified rollback,prepares
scene channel before launching copied SFC. Uses full semantic component INSTEAD
OF duplicate tactical gate hooks. Named tactical event starts20s depth window;
observer controller stops/restores/unloads24s after gate. Original draws continue.

Sponsor:enter ordinary two-ship skirmish;keep both visible and hold camera still
initially. At single cue after5s make one SMALL camera movement then hold still.
Wait for double exit cue after collector/controller cleanup,then exit normally.
No timestamps,pointers,RE work or appearance change expected.

## Bounds / hazards / cleanup

3image pairs,64MiB raw+derived images (warn32MiB),32MiB ancillary evidence
(warn16MiB),96MiB run cap;300s prepared workflow including builds. Calibration
sidecars total37392bytes. Shared mapping remains16MiB/four2MiB acknowledged
slots/32owners;8asset revisions maximum; ordinary state2700records/owner and
16MiB detailed state cap. Same-process reader copies a fixed12KiB table ONLY
for eligible snapshots; native draw only performs a nonwaiting frame query.
No continuous image dumps,unbounded transcripts or GPU screenshots as transport.
This workflow is not capable of a geometry multi-GB firehose; older broad-mode
2GB capability remains separately opt-in and must NOT be combined here.

Writer/storage allocation and asset serialization remain outside render
callbacks. Three existing bounded GPU-to-CPU image copies occur at Present;
not performance-neutral or a production replacement synchronization contract.
Thread/frame mismatch,ambiguous owners,resource limits,missing assets or rejected
source formats produce PARTIAL and retain original rendering. Do not loosen
validation to force a result. Reference-count warnings67(native SFC) and40
(separate Remix SDK host) remain open; normal exit is not proof they are resolved.

On success controller drains callbacks/restores hooks/stops worker/unloads before
exit cue. Native addon retains its own mapping handle until runtime destruction.
After normal game exit collect worker files,restore copied proxy/config,check
both installations and launcher settings. On failure do NOT kill SFC or unload
live hooks;request normal exit and use existing verified interrupted-run recovery.
Archive useful evidence with CRC verification;do not delete originals or raw
evidence silently. No staging/commit.

## Offline reproduction / adjudication

Build existing return and M1 components;native22check mailbox tests exercise
contention,ambiguity,frame rollover,reuse,inactive/malformed session. Existing
producer tests explicitly exercise pre-throttle calibration and worker drain.
Run tools/remix_runtime/qualify_present_calibration.py --execute for bounded
owned10_1 GPU fixture (30s native timeout,1MiB GPU fixture output) plus10s producer
regression. Synthetic IDs/transforms here are transport tests,NOT ship evidence.
Run169Python regressions and current-source positive/negative native proxy/depth
fixtures;refresh offline qualifiers before gameplay. Qualifications pin both
component/addon SHA256 and source hashes. Full semantic DLL uses /Brepro for
repeatable deliberate builds;prepared runner uses its qualified prebuilt binary
and fails closed if missing/changed,avoiding a full observer-suite build at launch.

Read semantic.analysis.json alongside depth.analysis.json. Complete capture
provenance does NOT establish matching projected ship pixels or retained-scene
occlusion. Next analyze fresh composed projections against native depth per
sample/viewport; account for foreground objects andMSAA before suppression.

Documentation timing: initial implementation/unit fixtures preceded this new
runbook entry; their exact commands/results are retained in Run17. This entry is
created before any new gameplay;no undocumented sponsor procedure is required.

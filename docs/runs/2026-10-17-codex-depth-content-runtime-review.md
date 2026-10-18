# Codex run — tactical depth contents verified

Run SFC-RETURN-20261017-15,2026-10-17 EDT. Sponsor completed corrected depth run
and reports "done,no issues on my side". Analyze only,no new gameplay or rendering
implementation. FuelGuard actual-thread hook attached,no daemon/helper/delegation.
Starting/final HEAD e96765a,indexempty,prior dirty work preserved,no stage/commit.

## Result / confidence

**CONFIRMED: the discovered native depth resource contains a visible ship
silhouette and tactical grid spatially matching paired SFC color images,
including a changed camera view.** This is useful tactical depth content,not
merely a bound resource descriptor. It is not proof of complete scene coverage,
native owner identity,Remix depth compatibility or safe original-ship suppression.

Read HANDOFF,REMIX-DEPTH-001,Run14 qualification and actual runtime manifest,
result,depth-status/analysis,three original packets,PNG comparisons and cleanup
logs. No settled semantic seam or renderer architecture question reopened.

Actual artifacts/remix-runtime/runs/20261017-190353-769314-in-game,PID20528.
Requested20s tactical window;50.172s whole prepared run. Completed3pairs,
issued3,no GPU/I/O errors,no ambiguity,no abandoned pending readback. Reader
ps_4_1,actual feature0xA100(10_1),source1920x1080/R32_TYPELESS39/8samples,
paired color1920x1080/RGBA8format28. Failure stage0/HRESULT0. Native reader
DLL unchanged from qualified5B32A337865F5D92BB7D00AF8E059597C1B48B125166585D8BB60B8663596F02.

## Exact packets / content adjudication

|Packet|Present|QPC (frequency10,000,000)|Offset from first|SHA256|
|---|---|---|---|---|
|depth-0.bin|724|163427954808|0s|E6D799954F361D25E8631A786F4DD4FFFD643910D354E5F8DD8A9275E5ABEF29|
|depth-1.bin|1024|163477945905|4.9991097s|8CC50908094FB0921700D07E882476303274C019042C5357D730214E879F9BF6|
|depth-2.bin|1324|163527958957|10.0004149s|8DB03F9F94A82A45DC4A7AE17D555C9487AFB509B861BA7744D519CE85E1F472|

All resource epoch1,768B header+float4 depth+packed color,16,589,568B each.
Zero nonfinite,out-of-range or sample-order errors. All planes span finite
depth approximately.96703756..1 across this run. Min-depth pixels below
1-1e-7:42,444 /36,433 /29,112,respectively. No distance linearization assumed.

Directly viewed all three depth-N-color.png/depth-N-min.png pairs. Visible ship
near preview(x530,y415) in first/second image appears near(x530,y265) in third;
depth silhouette moves correspondingly. Tactical grid horizon also changes
consistently. No depth silhouettes of the HUD/cursor or nebula visible in these
three diagnostic views;do not generalize this to all effects/UI or claim their
draw order. Only one clearly resolved ship is visually adjudicated here;second
ship visibility/owner identity not proven by these snapshots. No distinct-enemy
coverage claim despite the usual two-ship fixture.

Important display detail:raw depth samples every second source pixel(2x,2y),
while existing PIL nearest half-size color derivative selects pixel centers
(one-source-pixel sampling-phase difference). Visual correspondence is clear,
but do NOT claim pixel-exact mask registration from the PNGs. Original full
color and raw depth remain available for exact-coordinate comparisons later.
No UV/geometry/orientation or original image was repaired for this review.

## Static native depth-state observations

At third packet,cumulative selected-DSV original draws have four state sets:

|flags|Depth enable|Write mask|Compare enum|Draw observations|
|---|---|---|---|---|
|257|yes|ALL|8 ALWAYS|720|
|256|no|ALL (not proof of writes while disabled)|2 LESS|2,215|
|257|yes|ALL|4 LESS_EQUAL|80,761|
|1|yes|ZERO|4 LESS_EQUAL|856|

Stencil disabled,reference0 throughout these rows. Native state descriptors plus
real nonuniform depth pixels corroborate meaningful depth use. Counters do not
identify ships versus grid/effects or prove every observed draw wrote depth.
Eight samples are read,only sample0/min/max/mean retained;this is not lossless
per-sample coverage. A shared projection/distance convention with Remix remains
unqualified;these normalized nonlinear values cannot blindly compare to another
renderer's output.

## Behavior / cleanup / bounds

CONFIRMED sponsor observation:no issues on sponsor side during run. Independent
mechanical evidence:normal game exit,launcher CHILD_EXIT code0,gate-controller2560
exit0,hook bytes restored,gate DLL unloaded,host exit0,proxy/config restored,
original critical hashes and launcher settings unchanged. No Remix renderer or
ship suppression in this test. Both client SHA256 remain
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29;
copied proxy E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7.

Native warning persists verbatim:
`Reference count for ID3D11Device0 object 07FD6168 (08B69F4C) is inconsistent (67).`
Normal exit is not warning-free internal cleanup;unresolved,not a quantified leak.

Raw packets49,768,704B;raw+15PNG derivatives50,700,037B (~48.4MiB),below64MiB.
Whole run55,682,889B,below96MiB;32MiB warning expected,NOT capture failure.
No repeated-frame dumps beyond three scheduled pairs. Archive
artifacts/remix-runtime/archives/20261017-depth-content-runtime.zip:
5,136,753B (~4.9MiB),31entries,50,847,151Bselected source,CRCverified,SHA256
6B0DBE067C807BF5E21ABE97C4279BFE4DEB523948741887C19BCD38439208F7.
Raw retained under allowance,no deletion. Source originals and raw run/result
remain unchanged;pending sponsor field in raw result is superseded by this
curated record,not rewritten retrospectively.

## Reproduction / validation / changes

Runtime entry was established elevated parent:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\remix_runtime\start_return_image_session.ps1" -DepthSnapshots
```

Offline packet validator:tools/remix_runtime/depth_snapshot_analysis.py
read_packet() for each exact depth-0/1/2.bin. Check hashes,counts,finite/order
metrics;relative time=(packetQPC-firstQPC)/result.final.qpcFrequency.
Depth pixel statistic=np.count_nonzero(depth[:,:,1] < 1-1e-7).
Native state table is snapshots[2].native_depth_states in existing analysis.
Archive via archive_broad_evidence.py <exact-archive> <exact-run>.
Existing display derivatives generated by approved runtime analyzer;not recreated
or edited to improve apparent agreement. JSON parsing,packet validation,archive
CRC/current hashes and git diff --check PASS. No code changes/native rebuild
needed for this evidence review. No active game/fixture/host remains.

Changed only this new record,curated runtime evidence,HANDOFF,probe result and
readiness summary. HEAD e96765a,indexempty,unstaged/untracked existing/current
work preserved. No staging or commit.

## Exact next action

Offline-qualify selected-ship Remix output coverage/depth and its coordinate/
projection relationship to this paired SFC depth/color evidence,before implementing
owner-specific suppression. Need fresh asset/camera/frame provenance contract,
not the asynchronous30Hz preview stream assumed adequate. Existing return-path
plan still governs;no new runtime test prepared here. Do not repeat broad tracing,
claim complete depth/effect coverage or turn this result into milestone PASS.

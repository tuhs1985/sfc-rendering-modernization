# Run78 — immutable input and deliberate-stall recovery

2026-10-20 America/New_York. Result:OFFLINE INPUT/RECOVERY DEMONSTRATED;
Gate3 CONTINUES,live source binding/sealing and simultaneous SFC load unqualified.
Authority:sponsor agreed newest-frame scheduling and authorized autonomous
testing;approved additive execution plan/Run77/handoff. No SFC launch or sponsor
action required in this unit. No original suppression,architecture change,
prediction,buffered game frame,appearance adjustment,helper or agents.

## Starting state

HEADd29111f7a513c4510c4d33aeeda2c355d98443a5,codex/github-sanitized,index0,
18modified tracked/82untracked individual files. All earlier changes preserved.
Fuel Guard exact-thread attach via healthy recent hook,no sandbox daemon started.
Read canonical handoff,active execution plan,Run77,neutral scene/output contracts
and existing host/receiver/ownership code before implementation.

## Implementation

[Input contract](../reconnaissance/d3d9-frame-ingress-contract.md) defines the
experimental296byte OWNER packet and1,344byte four-slot inbox. Bounded nonblocking
CAS ownership,immutable copied state,monotonic sequence and newest-acquired
selection;never overwrite Reading/Writing slots. State/content checksums,finite
matrices,exact expectation/deadline admission and explicit ineligible lifecycle.
No on-disk or in-process SFC modification. This is NOT a new production source
protocol nor proof that the engine has sealed a complete scene.

Native x86/x64 tests and actual private-mapping x86producer/x64consumer fixture
exercise normal,slow,disconnect,malformed and stop. GPU host adds default-off
--latest-input and --inject-lag-ms0/35/60. Reuses exact normal D3D9 Renderer and
output API/receiver;independent source thread cycles three recorded FCA poses
at synthetic60Hz. No OBJ/USD/SDK geometry,no CPU image transport. Source thread
continues while renderer stalls;old input is skipped rather than accumulated.

Early /WXbuild correctly rejected implicit alignment padding. Added explicit
wire padding,retained all layout assertions/warnings. Code review caught a
pre-acquisition clock race:concurrent offer may legitimately occur after the
consumer's entry clock. Removed that false invalid classification;final timing
admission still rejects future/expired output. Replay asset hash refined from
whole bundle label to decoded geometry/group/image content,excluding frame state.
Earlier successful prototype runs053316-480026 and053415-047443 retained under
their actual sources/binaries,not relabelled as final-source validation.

## Final native / cross-process evidence — CONFIRMED

142native checks per architecture PASS,including100,000concurrent publications
each. Final stress received98,910x86/98,135x64,invalid0;not a source-rate benchmark.
Final private-mapping cases under artifacts/d3d9-proof/ingress-runs:

|Case|Run suffix after20261020-|Received|Last source sequence|Finding|
|---|---|---:|---:|---|
|Normal|053537-256360-normal|184|240|All final state reached;obsolete skipped|
|Slow35ms|053537-972457-slow|13|230|13late completions rejected by admission;expired final work discarded|
|Disconnect|053538-535546-disconnect|49|60|Owned producer exits0;drains safely|
|Malformed|053538-741597-malformed|204|240|Exactly1invalid injected packet rejected|
|Stop|053539-332766-stop|10|10|Stop reaches source;exit0|

All guarded parents0/remaining owned0. Current-user protected ACL explicitly
created;source executable architecture verified32bit,consumer64bit. These are
synthetic states with epoch/revision/content changes,not real SFC retirement.
Ready-slot replacement is not included in consumer-obsolete counters;source
sequence gaps are explicit. Never infer "all updates consumed" from invalid0.

## Final actual GPU/input recovery — CONFIRMED within offline scope

artifacts/d3d9-intercept/direct64-runs,1920x1080,FCA runtime-captured asset3,
original primary images,one initial warmup then one Present per consumed input.
All costs include GPU output completion and independent x86 receiver GPU ACK.

|Case/run|Consumed of300|Late completions|Median ms|p95 ms|Max ms|First timely sequence after injected75|
|---|---:|---:|---:|---:|---:|---:|
|0ms/053644-865593|300|0|10.0281|10.530775|11.0735|Not injected|
|35ms/053706-942518|299|3|10.0333|11.04393|46.0199|79|
|60ms/053728-970432|297|2|10.0302|10.55796|70.0658|79|

35ms:late75,77,78;one expired input.60ms:late75and82;three expired inputs.
Sequence79was timely in the60ms case,but82later missed separately(~16.03ms
completion against a shorter remaining budget). Preserve that miss;do not claim
permanent flawless recovery or exclude it as an outlier. Last input300reached
both cases,source-late/invalid0,no accumulating FIFO. No per-frame CPU image
readback;timing-only is NOT same-run pixel verification.

These are actual GPU runs with synthetic independent demand,NOT a live SFC
source nor simultaneous GPU contention. Late outputs were copied into the
offline receiver's cache and marked late;NO onscreen presentation existed.
Admission rejection is tested separately,not claimed installed in a compositor.
Existing contiguous output transport sequence remains distinct from source
publication sequence,explicitly recorded in CSV;live key binding remains open.

Default (non-latest) pixel regression053840-137605:one1080pFCA snapshot,all3GPU
images byte-identical cross-process,maskIoU1,depth error1.5770470580545037e-6,
4,059covered colors. No change to oracle acceptance. Picking now has multiple
opaque runtime values,including0on374covered pixels;still NOT semantic owner IDs.
All6GPU jobs clean exit0/remaining0/APIShutdown0. Runtime warning40persists;
not leak-qualified. Unsupported1280x360layout remains rejected by default.

## Reproduction,validation and bounds

Bundled modern PowerShell/Python,VS2026Community /std:c++20 /W4 /WX /O2 /Brepro.
Same pinned Remix1.5.2/header0.6.4,driver/GPU and captured inputs as Run75.
Exact per-GPU-run source/executable/dependency hashes in result.json/scene.json.
Final hostSHA256 A0CBCF736108FD9164FA6F84218B44C19BC7A2D847FE6AAE74B42D12764A63B8.
Fixture x86SHA25657537EBF499504536772B1878C58D28818361AAA9EAF5A0E820AEB9DBC2448D9;
x64SHA2562E5F3E8DA3017426F3F243F137CF7364BD94D19CF330FF84645806E047062898.

```powershell
pwsh -NoProfile -File tools/d3d9_proof/build_frame_ingress.ps1
pwsh -NoProfile -File tools/d3d9_proof/run_frame_ingress.ps1
pwsh -NoProfile -File tools/d3d9_proof/build_direct64.ps1
python tools/d3d9_proof/run_direct64.py --execute --asset 3 --receiver normal --paced-frames 300 --timing-only --latest-input --inject-lag-ms 35 --output-size 1920 1080
python -m unittest discover -s tests -p "test_*.py"
```

Repeat GPU cases with lag0and60. Standalone input fixture guard15s/8MiB scratch/
1MiBconsole/native5s progress;GPUguard90s/128MiB scratch/2MiBconsole/outer100s.
Fixed four input slots,300source updates;output surface pool unchanged.
338Python tests PASS4.439s,including4new schedule-analysis checks. Native142x2,
five final process fixtures,three final GPU timing cases and default pixels PASS.
PowerShell parser/diff/client hashes/status checks pass. No game-side native
rebuild or old source-timing qualification invalidation.

128MiB reservation initially prevented more GPU runs at the10GB boundary.
Used existing exact-path archive guard,not raised cap or deleted evidence.
Six finished runs'generated inputs/readbacks177,403,328B->10,107,000B recoverable
ZIPs,decompressed SHA256 verified before exact-file removal. Source captures,
manifests,PNGs,logs,CSVs,analyses and original assets unchanged. Counted outputs
9,841,731,678B/10GB after archive. All owned processes exited. No security,
proxy/install or sponsor appearance TOML changes. No source capture was removed.

## Files and next action

Created:frame_ingress.h,ingress_replay.h,frame_ingress_fixture.cpp,
build_frame_ingress.ps1,run_frame_ingress.ps1,d3d9_frame_ingress_tests.cpp,
analyze_ingress.py,test_d3d9_ingress_schedule.py,input contract,this record,
curated receipt. Modified existing direct64host/runner for DEFAULT-OFF offline
mode,HANDOFF and execution-plan progress. No new SFC hook or runtime runner yet.

Next smallest action:bind actual fresh raw semantic owner snapshots to immutable
publication and qualify conversion/current-Present identity/conflict/retirement
invalidation offline;no assumption that scene counter seals a frame. Then prepare
the combined no-drawing SFC/renderer timing test. Cannot infer success from two
separate tests. No sponsor input needed until that prepared gameplay fixture.
No prediction,buffered native frame,original suppression or image wiring yet.

Final HEAD unchanged,index0,18modified tracked/93untracked individual files,
all Run65–78 changes unstaged/uncommitted,no push. Canonical HANDOFF updated with
this checkpoint;previous entries preserved. No active session must survive.

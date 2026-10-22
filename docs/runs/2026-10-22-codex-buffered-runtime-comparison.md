# Run109 — corrected buffered SFC runs, recording-associated timing difference

2026-10-22 America/New_York. Sponsor reports two corrected-buffer runs: first
stable with minor flicker on camera switches breaking line of sight; second,
with NVIDIA recording, no noticed camera-switch flicker. Read HANDOFF,Run108,
both actual manifests/results,source/audit/worker timing,controller/native
summaries and current timing definitions. Fuel Guard recent hook confirmed.
Diagnosis/documentation only;no source/config change,newgame/helper/agent/stage/
commit/push. HEAD0fc1300,branchcodex/github-sanitized,indexempty;priorworkpending.

## Direct evidence

| Recorded run | First:042446-565057 | Second:042653-754380 |
| --- | --- | --- |
| Sponsor recording description | Not recording | NVIDIA recording |
| Paired ship frames |5382|5395|
| Frames advancing without extra ship |24|5|
| Warmup records |2|4|
| Audit records / dropped / failed |5408 /0 /0|5404 /0 /0|
| Consecutive missing clusters / longest |23 /2records|4 /2records|
| Overwritten / worker releases |0 /5382|0 /5395|
| Pool busy / stale / invalid |0 /0 /0|1 /2 /0|
| Expired fresh-input admissions |22|2|
| Source-to-Present lead median |15.189ms|15.212ms|
| Saved complete scene age median |16.6665ms|16.662ms|
| Input offered to output/peer completion median /p95 |10.620 /14.179ms|6.854 /8.119ms|
| Render-output interval median /p95 |9.305 /12.776ms|5.6465 /6.902ms|
| Renderer output ready wait median |8.780ms|5.175ms|
| Actual query-sleep duration median |540.03us|543.44us|
| Query polls median |17|10|
| Postprocess median |491us|486us|

Run roots are `artifacts/remix-runtime/runs/20261022-<run>-in-game`.
Timer summary calculation:Pythoncsv/struct readers on saved `gpu/frame-timing.csv`,
`gpu/live-input.csv`, `source-timing.analysis.json` and bounded
`D3D9-SYNC-BUFFER-001.bin`;median via statistics.median,p95 sorted floor
index0.95*(n-1). Exclude first frame-timing bootstrap row. Missing clusters count
contiguous status2records,not inferred physical display duration or camera labels.
Source analysis uses selected owner2 profile. Fractions of eligible paired+missing
records:99.556% first,99.907% second. These are NOT subjective visible-success
rates; sponsor did not notice the five omissions in the recorded run.

Audit SHA256first
`7421c9564ab3f47552c235d6790ad1413317666205c3b49f56ba69d5a719c58f`,second
`ae18aee836e6b5e95b2f4b1e0af01b6156061bb81144042814fd38343c594202`.
Both raw audits pass exact saved-frame/session/sequence/hash validation with
owner2/revision2,zero reset/invalid/retired/resource_failed/depth_missing. Asset
retained,generation1,ACK1,reject0,no new binding. Second native summary:two
admitted objects,14388poseupdates/publications,zero rejects/failed updates,
two total asset captures/transfers,stoppedtrue. Offscreen_updates7193is a
counter also including later-visible-this-frame objects,not independently
measured hidden-object count. No visibility-triggered asset reload indicated.

Return and semantic build hashes match between runs;runtimeconf SHA256both
`BE2DD857F49F7166D3A5C4CCE1603C4EA7B73977030A5B647C813CD25F432558`.
Frozen lighting hash also matches. No code update between these two tests.

## Confidence and remaining uncertainty

CONFIRMED:constant alternating-frame regression is absent on both corrected
actual runs. Sponsor reports major improvement;second recording-associated run
has fewer omissions and shorter measured completion intervals. Source lead and
one-frame history age are almost unchanged. Query sleep duration and postprocess
time are similar;fewer polls correspond to earlier observed output readiness.

These are CPU-observed elapsed rendering/output/wait intervals,NOT timestamp-query
measurements of GPU-only work. Recording state is sponsor-reported,not machine-
instrumented. STRONG HYPOTHESIS:remaining omissions are delivery/readiness timing,
not model retirement/reload. Recording may influence GPU power/clocks,scheduling
or presentation behavior;alternatively run order,warm state/background load and
different gameplay could contribute. Those specific mechanisms are SPECULATIVE;
no GPU clock/power,encoder or OS scheduler telemetry captured. No causal claim
that recording stabilizes the integration and no requirement to keep recording.
No inference that query timer granularity improved;observed sleeps are similar.

No complete seamless PASS:24/5missing records remain and controls/rendering
normality not re-questioned beyond sponsor's stated overall impressions.
This is a useful corrected-buffer actual runtime result,not aggregateTRL or
original-ship replacement completion.

## Exit, bounds and retention

First run:normal game/renderer exit,critical client/config hashes andproxy
restoration PASS,but game exited BEFOREcontrolled removal. Controller8,
`Target exited before controlled component removal.`,native final summaries
absent. Rendering evidence remains useful;controlled unload NOTPASS.

Second run:errornull,normal game/rendererexit,controller0,removed/restoredhook
bytes andunloadedtrue;nativeworkerstopped,persistentstopped,trueclient/config/
proxychecks. Both rawrecordcounts<8192,dropped0,worker/log output bounded.
Maximumsceneage17.819/21.452ms,below50msexpiry. Noactiveownedgame/host/receiver.
Original/copied executable SHA256 retained
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.

Second completed game's196generatedinputcopies recoverablyZIParchived after
decompressed hash checks using existing `archive_fixture_binaries.ps1
-CompletedGame`;rawpackets/logs/results retained. Archive
`artifacts/remix-runtime/archives/20261022-042653-754380-in-game-generated-inputs.zip`,
4,628,935bytes,SHA256D4B540E9C7981DB2B35D4238592B050D7D2D61BC4E21FD8A8A89F53AA84BB89D,
77,337,848generatedbytesremoved,recoverable. First partial run notpassed to
completed-gamearchiveworkflow;retained unmodified. Artifacts12,715,585,110bytes
<authorized20GB. No recording media copied into repository.

Files changed:this run,curated comparison JSON,new HANDOFFcheckpoint. Fast
validation:rawaudit/CSV/manifest/hash/controller/native summary review,JSON and
referenced paths,gitdiff whitespace/status. Sourceunchanged,allpendingwork
unstaged/uncommitted on0fc1300,indexempty.

Exact next smallest action:use these existing worker input/output timestamps
to localize residual readiness misses before authorizing another change;do not
make NVIDIArecording a workaround requirement or repeat asset/position discovery.
A causal recording experiment would require controlled same-session toggling
and GPU/scheduler telemetry,not a conclusion from one sequential pair.

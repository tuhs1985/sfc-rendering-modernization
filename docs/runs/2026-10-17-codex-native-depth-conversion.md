# Codex run — qualify native-depth conversion through actual Remix

Run SFC-RETURN-20261017-20,2026-10-17 America/New_York. Sponsor "go" authorizes
next offline correction test from Run19. Read HANDOFF,Run19,coverage host/runner/
tests and REMIX-COVERAGE-001/coverage contract. Starting/final HEAD e96765a,
indexempty,prior dirty/untracked work preserved. FuelGuard actual-thread hook
attached;no daemon/helper/subagents,new SFC session,staging or commit.

## Result

**CONFIRMED standalone:the derived SDK camera correction matches native SFC
screen-Z through actual Remix GPU depth and object coverage.** Three captured
FCA poses replayed:mask IoU1.0 in all3,median depth errors1.65e-7/1.65e-7/4.32e-7.
Same-pose uncorrected control preserves maskIoU1.0 but reproduces0.0123745depth
error and fails native-depth criterion. This discriminates the actual runtime
camera setting,not merely CPU arithmetic or a visual artifact.

No original suppression or replacement,multi-output live transport,visibility/UI
qualification or milestone PASS. Run19's remaining~2%native depth discrepancies
and distant KFF insufficiency remain unresolved. Standalone256square SDK grid
is NOT the original1920x1080/8MSAA grid;agreement here is against independently
projected native composed matrix of that same captured state. Run19 supplies
the separate direct native-depth corroboration. Do not conflate these comparisons.

## Minimal implementation / decisions

Only tools/remix_runtime/run_coverage_probe.py extended with opt-in
--calibration-run,--snapshot0..2,--owner,--native-depth. Source capture sidecars
are revalidated for same session/PID/owner/model/source/revision;native depth and
semantic SHA256,frame/Present/QPC,asset identities retained in each manifest.
Use freshFCArevision2 packet6e752e8833239650548e51bf62fc128d08cc00a8241ce9174a2f9f3ccd5b24cf,
not old saved Toolkit model. Asset capturedframe4,poses120/420/720;rigid reuse
explicit,in-place deformation not qualified. First two FCA pose/camera states
identical;three captured frames do not mean three independent motion conditions.

Keep native M,XYcamera/basis,FOV,far and geometry unchanged;set only SDKnear=b/a
1.99993348565 instead of b/(a-1)1.00000005960. Far30013.91055456. Independent
reference ALWAYS uses nativeZ even with correction omitted;negative control
cannot pass by changing reference to match it. Default historical replay still
uses its original halfZ+.5 reference and prior behavior. Camera-state math,source
assets,observer,game runner,return host/addon,wire and C++probe unchanged.

Existing native output_probe.exeSHA4D6FDA99BEE9CE01B24B28B946386D43B4AFF17A14E813C27319402C49DFDE00
not rebuilt. Pinned Remix1.5.2x64/SDK0.6.4 hashes verified before each launch.
Only standalone owned SDK host ran,not Toolkit or SFC. Existing default opaque
double-sided diagnostic material/light;no appearance tuning or texture-fidelity
claim. Original model/native units preserved in replay,not fit/recentered there.

## Runtime evidence

All folders under artifacts/remix-runtime/runs (UTCfolderOct18,localOct17):

|Folder|Correction/source frame|Mask intersection/union|Median native-Z error|Result|
| --- | --- | --- | --- | --- |
|20261018-030933-213645-coverage|ON/120|478/478|1.6519823e-7|qualified|
|20261018-030951-555657-coverage|ON/420|478/478|1.6519823e-7|qualified|
|20261018-030956-363761-coverage|ON/720|474/474|4.3240475e-7|qualified|
|20261018-031001-064881-coverage|OFF/120|478/478|.0123745382|expected negative PARTIAL|

All runs:96frames/6phases,all18GPUcolor/depth/picking transfers byte-exact and
6native10_1shader IDbit decodes exact. Totals72/72transfers,24/24decodes. Control
movement/retirement/background sentinel/normalized depth checks pass too.
Negative control fails ONLY the intended native-depth replay criterion;process0,
output ownership,coverage and copies pass. No crash or infrastructure failure.
Output-reference threshold declared before use:maskIoU>=.95 and median depth
error<1e-5. No pixel-based fitted parameters or relaxed threshold.

## Commands / tools / validation

Bundled Python3.12.14,existing VS2026-built x64host,pinned public SDK output-copy,
native D3D11feature10_1 consumer and shader4.1 IDdecoder. Scoped external GPU
fixture execution only;no machine security-policy changes or routine sponsor UAC.
REMIX-COVERAGE-001 extension documented BEFORE new runtime use. Every call had
--execute (offlineownedfixture only),not game workflow.

```text
python tools/remix_runtime/run_coverage_probe.py --execute --calibration-run artifacts/remix-runtime/runs/20261018-025737-262069-in-game --snapshot 0 --owner 2 --native-depth
python tools/remix_runtime/run_coverage_probe.py --execute --calibration-run artifacts/remix-runtime/runs/20261018-025737-262069-in-game --snapshot 1 --owner 2 --native-depth
python tools/remix_runtime/run_coverage_probe.py --execute --calibration-run artifacts/remix-runtime/runs/20261018-025737-262069-in-game --snapshot 2 --owner 2 --native-depth
python tools/remix_runtime/run_coverage_probe.py --execute --calibration-run artifacts/remix-runtime/runs/20261018-025737-262069-in-game --snapshot 0 --owner 2
python -m unittest discover -s tests -p test_*.py
python tools/remix_runtime/run_coverage_probe.py --archive <the four exact folders above>
git diff --check
```

181Python tests PASS2.869s including new nativeZreference test for BOTH correction
flag states,and existing historical reference/transport/output regressions.
TEMP/TMP project artifacts/test-temp. Native binary unchanged,actual output checks
above provide dynamic corroboration;no need to claim a new C++build occurred.
Current semantic/calibration qualification remains valid and seven critical files
in both accepted/copied installations match Run19. Client unchanged.

## Bounds / cleanup / artifacts

Each3.61–3.89s and~5.42MB,under120s/32MiB (warn16MiB). FourGPUoutputs<=1MiB,
readbacks<2MiB,only18planes/6comparison frames perrun. No continuous screenshots,
readback image used asGPUupload,unbounded traces or simultaneous game sessions.
Four-run total21,667,126B. Archive1,098,542B/152entries,CRCverified,
SHA BD5302C942FAFDF364ABD2D08AE41C01C3907208803F792A45B943DD27BCF8B7,
path artifacts/remix-runtime/archives/20261018-031031-927578-coverage.zip.
Raw retained,overall coexistence below10GB. No files deleted.

All owned process exit0/API shutdown0;SDK warning `[40] common device objects
were not disposed of` persists in EACH run. Not warning-free cleanup or resolved
resource lifetime. SFC54/67warnings unchanged/unexercised here. No active host,
game or controller needed after restart.

Files changed:run_coverage_probe.py,test_remix_coverage_probe.py,
REMIX-COVERAGE-001.md,remix-depth-coverage-contract.md,readiness,HANDOFF,this record,
new curated evidence20261017-remix-native-depth-conversion.json. Generated
payloads/manifests/outputs/analyses/logs and archive ignored. Original reference/
capture packets unchanged;no staging/commit,indexempty,all existing work preserved.

**Exact next action:**define and offline-test the bounded multi-output return
contract carrying color+owner coverage+corrected depth with matching owner epoch,
asset revision,camera/pose and frame validity into the game-side consumer. Keep
original ship drawing enabled until that contract/visibility/fallback is qualified.
No more camera-calibration gameplay or appearance/light tuning needed now.

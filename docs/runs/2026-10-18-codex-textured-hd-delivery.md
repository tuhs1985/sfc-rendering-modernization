# Run30 — steady, original-textured full-HD additive delivery

Run SFC-RETURN-20261018-30; 2026-10-18 America/New_York.
**READY FOR SPONSOR RUNTIME TEST. No SFC run performed here.**

## Authority / starting baseline

Sponsor requests steady/sharper delivery, complete original textures, at least
screen-space resolution; original replacement remains separate. Read authoritative
HANDOFF, approved M1 plan/current gate allocation, Run28 visible result, Run29
future-renderer gate, current semantic/camera/resource and return contracts/probes.
Approved CDD unchanged. HEAD e96765a1a34c15212ed22f11edeb9a708b9fc18d;
preexisting dirty/untracked work preserved, index empty. No stage/commit.
FuelGuard attached real thread via hook; no daemon/helper/delegation.

Prior actual game run170018-838194:953 outputs/285 visible submissions, coarseness
and flicker isolated to added256-square copy. Do not repeat connection qualification
as a new achievement or change native renderer architecture to conceal it.

## Decisions / implementation

Explicit v4 delayed-additive profile holds newest completed source <=100 ms
request-age at enqueue with stable identity checks. Captured frame/pose/camera
stay captured, not relabelled current. Strict v3 diagnostic remains intact.
Original ships are NEVER suppressed; replacement cannot inherit this policy.
Output/shared/private descriptors now1920x1080. Four surfaces33,177,600 bytes.
Legacy control prefix256-square is compatibility metadata, not actual output.

Fresh packet group associations resolve original primary image files on worker.
Hash-deduplicated DDS materials, grouped indices and all original geometry/UVs
preserved. Fullbright primary contribution is provisional illumination, NOT native
emissive semantics; secondary maps retained only as provenance. Missing/alpha
primary fails partial. No game-callback IO/decode/waits/readback. Receiver busy
ACK retry preserves pending lease. Full contract, format, hazards and limits:
[contract](../reconnaissance/textured-additive-delivery-contract.md),
[probe](../reconnaissance/probes/REMIX-TEXTURED-RETURN-001.md).

### Exact files changed in this run

Under `tools/remix_runtime/`: new `textured_asset.py`, `ship_textured_asset.h`;
modified `ship_triplet_wire.h`, `ship_triplet_consumer.h`, `ship_live_request.h`,
`ship_live_receiver.h`, `return_addon.cpp`, `ship_live_host.cpp`, `live_return.py`,
`run_return_game.py`, `start_return_image_session.ps1`, `run_coverage_probe.py`,
`qualify_live_return.py`, `ship_live_gpu_fixture.cpp`.
Tests: new `tests/test_textured_asset.py`; modified `tests/test_live_return.py`,
`tests/ship_live_request_tests.cpp`, `tests/ship_triplet_tests.cpp`.
Documentation: this record, new contract/probe/evidence JSON, HANDOFF newest entry,
existing live-return probe cross-reference. Accepted semantic component unchanged.

## Reproduction / validation

Bundled PS7: `-NoProfile -File tools/remix_runtime/build_live_return.ps1`.
Native /W4 /WX builds PASS, request tests89 and triplet tests67 eachx86/x64;
repeat build reproduced binary pins. TEMP/TMP set to ignored `artifacts/test-temp`;
bundled Python `-m unittest discover -s tests -p test_*.py`:205 PASS/4.203s.
PS parser, final read-only `run_return_game.py --textured-ship`, qualification,
archive integrity, referenced paths and git diff --check PASS.

Actual GPU fixtures use `qualify_live_return.py --execute` with flags below;
scoped approved build/GPU process access only, no sponsor admin dialog. Final
source-pinned runs under `artifacts/remix-runtime/runs/`, all suffix `-live-private`:

| UTC run | Extra flags | Result |
|---|---|---|
|20261018-175039-213725|--addon --textured|PASS;131 outputs/129 acquired,0 failures;59/59 steady samples|
|20261018-175100-850383|--addon --textured --slow|PASS;131/129,0 failures;59/59 steady samples|
|20261018-175124-045490|--addon --textured --disconnect|PASS;3/2,host1 intentionally terminated,fixture0|
|20261018-175145-403906|(direct)|PASS|
|20261018-175153-530509|--addon|PASS|
|20261018-175202-422810|--slow|PASS|
|20261018-175212-054788|--disconnect|PASS intentional termination|
|20261018-175219-880773|--addon --visible|PASS strict legacy;IoU0.994603|

Then `--qualify` with these eight directories produces both visible-camera and
textured-delivery qualification flags; launcher requires matching sources/binaries.
Textured image14272 pixels/113 quantized colours,56 primary materials/58groups;
81 unique primary/secondary source hashes match both installations. Image output
46,367,290 bytes; normal/slow/disconnect sessions55,527,720/55,541,329/55,525,439B.
Source-age expiry and renderer death reject, no private hook-state failures.

Initial172907 native display worked but raw mask comparison failed; preserved as
PARTIAL. Native-resolution/filter-aware oracle and explicit narrow-edge textured
criteria qualify footprint, not exact pixel match: rawIoU0.920925,centroid0.340621px,
area1.008622,beyond3px unexpected1/missing5. Old strict magenta0.95 gate unchanged.
Shifted/corrupt masks reject. Initial C2664/C4267 compile errors corrected before
final /WX builds. Cold~0.52s output rejected, warm~6ms observed; total fixture21–23s
includes preparation. No instant-loading claim. SDK warning40 still OPEN.

## Pins / preserved originals / evidence

Remix1.5.2 d3d9.dll SHA256
`F7C310821AA98BCDFDEC120330B0A89457B7C5EBA58D21464AF32639611C809F`;
SDK0.6.4 header `E623E4956A76894EEEF02361334C7C0458D4EC8BF49F729EC9038C36128BBF47`.
Host `E9F0C4095E29ADB54233AE0B5247083A15823AF8852B6DDCA736071C03AA377C`;
fixture `87B617DDCCEEEB5304BD78D3834A679D28EF92A46DBCEC435D2832ED86353975`;
addon `CD8FCD9E7FEA43C3596612E031932D8EB96C2EE4E4B7BD6966003022219B4BD3`.
Qualification SHA `1744456BF91556D9D68C26E6B5264400956CA1C18F3943A38555392BC765EDA9`.
Seven critical installation files unchanged in accepted and copied installation;
both executable SHA `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
No on-disk client patch, no accepted-install changes. Existing semantic DLL SHA
`BCC3BB19276A740E514D5CA4C0A1CF09ACF0169416251C1F552384AE069B8FE1` unchanged.

Ignored archives, raw retained (no deletions):
- `artifacts/remix-runtime/archives/20261018-textured-hd-delivery-final.zip`,
  28,713,068 bytes; SHA `CDE19FD80DE686C65EFD058DA4BBCEEF1F4D61231F37E095571245DE85622E74`.
- preparation archive43,507,041 bytes; SHA
  `D117BCF12083BB2A6A9C06EA78B9DF06BDFE59AA843A71162260AC0AC45FF70D`.
  Filename `20261018-textured-hd-delivery-preparation.zip`; includes failed oracle
  and superseded successful qualifications. Final eight runs above authoritative.

## Adjudication / next action

**CONFIRMED offline:**original texture provenance,full-HD GPU path,bounded held
image with unchanged captured provenance,synthetic motion continuity and failures,
legacy regressions. **STRONG HYPOTHESIS:**this improves actual extra-copy stability
and sharpness. Sponsor gameplay confirmation pending. Alpha/glow/native lighting,
instant loading,scene/HUD occlusion,frame-exact replacement remain unqualified.
Future-renderer boundary gate remains OPEN. No milestone advancement.

No active SFC/host/mapping needed to resume; generated source qualification pins
are necessary and rebuilt binaries must match. No stage/commit; preexisting dirty
work preserved. Exact next action: run the prepared `-TexturedShip` command in
the probe from the validated elevated parent, observe the full-textured extra
copy and native controls, then exit at two-beep request for runtime adjudication.

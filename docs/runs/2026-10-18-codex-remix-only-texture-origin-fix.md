# Run38 — Remix-only texture-origin correction

SFC-RETURN-20261018-38;2026-10-18 America/New_York. Active bounded textured
additive return-path experiment;no renderer replacement/milestone completion.
Sponsor authorizes fix,explicitly forbids carrying Remix-specific behavior into
future D3D9/D3D12 adapters.

## Baseline and decision

HEAD e96765a1a34c15212ed22f11edeb9a708b9fc18d;existing dirty work/indexempty.
Read HANDOFF,Run37,production SDK host/material preparation,qualification/build/
tests,current contract and future-renderer gate. FuelGuard hook attached actual
thread;no helper,subagent or daemon. No staged/committed changes.

Run37 independently established identical captured/model/image inputs but opposite
vertical sampling between installed Blender and pinned Remix SDK/DDS. Sponsor
confirms captured OBJ correct;prepared in-game layer already reversed. Correction
is **adapter normalization**,not a claim that Remix has a bug or all DirectX
renderers need a flip. Native visual parity remains pending runtime comparison.

New `remix_texture_coordinates.h` supplies constexpr v=1-captured_v;U unchanged.
Only `ship_live_host.cpp`'s textured-mode SDK vertex preparation calls it,once,
AFTER validating/copying raw mesh arrays. Positions,normals,indices,winding,raw
packets,live-mesh.bin,OBJ,original PNG/DDS rows,shared scene/capture remain intact.
No clamping,second image flip,brightness/light/material change or new architecture.
Legacy magenta untextured path unchanged. Provenance labels backend/scope and
raw-data preservation. Header/comment,contract and renderer-independence gate
explicitly require future adapters to qualify their own conventions. This does
not close the renderer-independent-boundary gate.

## Implementation / reproducible validation

Files modified:ship_live_host.cpp,live_return.py(source pin),textured_asset.py
(metadata only),build_live_return.ps1(native test),test_textured_asset.py,
textured-additive-delivery-contract.md,renderer-independent-boundary-gate.md,
HANDOFF. Added remix_texture_coordinates.h,remix_texture_coordinate_tests.cpp,
this record. Exact source/binary hashes retained in offline qualification manifest.

Toolchain remains VS2026Community18.7.3,x86/x64 /std:c++20 /EHsc /W4 /WX /Brepro;
PS7.6.5,bundled Python3.12.14,pinned Remix1.5.2/SDK0.6.4. No dependency changes.
Initial sandbox build could not overwrite existing reshade_registration.lib:
LNK1114,error5. Repeated same scoped build through approved escalation;no ACL or
security weakening. No sponsor UAC routine added.

```text
pwsh -NoProfile -File tools/remix_runtime/build_live_return.ps1
python -m unittest discover -s tests -p test_*.py
```

Native build PASS;89request checks plus14UV adapter checks each x86/x64 PASS.
UV tests cover endpoints,interior values,out-of-range repeating coordinates and
double-conversion reversal. Python223PASS4.356s;TEMP/TMP=artifacts/test-temp.
Regression requires conversion only in textured host,one call site,header included
in source pins,and no adapter dependency in capture/export/asset preparation.

Offline production qualification uses existing REMIX-LIVE-RETURN-001 /
REMIX-TEXTURED-RETURN-001 / REMIX-PREPARED-IMAGE-001. No new capture mechanism.
Run `python tools/remix_runtime/qualify_live_return.py` with each argument set:

```text
--execute --addon --textured --capture-image
--execute --addon --textured --slow
--execute --addon --textured --disconnect
--execute
--execute --addon
--execute --slow
--execute --disconnect
--execute --addon --visible
```

Then `--qualify` with the eight exact newly generated folders. Each owned offline
fixture60s/32MiB detailed logs,warning16MiB;images128MiB separate;existing output
pool<=128MiB,one-shot snapshot. SFC never started. No continuous screenshots or
geometry firehose. Existing normal sponsor runner90s tactical/300s total remains.
Reader failure and mask/age/identity/fallback behavior retain existing contracts.

All eight gates PASS,qualification flags visible_camera/textured_delivery/
prepared_image=true. Textured fixture130produced/128acquired/failed0,maskIoU
0.99886925795053,host0/fixture0/SDKshutdown0;actual host log confirms conversion.
Prepared PNG roundtrip PASS. All output bounds held;16MiB warning in capture mode
expected,32MiB nontexture cap retained. Slow/disconnected receiver and legacy
direct/callback/visibility modes PASS. Read-only `run_return_game.py
--capture-ship-image` preflight PASS;no SFC/gameplay initiated during this run.

Qualification SHA256
`0117BC565B1B04010BC79640B5BA7A31FA07FC532160713EFECBBDF316586A66`;
host SHA256 `0D53E9A40254C06A68E4ECF270E0437A9DE53961233D9A81492907E9304F2304`.
Addon unchanged `6C37A539A2133BEF0C539EFD2EA539EDA5E2E05F7CB160884B582FB6C51A1980`.
Exact eight folders/pins in [evidence](../reconnaissance/evidence/20261018-remix-only-uv-fix.json).
Archive28,811,569B,raw retained,CRCverified:
`artifacts/remix-runtime/archives/20261018-remix-only-uv-fix-qualification.zip`,
SHA256 `53FAB52C9DB1784FE67FA5304B35286F7B341F02C7E81F95683D2E8AA5086AE1`.
Final JSON/source-parser checks/git diff --check PASS,indexempty,no stage/commit.
No persistent process/session needed. Implementation/offline behavior CONFIRMED;
native visual correction still awaits sponsor comparison. Existing SDK40 finding
and separate texture-control teardown PARTIAL not silently closed by these gates.
No gameplay/native texture parity success claim from offline safety qualification.

Independent accepted and copied StarFleetOP.exe hashes remain
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.

## Next smallest action

After offline qualification completes,run existing prepared workflow with
`-CaptureShipImage`;usual two-ship skirmish,observe extra saucer versus original,
hold briefly for automatic prepared-layer capture,and exit at two-beep request.
No manual timestamps,new model conversion or on/off cycle. Original ships stay
ON. If remaining mismatch persists,inspect corrected layer instead of guessing
another flip. Source data/other renderer adapters must remain unchanged.

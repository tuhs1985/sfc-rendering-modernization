# Run36 — one exact prepared image before in-game insertion

SFC-RETURN-20261018-36;2026-10-18 America/New_York.
Sponsor accepts correct Blender model,asks whether exact returned pixels can be
inspected,and authorizes proposed one-shot capture. No mirror/Toolkit window,
second render,asset conversion,visual repair or original-ship suppression.

## Baseline / question

HEAD e96765a1a34c15212ed22f11edeb9a708b9fc18d;preexisting dirty work preserved,
indexempty. Read HANDOFF,current prepared return/probe,Run34/35,receiver/late
AddImage path,wire/registration layout and runner/fixture. FuelGuard attached
actual thread through hook;no daemon/helper/delegation. Approved CDD unchanged.
Sponsor's Blender observation supports captured model correctness,not proof
that NVIDIA alone caused the reversed texture. Need isolate returned image from
late SFC composition without changing the picture under investigation.

## Implementation / exact capture boundary

New default-off `-CaptureShipImage` implies textured continuous profile. At an
eligible `currentDisplay`,immediately before its SRV is returned to late AddImage,
queue ONE CopyResource of the SAME prepared private BGRA texture into an immutable
shared GPU diagnostic slot. Record captured key/owner/revision/model/source/LOD,
asset/pose/camera/source frame,sequence,source-request/captureQPC and display rect.
Mark AddImage CPU enqueue and poll event query DONOTFLUSH. Publish READY only
after copy completion. Snapshot is AFTER private alpha/depth/picking masking,
BEFORE late display scaling/filtering/composition. A wrong PNG would implicate
the pre-insertion pipeline,not uniquely RTX;a correct PNG narrows later processing.

Separate owned x64 reader opens only same-session shared snapshot,checks adapter/
PID/key/descriptor,uses its OWN device/context to stage/read/save. No render-callback
Map,CPU image copying,file IO,flush,wait,new thread or allocation. Only256B control
header copied in callback. Resource initialized once at device setup,not per object.
Normal rendering/leases never wait for reader;failed reader produces missing-image
PARTIAL after gameplay,not native game failure. Driver resources retain references
through reader lifetime;bounded stop cleanup kills only owned external worker.

Device recreation edge found in review:initial version reinitialized header on
each Receiver creation. Corrected same-session non-OFF attempt guard preserves
pending reader/immutable result across recreation;cancel/error remain PARTIAL,
never silently rearmed. `markDisplay` requires this instance's submitted copy.
Preliminary fixture qualifications are historical;final guarded pins below govern.

Protocol/probe/limits documented BEFORE first offline use:
[REMIX-PREPARED-IMAGE-001](../reconnaissance/probes/REMIX-PREPARED-IMAGE-001.md).
Header256B at offset2304 in existing current-user4KiB control mapping;no existing
wire/command/registration overlap. Single shot,not a streaming resource ring.
Raw header+1920x1080BGRA max8,294,656B. External Python saves lossless RGBA PNG with
only channel reorder,no flip/resize/gamma/exposure/alpha changes;roundtrip verified.
JSON records full provenance/hashes and separates native viewport from source size.

Existing four output surfaces stay;one immutable GPU copy+one worker staging copy
add at most16,588,800B for this explicitly scoped diagnostic. Total output/capture
resources~47.46MiB<128MiB envelope,not total SDK VRAM claim. Logs/evidence remain
32MiB excluding128MiB texture resources,warn16MiB. Reserve worst-case PNG before
conversion to avoid exceeding cap. No continuous screenshots or geometry firehose.
Normal90s tactical/285s Python/300s prepared workflow and10GB allowance retained.
Worker lifetime95s,GPU wait5s outside game;runner bounded owned-process cleanup.

## Reproducible workflow / files

New sources: `ship_image_snapshot.h`,`ship_image_reader.cpp`,`ship_image_snapshot.py`,
`test_ship_image_reader_failure.py` under tools/remix_runtime.
Modified: `ship_live_receiver.h`,`return_addon.cpp`,`build_live_return.ps1`,
`live_return.py`,`qualify_live_return.py`,`run_return_game.py`,
`start_return_image_session.ps1`. Tests:new `tests/test_ship_image_snapshot.py`,
modified `tests/test_live_return.py`. Documentation:this record,new probe/evidence,
HANDOFF. No geometry/material/texture/light or original-client changes.

Bundled PS7 `-NoProfile -File tools/remix_runtime/build_live_return.ps1` builds
same x86 addon/fixture,x64 host plus new x64 reader,/W4 /WX,Remix1.5.2/SDK0.6.4;
native89request checks each architecture PASS. Same process-local NRC/DLSS/RR OFF,
no new dependency,renderer,wrapper or UAC policy. Capture qualification requires
matching new sources and reader binary plus successful exact-image fixture.

From established elevated parent:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\remix_runtime\start_return_image_session.ps1" -CaptureShipImage
```

Usual skirmish,focus extra returned copy at useful size then hold briefly. Capture
is automatic15s after first eligible display (next eligible image if temporary
invalidation). This diagnostic suppresses camera/movement instructions,not drawing.
No manual screenshot/timestamps or on/off cycle. Copy stays ON until normal90s
stop/cleanup;exit at two-beep request. Expected unique run folder contains
`prepared-ship-image.sfcimg`,`.png`,`.json`,reader log and usual evidence.

## Validation / confidence

Pure Python220tests PASS/4.370s:lossless colour order/transparency,correct source
identity/age/rectangle/size checks,malformed/incomplete/replayed-source rejection,
overwrite refusal,default-off capture no callback readback/IO/wait,sticky snapshot
guard and qualification requirement. PowerShell/Python parser,refs/JSON and
git diff --check PASS. Original/test executable independently unchanged at SHA
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.

Preliminary204631 and204804fixtures captured valid full-HD alpha images,sequence45,
source frame120,owner2,asset matching recorded FCA. Decoder pixels/PNG lossless;
16028nonzero-alpha pixels,request-age~15–18ms. These are OFFLINE recorded-geometry
fixtures through actual addon/transport,not fresh SFC gameplay. Same driver path
and same SRV allocation corroborate boundary;not final displayed-pixel identity.

Final guarded eight GPU gates,reader-kill fault and exact pins/archives appended
below. Worker fault is expected requested-image PARTIAL with native fixture PASS,
not successful image qualification. Known standalone UV-control shutdown PARTIAL
and normal-host SDK40 remain separate open findings. No claim saucer fixed.

No stage/commit,indexempty,prior work retained. No active process/session required
to resume. **Exact next action:**sponsor runs new command;after normal exit inspect
PNG+source metadata against SFC/Blender before choosing any texture conversion.

## Final guarded qualification — READY FOR SPONSOR RUNTIME TEST

All eight final GPU gates PASS,UTC20261018,suffix`-live-private`:
205323-463061(textured capture),205345-730716(textured slow),
205408-984383(textured disconnect),205430-734532(direct),205439-062142(callback),
205448-305151(slow),205458-151732(disconnect),205506-213611(strict visible).
Then205517-872434 controlled owned-reader termination:requested image PARTIAL as
expected,native fixture PASS/failed0,host shutdown api0;positive fault-isolation
review retained separately,NOT added as successful image capture qualification.

Capture gate:131outputs/129acquired,private failures0,host0/fixture0,
IoU0.998869,1920x1080 snapshot16028nonzero-alpha pixels,sequence44/sourceframe120,
owner2,request age43.1253ms. Independent PNG roundtrip and selected asset/owner/
revision comparison PASS. Captured source is recorded fixture geometry,not a new
SFC game run. Curated [offline image](../reconnaissance/images/20261018-prepared-layer-offline.png)
retains original RGBA bytes,PNG SHA256
`d53c870364ee3b85e1a5a77fba16dda4b79b5d65ea92ca603415cc25b39c4761`.
Packed BGRA pixelSHA `734bfec94d8930d8ba207f78a111deb62f94938f129688c579b3c3507831ff71`.

Qualification flags visible_camera/textured_delivery/prepared_image alltrue;
SHA256 `893DE9BA47702CCEDA24C3044A1330F38511681AC2635518C8A113046A70E566`.
AddonSHA `6C37A539A2133BEF0C539EFD2EA539EDA5E2E05F7CB160884B582FB6C51A1980`;
readerSHA `1784920C447F9A130AF2773E455A5BB78CAC6277C6394656A75A22D1912764ED`.
Read-only `run_return_game.py --capture-ship-image` preflight PASS.
Final220Python tests PASS/4.710s,PS parser PASS;no native/client changes after
qualification,no game launched. Actual graphics-device recreation not separately
runtime-induced;sticky no-rearm guard corroborated by source/regression,not an
exhaustive resize/device-loss certification. Worker death directly exercised.

Nine guarded sessions archived(raw retained,no deletion):
`artifacts/remix-runtime/archives/20261018-prepared-ship-image-final.zip`,
36,200,984B,CRC PASS,SHA256
`598F8FBD5D3171F6628D51D6FCEB8FAD2B7F2767E322F7CDC165BDEDB19B6E36`.
Earlier `20261018-prepared-ship-image-qualification.zip` is SUPERSEDED pre-guard
evidence,not authority for current source pins.16MiB warnings expected due one
8MiB raw image;32MiB cap never exceeded. Source references/JSON/diff checks PASS,
indexempty,no stage/commit. [Curated summary](../reconnaissance/evidence/20261018-prepared-ship-image.json).

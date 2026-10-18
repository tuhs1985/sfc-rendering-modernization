# REMIX-PREPARED-IMAGE-001 — one exact prepared ship-layer capture

2026-10-18;default OFF. Sponsor authorizes capturing pixels before insertion to
localize saucer-texture reversal. Not another render,model conversion,desktop
screenshot or continuous recorder. No native SFC draw suppressed.

## Capture point / provenance

`ship_live::Receiver::currentDisplay` first validates current owner/revision,
source age and native viewport exactly as before. Immediately before returning
the SRV to the late ReShade AddImage call,it queues one GPU CopyResource of the
same private prepared BGRA texture into an immutable shared diagnostic slot.
`imageDisplayed` marks the actual AddImage CPU enqueue;nonblocking event-query
polling publishes READY only after GPU copy completion. These are prepared layer
pixels AFTER our alpha/depth/picking mask,BEFORE final display-rectangle scaling/
filtering/composition. They are NOT raw pre-mask Remix output or final SFC screen
pixels. A wrong capture localizes failure before late insertion,not automatically
inside NVIDIA's code. Colour-management/display resampling can differ afterward.

One256-byte header at offset2304 in existing current-user4KiB control mapping,
no overlap with wire512/command1024/registration1792. Magic0x31495353/version1.
Layout: `<8I4Q2I4f`88B + existing152BKey + fourDWORD(error,model,source,LOD).
Header includes PID,dimensions,format87,shared handle,request/captureQPC/frequency,
sequence,AddImage-enqueued flag,exact display rectangle,session/owner/asset/pose/
camera/source-frame identity. States OFF/ARMED/COPYING/READY/READING/WRITTEN/
ERROR/CANCELLED (0–7),single immutable slot,no reuse or overwrites.
Device recreation never rearms or overwrites a same-session attempt,including
READING/WRITTEN/error/cancelled states. An interrupted attempt stays PARTIAL;
do not relabel an old image with a new resource identity or take a second shot.

## Resources / safe operating envelope

Preallocate one GPU diagnostic texture/event at receiver initialization ONLY when
flag enabled. Callback does no Map,CPU image copy,allocation,file IO,flush or wait;
GetData uses DONOTFLUSH. A separate owned x64 `ship_image_reader.exe` validates
session/PID/adapter/descriptor and reads the frozen image with its OWN D3D11
device/context. Worker GPU timeout5s,overall95s,one file only. It never calls or
blocks SFC. Reader failure leaves original rendering/return delivery unchanged;
requested missing image becomes PARTIAL after gameplay exits.

Existing four output-pool surfaces remain unchanged. This specifically justified
one-shot diagnostic adds ONE immutable shared copy plus ONE worker staging copy,
at most16,588,800B total,temporary;not an expanded streaming-output pool. Combined
with four output surfaces~47.46MiB within128MiB GPU output/resource envelope.
One packed raw file maximum8,294,656B (header included),one lossless RGBA PNG up
to~8.3MiB,one small JSON sidecar. Source remains BGRA8;conversion changes channel
order only,no flip/resize/gamma/exposure/alpha edits. Combined32MiB non-image
evidence cap remains (warning16MiB may be expected);image resources128MiB and
10GB total allowance unchanged. No multi-GB producer or repeated images.

## Build / exact launch / sponsor actions

Pinned Remix1.5.2/SDK0.6.4,ReShade6.7.1.2133,VS2026Community18.7.3 x86 addon/x64
reader,/W4 /WX. Python3.12.14/Pillow;no new dependencies. Same process-local
NRC/DLSS/RR OFF. Build existing `build_live_return.ps1`,which now also builds
the small external reader. Qualification includes all sources/reader hash and
requires a successful one-shot offline fixture before capture mode can launch.

From established elevated parent (PS5 forwards to bundledPS7,no routine newUAC):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\remix_runtime\start_return_image_session.ps1" -CaptureShipImage
```

Capture flag implies normal continuous textured profile. Enter familiar two-ship
skirmish. Focus/zoom toward extra returned ship once it appears,then hold camera
briefly. Snapshot triggers automatically after15s of first eligible displayed
copy;it captures next eligible fresh output if state is temporarily invalid.
No manual screenshot,timestamp,UV inspection or administrative prompt.
For this image diagnostic only,routine camera/movement cues are omitted:hold
view rather than rotate/turn on a cue. Copy stays ON through90s observation;
exit normally at usual two-beep request. Five-minute workflow limit unchanged.

Outputs in unique `artifacts/remix-runtime/runs/<UTC>-in-game`:
`prepared-ship-image.sfcimg` (256Bheader+tightly packed top-to-bottom BGRA),
`prepared-ship-image.png`,`prepared-ship-image.json`,`ship-image-reader.log`,
plus usual evidence. Sidecar source owner/revision/frame/asset must match source
manifest;decoder rejects malformed/incomplete/old/foreign identity metadata.
Never substitute screenshot/missing-model template on failure.

Offline `qualify_live_return.py --execute --addon --textured --capture-image`
uses same addon/reader through real GPU transport,explicit documented delay2000ms
to fit bounded fixture. This is not SFC gameplay evidence. Same60s/32MiB fixture
cap plus128MiB original/derived textures. Ordinary gates run with capture OFF.
Offline failure test:`python tools/remix_runtime/test_ship_image_reader_failure.py`
uses the same60s/32MiB fixture but terminates ONLY the reader process returned by
its own Popen call,not processes selected by name. Expected image result PARTIAL;
native rendering/lifecycle must still PASS and host shutdown api0. Preserve its
`reader-fault-review.json`;never use this negative capture as successful image
qualification or execute against SFC.

Cleanup:existing normal component restore/unload/host shutdown and unchanged-client
checks;runner waits up to5s for owned reader then terminates only that worker if
needed. Snapshot held separately,so no lease or callback waits during shutdown;
worker-held shared resource remains valid through its own reference. No persistent
installed files or global state. Preserve partial file/logs;archive useful evidence
after analysis. Do not delete reference assets or manually remove unrelated proxies.

Inspect PNG first against sponsor's correct Blender model and SFC view;use raw
header/image hashes as provenance. Do not claim orientation repair or RTX bug merely
because appearance differs. No automatic texture/normal/face/light changes.

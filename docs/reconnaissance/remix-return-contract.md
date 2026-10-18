# Remix returned diagnostic image — contract v2

Status: offline GPU/consumer/compositor CONFIRMED; SFC gameplay UNTESTED.
This is not synchronized ship replacement. No original ship drawing is suppressed.

Optional expanded search extension at mapping256: depth_search_wire.h/version1,
2304B,6phase counters and32resource/view observations. Default-off -SearchDepth,
observation-only mode,full90s. Main256B/v2 prefix unchanged. See current probe/run
record for CPU-state,mid-call replay,worker restoration and coverage limits; this
is not a replacement/frame/depth-image transport contract or GPU inventory.

Latest2026-10-17: [earlier-scope preparation](../runs/2026-10-17-codex-early-depth-preparation.md)
adds scope2 pre-effects public Present observation,depthViewFormat180,remaining
72reserved bytes; existing256B/v2 prefix unchanged. -ObservationOnly creates same
control channel WITHOUT loading Remix,zeroimagecopies/draws; not a renderer
regression pass. Offline default-material host also hit driver617.42+0xF10CF4
crash,so prior custom-material-only implication is rejected; cause still open.
Next read-only test isolates depth availability; no original suppression.

Current continuation: [cleanup/ship readiness record](../runs/2026-10-17-codex-return-cleanup-and-ship-readiness.md).
Bounded host retirement fence passed,40-object shutdown warning persists even
without SFC; cause remains open risk. Default-off optional visibilityVersion1
extension uses formerly reserved144..175bytes for eight late DSV descriptors;
prefix256B/v2 unchanged. Zero means absent. Counts/descriptor presence do not
qualify scene depth or permit suppression. See REMIX-RETURN-001 for exact layout,
controls and prepared -InspectVisibility run. All original rendering continues.

Update2026-10-17: [actual runtime review](../runs/2026-10-17-codex-remix-return-runtime-review.md)
supersedes UNTESTED above: finite in-SFC returned diagnostic image CONFIRMED,
sponsor reports normal gameplay,656transfers/ACKs and normal process exits.
Runtime internal cleanup warning remains open; removed-state ordinary startup
not yet exercised. No replacement or formal milestone completion claim.

## Dependencies and launch

Official Remix release1.5.2, release-associated SDK0.6.4 from dxvk-remix
b81a7b566b1eeb9edb4dc2b3c9d3972e0f253ad4; archive/runtime hashes are in
[qualification record](../runs/2026-10-17-codex-remix-output-qualification.md).
The binary reports remix-1.5.2+68edea01; that suffix is not a verified public
source commit. Compatibility is established for the exercised subset, not every
SDK material interface. Custom-material driver failure remains unresolved.

Existing copied ReShade6.7.1.2133 x86 remains unchanged. Official SDK tag commit
8cf85bd12d56697d756d4fcb45e501f5d1b540fa, API18, ImGui19250 at
3912b3d9a9c1b3f17431aebafd86d2f40ee6e59c. Limited build rejects automatic
addon32 discovery; project DLL registers through supported external APIs and
allowed runtime/overlay events. No restricted event or proxy bypass.

Microsoft Detours4.0.1 e4bfd6b03e50de46b47abfbd1e46b384f0c5f833 supplies
startup-only process-memory import insertion. Loader verifies test-copy path
and client/component SHA before creation and child path/client SHA before resume.
Component restores process headers before game entry. No disk executable edit,
live callback-vector registration race, global launcher registry change or hot
unload. Ordinary copied-client launches have no project import/component.

## Ownership, synchronization and bounds

`return_wire.h` and `return_channel.py`: version2,256-byte control state inside
unique Local GUID4KiB mapping. Protected DACL permits only current token user SID.
Mapping identifier explicitly reaches component; exact full executable path also
required. Session lifetime follows owned mapping handles. Legacy KMT GPU handle
does not have an independently configured NT DACL; do not overclaim isolation
against an arbitrary hostile process with a disclosed GPU handle.

SFC-side native D3D11 creates256x256 BGRA8 shared texture and private display copy
(524288bytes together). Host takes native resource lease, validates descriptor,
imports via D3D9Ex, renders default-material triangle + green sphere light with
SDK, calls CopyRenderingOutput(final). Producer D3D9 EVENT completion precedes
Interlocked publication. Receiver polls D3D11 EVENT without waiting and ACKs only
after CopyResource into private display completes. No CPU image transport,
game-thread readback, disk/image conversion or game-thread waits.

One in-flight output, session-monotonic sequence, device/resource epoch and
renderEpoch/presentedEpoch separate generations. Fresh first packet can supersede
unacknowledged old-resource output; same-resource producer cannot overwrite until
ACK. Old epoch, malformed header, invalid descriptor, late>1second, disabled,
unarmed or stopped output cannot be displayed. Failure omits image; original SFC
drawing is never suppressed. Host GPU wait bounded5seconds; game never waits.

Supported frame544x384..1920x1080. Fixed256square at(x=width-272,y=96), ending
at(width-16,352). ReShade background image draw list, no input widgets or new
desktop overlay. ReShade GUI backend preserves graphics state; offline OM/RS/IA
sentinels passed actual Presents. This does not yet prove SFC UI placement.

Destroy clears READY before releasing resources; host lease protects imported
resource. Recreation advances epoch. Stop hides immediately; normal game runtime
destroy releases component resources before process/DLL teardown. No hot unload.
Disabled means flags off; removed means next ordinary direct-client startup
without startup loader/session/import. Removal in SFC remains a gameplay check.

Runtime process-local NRC/DLSS/RR off; synchronous required shader compilation.
No system/driver setting changes. Native fixture takes only five fixed readbacks
and one BMP for evidence; production game path takes no image dumps.

## Evidence and remaining limits

Latest offline result `artifacts/remix-runtime/runs/20261017-052545-410229-return-fixture`:
223frames, zero state errors; enabled7425 green pixels, disabled0, resized7425,
recreated7429, disconnected0; original blue region preserved. Host exit1 is
INTENTIONAL owned-renderer kill, not a graceful-stop result; fixture exits0.
Startup restored/verified1, three resource clears, final READY0/error0.

Standalone graceful producer exit and slow/failed consumer recovery were tested
separately; actual GPU driver-loss/recovery and resource exhaustion are not yet
experimentally demonstrated. Header/format/dimension/time guards are tested;
do not describe guards as hardware-fault injection results. GPU output route is
CONFIRMED only for the finite default-material diagnostic; textures, depth,
coverage, owner suppression and synchronized replacement remain unqualified.

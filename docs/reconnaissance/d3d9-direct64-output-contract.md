# Direct64 ordinary-D3D9 output — experimental offline contract

Run75 update2026-10-20:current same-SID channel adds unique READY/ACK auto-reset
events,worker notification only;state/checksum/fences still authoritative. Receiver
copies into private DEFAULT GPU triplet before ACK;staging only sampled diagnostic
copies. No owning producer image use after ACK. At1080p shared/private/two staging
triplets total99,532,800B<=128MiB. One-present snapshot correlation confirmed;
short300update artificial60Hz1080p timing-only run0misses,p95~11.98ms. NOT live
rate or current-game-frame delivery;source lead/seal must still be measured.

2026-10-20 update:[Run74](../runs/2026-10-20-codex-d3d9-cross-process-output.md)
qualifies independent x86 D3D11 receiver and explicit one-set ownership for static
snapshots. Seven normal/slow/fault cases,exact cross-process pixels. Protocol in
output_channel.h:protected current-user mapping192bytes,packet128bytes;session,
source frame/state hash,scene hash,owner epoch/revision,resource epoch,sequence,
GPU LUID/legacy handles,dimensions,QPC,FNV. READY only after producer GPU fence;
ACQUIRED ->receiver copy/fence ->exact ACK ->reuse. Invalid/stale ACK/disconnect
retire generation and stop writes before release. GPU bytes never cross CPU IPC;
staging raw32files are offline verification only. Receiver must exit before local
resource destruction. Legacy handles not NT-security objects;no malicious same-
user isolation claim. One set suffices for ownership proof,not live throughput.
Run73 missing-cross-process statements below are historical,not current blockers.
Current next action:one-present correspondence test,then offline cadence. Timing,
device loss,recreation,multi-owner identity/occlusion and live frame sealing remain
unqualified. Runtime warning40still unresolved.

Run73,2026-10-19. Sponsor approved64bit helper qualification,not live replacement.
Same renderer-neutral geometry/images/transforms as native proof;SFC capture32bit
unchanged. API-specific implementation does not become the durable scene format.

## Input and ownership

`scene.bin`/`scene.json` remain neutral OFFLINE replay v1,not live IPC. Runtime
captures are sole geometry source;MOD names are identity labels. Same Renderer
uploads raw XYZ/N/UV/groups;no Remix SDK mesh/material/instance calls. Normal
Direct3DCreate9Ex/CreateDeviceEx on pinned64bit `.trex/d3d9.dll` enable ordinary
draw conversion. Pinned output API registers that existing device only.

GPU consumer must match producer LUID. One fixed three-image shared output set:
BGRA8 color,R32_FLOAT normalized depth,R32_FLOAT preserving raw picking bits.
Output budget<=128MiB;current960x540 uses6,220,800bytes for shared images,plus
separate bounded OFFLINE staging. Import aliases existing native D3D11 resources.
No VkImage value is treated as transferable Windows resource. No cross-process
receiver or authenticated handle protocol exists yet in this proof.

For each immutable snapshot:24ordinary presents warm current state ->output copy
->renderer D3D9 event completes ->D3D11 copy/event completes ->offline Map/readback.
No image pixels pass via CPU between renderer and native GPU consumer;Map is
verification only. These waits,warmup10ms sleeps and readbacks MUST NOT migrate
into SFC callbacks or count as qualified real-time performance.

After local GPU work drains,all imported views/textures/consumer resources retire
before registered-device aliases detach and API Shutdown releases owned refs.
Runtime common-device disposal warnings persist;exit0 is not a leak qualification.

## Pixel coordinates,depth and identity

Actual output is full camera frustum over full960x540 image. SFC viewport remains
separate metadata(x200,y30,w1720,h1020 in these cases). Future compositor must map
output to that viewport,not stretch it over the whole game display. Standard
ray-tracer samples at pixel+0.5;legacy native D3D9 oracle samples integer centers.
Independent asymmetric controls corroborate this difference;do not mutate geometry,
camera FOV,texture coordinates or copy SDK V flip to compensate. Saved USD camera
omission does not invalidate the now-measured runtime projection for these cases.

Actual depth matches native normalized projection within1e-6. Background is explicit
-1234sentinel;finite[0,1]depth distinguishes the ISOLATED one-ship coverage. Color
black remains valid,not a transparency key. PickingID0 appears on visible surfaces
AND background;ordinary picking values are NOT SDK selected-owner IDs. This
coverage rule does NOT separate overlapping ships/retained effects. Owner/session/
asset identity currently comes from the immutable source snapshot,not picking.

`returned-F-T.raw32`:little-endian uint32 width,height,then tightly packed4bytes/
pixel,top row first,T0=BGRA8,T1=float32depth,T2=uint32picking bit pattern. <=1920x1080
and exact byte size required. Source/EXE/runtime/output hashes and completion logs
are separate provenance. `pixel-analysis.json` compares actual output with native
composed-transform oracle under explicit viewport/sample conventions;it is not
an inferred camera from USD. PNG is diagnostic color copy,not appearance parity.

## Qualified and missing

CONFIRMED:shared GPU image return between different APIs/devices IN ONE process;
KFF/FCA and independent controls,known camera/object changes,source uploads,
color output and normalized depth. No live motion/cadence/latency,resource-pool
reuse protocol,stale/lost receiver,owner lifetime,cross-process/x86 consumer,
appearance/lighting parity,multiple simultaneous owners or in-game occlusion PASS.

Exact next action:standalone32bit D3D11 test consumer opens the64bit producer's
surfaces with explicit bounded completion/ownership and source-frame metadata.
Prove matching pixels and disconnect/retirement before live cadence/SFC integration.

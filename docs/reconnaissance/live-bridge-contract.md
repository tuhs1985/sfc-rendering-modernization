# Live ship bridge v1 — experimental local contract

New default-off multi-ship protocol3/component0.20 is documented separately in
[fresh scene contract](live-scene-contract.md),[probe](probes/LIVE-SCENE-001.md).
Old single-ship launcher/protocol2 below remain supported diagnostic baseline.

## Current extension — protocol2 / component0.19, camera-aligned mode

[LIVE-CAMERA-001](probes/LIVE-CAMERA-001.md) supersedes the live wire size/default
camera below; protocol1/0.18 text retained for actual historical runtime evidence.
Header version2,record96DWORD/384bytes at260 under same guard256. Prefix48 unchanged;
48 validcamera1;49–65 directview;66–82 projection;83–88 viewport x,y,w,h,half-w,
half-h. One atomic publication covers owner/model, supplied/composed and camera.
Native read/recheck also repeats supplied/composed after reading camera. Old live
versions refuse mismatch; old saved logs remain supported by offline analyzer.

Default prepared entry now follows SFC camera; explicit --fixed-camera retains
old diagnostic only. Camera controls in separate viewer disabled in aligned mode.
Near/far standard-perspective parameters reconstructed to reproduce P, not a
qualified returned-depth convention. Camera and model share nativeorigin/import
scale100. Three mesh points check direct S*P*V*M vs engineC and effective USD
scene-hierarchy+camera projection vs C (<=.25nativepixel), logged per update.
Viewer is tactical viewport crop scaled to fit, selectedship only; not whole HUD/
background/otherobjects or pixel-identical materials. Extra read payload160bytes
twice plus final object/composed check, no extra hook/I/O/engine calls in callback.
All original90s/2MiB/2700update/8MiB core output and cleanup limits unchanged;
expected bridge logs ~1–3MiB combined. Preparation originally left alignment
untested;[actual0.19 runtime](../runs/2026-10-16-codex-live-camera-runtime.md)
subsequently corroborated the selected-ship camera bridge. Full pixel/lighting
equivalence remains unproven.

Authority/scope/launch: [LIVE-BRIDGE-001](probes/LIVE-BRIDGE-001.md).
This transports observations to a separate installed Remix Toolkit preview, not
the game image. It is not a final renderer contract or aggregate TRL claim.

## Channel and publication

Creator: bundled Python supervisor, unique `Local\SFCBridge_<32 lowercase hex>`.
Pagefile-backed Windows mapping2MiB; protected DACL grants access only to the
current token's user SID. Native worker opens existing mapping; viewer read-only.
Header UUID words must match the explicit launch name. No global names/network,
process-global graphics/security changes or reliance on old native pointers.

All integers little-endian unsigned32; offsets below are bytes:

| Offset | Meaning |
| --- | --- |
|0|8 words: magic31424C53,version1,bytes2097152,state,4 UUID words |
|12|State0 awaiting worker,1 connected,2 worker stopped,3 failure/cancel |
|128,160|Two immutable asset descriptors: ready,mesh bytes,reference bytes,owner epoch;32-byte stride |
|256|Aligned seqlock counter; odd while worker writes, even when complete |
|260|48-word latest observation,192bytes |
|4096,528384|Two512KiB immutable mesh+reference payload areas |

Descriptor ready is atomically set last, after payload and metadata; never reused.
Worker wraps observation copy with interlocked odd/even sequence changes and memory
barriers. Reader accepts only equal nonzero even guards around a full record copy.
Latest observation replaces older ones; receiver has no backpressure/control over
SFC. Tests cover actual x86 worker/64-bit Python mapping, odd/incomplete guard,
read-only receiver, bounds, session mismatch and same-name rejection.

Observation words:0 publication sequence,1 owner epoch,2 render frame,3 elapsed
tactical milliseconds,4 state(active1/retired2),5 model label,6 source label,
8–24 raw supplied transform,25–41 raw composed transform,42–44 math dispatch,
45 asset slot; other words reserved0. Native pointer-shaped labels are opaque,
never remotely dereferenced. Session is mapping/header, not inferred from PID.
Unsupported nonzero dispatch rejects display; no invented alternate semantics.

Hook side uses fixed storage and TryAcquireSRWLockExclusive; busy mailbox drops
without waiting. Existing semantic-hook locking/state-preserving stubs unchanged.
At most one update/34ms (less than30Hz). Asset capture is fixed-storage guarded
read/recheck, at most two immutable attempts; existing read-only capture retained
independently. Worker alone serializes/writes files and channel. Drained callbacks,
worker joined, then mapping release; join timeout returns stop failure without
freeing live storage. Controller never unloads after failed M1Stop.

## Qualification and lifecycle

Initial known supported asset kff.mod:254positions/452triangles/1356corners/five
groups, ten exact registry-named original images. Fresh packet checksum/owner/
model/source/frame and source-group words must match fresh references. Signature
compares position/corner normal/UV bits, indices, polygon group/face vector/order;
does not hash process pointers or live resource IDs. References pair to accepted
template groups by filename and original SHA256, not incidental ID equality.
Files resolve beneath installed game root and retain original bytes. Captured
file data remains portable evidence even though hooks_restored=false while live;
post-stop cleanup evidence is separate, never falsified to qualify live data.

Imported job `C:/Project/RemixJobs/20261016-050350Z-6dffd5be` and its original
packet/ten images stay the baseline. No live reimport, conversion or GPU readback.
Mismatch produces partial/hidden display, never substitutes a different mesh.
Only fixed initial geometry is supported; deforming/damage/other models or LODs
are not silently treated as equivalent. Exact asset attempts capped at2; failed
attempt consumes a slot, and exhaustion requires review, not automatic retry.

Owner identity derives from existing owner table. Retirement or changed same-owner
model/source/list/count ends the display epoch. Reappearance needs a new immutable
asset qualification/slot. Consumer rejects retired or backwards display epochs,
bad identity/dispatch and nonfinite/nonrigid inputs; stale >=1s hides display.
Native model/source pointer reuse alone cannot revive a retired epoch. Two asset
epochs maximum; additional lifetime transitions remain hidden/PARTIAL.

## Matrix conversion and imported hierarchy

Native supplied17words are NOT a generic4x4. Interpret first three rows of four
floats as R and t for `p'=R*p+t`; word16 is metadata. Retain remaining float row
for evidence/finite validation, not as an assumed projective camera. Only sampled
proper rigid transforms admitted: row Gram/determinant tolerance1e-3; no repairs.
Static ship-specific provenance is supported, camera independence runtime pending.
Native34 source floats read/rechecked (both raw transform payloads, metadata kept).

For USD row-vector convention use:

```
[ R00 R10 R20 0 ]
[ R01 R11 R21 0 ]
[ R02 R12 R22 0 ]
[ tx-ox ty-oy tz-oz 1 ]
```

Origin is first accepted translation per fresh display epoch, rotation retained.
Apply session-only `xformOp:transform:sfcLive` to existing
`/ReferenceTarget/XForms/World`, above captured mesh and BELOW existing import's
uniform100scale at XForms. This keeps native translation and mesh scale consistent;
putting native translation at root would be100times too small. Root/local geometry,
axes, UVs, normals, face order and existing transforms are not rewritten. Read back
authored matrix every update; disagreement fails the viewer. Fixed camera frames
initial epoch once; Frame ship is manual thereafter, no continuous tracking.
Synthetic camera/light/provisional-emission approximation unchanged.

## Bounds and safe runner behavior

Entry `tools/m1_component/start_live_bridge_session.ps1` requires already-elevated
parent, builds/tests native component0.18 and owned-process guard, then runs
supervisor. No automatic RunAs/UAC. Viewer startup limit180s, total300s after build;
game launches only if viewer ready within45s, leaving a255s safe budget. Otherwise
partial/no game launch. Game discovery30s/tactical gate90s/capture90s/exit wait30s
plus overhead. Sponsor has90s for ordinary skirmish setup after discovery, not a
new timed camera exercise. Runner forwards ArmTimeoutSeconds to controller gate.

Defaults remain offline180s; only live mode requests native guard300s. Guard still
enforces256MiB scratch/8MiB Kit-console and kills only owned preview descendants.
Bridge core evidence is <=2700 fixed records + two<=512KiB assets + small bounded
summaries, below8MiB; SFC event limits/128MiB image bounds remain as probe.
Normal expected bridge evidence <2MiB; no frame image capture or multi-GB tracing.
On outer deadline, signal viewer disconnect; NEVER terminate SFC/controller while
hooks may be active. If cleanup still pending, record safe-park/partial and await
original controller's bounded stop; do not claim clean completion.

Replay mode `python tools/remix_ingest/run_live_bridge.py --replay` uses genuine
saved asset data with explicitly synthetic movement, retirement and fresh-epoch
pointer reuse. It never launches/injects SFC and never counts as runtime proof.

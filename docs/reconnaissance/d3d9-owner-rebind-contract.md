# Resident-asset owner rebind — experimental contract1

Scope:one unique configured model in the known two-different-ship fixture. Ordinary
D3D9 adapter,not a final renderer/ownership API. No original suppression. Existing
exact frame/session/owner/revision/state/sequence checks remain authoritative.

## Qualification and identity

Returning observation requires a fresh validated mesh/resource packet matching
current owner/model/source labels. Normalize geometry,LOD header20..22,group
flags,primary/secondary original-image SHA256 assignments and secondary-role
evidence into a full content SHA256. Resource IDs,pointers and packet provenance
are not content identity. Secondary ID0 is explicit absent association,not a
missing guessed glow image. Missing nonzero associations are unsupported.

Original image bytes are hashed once per unchanged file identity/size/timestamps
in this session;fresh packet signatures are cached. No decoding,conversion or
GPU asset creation during rebind. Changed content/LOD is unsupported by this
resident-asset proof,not silently displayed. Existing calibration8revision bound
and32owner observation table remain. Known player-fixture model name is NOT a
native player flag. Multiple current same-model owners are ambiguous and hidden.
Evidence clarification2026-10-21:the epoch is OUR observer's lifetime label.
CONFIRMED:our observer retires/reassigns it across an observation gap. This is
NOT evidence that SFC destroys/recreates the ship or changes persistent identity.
Sponsor's working assumption is that the same SFC ship persists across camera
changes;STRONG HYPOTHESIS:simulation/position updates continue offscreen,consistent
with reported tracking projectiles and fighter combat. This was not directly
measured in our offscreen capture. SPECULATIVE:offscreen ships continue through
the same rendering/submission path;simulation and GPU drawing must not be
conflated. The gap could reflect culling or our selected observation coverage;
the cause is unresolved. No confirmed native death signal or persistent game-ID
has been established. Do not turn observation absence into a game-lifetime fact.
A fresh identical model after pointer reuse is a NEW epoch,never revival of old
identity;generic persistent game-object ownership remains unqualified.

## Shared control

Separate versioned128byte control at mapping offset11MiB+112KiB,between existing
live-owner store and GPU pool11MiB+128KiB. Static bounds/layout assertions in x86
and x64. Existing16MiB current-user-only mapping and old live packet version stay
unchanged. No new external resource handle or on-disk game change.

| Bytes | Meaning |
| --- | --- |
| 0..31 | magic0x3142524f,version1,bytes128,session4words,gamePID |
| 32..35 | aligned request guard:odd writing,even committed |
| 36..63 | reserved zero |
| 64..103 | target:generation,owner,revision,model,source,reserved0,cookie64,checksum64 |
| 104..107 | worker acknowledged generation |
| 108..111 | rejected request count |
| 112..127 | reserved zero |

One Python worker producer,Windows x86/x64 aligned release stores;native worker
stable-snapshots guard with interlocked acquire barriers. Target checksum is FNV1a64
over first32target bytes. Generation must be exactly previous+1,in1..64. Full
SHA256 content comparison is Python authority;64bit cookie is a resident binding
token,NOT an independent cryptographic geometry proof. Worker requires same
session/PID,cookie,complete committed request and valid checksum/nonzero labels.
Initial binding generation1 must match prepared scene. Invalid/stale/skipped
generation does not change selected identity. Read/ACK are nonblocking.

Python recovery scan on one dedicated worker,with a2ms interruptible wait,only
after renderer started. This is a scheduling policy,not a guaranteed500Hz rate.
The worker exclusively drains fresh asset transfers and reuses their validated
decoded immutable packets;the main50ms runner loop does not concurrently drain.
Current owner rows
must be within8render frames of producer's current frame;stale status1 rows cannot
block recovery or resurrect ships. Existing selected active epoch takes precedence.
If absent,unique matching fresh content may request next generation ONLY after
fresh same-epoch lighting is staged. ACK confirms the selected binding;it does
not start another serial light-file handoff. A target that disappears before ACK still cannot display stale
pixels:current frame/owner observation remains required at composition.

Native worker adopts labels and atomically selects new owner/revision between
rendered submissions. Sequence watermark stays monotonic. In-flight former-owner
packets are discarded;delayed old completions/output cannot satisfy new exact
identity. Renderer,mesh/material/texture resources,scene hash and output surface
pool stay resident. No cached pixel hold,queue blocking or new SFC detour.

Fresh light observations also need new epochs. Existing two-slot collector frees
slots at observation retirement only for explicit live D3D9 mode;stale>400ms slot
reuse covers missed try-lock notification. Slots/capture queues remain fixed.
Every snapshot retains new epoch/model/source provenance;queued old snapshots may
finish writing old filenames but cannot qualify for new owner. This is NOT death
detection or retrospective light replay. Historical discovery mode unchanged.

## Run98 light transport and deadline admission amendment

Explicit default-off `SFC_D3D9_SHARED_LIGHTS=1` requires initialized stores before
hook installation and the existing source-timing/live-D3D9/light-tuning modes.
Same current-user16MiB mapping,not a new IPC security boundary:

| Offset / size | Contents |
| --- | --- |
| 15MiB /198720bytes | version1 raw store,32 epoch-modulo cells,each6208bytes |
| 15MiB+256KiB /1088bytes | version1 encoded Remix-adapter light packet |

Each64byte header carries magic/version/size,session4words,PID,stopped/published
counters and zero reserved words. Raw magic0x31524c53,encoded0x31454c53. Each
aligned cell has guardDWORD,reservedDWORD,captureQPC64,payload. Raw payload is
the unchanged6156byte native snapshot with explicit36byte tail padding;encoded
payload is existing200byte light packet plus808byte shapes packet. x86/x64
static layout checks. Odd/changing guard,wrong PID/session/epoch,stopped or bad
payload means unavailable,never wrong-owner fallback. Modulo collisions hide
the missing observation rather than cross-associate it.

Render callback adds QPC to its existing fixed8entry queue;no files,allocation,
viewer calls or waits. Existing native worker publishes validated raw snapshots
before diagnostic file writes. Python worker preserves original captureQPC when
encoding;polls never refresh age. Native renderer snapshots encoded cell directly
at submission,with existing checksum/context/shape/freshness validation. Light
sampling remains5Hz/owner,first fresh epoch unthrottled. Diagnostic native-light
files remain evidence,not delivery dependencies. Offline replay is still synthetic
and never used as a game fallback. Appearance/configuration unchanged.

Known-old input is rejected before projection/GPU submission and checked again
after lighting:source frame must still be current,not rejected,and offeredQPC
age<=2ms. This bounds admission age,NOT total GPU latency or display cadence.
Record expired/old-epoch counters;do not conceal omissions or hold stale pixels.
The source remains full-rate and output still requires exact current identity.

Recovery worker joins before renderer stop/mapping release. Failed join forbids
unmapping storage it may still use;error is retained,not called clean shutdown.
First-load preparation and vendor40-object teardown warning remain separate.

## Shutdown and evidence

At formal observation end:stop renderer via existing shared stop flag and wait for
owned exit;then wait for controller's gate-relative watchdog plus bounded35s
stop/unload allowance,never beyond overall workflow deadline. Previously15s from
formal end could precede controller120s trigger. Do not treat process exit as
controlled removal. Exit cue only follows required gate/bytes-restored/unload
checks. No new controller command/event or shorter recording window.

Record bounded generation request/ACK/rejection events,coarse Python-observed ACK
latency,full content signature and final128byte control in
`D3D9-OWNER-REBIND-001.bin`;old input/audit/GPU pool evidence retained. ACK latency
includes polling and is not first visible-pixel latency. Initial preparation
latency is NOT fixed by rebind. Rejection/ambiguity is explicit partial evidence.

Offline evidence combines native checksum/session/guard/generation/late-completion
tests,relay/content tests,actual standalone ordinary-D3D9/Remix output with two
synthetic fresh epochs,and actual native light observer queue tests. Synthetic
GPU lights remain labelled replay,not actual game lighting proof. Gameplay
camera-return and controlled-unload confirmation still require sponsor run.

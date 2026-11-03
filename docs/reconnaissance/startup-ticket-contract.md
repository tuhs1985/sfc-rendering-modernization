# Shared startup ticket — version1

## Bootstrap boundary

The published and current M1StartW read their existing INI configuration (including LiveChannel) before opening the live mapping. That order is unchanged. No ticket is used to discover LiveChannel,no M1 hook/configuration loader is changed,and no renderer readiness is required before M1 attaches.

The supervisor already creates the current-user-only protocol4,16MiB SceneChannel before starting the renderer. After verifying the game PID,it initializes the startup cell and passes the existing session name and game PID through the renderer environment. The renderer can open that mapping independently of M1's subsequent configuration/attachment. Fresh asset observations still precede ticket publication.

## Storage and ownership

A256-byte,64-byte-aligned cell starts at4096 in the existing metadata region. It ends before65536,where the four geometry transfer slots begin,and before the calibration region at32768. No mapping expansion,new named event,filesystem polling or access-control widening.

| Relative offset | Data / writer |
| --- | --- |
|0..35|magic,version1,bytes256,game PID,session words,supervisor PID;supervisor initialization only|
|36|aligned32-bit ticket state|
|40|host PID;host only|
|44|aligned32-bit readiness:0 -> -1claimed ->1ready;host CAS|
|48|ready QPC;host before ready1|
|56|published QPC;supervisor before Published|
|64..167|unchanged104-byte activation payload;supervisor once|
|168|accepted QPC;host after successful claim|
|176..255|reserved padding|

Ticket state:Empty0 -> Writing1 -> Published2 (single supervisor writer);Published2 -> Accepted3 or Rejected5 (native compare/exchange). Cancelled4 is supervisor cancellation after preparation/recovery workers have drained. A new cell cannot be initialized over a live initialized cell;existing session mappings are never reused while alive. A second host cannot claim an already published readiness slot.

Python follows the existing supported Windows x86/x64 aligned-store transport convention. Native readers use interlocked acquisition. Published ticket bytes are immutable. Partial Writing is never consumed;malformed complete packets reject. No state from the old session authorizes a new one.

## Validation and waiting

Validate global mapping/session/version/extent,cell layout/session/game/supervisor PID,then the original activation magic/version/104-byte length,PID/session,model/source,nonzero mask/cookie/content hash,reserved word,finite permitted offset,and FNV checksum. Native validation remains authoritative after transfer.

The host retains game and supervisor process handles. Existing10ms bounded idle checks now inspect only shared state;process termination wakes the wait immediately. There is one180s absolute startup deadline. Optional offline prefetch pump remains outside SFC and unchanged. No render-callback waits or new frame-rate limit. Before accepting,host rechecks liveness and atomically claims the published state. Invalid state/identity fails before scene submission.

Ready is published only after existing GPU warm-up. Enhancement priming reads that shared readiness without gating initial base delivery. Final reports carry bounded ready/published/accepted QPC receipts. Cancellation no longer creates a disk marker. Supervisor drains its service,stops native source,signals cell cancellation for an idle host,waits for owned host termination,then releases channel storage through existing cleanup.

No active workflow uses renderer-activate.bin,renderer-ready.bin or renderer-cancel anymore. Historical file-watching diagnostic artifacts are obsolete;the oversized file-filter observer was already retired. Disk configuration,scene files,texture handling,materials,lighting and actual frame/output protocols are unchanged.

## Qualification

See Run244 for actual x86/x64 consumer lifetime tests,normal Strict/ExtraFrame GPU startup comparison,cleanup and remaining post-activation delay. This contract does not claim every disk access or all startup delay has been eliminated.

# Run233 — persistent scene lights

Sponsor clarified that native lights0and1 are to be assumed always-on scene lights,and the configured GI light must likewise remain on. This is an explicit scene-role policy,not a new claim about unknown weapon/effect slots. Explicit configuration OFF and strength/type changes remain authoritative.

## Implementation

- The current D3D9 encoded light channel contains only native scene slots0/1 plus configured `project_fill`/GI. It now uses persistent-scene validation. After the first valid packet,light values persist for the session without the30-frame/500ms expiry used by timed owner-local lights. No observation timestamp is rewritten.
- Rebinding the scheduling ship does not retire these scene lights. New packets still require the current source association;retaining already accepted scene values is session-scoped. Configured ship-relative light positions are recomputed against the current model,as before. Scene persistence does not create lights from invented data before first qualification.
- The relay no longer requires fresh native enabled/consumed/global-gate state for established slots0/1 in persistent mode. Native type,direction/value validity and session/source provenance remain. Packet enabled flags come from the user's configuration,so explicit OFF is honoured. The same accepted companion shapes preserve the configured GI light.
- The relay's cached scene bank no longer expires solely from observation age or blocks scheduling-owner changes waiting for a new scene-light observation. Structural/checksum/finiteness and new-session separation remain. Default temporal validation for other callers remains unchanged;weapon/effect lights were not added or given scene persistence.
- No appearance values,TOML settings,geometry,client binaries,presentation policy or startup-toggle behavior were changed. One startup Present remains default;`-LegacyStartupWarmup` remains available.

## Validation

- x86/x64 light tests31checks each:long gaps and scheduling-owner changes retain scene0/1 and configured third light;explicit OFF removes its intended light;new-session identity removes all retained handles. Existing timed-expiry,wrong-owner,malformed-packet and recovery tests remain. Startup/submission policy12checks each unchanged.
- Python light suite47and native suite32pass. New tests cover native visibility gates versus explicit config enable,and scene-light readiness not blocking anchor change.
- Actual GPU/native insertion fixtures600measured frames each:Strict `20261031-201156-149903-return-fixture`,ExtraFrame `20261031-201330-237164-return-fixture`. Both exit0,all three owner instances inserted,two exact colour/depth/native effects/text checks,zero mismatches/state errors. Current frozen appearance remains. No SFC gameplay launched by agent.
- ExtraFrame initially could not start because the existing20GB evidence cap lacked its544MiB reservation. Generated DDS/fixture images from four closed successful runs were losslessly archived and decompressed/SHA-256 verified before exact loose-file removal;raw packets,timing/logs/results remain. Recovery receipts and compaction script are retained in `artifacts/player-replacement/run233/` and each run. The cap was not raised. The final ExtraFrame run passed.
- Native multi-ship qualification and non-executing preflight refreshed. Existing launcher remains the next sponsor checkout. Changes remain unstaged/uncommitted;client/appearance files remain unchanged.

This supersedes Run232's timed retention description **only for the explicitly designated scene-light channel**. Remaining camera/output timing and cloak support remain separate;this is not a claim that every gameplay fallback is resolved.

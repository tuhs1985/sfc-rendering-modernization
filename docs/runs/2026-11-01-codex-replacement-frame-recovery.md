# Run260 — Recover per frame instead of disabling replacement

## Change

Sponsor requested that routine replacement issues recover through native SFC drawing rather than shut down the enhanced scene. Implemented in the actual owner-qualified post-capture coordinator, preserving capture-first ordering, owner epochs and resource leases. [Recovery contract](../reconnaissance/native-replacement-recovery.md).

- Nested calls pass through without changing the outer operation.
- A changed owner/submission blocks only further suppression for that owner/frame; other ships continue. The normal next-frame reset enables a fresh attempt using retained assets.
- Genuine unwritable suppression arguments and unknown dispatch/GPU-resource failures remain terminal, now with bounded reason/frame/owner receipts. No other validity checks were silently removed.
- Present no longer logs old commits after terminal stop or repeated presentation of the same source record. Offline analysis independently filters historical duplicates; terminal flags cannot be hidden by earlier successful commits in the final report.
- Original assets, appearance, lighting, timeout/deadline policy, IPC sizes, GPU ownership, cleanup and scene registry are unchanged. Callback additions are rare-event fixed-storage counters; no callback I/O, allocation or waiting.

## Validation

- Actual x86 hook/component test: **82 checks**, including capture-before-suppression, primary/secondary lists, nested passthrough, independent owners sharing geometry, retirement without global stop, next-frame recovery, unknown later caller, and a deliberately read-only suppression-argument page that correctly triggers the remaining terminal protection.
- Native core: **1,216 checks per architecture**; membership: **193 per architecture**; pinned flush qualification12,300checks. Existing corner snapshot/fresh-copy tests pass.
- **48 focused Python regressions** pass: gate analysis, cohort qualification, early exit, controller lifetime, graphics startup and warm startup.
- Standalone actual GPU return checks: `20261101-215341-024405-return-fixture` (Strict), `20261101-215501-813131-return-fixture` (ExtraFrame). Each completed600measurementframes,3owners/2unique+sharedassets, two pixel/depth/text comparisons with zero mismatch, state errors0, terminalpartial0, repeatedrecords0, normal fixture/renderer exits and no remaining owned processes. Deliberate overruns exercise native fallback; measured commits536/600Strict and584/600ExtraFrame are not a claim of100% admission.
- Reanalysis of retained carrier evidence produces4,395unique records,4,338commits and714excluded duplicates, with explicit `PARTIAL_TERMINAL_STOP`. Original run files are unchanged. The exact historical stop branch remains unrecorded; this increment removes the recoverable terminal branches and records reasons for future events.
- Renderer host remains byte-identical `B0A157DE420975E7C199DC440E51204C797A7A7AEA44E20CF446F8A8A0E16D3C`; current appearance unchanged (lights `F6CC60D4C2671E8876820BD3A8CAEFB0740EFF64383C4CB15208AF27CD68D4DD`, rendering `78177E1D40498186B60C7912B46B897BA08D332DF4A24EA41F92C042E89202C5`). Native adapter and component are newly built/tested.
- Current cohort receipt refreshed from the two new GPU checks; standalone light-worker qualification and actual launcher preflight pass. Closed successful-run converted DDS/texture copies are losslessly archived with hash verification and recovery manifests to retain the existing20GB allowance. Original captures/client assets/logs preserved.

## Next action

Use the same native multi-ship launcher for a carrier checkout. It may be exited normally at any time. Review retry counters and confirm replacement remains active throughout camera changes and fighter arrivals/destruction. No new broad discovery trace, appearance tuning or loading redesign is required. This validates the correction in gameplay before moving beyond the established Remix integration. Alpha scope still separately includes weapon lights, damage textures and destruction break-model support.

No SFC launched during implementation. Changes remain unstaged and uncommitted.

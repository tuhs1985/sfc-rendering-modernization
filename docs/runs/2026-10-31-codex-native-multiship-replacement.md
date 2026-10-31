# Run228 — supported multi-ship native replacement prepared

Sponsor authorized extending the successful player replacement to other supported ships. Parent checkpoint: `ac0e7746df18585c9ce95e7a9a1ef55288cb87cb`. This increment is unstaged and uncommitted. No SFC gameplay was launched by the agent.

## Delivered

- Default-off multi-ship replacement uses fresh retained geometry/resources rather than an F-CA filename filter. The existing original-capture-first hook and native batch boundary remain.
- A shared completed scene carries exact rendered membership and per-pixel physical owner/depth coverage. Each owner inserts only its pixels at its own original primary mesh boundary. Successful insertion authorizes only that owner's primary/secondary suppression; unsupported owners remain native.
- Independent owner decisions, cached geometry sharing and whole-frame GPU leases avoid one renderer wait or extra output image per ship. Retirement/revision changes cannot borrow another owner's decision. Unexpected identity loss after a commit marks partial and stops new commits without attempting to undo GPU writes.
- Current light/material/image controls, zero-offset placement, native later shields/text, diagnostic launchers and parked shield replay are preserved. [Contract and bounds](../decisions/2026-10-31-native-cohort-contract.md).

## Focused validation

Native x86/x64 gate core: 1,216 checks each. New membership wire: 17 checks each, including distinct owners sharing content, missing membership, stale frame/hash/revision/source, duplicate owners, incomplete publication and pointer reuse. Pinned extracted native flush: 12,300 checks. Actual x86 capture/coordinator fixture: 59 checks, including capture-before-suppression, primary/secondary consistency, two owner identities sharing geometry and retirement after commit. Existing corner snapshot checks pass. Dedicated light/scene observer build and worker qualification pass. Receiver build passes its existing output/state/transport checks; Python native suite: 32 tests pass. Parser/preflight/diff checks are retained locally.

Actual ordinary-D3D9 → Remix → GPU-copy → native MSAA colour/depth fixture, two different captured meshes plus a third synthetic owner sharing the first mesh:

| Evidence folder under `artifacts/remix-runtime/runs/` | Policy | Measured frames | Committed frames | Native fallback frames | Per-owner commits, whole recording |
|---|---|---:|---:|---:|---:|
| `20261031-153309-707095-return-fixture` | Strict | 600 | 536 | 64 | 537 each |
| `20261031-153354-222050-return-fixture` | ExtraFrame | 600 | 580 | 20 | 581 each |

Both: all three owners have independent insertion/suppression receipts; two geometry loads plus one shared binding; no rejected/omitted draws in the renderer summary; two exact-pixel comparisons with zero mismatches and all three owners visible. Normally drawn far/near native effects and depth-disabled text are included. State errors, partial/invalid/ring drops are zero; both processes exit zero. Maximum pending gate and measured slot occupancy are one. No new output image is allocated for additional owners.

These are fault-injection runs: each has 16 deliberate 32 ms overruns and 31 representative 12 ms worker delays. Fallback totals exceed direct overrun counts, including following-frame effects and scheduling variance; they are not claimed to be entirely explained or representative of normal gameplay. Strict median/p95 presentation intervals were 16.895/17.563 ms; ExtraFrame 16.890/21.666 ms. These figures include deliberate stress. There is no claim of seamless ordinary gameplay from the fixtures. Native gate records are per frame, while cohort receipts count owner insertions/lists; do not compare those totals as if they were the same measure. The cohort unavailable field is a limited membership-admission counter, not a complete timing-failure count; use the gate records for timing failures.

The original player-only diagnostic was also rechecked, 600 measured frames each: baseline `20261031-153629-940889-return-fixture`, Strict `20261031-153702-796714-return-fixture`, ExtraFrame `20261031-153833-584470-return-fixture`. Both insertion cases pass exact colour/depth/order checks; baseline makes no insertions. Qualification receipts for both workflows are refreshed from actual evidence. Earlier sponsor-confirmed Run227 gameplay remains distinct historical evidence.

Local receipts: `artifacts/player-replacement/native-cohort-tests/qualification.json`, `artifacts/player-replacement/native-gate-tests/qualification.json`, build/test/console logs in the cohort test folder. Versioned qualifiers validate inputs; ignored receipts and proprietary packets are not staged. Both current source/compiled endpoint checks and the pinned backend remain required at preflight.

## Storage and cleanup

The existing 20 GB cap was nearly full. Closed fixture images and three completed game's derived DDS sets were compacted losslessly into verified ZIPs. Every entry was decompressed and SHA-256 checked before its exact loose copy was removed; per-run archive manifests preserve recovery paths/hashes. Raw movement/timing records, source captures, original images and client files remain. Scripts and selection receipts are retained in `artifacts/player-replacement/native-cohort-tests/`. This compaction is evidence maintenance, not an increased budget or discarded failure evidence.

No owned game/renderer/receiver/fixture processes remain after qualification. Accepted/copied client and current rendering/light settings hashes remain unchanged. Game cleanup must still be verified after the sponsor's new run.

## Exact next action

From the established elevated parent:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\native_insertion\start_native_multiship_session.ps1"
```

Use a skirmish with different supported models; repeated instances are useful too. Expect ships in their normal locations, not offset copies. Begin still, then change cameras, move/turn, briefly pause/unpause and expose shields. Exit at the usual two-beep request after the 90-second tactical window. Strict is the launcher default; `-TimingPolicy ExtraFrame` remains explicit, not a required second run.

Acceptance remains pending: all eligible visible owners replaced without doubling, stable camera transitions, correct native shield/text occlusion, unchanged gameplay/UI and normal cleanup. Unsupported assets or missing ships are partial results. Damage textures, weapon lighting, fast `_brk` handling, broader object families and arbitrary deformation are not implemented by this increment.

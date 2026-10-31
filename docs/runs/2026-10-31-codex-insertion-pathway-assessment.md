# Run225 — insertion pathway assessed against supported APIs

Sponsor requested the best pathway after reviewing the late-image/alpha-layer problem. Performed read-only source and Microsoft API research; no native hooks, binaries, renderer settings, qualification receipts or gameplay changed. Parent commit `0c82e01`.

[Decision, alternatives, supporting documentation and next increment](../decisions/2026-10-31-native-insertion-synchronization.md).

Recommended first qualification: separate, bounded event-driven frame coordination **before original mesh suppression**, after capture releases its lock. Reuse the existing worker's completed-output notification and native depth compositor. Explicit tradeoff: SFC's rendering thread can wait briefly, so this is a new optional policy to measure, not free latency or a change hidden in the capture callback.

Important source findings: output publication does not require suppression or SFC Present; frame receipts exist beforehand. Current game output is copied/fenced before READY, so notify from that edge. First selected-list decision must remain original until a matching completed lease and insertion submission are secured. Current native draw recorder holds its capture critical section and its existing drain counter ends before any proposed post-recorder coordinator; new coordination needs its own safe lifetime.

GPU queue waits are documented and worth keeping as a later option. Current pool surfaces are assigned too late for an advance wait; the Wait API does not provide a timeout. A reserved-surface contract and loss/cancellation policy are required before it is preferable here. Deferred command lists do not automatically record the game's existing immediate-context work. Restoring separate alpha layers from the final image is not available.

Retained analysis under `artifacts/player-replacement/run225`: ten source checks, hashes and copy/fence/publication order. Supported Microsoft sources linked in decision. No new runtime success claim, fixture campaign or sponsor discovery run. Changes unstaged/uncommitted; next action is isolated gate/depth-insertion qualification, then a prepared player checkout if it passes.

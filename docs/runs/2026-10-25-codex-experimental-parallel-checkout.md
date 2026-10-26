# Run182 — explicit sponsor checkout of parallel/progressive gameplay

Sponsor reviewed Run181's stable-path result and explicitly requests enabling the
new path for a real checkout. This authorizes an experimental live run despite
Run180's known delayed-material delivery limitation; it does not promote the path
to the normal default or relabel its failed offline gate as a pass.

Added opt-in `-ExperimentalParallelAssets` to
`tools/d3d9_proof/start_d3d9_multiship_session.ps1`, forwarded through Windows
PowerShell5.1 to the established modern/elevated parent. Python switch
`--experimental-parallel-assets` requires multi-ship/performance, explicitly
selects `progressive_scene_relay.Relay`, and passes `experimental_live_checkout=True`.
No switch still selects the stable legacy relay. Banner prints
`EXPERIMENTAL PARALLEL ASSETS ENABLED`; manifest and result both record the boolean.
Finish records parallel_parts, individual task spans, group-ready/stage-publication
events and experimental_live_checkout. Do not infer enabled status just from four
workers/performance mode; verify these new fields in the resulting capture.

Progressive relay now permits actual gameplay only with that explicit opt-in.
Its existing receiver/coordinator service starts after verified game launch,
before the first asset, to avoid the outer50ms loop limiting fine-grained tasks.
Main-thread poll delegates to that one service; renderer launch cannot start a
second service. Existing service shutdown/join protects storage lifetime. No SFC
callback, render-frequency cap, native hook/protocol, runtime/SDK, original assets,
shader/settings or suppression changes.

521main Python checks PASS, including13focused parallel checks (new single-owner
poll/idempotent-service/flag-forwarding/evidence checks). PowerShell syntax PASS.
Affected native-light worker qualification rerun PASS. Current-source standalone
stable-path fixture20261025-191727-004117-return-fixture:595/600delivery, no source
state errors, original HUD/scene exact, resize/recreation and normal owned exit.
Shared multiship native/source/binary qualification renewed via normal adjudicator;
no lock bypass. Experimental read-only preflight prints banner and PASS, no SFC
launched. Invalid opt-in without multi-ship is correctly rejected before launch.
This is NOT new live-service/SFC or non-disruptive progressive-consumption proof.

Sponsor command:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\d3d9_proof\start_d3d9_multiship_session.ps1" -ExperimentalParallelAssets
```

Use the same skirmish/ships for comparison. Observe time to extra ships, texture/
material arrival and flicker during camera changes; play normally and exit at
the usual two-beep request. Original drawing remains enabled. Existing90second
tactical/285second prepared/20GB and other capture/cleanup/hash rules retained.
Known late-material interruptions explicitly remain possible; no artificial
material delay is injected into this live run.

HEAD9ff2d3d; all changes unstaged/uncommitted, no push. Prior working changes and
evidence preserved. No owned test process/channel remains. Next exact action:
sponsor runs the opt-in command, then review new flag/task/publication/first-output
evidence and sponsor observations before any default promotion.

# Break-piece observation

Use the existing Administrator PowerShell. Enter a familiar two-ship skirmish
without fighters, destroy one ship in view and keep the debris visible briefly.
Exit normally at the two-beep cue. The tactical observation lasts 90 seconds.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\break_probe\start_break_session.ps1"
```

The separate x86 observer reuses the early-model supervisor, verified game copy,
bounded channel, process identity and hook restoration checks. It launches no
Remix renderer and leaves native ship and debris draws enabled. The normal
launchers do not load this variant.

The seven added hooks observe the factory at `0x0041455B`, child constructor at
`0x0041B657`, child draw scope at `0x0041B900` and indexed visual submission at
`0x0042FE7E`, polygon wrapper at `0x006AC5A0`, simulation update at
`0x0041BA0F` and destructor at `0x0041B8B4`. The first qualified tactical handoff selects one ship. Each child
is tied to its constructor, visual and piece index. At indexed submission the
probe reads the manager's supplied and composed transform snapshots after the
draw's setter call. It retains at most 128 children and eight samples per child.
The wrapper joins the actual native count and list to the indexed polygon range.
It snapshots fresh piece geometry and texture associations using preallocated
storage. A worker writes up to four 2 MiB diagnostic geometry packets and their
reference manifests. This diagnostic capacity is independent of production
scene limits. A larger break model remains partial.

Evidence goes under `artifacts/remix-runtime/runs/break-*`. The trace limit is
16 MiB with an 8 MiB warning, plus 32 MiB ancillary storage and the existing
20 GB aggregate check. The prepared workflow is bounded at 285 seconds.
The updated observer carries mesh payloads and texture filenames. Original
image files remain on disk. It stops early once all pieces in a break model
of up to four pieces have snapshots, eight pose samples and destructor receipts. Otherwise the
90-second tactical limit applies.

Build with `tools/early_model_probe/build.ps1 -BreakProbe`. Use
`start_break_session.ps1 -CheckOnly` for preflight. The strict x86 build and
preflight were verified. Twenty-nine native range, registry and simulation-pose
checks pass. The previous live checkout qualified four FCA pieces, changing
poses, fresh geometry and image associations, and restoration of all fourteen
previous hooks. The parent timed out waiting for game exit after completion.

The new sixteen-hook variant records up to 512 simulation updates per piece,
raw state paired with draw transforms, a full camera observation per sampled
draw, predicted pose comparisons and destructor receipts. Its raw state stores
the initial 17-word transform, current position, pivot and two native angular
fields. The pose calculation follows the native bias-plus-bitmask angle
conversion and native sine/cosine table lookup. Live comparison is pending.
Unfinalized old captures decode as partial without changing original headers.

For the next checkout, self-destruct one FCA with a wingman present. Briefly
switch away and back while debris is alive, then keep playing until the exit
request. Exit normally when requested so the parent can record game exit.

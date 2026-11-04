# Damage-layer observation

Default-off, separate x86 observation DLL. Reuses the existing early-model
observer's startup, current-user-only control mapping, lifecycle registry,
nonblocking ring writer, Detours transaction and automatic tactical gate.
The normal M1/Remix binary and launchers are not replaced or rebuilt.

## Run

From the established Administrator PowerShell, with the previous copied game closed:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\damage_probe\start_damage_session.ps1"
```

Enter the familiar F-CA skirmish within 120 seconds. Let **hull damage** develop;
shield hits alone may not activate the damage textures. Increasing game speed
is fine. Briefly rotate the camera after damage appears. Destroying your ship
is unnecessary. Exit normally at the two-beep request after 90 tactical seconds.

SFC draws normally. **No Remix replacement appears during this observation.**
No screenshots, manual timestamps, Toolkit, extra wrapper or security changes.
`-CheckOnly` performs preflight without starting the game.

## Captured information

- Named visual loading, attachment, owner/visual epochs and retirement, using
  the existing nine semantic hooks.
- Model-entry damage-selector bits and family, primary/secondary list identity,
  polygon count and invocation token/QPC, emitted on state changes.
- Existing polygon-wrapper boundary `0x006AC5A0`, known callers
  `0x0042E55D` and `0x0042E626`. Original arguments/results pass unchanged.
- Selected material's nine words **copied during the callback**, including its
  resource pair; four raw manager words at `+0x1EC8` are recorded without
  labelling them D3D blend factors.
- Eighteen resource-table IDs from the qualified acquisition slots, joined to
  the original filename/hash inventory in the same process. IDs are not pointers.
- One immutable secondary mapping per observed visual epoch/model/list: positions,
  polygons and separate corner UVs/normals. Portable corner ordinals replace
  native corner pointers in the saved packet; source data is never changed.
- First lazy mapping creation before/after model return, proving ordering relative
  to the primary pass. Model tokens identify invocations, not presentation frames.

Pure black transparency on damage images is established from the sponsor's
authoring experience. It is not a question this run needs to re-prove. Ordinary
hull black markings remain opaque. Exact native blend/filter/companion behaviour
remains an offline correlation task; opaque manager words alone cannot prove it.

## Bounds and cleanup

16 MiB metadata, warning at 8 MiB; 2,048 preallocated ring cells. Four preallocated
mapping slots, each below 2 MiB: at most 8 MiB mapping output. This is an
**observation capacity**, not a new ship limit in the integration. Additional
mappings or busy slots produce counted omissions and a partial report while
original SFC drawing continues. No original texture-image bytes are dumped.
Each mapping permits 65,536 positions, 8,192 polygons and 32,768 corners.

Native callbacks use guarded reads, fixed storage and try-locks: no file access,
allocation, renderer calls, decoding or observer waits. A worker writes immutable
mapping slots and metadata. Stop detaches all ten hooks, drains callbacks before
the terminal receipt and closes files. The DLL remains loaded for the copied
process lifetime. The existing bounded runner checks accepted/copied client and
launcher settings before/after, requests normal exit, stops its own control host
and leaves no deployed proxy to remove. Early process exit may leave a partial
trace; it never starts a second game beside an existing SFC process.

Retains the existing 20 GB admission check, 112 MiB reservation, 48 MiB per-run
file ceiling and 285-second supervision deadline. Evidence is under
`artifacts/remix-runtime/runs/damage-*`: `manifest.json`, `damage.bin`, up to four
`damage.bin.mapping-N.bin` files, inventory, launcher/host logs and `result.json`.
Missing damage activity is an explicit partial result, not a failed game run.

## Local qualification

```powershell
& tools/damage_probe/build.ps1
& 'C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B tools/damage_probe/run_probe.py --qualify
```

Qualification uses synthetic native functions and an actual startup-injected
standalone executable, not SFC. It requires exact callback/transport/decoder
receipts, two observed asset epochs, copied stack material, exact secondary UVs,
native return/LastError/SSE preservation, and byte-exact ten-hook restoration.
Source/dependency/binary hashes invalidate stale qualification automatically.
The `SFC_DAMAGE_PROBE` build guard removes the extension completely from the
normal nine-hook early observer. Normal renderer settings remain unchanged.

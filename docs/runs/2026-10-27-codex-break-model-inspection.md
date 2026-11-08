# Run212 — inspect the existing _BRK model path

Sponsor identifies destruction model as the `.mod` file with `_brk` in its name.
Bounded read-only asset/code/evidence inspection confirms this identification.
No game launch, hook, renderer change, asset export or implementation. Documentation
changes remain unstaged/uncommitted. Earlier alpha-scope note remains in force.

## CONFIRMED

- Installed `Assets/Models/fca/FCA_BRK.MOD` exists:757,968bytes, SHA256
  `1b8ca3e0321b174240657ee3c799cfa13c5e91bc6e401c8ae03c2f848d3e5a90`.
  Normal FCA is758,572bytes. KFF break model69,068bytes versus54,756normal.
- The four inspected files have `MDLS` containers and bounded top-level `STRS`,
  `MATS`, `MOD0` chunks. The normal examples also contain `PNTS`. This is a chunk
  inventory, not decoded break-piece boundaries, piece counts or animation data.
  No texture filename extension in STRS does not mean missing textures; those
  string tables contain material/image stems and other labels.
- Existing [early-model static evidence](../reconnaissance/early-model-availability.md)
  identifies suffix `_BRK.mod` at0083CBAC. After attaching the primary visual,
 0041579D requests the suffixed name through0042F39A;004157A8 passes its returned
  visual to0053F2D6. Read-only pinned-client verification confirms0053F2D6 stores
  that argument at **ship+0x8C**, distinct from the primary visual at+0x88.
  No new interpretation of arbitrary fields or new whole-function hook.
- Client SHA256 remains
  `4d65761d7dd69ef1504070261b81e9c200c0af18105033e1c4d2222c62320c29`.
  Local disassembly was read only in the already mapped setup/secondary-model
  neighborhood. Proprietary code excerpts are not added to this record.
- Crucially, the existing
  [Run177 timing result](2026-10-25-codex-early-model-timing-result.md) already
  records successful **FCA_BRK and KFF_BRK loading during ship setup, before the
  first tactical render gate**, associated with their corresponding ship owners:

| Asset | Native load duration | Completion before tactical gate | Source groups | Missing referenced image IDs |
| --- | ---: | ---: | ---: | ---: |
| FCA_BRK |36.1396ms|30.1368ms|58|0|
| KFF_BRK |7.1914ms|6.6709ms|5|0|

These are native model-loader observations, not Remix readiness or destruction
presentation timings. Both observed break assets had one loaded LOD. They were
distinct asset epochs, not additional living ship owners. This corrects the
earlier uncertainty about whether a separate break asset is selected at all.

## STRONG HYPOTHESIS — useful implementation opportunity

Capture the successfully loaded break asset from SFC and prepare/cache its backend
resources while the normal ship is alive. Destruction could then activate retained
resources rather than begin a cold geometry/texture load at the explosion.
This uses fresh SFC-loaded data, not conversion of the installed MOD file into
our renderer. Original files were inspected only for inventory/format context.

Earlier acquisition still needs a safe immutable snapshot/lifetime boundary;
the existing render-seam collector expects manager context that the loader lacks.
Do not fabricate that context, invoke SFC rendering to obtain it, call native
load/refcount functions on our worker or assume a pointer remains valid.

## Still unqualified

Exact destruction activation, break-piece partitioning, per-piece movement,
ownership/lifetime after the intact ship retires, applicable capture/render paths,
and prompt backend display. Do not equate a `MOD0` chunk/LOD count with one debris
piece, or assume the existing single-rigid-instance path handles breakup motion.
Two preloaded examples do not establish universal preload behavior or a complete
mission roster. Prior destruction captures may already help; review before
requesting a new discovery run. No numeric alpha loading threshold is set here.

**Exact next action:** keep the prepared player-replacement test unchanged. After
its result is reviewed, qualify early fresh capture/retention of the already-loaded
`ship+0x8C` break visual and identify the destruction piece-transform/lifetime path.

## November 6 follow-up — carrier evidence and break-piece creation

- Run259 retained 14 calls to the ship-destroy hook and seven tracked registry
  retirements. The event CSV contains only its header, the identity census was
  off, and the 29 mesh/resource manifests contain zero `_brk` filenames. The
  counters establish native destruction-hook activity, but do not identify which
  hulls or fighters retired, or give first-draw and piece-transform records.
- Run259's paired rejected visual/model samples at `0x00413B2D` and
  `0x0042FDD5` do not establish debris. The upstream call that returns to
  `0x00413B2D` reads the primary visual at `ship+0x88`.
- Read-only disassembly for the pinned executable identifies a separate
  handoff. The conditional call at `0x0041674F` passes the ship and its
  `+0x8C` break visual to `0x0041455B` and clears the ship slot afterward.
  The factory calls `0x0041424A`, which copies the ship's 17-word transform
  into the new object. With a non-null visual it obtains a count via visual
  vtable slot `+0x50`, loops over indices, and passes the visual and index to
  `0x0041BAB6`. That helper allocates a separate object and calls
  `0x0041B657` for each successful construction. The parent path registers
  successful children. The current copied executable SHA256 matches the pin
  above. These are static relationships, without a runtime piece count,
  per-piece pose stream or qualified draw/suppression boundary.
- Next trace `0x0041B657` through the child update and draw slots offline.
  Then, if retained evidence cannot qualify the join, observe only the
  parent/visual/index, first draw and changing child transform. No repeat
  carrier stress run is needed.

### Break-piece update and draw slots

Read-only PE section mapping of the pinned copied executable resolves the
child vtable at `0x007972B4`. The constructor at `0x0041B657` stores the break
visual at child `+0x9C` and the piece index at `+0xA0`, and copies the initial
17-word pose into child `+0xA4`.

- **Update, slot +0x08 → 0x0041BA0F.** Uses child-local elapsed time and motion
  fields to update position and angular state, with an age-triggered virtual
  call through slot +0x10. Exact retirement semantics remain unqualified.
- **Draw, slot +0x0C → 0x0041B900.** Builds a per-piece render transform
  from the child state and sets it through the graphics manager at
  `0x0041B9E0`. Then `0x0041B9FB` submits the visual, piece index and mode
  through visual slot +0x20. The known visual vtable `0x007985A4` maps this to
  `0x0042FE7E`, which forwards to the backing model's virtual slot +0x10.
  This is a distinct branch from the intact visual's +0x18 path.
- **Scope.** The retained carrier manifests contain no break meshes. No exact
  constructor, update, draw-return or handoff-return address matches were found
  in the retained second render-family survey JSON. That bounded survey sampled
  downstream activity, so absence does not rule out debris in gameplay.

The next qualification can be a bounded, default-off observation of the
handoff, first indexed draw and a short sequence of draw-time transforms from
one destruction. Observe the effective transform at the setter and join it to
the indexed draw. Keep original drawing intact. The backing-model geometry
partition and output coverage must be qualified before suppressing native debris.

### November 6 live break observation

The sponsor destroyed a ship using the isolated break launcher. Capture
`artifacts/remix-runtime/runs/break-20261107-042142-337901/break.bin`
contains 160 complete records in 82,048 bytes. Its header was not finalized
and no result report was written. Preserve the raw file. A separate
`break-recovered-review.json` records the recoverable observations.

The first qualified handoff is owner epoch 4 and visual epoch 15, resolved
through same-run loader records to `assets/models/fca/fca_BRK.mod`.
At 41.3906 seconds after observer startup, four children were constructed with
indices 0–3. All four produced eight indexed draw observations with eight
distinct supplied transforms each and zero record flags. First draws followed
the handoff by approximately 2.3–6.5 ms. These are native observations,
not Remix load or presentation latency.

The game launcher records normal child exit, code 0. Last retained observation
is at 86.1213 seconds after startup, before the 90-second tactical deadline
(tactical gate was at 18.1123 seconds). Hook restoration and observer shutdown
are unverified because terminal records and the finalized header are absent.
A return_host helper with the matching launch time remained alive at review.
After the sponsor interrupted the probe, no return_host or SFC process remained.
The reason the parent did not finish its exit handling remains unresolved.
This completion defect does not invalidate the complete breakup observations.

### Initial piece capture implementation

`tools/scene_bridge/break_piece.h` now reads the lazy native partition layout.
In the pinned indexed draw at `0x0042E9D6`, model+0x30 contains cumulative
polygon ends and +0x34 contains the piece count. Piece zero starts at zero;
later pieces start at the preceding end. The submission returning to
`0x0042EA92` uses this subrange of model+0x14, with original shared positions,
corner normals/UVs and source groups. The secondary path returns to
`0x0042EB34`; it is outside the new primary snapshot.

The default-off break observer now snapshots a primary subrange into the
existing portable mesh packet and captures its original texture associations.
Worker output is separate from callbacks. The initial diagnostic holds four
preallocated geometry snapshots and retains the existing eight poses per child.
It automatically requests restoration after all four FCA pieces are captured
and sampled. The ordinary replacement path does not yet load these packets.

Fifteen native checks pass for cumulative ranges, exact polygon/group/corner
membership, checksums, stale lifetime, bad indices, malformed boundaries and
unprepared native layout. Strict x86 observer build and read-only launcher
preflight pass. The original partial live capture now decodes while explicitly
reporting unverified cleanup. The geometry snapshot and early completion need
live verification. Exact blocker to renderer integration is the missing fresh
piece geometry/resource capture; use the same break launcher for one visible
FCA breakup. Do not weaken the live-scene parser's intact-ship origin check to
admit unqualified break data.

### Second live capture — fresh piece geometry verified

Run `break-20261107-044811-246216` has a finalized trace with no decode issues,
all fourteen hooks restored, no active callbacks and no hooks left installed.
Four geometry packets and matching texture-reference manifests are present.
The retained `geometry-review.json` independently verifies checksums, array
sizes, triangle/corner indices, finite corner values and group assignments.

| Piece | First polygon | Triangles | Material groups |
| --- | --- | --- | --- |
| 0 | 0 | 2923 | 27 |
| 1 | 2923 | 889 | 19 |
| 2 | 3812 | 889 | 19 |
| 3 | 4701 | 1669 | 18 |

The ranges cover 6370 triangles contiguously without overlap. All packets carry
the same 3497 original positions. All four reference manifests resolve to
`assets/models/fca/fca_BRK.mod`; 84 unique referenced image files exist in the
test copy and their SHA256 values are retained in the local derived review.
This verifies fresh primary geometry/resource capture, not a rendered Remix
debris result or secondary-path equivalence.

The automatic observation completed and finalized successfully. The parent
subsequently timed out waiting for normal game exit within its 30-second exit
window. Result error is `Normal game exit not confirmed`, host exit is 0 and
original/copied client and launcher-setting checks all passed. No SFC,
return_host or return_launcher process remained at review. Keep this exit-window
failure separate from confirmed native restoration and valid captured geometry.

The prior missing-geometry blocker is resolved for this FCA example. Next admit
the qualified piece origin through a dedicated conversion entry point, reuse
the shared asset positions/material resources, and track each debris child
independently of the retired intact owner. Preserve native drawing until the
piece's matching output and suppression boundary are qualified.

`tools/remix_ingest/break_scene.py` now provides dedicated break-piece
conversion using the existing mesh decoder. The normal decoder retains its
intact-ship origin check. The new entry joins each piece to the live handoff,
visual, owner epoch, child pointer, piece count, polygon range and association
manifest, and verifies complete partition coverage and shared positions.
All four actual packets decode without changing geometry or UVs. Wrong child,
index, count and association status are rejected in focused checks. Three
existing mesh/image decoder regressions pass.

The wider legacy preview suite was also attempted. It remains unsuitable as a
blanket gate here because it expects the removed C:/Project/RTXRemix Toolkit
tree and its shared-memory tests fail with access denied in the restricted
session. Those failures are recorded separately from the passing focused decoder
checks; no full preview/native transport regression pass is claimed.

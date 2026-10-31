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

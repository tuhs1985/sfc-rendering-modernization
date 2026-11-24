# November 23 — opaque, fitted UE inspection display

Sponsor's successful live run `20261123-224302-717753-in-game` received 3275
snapshots, two assets and 94 original images, then exited and restored normally.
Its UE window showed black outlined ships near the upper-left. This was not
accepted as a completed visual checkout.

## Reproduction and fix

The pinned public UE `EngineTypes.h` defines `SCS_SceneColorHDR` as RGB scene
colour with **inverse opacity** in alpha. A normal alpha-blended Slate image
therefore hides opaque ship surfaces. The old widget also placed a native
1720×1020 tactical image at (200,30) inside a requested 1280×800 inspection window.
The independent source RGB checks never tested that displayed widget.

Added explicit diagnostic `SFCInspectionCheck`: public
`FSlateApplication::TakeScreenshot` reads the actual inspection widget once,
separately from target RGB readback. Before the fix,
`inspection-visible-red-01` fails with displayed/source coverage IoU **0.0000**.

`SFCInspectionView.h` now uses public Slate `IgnoreTextureAlpha` only for the
inspection draw, backed by an opaque black panel. It draws the complete tactical
image centrally at a uniform aspect-fit scale. Current target dimensions are
read when painting, so target resize does not depend on an old brush extent.
Offline and live-registry inspection use the same widget and Exit control.
Source viewport offsets retain their original meaning in native output; they
are not reapplied as window offsets. No capture source, camera, mesh, image,
material, depth/owner export or insertion behavior changes.

## Verification

`qualify_inspection.py` compares actual widget coverage to an independently
resized capture, excluding the Exit-button strip. It fails empty coverage and
requires IoU >= 0.88. These are bounded diagnostic readbacks, never normal play.

| Package / window | Target | Coverage IoU |
| --- | --- | --- |
| Shipping 1280×800 | 1720×1020 | 0.947590 |
| Shipping 960×960 | 1720×1020 | 0.930474 |
| Development 1280×800 | 1720×1020 | 0.947590 |

The source target's RGB bytes compare identical before/after the widget fix.
The BMP comparison does not establish alpha-byte identity; alpha is preserved
by leaving the capture target and its producer untouched. The new widget only
changes how Slate draws it into the inspection window.

`source-service-inspection-01` also passes actual transfer/ACK, original image
preparation, catalogue admission and 20 completed Shipping GPU samples with one
mesh. Both configurations build; read-only live-launch preflight passes.
Some obsolete intermediate image copies were pruned only after exact SHA-256
comparison, 82,800,216 logical bytes; retained aliases are recorded in
`inspection-evidence-aliases.json`. All actual window images and current inputs
remain. The 20 GB evidence/reservation check passes.

The same live command is ready for sponsor confirmation. No SFC gameplay was
started for this fix; task 3.5 stays open until the corrected window is confirmed.
All changes remain unstaged/uncommitted.

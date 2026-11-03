# Run280 â€” Toolkit sphere-radius inspection

The initial fixture lacked Toolkit project dependencies and capture/replacement layers. The MCP open call returned OK but the UI correctly requested project setup. Do not interpret MCP request acceptance as successful workspace opening.

Corrected isolated project: `artifacts/player-replacement/run280/radius-comparison.usda`. Contains an empty replacement working layer and an explicitly synthetic capture wrapper referencing the diagnostic scene. Local deps and mods links use NVIDIA's documented installed project-wizard convention; installed vendor code and game configuration are unchanged. The mods/run280 junction points back to this fixture directory: do not recursively follow junctions when measuring or archiving it.

Opened the Modding workspace and InspectionCamera through the Toolkit UI. Visually verified four FCA hull copies and light guides render. Screenshot: `artifacts/player-replacement/run280/toolkit-comparison.jpg`. Toolkit remains open for inspection. Its local MCP endpoint communicates and exposes 35 project/layer/material/reference tools; this tool inventory has no screenshot or general light-attribute interface, so viewport inspection uses computer-use.

Source and synthetic emitter placement are recorded in radius-scene.json. Geometry comes from the fresh LIVE-SCENE packet, not a game-folder MOD conversion. Radii left-to-right: 0.01, 0.05, 0.25, 1.0. All centers are 0.05 native units beneath the same selected triangle. Grey diagnostic material and intensity100 are deliberately not the gameplay appearance baseline. Guide icons and camera distance currently limit useful visual comparison; no quantitative occlusion/illumination acceptance is claimed.

This establishes a working visual inspection environment, not the cause of the invisible weapon lights. Actual hardpoint burial remains unproven: the last performance run did not retain contemporaneous ship poses for its active-light frames. Next: isolate a close hull/light view, remove viewport icons from comparison, and compare exposed sphere area and resulting hull illumination using controlled placement. Then correlate actual game light and ship transforms if needed. Do not move native light origins or change normal integration based solely on this synthetic fixture.

Changes remain unstaged/uncommitted. Normal runtime and settings untouched by this inspection.

## Live radius checkout — November3

Sponsor selected effect radius0.05 for the next live run; only [effects].radius changed from1.0. Existing scene/fill lighting and effect intensity/color remain unchanged. Read-only ExtraFrame multi-ship preflight with LightDiagnostics passed. Temporary Toolkit deps and mods/run280 junctions were removed after inspection because recursive evidence scanning follows them; targets remain. The loaded Toolkit scene may stay usable, but reopening requires a nonrecursive project arrangement. No game was launched by this preparation.

# Current sponsor-approved temporary appearance baseline — 2026-10-19

HISTORICAL / SUPERSEDED by [2026-10-19 revision2](../20261019-sponsor-temporary-appearance-r2/README.md).
The original checkpoint text and exact configuration copies below remain intact.

AUTHORITATIVE appearance checkpoint: sponsor explicitly designated the current
settings as the new temporary baseline after reporting improved appearance and
providing a screenshot. This supersedes earlier tentative appearance snapshots
for future tuning/restoration, NOT requirements, factory defaults or runtime gates.
Historical snapshots remain intact. Full four TOML files here are authoritative.

These are byte-identical copies of active tools/remix_runtime/config files.
No active configuration was rewritten. No screenshot containing desktop/chat
content was copied into the repository. Sponsor observation is visual evidence,
not a measured native-SFC parity or washout-cause determination.

| File | SHA256 |
| --- | --- |
| lights.toml | 01BB042A29FFE379BF40E5DBD95B11670D2FAC927BEB846375ACFF9BE94240AA |
| materials.toml | 4C5EA9BF8330188B3F89CF2007278509AD7F652CDF5AC1CF29AE09EA54446728 |
| image.toml | C71366DFABC1DB06BA380DC89A392DD3D2611EF579464A3930F90A5634C581CE |
| quality.toml | 89FD0A280ACF3D80194A274E3B33BD72CBF29E3D9ED53D453FC45DC4EC526D40 |

Key values: uniform roughness0.2,illumination5,metallic0,anisotropy0;
generated roughness ENABLED,strength0.9,black0,white1,invertfalse,gamma1.
Image enabled,local tone mapping,automatic exposure OFF,brightness50,EV0,
contrast1.12,gamma0.7,saturation1.2. Quality enabled,requested16x anisotropic,
mip0,AAoff,denoisingon,supersampling1. Lights conversion1/master1;both native
directionals enabled,multipliers1,angular diameters10/17degrees. Full files also
preserve independent project-fill and dormant shape settings without guessing.

Validation: hashes match active sources;all four files pass current TOML/schema/
range validators. No new build/GPU/gameplay run needed for a snapshot-only task.
Run59 native/return qualification remains unchanged;generated roughness remains
an artistic approximation. No independent opaque specular control exists here.

Restore only when requested:copy the desired file(s) from this directory to
tools/remix_runtime/config using the same filenames. Save/reload with the existing
light-tuning runner,or use on next launch. Do not copy older tentative baselines
over these settings automatically. Keep future tuning changes separate from this
immutable snapshot;create another dated checkpoint when approved.

# Current temporary appearance baseline — 2026-10-19 revision2

Sponsor requested this updated baseline. Exact copies of all four current tuning
files;active settings were NOT rewritten. Supersedes the prior
20261019-sponsor-temporary-appearance checkpoint for future comparison/restore.
All older snapshots remain historical evidence,not current tuning authority.

| File | SHA256 |
| --- | --- |
| lights.toml | 01BB042A29FFE379BF40E5DBD95B11670D2FAC927BEB846375ACFF9BE94240AA |
| materials.toml | E76E67D5E68F3CCBD33EF1EBFBBF048DBFF30F7CEAC6E28A25E9F4604B1F9B02 |
| image.toml | C71366DFABC1DB06BA380DC89A392DD3D2611EF579464A3930F90A5634C581CE |
| quality.toml | 89FD0A280ACF3D80194A274E3B33BD72CBF29E3D9ED53D453FC45DC4EC526D40 |

Changes from prior snapshot:roughness0.2→0.4,metallic0→0.2,anisotropy0→0.5,
generated roughness-map gamma1→0.4. Other material values unchanged:illumination5,
map enabled,strength0.9,black0,white1,invertfalse. Lights/image/quality files
byte-identical to prior snapshot. Full files,not this summary,govern restoration.

## Correction: observed light versus its cause

CONFIRMED sponsor observation:an apparent light contribution was seen during
tuning. Sponsor now clarifies that illumination maps were not isolated as its
cause;metallic response may also have contributed. SPECULATIVE:the precise
interaction between emission,reflections,metallic response and other settings.
No controlled comparison isolated those variables in this documentation task.

Known implementation remains:the primary*secondary derivative is wired to Remix
emissive input. That does NOT prove every observed bright/reflected contribution
originated from that map. Metallic response changes reflection/diffuse behaviour;
it is not automatically another emitting light source. Earlier wording attributing
the observation specifically to illumination maps is historical and too strong.
No new native SFC light,physical calibration or native visual-parity claim.

Restoration when requested:copy desired TOML file(s) back to
tools/remix_runtime/config with unchanged filenames;save/reload using existing
tuning runner or use on next launch. No factory default changes. Keep this
snapshot immutable;future approved tuning gets another checkpoint.

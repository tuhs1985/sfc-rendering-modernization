# First public Remix alpha

November 18, 2026. Sponsor authorized committing current work and publishing
the existing alpha, with explicit requirements and single-machine qualification.

## Source checkpoints

- `43df260`: packaged UE proof, review, insertion plan and related continuity,
  committed locally on `codex/expand-rendering-interface`. No UE runtime or
  captured assets enter the Remix release.
- `e747bd34e5d69c2434edd099232a5b59df784d50`: public alpha preparation from
  merged `370accf`, branch `codex/publish-alpha-1`, tag `v0.1.0-alpha.1`.
  This is the public package's source reference.

## Package and provenance

Promoted the exact qualified private candidate, SHA-256
`b1c992f442cf2ba178029b8e3444e2da93a0123daa4532bcc2d8eecbd61725c1`.
Its 3,884 immutable files were verified. All vendor bytes/provenance matched
the reviewed merged candidate with complete recipe review. All 64 packaged
application modules matched the release commit after UTF-8/line-ending
normalization. The only native source change since the inherited build is
the startup-status launcher, identical to qualified source `69a682d`.
The other native binaries retain build lineage `e450c30`; they were not
recompiled or falsely labeled as freshly built from the publication commit.

`tools/release/promote_alpha.py` checks these boundaries, fixes private/pending
manifest metadata, attaches the actual source reference and public README,
and verifies that **no runtime bytes changed**. This is a promotion of tested
bits, not a rebuilt renderer. Only README and package metadata differ.

Public ZIP:
`artifacts/alpha/public/v0.1.0-alpha.1/SFCRemix-v0.1.0-alpha.1.zip`.

- Size: **510,884,422 bytes**.
- SHA-256: `e93e7d55e75e174cfa75f6ba648c32b7495d36fe4b39e519af4e4d3a38009d52`.
- Payload layout: only `SFCRemix-Launch.cmd` and `SFCRemix/`.
- Included: application/native components, pinned vendor runtime/dependencies,
  versioned defaults, notices and instructions.
- Excluded: the game, game assets, captured models/textures, saves, private
  settings, development captures, UE proof binaries and proprietary research.

## Qualification

Before the UE checkpoint, 12 focused Python checks passed and the changed
native retained-frame fixture passed 117 checks on each of x86/x64 without
the optional captured companion. These checks are not alpha gameplay evidence.

For publication, five promotion, six ZIP and seven release-manifest tests
passed. The exact promoted ZIP passed its actual native launcher
`--preflight` after extraction with only the seven protected game/profile
files supplied. All seven hashes remained unchanged. The temporary extraction
was removed. No full game copy was created and no additional gameplay was run.
This remains **successful gameplay testing on the author's machine only**.

The README and release notes specify supported client SHA-256, Windows x64,
NVIDIA RTX compatibility, driver **616.92+** from NVIDIA's pinned-runtime notes,
tested driver **621.01**, native dimensions and graphics setup requirements.
The tested machine is Windows 11, i7-13700KF, 32 GB RAM and RTX 4070 Ti 12 GB.
The exact CPU/GPU/RAM configuration is not presented as a universal minimum.
Other-machine success and full model/effect coverage are not claimed.

## Publication

Published GitHub prerelease ID `450652595` on November 18 at 17:58
America/New_York (22:58 UTC). All three assets reported uploaded, their sizes
and server-reported SHA-256 digests matched local files, and the tag resolved
to `e747bd34e5d69c2434edd099232a5b59df784d50` before publication. GitHub then
confirmed `draft=false` and `prerelease=true`. Requirements and the explicit
single-machine notice were verified in the actual release body.

Public release:
https://github.com/tuhs1985/sfc-rendering-modernization/releases/tag/v0.1.0-alpha.1

The release contains the ZIP, its checksum and a small public promotion receipt.
No game files or development captures were uploaded. The large upload took
several minutes; it remained a draft until complete. Local API/preflight and
promotion evidence is beside the public ZIP under `artifacts/alpha/public`.

The release tag remains on the exact package-source commit. Publication
evidence may be recorded by a later documentation-only commit without moving
that tag. Return to the UE branch after release work, preserving unrelated
attachments and `windows-memory-audit.md`.

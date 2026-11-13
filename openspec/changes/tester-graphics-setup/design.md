# Design

The launcher already exposes `--preflight` without elevation. Keep that entry
point and its success receipt. Use the same graphics checks for normal play and
the report. Normal play rejects the first mismatch. Preflight collects the
missing and mismatched files, protected setting differences, resolution
problems and conflicting proxies before returning failure. Do not start native
preflight on an unqualified graphics stack.

For preparation, qualify a portable profile with local vendor inputs verified
by hash. Test the necessary D3D11 target, 8× MSAA, D32 depth and paired
resolutions. The existing baseline embeds a machine-specific ReShade cache
path and adapter choice. The portable profile needs its own qualification.
Account for the preset and shaders that contributed to the accepted appearance.

Change the ReShade cache path first. The shipped runtime already directs
cache, screenshots and add-ons into session data, and the accepted preset and
shader inputs resolve relative to the game copy. Carry those appearance inputs
forward for comparison. Qualify adapter selection separately. The output
receiver opens the renderer's GPU by adapter LUID, so test the native
compositor on the same GPU. Ask the pinned Remix runtime for its actual device,
then try the existing dgVoodoo setting before probing alternatives. Stage
only a setting observed to open the same LUID. Preserve the existing
game-side LUID check and native fallback. Hybrid-GPU gameplay is a separate
compatibility check.

The preparation step should act on a separate game copy with SFC closed, show
which files it will change, preserve allowed player settings, keep verified
backups and record enough state to roll back interruptions. Reuse verified
atomic file replacement. Keep preparation recovery distinct from the per-run
ReShade swap journal. Test both separately and together before enabling the
prepared profile for normal play. Review vendor terms before bundling any
additional binaries.

Distribute one ZIP for extraction into a separate OP game copy. Use the supplied
`SFCRemix-Launch.cmd` entry point for first-run preparation and launch. Show
the proposed changes and require confirmation before replacing existing files.
Hash the local graphics inputs automatically. Keep qualified files and preserve
the existing preset and shaders. The provided project OP copy matches the
standard ReShade and dgVoodoo DLL pins.

Include the verified standard x86 ReShade baseline and the verified full-add-on
x86 runtime as separate ZIP inputs under `SFCRemix`, with the versioned license
notice. Use the standard payload when the game copy is missing that baseline or
has a different version. Keep the full-add-on payload for the existing session
swap. Package other qualified vendor dependencies with their own notices.
Extraction, hashing and provenance checks belong in the release workflow.

# Release and build tools

Everything in this directory is a development/build input. None is imported
from this directory by the shipped launcher. Application entry-point sources
live in [src/launcher](../../src/launcher/README.md).

| Area | Files |
| --- | --- |
| Native builds and probes | `build_launcher.py`, `privilege_probe.cpp`, `run_extent_probe.py`, `run_shared_layout_probe.py`, `shared_layout_probe.cpp` |
| Dependency preparation and review | `inventory_dependencies.py`, `prepare_python.py`, `python-dependencies.json`, `prepare_notices.py`, `package_layout.py` |
| Package assembly and qualification | `runtime_modules.json`, `build_zip.py`, `stage_preflight_fixture.py`, `qualify_production_prewarm.py` |
| User-document build input | `ALPHA-README.md` |

`runtime_modules.json` is the reviewed source allowlist, not an installed
dependency. Legacy session forwarding tools are excluded.
The private staging fixture exercises the installed entry point without starting
SFC; it is not a public distributable or permission to redistribute vendor files.

Use the Windows Python environment in the project README to run
`tools/release/build_launcher.py` and `tools/release/stage_preflight_fixture.py`.
The build writes ignored `artifacts/alpha/launcher-bin`; staging creates a fresh
ignored fixture. It does not update the existing private alpha game copy.

The default reduced fixture also runs the packaged launcher with five deliberate
graphics mismatches. It checks the failure report, verifies file hashes before
and after, restores the fixture and checks it passes again. The result is in the
fixture's `result.json`. Run this check after changing launch admission or how
the graphics profile is reported.

The stager's `--functional` option makes a private full game copy, includes the
root double-click CMD and runs preflight only. It is not a public ZIP or gameplay
acceptance. Before offering it for play, qualify the matching renderer and actual
installed startup; a default reduced preflight fixture cannot launch a game.

Use `stage_preflight_fixture.py --functional --portable-cache` to qualify the
cache-only ReShade profile. It makes a new private copy, changes only the cache
path, and compares the installed helper's generated settings against the
accepted profile. The test hashes the existing preset, shader and texture files.

For a separate GPU selection check, pass the staged `SFCRemix` folder to
`qualify_graphics_adapter.py`. The x86 DirectDraw fixture tests the two dgVoodoo
adapter settings and records the D3D11 adapter identifiers in `result.json`.
Add `--match` to run the pinned Remix adapter probe automatically, try the
current setting first, and stage `matched-dgVoodoo.conf` only on an exact
device match. The game copy stays read-only. A hybrid-GPU checkout remains
a compatibility test for the resulting setup.

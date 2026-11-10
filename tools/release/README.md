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
dependency. It selects 59 Python modules, including two under `src/launcher`
and three under `src/session`. Legacy session forwarding tools are excluded.
The private staging fixture exercises the installed entry point without starting
SFC; it is not a public distributable or permission to redistribute vendor files.

Use the Windows Python environment in the project README to run
`tools/release/build_launcher.py` and `tools/release/stage_preflight_fixture.py`.
The build writes ignored `artifacts/alpha/launcher-bin`; staging creates a fresh
ignored fixture. It does not update the existing private alpha game copy.

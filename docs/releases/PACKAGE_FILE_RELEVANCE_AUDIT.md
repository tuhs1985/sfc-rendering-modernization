# Whole-alpha file relevance audit — November 9, 2026

Read-only extension of [the packaged tools audit](PACKAGED_TOOLS_AUDIT.md).
Sponsor direction: every distributed file must serve the current alpha, not a
possible future feature or a developer workflow. Runtime execution, user settings,
safe recovery, optional bounded troubleshooting, integrity checks, instructions
and required vendor notices count as legitimate product requirements.

**No files removed, no product/runtime code changed, no game or renderer started.**
The runtime/development refactor remains parked. This is a removal/review list,
not authorization to implement it or a proven minimal dependency closure.

## Scope and complete inventory

Inventoried all **3,901 current files**, including **3,895 immutable package
inputs**, the manifest, two editable settings and three operational data files.
Each file has a category and reason in:

- `artifacts/alpha/package-file-relevance-audit.csv` — complete per-file list.
- `artifacts/alpha/package-file-relevance-audit.json` — counts/sizes/roles.
- `artifacts/alpha/package-native-import-audit.json` — selected real PE imports.

This inventory is local development evidence, not another file to ship. The
mutable filenames/operational data are not public ZIP payloads. No settings or
game image contents were read for this inventory.

## Additions to the removal-candidate list

**2,555 additional files / 29.02 MiB** outside the previous 34 code-module candidates. Counts below do not overlap.

| Group | Files | MiB | Why it can leave the current alpha / prerequisite |
| --- | ---: | ---: | --- |
| Package/environment/installer builders | 498 | 7.86 | `pip`, its dist-info, `Lib/ensurepip`, `Lib/venv`, `Lib/msilib`, `_msi.pyd`. Packages are installed at build time; alpha never installs packages or makes environments/MSIs. Keep separately required licenses for retained components. |
| Python GUI/editor stack | 1,399 | 11.79 | `python/tcl`, `Lib/tkinter`, `Lib/idlelib`, `Lib/turtledemo`, `turtle.py`, `pythonw.exe`, Tcl/Tk DLLs, `_tkinter.pyd`, Pillow Tk adapters. Current UI/launcher is native, not Tk. Must exclude the associated wrappers and native pieces consistently. |
| Library self-tests/benchmarks | 521 | 7.11 | CPython `_test*.pyd` and `_ctypes_test.pyd`; NumPy test directories, testing API/conftest and five named native test extensions. Keep `numpy/_pytesttester.py`: normal NumPy and `_core` imports reference that module even if nobody runs a test. |
| Python test/debug/profiler tools | 20 | 0.52 | `Lib/unittest`, `doctest.py`, `pdb.py`, `bdb.py`, `profile.py`, `cProfile.py`, `pstats.py`, `trace.py`. Validate no retained module imports them. Developer smoke scripts using unittest.mock should use a separate harness, not make unittest a production requirement. |
| NumPy extension/build interfaces | 108 | 1.42 | f2py/Fortran tooling, C/Cython headers/interfaces/import libraries and PyInstaller hooks. Keep compiled numerical extensions, their data and OpenBLAS dependencies. Exclude only build interfaces, not whole NumPy subpackages by guess. |
| Demos/reference extras | 7 | 0.01 | `Lib/__phello__`, `antigravity.py`, `this.py`, NumPy interactive `doc` material. No alpha operation invokes these. |
| Old texture-hash subprocess | 1 | 0.31 | `runtime/d3d9-proof/material-bin/texture_hash.exe`. Progressive material production uses `mesh_checksum.dll.sfc_texture_identity`; old `material_binding.prepare` still references the EXE and the manifest requires its role. Remove those legacy dependencies/role before excluding it; do not delete first. |
| Notice build receipt | 1 | 0.00 | `notices/inventory.json` is an internal build review receipt with `ready_for_distribution=false`, not a license. Keep it in build evidence; preserve all full license/third-party notices in the product. |

The candidate designation means functionality outside the fixed alpha contract.
Actual exclusion still needs the retained import/load graph and a fresh installed
checkout to pass. Some tests/build helpers reference each other; only remove them
as a reviewed group. Do not implement this as blanket `*test*`, `*.json`, `*.h`
or `*.txt` deletion.

## Large vendor files: review, not approved excess

- `runtime/remix-runtime/deps/candidate-1.6.1/runtime/crashpad_handler.exe` — 1.04 MiB.
- `runtime/remix-runtime/deps/candidate-1.6.1/runtime/crashpad_wer.dll` — 0.04 MiB.
- `runtime/remix-runtime/deps/candidate-1.6.1/runtime/nvngx_dlss.dll` — 56.23 MiB.
- `runtime/remix-runtime/deps/candidate-1.6.1/runtime/nvngx_dlssd.dll` — 46.10 MiB.
- `runtime/remix-runtime/deps/candidate-1.6.1/runtime/nvngx_dlssg.dll` — 7.16 MiB.
- `runtime/remix-runtime/deps/candidate-1.6.1/runtime/nvngx_dlssnr.dll` — 254.08 MiB.

DLSS is not exposed by the current quality parser (AA is off/temporal), but that
alone does not prove these DLLs can be absent during Remix initialization or
fallback. Likewise, crash reporting may be called by vendor runtime internals.
Require pinned-runtime loading evidence and supported configuration before
excluding these. Do not claim their combined size as reclaimable space yet.
The same caution applies to NVRTC/CUDA, denoisers and USD plugin/schema resources.

## Concrete keep findings

The actual normal import table of the pinned `d3d9_x64.dll` lists:

- `GFSDK_Aftermath_Lib.x64.dll`
- `NRC_Vulkan.dll`
- `libxess.dll`
- `rtxio.dll`, `NvLowLatencyVk.dll` and numerous OpenUSD libraries.

Therefore the current selected binary requires those load dependencies even if
we do not expose the associated feature. Removing them because NRC/XeSS is off
would break loading. This is stronger evidence than judging filenames.

`_hashlib.pyd` imports `libcrypto-3-x64.dll`: it is not merely unused networking
baggage. `_ctypes.pyd` imports `libffi-8.dll`; ctypes drives the live bridge.
NumPy core/linalg extensions import the shipped OpenBLAS and hashed MSVC runtime
DLL. Those dependencies stay. Interpreter DLLs, image codecs, exception/logging
support and the retained standard library must not be cut simply because no
single sample observed them.

Pillow auto-registers image plugins and alpha must load tester-owned assets.
Keep its non-Tk codecs until the supported image-format closure is explicitly
qualified; PNG/DDS conversion and original image decoding are real runtime work.

## Private-only material and legal/operational files

`FIXTURE-NOT-FOR-DISTRIBUTION.txt` is not a final product feature, but currently
serves the private manifest notice role and correctly warns about an unapproved
checkout. Keep it here; replace the role with proper public release documentation
when the actual candidate is approved. Do not ship the private marker as final
user documentation or delete its role early.

Keep the immutable manifest, launcher, optional troubleshooting launcher,
required profiles/defaults, full license/third-party texts and retained package
metadata. Do not remove notices merely because runtime code does not open them.
Settings and recovery/cache files are user-owned operational state, not ZIP
inputs. No additional screenshots, captures or proprietary model data was found
in the current alpha payload.

## Dependency gap exposed by the same audit

The pinned Remix import table also lists standard-name `MSVCP140.dll`,
`VCRUNTIME140.dll` and `VCRUNTIME140_1.dll`. The package has **no standard-name
MSVCP140.dll**. The Python root contains the two VCRUNTIME DLLs, but the host's
explicit `LoadLibraryExW` search uses the Remix DLL directory and System32, not
that Python directory. NumPy's privately hashed MSVCP library does not satisfy a
standard-name loader import.

This is a **clean-machine dependency-closure gap to resolve before release**, not
a new proven cause of a gameplay failure. Current-machine success may rely on
system-installed Visual C++ libraries. Identify a qualified application-local
bundle/search location and redistribution terms, then verify on the promised
clean/second-machine checkout. No installation, download or protection change
was made during this audit.

## Boundary of this audit

Static file inventory, source references, current bootstrap/quality contracts and
selected real PE normal-import tables only. Delay imports, runtime LoadLibrary
calls and plugin discovery prevent using an absent static edge as removal proof.
No new live capture or executable-under-test was launched. Refactor and candidate
exclusion remain parked/not implemented until separately authorized.

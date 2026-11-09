# Alpha dependency and redistribution review

November8,2026. This records implementation evidence and remaining release
review. **No public ZIP is approved or published.**

## Functional closure

The private checkout at `C:\Project\SFC-Alpha-Checkout` contains application-local
CPython3.12.14, NumPy2.3.5, Pillow12.3.0, the compiled x86/x64 project components,
the selected pinned Remix1.6.1 x64 runtime, the qualified ReShade proxy,
settings defaults and a generated integrity manifest. Its independent game copy
is outside `SFCRemix`, never a ZIP input. No Toolkit or Codex runtime is copied.

November9 cleanup removes Python root headers/link libraries/build tools and the
unselected `d3d9_a64ec.dll` alternative from installed payloads. Staging/ZIP rules
exclude these exact paths. Standard-library/image/runtime DLLs and notices are
preserved; upstream source distributions remain intact. See the
[cleanup and comparative validation](../runs/2026-11-09-codex-alpha-layout-cleanup.md).

The actual installed normal coordinator passes read-only preflight from this
package, including after moving it. The legacy1.5.2 runtime and development
qualification receipts are absent. The retained `return_host --observe-only`
creates control/session state without loading that legacy runtime; release
metadata no longer hashes the unused DLL. Preserve the small legacy control
host and startup-gate binary until functional checkout establishes their removal
is safe. No startup architecture was redesigned to save package files.

The Python import inventory is a static superset, including inactive diagnostic
and Toolkit-preview branches. `pxr` is not bundled or required by normal play.
The entry point is now `SFCRemix-Launch.cmd`→native `SFCRemix/launcher.exe`→bundled
Python. PowerShell is not used; the old package `launch.ps1` is removed. The
native launcher imports only Windows Shell32/Kernel32 and uses a static C runtime.
Private preflight and moved Unicode/spaced fixture preflight pass.

Installed gameplay, all subprocess/module loads, clean-machine operation and
second-machine acceptance are still pending. Preflight is not proof of closure
through gameplay. The initial profile validator still requires the recognized
game-copy graphics configuration; general installation-profile coverage is open.

## Identified vendor sources

| Component | Distribution and terms | Packaging obligation/status |
| --- | --- | --- |
| Remix1.6.1 | Official NVIDIA x64 release, SHA256 `7dd1d44492a609050e44b0e3581cec31135d1ed88b4a91123b4faae91955716a`; API0.6.5 header/source pin in `runtime_candidate.py` | Preserve original `LICENSE.txt` and complete `ThirdPartyLicenses-dxvk.txt`; bundled RTX SDK/Aftermath terms are separate from project MIT. Review exact final allowlist and end-user terms before approval. |
| CPython3.12.14 | Official Astral python-build-standalone20260901; exact URL/hash in `python-dependencies.json` | Preserve CPython's complete license, including its Microsoft distributable-code notice, and required application-local VC DLLs. Do not source from Codex. |
| NumPy2.3.5 / Pillow12.3.0 | Exact Windows wheels from official PyPI, locked hashes | Preserve original distribution metadata/licenses, including bundled-library notices; no user-side package installation. |
| ReShade6.7.1 full support | Official Addon installer, SHA256 `FC55C5C62D0BC43BF02C40EC9AEF69E0B74F22A6017403AF1897EC32E5CD0E8F`; extracted x86 proxy hash pinned | BSD-style upstream license at source commit `8cf85bd12d56697d756d4fcb45e501f5d1b540fa`; preserve notice. Game-copy presets/shaders remain game inputs and are not copied into the ZIP without separate review. |
| dgVoodoo2.86.5 | Preserved original archive obtained from masterotaku mirror; qualified DDraw/D3DImm exactly match its x86 entries | Record mirror/archive provenance, retain components unmodified and reference author's redistribution terms. Optional x86 D3D8 hash `72bd6b84face40b928dfd5d1ee6d30f2ce8671919d0264b24513e25a2c647fd3` independently matches that archive and is recognized without accepting arbitrary proxies. |
| Detours | Pinned upstream source already used by project | Preserve original MIT notice in compiled distribution. |
| xxHash0.8.0 | Pinned incorporated header | Preserve original BSD2-clause notice; not project MIT. |
| Windows/driver libraries | System D3D/DXGI/compiler and installed GPU driver | Do not copy system/driver files from this workstation. Validate prerequisites; retain app-local redistributables from identified upstream distributions. |

`tools/release/prepare_notices.py` collects eight full applicable upstream notices
into ignored `artifacts/alpha/notices`, recording hashes/origins. This inventory
is deliberately marked not distribution-ready until the exact bundle and terms
are reviewed. Vendor components cannot be relicensed under project MIT.
Contributed research is not a runtime dependency and is excluded from the ZIP.

Official references: [Remix release](https://github.com/NVIDIAGameWorks/rtx-remix/releases/tag/remix-1.6.1),
[pinned ReShade license](https://github.com/crosire/reshade/blob/8cf85bd12d56697d756d4fcb45e501f5d1b540fa/LICENSE.md),
[dgVoodoo redistribution](https://dege.freeweb.hu/dgVoodoo2/ReadmeGeneral/),
[Microsoft redistribution guidance](https://learn.microsoft.com/en-us/cpp/windows/redistributing-visual-cpp-files).

## Exit gate

Complete private gameplay and interrupted-restoration checks, resolve any missing
runtime inputs, finish vendor/profile closure, then build the exact allowlisted
ZIP from a reviewed commit. Record size/checksums and clean-directory/second-machine
results. Sponsor approval is required before tagging or publishing the prerelease.
The private checkout contains proprietary game files outside the package and must
never be distributed as a whole directory or used as the public ZIP input root.

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

## November 11 release input review

The reversible-setup package passed the local private gameplay checkout. A
separate review rehashed its 3,860 immutable files, compared all 191 Remix
files with the official pinned x64 runtime manifest, and inspected the normal
PE import tables of 141 binaries. The review list omits the private fixture
marker and notice inventory from proposed public payloads. It does not include
the enclosing game directory or any mutable package data.

| Input | Verified | Remaining release check |
| --- | --- | --- |
| Visual C++ for Remix | Remix and OpenUSD import `msvcp140.dll`, `vcruntime140.dll`, and `vcruntime140_1.dll`. The private package had these CRT names available through this workstation, with only Python's own copies of the two vcruntime files in the package. VS 2026 x64 REDIST 14.51.36231 files are pinned and staged for placement beside the Remix DLL. The standalone GPU adapter probe passed with the augmented runtime. | Verify application-local loading and gameplay on Windows without a system VC runtime installation. The workstation result confirms compatibility with the staged layout on this PC. [Microsoft 2026 REDIST list](https://learn.microsoft.com/en-us/visualstudio/releases/2026/redistribution). |
| Remix supplemental notices | Verified 24 texts from NVIDIA's Minecraft integration at `befcc00d16a4fc9f284cec0eceed6c639e17fa64`. Its MIT and DXVK third-party aggregate notices match the 1.6.1 archive byte-for-byte. The other 22 are mapped for review and cover OpenUSD, oneTBB, XeSS, Crashpad, NRC dependencies and other components. | Confirm version applicability against the exact pinned x64 file list and finalize separate SDK and CUDA terms in the shipped notices. [NVIDIA notice inventory](https://github.com/NVIDIAGameWorks/rtx-remix-minecraft/blob/befcc00d16a4fc9f284cec0eceed6c639e17fa64/THIRD_PARTY_NOTICES.md) · [CUDA 13.3 terms](https://docs.nvidia.com/cuda/archive/13.3.0/eula/index.html). |
| dgVoodoo | The preserved 2.86.5 archive matches the mirror's Git blob `bfec80629136002ae88496512fad9a3cac6f5ed1`. Its original x86 DLLs match the two setup inputs. The author's current terms allow unmodified components shipped with a specific game mod. | Include attribution, the version-specific preserved archive provenance and the author's terms reference in the exact candidate. [Preserved archive](https://github.com/masterotaku/dgVoodoo-binaries/blob/main/dgVoodoo2_86_5.zip) · [Author's redistribution terms](https://www.dege.freeweb.hu/dgVoodoo2/ReadmeGeneral/#redistribution-rights). |

Local evidence is in `artifacts/alpha/alpha-release-input-review.json`,
`alpha-release-native-imports.json`, `remix-notice-review/review-inputs.json`,
`remix-crt-recipe-inputs.json` and `remix-crt-gpu-probe.txt`. Eleven focused
alpha Python regressions passed. The recipe review has no approved commit yet.
The public builder requires a reviewed commit and matching built binaries.
The reversible setup source is still uncommitted. No release ZIP, extraction
checkout or tag was produced during this review.

The supplemental notice source pins `minecraft-rtx2-a00da12a-win64-release`.
The two byte-identical notices establish overlap with the public Remix archive.
Check the remaining supplemental notices against the shipped 1.6.1 components
before marking the full recipe reviewed.

## Exact ZIP extraction checkout

The allowlist builder produced a local `SFCRemix-v0.1.0-alpha.1-private-checkout.zip`
under `artifacts/alpha/candidate`. It contains 3,886 manifest inputs and
only adds the CMD launcher and the SFCRemix directory on extraction.
The ZIP is 510,845,229 bytes. SHA-256 is
`daf688b30f809e3721663540ad61a905dd95447699bbc8b518ec6cac3fb7a360`.
The manifest records pending vendor review and no release commit. The
archive is for local verification. No tag or publication was made.

The candidate includes the three application-local Remix CRT DLLs, the
two ReShade variants, reversible graphics setup, default profiles and
vendor notices. It excludes the surrounding game, local settings, saves,
and development captures. The local recipe and exact archive receipts
are in `artifacts/alpha/candidate`.

Extracted the exact archive into `artifacts/alpha/candidate/game`, a fresh
copy of the validated SFC test source. Native preflight identified the
original ReShade configuration. Installed setup used the staged probes to
qualify the GPU and apply the profile. Native preflight passed with the
applied profile. Restore returned the protected files byte-for-byte, and
the last preflight again identified the original ReShade configuration.
The source files matched their original hashes. The receipt is
`extraction-qualification.json`.

These checks used the packaged bootstrap for the setup and restore actions.
The next check is the normal CMD launcher with its elevation path and
enhanced gameplay in that extracted copy. Twelve focused alpha tests passed.
Clean-machine and hybrid-GPU coverage remain open.

### Extracted game asset repair

The sponsor reported a launch failure, then a white/black tactical background
and an early console exit. The retained run `20261112-042551-898187-in-game`
stopped on `Original image missing/bound` after 30.719 seconds. The game was
still running, so the graphics swap was deferred for recovery. No separate
failure receipt is available for the first attempt.

The local extraction checkout script treated every BMP as a screenshot.
It omitted 4,379 original bitmaps from the copied Assets tree, including
ship images and background resources. This happened when copying the
tester-owned game, before extraction of the ZIP. Restored all 4,379
files in place from the validated source and compared each SHA-256.
Compared file presence and size across Assets, MetaAssets, and the ReShade
shader tree. The script now filters screenshot filenames only in the root
and checks the asset trees before exercising the launcher.

Local evidence remains under `artifacts/alpha/candidate`, including
`failed-checkout-evidence` and `asset-repair-receipt.json`.
The archive checksum and game checkout command are unchanged.
The next gameplay run qualifies the repaired copy.

### Tester ReShade configuration

The sponsor confirmed that the original private ZIP ran in another SFC
folder and requested that their `ReShade.ini` remain theirs. New packages
omit the setup INI template and its expected hash. Installed preflight
accepts existing settings or a missing INI. The running session derives a
ReShade configuration under its own data directory and redirects the
cache, screenshot and add-on paths there. With no INI it uses ReShade
defaults in that directory. Existing rules keep shader, texture and preset
paths inside the game copy.

New release sessions restore only the swapped DLL. Legacy setup and session
journals retain their original restore behavior. Test coverage verifies
customized and missing INI admission, session-only defaults, and both
legacy and isolated interrupted recovery. All 777 Windows regressions passed.

The updated private ZIP is
`artifacts/alpha/candidate/SFCRemix-v0.1.0-alpha.1-preserve-reshade-private-checkout.zip`.
SHA-256 is `99d89755467a968a32ae2eafd089e257e0a630299e200a10572e0f641361fdaf`.
Applied its exact changed package files to the existing disposable checkout.
Native preflight, GPU preparation with closed stdin, restore, and generation
of the private session config passed. The tester INI's bytes and modification
time matched before and after each check. Gameplay of the revised ZIP is open.

### Tester-owned game and wrapper settings

The launcher admits the tester's `sfc.ini` and `dgVoodoo.conf` by checking
the graphics settings relevant to the alpha. It checks supported SFC
dimensions and the paired wrapper dimensions. The wrapper must use hardware
Direct3D 11 with the 8x multisample layout used by native insertion. Runtime
still checks the actual target and matching GPU. Preference values and
comments outside those graphics checks do not have to match the development
profile.

Setup installs only the qualified DLLs after confirmation. It runs the
adapter probe on the tester's wrapper settings in scratch storage and
reports a verified alternative adapter setting when the existing one
selects a different GPU. It does not install a wrapper settings template.
New interrupted sessions can restore the DLL even if the tester changes
their settings after exit. Explicit recovery of old journals still follows
the original verified backups.

The revised private ZIP is
`artifacts/alpha/candidate/SFCRemix-v0.1.0-alpha.1-preserve-settings-private-checkout.zip`.
Its SHA-256 is `11caa47ebe82788f1ce21689649a21e295da2e52646e5ba40e0d395baf1d238a`.
The existing checkout was updated in place. Native preflight, real GPU
preparation, restore and temporary ReShade configuration generation passed.
The bytes and modification timestamps of all three tester configuration
files matched before and after. All 778 Windows regressions passed on retry
after a transient Windows file-replacement error in the material test.
The sponsor confirmed revised-package gameplay. Clean-machine and
hybrid-GPU qualification remain open.

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

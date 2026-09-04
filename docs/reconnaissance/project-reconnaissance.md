# Project Reconnaissance Report

Date: 2026-09-03  
Scope: read-only inspection and repository preparation; no game/tool execution,
patching, broad decompilation, renderer implementation, staging, or commit.

Labels used below:

- **Observed** — directly supported by files, metadata, hashes, imports, or strings.
- **Inference** — a bounded interpretation of observed evidence.
- **Unknown** — not established in this pass.

## Executive summary

- **Observed:** The workspace contained 3,043 files in 230 directories before
  repository preparation. `Game Assets/` contains 3,008 files (~2.71 GiB) and
  `References/` contains 35 files (~581 MiB).
- **Observed:** `StarFleetOP.exe` is an unsigned 32-bit Windows GUI PE with file
  version **2.5.6.4**, MD5
  `2BE8F713F81B1C68D50EAD6088C32886`, and SHA-256
  `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
  Its MD5 exactly matches the d4v1ks editor definition labelled “Orion Pirates
  2.564 with the July 2019 update.” The embedded PE timestamp is
  2019-06-29 21:08:35 UTC; the community label is the more specific build
  identification because it is hash-bound.
- **Observed:** The client imports `DDRAW.dll`, `DSOUND.dll`, and `DINPUT.dll`.
  It imports `DirectDrawCreate`, `DirectDrawCreateClipper`, and
  `DirectDrawEnumerateA`; embedded diagnostics identify `IDirectDraw2`,
  `tDDSurfMgr`, `tD3DMgr`, front/back surfaces, flipping/blitting, palettes,
  display-mode changes, and Direct3D device initialization.
- **Observed:** The installed game directory contains only three DLLs:
  `Mss32.dll`, `OSSpecific95.dll`, and `OSSpecific98.dll`. It contains no local
  `ddraw.dll`, `d3d*.dll`, `dxgi.dll`, dgVoodoo runtime DLL, `dgVoodoo.conf`,
  ReShade DLL, or ReShade configuration.
- **Inference:** The presently installed rendering chain is the game’s legacy
  DirectDraw/Direct3D path resolved through Windows system components. An
  optional dgVoodoo path exposed by the launcher could provide a modern API
  boundary compatible with ReShade, but it is not installed or active in this
  snapshot.
- **Observed:** Git was initialized and a conservative controlled workspace was
  added. Nothing was staged or committed.

## Directory and component inventory

| Location | Classification | Observed contents |
|---|---|---|
| `Game Assets/` | Working installation; excluded from Git | Client, dedicated server, intro player, launcher, runtime DLLs, editable configuration, game data, saves, and community tools |
| `Game Assets/Assets/Models/` | Proprietary/community game assets | 2,537 files (~2.16 GiB): 366 `.mod` models and 2,156 bitmap files, including model-specific readmes |
| `Game Assets/Assets/Textures/` | Game assets | 102 bitmap textures (~9 MiB) |
| `Game Assets/Assets/Sprites/` | Packed game data | One `sprites.q3` archive (~83 MiB) |
| `Game Assets/Assets/Scripts/` | Compiled mission content/configuration | 88 `.scr` files (~32 MiB) and `scripts.ini` |
| `Game Assets/Assets/Maps/`, `Campaigns/` | Game data | `.mvm` strategic maps and `.mct` campaign templates |
| `Game Assets/Assets/Specs/`, `Strings/`, `Settings/` | Human-readable game data/configuration | Ship/fighter lists, bindings, BPV data, localized/UI strings, and `.gf` settings profiles |
| `Game Assets/Assets/Sound/` | Large packaged media | Three large sound/music ZIPs and two index files (~404 MiB) |
| `Game Assets/D4v1ks/` | Redistributable third-party compiled tools/evidence | Campaign map, mission, model/material, Q3 sprite, binary editor, and launcher tools plus documentation/palettes |
| `Game Assets/Savegames/` | Generated/user state | SQL database creation script and placeholder save directories |
| `References/Tools (2021-09-05)/` | Reference/original tool set | 33 files; byte-for-byte identical to their working-tree counterparts where corresponding files exist |
| `References/*.zip`, `References/*.7z` | Archival originals; large binaries | SFC Launcher ZIP and August 2019 game archive; excluded from Git and preserved unchanged |

The August 2019 7z contains 3,179 entries and the expected game-root layout. Its
SHA-256 is
`D693D23707DB29B2AE057E9138090A453B770B823844CC1DCD7921E3C530C218`.
The installed launcher is byte-identical to the executable inside the preserved
2.1.0.22 launcher ZIP.

No source-code project was present. The `.bat` files are launch glue for the
d4v1ks SFC binary editor and Q3 editor; the supplied editor applications are
compiled .NET executables. The original game/client/server components are native
x86 PE files.

## Game build and runtime dependencies

### Client

**Observed:** `StarFleetOP.exe` metadata:

| Property | Value |
|---|---|
| File version | 2.5.6.4 |
| Product version | 1.0z |
| Description | Star Trek: StarFleet Command - Orion Pirates (Client) |
| Architecture/subsystem | x86 / Windows GUI |
| Image base | `0x00400000` |
| Entry RVA | `0x0033A2A0` |
| Signature | Not signed |
| Hash identity | Matches the d4v1ks `2564` editor map and its local backup exactly |

Its direct import set is `KERNEL32`, `USER32`, `GDI32`, `COMDLG32`, `ADVAPI32`,
`OLE32`, `WINMM`, `WSOCK32`, `DDRAW`, `DSOUND`, `DINPUT`, `MSS32`, and
`DBGHELP`. Embedded source/assertion strings retain numerous original Taldren and
QuikSilver build paths, including `SFC2_5` game sources and a common
`dmp3d/glsurface` rendering layer. This is useful symbol-free structural evidence.

### Other native components

- **Observed:** `ServerPlatform.exe` is unsigned x86 console code, imports legacy
  Winsock plus `DBGHELP`, embeds version `2.5.6.4`, and contains GameSpy server
  metadata/endpoints. Its MD5 is `61B1AD3AE69AC4EA8F9B5C5C3F4E23CE`.
  That does not match the pre-edit MD5 declared in `ServerPlatform.txt`;
  localhost/GameSpy-patch strings are present, so it appears to be a modified
  community server build. The exact edit history is **unknown**.
- **Observed:** `Mss32.dll` is Miles Sound System 6.1a and exports 343 symbols.
- **Observed:** `OSSpecific95.dll` and `OSSpecific98.dll` are small unsigned x86
  compatibility modules with one export each.
- **Observed:** `sfc2intro.exe` identifies as RAD Video Tools 1.0v.
- **Observed:** None of the inspected executables or DLLs has an Authenticode
  signature.

## Rendering and compatibility chain

### Active snapshot

1. **Observed:** `StarFleetOP.exe` loads the system-named `DDRAW.dll` and creates
   DirectDraw through its public exports.
2. **Observed:** The internal rendering layer obtains `IDirectDraw2`, enumerates
   display modes, changes/restores display modes, creates front/back surfaces,
   flips or blits them, manages palettes and z-buffers, and initializes a
   Direct3D device.
3. **Observed:** `sfc.ini` selects an 800x600 fullscreen 3D configuration with
   `driver=0`, z-buffering, and luminance textures enabled.
4. **Observed:** No local translation/proxy or post-processing DLL/configuration
   is present; ordinary Windows DLL search therefore reaches system DirectDraw.

### Available but not active

- **Observed:** SFC Launcher 2.1.0.22 presents an “Optional (dgVoodoo)”/
  “dgVoodoo” compatibility choice and contains templates for `dgVoodoo.conf`
  with a `DirectX` section and `DesktopResolution` substitution. It also edits
  `sfc.ini` windowed/resolution settings and contains backup/version handling.
- **Observed:** The launcher package contains only the launcher executable; no
  dgVoodoo runtime DLLs are bundled in its ZIP. No ReShade-named material occurs
  in the launcher or installed game tree.
- **Inference:** dgVoodoo is the evidenced translation route by which the legacy
  DirectDraw/Direct3D output could be exposed to a ReShade-supported modern API.
  The required dgVoodoo build, DLL set, output API, and ReShade version/preset are
  **unknown** and must not yet be treated as architectural commitments.

## Launcher findings

**Observed:** `SFCLauncher 2.1.0.22.exe` is an unsigned x86 .NET Framework 4.8
Windows Forms application. Embedded data supports SFC1, SFC2 EAW, SFC2 OP, and
SFC3 executable/registry layouts. For OP it recognizes `starfleetop.exe`, edits
or creates legacy registry entries, modifies `sfc.ini`, provides windowed and
resolution controls, creates backups, can update configured HTTP/GameSpy values,
and offers optional dgVoodoo configuration. It labels the supported OP patch as
“SFC2OP 2.5.6.4 Patch.” It references the public SfcOpServer project for one
server-specific HTTP feature.

**Inference:** The launcher is primarily a compatibility/configuration and
known-build patching front end, not a resident render hook. No evidence showed it
remaining in-process after launching the game.

**Unknown:** This pass did not execute the launcher, so its exact file-write set,
registry-write set, privilege behavior, and dgVoodoo acquisition/deployment
workflow remain unverified.

## d4v1ks tool findings

| Tool | Observed capability |
|---|---|
| Campaign Map Editor 1.0.0.3 | Loads/saves strategic maps; edits terrain, regions, strength/economy/impedance, planets, bases, and map scale views |
| Mission Editor 1.0.0.2 / 2.3.0.2 | Opens SFC1/SFC2 EAW/SFC2 OP/SFC3 compiled mission `.scr` files and safely edits their encoded mission maps |
| Model Browser 1.0.6.5 | Views `.mod` models; imports/exports triangulated OBJ/MTL; preserves LOD group conventions, damage points, hardpoints (up to 25), break-model parts, and pivots; documented 64K vertex/triangle limits |
| Materials Editor 1.0.0.2 | Edits `.mod` material properties; recursively scans for unused materials, missing textures, and incorrect luminance textures; can remove/fix selected issues and generate scan logs |
| Q3 Editor 1.7.4.0 | Loads and edits the packed `sprites.q3` workspace with palette assets; documentation imposes restrictive private/mod-use terms, so generated Q3 material should not be placed in Git without rights review |
| SFC Editor 1.4.0.2 | Hash-gated typed binary editor driven by declarative text maps; supports numeric/string/opcode types, arrays, restricted values, and named tabs |
| SFC Launcher 2.1.0.20 / 2.1.0.22 | Multi-game compatibility/configuration/known-build patching as described above |

The supplied checksum manifest is stale in two narrow places: it expects Campaign
Map Editor 1.0.0.2 while 1.0.0.3 is present, and its campaign-editor text hash no
longer matches. The other 29 present entries match; one superseded 1.0.0.2 binary
is absent. Working and reference tool copies are otherwise byte-identical.

## Existing reverse-engineering evidence

- **Observed:** `StarFleetOP.txt` is bound to the exact client MD5 and contains
  245 active typed offset rows across 28 functional tabs, plus eight commented
  candidate rows. It maps weapon tables, ranges, speeds, special abilities,
  damage allocation, movement, sensors/scanners, shields, transporters, year
  rules, and a GameSpy field. This is concrete prior executable-layout work.
- **Observed:** `ServerPlatform.txt` maps GameSpy hostname fields and a version
  location for a known server hash.
- **Observed:** `DAC_IDs.txt` maps damage-allocation chart identifiers to game
  systems and documents once-per-volley entries.
- **Observed:** Model Browser documentation captures `.mod` semantic structure:
  LODs, materials, diffuse/emissive textures, damage points, hardpoints, break
  parts, and pivots. Materials Editor adds automated consistency checks.
- **Observed:** Mission and campaign editors demonstrate community knowledge of
  `.scr` mission-map and `.mvm` strategic-map structures. Q3 Editor demonstrates
  knowledge of the packed sprite/palette format.
- **Observed:** The client’s retained class, assertion, error, and source-path
  strings provide anchors for targeted rendering analysis (`tDDSurfMgr`,
  `tD3DMgr`, `tD3DViewMgr`, `tDDSurface`, and related initialization methods).
- **Inference:** The exact hash-bound offset map substantially lowers risk for
  build identification and targeted static investigation, but its mapped fields
  are mostly game mechanics rather than render-call entry points.

## Git repository and classification policy

The repository now has the following controlled structure:

```text
.
|-- .gitignore
|-- README.md
|-- artifacts/                 # local generated evidence; contents ignored
|-- docs/
|   |-- decisions/             # future reviewed decisions
|   `-- reconnaissance/        # evidence-backed reports
|-- src/                       # intentionally empty pending review
|-- tests/                     # future legal/repeatable fixtures
`-- tools/recon/               # read-only PE and string inspection helpers
```

Classification decisions:

- **Project-controlled:** root policy/readme, reconnaissance reports, future
  reviewed decisions, source, tests, and reproducible read-only helper scripts.
- **Documentation/reference suitable for Git:** only newly written project
  documentation or material whose redistribution rights are clear. Existing
  third-party/game readmes remain with their ignored source trees for now.
- **Trackable configuration:** sanitized templates named as examples; never the
  live `sfc.ini`, launcher state, wrapper state, credentials, or machine paths.
- **Generated output:** captures, dumps, logs, screenshots, extracted files,
  disassembler databases, backups, scan reports, and build output are ignored.
- **Large/third-party/proprietary:** all game assets, executables, DLLs, archives,
  and compiled community tools are excluded. Their identity should be recorded
  by hashes rather than duplicated in Git.
- **Secrets:** `.env` variants, credentials, keys, certificates, and live game
  configuration are ignored. The current `sfc.ini` contains legacy account data,
  including a password-like value, and must not be committed.

The `.gitignore` implements this policy globally and explicitly excludes
`Game Assets/` and `References/`. No supplied material was deleted or modified.

## Key technical unknowns

1. Which Direct3D interface/device generation and draw methods the client uses
   after obtaining DirectDraw2, and whether any rendering bypasses that path.
2. The complete render-state, texture-format, palette, z-buffer, lost-surface,
   and fullscreen/windowed behavior exercised in real gameplay.
3. Whether an existing dgVoodoo deployment previously used with this copy exists
   elsewhere, and its exact version/configuration/DLL hashes.
4. Which modern output API the known dgVoodoo path uses and the exact ReShade
   hook point/configuration that has been demonstrated with SFC OP.
5. Whether wrapper translation preserves luminance/damage textures, alpha/color
   key behavior, UI composition, videos, screenshots, and alt-tab/device-reset
   behavior without defects.
6. The launcher’s exact patch table and side effects for this MD5 when exercised
   in a disposable copy.
7. Whether symbols, source fragments, newer d4v1ks tool versions, wrapper configs,
   or community render documentation exist outside this workspace.
8. Licensing/redistribution constraints for every candidate wrapper, generated
   Q3 content, community binary, and any future test fixture.

## CTE-1: legacy render access implications

Assuming CTE-1 concerns obtaining dependable access to the legacy render stream:

- **Observed positive evidence:** The client has a narrow, conventional x86
  DirectDraw entry boundary and recognizable internal render-manager anchors.
  DirectDraw is dynamically resolved by normal DLL loading, and no existing local
  proxy currently occupies that boundary.
- **Inference:** A controlled proxy/translation experiment can likely observe or
  translate rendering without patching `StarFleetOP.exe`. That makes DLL-boundary
  interception the least invasive initial feasibility path.
- **Risk:** DirectDraw creation is only the entry point; actual Direct3D COM calls
  do not appear in the import table. Interface negotiation and runtime traces are
  needed before claiming full frame, depth, motion, texture, or semantic access.
- **Risk:** Palette/surface flipping, legacy display modes, mixed GDI/UI paths,
  and device-loss behavior may constrain capture or modernization quality.
- **Discipline:** These findings lower the uncertainty of finding an access point;
  they do not select dgVoodoo, ReShade, a custom proxy, binary patching, or any
  neural/upscaling technique as a requirement.

## Recommended next technical investigation

Create a disposable copy of the exact hash-identified game build outside the
preserved installation and run a tightly scoped legacy-render access experiment:

1. Establish a repeatable baseline scene and record native behavior, logs,
   screenshots, resolution/window-mode behavior, and loaded modules.
2. Observe DirectDraw/Direct3D interface negotiation and call flow with a
   read-only/debug capture method, using the retained `tDDSurfMgr`/`tD3DMgr`
   strings as targeted anchors rather than broad decompilation.
3. Separately reproduce the launcher’s optional dgVoodoo setup in the disposable
   copy, pinning and hashing every added DLL/configuration file.
4. Verify the resulting modern API and only then test whether ReShade can attach;
   compare UI, 3D scene, texture/luminance effects, depth availability, video,
   screenshots, alt-tab, and performance against baseline.
5. Record outcomes as CTE evidence and architecture options, not requirements.

This sequence directly answers whether legacy render access is stable and useful
while preserving the supplied working installation and avoiding premature
renderer implementation.

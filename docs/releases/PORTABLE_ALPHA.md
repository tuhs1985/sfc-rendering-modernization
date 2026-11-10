# Portable alpha implementation — v0.1.0-alpha.1

Approved November 8, 2026. **Implementation in progress; no releasable ZIP,
tag or GitHub prerelease exists.** The current development baseline is still
1920×1080. Native-size allocation and generation retirement are now connected in
the alpha path; six-size standalone qualification passes. Packaged gameplay has
not been qualified.

## Accepted delivery contract

Testers make their own game copy. Extract exactly `SFCRemix-Launch.cmd` and
`SFCRemix/` beside its supported `StarFleetOP.exe`. Extraction does not overwrite
game files. No installer, runtime download, Toolkit, Codex, Python installation,
PowerShell or build tools are required on the tester's machine.

Use application-local Python and a native Windows launcher behind the
double-clickable `SFCRemix-Launch.cmd`. No PowerShell is invoked by this entry.
Request elevation once when needed. The normal profile is untimed replacement,
ExtraFrame, weapon lights, damage and supported break models. Preserve current
lighting/material/image values. Manual ZIP updates preserve editable settings.

Native game dimensions must reach renderer, colour/depth/owner transfer and
composition. Sponsor correction: alpha qualification covers **1024×768,1280×720,
1366×768,1440×900,1600×900,1920×1080**. Native1440p/4K are deferred. The historical
1280×360 corruption remains a diagnostic negative case, not an alpha blocker.
1366×768 provides the supported odd-width case. Qualify target/device replacement
and lease retirement. Supersampling,
D3D12, new assets and appearance tuning remain outside this increment.

## Implemented so far

- New source packages also install the canonical coordinator, exit monitor and
  report module under `code/src/session`. The bootstrap imports them directly;
  the three compatibility tools retained in the development tree are not shipped.
  Existing alpha checkout remains unchanged. This is a source/package-path
  qualification, not a newly assembled playable package or gameplay acceptance.

- The portable entry point now lives in `src/launcher`; new packages install its
  Python files under `code/src/launcher`. `tools/release` contains only build,
  packaging and qualification inputs. Native launcher and package layout must
  update together. The existing private alpha checkout is unchanged by this
  relocation; see the [boundary qualification](../runs/2026-11-09-codex-release-tooling-separation.md).

- Production code now uses `tools/release/runtime_modules.json`, an explicit
  59-module allowlist. Development tools stay in the source tree but are absent
  from the alpha; the diagnostic placement/model profiles and old texture-hash
  executable are no longer required. See the
  [separation record](../runs/2026-11-09-codex-production-module-separation.md) for
  offline proof, startup correction and sponsor gameplay confirmation.

- `tools/remix_runtime/runtime_context.py` separates development paths from the
  explicit package root. Release game path is the package's parent, never the
  accepted developer installation. Session evidence/cache/baseline paths map to
  `SFCRemix/data`; settings map to `SFCRemix/settings`. Construction is read-only.
- Normal coordinator, mesh/material preparation, runtime selection and recovery
  modules are being migrated to that context. Geometry-reference resolution is
  package-relative. Development qualification checks remain active in development;
  release preflight uses a generated immutable manifest instead of source/test
  receipts. This is not yet a qualified complete packaged launch.
- Manifest checks cover immutable file hashes, missing roles, extra immutable
  files, traversal, case collisions, reparse links and exact executable identity.
  A separately qualified existing graphics profile is required before mutation;
  unknown proxy combinations are refused. PlayerName remains game-owned.
- Explicit first launch seeds settings without overwriting edits. Release wrapper
  and bootstrap select existing normal coordinator flags, including BRK. Recovery
  uses existing verified transaction code and refuses to run while SFC is alive.
- The allowlist ZIP builder hashes inputs and archived output, requires a reviewed
  commit and vendor origin/notices, excludes game/capture/private-setting payloads,
  and never uploads or overwrites a previous candidate. Its test ZIPs contain
  synthetic text only and are not application packages.
- MIT license selected as directed, for project-authored code only. Contributed
  research, proprietary game assets and vendor components are not relicensed.
- Checked output accounting and a versioned 128-byte native target notice are
  implemented/tested in isolation. Notice space is 4352–4479 in the existing
  semantic mapping, after startup-ticket storage and before environment storage.
  It carries session, PID, dimensions, device/target generation and observation
  time, independently of assets. It now drives passive host startup, rendering,
  receiver/pool allocation and native insertion. Output wire2/pool3 preserve
  fixed-capacity layouts and distinguish generations. On resize, old GPU leases
  drain before output recreation; retained geometry/textures remain loaded.

## November8 native-resolution integration update

All six supported sizes have zero pixel mismatches in independent GPU-sharing
and full600-frame multi-ship insertion tests. Resize1920×1080→1024×768 followed by
full game-device recreation passes with correct colour/depth/native text before
and after, three retained owners, no graphics-state errors, normal receiver
retirement and SDK shutdown0. Renderer generations advance1→2→3 while asset loads
remain2 with1shared instance: no geometry reload. The intermittent shared-asset
admission race is fixed and the remaining-size tests pass. These are standalone
results, not sponsor gameplay acceptance. [Exact run receipts](../reconnaissance/evidence/20261108-alpha-native-resolution-qualification.json).

Resize qualification caught two integration defects, now fixed: source-stop
checks must run even while a target notice is invalid; the passive ledger must
retain nonzero receipt counters when a fully drained target is recreated.
Shared-asset aliases now publish only after canonical renderer admission; CPU
alias storage is intentionally absent, so early alias publication was invalid.

729Python regressions pass, including alias-order and actual Windows Unicode-INI
boundary checks. Existing Strict/ExtraFrame600-frame development tests pass and
the normal untimed BRK launcher preflight is refreshed/passes. The
package profile recognizes the six dimension pairs while hashing every other
graphics-setting byte. The release ReShade base uses its pinned upstream
`RESHADE_BASE_PATH_OVERRIDE` facility to place generated config/cache/log output
under package data and keep existing shader/preset input paths in the game copy.
Its actual GPU-boundary test passes at1366×768 and through resize/device
recreation. No appearance controls were changed.

## Private functional checkout ready for sponsor play

**First checkout correction:** the sponsor's172602run was rejected by the native
launcher's hardcoded development location before any SFC process was created.
The package launcher/manifest are now updated; native package-bound preflight,
Unicode preload/GPU qualification and730Python regressions pass. Retry the same
command below. The earlier preflight success did not prove native launch
readiness. [Failure and correction](../runs/2026-11-08-codex-alpha-launcher-portability-fix.md).

`C:\Project\SFC-Alpha-Checkout` contains an independent game copy and application
package with the complete pinned runtime, app-local Python and current settings.
Installed preflight passes after moving to this short path. The actual normal
coordinator also passes packaged preflight with old1.5.2 runtime/development
receipts absent. All4143 immutable package inputs are checked. This is an
uncommitted, non-distributable functional checkout, not a public alpha ZIP.

Sponsor entry point: double-click `C:\Project\SFC-Alpha-Checkout\SFCRemix-Launch.cmd`.
From Command Prompt:

```cmd
C:\Project\SFC-Alpha-Checkout\SFCRemix-Launch.cmd
```

Play a skirmish/campaign normally, exercise camera changes, weapons, damage and
destruction, then exit normally. Check early exit/immediate relaunch/recovery.
This copy is untimed; original accepted/test installations are unchanged. Do not
distribute this entire directory: proprietary game files are outside `SFCRemix`.
Full gameplay/dependency closure, the recognized installation-profile coverage,
final vendor terms/allowlist, reviewed-commit ZIP and second-machine acceptance
remain open. [Dependency review](DEPENDENCY_CLOSURE.md).

## Application-local Python evidence

`tools/release/python-dependencies.json` pins upstream URLs, lengths and SHA256
for Astral's official python-build-standalone CPython 3.12.14 Windows x64 release
20260901, NumPy 2.3.5 and Pillow 12.3.0 Windows cp312 wheels from PyPI.
`prepare_python.py` retrieves/verifies these, bounds extraction, rejects archive
links/traversal, and installs the verified local wheels without network/package
resolution. No Codex runtime is copied and no machine-wide runtime is installed.

Prepared locally at ignored `artifacts/alpha/python-3.12.14/`. Its isolated
interpreter imports exact versions successfully. First full regression run passed
713 tests; final expanded release/path/ZIP/target suite passed 723. Windows shared-memory and
process tests require the existing desktop-session execution context. Restricted
session failures are not packaged gameplay results. Native C++ extent and notice
tests passed 15 and 12 checks respectively under both x86/x64 `/W4 /WX`; this is not GPU
or target-resize qualification.

## Portable preflight and output-transfer findings

The historical Windows PowerShell5.1 wrapper and bundled independent interpreter
passed a3939-file read-only package preflight twice: a game-copy fixture containing
spaces/é, then the same package moved to another folder. No Toolkit/PowerShell7/system
Python was used; source game-copy critical hashes remained unchanged, and no
settings/data were seeded in preflight mode. This private fixture is incomplete
and **not distributable**. It does not prove normal-play dependency closure,
clean-machine launch, UAC workflow, native insertion or restoration/removal.

Native transfer qualification exposed a release issue at1280×360:

| Extent | D3D9-source mismatches | Native-D3D11 mismatches |
| --- | ---: | ---: |
| 960×540 control | 0 | 0 |
| 1280×360 | 0 | 271360 / 460800 pixels |
| 2560×1440 | 0 | 0 |
| 3840×2160 | 0 | 0 |
| 1031×517 odd width | 0 | 0 |

These are GPU-written quadrant tests with independent readbacks on both sides
of the same shared texture. Source correct/native incorrect isolates the fault
below camera/geometry/material handling. Native row pitches are explicitly used,
including4224bytes at1031pixels. The complete ray-traced synthetic1280×360 output
also reproduces scrambled layout;960×540 returns recognizable geometry coverage.
Cross-process copies are byte-identical to the already-wrong native image, so
matching transfer hashes alone cannot qualify it. First no-bootstrap exploratory
output was zero/uninitialized and is not this correctness evidence.

The simple sharing probe prints SDK Shutdown0 but then needs its bounded process
watchdog to finish, including the passing-size cases; all owned processes end.
Final-source960/1280replays preserve source/binary/runtime hashes and reproduce
the same pixel difference. **No full probe cleanup or higher-resolution live
rendering PASS is claimed.** The actual native host was rebuilt with identical
SHA256, existing successful600-frame Strict/ExtraFrame evidence revalidated, and
normal development BRK/untimed read-only preflight passes. Development appearance
and its1-Present default remain unchanged;24Presents are diagnostic fixture only.

The pinned release's public texture-import source selects opaque Win32 KMT.
The [Vulkan specification](https://docs.vulkan.org/refpages/latest/refpages/source/VkExternalMemoryHandleTypeFlagBits.html)
distinguishes that from the D3D11 texture KMT handle returned by GetSharedHandle.
This is a plausible runtime-import compatibility explanation, **not a verified
causal fix** or instruction-level binary/source attribution. No runtime patch,
translator change, padding/coordinate workaround or CPU transfer was introduced.
See [curated evidence](../reconnaissance/evidence/20261108-alpha-portability-and-output-layout.json).

The1280×360 investigation above is historical negative evidence. It does not
block the corrected six-size alpha scope. Passing quadrants at1440p/4K do not
qualify those dimensions for release.

## Output accounting decision

Keep existing two output-pool slots and conservative sixteen four-byte controlled
output planes. Checked storage is 132,710,400 bytes at1080p,235,929,600 at1440p,
530,841,600 at4K. The old128MiB bound cannot honestly cover4K. The dimension-derived
accounting retains the existing128MiB limit for the six alpha sizes. The larger
numbers document future work only; these exclude native SFC and internal Remix
memory. No queue, asset or image budget increase has been enabled.

## Dependency review still open

The November 9 [external-tester graphics baseline audit](GRAPHICS_BASELINE_AUDIT.md)
confirms that a matching EXE alone is insufficient: pre-existing wrapper DLLs and
broad config signatures are required. The ReShade signature includes developer
cache/UI state, and no portable tester-preparation command is supplied yet.
Resolve this setup gap before treating arbitrary supported-EXE copies as ready.

| Component | Identified source / pin | Remaining closure |
| --- | --- | --- |
| CPython/NumPy/Pillow | Exact upstream distributions in dependency lock; isolated runtime works | Package all required original notices, audit PE imports/application-local VC runtime, test clean environment |
| Remix | Existing pinned1.6.1 runtime, API0.6.5, SDK commit0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0 | Review entire binary bundle, third-party/RTX SDK notices and redistribution conditions; select exact allowlist |
| Legacy control host | Current return_host `--observe-only` still creates control/session state | Retain required bootstrap dependencies until absence is proven; do not redesign startup to remove them |
| ReShade | Qualified x86 full-support6.7.1 proxy plus current recognized game-copy stack | Review upstream binary/source notices and presets; account for log/cache paths and transactional restoration |
| dgVoodoo | ProductVersion2.8.6.5; file version4.7.1.3000 is emulated DirectDraw | Preserved original2.86.5archive from masterotaku matches both qualified x86 DLLs exactly. Its Readme links official online terms. Record mirror provenance and terms; no silent upgrade or unidentified DLL |
| Detours/xxHash/Microsoft runtime | Existing pinned incorporated dependencies | Complete notices and exact redistribution/import inventory |

Official references: [dgVoodoo redistribution rights](https://dege.freeweb.hu/dgVoodoo2/ReadmeGeneral/),
[2.86.5 release](https://github.com/dege-diosg/dgVoodoo2/releases/tag/v2.86.5),
[pinned Remix SDK](https://github.com/NVIDIAGameWorks/dxvk-remix/blob/0a6cd5b1ee814ec390c358e0c9c32ece8895ddc0/public/include/remix/remix_c.h).
Current online dgVoodoo terms are not an archived2.86.5 package receipt.

## Next work and publication gate

1. Finish actual runtime dependency closure, default profiles/notices and portable
   coordinator/recovery tests. Audit subprocesses, native DLL imports, cache/log
   destinations and legacy imports; a static Python import list is not closure.
2. Wire native target notice into early startup without waiting for assets.
   Propagate output extent and generation throughout producer/receiver/game pool
   and compositor. Drain leases on target changes, preserve cached geometry and
   native fallback. Current fixed1080p validators/allocations still need changes.
3. Run actual intact/debris GPU path and dimension/orientation/depth/owner fixtures,
   fault/resize tests, regressions and read-only launcher preflight. Do not claim
   live readiness from isolated contracts.
4. Build the actual allowlisted candidate from a reviewed commit. Clean-directory
   checkout without developer runtimes, then sponsor/second-machine gameplay,
   repair/destruction/campaign/early-exit/recovery/restoration checks.
5. Present exact ZIP, size, checksums, measurements and known limitations for
   sponsor approval. Only then tag and publish the GitHub prerelease.

Preserve cloak/transparency, broader unqualified BRK files and camera-dependent
gray-wing findings. No test has yet established alpha package acceptance.

# Tester graphics-baseline dependency audit

November 9, 2026. Read-only investigation prompted by a tester whose reported
2.5.6.4 executable passed but working graphics files did not. The tester's own
files were not supplied; this audits the local alpha manifest and identical
validator in current source, not the tester's installation directly.

## Confirmed local requirements

Executable version text alone is insufficient. Accepted `StarFleetOP.exe` SHA256:
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
Local file version is 2.5.6.4, product version 1.0z.

The current package requires these existing game-directory DLL bytes before it
will start. These requirements are distinct from the libraries bundled inside
`SFCRemix/runtime`.

| Existing file | Identified tested distribution | SHA256 |
| --- | --- | --- |
| `DDraw.dll` | dgVoodoo 2.86.5, x86; ProductVersion 2.8.6.5, emulated file version 4.7.1.3000 | `62F1E1B2AC5196F4A74B35B898BA8644322F976026324E2F767A4096BFB58748` |
| `D3DImm.dll` | dgVoodoo 2.86.5, x86; ProductVersion 2.8.6.5 | `F51507ACBB1C5510AB72881EEFDE5E4DFE6376667546E86DDCF62E6A9EE4923F` |
| `dxgi.dll` | ReShade32 6.7.1, file version 6.7.1.2133 | `E35E4E2E47F4765F0799CB54C88E5ADE49B50CD7895C137B9D557F263344CAB7` |

### Verified source for the standard ReShade x86 DLL

This extraction and verification procedure is for release maintainers. Tester
preparation should check the shared OP files automatically, reuse an exact
match, and obtain any required replacement from the reviewed package.

The supplied project OP test copy has the exact standard ReShade baseline,
both pinned dgVoodoo x86 DLLs, and the expected ReShade preset and shader folder.
Keep the standard and full-add-on ReShade DLLs as separate verified inputs in
the alpha ZIP. ReShade's [6.7.1 license](https://github.com/crosire/reshade/blob/v6.7.1/LICENSE.md)
permits binary redistribution with its copyright notice, conditions and
disclaimer. The local packaging notice matches the versioned upstream license.
This check covers the ReShade DLLs. Presets, shaders and other vendor components
have their own provenance and notice checks.

Use the [official standard ReShade 6.7.1 installer](https://www.reshade.me/downloads/ReShade_Setup_6.7.1.exe).
Both the `www.reshade.me` and `reshade.me` endpoints returned the same
3,982,560-byte installer on the verification run. Its SHA-256 is
`4D7C19A5C08849E3A83C2824CF93636349A4A605C009812ADB682720D984FA4D`.

Open the EXE as a ZIP archive with 7-Zip and extract just `ReShade32.dll`
into a separate staging folder. The installer does not need to run.

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath .\ReShade_Setup_6.7.1.exe
& 'C:\Program Files\7-Zip\7z.exe' e -tzip .\ReShade_Setup_6.7.1.exe ReShade32.dll '-o.\ReShade-x86' -aos
Get-FileHash -Algorithm SHA256 -LiteralPath .\ReShade-x86\ReShade32.dll
```

Compare the installer hash above and the DLL hash in the table. The extracted
DLL was verified as a 32-bit PE DLL, file version 6.7.1.2133, byte-identical to
the required baseline. Windows reported the ReShade signer and returned
`UnknownError` for Authenticode verification, so the verification here is the
official HTTPS download and matching byte hashes. 7-Zip extracted it successfully despite archive offset
and trailing-data warnings. Windows' built-in .NET ZIP reader failed on the
embedded archive. The developer check also passed using Python's `zipfile`,
which is available in the application-local Python for future preparation.
Setup will stage the verified DLL as `dxgi.dll` for a separate game copy.

The package separately supplies full-add-on ReShade32 6.7.1.2131, SHA256
`A1BA732B5E31E0405CDE322CC5EC62CF972B3FBAEFBB6CBDC8A24DA00D58AE24`,
for the temporary graphics transaction. Supplying that runtime component does
not satisfy the initial baseline `dxgi.dll` check. Do not confuse the two files
because both say ReShade 6.7.1.

`D3D8.dll` is not required, but if present only the recognized dgVoodoo file with
SHA256 `72BD6B84FACE40B928DFD5D1EE6D30F2CE8671919D0264B24513E25A2C647FD3`
is allowed. Other `d3d9.dll`, `winmm.dll`, `version.dll` proxy conflicts are
rejected. A different working wrapper is unqualified, not proven incompatible.

## Settings checks are substantially stricter than documented

| Input | Actual validator behavior |
| --- | --- |
| `ReShade.ini` | Exact whole-file SHA256; no normalization or editable fields |
| `dgVoodoo.conf` | All non-dimension bytes protected; only paired recognized resolution fields normalized |
| `sfc.ini` | All bytes protected except Network/PlayerName and recognized Width/Height fields |

Current raw ReShade baseline SHA256:
`2AF4D74A147EDCF90F0811629DACE3BE3DA6C34E8739FA3E1E573AE93FAE9501`.
It contains a developer-user absolute cache path and saved overlay layout.
Changing only the cache directory or FPS display fails initial preflight, despite
the runtime later generating a portable session-local cache/config override.

The dgVoodoo baseline selects adapter ordinal 1, D3D11 FL10.1 output, 8x MSAA,
forced 32-bit depth, anisotropic filtering 16 and forced 1920x1080 dimensions.
The existing insertion compositor genuinely requires supported D3D11 targets,
8x MSAA and D32 depth. The adapter ordinal and UI/cache details are not thereby
established as universal requirements; they are nevertheless enforced by the
current broad file signatures. Do not distribute the developer profile as a
portable solution without resolving that distinction.

The permitted paired dimensions are 1024x768, 1280x720, 1366x768, 1440x900,
1600x900 and 1920x1080. SFC Width/Height, dgVoodoo GeneralExt/DesktopResolution
and DirectX/Resolution must agree. Other settings, whitespace and comments are
still protected. This can also reject unrelated user preferences in `sfc.ini`.

## Actual boundary checks

Used disposable copies with the real `verify_game_profile`, not mocked hashes:

- Qualified baseline passes.
- Only ReShade cache path changed: rejected.
- Only ReShade FPS display changed: rejected.
- Only game-owned PlayerName changed: accepted.
- Paired output changed to 1280x720: accepted.
- Only a dgVoodoo comment appended: rejected.
- Only an SFC INI comment appended: rejected.
- DDraw bytes changed: rejected.

Original game/configuration files unchanged. No game or renderer started.
Local detailed evidence: `artifacts/alpha/tester-graphics-profile-audit.json`.
The tested old alpha validator, dimension normalizer and preference normalizer
match current source, so this is not a regression introduced by source relocation.

## Additional closure gap

The accepted ReShade configuration references `SFCOP_1_Preset.ini` and
`reshade-shaders/Shaders`/`Textures`. Those inputs are not validated by this
graphics-profile gate: the disposable profile passed without them. They are
appearance dependencies to inventory, not demonstrated prerequisites for Remix
insertion startup. Exact-file profile checks are not complete dependency closure.

The bundled launcher has no tester-facing prepare/adopt-profile command. Its
options are launch, preflight, restore and troubleshooting. The existing
`prepare_test_install.ps1` is a workstation-specific copy of an already prepared
installation, not a supported external setup process.

## Disposition

Sponsor parked implementation on November 9 until repository organization is
finished. Reopen afterward before general external-tester setup. The existing
Obsidian Parking Lot records the reason and first action; the audit stays here
as authoritative evidence. No preparation implementation is currently active.

Tester description is substantially correct, with the PlayerName/dimension
exceptions above. The missing documented/prepared graphics baseline is our
packaging gap. Do not tell testers to disable hashes, edit the manifest, remove
their working files or install arbitrary old DLLs as a workaround.

Next work should provide an explicit reversible game-copy preparation path with
identified vendor files and reviewed redistribution/notices, portable clean
configuration, preserved preferences, and validation of essential supported
graphics state. Any alternate working graphics stack needs its own compatibility
qualification. This audit changes no runtime validation and supplies no new
public bundle or supported alternative profile.

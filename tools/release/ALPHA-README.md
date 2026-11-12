# SFC Rendering Modernization — v0.1.0-alpha.1

Experimental RTX Remix ship replacement for the supported Starfleet Command:
Orion Pirates client. This guide describes the intended release package; a
private checkout is not an approved public release.

## Start

1. Make a separate copy of your supported SFC installation. Keep your usual
   installation and saves as your backup.
2. Extract the complete release ZIP beside `StarFleetOP.exe`. It adds only
   `SFCRemix-Launch.cmd` and the `SFCRemix` folder. Do not copy individual files
   out of that folder into the game directory.
3. Double-click `SFCRemix-Launch.cmd`. It starts the native Windows launcher.
   Accept the single Windows elevation prompt when
   requested. On first launch, the launcher checks that SFC and Remix can use
   the same GPU. If graphics files need changes, it lists them and asks before
   applying them. Select your campaign or skirmish normally.
4. Exit SFC normally when finished and let the launcher finish cleanup.

Replacement, weapon lights, damage and qualified break models are enabled.
ExtraFrame timing is the standard. Normal play has no match or session timer.
Native drawing remains available while a matching replacement is being prepared.
The Toolkit, Python installation, PowerShell and developer tools are not needed.

## Supported setup

The initial alpha supports the pinned Community Edition executable, SHA256
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
Other executable revisions are unsupported. Preflight also checks the recognized
graphics profile and refuses unknown conflicting proxies before changing files.
Profile compatibility must pass; do not work around a rejection by deleting DLLs.

Keep your existing SFC and dgVoodoo settings. First-run preparation may propose
the qualified graphics DLLs. If the game and Remix use different GPUs, the
launcher reports the verified dgVoodoo adapter setting for your game copy.
The current compositor requires hardware Direct3D 11 and 8x multisampling.

The launcher uses your ReShade settings to create a session configuration under
`SFCRemix/data`. Keep your shaders, textures and presets inside the game copy.
ReShade's session cache and screenshot outputs use the package data directory.

Known stable native sizes are1024×768,1280×720,1366×768,1440×900,1600×900 and
1920×1080. The game and its wrapper must use matching supported dimensions.
Native1440p/4K and supersampling are not part of this alpha qualification.
An RTX-capable GPU and a driver supported by the pinned Remix1.6.1 runtime are
required. The package does not install or change your graphics driver.

## Settings and updates

The first launch creates editable `SFCRemix/settings/lights.toml` and
`SFCRemix/settings/rendering.toml` from the versioned defaults. Their comments
describe the controls. Existing settings are preserved on subsequent launches
and manual ZIP updates. Restart the game after changing normal-play settings.

To restore a default profile, close SFC, rename that settings file as your backup,
then launch again. Do not edit immutable files in `SFCRemix/runtime`, `code` or
`defaults`; integrity checks will identify changed package inputs.

## Recovery and removal

After an interrupted run, close SFC before starting the launcher again. It checks
the saved recovery journal and restores the graphics files. To undo the first-run
graphics preparation and recover the files you had before setup, close SFC and run:

```cmd
SFCRemix-Launch.cmd --restore
```

After restoration completes and SFC is closed, removing the launcher and
`SFCRemix` folder removes the package. Keep your settings or logs first if wanted.
Do not remove game assets, saves or unrelated game configuration files.

Working files, caches and recovery records are under `SFCRemix/data`. Do not
delete recovery records or their backups while a transaction is incomplete.
If preflight refuses an unknown file, keep the message and request support.

## Reporting a problem

Normal launch saves **no run history**. Temporary models, textures and runtime
logs are working files, removed after the game closes and graphics restoration
is verified. Settings and reusable runtime caches remain. An interrupted session
keeps its working/recovery files until the next safe restoration.

To save a small troubleshooting report, double-click `SFCRemix/Troubleshoot.cmd`
instead, or use `SFCRemix-Launch.cmd --troubleshoot`. It keeps at most **five
reports, 64 KiB each (320 KiB total)** in `SFCRemix/data/troubleshooting`. Older
reports are replaced; this limit never ends gameplay. Reports contain exit and
restoration status and a short error message. They contain no model/texture
payloads, screenshots, frame traces, saves or settings. Nothing is uploaded.

Neither mode has a gameplay timer or recording storage quota. Actual disk space
needed for working files and graphics resource limits still apply. These options
do not retroactively delete historical development captures.

Report your executable version, native resolution, GPU/driver, ship models and
what happened. If you opted in, include the short report from
`SFCRemix/data/troubleshooting`.
Do not upload your entire game folder, captured ship geometry/textures, saves or
private settings. A gameplay video can help with camera-dependent visual issues.

Known limitations include cloak/transparency, unqualified break files, some
camera-dependent gray-wing appearances and incomplete coverage of every model
or effect. This is ship replacement, not a complete replacement of all SFC
rendering or a formal project-milestone completion claim.

## Licenses

Project-authored code is MIT licensed. Vendor software retains its separate
terms and copyright notices; see the package's third-party notices. No game
assets, captured models/textures or contributed research documents are included
in the release ZIP. The user supplies the game.

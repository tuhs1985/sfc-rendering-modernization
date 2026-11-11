# Portable launcher

This directory owns the application entry point, not the release toolchain.

| Input | Responsibility | Installed destination |
| --- | --- | --- |
| `launcher.cpp` | Native Windows entry, options, elevation and bundled-Python launch | Compiled `SFCRemix/launcher.exe` |
| `bootstrap.py` | Package validation, settings, recovery and coordinator startup | `SFCRemix/code/src/launcher/bootstrap.py` |
| `session_recording.py` | Default-off recording and safe working-file cleanup | `SFCRemix/code/src/launcher/session_recording.py` |
| `SFCRemix-Launch.cmd` | Double-click convenience entry | Beside the `SFCRemix` directory |
| `Troubleshoot.cmd` | Optional minimal-report entry | `SFCRemix/Troubleshoot.cmd` |

Build and packaging remain under [tools/release](../../tools/release/README.md).
Only the explicit production allowlist and package recipe determine what ships;
this README and C++ source are not installed runtime files.

The native launcher and Python package layout must be updated together. Existing
packages keep their own launcher and are not changed by a source-tree migration.
The bootstrap explicitly establishes its import paths for isolated bundled Python
(`-I -B`); it does not search the development checkout or old release-tool folder.

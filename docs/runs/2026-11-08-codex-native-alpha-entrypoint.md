# Double-clickable alpha entry point without PowerShell

November8,2026. Sponsor directed replacing PowerShell for normal alpha launching.
This supersedes the earlier WinPS5.1 delivery choice. No game launch, renderer
change, appearance change, commit or publication in this increment.

## Implemented

`SFCRemix-Launch.cmd` directly starts native `SFCRemix/launcher.exe`, which starts
the bundled Python bootstrap. There is no powershell.exe, pwsh.exe, script
execution-policy change, PATH lookup or external application installation in this
launch chain. The old release `launch.ps1` is removed from source/private package
and its manifest roles now identify the native executable.

The native launcher locates its own package, accepts only play/preflight/restore
actions, supplies explicit working directory/context, waits for the owned runtime
and preserves exit status. The CMD file keeps errors visible instead of closing
immediately. The elevated parent reports the evidence location if its elevated
child fails. Existing administrator policy is retained with one Windows RunAs
request where needed; preflight and help do not request elevation. Non-admin SFC
qualification remains a separate pending step.

`tools/release/build_launcher.py` builds the x64 static-runtime executable through
the existing Visual Studio toolchain. Its PE imports are Shell32/Kernel32 system
DLLs. Native launcher startup adds no Python/VC/PowerShell installation dependency.
The package stager and user guide now use this entry. Existing development-only
PowerShell tools are outside this normal-play change.

## Validation

- 731 Python regressions pass, including native argument/help checks and a ZIP
 assertion that the distributed CMD calls launcher.exe without PowerShell/.ps1.
- Actual installed native preflight passes the private 4143-file manifest and
 existing native game-path/hash check without starting SFC.
- The private exact CMD entry passes `--preflight` through Command Prompt.
- Fresh spaced/accented fixture and the same fixture moved to another directory
 both pass native entry-point preflight. Installed normal coordinator preflight
 also passes; no game or Toolkit is started and source-copy files are unchanged.
- Only the private entry point/manifest changed; prior files are retained under
 ignored `artifacts/alpha/cmd-entry-rollback`. User settings and game files are
 preserved. Evidence is in `artifacts/alpha/cmd-entry-preflight.json`,
 `cmd-boundary-preflight.txt`, `cmd-entry-moved-fixture.txt` and
 `python-regressions-cmd-entry.txt`. The final executable includes an additional
 error-location message; final native/CMD preflight covers that build.

## Sponsor next action

Double-click `C:\Project\SFC-Alpha-Checkout\SFCRemix-Launch.cmd` and accept the
current Windows administrator prompt. No terminal or `.ps1` interaction is
required. Actual elevated/gameplay launch and normal exit still need sponsor
checkout. Public ZIP/vendor/profile/second-machine gates remain open.

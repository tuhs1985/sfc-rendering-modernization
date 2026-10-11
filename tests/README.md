# Verification placeholder

This directory is reserved for repeatable tests and legally trackable fixtures.
Game binaries and proprietary assets must remain outside Git.

## M1 offline checks (no gameplay)

Use the bundled PowerShell 7/Python runtimes recorded in the probe definitions.
`tools/m1_component/build_m1_component.ps1` builds x86 binaries and runs contract,
WINMM forwarding, source-copy, production tint lifecycle and shading-off tests.
Generated binaries stay under ignored `artifacts/m1/bin/`.

Python: `python -m unittest discover -s tests -p 'test_*.py'`.
In the restricted Windows sandbox set process-local TEMP and TMP first to the
existing ignored `artifacts/m1/test-temp` absolute directory; default sandbox
temporary directories may reject fixture writes. Do not change system settings.

Windows PowerShell 5.1 runtime shim tests are harmless and do not launch SFC:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tests/test_m1_visual_entry_runtime.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tests/test_m1_visual_entry_runtime.ps1 -EntryName start_m1_shading_off_session.ps1
```

Runtime and visible-behavior claims require the separate versioned probe and
sponsor observation; these synthetic tests cannot establish them.


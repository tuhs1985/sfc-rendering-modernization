# Verified ReShade ZIP build inputs

November 11, 2026. Based on local commit `513ceea` on
`codex/tester-graphics-setup`.

```powershell
& .\artifacts\alpha\python-3.12.14\python.exe -B .\tools\release\prepare_reshade_payloads.py
```

The builder checks the verified standard installer archive and stages
`ReShade32.dll` from its embedded ZIP when needed. It verifies the standard
6.7.1.2133 and full-add-on 6.7.1.2131 binaries and the upstream license notice
before emitting their recipe entries. The standard DLL is a separate
`reshade_baseline_proxy` role. The full-add-on keeps the existing
`reshade_proxy` role and path. Both live inside `SFCRemix`.

The ZIP regression checked both DLL paths and the notice, verified their
archive contents, and rejected a recipe whose baseline disagreed with the
standard role. All 770 Python regressions passed. A private functional copy
staged the real binaries and passed preflight with 3,852 immutable files
before and after moving the package. The installed cache comparison also
passed. Evidence is under
`artifacts/alpha/preflight-fixtures/20261111-204435-676774` and
`artifacts/alpha/reversible-setup-zip-*.txt`.

No public ZIP was built. No accepted game copy was changed. Launcher
preparation and rollback are the next implementation boundary.

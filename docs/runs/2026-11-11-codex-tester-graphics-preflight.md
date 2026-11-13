# Tester graphics preflight

November 11, 2026. Based on merged GitHub master `e324e5c`, on branch
`codex/tester-graphics-setup`.

Run the checker from a copy with the updated private package extracted.

```cmd
SFCRemix-Launch.cmd --preflight
```

The command requires neither elevation nor a running game. Package integrity
and client identity still gate the graphics report. The report identifies each
detected issue in the existing graphics profile and exits with failure when
any issue remains. Normal play shares the same checks and rejects the first
issue. The existing success receipt and native launcher preflight carry forward.

The actual packaged launcher detected a missing DDraw DLL, wrong baseline
ReShade DLL, protected SFC settings edit, mismatched dgVoodoo dimensions and a
conflicting D3D9 proxy in a single run. All files in the disposable copy were
hashed before and after. The checker changed none. The fixture passed again
after the test inputs were restored. The package also passed at its original
path and after moving through a path containing spaces and a non-ASCII
character. All 765 Python regressions passed. No game or renderer started.

Local evidence is in `artifacts/alpha/tester-graphics-preflight-*.txt` and the
private fixture under `artifacts/alpha/preflight-fixtures/20261111-052937-233465`.

The default `tools/release/stage_preflight_fixture.py` run now repeats the
five-mismatch check in a fresh minimal package, verifies the original and
modified file hashes, and records the restored preflight in `result.json`.
Use the pinned Windows Python from the repository root. The repeatable run
passed in `artifacts/alpha/preflight-fixtures/20261111-054142-050028`.

The [graphics baseline audit](../releases/GRAPHICS_BASELINE_AUDIT.md) records the
exact vendor identities and existing graphics constraints. Qualify a portable
profile with verified inputs, then add explicit backup and restore for setup.
The existing per-run ReShade swap and its rollback remain separate. This
increment has no preparation command or clean-machine gameplay result.

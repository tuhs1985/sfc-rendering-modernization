# Proposal

## Why

The shipped session coordinator still shares its implementation directory with development probes and qualification runners. Give its orchestration, normal-exit handling and report lifecycle explicit application ownership, following the committed launcher separation.

## What Changes

- Relocate three session modules into `src/session`, with descriptive module names.
- Keep small development-only compatibility entry points for existing launch scripts and probe imports.
- Connect the installed bootstrap and package allowlist directly to application modules, excluding compatibility shims.
- Update current tests, qualification source inventories and documentation together.

## Capabilities

### New Capabilities

None; pure refactor with `skip_specs: true`.

### Modified Capabilities

None. Diagnostic modes, rendering, settings, recording, cleanup and native fallback retain their behavior. Splitting diagnostic branches out of the coordinator is a later change.

## Impact

`run_return_game.py`, `session_exit.py`, `run_report.py`, their source/import consumers, bootstrap and release inputs. Existing private alpha and all game assets remain unchanged. No runtime upgrade, appearance tuning or new renderer work.

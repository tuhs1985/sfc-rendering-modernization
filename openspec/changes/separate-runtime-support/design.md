# Design

Canonical src/runtime modules are runtime_context.py, release_manifest.py, windows_processes.py, runtime_files.py, copied_preferences.py and session_recovery.py. They retain original implementations and context semantics. Bootstrap and standalone coordinator add src/runtime before their first runtime import; installed allowlist ships canonical files only.

Legacy same-named development modules use standard importlib file loading with the public module name, registering the canonical module before execution so dataclasses and shared mutable state keep one identity. The runtime path is prepended first; dependencies use canonical modules directly. The old recover_broad_session entry aliases session_recovery and forwards its existing CLI. These compatibility files never ship. Recovery uses graphics_transaction.atomic_copy, not broad_capture.

Preserve all integrity and game-absence checks, original assets, ExtraFrame, untimed play and existing settings. Application source inventories include src/runtime in addition to legacy entry points. Update package/qualification entry search paths without updating accepted existing packages. Shared GPU and asset source stays put.

Verify legacy/canonical identity in isolated processes, portable paths, actual manifest validation, actual temporary-file recovery and refusal while game is alive, repeated startup/normal exit/error cleanup, diagnostic command admission and import exclusion. Then rebuild unchanged native source against current inventories, run affected GPU/worker fixtures and package checks, prepare a separate playable copy, and keep sponsor gameplay acceptance pending.

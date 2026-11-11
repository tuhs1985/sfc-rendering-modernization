# Game session orchestration

| Module | Responsibility |
| --- | --- |
| `coordinator.py` | Validate requested mode, prepare/launch the copied game and owned helpers, supervise the session, restore and finalize |
| `exit_monitor.py` | Observe verified game exit and retire owned controllers; no game hooks |
| `reports.py` | Atomic bounded result checkpoints and interruption reporting |

The installed [launcher bootstrap](../launcher/bootstrap.py) imports this
coordinator directly. The release allowlist installs these three files under
`code/src/session`; the application never imports the old forwarding tools.

Existing development commands at `tools/remix_runtime/run_return_game.py` and
legacy imports of `session_exit`/`run_report` forward to these same module objects.
The wrappers contain no alternate orchestration or independent report state.
They remain for existing native-insertion launchers and probe tools, not for the
release package. Source inventories track both wrappers and actual implementation.

This first move preserves the existing coordinator's diagnostic options and
branches. It does not yet extract them into a separate diagnostic runner or
claim a performance improvement. Shared rendering, resource preparation, recovery
and IPC modules still live under `tools` pending their own bounded migrations.

Game launches still require established preflight/qualification. Relocation does
not authorize renewing old source-hash receipts without their documented checks.

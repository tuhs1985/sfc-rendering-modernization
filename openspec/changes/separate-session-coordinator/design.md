# Design

## Application boundary

Move `tools/remix_runtime/run_return_game.py` to `src/session/coordinator.py`, `session_exit.py` to `exit_monitor.py`, and `run_report.py` to `reports.py`. Preserve executable function/class bodies, including diagnostic options. This is ownership separation, not yet diagnostic-code extraction.

Coordinator establishes its own directory and the unchanged shared runtime directory before importing helpers. The installed bootstrap adds `code/src/session` explicitly and imports coordinator directly. Production inventory swaps three entries; total stays 59. Native launcher still starts the relocated bootstrap; no native rebuild is needed for this second move.

## Development compatibility

Keep three thin files at old tool paths. They import the canonical application module; imports alias the same module object so patches, exception identity and report state are shared. The old runner script forwards its CLI with unchanged exception reporting. No alternate coordinator implementation and no wrappers in the shipped package. Existing launcher command paths remain valid.

Qualification source inventories must include the canonical modules as well as wrappers where applicable. Existing exact-hash receipts are historical; never silently refresh them or relax verification. Before this change the development normal preflight already rejected `tools/d3d9_proof/live_light_binding.py` against its old native-cohort receipt. Record that pre-existing state separately from the new package-path qualification.

## Verification

Compare moved function/class ASTs against commit 8e69c93. Exercise legacy imports/state sharing and CLI admission in isolated subprocesses, direct application entry, all regressions and installed read-only package/coordinator preflight. Preserve existing alpha and appearance. No game/GPU process starts; no new renderer or gameplay result is claimed. Document source-only qualification limits rather than issuing a gameplay launcher for a non-playable fixture.

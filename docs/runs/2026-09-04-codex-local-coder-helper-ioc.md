# Codex Run Record — First SFC local-coder-helper IOC

## Run identity

- Run ID: `CODEX-20260904-LOCAL-HELPER-IOC-001`
- Date: 2026-09-04
- Active state: completed M0 / TRL 3 repository; post-M0 tooling validation
- Starting commit: `38d57fd5889b2f641e8a396d7c1d66bd90c6759b`
- Delegated task ID: `sfc-analyzer-unittest-20260904-01`
- Mode: `local`
- Context profile: `normal`

## Pre-run safety snapshot

- ZIP: `C:\Project\SFC-Modernize Engine Backups\SFC-Modernize-Engine-pre-local-helper-20260904-165519.zip`
- Size: 550,448 bytes; 275 entries.
- Included `.git`, all versionable project content, and current uncommitted UAC
  policy work.
- Excluded supplied game/reference originals and disposable generated
  `artifacts/pre-m0`, analysis, capture, dump, scratch, and temporary content.
- The active working tree was not altered or cleaned for the backup.

## Selected delegated task

Add one standard-library regression test for
`tools/m0_probe/analyze_probe_log.py`. This was a real, presently useful task:
the analyzer gained semantic owner mappings during M0, while `tests/` still
contained only a placeholder. The task was deterministic and required no
executable interpretation, architecture choice, ABI judgment, or semantic
ownership adjudication.

Context supplied to Tiel was limited to:

- `tools/m0_probe/analyze_probe_log.py`;
- `tests/README.md`;
- the 22-column probe CSV header as non-file context.

No game binary, raw capture, helper-project source, reverse-engineering
uncertainty, or unrelated repository content was supplied.

Acceptance criteria required exactly one new file,
`tests/test_analyze_probe_log.py`, using only `unittest`, temporary synthetic
CSV data, and standard-library process/file handling. It had to verify probe-ID
output naming, event counts, indexed-draw shape, geometry caller and argument
shape, ship-to-visual identity, visual-to-Model0 identity, and meaningful JSON
and Markdown output. The required command was
`python -m unittest tests.test_analyze_probe_log`.

## Delegation and Tiel result

`local-coder-helper/delegate_coding_task` was invoked exactly once through its
STDIO MCP endpoint with the task ID, mode, profile, supplied files/context, and
acceptance criteria above.

- Tiel status: `failed`.
- End-to-end local-model latency: approximately 92.2 seconds.
- Helper-reported task duration: 62.845 seconds.
- Tokens: 3,111 prompt; 2,048 completion; 5,159 total.
- Result: no proposed patch. The helper rejected Tiel's malformed structured
  JSON because `proposed_result` ended in an unterminated string.

## Codex adjudication and implementation

The local result was **rejected** because no complete, parseable proposal was
available. It was not applied, reconstructed from raw output, or retried.
Following the first-proof policy, Codex implemented the bounded test directly.

Codex reviewed the test against the analyzer's actual CSV parsing and field
mappings. The accepted implementation creates only temporary synthetic input
and output, invokes the real analyzer, and asserts the required JSON and
Markdown semantics. It does not use proprietary data or write generated files
into the repository.

Validation:

- `python -m unittest tests.test_analyze_probe_log -v` — PASS, one test in
  approximately 0.09 seconds.
- `python -m py_compile tools/m0_probe/analyze_probe_log.py tests/test_analyze_probe_log.py` — PASS.
- `git diff --check` — PASS.

## IOC assessment

Delegation did **not** save meaningful Codex work in this run because the
proposal could not be parsed and the implementation had to be written and
validated locally.

Concrete deficiencies exposed:

1. The normal-profile 2,048-token completion ceiling allowed the structured
   response to truncate inside `proposed_result`, converting an otherwise
   bounded task into a terminal malformed-JSON failure without a proposal.
2. The MCP registration is project-scoped inside the helper repository and was
   not surfaced as a native callable tool in the SFC repository session. The
   IOC therefore had to address the same registered STDIO MCP endpoint
   directly. No helper files were modified.

## Files and repository state

- Added `tests/test_analyze_probe_log.py`.
- Added this run record.
- Pre-existing uncommitted UAC-policy work remains intact in the runner,
  M0-RT-002/M0-RT-003 documentation, shared runbook, and its run record.
- No runtime probe or game process was launched.
- No raw SFC evidence was generated or modified.
- Nothing was staged.
- Nothing was committed.

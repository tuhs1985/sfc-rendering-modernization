# Run47 — tolerate native-light snapshot sharing collisions

Date2026-10-18 America/New_York. HEAD2fa8032; existing Run40–46 source/docs remain
unstaged/untracked, index empty. Sponsor reports successful tuning interrupted by
Errno13 on gate/native-light-latest-2.bin. No new rendering feature requested.

## Evidence / starting state

Actual artifacts/remix-runtime/runs/20261019-012229-232879-in-game:
light_tuning=true; workflow320.594s;15accepted config revisions/19rejected edits,
2072light packets,5566drawn/5568rendered/failed0. The unhandled PermissionError
on snapshot read is CONFIRMED. A Windows atomic replacement/sharing collision is
a STRONG HYPOTHESIS for the original cause, not independently captured as an OS
error32 event. Persistent ACL denial is not proven or "repaired" by changing ACLs.
Sponsor says working well apart from interruption; no all-type appearance claim.

Original result remains PARTIAL: normal_game_exit=false,gate_clean_unloaded=false,
controller still running at report time,renderer_exit0,accepted critical files and
launcher settings unchanged. Subsequent read-only process inventory finds no game
or controller41960. Do not rewrite original result or infer normal exit/controlled
unload solely from process disappearance. This was genuinely longer than90seconds.

## Change / policy

Only tools/remix_runtime/live_lights.py and tests/test_live_light_wiring.py change
implementation/tests. New read_latest uses explicit Win32 CreateFileW GENERIC_READ,
FILE_SHARE_READ|WRITE|DELETE,OPEN_EXISTING; reads at most6157B, requires6156B and
closes its handle on success/failure. Existing writer atomically replaces immutable
snapshots; sharing delete permits replacement while a reader retains the old file.
No new game hook, ABI, native writer, SDK, security/ACL or configuration changes.

Tuning record iterator catches transient access/sharing/missing errors (Windows
2/3/5/32/33 or PermissionError/FileNotFoundError), skips that update, and retries
at the existing next100ms poll. No busy-spin/sleep/retry loop. Native observation
timestamp is never freshened by an unreadable/duplicate file. Last valid packet
may continue only under the unchanged500ms light-age and100ms image-age rules;
prolonged unreadability omits the extra copy, never original SFC rendering.

read_busy/read_recoveries/read_pending provide bounded diagnostic counters. First
busy/recovery messages use existing100message limit. Malformed data/wrong size and
other IO errors are NOT reclassified as benign sharing collisions. Persistent
unreadability remains visible in counters/messages and freshness failure, rather
than weakening permissions or blocking SFC. Existing90s short mode is unchanged.

## Verification

Bundled Python3.12.14,ctypes Win32; no package install. Tests run via
`python -m unittest discover -s tests -p test_*.py` with TEMP/TMP artifacts/test-temp.
250PASS4.843s. New tests: injected busy read keeps exact original QPC in emitted
packet; actual Windows exclusive file handle provokes reader failure, then removal
of lock allows next poll recovery; malformed-size exception closes handle and a
Unicode filename can be read/replaced/deleted afterward. These are real OS sharing
tests, not just a mocked exception. No new native build needed (binaries unchanged).

Full ten source-matched standalone GPU gates, read-only --light-tuning preflight,
archive/pins/final status recorded below after completion. No SFC gameplay started
by Codex. Existing native observer receipt remains applicable. No capture limit
increase, continuous screenshots or additional raw dumps; fixed-size reads only.

The fix-only ten standalone gates013216..013435 passed before sponsor added a
separate dome task. Their qualification is superseded by combined Run48 final
eleven-gate validation. No original evidence or manifests rewritten. See Run48
for final current pins/archive and launcher readiness; Run47 fix remains included.

## Scope / state / next action

Preserve all sponsor TOML edits and original client/reference artifacts. New record,
probe amendment and HANDOFF accompany source/test fix. No stage/commit/deletion.
Exact next action after qualification: sponsor resumes with the SAME tuning launcher,
edits/saves as desired and exits normally; inspect new read_busy/recovery counters
and final exit classification. Actual long-session recovery remains to be confirmed
in gameplay; do not force another artificial camera or timing exercise.

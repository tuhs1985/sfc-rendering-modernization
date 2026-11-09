# Alpha normal play: optional retained reports

Sponsor confirmed the corrected private package renders correctly. Latest
reviewed pre-change run `20261109-044415-086471-in-game` has error=null, normal
exit and restored proxy. Sponsor requests simple player messages, recording off
by default, optional minimal troubleshooting and no diagnostic quota stopping
normal gameplay. Required working files are explicitly acceptable.

## Installed choices

| Launch | Retained run data |
| --- | --- |
| `SFCRemix-Launch.cmd` or `SFCRemix/launcher.exe` | Off: no run history after verified restoration |
| `SFCRemix/Troubleshoot.cmd` or launcher `--troubleshoot` | One allowlisted JSON summary; up to 64 KiB; newest five only (320 KiB total) |

Reports contain session identifier, exit/restore status, stage and a short error.
No geometry, textures, screenshots, frame traces, settings, saves or uploads.
Paths are redacted. Report rotation never stops gameplay. Both modes are untimed.
Bootstrap hides development instructions/progress and prints short start, mode,
completion and actionable error messages. Native launcher accepts the optional
mode and its help describes default/cap. Troubleshooting CMD is a required
manifest role and staged beneath the package, preserving the root ZIP layout.

## Working files and cleanup

The renderer still needs temporary captured/prepared assets, internal worker logs
and transaction backups. New release sessions get an atomic retention marker.
After coordinator shutdown, absence of SFC and a verified restored game profile,
retention removes that session's working directory. Off creates no report;
minimal writes only the allowlisted summary. Settings/reusable environment cache
remain. Existing unmarked development evidence is deliberately untouched.

An interrupted/unsafe-to-delete session remains until the existing recovery path
restores its transaction. Malformed/incomplete retention/recovery records are
preserved, not guessed complete or allowed to block unrelated report rotation.
Linked data/session roots and unexpected deletion targets are refused.

Removed recording-quota termination from **installed untimed play** at three
layers: coordinator evidence reservation/log checks, worker aggregate evidence
allowance/reserve, and the owned-process guard's scratch-size kill. The guard also
skips recurring scratch directory scans in this mode. Development diagnostic
limits remain. Actual free disk checks, per-asset decoding/memory bounds, process
ownership, parent-death cleanup and graphics fallback remain.

## Validation

- 742 desktop Python regressions passed after recording/budget changes.
- Final eight focused retention tests passed, including the subsequently added
  malformed-record test: off deletes real working files without reports; minimal
  rotates nine sessions down to five; live/incomplete sessions preserve backups;
  restored sessions clean; historical evidence/settings survive; bootstrap quiet
  mode/options exercised; simulated enormous inventory doesn't reject play.
- Actual rebuilt x86 guard process: child writes above a 64 KiB scratch quota and
  over its console cap. Installed play completes with stop_reason=0; development
  control still stops with reason21. This exercises the real process boundary.
- Isolated installed Python initially exposed an import search-path omission;
  corrected bootstrap to include its release-module directory before importing
  retention. Exact updated native preflight and help then pass (4,147 inputs).
- Fresh staged, moved non-ASCII/spaced package and prepared coordinator preflight
  pass. Existing installed captured-FCA initialization/light binding smoke passes.
- `git diff --check` passes. No SFC gameplay or new renderer run launched by Codex.

Private checkout updated with manifest hashes and rollback under
`artifacts/alpha/recording-policy-rollback`. Appearance/settings unchanged. New
retention behavior awaits ordinary gameplay exit/relaunch confirmation. No tag,
public ZIP, commit or push. Older private captures were not purged by this change.

# Run296 — Preserve campaign-saved player names

Sponsor direction:changing a player name is ordinary game use,not a blocker.

## Change

Allow `[Network] PlayerName` edits in copied `sfc.ini`,without editing or restoring
the user's value. All other INI bytes and protected copied binaries/configs remain
checked. Accepted original installation/launcher checks remain exact.

Startup compares a protected INI signature against the independently prepared
reference. Reference `artifacts/remix-runtime/test-install/sfc-baseline.ini` was
created once from the accepted prepared source only after matching its full hash
to `source-copy-files.json`;its hash is included in local cohort qualification.
No private reference/config contents are added to Git. Never regenerate it from
the mutable test copy to authorize an unknown configuration.

Each new session records its starting protected signature. Normal exit and
interrupted-run recovery use it,so a later name edit neither reports failed
restoration nor prevents verified proxy/config rollback. Raw before/after hashes
remain recorded;`copied_player_preferences_changed` identifies permitted changes
without recording name values in the new preference field.

Legacy recovery retains exact behavior unless a verified prepared reference can
explain the difference;unprovable changes remain rejected. Duplicate Network
sections/player-name entries are rejected as ambiguous. No general INI bypass.

## Verification

-694Python tests PASS. New pure cases cover allowed names,protected graphics/
  other-network values,same key in another section,ambiguous duplicate names,
  changed proxy,verified reference hash,per-session signature and strict missing-
  signature behavior.
-Two recovery integration cases cover new session signatures and legacy prepared
  references. Both preserve the edited name while restoring proxy/config,and
  reject a graphics change before touching either restoration target.
-Native-light worker/source and native-cohort qualification records refreshed.
  Existing native/GPU binaries unchanged;previous two600-frame GPU regressions
  reused. No unrelated render tests or another gameplay run requested.
-Actual untimed and timed native multi-ship read-only preflight PASS with the
  sponsor's existing saved name. Neither source nor copied `sfc.ini` edited.

Run294's historical PARTIAL record remains intact;this corrects future policy,
not past evidence. Run295's cleanup remains complete and its config blocker is
now resolved. Gray KFF wing appearance/dropout remain separate findings.
Changes unstaged/uncommitted. Normal launcher command unchanged.

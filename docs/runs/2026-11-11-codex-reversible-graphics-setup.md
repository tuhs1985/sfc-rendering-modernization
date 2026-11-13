# November 11 reversible first-run graphics setup

The normal launcher verifies the pinned SFC executable and supported game
settings before proposing graphics changes. The setup matches real device
LUIDs from the packaged Remix and dgVoodoo probes. It applies a verified
portable profile after confirmation. A separate setup journal tracks every
original, including files that were absent. Restoration refuses to overwrite
independent edits. Existing interrupted-session recovery runs before setup
restoration.

## Qualification

- 775 Windows regression checks passed. Filesystem tests covered declined
  changes, repeat setup, interruption during setup and preservation of edits.
- A private functional package verified all 3,860 immutable files after a
  move to a directory containing spaces and a non-ASCII character.
- Installed qualification deliberately removed DDraw.dll and supplied
  mismatched dxgi.dll and ReShade.ini in the disposable copy. Read-only
  preflight found all three. Declining preserved all three. Approving ran
  the device probes, prepared the profile, and passed strict preflight.
  Repeat preparation completed with closed stdin. Restore removed the added
  DLL and returned both replaced files byte-for-byte, and the test reset and
  preflighted the fixture for gameplay.
- The installed preparation test used the bundled Python entry point.
  Native launcher preflight was exercised separately. No gameplay was started
  during these checks.
- Windows temporarily held the GPU probe scratch directory open in two
  earlier attempts. Setup now keeps its dedicated scratch directory and
  clears only verified child paths, retrying transient file locks.

Local evidence is under `artifacts/alpha/preflight-fixtures/20261111-205741-184808`
and `artifacts/alpha/first-run-setup-installed-verified.txt`.

## Gameplay checkout

The sponsor reported the private package worked through the normal CMD
launcher. The game copy already matched the qualified graphics profile.
Normal play retained no diagnostic run records. After gameplay the native
read-only preflight verified all 3,860 immutable package files and accepted
the restored game graphics profile.

The sponsor identified rapid camera panning as the trigger for the prior
gray-wing appearance and suspects the mask briefly falls out of sync with
the ship image. Compare colour, depth and coverage frame/camera identity at
native insertion during a targeted reproduction. This checkout supplied a
visual reproduction, with the synchronization mechanism still unverified.

Qualify gameplay and recovery on a clean machine and GPU selection on a
hybrid system. Review remaining vendor notices and package closure before
assembling the public ZIP.

## Fixture retention cleanup

Removed 14 superseded preflight game directories and six named private
checkouts under `artifacts/alpha`. The current
`20261111-205741-184808/Moved portable game é` checkout stays at its
existing launch path. Dated preflight receipts and qualification output
remain in place. Package manifests and files differing from the current
checkout and source, including settings and images, are recorded in
`artifacts/alpha/retired-checkout-records-20261111/removed.json` and
archived alongside it. Existing saves in removed copies matched a retained
copy. Net logical removal was 38.85 GiB, leaving 26.78 GiB across artifacts.

The stager now removes temporary game/package trees after preflight, including
on failure. A successful functional checkout can be retained explicitly
with `--keep-game`. The installed read-only preflight passed and left no
new game tree. A focused lifecycle check also exercised default cleanup,
explicit retention, and cleanup after a simulated failure.

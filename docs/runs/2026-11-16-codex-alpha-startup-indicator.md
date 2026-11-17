# Alpha startup status indicator

Branch `codex/alpha-startup-indicator` is based on the accepted alpha commit
`e450c30`. SFC-07 was checkpointed separately at `e07a025`.

The packaged launcher opens a small nonactivating status window before starting
bundled Python for normal and troubleshooting launches. The bootstrap clears
the inherited event from its environment and disables its inheritance before
starting other processes. The coordinator signals it at the existing
graphics-ready check. The window also closes when the bootstrap exits.
Diagnostics such as preflight, prepare and restore use their existing console
output. The event does not gate the game or change startup timeouts.

The strict x64 launcher build passed. A standalone fixture exercised the real
window and process wait with normal, slow, failed and no-window scenarios.
The focused recording suite passed eight checks with one unrelated job-guard
test skipped because its binary is absent in the isolated worktree. The
startup readiness test verified that a failed readiness check does not signal
the event.

The private checkout ZIP contains 3,884 validated inputs and passed installed
read-only preflight from a temporary extracted profile. Test profile hashes
matched after preflight. SHA-256
`625dfcf1ac0133847fcdde056a64d4376b0ca22a19321824fc1f8d349959ba02`.
The unchanged components came from the accepted alpha package. The new package
is a private checkout build from uncommitted source. The existing tester ZIP
remains the release baseline.

Next validate the loading window in a real packaged launch, including a slow
start if one occurs. Confirm the window disappears at the menu and the normal
startup error remains legible. The synthetic fixture does not establish
visibility over the game's presentation on all display setups.

The follow-up centers the window in the foreground monitor's usable work area
without taking focus. The strict launcher build and the window fixture passed.
The fixture checked horizontal and vertical placement within one pixel, as well
as normal readiness, delayed readiness, startup failure and commands that skip
the window. Real game startup remains to be checked.

The centered private checkout ZIP passed extracted-package read-only preflight
with 3,884 inputs and unchanged protected files. SHA-256
`29cd7f41f97b01d04695536590ab961360b3273a713a1742330e44c668d65af7`.

The next private candidate displays four steps with a per-step elapsed timer.
Package verification begins in the initial launcher window. The bootstrap
signals game-copy preparation after manifest verification. The coordinator
signals Remix startup before launching the host and SFC graphics startup after
the host session is available. The existing graphics-ready event dismisses the
window. Events are anonymous and inherited only by the bootstrap, which clears
their environment variables and disables inheritance before starting helpers.
Stage updates do not gate game startup or write diagnostics.

The standalone Win32 fixture verified all four labels, timer advancement and
reset, stale-stage handling, centering, closure on readiness and failure, and
quiet non-play startup. The focused Python suite passed nine checks with one
unrelated job-guard check skipped. The timer refreshes once the bundled Python
process has been created and the launcher enters its message loop.

The four-stage private checkout passed extracted-package read-only preflight
with unchanged protected files. SHA-256
`3f6428ba46f741568847b0315e2202f13ccb1b41b0ff1f4b81317f87a65ef48c`.
The sponsor confirmed this package worked in a live launch and designated it
the new private alpha baseline on November 16. This checkout covers the
startup window. It adds no new graphics or compatibility qualification.

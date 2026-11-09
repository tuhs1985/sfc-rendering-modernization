# Private alpha launcher portability correction

November8,2026. Unstaged/uncommitted changes; no publication or game launch by
Codex. Sponsor retry is pending.

## Failure attribution

Private run `C:/Project/SFC-Alpha-Checkout/SFCRemix/data/runs/20261108-172602-847035-in-game`
ended after0.641seconds with no target PID. `launcher.log` states
`LAUNCH_FAILED not the approved copied client win32=0`. The native launcher still
required the exact development path `C:/Project/SFC-Remix-Return-Test/StarFleetOP.exe`.
The valid extracted game at the new location was rejected before CreateProcess.
This was a packaging defect, not a game crash or rendering regression.

The result records unchanged critical files/preferences, stopped control host,
no controller left running and `broad_proxy_restored=true`. An explicit installed
restoration check is retained separately. The earlier package preflight never
invoked this native path check; its success did not establish launch readiness.

## Changes

- Native release launch derives the authorized game from the package parent.
  It verifies the actual launcher's location inside that package, canonical
  game/component paths and the pinned client hash. The run copy of the add-on
  must match the immutable package add-on hash. Unknown targets/components and
  attempts to use the developer launcher as a package launcher are refused.
- Development launch keeps its exact approved test-copy restriction. Standalone
  fixtures keep their owned-artifact restriction; this fix does not authorize
  arbitrary process injection or alter capture/rendering paths.
- New `--check-game` mode exercises native path/hash/import-name validation
  without creating a game process. Installed bootstrap invokes it before
  preparation and during `-Preflight`, so the observed failure is caught earlier.
- Detours accepts a wide game path but a narrow DLL import name. For Unicode
  package directories, use an ASCII relative add-on path contained beneath the
  child's explicitly supplied working directory. No short-name dependency,
  asset change or extra DLL in the game root is introduced.
- Native launcher now honors the existing untimed play-session flag; fixture
  and timed-test watchdogs retain their limits. The inherited5/33-minute launcher
  wait is not allowed to end the alpha's explicitly untimed normal play.

## Validation

- x86 strict native build succeeds. Path/policy test:14checks including foreign
  targets, immutable/run-copy admission, Unicode import names and untimed waits.
- Actual compiled launcher passes no-game preflight from a synthetic moved
  Unicode package; wrong game/root and modified add-on fail. This checks the
  process/file boundary rather than only Python's manifest logic.
- Actual Detours preload and600-frame multi-ship renderer/insertion passes in
  `artifacts/remix-runtime/runs/20261108-173157-657031-é-return-fixture`.
  Two pixel comparisons have zero mismatches; three owners, native depth/text,
  graphics-state restoration, normal receiver retirement and SDK shutdown pass.
- Full Python suite:730tests pass, including actual native launcher preflight.
  Existing development untimed BRK preflight also passes. Cohort qualification
  retains the prior Strict renderer proof plus this new ExtraFrame boundary
  proof; the wait-policy change is covered by focused native checks.
- Updated only the private package's bootstrap and native launcher. Previous
  files/manifest are retained under ignored `artifacts/alpha/launcher-fix-rollback`.
  New manifest hashes verify; installed WinPS5.1 preflight passes4143inputs.
  Evidence: `artifacts/alpha/private-launcher-fix.json` and native/Python logs in
  `artifacts/alpha`. Appearance settings and existing gameplay captures preserved.

## Next action

Sponsor retries the same installed command and exits normally. Review actual
packaged gameplay and cleanup before claiming launch or alpha acceptance. This
correction does not finish vendor/profile review, second-machine testing or
approve a public ZIP/tag.

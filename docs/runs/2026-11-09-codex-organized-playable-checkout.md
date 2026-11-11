# Requalified organized-source private gameplay checkout

November 9, 2026 America/New_York; newer evidence directories use November 10 UTC.
Sponsor requested commit and continuation. Committed session separation as
`0df894b36fe78f875d914b25ac2d0ee6ebbe17f9` on
`codex/organize-repository-foundation`. No push, merge, tag or release.

## Development qualification restored

Initial audit found 37 changed native-cohort inputs among 646 records and two
changed light-observer inputs among 32. This included pre-existing production
cleanup/startup changes, not just the two source moves. Archived old receipts,
candidate host and build receipt under
`artifacts/alpha/organized-checkout-qualification/before`.

The developer candidate executable still predated the profiling-off prewarm fix.
Ran the existing strict candidate build from current source. Its SHA256 is now
`1bf0045d64b2cb6283bb20e9476b64e16c436e45b1ccd6e860377d3e2e53c16b`, exactly the
already accepted private-alpha executable. No renderer source changes or new pin.

Ran existing real native-light queue/scene/shared-memory/untimed worker
qualification successfully, then two genuine standalone native multi-owner GPU
fixtures with moving/pulsing effect lights and reversible damage:

- ExtraFrame: `artifacts/remix-runtime/runs/20261110-003526-144744-return-fixture`.
  600 frames; 1,752 native ship draws, three owners, two exact pixel/depth/text
  checks, zero state errors; fixture and host exit zero.
- Strict: `artifacts/remix-runtime/runs/20261110-003634-430726-return-fixture`.
  600 frames; 1,599 native ship draws, three owners, two exact pixel/depth/text
  checks, zero state errors; fixture and host exit zero.

These fixtures include intentional admission faults/delays. Draw counts are not
real-game FPS, universal delivery guarantees or sponsor acceptance. Existing
qualifier accepted the new evidence and retained both policies. Current receipts
validate 662 cohort inputs and 35 light inputs with zero mismatches. Normal
development read-only preflight now passes through the legacy command path with
native multi-ship, ExtraFrame, untimed play, damage and break flags. No guard was
disabled and no receipt was renewed merely by replacing old hashes.

## Actual playable package prepared

Used the existing functional stager to copy the verified test game and application
dependencies into a fresh private checkout. No public ZIP produced. Original and
moved space/Unicode preflight, followed by installed coordinator preflight, all
passed. Then moved only that new game copy to the stable ignored location:

`C:/Project/SFC-Modernize Engine/artifacts/alpha/organized-game`

Package: `SFCRemix` below that game directory. It contains 3,848 immutable files,
59 Python modules matching committed `0df894b` source, the matched native launcher,
new bootstrap/coordinator paths and the fixed renderer. Old compatibility tools
are excluded. All 409 source game `.mod` files remain outside the application
package, as private test-game assets, never public distribution inputs.

The two appearance profiles are byte-identical to the existing private alpha.
Existing `C:/Project/SFC-Alpha-Checkout`, accepted installation, assets and saves
were not modified. The stager now includes the normal root CMD in functional
copies and reports that entry separately from the native executable. The freshly
prepared copy has that exact source CMD; its final-path command preflight passes.

## Installed verification

- Existing installed CPU asset/material/light check passes with the new package:
  fresh captured FCA geometry, 19,110 vertices, 58 groups, base/enhanced images,
  real light binding, excluded development modules absent, startup profiling off.
  This is CPU preparation, not GPU material consumption.
- Actual installed host/receiver normal startup/output passes with profiling off:
  readiness 3.046 seconds; all three GPU-transferred planes match exactly; one
  bootstrap output; normal owned-process exit. This is initialization readiness,
  not first-ship appearance time or a visual appearance test.
- Separate installed cancellation before first output passes, with zero output
  frames, no startup profiling rows and no remaining owned processes.
- Installed immutable package/native preflight passes at final stable path.
- 21 focused release tests pass in 2.152 seconds. Reused the prior committed
  752-regression result for unchanged runtime source; no redundant full campaign.

Detailed bounded receipts/logs:
`artifacts/alpha/organized-checkout-qualification/`, including
`playable-checkout.json`, `qualification-summary.json`, `gpu-normal/qualification.json`,
`gpu-cancel/qualification.json`, `installed-assets.txt`, `release-tests.txt` and
`development-preflight.txt`. Standalone test output stays outside the game copy.

## Sponsor checkout and remaining limits

**Gameplay checkout accepted — November 9.** Sponsor reports approximately six
minutes of stable play in the reorganized build: damage applied correctly, ships
destroyed correctly and lights worked correctly. Sponsor explicitly accepts this
qualification. This completes the hands-on regression checkout for the source
reorganization. It is sponsor observation, not a new instrumented frame-time or
cleanup measurement; normal play had recording off. No repeat run requested.

Double-click `SFCRemix-Launch.cmd` in the new game directory, or run:

```text
cmd.exe /d /c call "C:\Project\SFC-Modernize Engine\artifacts\alpha\organized-game\SFCRemix-Launch.cmd"
```

Normal play is untimed, ExtraFrame standard, recording off, replacement, weapon
lights, damage and supported break models enabled. Use a familiar skirmish;
change cameras, fire weapons, observe damage and destroy a ship, then exit
normally. These were the prepared checkout instructions; the sponsor acceptance
above now completes this step. No SFC was launched by Codex during preparation.

Other old diagnostic receipts were not globally renewed. Vendor redistribution,
public prerelease review and clean/second-machine release checks remain open.
The external-tester graphics preparation issue is explicitly parked until
repository organization is finished; see the existing Obsidian Parking Lot.
Current new work is a small functional-stager improvement, planning and records;
it is unstaged/uncommitted after the requested coordinator commit.

# FCA live destruction replacement demonstrated

November 8, 2026 America/New_York. Run:
`artifacts/remix-runtime/runs/20261108-054758-017705-in-game`.
[Curated evidence](../reconnaissance/evidence/20261108-live-break-success.json).

Sponsor confirms the test worked: fragments moved/separated correctly, with
normal controls, HUD and surrounding effects and no issues noticed. Sponsor
also explains that destroying the remaining friendly ship second ended the
game/session. Do not classify that expected exit as a BRK rendering failure.

## Functional result

Two independent FCA parent lifetimes produced four fragments each. Fresh raw
revision references confirm parents 1 and 2, with independent child epochs
`0x80000001`–`0x80000008`. Each group covers the same four partitions totalling
6,370 triangles. All eight children have successful native insertion and
original-list suppression receipts, not just accepted asset packets.

| Parent | Piece index | Owner epoch | Insertions | Suppressed lists |
| --- | ---: | --- | ---: | ---: |
| 1 | 0 | `0x80000001` | 845 | 1,690 |
| 1 | 1 | `0x80000002` | 1,121 | 2,242 |
| 1 | 2 | `0x80000003` | 1,059 | 2,118 |
| 1 | 3 | `0x80000004` | 1,055 | 2,110 |
| 2 | 0 | `0x80000005` | 220 | 440 |
| 2 | 1 | `0x80000006` | 220 | 440 |
| 2 | 2 | `0x80000007` | 220 | 440 |
| 2 | 3 | `0x80000008` | 215 | 430 |

The twice-as-many list receipts on fragments corroborate primary/secondary
submission handling. These counts are owner/list operations, not displayed FPS.
There were no fragment unavailable receipts. Native cohort unavailable3 belongs
to the intact KFF, not these pieces.

Six unique renderer assets loaded with five shared bindings: FCA intact, KFF
intact and four distinct FCA fragments; the duplicate intact FCA and the second
set of fragments reuse prepared content. No rejected or partial assets.
Instance/parent provenance is read from each raw revision's reference file;
shared manifests may retain the canonical asset's original capture provenance
and must not be used to assign a later alias to its parent.

## Timing and limits of measurement

The first set's GPU asset admissions occur approximately292–335ms after each
piece's captured source-frame start, with all four admitted approximately395ms
after the first piece's source-frame start. Derived from retained native gate
QPC stamps and the renderer's QPC-based `at_us` admission records. This is
actual live asset admission, **not** first-pixel display time or the start of
the destruction animation. The second set uses the cached assets.

| Retained gate measure | Result |
| --- | ---: |
| Frame records / insertion frames | 4,960 / 4,910 |
| Original-only frame records | 50 |
| Deadline misses / stale / invalid / partial commits | 0 / 0 / 0 / 0 |
| Median / p95 native frame elapsed | 15.643 / 16.587ms |
| Median / p95 source-to-presentation callback age | 15.523 / 16.453ms |
| p95 / maximum presentation interval | 17.817 / 28.701ms |
| Maximum output slot occupancy | 1 |

Original-only records and omitted renderer draw attempts are not all failures
or uniquely timed visible dropouts. The renderer records137omitted attempts
during residency/admission; sponsor observed no issues. No reconstruction of a
visible gap is justified from those aggregate counters. Native input invalid0;
no output-resource failure, missing depth or unresolved material publication.
These measurements qualify this fixture, not every ship, hardware profile or
formal performance threshold across the supported game.

## Exit and cleanup

Supervisor error is null, observation complete and normal game exit true.
Renderer and output receiver exit0; receiver retires after4,911frames. No
controller is left running, no owned helper remains at review, copied proxy is
restored and accepted client/launcher settings are unchanged.

The historical supervisor result remains PARTIAL because the controller exits8:
the game exited before controlled live component removal. Sponsor's second
self-destruction explains that timing. This is not a rendering failure or leaked
helper. Game process exit releases its hooks/resources; this run does not prove
the separate controlled live-unload sequence, and the original report is retained.
No cleanup or classifier code was changed during analysis.

## Disposition

**FCA live break-model replacement demonstrated**, including a second parent
and shared fragment content. The previous receiver/worker admission defects
are resolved for this checkout. Existing broader geometry/pose evidence remains
valid; another discovery run is unnecessary.

BRK remains opt-in in current launchers; no default was silently changed.
This is the first successful supported breakup checkout, not universal break
file/LOD coverage or an alpha-release declaration. Record this against the
required destruction feature and return to alpha delivery preparation: runtime
dependency inventory, portable installation paths, staged package and clean-machine
setup/recovery/removal. No commit or push was requested.

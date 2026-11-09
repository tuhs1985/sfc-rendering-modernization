# Private-alpha folder/payload cleanup

Sponsor requested inspection and removal of unnecessary product folders. No SFC
or owned renderer/controller/helper was running. Package hashes and copied game
profile were checked before cleanup; game/settings checks pass afterward.

## Removed from the product

- Empty `data/archives`, `data/offline-runs`, `data/direct64-runs`. Bootstrap no
  longer creates them. Normal operational folders remain; troubleshooting is
  created only by an opted-in report.
- Four completed/restored historical private checkout runs, about 270.52 MiB.
  Kept compact run records and the one captured FCA input used by the current
  installed initialization regression **outside** the product, in ignored
  development qualification storage. Other obsolete generated copies deleted.
- Python root `include`, `libs`, `Scripts`: 251 development headers/import
  libraries/build-tool files, about 2.11 MiB. Kept NumPy/Pillow runtime packages,
  DLLs, standard library and license material. Did not broadly trim optional
  standard-library modules or guess about shader/AI dependency libraries.
- Unselected Remix `d3d9_a64ec.dll`, about 270.44 MiB. Normal alpha selects the
  separately pinned `d3d9_x64.dll`. Note: this hybrid alternative advertises AMD64
  in its PE header; filename alone is not a sufficient PE architecture test.
  Its exact original vendor distribution copy remains available outside the
  product. Other Remix dependencies and vendor notices preserved.

Approximately **543 MiB removed from the checkout**. Product data now has only
three small files: baseline configuration, environment cache and one opted-in
summary. Remaining data directories are `baseline`, `cache`, `runs`, `tmp`,
`troubleshooting`; `runs` and `tmp` are empty. Immutable manifest now has 3,895
files. Actual package folder sizes: Python 104.96 MiB; runtime 879.95 MiB.

## Preventing recurrence

Build-only `package_layout.py` applies exact root-level Python exclusions and
excludes the unselected Remix alternative when staging. ZIP recipe validation
also rejects those paths, including vendor entries. Upstream dependency caches
are unchanged. Existing logical development-path mappings can remain in the
shared context without creating unused directories in installed play.

## Evidence and validation

Cleanup records:
`artifacts/alpha/layout-cleanup/20261109-052110/cleanup.json` (immutable removals),
with first-pass run records under sibling `20261109-051943/run-records`.
Regression input relocated to
`artifacts/alpha/qualification-inputs/private-fca-20261108` and the local installed
smoke adjusted to use that location. These are not ZIP inputs or Git assets.

Cleanup paused at an overly narrow hybrid-PE assertion after deleting reviewed
build folders/runs. Resumed only after verifying every other immutable hash and
the untouched vendor alternative. Manifest reconciled and verified; no game was
launched in between.

- 746 desktop Python tests PASS, including root-only staging exclusions, retained
  runtime libraries/licenses, minimal bootstrap directories and ZIP rejection.
- Installed native preflight PASS; actual trimmed Python captured-FCA initial
  context, image/hash helpers and live light binding PASS. No SFC launched.
- Real installed host/runtime/receiver loaded and rendered a bounded 1024×768
  standalone fixture successfully; all three transferred planes equal their
  producer copies. Original untouched distribution control also exits zero with
  identical physical-depth and owner planes. Thus no cleanup-induced difference
  on those planes.
- The diagnostic's independent coverage oracle is **partial in both**:
  IoU=0.965399 (threshold >0.99), identical counts 8924/8855. Do not call the entire
  fixture an oracle PASS or treat this as a new cleanup regression. No renderer
  edits or repeated discovery campaign were introduced to change that result.
- `git diff --check` PASS. Gameplay after payload pruning remains unverified.

Settings, game assets, saves, recovery baseline, default-off report policy and
appearance unchanged. Changes remain unstaged/uncommitted; no public release.

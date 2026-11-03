# Run273 — standard Windows material-file replacement

## Change

Requested production fix for the Run271/272 material-file publication denial. Existing generated USD material files now use Microsoft's [ReplaceFileW](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-replacefilew), flags0. Initial creation still uses ordinary rename. The shared helper is used for the master material library and progressive per-asset stage updates.

Pending data is completely written before replacement. Original captured geometry/UVs/images, material text, image conversion, rendering, appearance configuration, generation timing, progressive ordering and distinct-whole-second master revision timestamps are preserved. Publication receipts now identify the exchange method. No rendering-thread IO, new renderer callbacks, wait, polling loop or worker was added. The API function is cached on first supervisor use. No added dependency or Defender change.

Existing destination/temporary symlink rejection remains; read-only destination is explicitly rejected. Extended absolute Windows/UNC paths avoid a new MAX_PATH limit. No ACL/merge-error-ignore flags are enabled.

## Failure handling and scope

For documented partial failures1176/1177, if the public name has disappeared but the completed pending file is present, restore that completed file to the missing name. Never overwrite an existing target or delete unknown old files. Report the original failure even after recovery; do not claim successful runtime consumption. Missing pending data or failed restoration reports a specific terminal error. Fault injection qualifies these branches; actual partial filesystem failures were not induced.

Real locks that deny deletion still fail, preserving the old destination and pending data. Releasing such a lock allows the next normal publication. The existing retry/five-second terminal policy is unchanged: the user requested the standard replacement fix, not a broader retry-policy change. A persistent denial from another cause can therefore still stop a run; nonfatal/coalesced enhancement retries remain a separate proposed improvement.

## Validation

-77 focused Python regressions pass, including8 new Windows publication cases: initial/repeated writes, actual shared reader and mapping, exact pinned OpenUSD reader, true non-delete-sharing lock/retry, access denial, partial failure recovery, read-only behavior and long paths. Original reader sees old bytes; a new open sees new bytes; logical timestamp is retained.
- Existing reproducible candidate-host build refreshed for the new source snapshot; renderer source/behavior unchanged. No native component rebuild is required for this supervisor-only fix.
- Delayed Strict `20261102-224357-772610-return-fixture` and immediate ExtraFrame `20261102-224533-628596-return-fixture` each pass600frames, three owners/two assets including shared geometry, pixel/depth/text checks, graphics-state restoration and clean teardown. The Strict run records two master updates and ExtraFrame one coalesced master update; all explicitly report `exchange=ReplaceFileW`, with zero publication retries and no asset partial results. Owned children remaining0.
- Existing cohort qualification refreshed using those two passing runs; normal read-only gameplay preflight PASS. The rebuilt host is byte-identical to Run270: SHA256 `EC6CB79A36838EF8254F726202AD1B0B9DA24365F16969083602F06C24CD37A4`. Original client hash is unchanged. Compact machine receipt: `artifacts/player-replacement/run273/summary.json`; regression output and fixture console records are retained beside it.

Normal SFC gameplay/stress checkout remains sponsor work. No staging or commit; prior unrelated edits preserved.

Use the existing command:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\native_insertion\start_native_multiship_session.ps1" -CompletionDiagnostics
```

# BRK parallel-worker admission correction

**Follow-up:** the next live run found the intact-only shared-memory receiver
still upstream of this corrected worker. [Receiver fix and connected-path tests](2026-11-08-codex-break-receiver-fix.md)
supersede worker-only verification as the current retry checkpoint. This fix
remains required, but did not alone unblock live input admission.

November 8, 2026. Fixes the [confirmed active-path mismatch](2026-11-08-codex-live-break-failure-review.md).
No game launched; no source assets, runtime pins, appearance, native hooks,
suppression policy or synchronization behavior changed. Work remains unstaged
and uncommitted, with prior changes preserved.

## Change

`parallel_assets.Pipeline.decode` now uses `break_scene.decode_runtime_mesh`,
with the relay's explicit `break_models` flag, just as the other admission path
already did. Normal intact input keeps its original validation. Indexed input
remains rejected when the flag is absent/false. Metadata, partition range,
owner/parent epochs, source identity and checksum checks remain mandatory.

This corrects which qualified decoder the production progressive worker calls;
it does not relax origin checks, relabel debris as intact or bypass validation.

## Verification

- Six break transport/preparation tests PASS, including two new regressions:
  the actual `Pipeline.decode` accepts enabled debris, rejects disabled/malformed
  debris and wrong-owner rows, and accepts intact input in either mode; mixed
  intact/debris goes through `Pipeline.submit`/`pump`, the real decode, actual
  geometry/base bundle and enhanced material generation. No mocked mesh decoder
  or pre-supplied decoded mesh in these new cases.
- The six-test set also includes actual x86 native/Python current-user mapping
  transfer/acknowledgement and existing damage-policy checks. Desktop-session
  execution PASS; restricted-session native mapping start fails as previously
  documented, not because of this fix.
- Parallel assets 26, break output 4, damage materials 9 and multiscene resources
  6 PASS: **51 targeted Python tests total**.
- Actual seven saved captures from the failed checkout were copied into a new
  isolated replay folder, leaving the originals unchanged. The production
  worker completed six unique assets and one shared intact alias. All four FCA
  pieces reached base-ready and generated every associated enhanced group:

| Capture revision | Piece | Triangles | Enhanced groups completed |
| --- | ---: | ---: | ---: |
| 4 | 1 | 889 | 19 / 19 |
| 5 | 3 | 1,669 | 18 / 18 |
| 6 | 0 | 2,923 | 27 / 27 |
| 7 | 2 | 889 | 19 / 19 |

Total debris geometry remains 6,370 triangles. Both intact FCA instances and
the KFF also prepared correctly, with the second FCA sharing the first result.
Damage mode was enabled for this replay; pieces retain their existing dedicated
policy, with no invented intact damage UVs. Active material profile hash was
`78177e1d40498186b60c7912b46b897ba08d332df4a24ea41f92c042e89202c5`.

Local replay report: `artifacts/break-live/worker-fix-20261108-verified/review.json`.
The recorded approximately 0.967-second preparation span is CPU/offline work
with cached local images and a synthetic finite camera/pose. It does not measure
actual destruction-to-display time, GPU residency, enhanced publication to
Remix or a live subsecond guarantee. The replay matches the progressive
consumer's completed-job release so its four-asset working set admits all seven
captures. An initial local replay used a frame-zero synthetic row and omitted
that release; its fixture failure is not a second production defect.

Pinned 1.6.1 host build/source receipt refreshed. Existing successful Strict and
ExtraFrame 600-frame insertion evidence was revalidated for qualification;
those GPU fixtures were **not rerun** and do not independently exercise this
debris fix. Native/compositor code is unchanged. Read-only ExtraFrame/all-ships/
break preflight PASS, damage ON. Launcher syntax and `git diff --check` PASS.

## Next checkout

The failed session's copied-install recovery was already verified before this
fix. Use the same prepared command:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\native_insertion\start_native_break_session.ps1"
```

F-CA plus a surviving wingman; wait for the enhanced hull, destroy it in view,
watch fragment motion, switch away/back and exit normally at the cue. The
checkout remains ExtraFrame, zero offset and 90 seconds of tactical observation.
Review actual piece admission, indexed insertion, lifecycle and cleanup. Live
debris/suppression remains unaccepted until this result is reviewed; the worker
fix resolves the known blocker but is not a claim that every later stage passes.

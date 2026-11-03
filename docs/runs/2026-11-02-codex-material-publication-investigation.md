# Run271 — material-file replacement investigation

## Scope

Investigation and proposed solutions only. Normal publisher, retry policy, renderer, appearance and Run270 qualification remain unchanged. No SFC launch, new discovery trace, protection changes, staging or commit. Disposable controls and an isolated standalone GPU experiment live under `artifacts/player-replacement/run271/`.

## Confirmed failure and contributing policy

Run269 failed at `material_library.publish_remix_revision`: `mod.usda.pending` replaces the loaded `mod.usda` with `Path.replace`. The actual error is Windows5/access denied, not proven32/sharing violation. The coordinator catches every PermissionError, calls it sharing-busy, and stops after five seconds. That termination policy is independent of the underlying denial; the last accepted materials could remain usable.

CPU-only exact publication previously passed100calls in63.318ms. File attributes were Archive, not ReadOnly. A bounded renderer mapping query and Restart Manager query found no owner; neither establishes absence of regular file handles, races or filter activity. This denial is separate from Run268's directly attributed Defender file-open wait.

## Controlled reader reproduction

- Closed-file replacement succeeds. Holding a Python reader, reader plus mapping, or mapping alone reproduces Windows5; releasing the reader/mapping permits replacement.
- More decisively, call the actual bundled `usd_arch.dll` export `ArchOpenFile(path,"rb")`. Four trials fail ordinary replacement while the FILE remains open and succeed after `fclose`.
- DLL SHA256: `52dab8f4b87ce09d86ed6f048a7071a55c29071aa7a13981f259d789997f51b5`. Export namespace is OpenUSD25.11. No runtime host is needed for this reproduction.
- DELETE-access opens with all share modes succeed before, during and after the bundled reader. Thus the existing comment claiming missing DELETE sharing is unsupported and contradicted by this control. The error alone does not establish Defender, ACL failure or missing share flags.
- Best-supported explanation: the current replacement operation is incompatible with a reader retaining the old file. This mechanism is reproduced with the packaged reader; the exact holder during each historical failure remains unobserved.

## Candidate solutions tested on disposable files

`ReplaceFileW`, flags0, succeeds4/4 with the packaged reader held open. New opens read the new bytes; the existing reader still reads old bytes; the pending name disappears and the distinct modification timestamp survives. Ordinary replacement fails4/4 under the same conditions.

The newer handle-based POSIX rename succeeds by return code4/4, but one trial's immediate filename read still returned old content/timestamp. Do not recommend that alternative without explaining this anomaly. No unsupported flags or permission-bypass options were used.

Microsoft documents [ReplaceFileW](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-replacefilew), including preserved attributes and partial-failure codes1175–1177. Production handling must account for those states, not blindly retry or delete the current stage. OpenUSD's [filesystem asset implementation](https://raw.githubusercontent.com/PixarAnimationStudios/OpenUSD/v25.11/pxr/usd/ar/filesystemAsset.cpp) retains its file until asset destruction; [ArchOpenFile source](https://raw.githubusercontent.com/PixarAnimationStudios/OpenUSD/v25.11/pxr/base/arch/fileSystem.cpp) requests delete sharing, consistent with the direct access probe. Packaged source parity beyond the tested export is not assumed.

## Recommended production change, not implemented

1. Use the supported Windows replacement operation for existing generated material libraries; keep first-file creation separate. Preserve complete pending writes, material bytes, paths and the distinct-whole-second revision timestamp. Handle long paths, read-only/link checks and documented partial failures explicitly. No in-place rewrite of a loaded USD file.
2. Remove the five-second workflow termination for delayed enhancement publication. Retain the last accepted library, coalesce newer pending generations, and retry on the existing supervisor cycle without blocking SFC. Keep resource limits and report persistent publication failure clearly; never claim enhanced materials installed merely because publication succeeded.
3. Record exact operation/error/generation and whether the last accepted file remains available. Correct the missing-delete-sharing comment and catch-all diagnostic label. Do not introduce continuous ownership scanning in normal operation.
4. Qualify immediate/delayed publication, held readers/mappings, missing destination, documented failure states, cancellation and unchanged final pixels. Keep original sources/images and GPU ownership unchanged.

Versioned immutable USD layers are a secondary option only if standard replacement cannot be qualified. They still need a stable notification/reload relationship and bounded retirement; they are not an automatic fix. Avoid truncating loaded files, removing timestamp differentiation, permission exceptions, longer fatal timeouts or blaming Defender without evidence.

## Standalone rendering comparison

Artifact-only `replay_solution.py` preserves the existing publisher's content/mtime logic and substitutes ReplaceFileW only for its exact pending-library exchange. It ran the standard delayed600frame Strict three-owner/two-asset fixture with the normal Run270 host: `20261102-131305-081672-return-fixture`. No normal source edits or SFC launch.

- Both library publications succeeded,10.451ms/12.291ms,zero recorded publication errors. Existing five-second retry policy was not modified.
-600frames,1609owner commits,three independent owners; pixel mismatches0, native depth/text checks pass, graphics-state errors0, gate errorNone and partial0.
- Host/fixture/renderer exit0; remaining owned processes0. Scratch peak105,706,013B, below existing bound.
- Strict timing fixture includes deliberate overruns and representative delays;536measured frame commits/64fallbacks are not a zero-fallback gameplay claim. No new performance policy or qualification receipt.
- This supports the proposed operation, but one real-renderer pass is not fleet-wide reliability or a controlled proof of the historical live holder. Generic fixture pixel checks are not a dedicated proof of every enhanced-material revision being installed; production qualification still needs that readback.

Receipts: `rename-controls.json`, `arch-open-control.json`, `rename-solution-control.json`, `replay-solution.json` and the existing fixture result/job logs. Normal Run270 gameplay qualification remains intact because no watched production source changed.

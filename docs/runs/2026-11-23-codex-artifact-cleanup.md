# Generated artifact cleanup — November 23, 2026

Sponsor authorized cleanup after the 5% checkpoint and explicitly lifted that
stopping limit for this work. Rendering implementation was not resumed.

## Removed

- Superseded first UE proof: Intermediate, DerivedDataCache, Saved/Cooked,
  Saved/StagedBuilds and Saved/Temp; 6,303,328,251 logical bytes.
- Unpinned generated gpu/assets and gpu/staging directories in completed runtime
  runs before November 12; 1,510,800,704.0 logical bytes. Raw source/gate packets,
  original captured texture data, configuration snapshots, logs and results stay.
- Total: 7,814,128,955.0 logical bytes across 7,787 files in 689
  generated directories. Measured C: free-space increase:
  7,780,507,648 bytes (about 7.8 GB decimal).

The old proof's source, content, packaged executable, logs and useful diagnostic
evidence remain. Its deleted build/cook directories can be regenerated. Old run
replay recipes may need regeneration of intentionally removed prepared assets.

## Selection and safeguards

The local ledger is artifacts/workspace-cleanup-20261123: before.json, plan.json,
removed.json, protected-hashes.json and after.json. The plan records every file,
size, reason and directory. Existing qualification/build/package receipts were
scanned; 258 referenced paths were protected. No selected directory contained a
protected reference. Every recursive target was verified as an absolute path
inside this repository's artifacts directory, with linked paths refused.
No SFC or UE process was running. Deletion used native PowerShell literal paths.

Dependencies, current UE builds/final qualification inputs, rollback copies,
public alpha ZIP, current alpha game checkout, raw captures/traces, source code,
user settings and original game assets were preserved. SHA-256 checks confirmed
the published alpha ZIP, both current UE executables, native component receipt
and final native-pool results were unchanged.

## Verification

The normal read-only UE source-session preflight now PASSes. No game or renderer
was started. Counted evidence is 18,045,072,745 bytes, below the existing
20,000,000,000-byte allowance. Its 570,425,344-byte next-run reservation leaves
1,384,501,911 bytes free in that allowance. The allowance and safeguards were not
changed. These are logical evidence totals, distinct from vendor/package/build
files outside that accounting and measured physical disk recovery.

No files were staged, committed or pushed. Continue the existing task 4.2
handoff when engineering resumes.

## Additional sponsor-authorized Remix archive cleanup

The sponsor authorized deletion of Remix data ZIPs not accessed in the previous
two weeks. Pre-review filesystem access timestamps selected 83 files totalling
646,029,857.0 bytes (646 MB). Cutoff: 2026-11-09T21:35:13.153956-05:00.
NTFS reports system-managed access-time updates enabled. None of these archives
was referenced by scanned qualification/build/package receipts. All 32 archives
with more recent recorded access remain; runtime dependency ZIPs and the alpha
release were outside this selection.

Only exact ZIP files in artifacts/remix-runtime/archives were removed, with
absolute parent/path, unchanged size and non-linked-file checks. Review, plan
and per-file deletion/timestamp ledgers are retained in the cleanup folder as
remix-zip-review.json, remix-zip-plan.json and remix-zip-removed.json.

Historical archive/restore records naming these files are now intentionally
non-restorable. Do not diagnose their absence as a new runtime failure.
Current read-only UE launcher preflight still PASSes. Counted evidence is now
approximately 17.40 GB, leaving approximately 2.03 GB after its next-run
reservation. No game, renderer, commit or push was started.

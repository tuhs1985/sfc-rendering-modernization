# Run254 — Texture payloads now arrive through memory

## Result

The Run253 critical generated-texture-file read is removed from the current progressive D3D9/Remix path, for both the first asset and later assets. Initial renderer setup measured 2.28–4.59 ms across five standalone trials, versus the previous sponsor run's 3.010 seconds and diagnostic reproduction's 6.053 seconds. This is the setup interval, not total loading time.

Three trials completed full rendering checks. Two delayed-start trials failed later at the existing five-second GPU-completion limit. Another completed delayed trial included a 6.721-second preparation interval for a later asset. These failures are preserved; consistent fast startup is **not** established and no new SFC gameplay checkout was run.

## Implementation

- `texture_memory.py` uses the existing current-user-only mapping implementation. The small `Channel.name_pattern` extension permits a separate texture namespace without changing existing scene-channel names or ACLs.
- The preparation coordinator reserves an exact-sized mapping before base assembly. The worker writes the very same final packets to memory and existing evidence files, then seals the memory packet before catalog publication.
- Initial host setup and later asset preparation both consume memory into the existing owned texture vectors. Active memory mode has no texture-file fallback. The older nonprogressive disk diagnostic remains explicit and separate.
- Catalog content, source session, owner/revision/model/source, image counts, dimensions, byte bounds and aggregate texture identity remain checked. Completion-order path IDs are handled explicitly; they are not treated as persistent object identities.
- Maps remain owned until native catalog acknowledgement, redundant alias release or drained shutdown. Pressure postpones preparation outside SFC callbacks. The map budget is 256 MiB plus four 2176-byte headers; one asset retains its existing 128 MiB payload bound. Actual observed peak was 20.9–39.3 MiB, not a fixed allocation per ship.
- Startup-ticket ordering, early passive receiver, M1 disk `LiveChannel` bootstrap, geometry capture, GPU uploads/fences, fallback, original assets and appearance are unchanged. The captured UVs and original images remain untouched.

See [the protocol and lifetime contract](../reconnaissance/texture-memory-contract.md).

## Validation

- 67 focused Python tests passed across texture memory, parallel assets, async material publication, preparation, startup tickets, source timing and native cohort handling.
- 19 real cross-process native consumer cases passed. No texture files were created in that test. Cases include exact bytes, publication ordering, path reassignment, wrong session/owner/revision/model/source/content/geometry/hash, count/bounds corruption, image corruption, oversize dimensions, missing mappings and shutdown.
- Final normal host SHA256: `48eea81bb1a731e8296ac5f78a5fd251b787ba0e5c4fc0ea9a1a75a3cacdd726`. Rebuilding after removing temporary phase instrumentation reproduced the exact binary used by both successful normal-policy fixtures.
- Strict immediate `20261101-144613-634026-return-fixture` and ExtraFrame delayed `20261101-145144-867260-return-fixture` passed 600 measurement frames, independent returned pixels, native depth/text, graphics-state checks, three owners, two unique assets and one content reuse, with normal renderer/fixture exit. Native preparation reported no asset rejection or partial resource result. Memory was released on teardown.
- Native cohort and light-worker preparation receipts were refreshed. Read-only gameplay launcher preflight passed; no SFC process was started. Defender service, antivirus, real-time and behaviour protections were all enabled.
- Image, quality, material and light accepted configuration hashes and `rtx.conf` match the Run253 sponsor baseline exactly. No appearance changes explain the timing differences.

## Trials and limits of the result

| Trial | Outcome | Initial setup | Other observations |
|---|---|---:|---|
| 144613 Strict, immediate | Pass | 4.594 ms | First native insertion 3.816 s from discovery; this fixture starts cold renderer preparation at discovery. Texture handoff does not remove that cold preparation. |
| 144741 ExtraFrame, 60 s passive | Failed later | 2.471 ms | Bootstrap output completed; first cohort GPU query exceeded the unchanged 5 s guard. |
| 145144 ExtraFrame, 60 s passive | Pass | 2.283 ms | First native insertion 579 ms from discovery. Another asset's preparation took 6.721 s. That interval was not yet split by operation; do not call it a proved geometry-file or memory-copy stall. |
| 145638 Strict, temporary phase diagnostics | Pass | 2.775 ms | Larger asset: scene read 8.338 ms, load 1.592 ms, memory textures 31.044 ms. Smaller asset: 0.169 / 0.114 / 1.754 ms respectively. |
| 145907 ExtraFrame, 60 s passive, phase diagnostics | Failed later | 2.325 ms | Larger asset: scene read 6.489 ms, load 1.455 ms, memory textures 25.852 ms. Smaller: 0.178 / 0.127 / 1.863 ms. Asset admission passed; first cohort GPU completion still exceeded 5 s. |

The two GPU failures occurred after the first output was acknowledged and after initial memory delivery. Neither is a malformed/missing memory-packet rejection. Their exact cause remains unproven. In the profiled failure, preparing both assets was fast; that does **not** explain the earlier unsplit 6.721-second preparation interval. Runtime replacement-texture messages occur near the waits, but this does not establish Defender, shader compilation, texture streaming or GPU execution as the cause.

No deadline was extended, no wait bypassed, no check removed to force a pass, and no renderer/material architecture switch was made. Failed trials are not included as successful rendering qualifications. The preparation receipt proves the completed normal-policy fixtures; it is not a claim of reliable low-latency startup.

## Evidence and repository discipline

`artifacts/player-replacement/run254/summary.json` retains timing, failures, per-owner results, configuration comparisons and host identity. `texture-memory-native.json` contains native IPC cases. Temporary diagnostic source, executable and build receipt are archived under the same run254 folder; those extra timings are removed from normal source.

Closed converted texture packets were losslessly archived with per-file SHA256 checks, archive verification and restoration receipts. No original captures, geometry, logs or source assets were discarded. Counted evidence was about 19.13 GB after analysis, within the existing 20 GB allowance and with the normal launcher reservation available.

Changes are unstaged and uncommitted. Existing unrelated working-tree changes are preserved. No security exclusions, external publication, game installation changes or runtime upgrade were performed.

## Next exact action

The memory handoff is implemented. Startup performance remains **partial**. Before another sponsor loading test, identify why the first cohort's GPU-completion query sometimes remains pending after a minute of passive startup. Use the retained failed logs and a narrowly bounded external renderer observation if needed; distinguish runtime worker/file waits, resource upload and shader/GPU work. Keep the five-second resource guard, original fallback and Defender enabled. Do not repeat the old process-creation or `texture-0.bin` discovery trace, and do not assume the unsplit 6.721-second interval has the same cause.

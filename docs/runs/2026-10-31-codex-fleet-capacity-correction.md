# Run237 — ninth-asset fix and large-fleet transport preparation

Sponsor clarified that fleets, fighters, pseudo-fighters and other objects can exceed100 simultaneous instances. Corrected the active path end to end rather than only changing the exception that ended Run236. No game launched by agent; sponsor stress checkout is next.

## Implemented

- The calibration transfer receiver now follows the shared asset budget instead of rejecting revision9. Transfers retain structural/identity validation and acknowledgement. Multi-ship recovery does not use its legacy decoded-asset cache, so that mode now discards the duplicate decoded copy after validation while retaining revision hashes. Historical single-owner recovery retains its needed cache.
- Shared byte-budget definitions in `scene_capacity.h` and `scene_capacity.py` replace separate active-path32/64 literals. State uses128KiB at512bytes/slot: **256 concurrent owner slots**. Catalog uses128KiB at128bytes/slot: **1,024 session asset revisions**. Capture ownership, simulation registry, native suppression decisions, scene publication, Python discovery, both preparation queues, renderer membership and receipt parsing use these values. Identical rendered content still shares geometry/textures with independent instances.
- The mapping stays16MiB; four2MiB transfer slots and four preparation workers remain concurrency bounds, not total object counts. Larger pending queues hold small descriptors, not hundreds of decoded meshes. A high-water mark avoids scanning all preallocated empty state slots during normal multi-ship discovery/recovery.
- Removed the separate64-generation scheduling-anchor rebind cutoff. Generations retain their signed atomic-protocol bound and sequential/session checks. Per-packet image/geometry bounds,256MiB renderer residency budget, GPU synchronization and20GB evidence allowance remain.
- Source owner/capture exhaustion and renderer asset rejection leave unsupported objects native and retain the supported scene. Full publication storage counts omissions instead of throwing. This is **not unbounded/dynamically growing scene storage**:256 active slots and1,024 revisions are this build's finite, preallocated transport capacities. Paging or configurable larger session budgets remain work if stress exceeds them. The game itself is not capped by these tables.

## Layout and compatibility

Scene channel protocol4; tracked-set/catalog protocol2; native membership protocol2. State table begins at8MiB+64KiB; native membership at8MiB+256KiB; tracked scene/catalog at9MiB and ends before the existing10MiB owner channel. Static assertions and cross-architecture tests check layout bounds. The diagnostic calibration snapshot remains32owners; omitting larger indices does not count as failed functional publication. Old components must not be mixed with this layout.

Updated/rebuilt capture DLL, return add-on, standalone source fixture,64-bit Remix host,32-bit GPU transfer worker and observer endpoints. Initial qualification exposed a remaining literal protocol1 startup check and an old transfer-worker binary; both corrected/rebuilt. A separate attempt failed inside NVIDIA allocation before scene rendering despite reported free VRAM; a subsequent cleared-process run succeeded without appearance changes. Failed attempts remain preserved:

- `20261031-210844-848096-return-fixture`: old startup protocol check.
- `20261031-211159-030766-return-fixture`: NVIDIA allocation failure.
- `20261031-211412-620399-return-fixture`: old GPU transfer worker rejected protocol4 mapping.

## Validation

- Actual shared-memory transfer: ninth asset decoded and acknowledged; owner160 read correctly. Receiver tests also accept revisions1–160 and the final1,024th slot, reject out-of-range input and preserve acknowledgement semantics. Mocked revision sweep is not a1,024-asset rendering benchmark.
- Native tracked-set tests:160 independent owners in one coherent publication;96checks eachx86/x64. Native membership/suppression receipts:160 owners sharing content;193checks each architecture. Actual GPU rendering at that count remains unmeasured.
-102 targeted Python tests pass, including large preparation descriptor queues, shared assets, receiver bounds, rebinds and light handling. Existing gate core1,216checks each,flush12,300,capture59,corner,observer and persistent publication checks pass. Real persistent worker:120pose publications,one diagnostic miss,zero functional failures.
- Final actual Remix/native insertion fixtures: Strict `20261031-211618-741588-return-fixture`, ExtraFrame `20261031-211730-464903-return-fixture`. Each600measured frames,three owners with shared geometry,two exact colour/depth/effects/text comparisons,zero mismatches/state errors,normal exits. These prove integration after the ABI change,not100-ship GPU performance.
- Current native multi-ship and observer qualification refreshed;non-executing Strict launcher preflight passes. Accepted/copied client and lighting/rendering hashes unchanged. No refresh cap,appearance or timing-policy changes.

## Evidence and next action

Verified lossless archives of closed-run generated images/converted texture packets restored stress-test headroom under the unchanged20GB allowance. The bulk archive covered94 older successful runs,1,513MiB raw converted textures,reclaiming1,400MiB. Original captures,geometry,logs,settings and failure records remain; archived bytes are SHA-256 verified and recoverable through each run's archive receipt. Approximately1,851MiB headroom remained after final fixtures. Local scripts/receipts and Python report: `artifacts/player-replacement/run237/`.

Use the unchanged native multi-ship launcher for sponsor stress testing. Observe the largest practical fleet/fighter population;no claim yet of universal geometry/cloak support,100-object gameplay performance or unlimited capacity. Review admitted owners,asset aliases,preparation latency,deadline misses,resource-budget rejections and cleanup afterward. Changes remain unstaged/uncommitted.

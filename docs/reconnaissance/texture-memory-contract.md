# Session-owned asset delivery — protocol 2

Run254 removed generated texture-file reads. Run256 extends the same handoff to the finalized neutral geometry packet, removing active bootstrap and later-asset geometry-file rereads. It does not change canonical captures, original images, Remix's image-origin correction, enhanced material generation, GPU uploads or output ownership. Protocol 1 is historical and is rejected by the current consumer.

## Producer and ordering

The supervisor already holds decoded images. Its preparation coordinator reserves an exact-sized mapping before queuing base assembly. `scene_bundle.prepare` copies each final BGRA packet into that mapping at the same point it writes the existing evidence packet. No second decode or file read produces the memory payload.

Each mapping contains one asset's immutable geometry and textures. The coordinator computes the exact scene size from the already prepared vertices, indices, nonempty groups and single initial frame. Assembly writes the same final scene bytes to memory and existing evidence before sealing the packet. Only then can the coordinator publish the existing asset catalog and startup ticket. The host opens the mapping after activation; there is no new dependency before M1 reads `LiveChannel` or attaches to the scene channel.

This runs outside the SFC process and its rendering callbacks. There are no new SFC callbacks, waits, refresh limits or per-frame image copies.

## Identity and layout

- Mapping name: `Local\SFCTextures_` followed by four eight-digit lowercase hexadecimal words. These are the explicit source-session words, with word zero XOR `0x54585431` and word three XOR the immutable catalog asset ID. The separate prefix prevents collisions with scene channels.
- Creation reuses the existing `Channel` current-user-only DACL and noninherited handles. Existing named objects are rejected. The renderer opens read-only.
- Bytes 0–31: existing channel header, magic `0x31424c53`, version 2, exact mapping size, reserved zero, and derived name words.
- Bytes 32–119: existing 88-byte catalog asset packet, including checksum. It binds owner epoch/revision, model/source, content identity, geometry bytes/hash and texture bytes/hash.
- Bytes 120–123: image count, 1–256. Bytes 124–127: ready flag, published last.
- Bytes 128–2175: capacity for 256 texture offset/length pairs.
- Geometry starts at byte 2176, with exactly the catalog's geometry byte count (at most 2 MiB). Its existing aggregate replay hash must match. This is the unchanged neutral scene format, including its schema, groups and initial frame.
- Texture payloads follow geometry contiguously, with no overlap, gaps or trailing bytes. Their offsets must start at `2176 + geometry_bytes`.
- Payloads retain the existing 16-byte `SFT1` header and exact BGRA8 pixels. Dimensions are 1–4096, length exactly width × height × 4 plus header. The existing aggregate FNV texture identity must match the catalog.

Preparation assigns filesystem path IDs by completion order after assembly. The memory proof therefore requires every catalog identity field except `path_id` and its dependent checksum to match the final catalog. Both packets must independently pass their existing checksums. Native pointers and resource IDs are not mapping identities.

## Initial and later consumers

The initial host attaches to the existing session catalog, validates its game/session identity and finds the bootstrap entry with `path_id == 1`. It receives and validates geometry and textures together, parses geometry through the unchanged neutral parser's new byte-input entry point, and checks scene/material coverage. It never opens `scene.bin` in active memory mode. Its texture vectors supply the existing `Renderer(preparedTextures)` input. The source scene hash used by output provenance is computed from those same received bytes.

Later asynchronous asset preparation uses the same memory consumer and byte parser. Reusable content still shares the existing resident mesh/renderer. The consumer checks a captured seal, exact identity, geometry hash, image bounds and aggregate texture hash before returning owned vectors. The final seal is compared again after copying. The parser retains all original count/index/finite-value checks; no geometry repairs or coordinate changes were introduced. `Renderer` retains initial-data upload backing exactly as before. Disk-only path/symlink checks are not performed for unused payload paths in memory mode.

`SFC_D3D9_TEXTURE_MEMORY=1` is explicitly set by the current progressive relay. A missing or invalid mapping in that mode is an explicit failure; it never quietly opens texture files. The older nonprogressive diagnostic path explicitly sets zero and retains its historical file transport. API work remains parked.

## Bounds, pressure and lifetime

Each asset is limited to the existing 128 MiB texture-payload budget plus 2 MiB geometry and 2176 bytes of header. Total unacknowledged mapping reservation remains bounded to 256 MiB plus four headers, including geometry. Memory is reserved to actual packet size, not that ceiling for each object. Existing image-output, resident-GPU, decoded-work and evidence limits remain independent and unchanged.

If the next reservation does not fit, the preparation coordinator postpones queuing that base job. No worker sleeps waiting for capacity and SFC continues drawing normally. The earliest prepared base can be published without waiting for enhanced materials or all other assets.

The supervisor holds each mapping until the native catalog acknowledges success or rejection. At success the native consumer already owns its CPU upload vectors and GPU resources; closing the producer's mapping cannot invalidate them. Aliases discard their redundant packet after preparation resolves canonical content. Failed unpublished jobs are released after their tasks drain. A published base survives a later enhancement failure until acknowledgement or shutdown.

Normal stop first shuts down the existing owned renderer/source workflow and drains preparation workers, then closes any remaining texture mappings. Stop before activation, producer/receiver failure and native fallback retain their existing handling. No GPU texture, fence or shared-output handle changes ownership in this increment.

## Verification

`tests/test_texture_memory.py` covers exact copied pixels, immutable publication, incomplete packets, capacity pressure, acknowledgement release and session isolation. `qualify_texture_memory.py` exercises the actual native consumer with no texture files: valid packets, completion-order path assignment, wrong owner/revision/model/source/content/hash/session/count, overlapping offsets, corrupt pixels, oversize dimensions and missing/retired mappings. Actual GPU fixtures separately qualify initial and later assets, shared instances, colour/depth/text and teardown.

The Run253 texture-file and Run255 geometry-file stalls are removed structurally from this consumer path. This does not guarantee all remaining Remix material reads, shader work or process startup will always be fast. Timing and failures are recorded separately in the run record.

## Optional slow-completion recorder

`-CompletionDiagnostics` on the existing native multi-ship launcher (or `--completion-diagnostics` in the Python fixture/game runner) explicitly enables the external host's recorder. Normal launches explicitly disable it, including when a stale environment value is inherited.

The existing five-second completion guard is unchanged. When enabled, the recorder measures time inside query calls, asset-service callbacks and polling pauses. Only waits taking at least 100 ms, or waits unwinding with an exception, are retained. A fixed array holds at most 64 records; further events increment a dropped counter. Source frame, wait identifier and QPC times support correlation with external worker observations. Records flush to the existing bounded host log at exit, including on caught failure before runtime shutdown. There are no additional file opens, image captures, game callbacks or automatic thread samplers.

Default-off means no extra per-poll QPC sampling or output; an inexpensive disabled branch remains. These timings identify where the host waited, not whether an unsignalled query represents GPU execution, queued CPU work or a particular driver/filter. A runtime-worker observation may still be needed to attribute an internal wait.

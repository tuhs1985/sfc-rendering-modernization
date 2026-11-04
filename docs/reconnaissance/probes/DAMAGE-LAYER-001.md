# DAMAGE-LAYER-001 — native damage selection and secondary mapping

Prepared November 3, 2026, Run283. Implementation and sponsor command:
[damage observer](../../../tools/damage_probe/README.md).
Static prerequisites: [Run282 damage path](../damage-texture-path.md).

Question: which per-owner scalar/family, selected material pair and generated
secondary coordinates does the accepted SFC client actually submit when hull
damage develops? Also establish the first-use lazy-list ordering. Damage black
transparency is already established by the sponsor, not an open hypothesis.

Use only the copied client with accepted SHA256
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
Default off; no Remix display, suppression, game asset writes or configuration
changes. No graphics hook, secondary renderer, texture dumps or broad survey.

Reuses nine qualified early-model entry hooks, adding the already-characterized
polygon wrapper at `0x006AC5A0` in a separate compile-time observer profile.
Wrapper ABI: thiscall, three 32-bit arguments, `ret 0x0C`; accepts only manager
vtable `0x007B8D4C`, selected-model context, native list/count agreement, mode1,
and callers `0x0042E55D`/`0x0042E626`. Original called once, unchanged.
Guarded copying captures the stack-backed material before returning.

Output envelope retains early observer magic/version/header; event kinds
100–104 identify model-state changes, polygon-pass state, mapping receipts,
first lazy mapping creation, and resource-table snapshots. Records are 512 bytes.
Owner and visual epochs are carried independently; native addresses are local
provenance only. Invocation token/QPC is not a fabricated native frame number.

Secondary mapping file: 32 little-endian words, magic `0x444D5031`, version1,
byte length, FNV-1a checksum (checksum field zero during calculation), provenance
and counts. Then position triples, seven-word polygon records, seven-word corner
records. Polygon word6 is a portable corner ordinal. No UV, normal or orientation
conversion. Limits and per-field definitions are executable in
`tools/damage_probe/damage_hooks.inl` and `damage_capture.py`.

The callback reads resource IDs from the eighteen qualified slots beginning
`0x008F57F8`. Offline decoding joins them to the pinned executable's original
filename acquisitions and Run282 hash inventory. A contemporaneous table or
prior same-owner/asset-epoch table is required; future unrelated tables cannot
rescue missing identity. No native pointer is dereferenced by the worker.

State records include four **opaque** native manager words from `+0x1EC8`.
They are not labelled D3D blend factors or asserted to establish all downstream
alpha/filtering state. This run qualifies association/mapping; remaining blend
arithmetic must be traced from existing pinned code or reported unqualified.

16 MiB metadata, four immutable mapping slots below2MiB each, fixed ring2048;
48 MiB total run ceiling, existing112MiB evidence reservation and20GB aggregate
admission. Capacity/busy/read failures are explicit partial evidence and do not
change original drawing. No cap is added to the functional renderer.

90-second automatic tactical window,120seconds to enter tactical play,
285-second supervision. Console/two beeps request normal exit. Stop detaches
ten hooks and drains callbacks before final file receipt. Accepted/copied client
and launcher settings are checked; the session host is owned and stopped.

Accept observation only when source/owner epochs, secondary pass, selected pair,
portable mapping/checksum and cleanup agree. No observed hull damage is partial,
not evidence that the game lacks the path. Damage display and first-use insertion
readiness remain subsequent implementation work.

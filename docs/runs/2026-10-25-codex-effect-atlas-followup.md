# Run170 — continued offline processing of the three effects runs

Scope: existing Run169 captures and narrowly adjacent static rendering code.
No gameplay, runtime probe change, new renderer, asset conversion or API work.
The [Run169 capture/cleanup results](2026-10-25-codex-three-effect-surveys.md)
remain authoritative for the three actual executions.

## Additional supported findings

**CONFIRMED:** captured owner epoch5 consistently supplied variant3 and branch
word0x101. Static draw0x004EFA4A has two independently enabled primitive paths:
object+3D invokes vtable+3C (0x004EFEC1); object+3C enables the main quad.
Both were enabled in the recorded entry snapshots. This does not prove every
branch emitted a nonempty primitive on every call.

The main quad indexes `0x009339F8 + 16*variant`. Initializer0x004EED96
and normalization helper0x005050E2 establish these intended records, expressed
as pixel-grid coordinates before division by256:

| Variant | u0 | v0 | u1 | v1 |
| --- | --- | --- | --- | --- |
| 0 | 128 | 255 | 191 | 192 |
| 1 | 192 | 255 | 255 | 192 |
| 2 | 128 | 191 | 191 | 128 |
| 3, captured | 192 | 191 | 255 | 128 |
| 4 | 192 | 127 | 255 | 64 |

For variant3, normalized bounds are U0.75–0.99609375 and V0.5–0.74609375.
Manager UV setter0x006AD320 stores arguments directly at+1EF4/+1EF8; no
vertical inversion there. These are pinned static initializer values, not a
runtime readback of the table or individual submitted UVs.

**CONFIRMED:** the other branch walks a64-entry circular position history
(mask0x3F), calls segment helper0x004F0044 and binds the same fx0 resource.
It uses a DIFFERENT table, `0x00933A48 + 16*variant`, initialized at0x004EEF2E.
Its five intended records before division by256 are:

| Variant | u0 | v0 | u1 | v1 |
| --- | --- | --- | --- | --- |
| 0 | 0 | 255 | 21 | 128 |
| 1 | 22 | 255 | 43 | 128 |
| 2 | 44 | 255 | 65 | 128 |
| 3, captured | 66 | 255 | 87 | 128 |
| 4 | 88 | 255 | 109 | 128 |

Helper interpolates V along segments and uses U edges and midpoint; it is not
the main quad's burst rectangle. Zero-length segments can be rejected.
**STRONG HYPOTHESIS:** this is a ribbon/trail visual path. History-based
segment construction is confirmed; exact weapon identity remains unproved.
Constructor0x004EF0BD maps an input style to+44; it is not established as an
animation counter. Input5 maps to variant3, not to a proved weapon name.

## Atlas provenance and orientation limitation

Read the original copied-install `Assets/Textures/fx0.bmp` directly, unchanged:
256x256, SHA256
`d12dd3b782d99772914b81fea810927339e8b62420b323c727b2505b4b84e915`.
Client SHA256 remains
`4d65761d7dd69ef1504070261b81e9c200c0af18105033e1c4d2222c62320c29`.
No proprietary image or executable was copied into versionable documentation.

Decoded image has vertical beam strips on its upper left, coloured burst cells
on its right and small particle artwork below. Main variant3 selects the
rightmost burst column, while segmented variant3 selects U66–87. Native upload/
sampling vertical orientation has NOT been established here. Main variant3
would correspond roughly to the orange/red cell with direct top-origin V, or
the magenta cell with vertically inverted V. The segmented table's V range
similarly changes which decoded image rows are sampled. Coherent upper-left
beam artwork under inversion is supporting visual evidence, not a loader proof.
Do not borrow the Remix-only texture-origin fix as proof of native orientation.

**Important limitation:** current records do not contain branch-level UV
observations. They join122,820 native quads to the concrete owner/resource,
but cannot partition them between the two paths or assign every quad to one
atlas cell. This refines, rather than invalidates, Run169's owner/resource join.

## Sponsor atlas observations — not engine classifications

Sponsor identifies phaser artwork in fx0 and notes that sheets contain multiple
effects. Other visual identifications: fx1 possibly an explosion in one corner;
fx2 animated quarter-circle; fx3 explosions; fx4 possibly Organian energy sphere
used in certain missions; fx5 space dust; fx6 possibly fusion effects. Preserve
these as sponsor observations/candidates, not independently verified runtime
effect names. The captured filename association is only established for fx0.

## What the other two runs cannot tell us retrospectively

Their complete90-second captures contain global-list births/retirements and
unscoped finalizer counts, but no selected concrete draw scopes. They did not
record the other concrete vtables/dispatch targets: those identities cannot be
recovered by relabeling counters. Nor do finalizer counts establish nonempty
draws. No synchronized light parameters/on-off transitions were captured in
these three runs. Older light findings remain separate evidence; they cannot
be joined to these effects by assumed timing or slot meaning.

## Validation and next action

Read-only PE section mapping recovered constants from the pinned client;
bounded existing disassembly supplied initializer/setter/segment anchors.
Initial constant-read attempt incorrectly treated the inspector's hexadecimal
image-base string as an integer; corrected conversion, rerun succeeded.
Original fx0 decoded successfully with Pillow; dimensions/hash checked.
No callback/hook/source/qualification/binary/config changes. Documentation
links and whitespace checked. Existing captures and Run169 results unchanged.
HEADfd79ce5; index empty; prior dirty work preserved; all changes unstaged and
uncommitted, no push. No owned runtime session survives. Existing20GB cap
unchanged; no bulk output or deletion. Repo status tracker updated; no claim
that an external Obsidian copy has been refreshed in this checkpoint.

**Exact next action:** implement/offline-qualify the already recommended bounded
quad counters/samples and concrete dispatch census, retaining selected UV/branch
evidence where practical. Resolve native image vertical sampling before naming
the exact burst cell. Synchronized light metadata is a future observation need,
not implemented by this analysis. No unchanged repeat gameplay run is needed.

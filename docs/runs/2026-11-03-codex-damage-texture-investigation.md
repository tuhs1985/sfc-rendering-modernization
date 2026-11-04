# Run282 — damage-texture investigation

Sponsor requests investigation using existing captures and notes that damage
is layered over the hull and pure black is transparent.

[Findings and next observation](../reconnaissance/damage-texture-path.md),
[versionable metadata](../reconnaissance/evidence/20261103-damage-texture-path.json).

Confirmed static: eighteen original damage images in three severity/family
groups with companions; separate lazily generated polygon/UV layer selected
by model-render arguments; secondary submission through the already observed
wrapper. Current fresh-mesh transport captures only the primary list. This
explains a concrete missing interface relationship, not an implemented fix.

Historical CSV review: 100 files examined; 50 contain 26,365 model samples,
all with zero recorded third argument and no secondary-wrapper rows. Bounded
sampling limits this conclusion. Run172 downstream summaries do not supply
an explicit damage-producer join or excluded geometry/images. No new gameplay
discovery run was requested.

Validated 1,729 relevant instructions against the pinned accepted executable;
all eighteen original images hashed and headers checked without modification.
The BMPs have no saved alpha channel. Sponsor-observed black transparency is
preserved as the intended behaviour; the precise native key/test/blend and
companion contribution remain unresolved. No alpha equation guessed.

Initial preparation ordering matters: the existing primary insertion boundary
precedes lazy damage-list construction. New work must qualify source-frame
damage state and first-use mapping availability; seeing a later secondary call
does not update an already inserted frame.

Only documentation, metadata and ignored offline analysis were added. No hooks,
renderer, settings, originals, game launch, build, staging or commits. Existing
light baseline and launcher remain unchanged. Exact next action: prepare the
bounded model-arguments/secondary-material-and-UV observation described in the
findings, then validate one damaged ship before implementing replacement damage.

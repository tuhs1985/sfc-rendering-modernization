# RT-004 — complete temporal samples; chase-camera qualification

**M1 CONTINUES — additional bounded evidence required.** Both selected owner
chains supplied18 snapshots through85s. Local corner payloads stayed fixed while
transform state changed. Not formal TRL4 PASS or full normal-space qualification.

## Exact evidence

Run artifacts/m1/runs/20261012-003542-enabled, PID11960, component0.7/corners.v3;
started2026-10-12T00:35:42.9384580-04:00, normal exit00:37:39.6622994-04:00.
[Definition](../probes/M1-C01-RT-004.md):90s automatic gate,36 attempts/two ship-
visual interest filters/5s windows/64 polygons x8 corners/3MiB packet. Geometry,
tint,shadingoff; semantic120 epochs/10k detailed events/eight owners/16–32MiB.

| Owner | Ship | Visual | Model0 | Source | Mesh counts |
| --- | --- | --- | --- | --- | --- |
|1|1CE7A0E0|1CE72138|0A6BC518|0494365C|254 vertices/452 polygons|
|2|0A778128|0A7708B0|0A6BC20C|1B897598|3,493 vertices/6,370 polygons|

All36 status0/64 polygons/192 corners each; analyzer issues empty. Both filters
have no missing/failed/unobserved windows, thread/visual rejection counters0,
outside-filter0, transition drops0. Literal IDs1/2 persist; only two initial
selection transitions, no retirement/reappearance. Fresh-ID handling not exercised
at runtime; prior RT-003 gap cause remains STRONG HYPOTHESIS.

Owner1 supplied object basis has one unique pattern; full supplied transform
changes in other fields. Owner2 has11 unique basis patterns, angular changes
fromwindow7 (~35s). Owner2 composed transform changes fromwindow4 (~20s).
Both raw corner-vector/indexed-position prefixes remain bitwise fixed through85s.
Owner1 vector lengths0.6761772605..1.0000000132, owner2 approximatelyunit;
source-group/vector association not one-to-one. Preserve raw magnitudes.

Sponsor confirms ship moved/turned after third cue, rendering/HUD/controls normal,
noissues. **Chase camera**, limited up/down angles, not independent orbit.
Cannot separate all camera contributions from target-following motion or identify
player/enemy owner solely by assumption. Fixed corners under supplied angular
changes corroborate static transform/light mapping: model-local inputs remain
STRONG HYPOTHESIS, not full handedness/inverse-normal/scale qualification.
Composed projection basis need not be orthonormal; large Gram error alone isn't
corruption. Commanded phase labels alone never prove actions.

## Safety and unresolved rejection count

5,390 gated epochs/17,502 Model0 calls. Known00509843 count5,394 finite/unassigned.
Hooks restored by component/controller; duration stop/removed/normal exit;
no intervention/lease, owner/thread overflow or failure log. No current game/
controller observed; temporary game proxy/config absent. Installed client SHA256
unchanged4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29,
MD52BE8F713F81B1C68D50EAD6088C32886; independently reread after completion.

**2,658 aggregate rejected_semantics remains unresolved**, not sampler rejection.
Follow-up [source investigation](M1-C01-RT-004-rejection-investigation.md) establishes
the aggregate includes pre-gate activity; 'late' below describes missing coverage,
not confirmed rejection timing. Failed ship/visual validations never enter CSV.
Source increments at failed ship/visual validation or nonmainline Model0 other
than00509843. CSV first120 epochs:237 Model0 returns0042FDD5,119 known00509843,
no third recorded caller. Late rejected kind/reason not recorded. Do not call
it confirmed harmless exception or selected-owner failure. Sampled chains are
coherent; whole-run semantic cleanliness isn't established. Sponsor saw no impact.
Geometryoff means no fresh downstream proof; startup succeeded but old Win32
failure cause remains unknown.

## Bounds and preservation

CSV340,851/packet642,256/analysis32,357 bytes; all15 raw files1,042,422 bytes.
No warning/hard cap exceeded. Detail saturated at120 epochs/1,189 events; summary
continued. Verified archive artifacts/m1/archives/M1-C01-RT-004-20261012-003542.zip
128,112 bytes, SHA2569340C17FC1DF74DD25CD09776A9E04968D943BDC237FFD78C5D3171E1C2AF77C;
all15 entry hashes match raw. Small raw retained/ignored, none deleted.
Runtime hashes (runner rebuild differs from preparation):
DLL EDACAB8756A4F1173AE1951140CEDC4D87FC25127790DDB84E46D52B8ED0611B;
controller9E3E649BF28A38FAB54F3849F5FCC6FCB5CE063283835C0257B78901EC7CA352.

Next smallest action: review three existing rejection branches, define bounded
kind/reason counters if retained evidence cannot attribute2,658. No blind repeat,
geometry hook, enhancement or broader RE. Preserve chase-camera limitation.

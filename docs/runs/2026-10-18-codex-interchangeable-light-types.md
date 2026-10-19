# Run46 — interchangeable Remix light types

Date2026-10-18 America/New_York; HEAD2fa8032. Run40–45 work remains unstaged/
untracked, index empty. Sponsor clarified: type selector for ANY light used by
our component, not merely a separately added dome. Current qualified sources are
the two native directional IDs; other native weapon sources remain unqualified.

Question: can either source be intentionally rendered through any pinned SDK
primitive/environment type with live settings, without changing SFC state?
Read handoff, approved M1 plan/current disposition, live light relay/validator,
wire/SDK consumer, pinned SDK declarations and existing fixture. SDK exposes
distant,dome,sphere,rectangle,disk,cylinder; spot is shaped sphere. Header confirms
types, not a guarantee until actual SDK execution. No broader engine RE.

Implemented type selector and dormant parameters on each existing TOML entry.
Both stay directional; sponsor conversion_scale=.07/master=1/angles1 preserved.
New light_shapes.py validates seven types, prepares optional bounded8bit image/
uniform white DDS, produces hashes/provenance and fixed552B companion. Existing
200B source/session/owner/age packet retained with explicit companion-required
flag. Revision/checksum/type/filename/unit axes/finite values checked in host;
missing/mixed companion skips extra copy, never changes native rendering. Config
invalidity retains last accepted settings. One enabled dome supported per scene.

Remix-only createShapedLight maps all types, with current model/diagnostic offset
used only for explicitly ship-relative local positions. No guessing native point
fields, no native writes, no hidden geometry hook. Shape changes retire/create
SDK handles after previous GPU fence. No new SFC callback IO/allocation/waits.
Existing process/output limits and tuning end-on-normal-exit convention retained.
No light/shadow/milestone parity claims; existing SDK warning40 remains open.

Files: light_shapes.py,remix_light_shapes.h (new); light_controls.py,live_lights.py,
remix_light_wire.h,remix_live_lights.h,ship_live_host.cpp,live_return.py,
qualify_live_return.py,config/lights.toml,configREADME; native wire tests and new
test_light_shapes.py; this record, probe and HANDOFF. No reference originals edited.

Tools/commands: VS2026Community18.7.3 C++20/W4/WX/Brepro x86/x64;
build_live_return.ps1; bundled Python3.12.14 unittest discovery;
qualify_live_return.py --execute --light-types and full regression matrix;
read-only run_return_game.py --light-tuning; parser/diff/hash/archive checks.
Scoped elevated builds only for generated artifact permissions; no security changes.

Preliminary SDK type test20261019-010914-165069-live-private PASS: second light
actually created as types1,2,3,4,5,6,0 in order, with continuing output and clean
host/fixture exits. This was synthetic native-light input plus recorded geometry,
not actual SFC gameplay. Superseded as final qualification after provenance and
one-enabled-dome backend validation edits; source manifests not rewritten.

Python247PASS; native89request/14UV/25wire checks eacharchitecture PASS.
Unit tests cover all types on both IDs, invalid shape data/multiple domes,
missing image, generated DDS/cache/checksum, companion revision/path/axis and
orthogonal rolled area-light basis. Final GPU/preflight/pins recorded below.

## Final validation / evidence

CONFIRMED ten final source-matched standalone GPU gates PASS; exact folders in
artifacts/remix-runtime/deps/live-return-qualification.json. First011302-737640,
last011520-864170 (20261019 UTC / live-private). Final type cycle20.954s:
host0/fixture0,123drawn/failed0,maskIoU.99886925795053,all seven type receipts in
order. Qualification now requires light_types_qualified alongside wiring flag.
This confirms SDK submission/type switching under standalone rendering, not
sponsor-verified appearance of each shape in actual SFC.

Read-only --light-tuning preflight PASS; no game/renderer started. Native observer
source receipt still valid, unchanged. Parser/unit/diff checks PASS. Both clients
remain SHA2564D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
Host D43A7624DDE402CE53D23D9C5700D868971DE7F796D9EE6D253C90AC5A5E1239;
qualification B60833196FB3440958948C9F8E0C3A001CED995F9D2250E027C82B471E09ED2D.
Archive artifacts/remix-runtime/archives/20261018-interchangeable-light-types-qualified.zip,
43,656,600B, SHA256631E18A5BB0F98C43EED822988F94BA419A45C0963A0E70004064E19E4FD88D4,
CRCverified; raw retained, no deletions. Total retained5,911,062,695B below10GB.
No active game/host is needed to resume; no staging or commit.

No sponsor gameplay during development. No stage/commit; original artifacts and
earlier evidence preserved. Exact next action after qualification: sponsor starts
tuning launcher, changes desired existing entry's type (e.g.light1 to dome), saves,
and exits normally when done. Read resulting receipts/visual report before claiming
appearance correctness. Future effect-light mapping/GI/full scene replacement deferred.

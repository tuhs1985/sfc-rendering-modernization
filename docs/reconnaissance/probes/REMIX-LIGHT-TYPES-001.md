# REMIX-LIGHT-TYPES-001 — per-source light-type overrides

## Current amendment — Run48

Optional project_fill is a THIRD project-origin light, not a captured source;
starts disabled/dome/.05 radiance scaling. Its own intensity/color bypass native
strength/conversion/master. Any supported type selectable; one enabled dome total.
New shape contractv2 is808B (three256Brows/header32/checksum8). Third enabled flag
in fourth row word; floats15..17direct radiance,18..20direction,21angular size,
22volume,23..27zero. Native rows preserve prior field meaning/zero padding. Native
identity200B packet unchanged. Incomplete/wrong-version/mixed revision fails closed.
Manifest/PROJECT_LIGHT_APPLIED receipts identify project origin. Capture bounds,
source2limit/3SDK light handles,image128MiB/evidence32MiB limits unchanged.
--project-fill standalone test proves separate dome on/off/on and native-master
independence; final11gates required. Same tuning launcher; no new gameplay steps.

The v1/552B two-row description below is historical design context, superseded
by this version2 amendment. Do not mix a v1 host with the current relay.

Purpose: any qualified light entry can choose any supported primitive/environment
type, including replacing the second native directional with a dome. Not a separate
added-only dome, not native SFC light reconstruction or a new renderer architecture.

Tools: pinned Remix1.5.2/SDK0.6.4, x64 host, existing Python relay and dedicated x86
observer. Existing build_live_return.ps1 builds native tests/host; qualification
requires a real SDK type-switch fixture, not just header enumeration.

Normal use: established elevated parent and start_light_tuning_session.ps1.
Enter usual two-ship skirmish; edit/save config/lights.toml. Exit normally whenever
done. No routine UAC, timestamping, geometry hook, original-ship suppression or
source game edits. Existing30minute tactical/33minute total ceiling remains.

Relay retains200B identity/age/current-source packet, companion flag in values10.
Optional fixed552B light-shapes.bin contains revision, two256B rows, FNV64.
Row: slot/type/ship-position-flag/reserved,28floats,128B relative DDS filename.
Types0..6:directional,dome,sphere,rectangle,disk,cylinder,shaped-sphere spot.
Floats:radius,width,height,length,coneAngle,coneSoftness,focus,roll,position3,
axis3,environmentYrotation,13reserved zeros. Header SHAP/version1/552/2,
revision64/reserved64. Companion revision must match200B source packet. A flagged
packet without valid complete/checksummed matching companion is never interpreted
as an ordinary directional fallback. Legacy unflagged diagnostic packet retained.
Files are atomic replacements, not append streams. Native pointers/type enums
and backend-independent captured data are unchanged.

Host uses separate shape handles, destroys/recreates only after previous output
fence completes. Ship-relative local positions use the current captured model plus
diagnostic offset, never an invented native positional light field. Directions
remain world-space. One enabled dome maximum in this adapter. Image filenames are
strict content-addressed DDS leaves; worker owns decoding/conversion/provenance.
Uniform white dome is explicitly generated lighting, not a recovered ship asset.

Bounds: same fixed2light sources,64KiB config,32MiB combined evidence with16MiB
warning,128MiB combined image output with64MiB warning,256DDS resources,4096image
dimension/32MiB environment source. First16config copies/last-good overwrite;
latest-only bank and100scene rows per owner in tuning mode. No continuous images
or geometry firehose. No raising storage/time limits.

Offline: qualify_live_return.py --execute --light-types starts OWNED synthetic
fixture only, never SFC. Cycles second source dome→sphere→rectangle→disk→cylinder
→spot→directional with API receipts in that order and verifies native presentation,
texture/geometry footprint, lifetime/fallback and normal fixture/host exits. Ten
full source-matched GPU cases establish ordinary baseline and new type controls.
Native tests check companion revision/checksum/type/path/axis and basis geometry.
Python checks all types on either ID, invalid configurations, dome DDS/cache and
missing-image rejection. True SFC appearance per type remains sponsor validation.

Evidence: artifacts/remix-runtime/runs/*-live-private or *-in-game; config copies,
light-shapes-manifest.json, SDK receipts and result/manifest. Expected additional
data is552B plus one tiny uniform DDS; user environment DDS output bounded above.
Cleanup: normal game exit; existing runner stops renderer, verifies hashes/settings.
No manual DLL placement/deletion. Do not kill a live-hook controller. Keep partial
results; SDK warning40 and process-exit-vs-live-unload distinction remain recorded.

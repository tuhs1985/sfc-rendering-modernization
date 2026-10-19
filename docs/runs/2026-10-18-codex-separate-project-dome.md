# Run48 — separate project dome, alongside snapshot-reader fix

Date2026-10-18 America/New_York; HEAD2fa8032. Existing Run40–47 unstaged/untracked,
index empty. Sponsor adds "give me seperate dome light to play with" while Run47
snapshot-sharing fix is being qualified. Keep that fix, add one independent light,
do not replace either captured source or overwrite tuning values.

## Implementation / scope

New optional [[lights]] id=project_fill,origin=project,type=dome,enabled=false,
intensity_multiplier=.05,color white,environment_image empty. No captured SFC
strength/conversion/master applied to this third light. Existing native entries
and sponsor values retained; user enables/adjusts separately. Like any component
light it can select all seven supported types, not a permanently dome-only slot.
No inferred native GI, weapon-light mapping or original-ship suppression.

Native200B freshness/identity packet remains unchanged. Version2 shape companion
is808B:32Bheader,three256Brows,8BFNV64. Same SHAP magic,version2,size808,count3,
config revision/reserved64. First two rows unchanged in meaning. Third row slot2,
kind0..6,ship-position flag,enabled flag (formerly reserved word); values15..17
direct RGB radiance,18..20unit direction,21angular diameter,22volumetric scale,
23..27zero. Other shape fields0..14 same asv1. Native rows15..27 remainzero.
Complete checksum/revision/type/path/axis/range validation before use. Older v1
companions fail closed; source-matched host/relay required. One enabled dome across
all three entries. Fixed3SDK handles,2native sources,existing output/image bounds.

Added independent third SDK handle/state, same completed-fence recreation rule.
PROJECT_LIGHT_APPLIED slot2 receipts distinguish added from native light evidence.
Manifest records origin, intensity/color and explicit strength basis. Disable/default
off leaves previous picture unchanged. Native observer/callbacks/client untouched.
Run47 Windows sharing-delete reader and nonfatal busy/recovery counters retained.

Files changed: live_lights.py,light_shapes.py,remix_light_shapes.h,
remix_live_lights.h,live_return.py,qualify_live_return.py,config/lights.toml,
configREADME; native wire tests/test_light_shapes.py; this record/probe/HANDOFF.
Existing Run47 source/test changes remain unstaged. No helper, global security/
ACL changes, unrelated cleanup or game launch. Same elevated-parent tuning runner.

## Validation

VS2026Community18.7.3/C++20/W4/WX/Brepro x86/x64,Python3.12.14; pinned
Remix1.5.2/SDK0.6.4. build_live_return.ps1; unittest discovery252PASS3.499s,
native89request/14UV/25wire checks eacharch PASS. Tests cover the independent
row/radiance,all types on project entry,one-dome bound,companion count/size808,
plus Run47 actual Windows lock/failure/recovery/handle-close tests.

Preliminary standalone --project-fill run20261019-013822-983921-live-private PASS.
PROJECT slot2 on/off/on with radiance .05 while native master changes .5→.25;
normal host/fixture exits,continuing textured output. Synthetic native input and
recorded mesh,NOT actual SFC gameplay. Final eleven source-matched regression
gates/preflight/archive/pins recorded below. No milestone completion claim.

Ten Run47 sharing-fix-only GPU cases had passed before this added task; those
source receipts are superseded by combined Run48 qualification, not rewritten.
All prior raw/partial evidence retained. No staging/commit/deletion.

## Final combined qualification

Eleven final source-matched standalone GPU gates PASS (013941-191960 through
014254-777930,20261019 UTC/live-private). Last independent-dome case27.719s,
host0/fixture0,maskIoU.99886925795053,project_fill_verified=true. Project light
on/off/on preserves .05radiance while native master changes; all7type and baseline/
slow/disconnect/camera/texture/snapshot gates also pass. New project_fill_qualified
flag required alongside existing light_wiring/light_types flags.

Read-only --light-tuning preflight PASS;no game/renderer launched.252Python and
native89/14/25perarch PASS;diff/parser/config checks PASS. Existing native observer
receipt valid. Both clients retain SHA256
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
Qualification SHA256C00AAC343043316E55D0C26428DF27C8AB13DA4ADD3DC8D42E9BF237AB137A03.
Archive artifacts/remix-runtime/archives/20261018-project-dome-reader-fix-qualified.zip,
57,155,127B,SHA25613967C19D4AECD14869A55395A2B65D187E329261446ACB49D64596796E03B7F,
CRCverified. Includes final11gates/receipt and original012229failed tuning evidence.
Raw retained,no deletions;total6,755,133,420B below10GB. No stage/commit.
READY FOR SPONSOR TUNING;actual gameplay verification of third light and automatic
busy-reader recovery remains pending. No active game/host required to resume.

## Next exact action

After final qualification, sponsor uses same start_light_tuning_session.ps1,
sets project_fill enabled=true and adjusts its own intensity while playing, then
exits normally. Review read_busy/read_recoveries,PROJECT receipts and exit/hash
checks. Captured sources retain their current types/weights unless sponsor edits
them. Actual gameplay validation of new dome/recovery remains pending.

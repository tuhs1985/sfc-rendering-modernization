# Run50 — preserve sponsor's tentative light/material baseline

Date2026-10-18 America/New_York;checkpoint22:56:25.9072402-04:00.
HEAD2fa8032fe8af00f9dee668a9ff0c1f10ef12d974;existing Run40–49 work dirty,
15tracked modified/48untracked entries before this record,index empty. No stage
or commit authorized/performed. Active work is bounded Remix return-path appearance
tuning,not a new rendering implementation or gate-completion task.

Question:which exact saved settings does the sponsor select as the current
tentative comparison baseline,and what new visible behaviour did they report?

Read current HANDOFF,Run49 final checkpoint,active config/lights.toml and
materials.toml. FuelGuard attached current thread via recent verified hook;
direct daemon access denied by sandbox,no daemon spawned. Tools:read-only
PowerShell/.NET byte reads+SHA256/Git status,apply_patch for durable snapshots/docs,
Python TOML/current schema validators. No external packages/helper/subagents.

## Saved baseline

Full files plus manifest and human summary in
docs/reconnaissance/evidence/baselines/20261018-tentative-light-material/.
Material:roughness0.9,illumination_strength0.35,metallic0.15,anisotropy0.5.
Light conversion0.15/master1;native directional0and1 enabled,multiplier1each,
angular diameters17and15degrees. Project dome enabled,intensity0.005,uniform white.
All other active and dormant settings preserved in full,not reconstructed from
chat. Source materials SHA256
5AF94EE33CA8B2A658802D4B23D4BFBCE8A7D5D7AB93ED6DCD56BF14996BAD31;
source lights SHA256
FC55CE88326AC4D544D166D42882540C257B2E54671517F9F6CD2F93B3F70E2F.

CONFIRMED:these saved settings match the selected snapshot at record time.
TENTATIVE sponsor-selected appearance,not a general SFC→Remix calibration.
Active settings were NOT edited;future edits must not overwrite this history.

Sponsor reports illumination “acts as a light source”. Record as CONFIRMED
sponsor visual observation of returned-scene emissive lighting,consistent with
the existing mapped emissive material. Not independently quantified or a new native
SFC-light discovery. No claim that returned-scene light illuminates retained
original game geometry. No extra explicit light added by this task.

## Files and validation

Created baseline README.md,manifest.json,lights.toml,materials.toml;this run record.
Updated canonical HANDOFF,newest checkpoint;older Run49 entry marked historical,
not deleted. No implementation,active config,client or source-asset changes.

Validation:parse both snapshots/active files;compare complete TOML values and
source-byte SHA256;run existing strict light schema/scales and material packet
encoder;check links and git diff --check. Results appended below.
No gameplay/probe/capture started:runtime probe IDs/limits N/A for this docs-only
run. Existing REMIX-MATERIAL-CONTROLS-001 and light-tuning limits remain unchanged.
No stop/cleanup/restart of any sponsor-owned runtime session;its state is not
assumed from chat. Original client was not written or rehashed in this task;
Run49's explicit unchanged-client verification remains the historical reference.

Unresolved:appearance equivalence/physical units/emission contribution not measured;
known SDK40and prior runner-exit classification issues not investigated here.
No requirements changes,gate advance,automatic retuning,stage or commit.
Next exact action:use this saved baseline unchanged for the next approved
comparison;await sponsor's next test instruction rather than start new work.

Final validation PASS:both complete snapshot TOML documents equal active settings;
both active SHA256 match recorded source hashes;strict light schema/scales and
56Bmaterial encoder accept the configuration;all snapshot paths exist;
git diff --check clean except informational CRLF notices. No full runtime/build
regression needed for docs-only snapshots. Final HEAD unchanged,index empty,
15tracked modified/50untracked entries (collapsed directory counts),including all
preexisting work. No stage/commit,active config changes or runtime commands.

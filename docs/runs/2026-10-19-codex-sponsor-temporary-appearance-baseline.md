# Run60 — record sponsor's new temporary appearance baseline

Date2026-10-19 America/New_York. Task: sponsor says current settings are the new
temporary baseline after improved roughness-map appearance. No new rendering
implementation or milestone claim. Starting HEAD357bc703e3dc0923cd4c7801ec87e99abc01f157,
codex/github-sanitized;existing Run57/58/59 and user tuning unstaged/uncommitted.
Fuel Guard attached existing hook;no daemon/helper. Read authoritative HANDOFF,
current four appearance configs and prior baseline README. No SFC/host active at
process check. No game/probe/build launched or runtime state changed by this run.

Created exact copies via PowerShell Copy-Item (no overwrite) of lights.toml,
materials.toml,image.toml,quality.toml in
docs/reconnaissance/evidence/baselines/20261019-sponsor-temporary-appearance/.
Added its README with hashes,key settings,scope and restoration instructions;
updated HANDOFF/config README pointers. No active config edits. Earlier snapshots
preserved and historical checkpoints explicitly superseded,not deleted.

CONFIRMED:exact snapshot SHA256 equality with all four active files;existing
Python encoder/TOML/schema/range checks PASS for materials/image/quality and
light_controls.validate/scales PASS for lights. First diagnostic command completed
all validation but its optional summary print incorrectly indexed the normalized
light record's absent `type` field (KeyError);corrected read-only print to inspect
the original TOML rows and reran successfully. No project defect/change needed.
No full test/build rerun:documentation and byte-preserving snapshot only;Run59
275tests/native/14return-gate results remain historical supporting implementation
evidence,not falsely claimed as newly executed. Final git diff --check and paths
checked. No source/assets/executable modified;no new runtime capture bounds needed.

Sponsor observation:returned ship looks better;new temporary appearance accepted.
Not proven:physical calibration,native visual parity,universal ship/material
coverage or the exact cause of prior washout. Generated roughness is still an
artistic approximation;SDK40shutdown warning and missing independent opaque
specular control unchanged. No CDD/requirements/defaults/TRL gate change.

Final Git HEAD unchanged;all work remains UNSTAGED/UNCOMMITTED,nothing pushed.
No screenshot copied (avoid accidental desktop/chat publication). No transient
tool state needed to restore this baseline. Exact next action:use the saved
four-file snapshot as the comparison/restoration point for any future authorized
tuning;do not automatically reset to older factory/tentative settings.

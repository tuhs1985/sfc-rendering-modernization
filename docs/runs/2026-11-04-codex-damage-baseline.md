# Run291 — damage joins native replacement baseline

Sponsor asks to integrate accepted damage rendering into the baseline,following
Run290 live confirmation. No shader/material/renderer/native source behavior
changed;only launch defaults and their verification/documentation changed.

- Native multi-ship PowerShell launcher now explicitly enables damage normally.
- `-NoDamageTextures` selects the previous damage-off behavior. Existing explicit
 `-DamageTextures` remains compatible;mutually conflicting flags are rejected.
- PowerShell5→7forwarding preserves the new disable option.
- Direct production Python defaults damage ON only with `--native-all-ships`;
 `--no-damage-textures` overrides;legacy/non-native workflows stay OFF by default.
- Read-only preflight reports resolved ON/OFF,without launching game/renderer.
- Standalone fixture damage remains explicit;its synthetic transitions and bounded
 readbacks are test tools,not baseline behavior. Completion/light diagnostics
 remain opt-in. Damage counters/check classification remains in DIAGNOSTICS.md.
- Lighting/material/image settings,canonical assets and game installations unchanged.

Validation:five tests execute the production parser setup without importing or
running game/process operations:default native ON,explicit OFF,legacy explicit
ON,unrelated workflow OFF,and conflicting flags rejected.678Python tests PASS.
PowerShell launcher parse and normal/disabled read-only preflights checked;
existing offline native-light qualification and current both-policy cohort
qualification refreshed. Candidate host binary not rebuilt:renderer code did not
change;its source-set receipt refreshed for launch/test-only edits. Existing
accepted live/GPU damage rendering proofs reused;no repeat gameplay requested
for a default-only change.

Scope remains tested standard-family damage. Other families/live repair and
break-model/destruction still need their own qualification. No alpha completion
claim. No commit or push requested for this new increment.

Final checks:normal direct CLI preflight PASS/Damage textures ON;explicit disabled preflight PASS/OFF;PowerShell launcher parse PASS;git diff --check PASS. No game or renderer started.

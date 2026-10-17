# Texture eligibility capture — sponsor-ready preflight

- Run ID/date: 2026-10-16-texture-eligibility-preflight / 2026-10-16.
- Task: existing offline texture-recovery proof; resolve fallback eligibility,
  not a new rendering feature or milestone/gate advancement.
- Starting baseline: HEAD fee152f137a55a3efeb47a5c236ebf9e3e1951cb,
  179 inherited modified/untracked status entries; index empty. Preserve all work.
- Authority/context reviewed: newest docs/HANDOFF.md checkpoint,
  2026-10-16-codex-texture-path-runtime-review.md, TEXTURE-EXPORT-001 definition,
  texture and mesh export entry scripts. Prior runtime0.16 does not contain the
  new fallback validation mask/previous alpha-test fields. Prepared0.17 does.
- Implementation: no additional source correction necessary; use already-built,
  offline-validated0.17 through existing runner. No new hook or diagnostic geometry
  capture; no client/assets/configuration edits or active game/controller process.
- Verified prepared component SHA256:
  A62303B34A0BD5673DAC2A75E2B344F1D0205DD73E71C5D7E486FA826EB5F401.
  Prior full native build/tests and 89 project/36 preview tests passed, as recorded
  in the runtime-review record. This preflight checked script routing and hash;
  no claim those full suites were rerun. git diff --check PASS (CRLF notices only).
- Reproduce from existing elevated PowerShell parent (no security-policy change):

  ```powershell
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\m1_component\start_texture_export_session.ps1"
  ```

- Runner rebuilds/tests, uses bundled PowerShell7, automatic tactical gate. Sponsor
  enters usual two-ship skirmish, both ships initially visible, plays normally,
  exits normally after two beeps/console request. No camera phases/timestamps or
  visual change expected. This preflight itself does not launch the game.
- Probe TEXTURE-EXPORT-001: one same-epoch snapshot,90s runtime,120 detailed frames/
  10000 events/eight owners,16MiB warning/32MiB log stop; ten resources,4096 squared
  dimensions,64MiB image warning/128MiB image stop. Default-off association capture
  explicitly enabled by entry point. Expected references <8KiB; no per-frame image
  dumping or multi-GB mechanism. Existing runner cleanup/hash checks retained.
- Evidence expected: new artifacts/m1/runs/<timestamp>-enabled packet/reference
  JSON, run result, bounded logs and textured derivative. Do not reuse prior live
  IDs/pointers. Analyze new mask/alpha-test values with analyze_texture_path.py;
  branch prediction is not proof of completed GPU passes or physical fidelity.
- Result: CONFIRMED prepared-binary/script consistency; runtime eligibility remains
  unresolved pending sponsor gameplay. No runtime evidence generated this turn.
- Files changed: this record and docs/HANDOFF.md only. Fuel Guard exact-thread hook
  receipt verified; direct sandbox daemon access denied/quota unknown, no daemon
  started. No helper/server/session used.
- Final repository state: HEAD unchanged; inherited work retained plus this record;
  index empty, nothing staged or committed. Next exact action: sponsor runs command
  above, then Codex reviews fresh same-epoch eligibility/cleanup/client hashes.

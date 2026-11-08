# Run293 — Untimed controller startup environment

Date:2026-11-04.

Sponsor reports failure almost immediately after starting the untimed launcher.
Authoritative evidence:`artifacts/remix-runtime/runs/20261104-060301-556261-in-game`.

## Cause and correction

`gate-controller.log` contains Usage only;controller exits2before tactical gate.
The runner supplied duration0but launched the controller without the explicit
session environment. That environment already contained `SFC_PLAY_SESSION=1`
for SFC/capture,while the controller inherited the Python supervisor's ordinary
environment. Its zero-duration guard correctly rejected the arguments.

Add `env=env` to the actual controller Popen call. No renderer/material/native
binary changes or validation bypass. Run292's preflight, helper tests and GPU
fixtures did not exercise this production controller process boundary;the prior
claim of readiness missed this wiring defect.

## Verification and recovery

- New test extracts and executes the actual production Popen expression with
  the built controller against guaranteed-invalid PID4294967294. Play+duration0
  reaches OpenProcess and fails3as expected;ordinary+0fails2/Usage;
  ordinary+120reaches OpenProcess. No target/game process or injection launched.
- Full Python suite684tests PASS,including4play-session tests. Existing native/
  GPU binaries unchanged;reuse both Run292600-frame GPU regressions. Refresh
  source/light/cohort qualification receipts and untimed/timed preflight.
- Failed run ended while SFC was still open,so rollback was correctly deferred.
  After game closure,the existing exact-run recovery restored copied proxy/config
  and verified every copied critical hash. `recovery.json` records this separately;
  original failed result is preserved. Original installation unchanged.
- Changes unstaged/uncommitted. No new campaign/gameplay success claim. Next:
  retry normal `start_native_multiship_session.ps1`,without diagnostic flags.

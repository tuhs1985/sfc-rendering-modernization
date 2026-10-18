# Codex run — returned Remix image in SFC

Run ID SFC-RETURN-20261017-02; date2026-10-17 EDT. Task: adjudicate
REMIX-RETURN-001 sponsor runtime, not implement ship replacement. Starting
HEAD e96765a, index empty, existing uncommitted return-path implementation/docs
preserved. Authority: approved return-path task, current HANDOFF, M1 plan and
[implementation record](2026-10-17-codex-remix-output-qualification.md).
Fuel Guard attach verified recent hook delivery for actual thread, no daemon
spawned. No helper, new gameplay, implementation edit, staging or commit.

## Question / inputs / reproduction

Does genuine Remix runtime output reach SFC's own displayed frame without
disrupting gameplay? Sponsor executed prepared start_return_image_session.ps1
from established elevated parent, usual two-ship fixture. Applicable
[probe definition](../reconnaissance/probes/REMIX-RETURN-001.md),
[contract](../reconnaissance/remix-return-contract.md),
[pinned dependencies](../reconnaissance/remix-return-dependencies.json).
Exact runtime configuration/build hashes in raw manifest.json; no manual times.

Raw run: artifacts/remix-runtime/runs/20261017-053407-630582-in-game.
Reviewed result.json,manifest.json,host.log,launcher.log,gate-controller.log;
inspected phase history, final counters and current process/hash/Git state.
Material checks: Get-Content/ConvertFrom-Json, per-phase counter comparisons,
Get-FileHash accepted+copied StarFleetOP.exe, Get-Process owned names,
git status --short and git diff --check. No raw JSON modified to insert verdict.

## Evidence / adjudication

- CONFIRMED sponsor report: moving triangle visible, disappeared/reappeared as
  directed, no in-game issues noted. Combined with actual GPU output protocol,
  verified process and presentation counters: **RETURN PATH DEMONSTRATED** for
  this additive256square diagnostic, not a desktop overlay or local rectangle.
- Captured90s tactical; prepared Python workflow123.984s within285s budget.
  Output resources524288B; run folder15files/1006500B, below16MiB warning and
  32MiB hard limit. No continuous screenshots or CPU image transport.
- Final produced=ACK=presented=copyCount656, drawCount2706, staleCount0,error0.
  Sampled enabled phase0draw29->1802/copy7->437; disabled phase1draw1808/copy438
  remain constant; reenabled phase2draw1820->2693/copy441->653; disconnected
  phase3draw2706/copy656 remain constant. Boundary sampling explains endpoints.
- Test-copy childPID4816 verified suspended path/hash before resume; startup
  restored=verified=1; resolution1920x1080, epoch/renderEpoch/presentedEpoch1.
- Automatic gate controllerPID42848 exit0, detail-bound stop,
  component_state=removed, hook_bytes_restored=true, component_unloaded=true.
  No diagnostic geometry hook. GameCHILD_EXIT0, rendererexit0/SDKShutdown0.
  FinalREADY0,sharedHandle0,enabled0,stop1,clearCount1. No remaining owned game,
  renderer,loader/controller found after test. Get-Process returned no matches;
  its nonzero no-match status is not a failed game exit.
- Original critical hashes and launcher registry paths unchanged per runner.
  Both client SHA256 reread:
  4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
  Original Community Edition remains preserved. Test copy may retain ordinary
  generated logs; these are not an on-disk client patch.

## Unresolved cleanup finding / limits

Exact host.log line after HOST_SHUTDOWN api=0:

```text
[01:35:26.717] err:   [40] common device objects were not disposed of.
```

CONFIRMED warning, not confirmed memory leak cause or failed GPU transfer.
SDK/register-device ownership, remaining local graphics references or runtime
teardown ordering are hypotheses only. No speculative Release or lifetime fix
applied. Normal exit/resource-clear counters establish operational shutdown, but
do NOT establish warning-free internal runtime teardown. Public register-device
ownership comment in our host is not independent evidence of SDK ownership.
This needs bounded source/lifetime adjudication before claiming cleanup closed.

Enabled/disabled/disconnected SFC behavior is confirmed. Separate ordinary
removed-state startup has not been sponsor-tested. No owner-specific replacement,
coverage/depth visibility, synchronized ship-frame contract or full-scene return
has been demonstrated. No formal milestone/TRL completion claim.

## Changes / final state / next action

Documentation only this review: this record, authoritative HANDOFF checkpoint,
contract runtime addendum and probe result note. Raw evidence archived separately
after analysis to artifacts/remix-runtime/archives/20261017-053407-return-runtime-evidence.zip
(14885B); original results retained. Existing100Python/native/offline tests
from preceding execution remain relevant; no implementation changed, so fastest
validation is raw consistency, unchanged hashes, no owned processes and diff check.

Final HEAD e96765a; existing implementation/tests/docs remain unstaged/untracked,
index empty; no staging or commit. No session state needs recovery or reuse.
Exact next action: bounded audit of host/SDK registered-device teardown ownership
for the40-common-objects warning, then close cleanup/removed-state verification
before owner-specific suppression. Do not repeat successful image-return test
without a specific new question or start appearance tuning.

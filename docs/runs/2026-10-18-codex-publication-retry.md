# Codex run — recover completed-output publication

Run SFC-RETURN-20261018-25;2026-10-18 America/New_York.
Authority:sponsor "Fix and prepare next test";approved return-path investigation.
**READY FOR SPONSOR PRIVATE RUNTIME RETEST**,not sustained-runtime PASS.

## Baseline / question

HEAD e96765a1a34c15212ed22f11edeb9a708b9fc18d;93 starting porcelain entries,
empty index;prior dirty work preserved. Read HANDOFF,approved M1 plan current
disposition,Run24,Run23 contract/probe and actual host/wire/tests/qualification.
FuelGuard attached exact thread via recent hook;no daemon/helper/subagent.
No SFC launched. No requirements,architecture,semantic ABI or client edits.

Question:can a completed GPU result survive a busy metadata guard without
stranding Rendering ownership or weakening exact-frame admission?

## Implementation and evidence adjudication

- `tools/remix_runtime/ship_triplet_wire.h`:explicit Busy/Invalid/Cancelled/
  Published outcomes;legacy bool publish interface retained. Shared producer
  completion helper clears pending only on Published/Cancelled,not Busy/Invalid.
- `tools/remix_runtime/ship_live_host.cpp`:completed GPU surfaces stay in flight
  on Busy,producer retries outside SFC after1ms. Existing5s request deadline
  bounds publication retries;Invalid is explicit failure. Genuine cancellation
  releases pending ownership. No new draw or surface overwrite during retry.
  Final bounded summary adds publication_busy and cancelled;no per-retry logs.
- `tests/ship_live_request_tests.cpp`:hold guard for eight deterministic
  completion attempts,assert unchanged sequence/Rendering/pending;release guard,
  publish once,require GPU-complete ACK;then test changed-request cancellation,
  stop cancellation and invalid state. Same helper is used by production host.

**CONFIRMED:**busy-guard defect and corrected ownership behavior reproduced by
native tests;62checks eachx86/x64 PASS (previous41). **STRONG HYPOTHESIS:**this
was the exact cause of Run24's stall;that run lacked a contention reason counter.
Four GPU fixtures below had publication_busy=0 where normal shutdown reported;
they validate surrounding transfer,not forced cross-process contention. Do not
claim a real SFC fix has already been demonstrated. Exact frame/pose/camera and
GPU fence rules remain unchanged. Stale output can still be rejected safely.

## Validation / reproduction

Tools:VS2026Community18.7.3,C++20 /W4 /WX,PS7.6.5,bundled Python3.12.14,
pinned Remix1.5.2/SDK0.6.4;Run23 dependency manifest unchanged.

1. PS7 `-NoProfile -File tools/remix_runtime/build_live_return.ps1`.
   Sandbox initially denied generated reshade_registration.lib replacement
   (LNK1114/error5);scoped approved unsandboxed rebuild PASS. No UAC/security
   settings changed;no library deletion workaround.
2. Same native compiler settings built `tests/ship_triplet_tests.cpp` into
   isolated live-return-bin:65checks eachx86/x64 PASS.
3. TEMP/TMP=`artifacts/test-temp`;bundled Python
   `-m unittest discover -s tests -p test_*.py`:195PASS/5.482s.
4. Bundled Python `tools/remix_runtime/qualify_live_return.py --execute`,then
   separate `--execute --addon`, `--execute --slow`, `--execute --disconnect`.
   Owned standalone processes only,never SFC. Existing60s/32MiB fixture caps.

| UTC run suffix (-live-private) | Condition | Seconds | Published / private attempts | Mask IoU | Bytes |
|---|---|---:|---:|---:|---:|
|20261018-134854-031701|direct SDK/native|9.907|88 / 67|1.0|2938584|
|20261018-134924-315238|copied proxy callback|8.765|87 / 65|not read back|6728054|
|20261018-134955-275129|slow receiver|9.203|87 / 65|1.0|2954672|
|20261018-135026-151293|terminated producer|7.468|2 / 2|1.0|2929023|

All fixture exits0/private failures0. Host exits0 except intentionally terminated
disconnect host1. Slow test retains no-overwrite marker;retirement/disabled
admission checks pass. Fixed recorded fixture pose is not moving-pixel proof.
SDK common-device warning40 persists;not waived by host0.

5. `qualify_live_return.py --qualify` followed by the four exact directories
   above renewed ignored `artifacts/remix-runtime/deps/live-return-qualification.json`;
   SHA256 `C3F64E490808D999798A08097074FB22D94BF5E94202B9BC51A139F85820C2C8`.
6. `run_return_game.py --private-ship` without --execute:read-only preflight PASS.
   Repeat isolated rebuild reproduced qualified binaries;second read-only
   preflight PASS (no renderer/game started). Archive90entries CRCverified.
   PS parser,JSON/reference checks,archive CRC and `git diff --check` PASS.
   Both installations' seven critical hashes rechecked unchanged vs Run24;
   clientSHA `4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.

New hostSHA `D2DDFDEA5DFB5AC02D673C3DFCEF54EB5E60DBA682F81E432CFFA4183207CE1F`.
AddonSHA unchanged `D81B457D64424C0FB458373E15D8FD33C7352A58D674D9E43172051FC30959E0`;
fixtureSHA unchanged `29D4B7A906248A1438C8DE35540CC99F38FC4DAE027EEC396928795D2DCC2CE0`.
Normal return-bin and semantic observer untouched. Builds remain ignored.

## Preservation, next test and state

Four full offline evidence folders compressed to
`artifacts/remix-runtime/archives/20261018-publication-retry-offline.zip`:
3919642bytes,SHA256
`82AA6048D5D9E59ACAB9F61B696D18FABD6A8B32DEECA10100754BD52EBD9102`.
CRC verified;raw retained,total15550333bytes,well below10GB ceiling. No screenshots
or repeated geometry dumps;fixed fixture image readbacks only,none in game.

Next use existing -PrivateShip runner,usual two-ship skirmish,90s automatic gate:
initial cue hold still;10s small camera change;20s gentle movement/turn;two-beep
exit. NO visible extra ship/tint expected;original rendering untouched. Inspect
progress beyond10s and again45–60s after OFF;do not interpret any positive draw
counter alone as sustained success. Review contention/cancellation summary,
retirement/rejection history,cleanup/hashes and sponsor behavior. If strict-frame
admission rejects moving output,record partial;never accept stale pose to pass.

Changes this run:three implementation/test files above,this record,curated
evidence,newest HANDOFF/probe/contract/readiness sections. Older checkpoints
preserved. No staging/commit;index empty;prior dirty work intact. No owned
game/host/fixture/controller left running. No transient tool session needed.
No on-screen copy,suppression or new milestone claim authorized by these tests.

**Exact next action:**sponsor runs prepared -PrivateShip command and follows cues;
Codex reviews sustained admissions before attempting on-screen integration.

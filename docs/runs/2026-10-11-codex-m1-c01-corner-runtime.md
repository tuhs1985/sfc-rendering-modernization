# Codex run — corner/transform runtime adjudication

- Run ID/date: `2026-10-11-m1-c01-corner-runtime`, America/New_York.
- Active C-01 read-only qualification, M1 CONTINUES. Sponsor completed prepared
  test, reported no issues, confirmed heard cues/performed actions. No formal M1
  PASS or new implementation/commit authority inferred from that report.
- Starting HEADfee152f;12 tracked modifications/14 untracked prior source/tests/
  documentation/evidence preserved, nothing staged. Sources: latest HANDOFF,
  M1-C01-RT-002, prepared contract/analyzer, actual run files and sponsor reports.
- Fuel Guard recent trusted hook verified/direct denied, no daemon/helper/subagent.
  Tools: PowerShell Get-Content/ConvertFrom-Json, float-bit decoding via BitConverter,
  SHA256/ZIP/process/path inspection, bundled Python3.12.14 analyzer and Git.
- Runtime M1-C01-RT-002: component0.5, existing x86 controller, runtime hashes/
  PID/timestamps in [curated evidence](../m1/evidence/M1-C01-RT-002-20261011-corner-inputs.md).
  Gate600s wait/45s run, two owners/six5s windows/12 attempts,64 polygons/eight
  corners,1MiB packet;120 epochs/10,000 events/eight owners/16–32MiB semantic
  bounds, geometry/tint/shadingoff. No architecture or broad RE changes.
- Commands: read named `20261011-234849-enabled` metadata, summary, packet,
  cue log, controller stdout, run-result; group identity/count/status fields;
  decode16 matrix words with ToSingle(GetBytes(uint32),0), compare basis/translation.
  `python tools/m1_component/analyze_m1_corner_snapshot.py artifacts/m1/runs/20261011-234849-enabled`
  rerun agrees ADDITIONAL_BOUNDED_EVIDENCE_REQUIRED. Automated issues not overridden.
- CONFIRMED evidence: owner1 four successful64-polygon/192-corner records remain
  bitwise fixed under object translation/composed-matrix changes; vectors finite
  but not uniformly unit, groups0/1/2 span vector patterns. Dispatch snapshots0.
  Owner2 allsix statuses2: totalpolygon6,370 exceeds reused4,096 guard before any
  corners. Numeric packet explains the failed probe branch without new RE.
- Rejected interpretations: successful gameplay means qualified normals;
  command issued means actual rotation captured; status2 means malformed model;
  sharing/sample prefix proves all surfaces. Model-local normal meaning remains
  STRONG HYPOTHESIS, rotation relationship unresolved. Missing owner1 lasttwo
  windows/visibility cause unconfirmed. No native/analyzer source edited this run.
- Cleanup/exit/hashes: hooks restored, original control flow, no live leases or
  semantic rejection/overflows; normal exit classifier true, client unchanged;
  independently rehashed installed/reference SHA256 match. No SFC/controller
  observed; game-directory proxy/config absent. No forced termination this run.
- Sponsor separately identified monitor refresh issue before this test; record
  as sponsor-confirmed hardware observation/parked outside component work, not
  independent driver diagnosis. No new skirmish issues reported or display edits.
- Raw handling:15 files444,700 bytes, CSV338,255/packet75,949. Compress-Archive
  exact run to artifacts/m1/archives/M1-C01-RT-002-20261011-234849.zip,24,571 bytes.
  All15 entries streamed through SHA256 and matched originals; archive SHA in
  curated evidence. Raw small/retained, all ignored; no material deletion.
- Files created: curated evidence and this record. Modified: HANDOFF, C-01
  qualification runtime status, probe runtime disposition, risk register. Prior
  pending source/tests/evidence preserved; no build repeated without source change.
- Validation: analyzer, raw/header/bounds/matrix review, archive entry hashes,
  client SHA, exit/hook verification, Markdown links/whitespace/status checks.
- Result M1 CONTINUES — additional bounded evidence required; safe probe worked,
  its count guard/sampling schedule limited qualification. Final HEAD unchanged,
  all changes unstaged/uncommitted; no persistent runtime/session assumed.
- Exact next action: prepare bounded read-only count-guard/snapshot-schedule
  revision, leaving tint safety limits intact; no automatic repeat or enhancement.

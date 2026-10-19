# REMIX-LIGHT-TUNING-001 — interactive lighting ratios and shadow softness

Run47 amendment: worker-side latest snapshot reader shares READ/WRITE/DELETE
with atomic producer replacement,6157B maximum read/6156B exact valid record.
Busy/access/missing snapshots skip once and retry at next100ms poll; bounded
read_busy/read_recoveries/read_pending counters and existing limited messages.
Old observation time remains unchanged; no stale-light TTL extension or waits.
Persistent unreadability hides extra output under500ms rule,not original rendering.
Wrong size/malformed contents/other IO remain errors. No ACL/security changes.

Purpose: adjust qualified two directional lights live on additive textured ship.
Question: which saved ratios/source sizes reproduce the desired SFC appearance?
No original-ship suppression or weapon-light/GI qualification. Run44 records build.

- Tool/version: same pinned Remix1.5.2/SDK0.6.4; dedicated x86 native observer,
  x64 SDK host, Python3.12.14 relay; source/binary qualification receipts required.
- Build: existing start_return_image_session.ps1 builds dedicated observer/host,
  never overwrites accepted m1_component.dll. Offline receipts fail closed if stale.
- Launch: established elevated parent, Windows PowerShell execution-policy bypass
  scoped to process; `tools/remix_runtime/start_light_tuning_session.ps1`.
  No extra routine UAC, task/service/global security change.
- Trigger: verified isolated client startup and automatic semantic tactical gate.
  Enter usual two-ship skirmish. Existing original rendering remains ON.
- Controls: `tools/remix_runtime/config/lights.toml`, save to apply within about
  half a second plus rendering. Master/per-light multipliers affect strength;
  larger angular_diameter_degrees softens shadows. Invalid edits retain last good.
- Stop: normal user game exit;30minute tactical safety ceiling/33minute total
  runner/host ceiling. Timeout performs controlled removal and asks normal exit.
  Normal process exit uses OS reclamation, not asserted live hook-unload proof.
- Filters: two qualified type0 slots, two owner epochs, no geometry diagnostic.
- Limits: native5Hz/owner, fixed8queue,18000max attempts; two6156B latest files
  (plus temporary replacements), no append native trace;100 detailed scene rows
  per owner;5second presentation summaries; first16config revisions/last good.
  Existing32MiB non-image/128MiB image/10GB aggregate limits remain enforced.
- Expected output: artifacts/remix-runtime/runs/*-in-game; manifest/result,
  bounded logs/assets/textures, config revisions, latest native bank, light packet.
  Typically a few MiB plus original/derived images; never uncontrolled GB output.
- Cleanup: exit SFC normally; runner stops owned renderer, closes mappings and
  validates hashes/settings. No accepted-install modification. Do not kill a live
  hook controller or delete running-session files. Preserve partial errors.
- Analysis: compare sponsor visual assessment with native-light SDK receipts,
  accepted config hashes/revisions, packet counts, normal launcher exit and hashes.
  A normal-exit tuning session does not produce controlled live-unload evidence;
  use existing short wiring test if that specific evidence must be repeated.
- Hazards: excessive intensity/source size can look unrealistic; config is
  provisional Remix adapter policy. API shutdown warning40 remains unresolved.
  No per-light shadow-only disable exists in pinned public SDK.

# Run172 — Federation/Romulan expanded surveys reviewed

Sponsor reports first run Federation, second Romulan; third could not start and
was described as cleanup failure. Those race labels are sponsor fixture context,
not inferred model names or a full list of opponents/weapons. Sponsor explicitly
confirms rendering, HUD, targeting and controls behaved normally in BOTH runs.

## Mechanical result — both complete

| Capture | Federation | Romulan |
| --- | --- | --- |
| Run under artifacts/remix-runtime/runs | 20261025-141338-349874-in-game | 20261025-141645-535316-in-game |
| Tactical seconds | 90.0029316 | 90.0013947 |
| Raw bytes | 342,556,800 | 216,971,136 |
| Records | 2,676,224 | 1,695,086 |
| Dropped / queued / writer error | 0 / 0 / 0 | 0 / 0 / 0 |
| Stop reason | TIME, not cap | TIME, not cap |
| Complete raw light records | 84,211 | 78,351 |
| Concrete global-list classes | 7 | 8 |
| Process-local object addresses | 20 | 15 |
| Coarse graphics-state signatures | 15 | 15 |
| Sampled native call chains | 25 | 24 |
| Complete origin samples | 83,353 | 34,035 |

Both result.json: errornull, normal_game_exittrue, gate_clean_unloadedtrue,
gate/controller/hostexit0, originalcriticalunchangedtrue, copiedcritical hashes
match accepted baseline, launchersettingsunchangedtrue, broad_proxy_restoredtrue.
Both native-cleanup receipts: installed/restoredtrue, error/faults/busy/census
overflow0. No game/owned host remains. No cap/sampling overflow or incomplete
light fragments. Existing stored broad.survey.json reports metadata complete,
semantic classification pending. Full file/record counts independently re-read.

Trace SHA256:
- Federation:05B44A3801BC90A030C727F2043B2D95EF4E7CD4E45C104C849A558A9480A75C
- Romulan:881982CE5E5333B25A6F9CC6548481E91D27926D915F4A3B56B8FD91DF6CB1F4

Original captures/manifests/results remain unchanged. Derived
`render-families.review.json` and `native-survey.review.json` are stored beside
each raw file. Ancillary output after analysis14,355,656/10,411,992bytes, each
below32MiB. Combined raw559,527,936bytes (~533.6MiB), comfortably below2GiB/run.

## Concrete classes — confirmed from pinned executable RTTI

The census supplies actual vtable and draw-target pairs. Read only each pair's
vtable[-4] complete-object locator and TypeDescriptor in the hash-verified PE;
confirmed native names below, not guessed from race or visual appearance. This
proves concrete list membership, NOT that visibility admitted every entry or a
one-to-one translated graphics draw/pixel owner. Counts are repeated membership
observations, not numbers of effect instances or shots.

| Native class | Vtable | Draw target | Federation / Romulan observations |
| --- | --- | --- | --- |
| tFx_Phaser | 0x007AA880 | 0x00500312 | 347 / 693 |
| tFx_Drone | 0x007AA050 | 0x004EFA4A | 15,190 / 3,728 |
| tFx_Photon | 0x007AA8DC | 0x00500C30 | 7,782 / not observed |
| tFx_Plasma | 0x007AA944 | 0x00501FED | not observed / 4,618 |
| tFx_Explosion | 0x007AA218 | 0x004F2C50 | 124 / not observed |
| tFx_DisruptorMuzzleFlash | 0x007A9974 | 0x004EEA2D | not observed / 33 |
| tFx_HeavyDisruptor | 0x007AA388 | 0x004F5427 | not observed / 33 |
| tFx_MineBlast | 0x007AA758 | 0x004FE513 | 124 / 123 |
| tFx_Tractor | 0x007AAC38 | 0x005070FE | 508 / 506 |
| tFx_Transporter | 0x007AAC9C | 0x00507FAB | 304 / 152 |

Ten distinct classes across both runs; five shared. Prior Run169/170's selected
fx0 path0x004EFA4A is now qualified specifically as tFx_Drone by pinned RTTI.
Its shared burst/trail atlas still does not make all fx0 artwork a drone effect.
RTTI locators/descriptors retained in derived reports. Native client SHA remains
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.

## Lights — same-run observations, with important distinctions

All64slots initially snapshotted. Slots0–5 were enabled at least once in the
Federation run;0–6 in the Romulan run. Native enabled types0,1,5 observed in
BOTH full traces. Looking only at final slot contents would miss transient type1
in Federation; it is not absent simply because the latest records show0/5.

- Slot0 native type0, white contribution and scale1.5: direction alternates
  between(0.98893636,0,-0.14834046) and(0,0,-1) in both runs. The first appears
 10,691/10,769records, the second10,693/10,771. This is repeated rendering-state
  use/override evidence, NOT proof the environmental light moves around the map.
- Slot1 native type0 has direction(0,0,1),white contribution,scale0.25; observed
  enable transitions10,692/10,770. Do not label each toggle a physical light's
  birth/death, flicker or a weapon shot. Exact caller/pass role still to classify.
- Slots2+ include native1/5 and changing point-like position/contribution/scale
  fields. Slot2 position changed1,515/1,308times; slot3 changed1,270/622times;
  other transient slots also changed. These confirm changing positional light
  inputs. A reused slot can represent different lights, so this is not independent
  tracking of one physical light's motion/lifetime. They do NOT identify which weapon owns each update,
  make +28 one universal intensity field or qualify a Remix conversion.
- Type0 position fields may change but are not used as position by the qualified
  directional-like response. Type5 direction-like storage/tail words may contain
  irrelevant/stale data; only fields consumed by that type should drive a renderer.
  The new offline reviewer decodes only qualified+04..+28 float storage and keeps
  unknown+2C..+3C words raw. Existing primary snapshot's broad float-bit display
  must not be promoted into physical meanings for those unknown fields.

Global gate and setter caller/QPC/thread are preserved. Native timestamps permit
temporal comparison, not exact weapon-light ownership. No GI or ambient-light
identity is established by these records.

## Graphics families / counter cross-check

Both again show opaque depth-writing triangles, modulation-compatible triangles,
additive triangles with different depth behavior, additive points/lines, unblended
depth-writing lines and surface/presentation strips. Largest families differ in
volume; these are observations of retained state, not named effects by topology.
No shader/geometry/image/constant payload was present or read. Existing call-chain
review remains explicit that flush contexts may submit queued work from elsewhere.

Primary origin statistics are flushed at Present. Complete raw stacks exceed
those flushed counters by16/7samples; independently counted16/7complete samples
after the final stats event explain the difference exactly. Zero incomplete
stacks/loss; no need to alter capture or call this a data-invalidating defect.

## Third launch — reservation block reproduced, no cleanup damage found

No third run directory was created. Console error from that attempt was not
provided, so do not claim its exact message independently witnessed. The current
preflight reproducibly failed with:

`ValueError: Survey source/archive reservation exceeds20GB output cap`

Both preceding runs report cleanup success; current process inventory and critical
hash preflight corroborate that. The broad admission reserves4,311,744,512bytes
for a possible2GiBsource plus recoverable archive/sidecars. Two new captures put
that worst-case reservation over the unchanged20GBtotal, despite each actual raw
capture being far below2GiB. This explains a pre-launch block without a leftover
proxy/hook or a need to reinstall anything.

Used the already prepared verified archival maintenance, target256MiB, on ONLY
three additional completed old fixtures:20261024-223136-631957-return-fixture,
20261025-000946-406742-return-fixture,20261025-001325-195259-return-fixture.
313,754,112generated DDS bytes ->17,866,056ZIPbytes;295,888,056bytes freed.
Every decompressed/source SHA matched; restore receipts in each exact run. Original
game files and all current/previous raw capture traces left intact.

After review/archival:15,502,586,452governed bytes before final small docs;
plus4,311,744,512reservation=19,814,330,964 <20GB. Same unchanged launcher's
read-only preflight nowPASS. Do not increase the aggregate cap, weaken cleanup
checks or blame runtime behavior merely to make a third launch start.

## Files / validation / next action

New offline-only `tools/recon/analyze_native_survey.py` and
`tools/recon/tests/test_native_survey.py`: streaming current wire, qualified RTTI,
fragment checks, bounded light/type examples, exact origin-counter reconciliation.
12recon testsPASS, including4new RTTI/target-mismatch/unknown-tail/nonfinite tests.
Existing read-only render-family analyzer ran on both traces successfully.
Survey source/binaries/settings/probe/qualification are UNCHANGED. No new
runtime/RE hook, capture or game launch. No new effect implementation/API work.

Run172/curated evidence/map/STATUS/HANDOFF updated; source syntax/JSON/paths/diff
checked. Prior dirty work preserved; HEADfd79ce5/indexempty/allunstaged/
uncommitted/nopush. No active owned runtime/channel. FuelGuard existing hook
attached; no helper/agents. Sponsor's explicit both-normal attestation recorded.
Existing Obsidian tracker compared/reviewed and refreshed with concurrent-edit
SHA guard; resulting contents verified identical to repository STATUS.

**Exact next action:** use these captures and pinned source to join the now-named
phaser/plasma paths to their actual resource/atlas selections and primitive/state
requirements; distinguish per-pass light overrides from persistent scene lighting.
No third gameplay run is needed yet. Review coverage before selecting an interface
extension; shields/damage/background/UI and attached families remain unqualified
where no actual upstream/resource join exists.

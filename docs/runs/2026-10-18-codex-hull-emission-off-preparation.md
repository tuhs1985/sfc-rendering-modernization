# Run34 — remove whole-hull emission for sponsor washout comparison

SFC-RETURN-20261018-34;2026-10-18 America/New_York.
Authority:sponsor "Let's push the washout fix then do a test run". Implement the
material correction;prepare same runtime workflow,not a new
connection/fallback proof. Original suppression and texture reversal stay separate.

## Baseline / implementation

HEAD e96765a1a34c15212ed22f11edeb9a708b9fc18d;prior dirty work preserved,index
empty. Read authoritative HANDOFF,Run33 diagnosis,current textured contract/probe,
native material adapter and worker manifests. FuelGuard attached actual thread
through hook;no daemon/helper/delegation. Approved CDD unchanged.

`tools/remix_runtime/ship_textured_asset.h`:keep primary as albedoTexture;set
emissiveTexture=nullptr,emissiveIntensity0,emissiveColorConstant(0,0,0). Do not
merely lower all scene brightness or alter original images. Camera,mesh,UVs,world
offset,primary file hashes and secondary handling unchanged. Initial intent was
to retain existing light;offline failure below required a bounded correction.
Legacy magenta diagnostic material remains available only in old modes;
it is not used on textured mesh surfaces. No current pipeline/wire/hook redesign.

`textured_asset.py` and `live_return.py`:current manifest/material description
now says reflected surface colour only,whole-hull emission OFF,directional light
provisional;record `whole_hull_emission=false`, `secondary_applied=false`.
`tests/test_textured_asset.py`:regression requires no emissive texture,intensity0,
constant0,unchanged albedo path and new manifest flags. Probe/contract/HANDOFF and
this record updated. Files/images from older runs not rewritten.

## Evidence / controls / expected result

Run33 fixed-light GPU control observed red87→240 with whole-primary emissionON;
fenced captures support correction,although that standalone diagnostic shutdown
was PARTIAL. Do not rely on its exit as a safety gate:normal production host
must pass refreshed clean-return fixtures separately. Existing SDK40 remains open.

Same [REMIX-TEXTURED-RETURN-001](../reconnaissance/probes/REMIX-TEXTURED-RETURN-001.md)
and native1920x1080 output,100ms source-request-age/owner identity guards,original
ships ON,continuous90s capture,two-beep normal exit,285s Python/300s workflow,
four surfaces<=128MiB,32MiB non-image/128MiB image bounds and10GB aggregate.
No screenshot tooling investigation,no SFC installation changes,no new UAC.
Same original textures,no UV flips. Provisional lighting is not native parity.

### Evidence-supported adjustment after first offline failure

Run `20261018-201501-739988-live-private` PARTIAL:fixture could not qualify enough
visible colours before15s cold-start cap. Host produced263/acquired262,0private
failures,clean LIVE_SHUTDOWN api0;fixture failed cold-start,runner wording "Fresh
host exited during test" was downstream symptom. No gameplay started. Do not
weaken colour/coverage criteria to accept an essentially dark ship.
Recorded model centre[-300.0985,214.3612,.3507] is~369world units from the old
radius.1/radiance200origin sphere. Removing emission exposed unsuitable test
illumination. Bounded alternative:one simple white DISTANT light for textured mode,
unit direction(0,-.70710678,-.70710678),angular diameter.53deg,radiance(1,1,1).
Legacy sphere unchanged. New source change `ship_live_host.cpp`;test requires
textured-only distant/legacy sphere selection. Sponsor informed in commentary.
No camera-following light,appearance tuning,game light extraction or arbitrary
brightness increase. This is now a material-plus-necessary-inspection-light test,
not a strict one-variable quantitative experiment.

## Reproduce / validation / final state

Bundled PS7 `-NoProfile -File tools/remix_runtime/build_live_return.ps1` PASS,
/W4 /WX;native89request checks eachx86/x64. Bundled Python with TEMP/TMP set to
ignored artifacts/test-temp,`-m unittest discover -s tests -p test_*.py`:
Initial211PASS/4.263s;final212PASS/4.391s after directional-light regression.
Eight bounded offline GPU gates refresh source/binary pins using
`qualify_live_return.py --execute` profiles:textured callback/slow/disconnect;
legacy direct/callback/slow/disconnect/visible. Exact final evidence appended below.
No gameplay launched by these fixtures;no wrapper installation/client patch.

Sponsor command from validated elevated parent remains:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\remix_runtime\start_return_image_session.ps1" -TexturedShip
```

Usual two-ship skirmish,extra copy stays ON;camera/motion cues retained,exit normally
at two-beep request. Compare hull colour/panels to prior washed-out copy,report
whether improved or too dark and any native rendering/control issue. Saucer
orientation may still be wrong and is not part of this correction.

No stage/commit authorized or performed;preexisting work preserved. No transient
session needed to resume;qualification must match rebuilt production files.
**Exact next action:**sponsor executes same command when ready;collect completed
run and visible comparison before calling washout correction demonstrated in SFC.

## Final readiness evidence

**READY FOR SPONSOR RUNTIME TEST.** Eight final GPU gates PASS,all suffix
`-live-private`,UTC20261018:201718-789860(textured),201740-519481(textured slow),
201803-486939(textured disconnect),201825-240643(direct),201833-510518(callback),
201842-605191(slow),201852-335182(disconnect),201900-319670(strict visible).
Textured normal131/128,slow130/127,disconnect2/1 produced/acquired;0private failures.
Normal and slow retained silhouetteIoU0.998869;normal60/60 steady motion samples,
14,134textured pixels/203quantized colours. All normal host/fixture exits0;
intentional disconnect hosts are not normal-exit claims. SDK40 remains separate.

HostSHA256 `0F48A1465F5B25540D5C5A7E82711A10BA2456F54EC67B861F94DDDD1E5C1606`;
qualificationSHA256 `00D590736F9B7E6F4D18A826DC538B7829717FDE1933408377A8A06AD501E2BF`.
Read-only `run_return_game.py --textured-ship` preflight PASS,no game started.
Source/JSON/Markdown references and git diff --check PASS,indexempty.
Both executable hashes independently unchanged:
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.

Nine offline runs including dark-hull PARTIAL archived(raw retained,no deletion):
`artifacts/remix-runtime/archives/20261018-hull-emission-off-preparation.zip`,
36,099,702B,CRC PASS,SHA256
`9833E97A336B519963F35EA89DB8077C6887A05A4CB2ECBAACBE373A00097D3B`.
Curated [summary](../reconnaissance/evidence/20261018-hull-emission-off-preparation.json).
Known normal-runtime SDK40,unresolved saucer reversal and scene/UI overlap remain
open. No SFC gameplay evidence or visual washout acceptance claimed from fixtures.

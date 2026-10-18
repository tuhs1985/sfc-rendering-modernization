# Run32 — stop repeating routine ON/OFF proof

SFC-RETURN-20261018-32;2026-10-18 America/New_York.
Sponsor:since delivery works,stop ON/OFF cycling unless a test specifically calls
for it. Authority updates routine workflow,not rendering architecture or requirements.

## Baseline / decision

HEAD e96765a1a34c15212ed22f11edeb9a708b9fc18d;prior dirty work retained,index
empty. Reviewed HANDOFF,Run31,runner schedule/cleanup and textured probe.
FuelGuard attached real thread through hook;no daemon/helper/delegation.
Sponsor's latest screenshot/report confirms visibly sharper returned textured ship;
apparent saucer texture orientation and washed-out provisional lighting remain
open. This run does NOT adjudicate those defects or modify textures/materials.

Routine `-TexturedShip` now remains enabled for the whole90s tactical window,
then explicitly disables/stops before semantic cleanup and two-beep exit request.
Camera/movement cues remain. Same source-age/identity guards and failure omission;
this does not mean stale output is retained. Original ships always remain ON.
Legacy diagnostic modes retain0–30ON/30–45OFF/45–60ON/60stop for targeted tests.
No global new switch,surface/transport change or original replacement.

## Files / validation / reproduction

- `tools/remix_runtime/run_return_game.py`:pure `observation_phase` helper selects
  continuous phase0 only for textured mode;explicit final stop before unload;
  console instructions describe continuous observation.
- `tests/test_live_return.py`:boundary regression at0,29.9,30,44.9,45,59.9,60,89.9;
  continuous never toggles,legacy phases remain0/1/2/3.
- Probe `docs/reconnaissance/probes/REMIX-TEXTURED-RETURN-001.md`,this run record
  and HANDOFF updated. Earlier run logs/phase descriptions remain historical.

Bundled Python3.12.14,TEMP/TMP=ignored `artifacts/test-temp`:
`-m unittest discover -s tests -p test_*.py`:207PASS/4.295s.
No native implementation changed/rebuilt;previous /W4 /WX binaries retained.
Source qualification includes runner,so refreshed eight bounded offline GPU gates
using `qualify_live_return.py --execute` with textured callback,slow,disconnect;
legacy direct,callback,slow,disconnect,visible. Same pinned Remix1.5.2/SDK0.6.4,
native resolution checks and strict texture silhouette>=0.98 required. No SFC
launched;scoped offline GPU access only. Final gate paths/qualification below.

All eight PASS;UTC20261018 runs (each suffix `-live-private`):194516-492698,
194538-151544,194601-289346,194623-017554,194631-270032,194640-243140,
194649-908535,194657-898522 in the flag order above. Refreshed qualification SHA256
`F247AEFCA8EFF336A0787CFD677E997AACFDBC9A0F90B66FD1A10F9BAD2FC3CF`;
read-only `run_return_game.py --textured-ship` preflight PASS. GPU gates confirm
unchanged rendering safety,not actual gameplay execution of the new90s schedule;
pure schedule boundary regression covers the routine policy change.
Archived at `artifacts/remix-runtime/archives/20261018-continuous-textured-qualification.zip`,
28,714,281B,SHA256
`062D5AB0D1759C0647B0A7467F71E2EC070C380F208E5A85512AEFE2377EA905`;
CRC PASS,raw retained,no deletions. Python parser,Markdown references and
git diff --check PASS;no stage/commit.

Same [probe](../reconnaissance/probes/REMIX-TEXTURED-RETURN-001.md) and90s tactical/
300s prepared limits;32MiB logs,128MiB images,four output surfaces<=128MiB,
10GB aggregate. Continuous observation may produce more updates than45enabled
seconds,but bounded logging/summaries unchanged;no repeated image dumps.
No UAC/security,client or accepted-install changes. Assets/materials untouched.

No stage/commit,indexempty,preexisting edits preserved. No active game/session
required. **Exact next action:**when the next approved visual test is ready,use
the same `-TexturedShip` command;expect continuous copy until exit request,not
an ON/OFF cycle. Do not request another run solely to prove this schedule change.

# Run61 — reclaim retired roughness-map versions during tuning

Date2026-10-19 America/New_York. Sponsor authorizes cache fix overnight;no gameplay
requested. Starting HEAD357bc703e3dc0923cd4c7801ec87e99abc01f157,
codex/github-sanitized,prior Run57–60/user work unstaged/uncommitted. Read HANDOFF,
material relay/map generator,host GPU-idle/material replacement path,Run59/60
authority. Fuel Guard attached existing hook;no daemon/helper. No settings reset.

CONFIRMED cause:each material revision retained a new full roughness DDS set;
combined session image files reached an imposed128MiB cache budget,not a measured
RAM exhaustion. This was a deliberate safety limit but unsuitable retention policy
for repeated tuning. Do not loosen total output bounds or delete in-use images.

## Design / files

Updated tools/remix_runtime/{material_controls.py,roughness_maps.py,
remix_material_controls.h,ship_live_host.cpp,qualify_live_return.py},
tests/{test_roughness_maps.py,test_material_controls.py,
remix_material_control_tests.cpp},config/README.md,
docs/reconnaissance/probes/REMIX-ROUGHNESS-MAP-001.md,this record,HANDOFF.
No config/settings,geometry,texture conversion,lights,image adjustment,compositor
or original SFC hooks changed. Factory and temporary-baseline values preserved.

New bounded atomic40byte receipt:processed/active material revisions,status,FNV.
Host writes only after safe old material/mesh destruction at existing complete
GPU/idle-consumer boundary,or after failed candidate cleanup. Initial receipt
follows asset creation. Repeats latest receipt on500ms worker poll to tolerate
brief Windows sharing violations. No SFC render-callback IO/waits/allocations.

Worker serializes publication:ONE pending profile,await matching receipt;keep
active/in-flight derivatives. Then delete only exact managed generated names in
resolved session textures directory,not original/emission DDS. Missing/stale/
corrupt receipt cannot retire anything;host rejection preserves active set;
failed unpublished generation cleared. Locked deletion deferred/retried within
the SAME128MiB budget. Warning now states image-cache budget,NOT system RAM,
and reports requested/allowed bytes. No cap increase or silent settings fallback.

Engineering judgment:successful SDK material destruction at the already-tested
GPU boundary ends that adapter material's use;worker receipt makes this explicit.
Runtime corroboration is required before returning the launcher for gameplay.

## Commands / limits / validation

Existing bundled pwsh/VS2026 C++20 build_live_return.ps1 (x86/x64),bundled Python
unittest discover -s tests with project-local TEMP/TMP. Probe
REMIX-ROUGHNESS-MAP-001 amended BEFORE expanded actual runtime test.
qualify_live_return.py --execute --material-controls now exercises8map edits,
invalid edit,uniform restore initially;first attempt below showed fixture duration
was insufficient. Final fixture uses4map edits,invalid edit,uniform restore and
requires6accepted profiles plus positive reclamation.
qualify_material_pipeline.py rechecks14source-matched return gates,compacts
finished fixtures using per-file decompressed SHA verified archive script,and
revalidates unchanged independent Run58 pixel proofs by their exact hashes.
No SFC launch. Same60s/32MiB fixture,128MiB image,4096dimensions,256edits,
10GB overall evidence. No repeated image dumps or appearance tuning.

Initial tests:276Python PASS before added host-rejection regression;native
material24checks each architecture,existing native checks PASS. Further final
test/actual SDK evidence recorded below after completion. No new TRL/milestone
claim. Independent specular knob remains unsupported;SDK40warning unchanged.

## Final result / handoff

Initial targeted fixture20261019-055744-345698-live-private returned PARTIAL:
consumer completed its normal short window before8expensive map preparations.
Native rendering/exit itself PASS,failed0,API shutdown0,3published profiles.
This was incomplete test coverage,not demonstrated unsafe retirement. Preserved
partial evidence. Bounded correction:publish private factory material BEFORE
asset prep,and hold stationary fixture20extra seconds under explicit cache-test
flag,within unchanged overall60s. Four map revisions exceed the old retain-all
128MiB capacity on this56material fixture;30-edit unit proof covers long sequences.
Modified ship_live_gpu_fixture.cpp only for that opt-in offline fixture hold.

Subsequent targeted fixture20261019-060114-755200-live-private PASS54.687s,
6accepted profiles/1invalid rejection,82,358,272Bretired map data reclaimed,
no pending revision,fixture_exit0,failed0,API shutdown0. Four enabled map revisions
plus uniform restore succeeded without raising128MiB budget. Added an additional
defensive check after this test:if SDK failed-candidate cleanup itself fails,
host stops optional rendering WITHOUT a release receipt;maps remain protected.
Full source-matched matrix covers the final source/binary below.

Review caught relay-construction ordering:long-lived tuning relay can predate the
asset-preparation publisher. It must adopt a newly published packet on EVERY poll
before collection,not only its constructor;otherwise active maps could be mistaken
for orphan files. Corrected and regression-tested. Repeated or delayed rejected
receipts retain active revision;stale/corrupt receipts never authorize deletion.
Final278Python tests PASS6.045s;material native24checks per architecture and
existing quality14/image22/request89/UV14/light25checks each architecture PASS.

Final source-matched verification PASS:14return gates,refreshed receipt SHA256
BC4941C0EE73AE40EE084C9216D46C8F568BF195D0104AC9F2F5DEDD10887B88;
host SHA256741BC626E2E5847A435B3ADCCD684C85E312F79EA99FFC86BDCCA5DEAE6C9A2F.
Final material proof20261019-060841-160461-live-private:53.313s,6accepted,
4enabled map revisions,1invalid rejection,82,358,272Breclaimed,no pending,
failed0,fixture_exit0,API shutdown0. No cap increase. Same independent Run58
17image/10quality pixel proofs revalidated against their own source/executable
hashes,not relabelled as newly executed. Read-only --light-tuning preflight PASS;
no SFC/owned host/fixture remains. Curated exact paths/results:
[evidence](../reconnaissance/evidence/20261019-material-cache-retirement.json).

All four active config files match the sponsor's temporary-baseline snapshot
byte-for-byte. Both client hashes remain unchanged:
4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29.
Python/PowerShell parser checks and git diff --check PASS. No unrelated changes.

Output cleanup:final9fixture texture archives53,348,841Breplace658,362,442B
generated copies after decompressed per-entry SHA verification. Also compacted
exact finished historical fixtures004230-199967,004252-524999,004316-231644,
004338-220535,004503-631406,004525-734698,004549-262164,004611-262528
(all20261019-/suffix-live-private) to preserve10GB ceiling and next-run headroom;
each46,367,290Bgenerated set replaced by4,730,177Bverified ZIP. Logs/packets/source
associations remain;texture-archive.json includes each ZIP hash. Targeted PASS
fixture archived too. Initial PARTIAL fixture was safely completed natively:
archive_fixture_textures.ps1 now permits an explicit -AllowCompletedPartial ONLY
for this precise incomplete-material-proof error AND both native PASS/shutdown0
markers. Its102,891,834Bgenerated set is recoverable from6,690,041BZIP,
SHA256C3C5198F067316F36166DB0D51DA3DEE3D80B3BE4B75234349BF8E4BA5E3EA4F.
No original/reference assets or evidence logs/packets removed. Same script's
default acceptance criteria unchanged. This additional helper change is part of
the exact file scope above,along with the new curated evidence JSON.
Final retained runtime evidence9,548,137,299B/10GB;384MiB next-run reservation PASS.

Final Git HEAD357bc70unchanged;all previous work and this fix UNSTAGED/UNCOMMITTED,
nothing pushed. No new live visual claim/TRL advancement. Temporary baseline remains
docs/reconnaissance/evidence/baselines/20261019-sponsor-temporary-appearance/.
No staging/commit/push authorized. Next exact action after validation:use existing
light-tuning launcher and tune normally;do not ask sponsor for administrative
confirmation or another manual RE test.

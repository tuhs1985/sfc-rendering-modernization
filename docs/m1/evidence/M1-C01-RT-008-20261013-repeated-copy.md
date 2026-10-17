# RT-008 — repeated fresh copies with guarded epoch retirement

**M1 CONTINUES — additional bounded evidence required** under the unchanged
[probe](../probes/M1-C01-RT-008.md) criterion of 32 handoffs. **CONFIRMED:**
30 distinct fresh private inputs were consumed without reported gameplay issues.
Do not misclassify missing two records as copy corruption or claim the full
32-record criterion passed. Normal appearance alone is not the evidence.

## Direct runtime result

Run `artifacts/m1/runs/20261013-225853-enabled`, component0.11, PID26148;
started 2026-10-13T22:58:53.6478731-04:00; completed
2026-10-13T23:00:59.3642750-04:00. Same two-ship fixture and automatic gate.
Sponsor: "did as instructed, game ran as expected"; no reported regression.

| Observation | Result |
| --- | --- |
| Fresh lists / applied handoffs | 30 / 30 |
| Preparation receipts / parent completions | 60 / 30 |
| Failure / receipt mismatch / halted flag | 0 / 0 / false |
| Copied payloads intact at stop | 30 of 30 |
| Handoff interval observed | 21,594 to 50,610 ms; 29,016 ms span |
| Rendered frame indices | 1,292 to 3,032; 1,740-frame span |
| Shape per handoff | 452-pointer list, first64 complete polygon payloads copied |
| Payload / slot / fixed bank | 8,976 / 20,512 / 657,004 bytes |
| Fingerprints before/after | 4131310351 throughout, all matching |
| Observation / corner windows | 90 seconds / 36 valid records through85s |
| Total rendered frames / owner retirements | 5,392 / 2 |

Selected owner epoch1, thread29176, ship`1250AD88`, visual`1237F658`,
model`1E12C518`, manager`04AC0038`, source`04A6365C`, original list`0C64D9B0`.
First private list`6061741C`; each subsequent private list is distinct. Primary
wrapper`006AC5A0` / return`0042E55D` and preparation`006ABFC0` correlate each
published pointer to the same selected scope. Two receipts per handoff are
downstream observations, not duplicate publication. Uncopied tail remains original.
All 30 records have successful publication, receipt, parent and integrity checks.

36 corner windows include 28 object-transform changes and 28 position-transform
changes within comparison-qualified epochs; sampled corner bits remain unchanged.
This supports observation during motion/camera activity, not a new coordinate-space
interpretation or proof that a modified payload was used. No visual change intended.

## Why the series stopped

Corner transition records show epoch2 retired at49,891ms, fresh epoch3 observed
50,969ms; selected epoch1 retired at51,000ms, fresh epoch4 observed51,110ms for
the same raw visual addresses. The selected epoch's first30 handoffs finished
before retirement; the next earliest would have been51,610ms, after that change.
Later corner samples show epoch4 using the same sampled model/source/count.

**CONFIRMED:** IDs were not merged, the selected lease did not migrate, and no
additional copy was published after retirement. This matches the deliberate
same-epoch guard. **Unresolved:** why the render observation gap occurred.
Retirement uses a short observation-gap rule; it is not proof of destruction,
actual visibility loss, gameplay failure, or sponsor error. Do not assume changing
that retirement threshold is the correct fix. There were2,332 identity skips
during otherwise eligible wrapper opportunities; they include other identities,
not solely the retirement event.

The private-copy analyzer correctly reports only
`repeat_count_or_limits_not_confirmed`. Keep its original criterion unchanged;
the run proves repeated handoffs but does not exercise runtime bank exhaustion.
No automatic rerun just to fill two slots. Next bounded question: how to explicitly
requalify a fresh epoch, as a new identity, without inheriting the old lease or
overwriting/freeing previously published data. Review that contract before code.

## Other paths and cleanup

Wrapper10,706 primary, zero secondary, 6,369 unscoped; accepted parent closures
10,706. Known`00509843` count5,396. Rejections1,946: 669 visual exclusions from
`004EFC49`, 304 from`00413B2D`, 973 Model0 owner-missing from`0042FDD5`.
These counts are consistent with paired exclusions, not complete per-call pairing.
The second caller remains unclassified; no broad RE or new ship-vtable assumption.
Wrapper/rejection/corner analysis issue lists empty.

CSV339,438bytes /1,180 detailed events; warning/truncationfalse; owner/thread
overflowzero. Generic`006AB410` hot hook, tint and shading changes disabled. No
fresh generic/native-draw transcript claimed. All hook bytes restored, normal
process exit observed, game-directory generated proxy absent, no remaining
game/controller observed. Inert bank/module deliberately pinned until process
exit; hook restoration is not early unload. No memory reuse/free claim follows.

## Preservation and hashes

All18 raw files total **1,166,084 bytes**, retained ignored. Hash-verified archive:
`artifacts/m1/archives/M1-C01-RT-008-20261013-225853.zip`, **131,826 bytes**,
SHA256 `1F0A970CC0146D8F7A5B0D5998EA5CED4C9F47E6E5CE5FD8EEB3E56B6088FA07`.
Every ZIP entry verified against its raw source. No deletion. Established 90s,
32 attempts /1s spacing, 700KiB bank, CSV16/32MiB and corner3MiB limits retained.
No uncontrolled or multi-GB output.

Client SHA256 unchanged, independently rechecked installed client:
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`;
runner MD5`2BE8F713F81B1C68D50EAD6088C32886`.
Runtime component SHA256
`5FF44EBEE7CABA1366D32FF945C02AD99CCDC21A74F3605F816D2FAE1281BF77`;
controller`F683FCC8C225DCB6789CCB845E115B75C9A60AFBA3907DC175EA4002FDB0B112`.
These runtime rebuild hashes supersede preparation hashes for this capture.

Exact evidence: M1-A-summary.json/repeated_private_copy records and component
log, corner packet/transitions, private-copy/wrapper/rejection/corner analyses,
run-metadata.json, run-result.json, cue log, telemetry and semantic CSV in run dir.
Metadata's legacy corner cue array0/15/30 is stale for copy mode; actual cue log
records setup22:59:06.2720262 and completed-start22:59:26.9140227. The actual
gated first handoff at21,594ms corroborates delayed release. Correcting inherited
metadata is a bounded tooling follow-up, not grounds to invent extra phase actions.

No full-rate substitution, reusable-buffer lifetime, destructive object-lifetime,
visual enhancement, C-02 authority or formal TRL4 completion is established.

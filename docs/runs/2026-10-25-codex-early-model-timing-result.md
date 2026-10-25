# Run177 — actual early model loading measured

2026-10-25 America/New_York. Sponsor supplied completed run and explicitly
confirmed normal rendering/HUD/targeting/controls. Review only; no new gameplay,
runtime code/build/settings/renderer change, staging/commit/push or cleanup.
API stays parked. This completes the initial native-timing question, not early
asset capture, startup-delay resolution or a milestone gate.

[Curated raw-derived results](../reconnaissance/evidence/20261025-early-model-timing-result.json),
[static path](../reconnaissance/early-model-availability.md),
[observer contract](../../tools/early_model_probe/README.md).

## Capture integrity

Actual run:artifacts/remix-runtime/runs/early-20261025-171918-511526.
Trace SHA256:7A03DD8C41501CA88E9E7FD94A306011C16840B8BE8B8045D289C97C36911017.
94records/48256bytes,90.0450336seconds after tactical marker; timer stop, zero
drops/queue/errors/flags/identity uncertainty/readfaults/busy.92records on one
game thread;2terminal records on worker. Source/build/dependency manifest matches
current qualification exactly. Fresh parser output exactly matches stored report.

Both named ship chains have live owner/asset epochs, source equality, actual
selected child and original mainline caller0042FDD5. All9hooks byte-exact restored,
active0/hookedfalse/fileclosed, normal game exit0/host0, accepted/copied critical
hashes and launcher settings unchanged. No new original-file changes. Sponsor
explicitly reports normal game behavior. Original evidence remains unchanged.

## Measured native timing

| Model | Request→first semantic entry | Full native loader | Parser portion | Work after parser | Full-load completion→first semantic entry |
| --- | ---: | ---: | ---: | ---: | ---: |
|Federation FCA|208.3085ms|90.8858ms|36.6085ms|54.2773ms|117.4186ms|
|Klingon KFF|27.6921ms|13.8198ms|7.0463ms|6.7735ms|13.8709ms|

These are native events, not Remix rendering or physically presented pixels.
Do not name a pointer as the player solely from its model; FCA is the expected
player-model class from the familiar fixture, but player-role flags were not
captured. Full loader→attachment:0.0038msFCA/0.0046msKFF. Most usable lead is
between attachment and first drawing; an attachment event is nearly as early as
full-loader return in these two cases.

Both primaries returned before the first tactical gate:66.2814msFCA/13.8678msKFF.
FCA first semantic entry comes later than the gate's first KFF rendering scope.
The ~47second pre-tactical interval includes sponsor menu/setup time; it is NOT
47seconds of available preparation time for these ship models.

All58FCA groups had nonzero primary IDs,31secondary-enabled groups and zero
missing referenced IDs; KFF5groups/5primary/5secondary, zero missing. First8IDpairs
sampled, not exhaustive image provenance/export. Position pointer unchanged from
parser to first draw for both, original-position pointer0: optional pointer-
replacement scaling was not observed here, but remains a static supported branch.
The post-parser54.3/6.8ms is aggregate native work, not isolated texture-upload,
disk, shader or GPU cost. Do not assign it entirely to one stage.

## Other observations / exceptions

18loader calls/18parser entries:17successful fresh native model loads,1failure,
**zero actual cache hits**. Offline cache controls remain the only cache-reuse
validation. Names include space backgrounds, xmn/xwp/xsh and hft/fft/kft/rft/gft/
ift/zft resources before the two ship primaries and separate _BRK assets. These
are loaded resources, not proof all factions/fighters appeared or a mission roster.

The LFT filename assets/models/lft/lft.mod returned failure after a parser call
in0.0565ms, with destructor entry and no qualified asset. Cause not recorded;
do not assume a missing disk file or our defect. Original game continued normally.
FCA_BRK36.1396ms/KFF_BRK7.1914ms are distinct assets; do not count them as new ships.
Background space29 was prepared ~44.8s before the tactical gate, then retired as
other backgrounds loaded. It is not early knowledge of the selected ships.

5observed ship constructors/3retirements leave2owners in the window. One pointer
retired as owner epoch4 then returned as epoch5 before KFF attachment; this is
actual evidence that pointer reuse must not be mistaken for continuing identity.

Nonship resource counters require caution: current diagnostic data22counts BOTH
source words even where the secondary flag is off. Background samples contain
unused7582116secondary words with zero secondary-enabled groups, producing an
out-of-range counter that is NOT evidence of corrupt active textures. XWP has
three zero primary IDs; intentional untextured versus unresolved not adjudicated.
Neither issue affects the two ship chains (their raw counters/missing IDs are0).
No hook/code change made while reviewing; retain these limitations before broader
asset export. No native exception/error invalidates this recorded timing result.

## Engineering conclusion / next action

CONFIRMED: the earlier name and post-load data exist; both native loads complete
in milliseconds. Earliest usable lead here is tens to~117ms, NOT seconds. Sponsor
correctly notes that native SFC preparation is fast. Moving the trigger earlier
alone cannot explain/fix the previously recorded several-second returned-image
delay. Translation duration is not independently measured by this observer.

Existing Run163 controls already locate a first-correct-material/readiness issue
on the ordinary D3D9 path: accepted5.170soutput versus2.578sfaster output lacking
enhanced materials; changing waits/prepublication did not establish parity.
This run is NOT a controlled A/B subtraction from those different fixtures, nor
proof every remaining millisecond belongs to a vendor operation. Keep supported
negative controls; do not repeat blind warm-up switches or claim no diffuse texture.

**Exact next action:** review existing accepted-scene delivery/material readiness/
first-correct-output timing on the ordinary D3D9 route using retained assets and
Run163 evidence. Identify the smallest attributable downstream change before
implementing it. No additional native discovery/gameplay run needed, no API
resumption/early-geometry export/renderer architecture change as a shortcut.

## Validation / state

22observer parser/supervision tests PASS0.041s; read-only preflight PASS. Independent
raw event extraction and timing arithmetic reproduce stored joined results;
manifest/current qualification exact. HEAD6d847dd/indexempty; prior Run174–176
dirtywork preserved. This run adds curated JSON/run notes and updates canonical
findings/probe/STATUS/HANDOFF plus reviewed Obsidian tracker. All unstaged/
uncommitted/nopush, existing20GBcap retained, no deletions/helper/agent/daemon/
owned process/channel. FuelGuard existing trusted hook attached.

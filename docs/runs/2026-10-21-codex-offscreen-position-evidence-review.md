# Run99 — existing camera-gap evidence and persistent-position candidate

2026-10-21 America/New_York. Sponsor asks to check recent captures for retained
position during brief camera break. Analysis/documentation only,no implementation,
gameplay,helper,agents,staging,commit or push. Fuel Guard recent-hook attachment
confirmed. Starting HEADd29111f7,index empty,Run98and earlier dirty work preserved.
Read HANDOFF,Run98,Run97curated evidence,lifecycle/source formats,existing native
owner/scene capture implementation and previously mapped LIVE-BRIDGE-001 source.

## Direct existing evidence

Run97folder `artifacts/remix-runtime/runs/20261021-062533-368618-in-game`:
parse gate96word state rows and lifecycle events,64word fresh mesh headers,source
timing stage1records. Source timing has per-offer identity/time,NOT transforms.
Compare last status1detail before retirement and first status1after return.

| Observer labels | Last detail / retirement / return frame | Detail gap | Translation change |
| --- | --- | --- | --- |
| FCA2→3 |2550/2558/2613|1047ms|(-300,200,0) unchanged |
| KFF1→4 |3761/3768/3825|1063ms|(14.806767,200,0)→(8.712179,200,0) |
| KFF4→5 |4162/4169/5056|14906ms|(-23.382172,200,0)→(-105.450958,200,0.264388) |

Across EACH pair,all fresh packet provenance header words8..15 are identical:
ship,visual,model,manager,source,caller,list,vertex-base addresses. CONFIRMED
address continuity,not an independent generation/allocator-lifetime guarantee.
FCA native ship0x17926BB0,visual0x17CD6F50,model0x1A2AC284;KFFship0x17A5AD88,
visual0x17A4E8E0,model0x1A2AC590. Manager is shared by both ships in the capture;
its supplied transform is contextual render scratch,not a per-ship persistent
position address. Merely polling manager+6F4offscreen could read the OTHER ship.

Retirement→return gaps922/953/14781ms. Inside those intervals source stage1offers
contain respectively55KFF1,57FCA3,887FCA3records,but ZERO fresh offers of the
missing ship. State detail also has no fresh missing-owner transform. The
continuing other-ship observations show the collector/game were not globally
stopped. They cannot fill missing-owner samples or prove exact update cadence.

Earlier Run95folder053837has FCA2→3:detail1981,retirement1987,return2203,
3703ms detail gap/3609ms retirement gap,same native header8..15and stationary
(-300,200,0),216other-owner offers during retired interval. Consistent result.

Evidence hashes Run97:

- `gate/LIVE-SCENE-001-updates.jsonl` SHA256
  `37F04490477EF60A908E62A7C64B05FB45FC7ECA057E43264699CEC2AD95ED5A`.
- `gate/LIFECYCLE-001-events.jsonl` SHA256
  `3DE4E240FD3EAEBB5C3F76D8B39607512DA0A67FD9134AB087BBBC5F8887B1FE`.
- Source timing SHA256 remains Run97record
  `F74F69947AB508DD63EB008C9B6FCF9BB19ACFA87CF62E43A137F49AD770E587`.

## What this changes—and does not prove

CONFIRMED:our OwnerTable uses ship address while active,then assigns next_id
when inactive. Component scene entry calls `retire_before(frame-2)` and retires
slots whose last observation is older;no native destructor/death signal is used.
Our epochs change while fresh captured native addresses remain identical and
moving enemy's supplied translation differs on return. Calling this an SFC
identity change would be unsupported. Camera cues are requested actions,not
frame-exact camera-switch timestamps;do not label all absence as measured GPU
culling or all translation difference as continuous sampled offscreen movement.

STRONG HYPOTHESIS:same SFC object persists and offscreen simulation continues.
Enemy displacement across gaps strengthens sponsor's projectile/fighter
explanation. Existing evidence does NOT establish fresh missing-ship positions
inside the gap because our collector only reads transforms on the render path.
Stationary FCA by itself cannot demonstrate offscreen updates. Continued
offscreen drawing remains SPECULATIVE and unnecessary to persistent simulation.

Already mapped narrow source candidate,not new discovery:
[LIVE-BRIDGE-001](../reconnaissance/probes/LIVE-BRIDGE-001.md) records ship virtual
+6C→00419DD2,getter builds ship-local cache+9C4via00413B34from rotation
+92A/+92E/+980and translation+E6/+EA/+EE,then00416323hands it to006AA550,
which copies17words into shared manager+6F4. This is static prior support for
looking upstream of the shared manager. It does NOT establish field formats,
atomic update timing,lifetime-safe offscreen reads or that cache+9C4updates
when the render getter isn't called. Do not call a game getter from a worker
or treat cached transform presence as freshness without qualification.

Design implication:separate persistent game-object lifetime,render visibility,
resident asset identity and fresh per-frame pose. No implementation authorized
or changed in this review;don't simply turn off retirement or show cached pixels.
Run98camera-return launcher remains prepared,but another same-path capture alone
cannot answer fresh offscreen pose:it has the same coverage gap.

## Reproduce/validation/final state

Read JSONL arrays length96. Select status1old[-1]/new[0],status2retirement event.
Packet `struct.unpack('<64I', raw[:256])`;compare words8:16. Supplied17words
row8:25decode as17little-endian floats ONLY to read matrix components3/7/11;
word16metadata is not interpreted as a float in arithmetic. Translation arithmetic
uses previously validated native model transform convention. Source stage1filter
retirementFrame<=frame<firstReturnFrame;count owners,not filenames/latest-memory.
No geometry/image conversion,no new bulk evidence or game-file mutation.

Read-only analysis commands completed;documentation `git diff --check` PASS.
Original evidence unchanged,no client/build/runtime test needed for doc-only
review. HEAD unchanged,index empty,all prior/new work unstaged/uncommitted.
No active tool/collector was started beyond Fuel Guard attach;session state
does not become persistent project evidence.

Exact next action:qualify the already mapped ship-local position/rotation source
and lifetime protection for a bounded offscreen read,without relying on the
shared graphics manager or invoking the render getter. Inspect existing exact
setter/getter evidence first;only then decide whether a narrow runtime probe is
needed. Do not request another identical camera-return run for this missing fact.

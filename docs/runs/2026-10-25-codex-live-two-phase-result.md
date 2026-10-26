# Run185 — live two-phase asset production faster, first returned frame unchanged

Reviewed latest `20261025-204448-465037-in-game`; experimental and parallel flags
true, no run error/preparation partial/rejected assets. Sponsor reports about3s
arrival/no noticeable speedup, occasional camera-switch flicker consistent with
prior behavior, and shorter-looking new-ship flicker. No independent assertion
that every SFC control was exercised. No SFC launch or implementation changes in
this review. FuelGuard advisory attached; available credits remain authorized.

Compared with Run183192053 (same initial KFF/FCA geometry hashes):

| Recorded milestone | Prior parallel | New two-phase |
| --- | ---: | ---: |
| KFF base, from its discovery | 292.33ms | 280.98ms |
| FCA base, from its discovery | 1153.53ms | **466.32ms** |
| FCA enhanced pieces, from its discovery | 1780.55ms | **983.71ms** |
| First matching returned/game frame, from first discovery | 3.488309s | **3.890227s** |

Thus asset production improved but **visible-path startup did not improve** in
these two sessions. Do not describe the CPU improvement as a displayed loading
speedup. These are observed live sessions, not randomized controls/physical pixel
timestamps. Initial model contents match; later activity differs.

Global discovery-relative times: renderer activation0.352169s; KFF base0.280975s,
FCA base0.635286s/enhanced1.152672s. Native asset admission1.480025s/3.614308s.
FCA bundle assembly/write173.249ms, prepared catalog identity0.0256ms; former
producer-helper wait is gone. Roughly3.25s remains from FCA base readiness to first
matching returned frame, but that full interval is not attributed to one operation.

Two KFT fighter owners discovered around54.997s/55.025s. Base readiness30.12ms/
31.00ms, one canonical asset plus alias; canonical enhanced37.57ms. Both bind to
the shared resource, native admission55.068283s. Four acknowledged owners,
no cross-association/rejection/partial. Content sharing and fresh late base
production work; this does not mean late display is uninterrupted.

Full buffered audit:96post-start missing returned layers, including69consecutive
records55.636–56.771s near fighter arrival. Several camera-period gaps3–4records;
no causal camera timestamp inferred. Sponsor judged occasional camera flicker
unchanged and addition flicker shorter. Do not silently turn that into a no-flicker
or seamless-streaming pass. Prior run had5post-start omissions and no fighter
arrival, so this is not a controlled stability regression comparison.

Normal game exit/gate unload/controller and renderer0/proxy restored/original
critical hashes/settings unchanged/final report complete. No owned process or
channel remains from review. HEAD9ff2d3d, all changes unstaged/uncommitted/no push.

## Remaining sequencing relationship

Static source review: `d3d9_direct_host.cpp` calls `MultiSceneRuntime.assets()`
through `ownerInput.idleWork` in `live_owner_input.h::next`. Frame0 bootstrap does
not call that input path. Later asset admission is serviced between output-loop
iterations; the same thread performs Present/output-copy, wait9, post-fence wait
and peer publication before the next input/admission pass. `assets()` itself
admits at most one resource per pass and uses one asynchronous preparation future.
This structure is CONFIRMED; it is not proof that any particular wait accounts
for the entire startup interval. Repeated first→second admission gaps~2.14s across
both runs make it a relevant next target. No new native/RHI behavior changed yet.

Exact next action: trace/service asset admission independently of first-output
waiting on the existing renderer thread, using bounded existing readiness/ownership
rules; attribute bootstrap/Present/copy/fence/peer portions before changing policy.
Preserve fast base production and coherent output; no extra discovery gameplay or
unqualified multithreaded D3D9 calls. Late material-consumption issue remains open.

# SFC-07 independent scene reader and first transient observation

The offline `tools/asset_diagnostics/inspect_scene.py` command reads existing `scene.bin` and `scene.json` pairs and checks the original packet and texture associations. `--arrays` includes positions, corner normals and UVs, and draw indices. `--game-root` verifies original encoded image hashes, source BGRA hashes, and any byte-identical aliases. The command uses the existing decoder and pose convention. It needs no D3D9 device, Remix runtime, or new transport.

The verified fixtures are the Bird-of-Prey in `20261104-060904-042345-in-game/gpu/assets/1` and the four `piece-*` directories in `artifacts/player-replacement/break-replay-20261107`. The reader verified 20,466 corners across five assets and 26 pose samples. It compared primary upload bytes against source images using the declared orientation. Original group filenames survive deduplication, and the reported source pixel hash uses top-row-first source pixels. Secondary associations preserve the recorded role evidence. The historic fragment record shares a parent epoch, so distinguish pieces by session, parent/visual epoch and piece index. Its pose ordinals do not establish shared game frames. The fixtures have no matched damage, light or retirement records. No such state is inferred from an absent row.

Existing regressions exercised shared assets, offscreen movement and retirement separately. A reader check accepted the real ship, then rejected a cross-session manifest and missing image. Eighty-four focused Python tests passed across scene handling, offscreen motion, damage, lighting, debris and lifecycle, plus three production dependency tests. The merged alpha archive hash remains `b6de54b43a9c6870fbb1f5849b25c5951a8e749d8d7d2f567623bbc92493a77d`.

## Run169 transient effect

Reparsed the exact 16 MiB trace and verified its archived SHA-256. It establishes 122,820 four-corner submissions and a scoped `fx0.bmp` resource association. The polygon records contain count, flags and association, with no vertex bytes or downstream effective-state record. The selected polygon call at `0x006ACE8A` is before clipping. On the pinned executable the subsequent path can clip or reject the quad before issuing the native draw, and the draw path can flush earlier work. Consequently the sequence of polygon calls is insufficient to reconstruct effective draw order.

`start_effect_resource_session.ps1 -Quad` extends the existing copied-game observer with up to 16 sampled preclip quads, one per observed effect scope, and records the native return separately. Each sample has four indexed 64-byte corner records, a scoped texture association and trace order. This preserves source evidence for later interpretation. It does not label those values as the effective downstream vertices or prove a render-target frame join. There are no bulk model or texture dumps, rendering-thread waits or additional hooks. Normal play does not enable the observer. The 90-second, 16 MiB trace and existing teardown checks remain in place.

The x86 build, 45 native checks including slow-writer drops, injected fixture with real hook restoration, and read-only copied-game preflight passed. Fixture `effect-20261113-053110-656648` verified the corner payload and resource association with synthetic inputs. Next run the copied-game quad observation, verify which submitted corners survive and qualify the effective state, frame and order at native draw before any Remix replay. SFC-07 remains open. No copied-game run was performed for this checkout.

## November 14 follow-up — copied-game checkout

Run `effect-20261114-044638-574960` completed the 90-second tactical window with quad sampling enabled. The 15,744-byte trace matches SHA-256 `78bf5b2eac3ffb951f4c51c6d2211a49a01607ddf11806138120f214ad1f1846`. It retained 68 births and 52 retirements across the observed effects list and counted 88,213 unscoped finalizer calls. No selected `tFx_Drone` draw scope entered, so there were no eligible quad records. This cannot establish whether drones were launched or whether they were drawn through a different path. The sampler had zero drops and zero reported native faults. Both the tactical gate and observer stopped cleanly, the game exited normally, and protected files and launcher settings matched their pre-run values.

For the next targeted run, use a ship with drone racks and launch several drones while both ships are in view. If drones were already visibly drawn during this run, first investigate why dispatch missed the selected scope. Effective state, frame and order remain open.

## November 14 drone rerun

The sponsor confirmed drones in `effect-20261114-050417-962897`. The trace retained 101,435 complete records in 12,983,808 bytes (SHA-256 `a0252941c46cee801ffb49667a9c6952504f10370a0acd7f3b11e820ac0aebfb`). All 16 sampled quads contain four indexed preclip corner records, a scoped `assets/textures/fx0.bmp` association and native return `1`. They span three `tFx_Drone` owner epochs. The 16-sample limit was reached. An opt-in offline parser recovered the records and marked the result partial. The launcher still uses strict analysis, and the raw trace is unchanged.

The observer file retains its initial header and has no stop or statistics record. The separate tactical gate unloaded, the launcher recorded the copied game exiting with code 0, and protected files and settings matched. Observer teardown and drop totals are unverified. The saved corners establish input to clipping. The next missing link is the effective native draw, including which corners survived, the sampled atlas cell, blend/depth/cull state and source-frame order. Resolve that link before attempting a Remix replay.

The sponsor also saw fighters in both November 14 runs. The same fighter model appeared several times, and the number of visible copies decreased as the fighters took damage. This is a gameplay observation for SFC-22. The drone quad samples do not establish how SFC chooses the fighter copy count or submits those copies.

## November 14 downstream trace

Read the two 32-bit float fields at corner offsets `0x2C` and `0x30` as U and V. The native batch builder copies from corner offset `0x14`, and the recorded values match the independently recovered variant-3 bounds and corner order. Samples 1, 2, 10, 12 and 16 match the main quad's U192–255 and V128–191 on the 256-unit atlas grid. The other eleven cover U66–76.5 with interpolated V129.9844–141.8906, consistent with one half of the variant-3 segmented trail strip. These are source UVs. The native upload orientation and the postclip samples still need verification.

The pinned executable routes the polygon through clipper `0x006B8190`, rejects output with fewer than three corners and performs a face test, then dispatches via manager slot `+0x184` to batch builder `0x006AB410`. That builder can flush the *preceding* batch before appending the new geometry. Flush `0x006AB380` calls Device3 indexed drawing at `0x006AB3C0`. A draw seen inside the source scope could therefore contain earlier geometry. A draw that contains the sampled quad could also occur after the scope closes.

Use one main quad for the next observation. Associate the sample with the clipped polygon and the exact index span appended to its batch. Carry that association to the indexed draw and record its success, native scene/target identity and order. Observe the actual texture binding and effective blend, depth and cull state at that draw. Use the existing survey path for translated state and frame observations where an exact join is possible. Reject ambiguous joins and retain native drawing. Raw vertex equality alone is insufficient when clipping or batch packing rewrites vertices.

The runner now checks for game exit while waiting for the observer to close. If the game exits first, it reports the game exit separately and tries offline partial recovery. A failed observer still fails the run. The last record in the drone rerun was about 115.1 seconds after observer startup. The file never got a finalized header, so the exact reason shutdown did not finish remains unverified.

All 44 pinned-client anchors passed. Seven Python parser tests passed, including strict rejection and explicit partial recovery of an unfinalized trace. The injected synthetic fixture and read-only copied-game preflight passed. The game-exit change awaits live verification. No downstream capture or replay was performed in this increment.

## November 14 batch observer checkout

`-Batch` selects one four-corner main-quad candidate from the documented atlas column. At the verified postclip enqueue, it records the appended index span. A preceding flush inside enqueue resets the span origin. At the later flush, it reads only that span's 16-bit indices and referenced 32-byte vertices, plus Device3 readback status for the texture, render target, render state and texture-stage state. The next engine Present result is joined on the same manager and thread. The probe restores hooks and closes the trace after the matching Present attempt or at the original 90-second deadline. The existing 16 MiB cap remains. The probe observes arguments immediately before the pinned indexed flush and cannot report the Device3 draw HRESULT, GPU pixels, or native texture upload orientation. No production or Remix path consumes the records.

The strict x86 build, 45 native checks and seven parser tests passed. The injected batch fixture `effect-20261114-054145-418985` verified a preceding flush, all six selected indices and packed vertex values, subsequent engine presentation and restoration of all nine hooks. The synthetic fixture does not use a real Device3. Read-only copied-game preflight passed. Live qualification remains open.

Run from the existing elevated PowerShell session. Enter a skirmish with a drone-equipped ship, fire several drones, keep them visible, and exit normally after the two beeps. A successful sample may end the observation early.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\effect_probe\start_effect_resource_session.ps1" -Batch
```

### First two batch gameplay attempts

Runs `effect-20261114-054250-609347` and `effect-20261114-054418-333600` both stopped at ship loading. The tactical gate reported `component_state=removed` and `hook_bytes_restored=false` and never reached the unload step. Its controller checks the original bytes at `0x006AB410`, which the batch observer had already detoured at startup. The runner correctly withheld arming. Neither run supplied a drone draw. Both copies and launcher settings matched their pre-run hashes.

Batch mode now opens its trace and reports passive startup first. It attaches its hooks only after the runner confirms tactical-gate restoration and unload. The fixture checks all nine target byte sequences during the passive interval, observes a real enqueue-hook attachment after arming, and verifies final byte restoration. The controller's original validation is unchanged. Rerun the same `-Batch` command for live confirmation.

### Live batch retry

Run `effect-20261114-054810-983411` retained 71 records in 9,216 bytes (SHA-256 `088b633f4bf31317b80b6a4468e23d7de2c9472b698239c900e3f5a963409d19`) with zero drops. The tactical gate restored its bytes and unloaded. The observer stopped on its first match 40.39 seconds after arming, then restored its hooks and finalized the trace. SFC exited with code 0. Both game installations and launcher settings passed unchanged checks.

The selected `tFx_Drone` main quad contributed index span 0–5 of native indexed flush 403812 and was the entire batch. Four pretransformed vertices produced triangles `0,1,2` and `0,2,3`. UVs retained U0.75–0.99609375 and V0.5–0.74609375 after clipping. The stage-0 texture pointer matched the live resource snapshot for `assets/textures/fx0.bmp` within the run. All 23 native state readbacks succeeded. Blending was enabled with ONE/ONE. Depth testing used LESS_EQUAL and writes were disabled. There was no face culling, alpha testing or color keying. Stage 0 modulated texture and diffuse color, with linear min/mag filtering and no mip filtering. The same manager and thread reported a successful engine Present at ordinal 2416.

This qualifies the captured native batch and state for offline decoding. The Device3 draw return code, native image upload orientation and GPU pixels remain unobserved. No repeat of this observation is required for the same fields.

### Offline native draw reader

```powershell
python -B tools/effect_probe/capture.py artifacts/remix-runtime/runs/effect-20261114-054810-983411/effects.bin
```

The reader decoded the saved native vertex layout as screen X/Y, depth, reciprocal W, packed ARGB colors and source UVs. It preserved all six batch indices and identified four unique vertices. It recovered the recorded render state and stage-0 state under named keys, preserving their native values. The reader requires the bound texture to match the scoped resource snapshot, all native state reads to succeed and a successful engine Present. Trace hash, owner epoch, scope, flush sequence and engine Present ordinal provide within-run provenance. Eight parser tests passed, including a mismatched texture, inconsistent repeated vertex and an unfinalized trace. No graphics device or runtime is needed.

Native atlas orientation and the Device3 draw result are explicitly unknown in the JSON. The next replay comparison needs native atlas orientation and a reference for visible output. The data is ready for independent inspection while production continues using SFC's original drone path.

### Retained-frame interface check

The existing version-3 retained frame has owner rows, camera state and damage. It has no transient draw fields. The standalone fixture reads a retained frame through `multi_scene::read`, the same function used by the D3D9 adapter, and acquires one optional 1,216-byte transient companion. The companion preserves captured screen-space vertices, batch indices, run-local texture identity, native render and sampler values, trace SHA-256 and the native draw/Present ordinals. Its adapter association is a separate session/frame/sequence/checksum key. Only the fixture pairs the recorded drone with a synthetic retained frame. No live association between engine Present and the adapter frame has been demonstrated.

The single-slot fixture uses atomic ownership for copying. A busy slot drops the offer and an obsolete or incomplete companion is rejected in one attempt. No production mapping offsets, frame format, adapter behavior or alpha package changed. Native upload orientation belongs to eventual pixel replay and remains deferred by scope. The current check concerns captured data and interface admission.

Strict x86 and x64 builds passed 120 checks each with the saved drone payload. The fixture verified byte-for-byte transfer, wrong session/frame/sequence/checksum rejection, incomplete geometry, producer contention and a slow consumer missing a superseded draw. Eight effect-parser and nine multi-scene Python tests passed. No game or renderer was started.

### Native scene boundary

The production frame counter advances at M1's engine begin hook (`0x0069E300`). The retained cohort is published at the first qualified semantic wrapper, before later native effects are necessarily available. The isolated `-Batch` probe now also observes engine begin. A successful begin starts a scope for its graphics manager and thread. An intervening begin invalidates unflushed or unpresented evidence. Flush and Present records carry the same observer-local scene ordinal, and the parser rejects disagreement. Historical records used zero and remain decodable with an unknown ordinal.

The observer ordinal is run-local evidence, with no numeric equivalence to M1's frame counter. The real association still requires observing the retained-frame key and selected draw in the same session. The new marker is loaded only after the tactical gate unloads. Normal rendering, production frame publication and the D3D9 adapter have no changes in this increment.

The strict x86 build, 45 native checks, eight parser tests, injected fixture `effect-20261114-181027-363561` and read-only copied-game preflight passed. The fixture checked a failed begin and a different manager's Present. The previous live trace still decodes with an unknown scene ordinal. The next copied-game check uses the existing `-Batch` command above.

### Live scene-marker checkout

Run `effect-20261115-042802-299367` (November 14 Eastern) retained 92 records in 11,904 bytes, with zero drops and SHA-256 `42071956eff345e1be70c8756e68ef503ab895e162862a84ba4a3a4a692de0ea`. The offline reader verified one main drone quad for owner epoch 2, with six indices, the `fx0.bmp` binding and all 23 state readbacks. Flush 381131 and successful Present 2270 both carried scene ordinal 2269. The observer stopped after the match, 37.95 seconds after arming. The tactical gate restored its hooks and unloaded, the effects trace finalized without issues, and SFC exited with code 0. Protected installation files and launcher settings passed the unchanged checks.

This verifies the native scene marker for one observed draw. The adapter frame key was outside this observation. A live consumer association requires a same-run observation of the retained-frame key and the selected draw.

### Retained-frame join verifier

The worker-side verifier requires three independent stamps from one session. The retained-frame publisher stamps its actual publication. The draw observer stamps the selected native flush and the successful engine Present. Each stamp carries the exact session/PID/thread/manager/frame/sequence/checksum, scene-start tick and observation tick. The verifier requires identical identity fields, ordered timestamps and an exact retained packet read through `multi_scene::read`. It also checks the packet's source-thread fields. The observer and game Present ordinals are independent evidence and are never used as retained frame numbers.

The 32-bit and 64-bit tests each passed 133 checks with the saved drone packet and synthetic retained-frame observations. The join rejected a failed Present, different frame, thread, manager or session, changed scene-start tick or sequence, inconsistent timestamps, wrong checksum, a different source thread and an in-progress ring slot. Seventeen focused Python tests and OpenSpec validation passed.

The existing `-Batch` observer runs independently and shares the scene-begin hook address with M1. For the final capture, M1 must remain the sole owner of that hook. Collect the authoritative key at retained publication and carry it through the selected native flush and Present, then run the worker check using the actual retained packet. That wiring and one successful copied-game run remain before closing the drone interface proof. Pixel replay, BMP orientation and Remix submission remain deferred.

### Same-run join checkout

The `-Join` launcher prepares a private scene mapping and an isolated M1 producer build. M1 owns scene begin and publishes its stamp only after committing the retained frame and its matching notification. The observer checks the authoritative source frame at the selected draw's submission, flush and successful Present. The worker uses the existing D3D9 frame reader, then saves one retained frame and its receipt. This path performs no renderer submission or suppression. The observer detaches before the producer controller verifies restored bytes and unloads the producer.

The strict x86 observer and isolated producer builds passed. The injected fixture `effect-20261115-045048-654568` exercised shared mapping, exact frame 42, capture, receipt validation and observer cleanup. It used a synthetic publisher. Copied-game preflight passed. The live run still needs to verify the actual M1 publication, same-run join and coordinated teardown.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Project\SFC-Modernize Engine\tools\effect_probe\start_effect_resource_session.ps1" -Join
```

Enter a skirmish with a drone-equipped ship. After **Retained frame source ready**, fire drones and keep them visible. Exit normally after the two beeps. Leave the game on its native graphics path.

### First live join failure

Run `effect-20261115-051206-842179` (November 15 Eastern) verified and launched the copied game. The producer reached tactical view and wrote one fresh asset. During anchor selection the Python runner tried to resolve `InterlockedCompareExchange64` through Kernel32 and raised an exception because that export was unavailable. The effects trace retained only its initial header, with no drone or retained-frame receipt. The runner timed out waiting for the observer to close, and the controller reported that SFC exited before controlled removal. The sponsor reported a hard freeze. The run ended after 30.72 seconds. Both protected installation snapshots and launcher settings matched. No associated Windows application-hang event was found in the queried interval and the running process had already exited.

The confirmed runner defect and the in-game freeze have different evidence. The diagnostic M1 worker now selects the initial anchor from a matching asset-transfer acknowledgement using the compiled native atomic. The runner waits for a checksum-valid retained frame before arming the observer, and retains the last observed hook phase even if the trace cannot close. The freeze's stack and cause are unknown. Isolate the producer and the observer lifecycle before repeating the full joined drone run.

Use `-JoinProducerOnly` for the next copied-game check. This uses the same diagnostic M1 producer, confirms the exact retained-frame reader sees at least 120 source frames of progress, and requests controlled producer shutdown. The drone observer stays passive from launch through exit. No drones are required. A clean result will establish producer startup and shutdown independently of the drone hooks.

### Producer-only checkout

Run `effect-20261115-052100-621049` completed with verified retained frames 19 and 139. The producer reported 141 pose publications and zero failed updates or calibration misses. The observer remained passive. The controller restored the hook bytes and unloaded the producer, SFC exited with code 0, and both installation checks and launcher settings matched. This qualifies the revised producer startup and removal independently. The hard freeze from the first combined attempt remains unattributed.

The next test uses the revised `-Join` command above. It waits for a valid retained frame before arming the drone observer, then reports the observer hook phase if startup or shutdown fails. The combined proof still needs one exact drone frame receipt and clean teardown.

### Live join checkout — frame verified, texture name missing

Run `effect-20261115-054316-072475` captured a four-corner drone batch with six indices, 23 successful state readbacks and a successful engine Present. The native verifier saved retained frame 863, sequence 851. Offline review independently checked the packet size and checksum, session, PID, ordered timestamps and matching render thread, graphics manager and source frame against the flush and Present records. Retained publication preceded the engine Present observation by 10.02 ms in this sample. The packet SHA-256 is `3c8cbdba970434fcfc3b0200137776342c8d04e92c35d2a3d84e57c36472b7d9`.

The trace finalized with 109 records, zero drops, zero active observer callbacks and a detached observer. The controller restored the producer hooks and unloaded it. SFC exited with code 0, and the accepted and copied installations and launcher settings passed the unchanged checks.

The report is correctly partial for texture provenance. It contains 12 resource snapshots and zero filename records. The native batch retained the surface identity, but this run cannot resolve its filename. The runner skips offline receipt verification whenever the trace has any issue, which also reports the frame join as unverified despite the saved and independently checked receipt. The observer worker can skip resource-name resolution for queued observations when batch completion enters shutdown before the worker drains them. This ordering fits the trace. Qualify that path in the diagnostic fixture before requesting another gameplay run. Keep frame verification independent of texture qualification and retain the stricter requirement for any complete draw admitted to a consumer. No pixels or Remix submission were tested. The Obsidian CLI could not connect to the desktop app, so its tracker update is pending.

### Final resource drain qualified offline

The forced-stop native fixture queued a resource record while the writer was paused, then stopped and disarmed the observer before resuming the writer. It initially finalized without filename records. The revised worker detaches hooks, then completes resource resolution for accepted records before closing the trace. It still rechecks the registry entry and surface and counts any loss under the existing bounds. Filename resolution remains on the diagnostic worker.

Receipt validation now runs independently of texture completeness and checks the recorded thread and manager as well as session, process, frame, sequence, packet checksum and observation order. Replaying the previous gameplay files verified frame 863, sequence 851, with the missing texture still partial. A mismatched thread was rejected. The strict x86 build passed 53 native checks. The injected quad, batch and retained-frame fixtures and the copied-game read-only preflight passed. Eight parser tests passed. The joined fixture is `effect-20261115-160136-203893`.

Use the same `-Join` launcher above with a drone-equipped ship. This final gameplay check needs the bound filename, indexed draw and retained-frame receipt together, followed by clean teardown. Remix rendering and pixel replay remain outside this check.

### Final live drone checkout

Run `effect-20261115-193534-701604` verified one main drone quad with the actual `assets/textures/fx0.bmp` surface binding, four unique vertices, six indices and 23 successful state readbacks. The draw on source frame 800 and successful engine Present 782 matched the retained-frame receipt for frame 800, sequence 789. The offline reader independently validated the draw and receipt and encoded the 1,216-byte companion payload. The engine Present counter is distinct from the source frame ID.

The observer finalized 71 records in 9,216 bytes, with zero drops and no reported issues. Trace SHA-256 is `68B1B33CDADAA95D7E3D5F05318D41FD793CEA2AC3DFE044C79683A2F0CCAEAE`. The observer detached, the retained producer restored its hooks and unloaded, and SFC exited normally. Both installations and launcher settings matched. This completes the live capture proof for the sampled main drone quad. Native atlas orientation, pixel replay and backend submission remain open.

### Offline atlas orientation candidates

The accepted and copied `fx0.bmp` files match byte-for-byte, SHA-256 `d12dd3b782d99772914b81fea810927339e8b62420b323c727b2505b4b84e915`. The BMP stores a 256×256, 8-bit, uncompressed indexed image with positive height and bottom-up file rows. A bounded static follow-up on the pinned executable followed registry acquisition at `0x0040EEDD` through population at `0x0040F015` to manager texture creation at `0x006A8E50`. One branch starts at `base + (height - 1) × pitch` and negates the pitch before constructing a temporary image. The saved trace does not identify which upload branch or source row order reached the bound surface. The BMP file row order alone does not establish that relationship. [Microsoft DIB layout](https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-bitmapinfoheader).

The offline candidate comparison sampled the exact captured screen positions and UVs, with bilinear filtering and an isolated black destination. It used the documented D3D9 transformed-vertex pixel-center convention as a replay assumption. All four vertices had constant depth, reciprocal W and white diffuse. The raw-V candidate on a top-down decoded atlas is orange, while the `1−V` candidate is purple. They differ at 450 of 552 modeled pixels. At screen coordinate (1062, 823), the respective candidate RGB values are (199, 53, 0) and (230, 81, 234). Images, script and JSON are local at `artifacts/effect-probe/fx0-orientation-20261115/`. [Microsoft transformed-vertex sampling](https://learn.microsoft.com/en-us/windows/win32/direct3d9/directly-mapping-texels-to-pixels).

The archived observation contains no captured pixels from the selected draw or bound texture. Use the two candidates to compare one native image of a visible main drone quad. A screenshot against a dark background can distinguish the color and atlas cell. A same-draw crop or matched target samples are still needed for numeric pixel parity. Keep the raw UVs unchanged pending that result. No game was launched or renderer path changed.

The sponsor recalls using fast drones in the checkout and seeing them as purple. The sponsor identifies orange as slow, blue as medium and purple as fast. This gameplay recollection favors the `1−V` candidate for the sampled main quad. The trace did not record speed class or pixels, so a matched native sample is still needed for confirmation and pixel parity. Do not generalize this candidate to other atlas cells or effects.

### Medium-speed atlas cross-check

The sponsor reports medium-speed drones for `effect-20261115-194836-810369`. The saved trace independently verifies a main quad bound to `fx0.bmp` on retained frame 751, sequence 740, with 71 records and zero drops. U remained `0.75–0.99609375` while V advanced from the previous `0.5–0.74609375` to `0.75–0.99609375`. On the decoded BMP, `1−V` selects the blue circular glow at column 3, row 0. Raw V selects the repeated silhouettes in row 3. Together with the earlier purple fast-drone report, this is strong evidence for using `1−V` as the replay candidate for these main quads. Pixel parity remains open. The local atlas crop comparison is `artifacts/effect-probe/fx0-medium-20261115/speed-atlas-cells.png`.

SFC exited normally and teardown passed. The run reported a copied-install configuration change. Comparison against a byte-for-byte match for the pre-run INI hash found only the `PlayerName` value changed in `sfc.ini`. The asset trace and frame receipt verified independently.

### Standalone D3D9 drone replay

The diagnostic runner checks the exact recorded state, `fx0.bmp` hash and quad topology before passing the original vertices and indices to the D3D9 fixture. It translates screen XY by an integer offset into a 48×48 render target and retains the original positions in the capture. The fixture samples the decoded atlas with raw V and `1−V` as separate controls. It uses an ordinary Windows D3D9 HAL device and an isolated RGB8 color and depth setup without MSAA, sRGB conversion or game layers.

The medium capture (frame 751, sequence 740) rendered blue with `1−V` and differed from the raw-V control at 471 pixels. The earlier fast capture (frame 800, sequence 789) rendered purple with `1−V` and differed at 450 pixels. Both draws stayed inside their recorded screen footprints. The largest RGB channel difference from the independent bilinear CPU calculation was less than one 8-bit level. A nonblack clear verified saturated addition. A nearer depth clear rejected the draw, and a second draw at a farther depth still added color, verifying depth writes were disabled. The strict x64 build and eight existing parser tests passed.

Build the fixture from an x64 Visual Studio developer prompt with `cl /std:c++20 /EHsc /W4 /WX tools\renderer_diagnostics\replay_drone.cpp /link d3d9.lib user32.lib`. Use `replay_drone.py <trace> <fx0.bmp> <replay_drone.exe> <new-output-directory>` with the repository's Windows Python and Pillow. The readbacks, images and reports are local at `artifacts/effect-probe/drone-replay-20261115/medium/` and `fast/`. No game or Remix runtime was started. The next comparison needs pixels from the native draw to qualify real-scene parity and wrapper color or MSAA differences.

### Native pixel capture route checkout

An isolated x86 fixture used copies of the verified game's dgVoodoo DLLs and configuration. It created a 48×48 DirectDraw4 render target and a Device3 HAL scene. A one-pixel read-only `Lock` with `DDLOCK_DONOTWAIT` recovered the correct clear and drawn colors, but the calls took 6.09 and 12.63 ms while the scene was open. That timing rules out using these locks around the in-game draw. [DirectDraw lock behavior](https://learn.microsoft.com/en-us/windows/win32/api/ddraw/nf-ddraw-idirectdrawsurface7-lock).

Preallocated video-memory destinations successfully retained the same clear and drawn colors across the single draw. Across four runs the two `DDBLT_ASYNC | DDBLT_DONOTWAIT` copy submissions took 0.04–0.45 ms. Reading immediately after `EndScene` still incurred a 17.73–22.12 ms first-copy lock. A 75 ms delay in the offline fixture reduced that first lock to 3.32–3.78 ms across three runs. This delay was a fixture control. The timestamps show a useful separation between enqueue and CPU readback, but do not qualify render-thread CPU locking or the game's real target format, size or multisampling. The probe sources, wrapper copies and timing logs are under `artifacts/effect-probe/native-pixel-20261115/`.

The remaining work is to qualify a completion-aware pixel readback on an isolated boundary before connecting it to a copied-game test. Accept a single exclusive drone batch only and compare a small matched pre/post region. Use the existing frame receipt for association. A busy or unsupported capture path must leave the underlying draw alone. No SFC session or Remix runtime was started for these wrapper tests.

### Completion-aware readback and remaining target join

`GetBltStatus(DDGBS_ISBLTDONE)` returned success for both private DirectDraw copies in three trials, but the first read-only lock still took 15.04–20.78 ms. The status result cannot qualify a nonstalling CPU read on this wrapper.

The x86 ReShade observer recorded D3D11 device and command-list initialization, but no visible draw event for the fixture's Device3 indexed call, even with a primary-surface blit. A D3D11 event query and nonwaiting staging map completed, but copies issued immediately after `DrawIndexedPrimitive` or `EndScene` still read the clear color. The wrapper had not submitted the indexed draw in the expected D3D11 order. Fence completion only verified the queued copies.

Bracketing the Device3 draw with private DirectDraw blits before staging the original, explicitly retained D3D11 texture yielded correct clear and drawn pixels. Across three repeated passes, the blits took 0.04–0.14 ms and each map after the GPU query took less than 0.004 ms. The isolated texture was RGBA8 with 8×MSAA. The blits changed the bound RTV, so the most recently bound view cannot identify the game draw's target. The tagged private scratch-surface test also yielded no matching ReShade creation event. Fixture sources and receipts are under `artifacts/effect-probe/native-pixel-20261115/`, especially `status-probe.txt`, `translated-pixels.txt`, `translated-endscene.txt` and `ordered-repeat.txt`.

The missing live link is the exact D3D11 texture and subresource corresponding to the `IDirectDrawSurface4` used by the selected native batch. Qualify the association across target switches and reject ambiguity before connecting this method to the copied game. The controlled fixture knows its source. A matching size, format or current RTV alone is insufficient in a live scene. No gameplay runner, Remix integration or shipped component was changed.

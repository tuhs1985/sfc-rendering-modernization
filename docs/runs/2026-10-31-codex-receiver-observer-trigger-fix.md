# Run249 — standalone reproduced stall; trace observer missed window

Sponsor executed Run248 observer. Evidence folder `artifacts/player-replacement/run248/trace-20261101-034013`,fixture `20261101-034016-536946-return-fixture`.

Fixture itself passed600frames,pixel/depth/text checks,zero state errors,child/host exit0. Receiver CreateProcessW again blocked5001.8548ms. **No ETL was recorded:** trace-result.json says trace_saved=false,error="No trace window captured". This does not invalidate the runtime reproduction,but supplies no kernel cause evidence.

## Diagnostic defect and correction

Observer used gate/run-metadata.json to discover the existing session. That file is written when fresh tactical assets arrive(CreationTimeUtc03:41:20),after the renderer has waited most of its60-second menu interval. It then started a new50-second readiness countdown from observation time;fixture ended before that countdown completed.

The fixture manifest.json exists before renderer launch(CreationTimeUtc03:40:19)and already contains semantic_calibration.scene_session. Observer now attaches through that early identifier and calculates elapsed readiness from the native cell's actual QPC timestamp,not the time the file/flag is first noticed. It rejects malformed session/clock data and fails explicitly if activation already occurred before trace start. A small observer.jsonl records mapping attachment,readiness age,activation and trace start so timing defects will be visible.

Checks:Python parser;session extraction against this actual fixture's early manifest;native-ready age0/50seconds;invalid backwards clock rejection. WPR profile/PowerShell parser unchanged and previously accepted. Live elevated recording still requires sponsor checkout;no false claim of end-to-end trace qualification.

Failed run receipts remain unchanged;controller correction is described above. Corrected script stays artifacts/player-replacement/run248/trace_receiver_startup.ps1(the Python controller behind it changed). No production startup/rendering/material/security changes. No extra GPU run performed by agent. Current token still lacks Windows kernel profiling permission.

Verified lossless closed-texture archive restores416MiB reservation needed by the standalone fixture+trace. See run249/texture-archive-receipt.json. Original geometry/logs/captures preserved;20GB allowance unchanged.

**Next:** repeat the same prepared command once from the existing Administrator PowerShell. No SFC/gameplay action. Inspect observer.jsonl and trace-result.json before any further request;a fast launch trace also provides valid comparison evidence. Changes unstaged/uncommitted.

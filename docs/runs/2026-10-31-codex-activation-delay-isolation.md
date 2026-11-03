# Run240 — activation-delay isolation

Sponsor resumed the parked startup investigation. No SFC gameplay launched; no appearance, capture, suppression, capacity or material policy changes.

## Archived comparison

Read-only comparison of activation-file and renderer-ready timestamps with native startup QPC markers shows the same approximately 5.6-second activation interval in four-owner, five-owner and 26-owner gameplay sessions. Six- and eight-owner sessions observed activation in approximately 11–12ms. This predates the latest fleet-capacity changes and is not proportional to scene size. File timestamp/QPC alignment is an estimate, not a direct single-clock publication trace.

The stress session's initial bases/enhancements were ready under a second and the renderer was already warm. Later unique KCA/KCL admissions took approximately105/75ms. This does not prove every asset can always be admitted that quickly.

## Standalone reproduction

`20261031-215707-695670-return-fixture`: actual pinned Remix1.6.1, existing native Strict three-owner fixture, 60-second synthetic menu idle, no SFC. Added bounded startup-profile markers only; no file access or allocation in SFC callbacks. Scene and activation matching unchanged.

The renderer detects activation and then spends **5.9508559seconds inside the existing bounded activation-file read**, before reporting `activation_read`. Checksum/identity validation and all six environment updates complete within approximately0.055ms afterward. The packet is104bytes. This localizes the delay before scene loading/drawing, not inside model production or GPU asset admission. Underlying OS/runtime cause inside the file-read operation is not yet established.

The actual600-frame fixture passed: three owners, two unique assets plus shared third, zero pixel mismatches and state errors, correct native depth/text, normal child exit. This is a diagnostic reproduction, not an improvement claim.

## Second reproduction: stream opening blocks

`20261031-215931-280933-return-fixture`: same standalone fixture and60-second idle. The activation-file stream constructor/open (including the existing binary/ate behavior) took **5.4993785seconds**. Size query,seek,104-byte read and close together took approximately0.0472ms. All activation checks/environment updates afterward were also immediate. This reproduces the stall twice with only three owners and localizes it to opening the control file,not model count,asset construction,checksum validation or GPU drawing.

The exact lower-level reason the stream open blocks (runtime/library lock,file-system interception or another OS wait) has not been sampled;do not claim a specific antivirus,driver or vendor defect. No lock bypass,security exclusion or settings change was attempted. The smallest corrective experiment is an in-memory activation ticket/notification using the existing bounded session bridge,retaining the same validation and startup ordering,or first compare a direct Win32 read to determine whether the stall belongs to the C++ stream path. Do not redesign asset preparation to work around this.

Second600-frame fixture also passed: three-owner pixels/depth/text,zero state errors,normal child exit. Both renderer job receipts report exit0 and remaining_owned_processes0. Pinned runtime teardown still prints its common-device-objects warning;exit0 alone is not proof of every internal vendor object being released. No SFC run or appearance changes. The only implementation edits are bounded external-host timing markers and equivalent explicit stream-read steps. No speedup/fix claimed. Build /W4 /WX and git diff --check passed.

Evidence: `artifacts/player-replacement/run240/activation_comparison.py`, `activation-comparison.json`; raw fixture logs retained. Changes unstaged/uncommitted. No automatic sponsor run required.

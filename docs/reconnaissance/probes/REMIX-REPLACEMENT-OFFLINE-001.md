# REMIX-REPLACEMENT-OFFLINE-001

2026-10-19. Executed OFFLINE;55checks per architecture PASS. No SFC launch.
See [contract](../ship-replacement-contract.md) and
[Run65](../../runs/2026-10-19-codex-replacement-depth-foundation.md).

Question: can an independently gated,unshifted returned ship respect native
8MSAA scene depth,write its own depth and preserve later UI/state?

## Configuration and reproduction

Windows11,RTX4070Ti,driver617.42;VS2026 18.7.3,C++20,/W4 /WX,/Brepro;
D3D11 hardware feature10_1. Synthetic64x64 color/depth/picking only,not Remix
rendering and not evidence of an in-game owner association. Both x86 and x64.

```powershell
& 'C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe' -NoProfile -File 'C:\Project\SFC-Modernize Engine\tools\remix_runtime\build_replacement_tests.ps1'
```

Generated binaries/objects/stdout/stderr only under ignored
`artifacts/remix-runtime/replacement-bin`. No proxy/DLL installation,registry
change,game patch,network fetch,Toolkit,Remix host or persistent service.
Each owned test executable has20s timeout;stdout/stderr checked<=2MiB each.
Timeout kill branch is configured but NOT deliberately exercised in this run.
Single tiny surface set;no ongoing captures or images written. Normal child exit
releases resources. No sponsor activity required for this offline probe.

## Acceptance exercised

- Valid exact-current admission;missing readiness/coverage/visibility/pre-UI/
  target evidence rejects. Stale/future timestamps and consumed sequence reject.
- Wrong owner/revision/session/PID/epoch/asset/object/pose/camera/frame/viewport,
  composed-state change,malformed key and nonfinite state reject.
- Existing offset/delayed diagnostic modes cannot authorize replacement.
- GPU pixel assertions:near scene occludes returned ship;returned depth occludes
  later farther drawing;nearer drawing/later depth-disabled UI covers ship.
- Full4096pixel comparison checks picking-ID coverage,legitimate black color,
  wrong-owner/background discard and NaN/infinite/negative/out-of-range depth.
- Native OM target/depth and IA topology survive composition. The implementation
  uses ExecuteCommandList(TRUE) for full state preservation;this fixture does not
  independently enumerate every D3D11 state slot.
- Null depth,mismatched dimensions/viewport,wrong input format,offset mode and
  unsupported single-sample native target decline. Cross-device rejection exists
  in code;not separately exercised with a second native device here.

Passing does not license in-game suppression. Real owner-boundary timing,
batching,UI/effect order,lifetime/disconnect,resize/device-loss integration and
stationary/moving replacement still need their actual integration evidence.

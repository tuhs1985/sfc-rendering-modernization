# Alpha administrator-access assessment

November8,2026. Assessment only. Normal launcher policy and the private test
package are unchanged; no SFC launch or security-setting changes were made.

## Finding

Administrator access appears removable from normal alpha play when the launcher,
game and helpers run as the same ordinary user in a writable game copy. Current
elevation is explicitly enforced by our release wrapper and two Python admission
checks, inherited from the early elevated-parent observation workflow. The
underlying process/graphics operations do not independently request elevation or
enable SeDebugPrivilege. Full non-admin SFC gameplay is not yet qualified.

## Current gates and dependencies

| Area | Evidence | Assessment |
| --- | --- | --- |
| Release wrapper | `tools/release/launch.ps1` uses RunAs whenever not admin, except preflight | Our policy, not a failed Windows capability check |
| Normal coordinator | Two IsUserAnAdmin checks in `run_return_game.py` reject execution | Our policy; retain until a distinct non-admin checkout |
| Native preload | Existing Detours CreateProcessWithDllExW creates our own child; native preflight already runs without elevation | No separate admin request in native launcher |
| Semantic controller | OpenProcess requests create-thread/query/VM-operation/read/write/synchronize; actual controller helpers allocate/write/read and load/unload a DLL | Same-user operations pass the unelevated owned-child test below |
| IPC/GPU | Local current-user mappings/events; ordinary D3D/Vulkan/Remix APIs | No SeDebugPrivilege, global mapping or service installation identified |
| Graphics transaction | File creation/replacement in the tester's own copy | Ordinary user must have write/delete rights. A protected Program Files installation is not the appropriate default alpha destination |
| Elevated target | Controller at lower integrity cannot assume access to an already elevated SFC | Start the whole normal-play chain consistently; report a mismatch rather than silently changing policy |
| Kernel tracing/profiling | ETW/kernel discovery tools have separate elevation requirements | Diagnostic toolset, not normal-play prerequisites |

Read-only registry inspection found no RUNASADMIN compatibility layer for the
private checkout or existing development test copy in HKCU/HKLM. The accepted
installation's entries contain only DWM8And16BitMitigation. No entries changed.

## Actual standard-user checks

`tools/release/privilege_probe.cpp` compiles x86 and includes the production
controller implementation with its entry point renamed. It calls the actual
`remote_string`, `remote_kernel_proc` and `remote_call` helpers against its own
disposable x86 child. The production SFC identity guard is not bypassed or run;
this probe never targets SFC.

After the child signals that startup is complete, the test proves:

- Parent and child tokens both report elevated0.
- The exact production OpenProcess mask1049658 is granted.
- Remote allocation, write/readback, LoadLibraryW and FreeLibrary succeed.
- The returned module base matches a separate module enumeration.
- Only the owned child is terminated/drained afterward; no helper remains.

Initial exploratory attempts ran before child readiness and returned an access
violation from the remote loader call; they do not establish an elevation
requirement. The qualified probe explicitly waits for the child's ready signal,
as the real pipeline already waits for game/component startup readiness.

Evidence: ignored `artifacts/alpha/privilege-assessment/result.txt`. Separate
ordinary-user file tests granted read/write handles to existing private-copy
graphics/configuration files without writing bytes. Disposable file creation,
replacement and cleanup also passed under that game folder. Evidence:
`artifacts/alpha/privilege-assessment/file-access.json`. Defender remains enabled;
no exclusions, ACL changes or privilege adjustments were introduced.

## Recommendation and next qualification

Make ordinary-user launch the intended alpha default after one scoped checkout.
Keep the existing elevated baseline available during that comparison. Change only
the wrapper/coordinator elevation policy for the checkout; retain exact hashes,
target/session validation, graphics transactions, same-user IPC and normal native
fallback. Require a writable game copy and reject elevated-target/access mismatch
with an actionable explanation. Do not automatically retry injection as admin.

Verify actual SFC startup, component attach, multi-ship replacement, camera/effects,
damage/destruction, early exit, immediate relaunch and interrupted restoration
from a confirmed standard-user parent. Review any game-owned registry/file access
failures before claiming non-admin support. There is no demonstrated need to
redesign the renderer, add a privileged service or disable Defender for this.

Microsoft references: [process access rights](https://learn.microsoft.com/en-us/windows/win32/procthread/process-security-and-access-rights),
[OpenProcess security-descriptor checks](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocess),
[CreateRemoteThread required access](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createremotethread).

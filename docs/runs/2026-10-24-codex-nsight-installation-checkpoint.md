# Run139 — official Nsight installer verified; OS elevation required

## Result

Profiler setup BLOCKED on actual Windows administrator token, not project architecture, credits, renderer feasibility or sandbox writable roots. No capture attempted and no performance conclusion added. User authorized installation with “Go” after Run138's installation request. Fuel Guard attached using current thread; no daemon/helper/agent.

Read current handoff and Run138. Preserve pinned Remix1.5.2, game/client assets, graphics driver and existing settings. HEAD `d40f8f230fc7504023e4a052c99a81b5a08ce6b4`, prior dirty work retained, index empty; no staging/commit/push. No implementation code modified and no new native build/test qualification claimed.

## Official source and downloaded installer

- [NVIDIA download page](https://developer.nvidia.com/nsight-systems/get-started) linked Windows Nsight Systems2026.5.1.161. Followed its official URL (not a guessed CDN filename): `https://developer.nvidia.com/downloads/assets/tools/secure/nsight-systems/2026_5/nsightsystems-2026.5.1.161-3889610.msi`, redirected to NVIDIA's download host.
- [NVIDIA installation guide](https://docs.nvidia.com/nsight-systems/InstallationGuide/) documents Windows MSI installation and recommends Program Files. [CLI guide](https://docs.nvidia.com/nsight-systems/UserGuide/index.html) documents Windows administrator requirement and process-directed Vulkan tracing; system-wide tracing is NOT authorized for this proof.
- `winget show --id Nvidia.Nsight.Systems` found no package. Search found Nsight Compute only, which is NOT a substitute and was not installed.
- Exact local installer: `C:\Project\SFC-Modernize Engine\artifacts\remix-runtime\deps\nsight-systems-2026.5.1.161.msi`,663,678,976bytes, SHA256 `379C0A15A9CF7B8028081073FDD1D9798B9AAA618FB46C6A01785B69ED01D5F2`.
- Windows Authenticode status Valid, signer NVIDIA Corporation. This was checked BEFORE execution. Installer is in existing ignored dependency cache, not a trace/evidence output directory; governed20GB capture allowance unchanged. No runtime dependency substituted.

Read MSI tables without modifying the package: ProductVersion26.5.1.161, ALLUSERS1. Features include core `QuadDMainFeature_x64` and optional VC redistributables. Requested core ONLY, no optional redistributables, no reboot and no GPU-driver installer. Did not force per-user properties or bypass launch conditions. A nonessential summary-table query failed with `OpenView,Sql`; feature/property inspection succeeded and the query changed nothing.

## Attempt and exact error

One normal signed MSI attempt, outside sandbox through approved execution, with `/qn /norestart ADDLOCAL=QuadDMainFeature_x64 /L*v <owned log>` returned1603. Execution outside the filesystem sandbox does NOT mean the Windows process token is elevated; explicit WindowsPrincipal check returned false.

Installer log (`artifacts/remix-runtime/deps/nsight-install-20261024.log`) reports:

```text
Setup requires Administrator privileges to install.  Please install using an administor user account. Application has not been installed.
Action ended 11:03:41: LaunchConditions. Return value 3.
```

Do not misread the generic MSI event “Windows Installer installed the product… Installation success or error status:1603” as success. No matching installed-program record or Program Files Nsight directory found afterward. Parent msiexec attempt exited; the remaining Windows Installer service process is an OS service, not an orphaned test process, and was NOT killed. No SFC/GPU fixture/profile started. No Windows Installer/UAC/security/driver policy altered.

Read-only machine check: RTX4070Ti, Windows driver32.0.16.1742; two existing virtual display adapters also present and untouched. Free C: space~229.8GB, so download failure/disk exhaustion is not the observed blocker. No unrelated process or file inspection was needed.

## Exact next action

User performs the one-time legitimate Windows elevation. This inline PowerShell command does NOT require enabling PS1 scripts; it requests Windows UAC approval, runs the already-verified core installer hidden, waits and prints its result:

```powershell
$p = Start-Process msiexec.exe -Verb RunAs -WindowStyle Hidden -Wait -PassThru -ArgumentList '/i "C:\Project\SFC-Modernize Engine\artifacts\remix-runtime\deps\nsight-systems-2026.5.1.161.msi" /qn /norestart ADDLOCAL=QuadDMainFeature_x64 /L*v "C:\Project\SFC-Modernize Engine\artifacts\remix-runtime\deps\nsight-install-elevated-20261024.log"'; $p.ExitCode
```

Afterward Codex verifies installation/CLI version and local help. Then prepare the fixed-duration, storage-reserved process-tree-only Vulkan capture described in Run138. Do not blindly launch a system-wide trace, request driver counter policy changes, start SFC or treat installation alone as a captured timeline. Windows CLI may also require an elevated parent; verify before promising unattended capture. If installation succeeds but capture privilege is absent, prepare a single bounded admin-parent launcher rather than changing Windows security policy.

Tests: installer signature/hash/feature checks and installed-state verification only. Existing488Python/native/render qualifications remain historical and unmodified, not rerun here. Repository validation: referenced installer/log/run paths exist; no code changes. Current handoff updated; older checkpoint preserved.

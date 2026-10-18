# Codex run — approved return-path execution, safely checkpointed

Date:2026-10-16 EDT. Sponsor explicitly requested implementation of the
"In-Game Remix Integration — Prove the Return Path" plan. Starting baseline:
e96765a,clean worktree/index confirmed before documentation changes.

Fuel Guard trusted warning reports five-hour allowance approximately0%. This
execution therefore records authorization and safely parks before any setup or
interception. This is a SESSION CAPACITY condition,not evidence of technical
failure or an infeasible return path. No runtime gate attempted or demonstrated.

## Approved execution scope and gates

1. Use a separate verified game copy;accepted Community Edition installation,
   launcher/client/assets/graphics dependencies must remain untouched. Freeze
   hashes/configuration/OS-driver-GPU/toolchain. Confirm launcher and discovered
   game process actually use test directory;abort on accepted-install path.
2. Pin matching official Remix SDK/runtime,not online-main headers combined with
   arbitrary installed DLL. Build minimal64bit runtime host,retain32bit SFC and
   existing semantic observer. Use existing bounded current-user communication.
   No Toolkit/ USD ingestion or repeated texture conversion in rendering path.
3. FIRST GATE BEFORE GAME HOOKS:render through runtime and demonstrate reusable
   GPU-side output transfer into standalone D3D11 consumer,with explicit resource
   ownership,synchronization and cross-process compatibility. Raw VkImage values
   are not exported handles. If unavailable,report precise missing capability
   and proposed alternative;no hidden CPU screenshot fallback,runtime patching,
   translator switch or unsupported success claim.
4. After first gate,default-off compositor in verified test presentation chain:
   256square animated REMIX image in tactical corner away from HUD;no original
   drawing suppressed. Preserve graphics state/proxy forwarding. Nonblocking fixed
   pool;omit late/missing/invalid output. Test resize/device loss/disconnect/normal
   exit,enabled/disabled/removed. Detached overlay/window is NOT in-game proof.
   Sponsor gameplay confirms HUD/cursor/controls/original rendering remain normal.
5. Only after return-image gate,qualify one-owner replacement:explicit asset,
   camera/transform,frame provenance/output validity. Existing30Hz asynchronous
   observer is NOT replacement-frame synchronization. Need owner-specific native
   suppression and correct coverage/depth/retained scene visibility. No black-key
   cutout/bounding rectangle. Suppress ONLY with matching ready output;otherwise
   original draws. Stationary first,motion only after correspondence proven.
   Unresolved weapons/shields/explosions/overlaps=>stop at return-path proof and
   report smallest missing relationship,not broad renderer reconstruction.

Bounds:existing scene transport;<=4 output surfaces,<=1920x1080,<=128MiB output
reservation;32MiB combined logs/warn16MiB,counters after saturation;90s tactical,
five-minute prepared workflow. No continuous image dumps. Existing elevated
parent,no routine UAC/security relaxation. One runner;human actions only actual
gameplay/visual confirmation. Tests before gameplay include slow/crashed renderer,
stale/invalid resources,exhaustion,resize/device loss/transfer shutdown,state
restoration and original regressions/hash checks.

Required artifacts:versionable integration contract,dependency manifest,probe
definitions/tests/runtime evidence,run record/HANDOFF. Archive useful evidence
without caches;no staging/commit automatically. No helper/subagent,appearance
tuning,full replacement/final architecture/aggregate gate claim.25s Toolkit delay
remains historical;measure actual runtime stages before optimizing them.

## Already discovered facts — verify, do not guess

Accepted config dgVoodoo OutputAPI=d3d11_fl10_1;prior loaded-module snapshot has
game-local DDRAW/ReShade DXGI plus systemD3D11. Accepted manifest remains authoritative.
SDK source documents Startup/CreateMesh/SetupCamera/DrawInstance/Present,
dxvk_CopyRenderingOutput(final color/depth/normals/object IDs/GUI),external
swapchain VkImage+semaphores. Interface existence is not cross-process/D3D11 proof.
Current online remix_c.h API0.6.5;NOT yet matched to installed binaries.
Installed C:/Project/RTXRemix/deps/remix_runtime/runtime/d3d9.dll is x86 bridge
(PE014C);Toolkit hdremix/d3d9.dll is x64(8664). Neither selected as compatible
host dependency. No source audit or DLL initialization performed this run.

Primary references:
- https://github.com/NVIDIAGameWorks/dxvk-remix/blob/main/public/include/remix/remix_c.h
- https://github.com/NVIDIAGameWorks/dxvk-remix/blob/main/documentation/RemixSDK.md
- docs/reconnaissance/live-scene-contract.md
- docs/reconnaissance/probes/LIVE-SCENE-001.md
- docs/runs/2026-10-16-codex-fresh-live-scene-runtime.md

## Execution result / restart

Documentation only:this record and new authoritative HANDOFF entry. No game copy,
download,dependency installation,build,runtime host,hook/compositor/game launch or
original file modification. No active process/mapping/tool state to recover.
Fuel Guard attach attempted with exact thread;no daemon spawned. Read Git state
and latest handoff;diff/path checks performed after edits. No test rerun claimed.
Final state:HEAD e96765a,index empty,new record/uncommitted HANDOFF only;no commit.

Exact next smallest action:read this authorization checkpoint and accepted
dependency manifest;perform read-only pinned SDK/runtime/output-sharing capability
qualification for the standalone64bit-host->D3D11 consumer gate. Then prepare
the isolated test installation as required;do not touch accepted install or add
in-game hooks until that gate passes. Resume approved execution without asking
the sponsor to repeat approval;stop only at its gate/blocker/runtime-test boundary.

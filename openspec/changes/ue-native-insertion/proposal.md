# UE rendering inside the SFC display

## Why

The packaged UE proof can render captured ships, original textures and the
recorded camera. The next objective is genuine UE output inside SFC, first
additively and then replacing one qualified player ship, while preserving
gameplay, native effects and tactical UI. The documented UE review identifies
prototype shortcuts to resolve before live input.

## What Changes

- Establish a packaged world-space UE runtime adapter with retained assets,
  separate camera/owner transforms, explicit lifetimes and optional diagnostics.
- Qualify built-in shared runtime geometry before committing to a mesh path.
- Qualify GPU-only UE DX12 to standalone D3D11 output using Epic facilities
  first, then public RHI/Windows facilities only for an identified gap.
- Connect the existing neutral source session to UE without Remix-specific
  image conversion or a new source refresh cap.
- Reuse native target discovery, output leases and insertion ordering through
  a UE output adapter. Keep ReShade/dgVoodoo at this stage.
- Demonstrate a textured offset ship in the game before enabling selected
  player-ship suppression at zero offset.
- Document independent source-interface and UE backend qualification. No
  stable public ABI or full-scene UE coverage is implied by this increment.

## Capabilities

### New Capabilities

- `ue-scene-consumer`: retained, world-space UE consumption of qualified SFC
  asset/frame state, including packaged operation and resource lifetime.
- `ue-game-output`: coherent UE colour/depth/owner output, GPU transfer and
  gated native insertion with a one-player replacement proof.

### Modified Capabilities

None. Existing Remix behavior remains the accepted comparison baseline.

## Impact

Proposed UE project/plugin source belongs under `src/ue_wrapper`, independent
of the preserved `src/ue5_proof` reference. Neutral receipt remains upstream
of D3D9. Existing session/coordinator, startup ticket, target notice, output
pool and native gate are reused behind explicit backend selection where
qualified. Any necessary interface extension is versioned and documented
without breaking the current Remix consumer.

UE 5.8.4 CL 58902052 stays pinned. No engine patch, new game renderer,
dgVoodoo/ReShade removal, D3D12 source adapter, appearance tuning or alpha
publication is included. This is a plan only. No implementation is complete,
and cross-API sharing remains a measured gate, not an assumed capability.

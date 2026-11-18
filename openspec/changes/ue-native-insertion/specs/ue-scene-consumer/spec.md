# UE scene consumer

## Purpose

Consume qualified SFC source assets and coherent live frame state in a packaged
UE application while preserving renderer-independent meaning and ownership.

## ADDED Requirements

### Requirement: Retained original assets and independent transforms
The UE adapter SHALL retain qualified original local-space geometry and image
associations separately from instance and camera state. It SHALL preserve source
corner attributes and rendering groups and apply only documented UE conversions.

#### Scenario: Camera changes while two owners share a mesh
- **WHEN** a coherent source snapshot changes the camera and one owner's pose
- **THEN** the adapter updates those transforms without rebuilding or reloading
  the shared asset, and the other owner keeps its own identity and pose

### Requirement: Session and world lifetimes remain distinct
The consumer SHALL use session/owner-epoch and asset-content/revision identity,
retain living offscreen owners, and invalidate retired or cross-session state.

#### Scenario: Recycled owner and delayed asset completion
- **WHEN** an old owner retires and its asset work completes after a new epoch
- **THEN** that work cannot revive or modify the new owner's instance

#### Scenario: World and consumer shutdown during pending work
- **WHEN** the world is recreated or the consumer stops while receipt/render work is pending
- **THEN** admission stops and owned work/resources drain before release without
  accessing destroyed scene objects or blocking the source capture callback

### Requirement: Packaged functional work is independent of diagnostics
Required loading and admission SHALL execute in Development and Shipping
configurations without enabled assertions. Normal mode SHALL omit image
readback, comparison scans, captures and automatic traces while retaining
cheap structural and memory-safety checks at input boundaries.

#### Scenario: Missing texture with diagnostics disabled
- **WHEN** an original image required by an asset is unavailable
- **THEN** the asset is reported unqualified without invalid memory access,
  assertion-dependent behavior or substitution with a different ship

#### Scenario: A new asset arrives during play
- **WHEN** a base model and its primary images are ready before unrelated enhancements
- **THEN** they become eligible independently and later material arrival does
  not rebuild the model or delay unrelated ready owners

### Requirement: Live consumer does not alter source gameplay
Live receipt SHALL reuse qualified source interfaces without a new fixed
refresh cap or source-thread waiting. The UE consumer SHALL keep SFC rendering
unchanged until a separately qualified native insertion transaction commits.

#### Scenario: Slow or absent UE consumer
- **WHEN** the UE process is delayed or exits
- **THEN** SFC's source callback continues normally and obsolete consumer work
  is discarded without presenting stale state as a new source frame

### Requirement: Inspection window can close normally
The packaged inspection application SHALL provide visible Exit and Escape
controls as well as ordinary operating-system window close handling.

#### Scenario: Exit during asset preparation
- **WHEN** the user closes the inspection application before its first frame
- **THEN** it cancels pending work and releases owned resources cleanly

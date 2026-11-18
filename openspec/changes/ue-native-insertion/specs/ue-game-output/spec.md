# UE game output

## Purpose

Transfer coherent UE-rendered pixels to SFC through the established native
insertion boundary, preserving source identity, depth, ownership and gameplay.

## ADDED Requirements

### Requirement: Standalone GPU transfer precedes native insertion
The UE backend SHALL demonstrate completed GPU-side colour, physical depth
and owner output in a standalone D3D11 consumer before native SFC insertion.
Built-in Epic facilities SHALL be evaluated before custom transfer code.

#### Scenario: A sharing mechanism cannot meet ownership or timing
- **WHEN** the qualified UE sharing mechanism fails an essential transfer condition
- **THEN** the missing condition is documented and native suppression remains
  disabled rather than using CPU screenshot transport or unverified handles

### Requirement: Output carries completed-image provenance
Each output transaction SHALL bind session, owner epoch, asset revision,
source frame/sequence, camera/pose/cohort identity, target/device generation
and output identity to its colour, physical depth and owner coverage.

#### Scenario: Visibly different frames are rendered in succession
- **WHEN** the producer renders two different source poses or frame markers
- **THEN** the consumer receives the correct pixels for each accepted identity,
  rather than accepting metadata attached to an older completed image

#### Scenario: Native resolution or device generation changes
- **WHEN** a target notice advances to a new size or device generation
- **THEN** old leases are retired before resource reuse and old-generation
  output cannot authorize insertion on the new target

### Requirement: Native colour depth and owner semantics are preserved
The backend SHALL supply the native consumer's qualified colour/depth/owner
formats and tactical viewport mapping. Owner bits and opaque black markings
SHALL survive transfer. UE depth SHALL be converted to the consumer's native
projection convention rather than treated as interchangeable world distance.

#### Scenario: Native foreground effects intersect the ship
- **WHEN** native shields, grid lines or depth-disabled text are drawn after insertion
- **THEN** they interact with the inserted ship through normal native ordering
  and depth without being captured and replayed by the UE adapter

### Requirement: Existing synchronization policy remains authoritative
The backend SHALL retain the standard ExtraFrame absolute admission deadline
and lease semantics without stacking additional unbounded waits or refresh caps.
Only actual completed output and completed game-side GPU copy may signal readiness.

#### Scenario: Output misses admission before insertion commits
- **WHEN** matching completed output is unavailable at the existing deadline
- **THEN** no original draw is suppressed for that transaction and stale output
  is not relabeled, while repeated ordinary-camera misses remain a failed gate

### Requirement: Replacement follows demonstrated additive insertion
The first native proof SHALL insert a correctly textured identified player
ship without original suppression. Only after that gate passes SHALL zero-offset
player replacement use capture-first Acquire/Commit/Cancel and owner-qualified
primary/secondary suppression through the existing native boundary.

#### Scenario: Matching output commits successfully
- **WHEN** zero-offset output for the qualified player's source transaction is inserted
- **THEN** only its supported original lists are suppressed after capture,
  leaving one visible player ship and native gameplay/effects intact

#### Scenario: Renderer disconnects before a replacement commit
- **WHEN** the renderer exits or the output identity becomes invalid
- **THEN** no new suppression commits occur, native rendering remains available,
  and pending leases and helper processes follow the existing recovery path

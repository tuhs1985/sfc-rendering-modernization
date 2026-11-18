## ADDED Requirements

### Requirement: Packaged captured scene rendering

The packaged UE5 proof SHALL construct a ship from a qualified SFC capture
and original source images, using the captured camera and viewport.

#### Scenario: Read a qualified captured ship

- **WHEN** the application receives a checked offline scene and its primary images
- **THEN** it preserves captured triangle membership, corner normals and UVs, and group image assignments
- **AND** its geometry and camera derive from the recorded source frame

### Requirement: Independent evidence

The proof SHALL record source identity and rendering results separately.

#### Scenario: Qualify packaged output

- **WHEN** the standalone package completes the proof
- **THEN** its report identifies the engine, capture, frame, mesh and images
- **AND** the output can be compared with the independent native projection reference

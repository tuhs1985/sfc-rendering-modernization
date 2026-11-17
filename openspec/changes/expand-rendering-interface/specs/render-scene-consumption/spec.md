## ADDED Requirements

### Requirement: Independent consumption of qualified scene data

The interface SHALL make qualified source scene data available to a consumer without requiring the Remix runtime or a D3D9 device to interpret it.

#### Scenario: Read an intact ship and a supported break model

- **WHEN** a consumer reads a qualified scene fixture with an intact ship and moving fragments
- **THEN** it can recover source asset and group identity, original image associations, instance lifetime and transforms, and the frame's camera and viewport
- **AND** the consumer can distinguish source values from adapter-specific material and coordinate conversions

### Requirement: Frame provenance and effect support

The interface SHALL preserve qualified frame, resource revision and ordering information for transient draws and report the limits of incomplete observations.

#### Scenario: A qualified transient draw is read

- **WHEN** an observed transient draw has a qualified source, primitive and effective render state
- **THEN** the consumer can associate its geometry, resource and render state with the correct frame and draw order

#### Scenario: An observed effect has incomplete evidence

- **WHEN** a resource, owner association or draw state is unknown
- **THEN** the interface reports the missing data and preserves the native path for unsupported rendering

### Requirement: Bounded normal play

Optional consumers SHALL operate within bounded storage and preserve SFC's normal rendering and fallback when they are slow or absent.

#### Scenario: A consumer misses a frame or disconnects

- **WHEN** the consumer is unavailable or cannot keep up
- **THEN** missed frame-local data is discarded without delaying SFC, and no unsupported or unmatched replacement is inserted

# M0 Semantic Rendering Ownership Map

## Best-supported ownership chain

```text
tEntityShip instance
  RTTI: .?AVtEntityShip@@
  vtable: 0x00796F0C
  render owner: 0x004162B9
  semantics: ship-owner identity, visual-model pointer at +0x88,
             object/world transform handoff
        |
        v
t3DVisual_Model instance
  RTTI: .?AVt3DVisual_Model@@
  vtable: 0x007985A4
  render/LOD owner: 0x0042FD3F
  semantics: stable model identity, model source at +0x158,
             LOD count/override/selection, selected child array at +0x160
        |
        v  virtual child call at 0x0042FDD2
tModel0 instance
  RTTI: .?AVtModel0@@
  vtable: 0x007983E8
  mesh owner: 0x0042E4B2
  semantics: stable mesh/LOD owner, source counts/pointers,
             flags and mesh/material-group fields
        |
        v  manager slots +0x138 / +0x13C
graphics-manager source state
  source init: 0x006ABF80
  source pointer: 0x006ABFB0
  semantics: source identity and counts; no explicit ship pointer
        |
        v
polygon preparation: 0x006ABFC0
  semantics: source/polygon-list identity, counts and flags
        |
        v
generic accumulation: 0x006AB410
  semantics: generic polygons and cached render state
        |
        v
batch flush: 0x006AB380
        |
        v
IDirect3DDevice3::DrawIndexedPrimitive: 0x006AB3C0
```

## Dynamic identity correlation

M0-RT-003 captured two stable tactical ownership chains:

| tEntityShip owner | t3DVisual_Model | tModel0 | Model source | Hits |
|---|---|---|---|---:|
| `0x1CC1A1D8` | `0x1CC11808` | `0x1CA3C3EC` | `0x0492365C` | 194 |
| `0x1CAE86C0` | `0x1CAE0E48` | `0x1CA3C0E0` | `0x1C9BB7F0` | 190 |

Both chains used graphics manager `0x04980038`, then converged into the
bounded source/polygon events, 1,500 generic submissions, 1,000 batch flushes,
and 1,000 indexed-draw calls. The procedure contained the player ship and at
least one other visible ship. The evidence distinguishes two ship owners but
does not assign which pointer is the player or target.

A third `tModel0` owner entered from `0x00509843` without a
`t3DVisual_Model` parent in the captured profile. It is a confirmed finite
exception path, likely non-ship/environment content, but its exact semantic
class is not required for the ship seam and remains unclassified.

## Semantic availability and loss

| Level | Ship identity | Model identity | Mesh/LOD identity | Transform | Material/texture identity |
|---|---|---|---|---|---|
| tEntityShip `0x004162B9` | explicit stable owner | pointer at `+0x88` | through model | matrix-like handoff present | indirect |
| t3DVisual_Model `0x0042FD3F` | parent relationship preserved | explicit stable owner | selected child and LOD fields | supplied by parent/manager | source retained |
| tModel0 `0x0042E4B2` | recoverable through caller, not an argument | parent relationship preserved | explicit stable owner | manager state | group fields and state calls present; exact material object layout open |
| manager source slots | absent | source pointer only | source/count identity | cached manager state | cached state only |
| polygon preparation | absent | absent | polygon-list identity only | baked/cached | generic state |
| `0x006AB410` and below | absent | absent | absent | generic vertices/state | generic bindings |

## Candidate modernization seam

The defensible seam is a cooperating chain rather than one function:

- primary owner: `tEntityShip::render` candidate at `0x004162B9`;
- model/LOD owner: `t3DVisual_Model` method `0x0042FD3F`;
- mesh owner: `tModel0` method `0x0042E4B2`;
- downstream validation anchor: manager source/polygon path through
  `0x006AB410`.

This chain retains ship, model, mesh/LOD, source, and transform intent before
genericization. Confidence is **CONFIRMED** for class identities, object
stability, call relationships, and downstream convergence. Exact material
layout and the non-ship exception taxonomy remain **STRONG HYPOTHESIS/open**.

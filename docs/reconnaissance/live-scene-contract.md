# Fresh live scene contract — protocol3 / component0.20

Authority/operating definition:[LIVE-SCENE-001](probes/LIVE-SCENE-001.md).
Default OFF,new start_live_scene_session.ps1 only;legacy protocol2 unchanged.
All integers little-endian DWORD.16MiB explicit current-user-only mapping.

| Offset | Contents |
| --- | --- |
|0|magic31424C53,version3,size16777216,state,4 UUID words|
|12|state0waiting/1running/2stopped/3failed|
|256+slot*64|4 slots:ready generation,ack generation,meshbytes,refsbytes,owner epoch,asset revision;remaining reserved|
|4096+owner-slot*512|32 slots:seqlock DWORD then96DWORD state|
|65536+slot*2097152|immutable-until-ack mesh packet immediately followed by resource JSON|

Native publishes descriptor generation LAST after payload+metadata. Receiver
copies and verifies descriptor twice,validates bounded packet,then acknowledges
that exact generation with aligned store. Worker does not reuse until ack==last
published generation. No timeouts that overwrite outstanding transfers. On slow
viewer shared4slots+preallocated native4staging slots saturate;new capture deferred,
original SFC renderer continues. Acknowledgements are not SFC command execution.

Owner state96words retains protocol2 camera block.0monotonic slotsequence,
1owner epoch,2frame,3tacticalms,4active1/retired2/unsupported3,5model label,
6source label,7asset revision (1..64,0pending).8..24suppliedM17words,
25..41engineC17words,42..44mathdispatch,45owner-table slot,46effective LOD child,
47reserved,48camera-valid1,49..65V17words,66..82P17words,83..88viewport
x,y,w,h,halfw,halfh floatbits;89..95reserved. Guard odd during write/evencomplete;
reader needs equal nonzero even guards around384bytes. No raw pointer dereference
outside native validated callback. Native pointer-shaped labels are provenance.

Asset wire remains sfc.mesh.v1 plus same-epoch sfc.texture.references.v1,expanded
bounded native storage only. Meshheader20..23 preserves LODcount/override/selection/
actualchild. Source fields/resource associations compared exactly;registry IDs
valid only inside that packet association,never cross-run keys. All asset revisions
immutable,global monotonic session1..64. Transfer generation belongs to slot,not
asset identity. Owner slots may be recycled after retirement but slotsequence
never resets and fresh owner epoch/revision is required.

Portable asset key=SHA256 of captured geometry/corner UV/normals/group data plus
groupflags and primary/secondary original image content hashes. Excludes native
labels,resource IDs,transforms/session metadata. Content-identical ships share USD
internal references;bindings retain fresh raw associations perrevision. No prior
import,expected ship name or frozen mesh dimensions required. Loader defaults to
qualified primary-only material;unknown secondary/alpha roles remain limitations.

One image-preparation worker outside SFC verifies/copies original bytes and exact
RGBA PNG/DDS derivatives;authoring happens on Kit update thread. USDsession
/Library holds shared assets,hidden by ancestor;visible /Ships/owner_<slot>
references asset root (not hidden ancestor). /Ships scale100;each instance gets
its own raw-converted live transform. Camera uses same fixed nativeorigin. Source
scratch stage unchanged,no USD Save. State/detail/output budgets in probe.

Malformed/pending/rejected/retired/stale owner hides,not substitutions. Camera
checks use each owner's matching M/V/P/viewport/C and actual USD transform;final
scene camera uses newest accepted frame. This is sampled asynchronous scene
delivery,NOT atomic whole-frame synchronization,returned depth/image readiness,
dynamic deformation support or every rendered tactical category.

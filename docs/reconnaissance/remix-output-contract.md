# Standalone Remix output contract — qualification version1

This is a prerequisite experiment, NOT the SFC replacement-frame contract.
No SFC hooks or scene capture are modified. Source output_channel.h is the wire
authority; State occupies<=4096B, fixed current-user-only Local mapping with
unique GUID. Host creates protected DACL allowing only its token user SID;
noninheritable handles, independently opened by owned child with explicit name.

The native D3D11 consumer allocates one256square BGRA8, one-mip, non-MSAA texture
with SHADER_RESOURCE|RENDER_TARGET and legacy SHARED flags. Its DXGI KMT handle
is published only through this user-only mapping. The Remix host imports that
handle using its public D3D9Ex CreateTexture and obtains its level0 surface.
Never cast VkImage to HANDLE; never CloseHandle a legacy DXGI/KMT handle. Native
consumer retains the owning D3D11 texture until host releases imported surface.
The KMT allocation is not a separately ACL-configurable NT handle: channel ACL
and owned same-user process boundary are tested here; do not advertise arbitrary
untrusted-process resource isolation or NT-handle/keyed-mutex support.

Flow: consumer READY -> host renders camera/mesh/light with SDK ->
CopyRenderingOutput(final colour, imported surface) -> D3D9 EVENT query END /
GetData(FLUSH) completes -> host publishes frame+sequence+verification hash ->
consumer GPU CopyResource to validation staging -> Map completes -> validate
matching hash and green triangle pixels -> ACK -> host can reuse same allocation.
No CPU pixel bytes travel across the mapping or create the consumer image.
Two fixed verification snapshots/readbacks establish provenance, colour and
movement orientation; they are diagnostics, never an image-return fallback.

Only two publication sequences (frame15 and31) in a32frame qualification run.
One in-flight surface, zero overwrites before ACK. Magic/version/size/dimensions/
format/reserved fields and exact sequence are checked; incomplete/stale messages
fail closed. Child records output hash/green count/horizontal centroid, host
requires exact pixels and rightward change for the controlled positive-X move.
The asynchronous SFC semantic30Hz stream is not used or declared frame-coherent.

Consumer startup/ACK wait<=5s, total child<=110s; runner<=120s/log32MiB warning16.
Standalone waits do NOT define future SFC compositor behavior: the game must
only use nonblocking readiness checks and omit unavailable output. GPU output
allocation262144B; one fixed producer validation staging and one consumer staging
also256square. No slot/image/resource growth. Project host owns child in a
kill-on-close job; on success releases imported GPU views before stop/clean child
exit. Crash kills only owned child; channel released when handles close.

Commands: build_output_probe.ps1 then run_output_probe.ps1 -Mode crossprocess.
No SFC launch, proxy installation, original suppression or game image returned.
Full first gate also needs failure-path tests; cross-process pixel success alone
does not authorize claiming the in-game returned-image or replacement gates.

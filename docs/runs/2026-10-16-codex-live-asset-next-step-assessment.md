# Codex run — next live asset delivery assessment

Date/task:2026-10-16,live bridge next-step assessment; no implementation authorized
or performed in this question/answer turn. Starting HEAD fee152f,index empty,
inherited dirty work retained. Question: must live mesh data come from SFC,or can
the Remix-side package read native model files?

Read live-bridge-contract.md and live_bridge.py qualification/asset channel code.
CONFIRMED current channel already carries a fresh bounded mesh+resource packet
from SFC in immutable asset slots. Receiver verifies geometry/UV/normal/group
content against the accepted preview and resolves original images by filename/hash.
Display still uses the pre-imported USD geometry,not newly constructed live mesh.
Thus fresh mesh transport exists; fresh mesh-driven display is the missing next link.
Prior shorthand "pre-captured mesh" describes displayed asset,not absence of fresh
runtime geometry capture. No statement that continuous image pixels are transported.

Official sources checked via web search:
- https://docs.omniverse.nvidia.com/kit/docs/rtx_remix/latest/docs/howto/learning-ingestion.html
  documents standard asset ingestion,not native SFC .mod support.
- https://github.com/NVIDIAGameWorks/dxvk-remix/blob/main/documentation/RemixSDK.md
  documents runtime CreateMesh/DrawInstance; distinct from current Toolkit USD
  preview. API availability does not choose final architecture or prove compatibility.

Recommendation/inference: first replace known-template-dependent display with a
mesh constructed from fresh qualified packet into session layer,using fresh
resource filenames to load original images off rendering thread. Keep live owner/
camera updates. Begin same known ship;prove displayed vertices/indices/UV/groups
match packet and no pre-imported model dependency. Then qualify a different model
or LOD in a separately bounded step. Do not promise arbitrary/damaged/deforming
assets without limits,lifetime rules and evidence. No need to resend static asset
every frame;publish new content on qualified asset/revision changes.

Direct native-file loader is possible project work,not confirmed built-in Remix
support;files alone do not supply active LOD,owner/lifetime or runtime mesh changes.
No model parser/new renderer/asset mutation implemented. No new capture/test needed
for this read-only assessment. Validation: source paths read,git diff --check PASS;
only this record added,not staged/committed. Fuel Guard attach exact-thread recent
hook verified,directsandbox denied/quota unknown,no daemon/helper started.

Next exact action: obtain sponsor approval for bounded fresh-packet-to-viewer mesh
construction increment;retain current proven state/camera path and capture bounds.

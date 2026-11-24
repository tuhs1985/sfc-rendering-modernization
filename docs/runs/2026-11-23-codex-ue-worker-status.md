# November 23 — UE live startup rejects native worker status

Both `20261123-223501-824131-in-game` and
`20261123-223542-142937-in-game` ended with `UE inspection window closed` before
any asset or source frame was admitted. UE exited zero, a known Shipping
rejection-reporting limitation. SFC exited normally and both proxy transactions
restored; protected client files and launcher settings remained unchanged.

## Root cause and correction

The read-only C++ adapter incorrectly interpreted common transport word 3 as
the source PID. The actual `LiveScene::run` in `m1_live_scene.h` writes worker
status there: 0 passive, 1 running, 2 stopped, 3 failed. The actual source PID is
in the version3 scene-store header. As soon as the worker wrote 1, the adapter
rejected it against the game PID. The replay fixtures incorrectly wrote a PID
into that same status field, concealing the mismatch. The standalone rendering
results do not establish the previously missed native-startup boundary.

Correcting the native-view fixture to running=1 first fails `No source frame
yet` before implementation. The adapter now interprets common worker status,
while retaining exact scene-header PID/session validation and the held source
process handle. Native tests additionally reject PID values in the status word,
failed workers and wrong scene PIDs, and handle normal worker stop. All six UE
replay publishers now use the actual common status semantics. No source DLL,
wire layout, graphics setting, renderer geometry or material behavior changed.

## Verification

- x86/x64 source-view and actual Windows mapping/process tests pass.
- `source-service-status-01` passes real original transfer/ACK, neutral resource
  preparation, catalogue admission and 20 completed Shipping GPU samples, with
  one mesh and correct native running status. No source geometry/image edit.
- `source-lifetime-status-01` passes passive stop, independent supervisor death
  and immediate fresh-session relaunch.
- Exact passive live-launch arguments also remain alive without native attach;
  that reproduction alone did not reproduce the failing worker transition.

Shipping and Development are rebuilt for the fix. Read-only launcher preflight
must pass before retrying the same sponsor command. Live SFC checkout is still
pending; task 3.5 stays open. All changes remain uncommitted.

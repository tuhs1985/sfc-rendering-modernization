# Codex run — MIP-POLICY-MINUS1-20261016

Newer adjudication: [config verification](2026-10-16-codex-mip-config-verification.md)
CONFIRMS child file loading and effective native startup value -1 from existing
log lines109–143. Uncertainty below about startup acceptance is historical;
per-pixel sampling/path behavior and the negative visual result remain unresolved.

Sponsor authorized next bounded preview policy test. Read current HANDOFF/base-mip
run checkpoint. HEADfee152f137a55a3efeb47a5c236ebf9e3e1951cb,index empty,165
short-status entries initially; inherited dirty work retained. Fuel Guard trusted
recent exact-thread hook verified/direct access denied; no daemon started. Earlier
quota guidance requires finishing this one experiment and checkpointing, not further
scope expansion. No helper, game run, renderer replacement, staging or commit.

## Hypothesis / mechanism

Could a conservative higher-detail mip preference recover sharpness while retaining
all normal mip levels? New explicit `--sharper-mip` flag in run_mesh_preview.py
requires textured smoke mode, excludes base-only mode. In NEW scratch child config
only, append `rtx.nativeMipBias = -1`; record before/after config hashes/requested
value in `mip-policy-test.json`. Source files/DDS mip chain, UV, geometry, synthetic
camera/lights and established NRC-off environment unchanged. Native option string
`nativeMipBias` found in installed x64 d3d9 runtime, but presence is NOT proof that
this requested value is applied to this renderer's texture path. No effective-value
getter available; record request, not fabricated readback. Default config unchanged.
Probe definition/addendum recorded in MESH-PREVIEW-001 before execution.

## Reproduction and validation

Bundled Python3.12.14/Pillow12.3.0, Toolkit1.6.0-dev/Kit110.1.1, existing owned
Job Object guard. Process PYTHONDONTWRITEBYTECODE=1; tests TEMP/TMP=artifacts/m1/test-temp.

```text
python -m unittest discover -s tools/remix_ingest -p test_*.py
python tools/remix_ingest/run_mesh_preview.py --job C:/Project/RemixJobs/20261016-050350Z-6dffd5be --textures --smoke --sharper-mip
git diff --check
```

25 relevant tests PASS. Graphics replay ran outside sandbox with existing scoped
approval,180s wall/256MiB scratch/8MiB console/three8MiB PNG caps. No global/UAC
or security changes. Expected a bounded hypothesis test, not a guaranteed fix.

## Observed result / confidence

Job `C:/Project/RemixJobs/preview-20261016-120308Z-98f73eb7`:18.703s,exit0,
no remaining owned processes; peak scratch1238641bytes, console24546bytes,
no cap warning. Same452triangles/11mesh prims, source USD SHA
`5c08f217b36ef9056c3a1940931ff2fd463286ca67e120d7bd80269b997634b2`
unchanged. All five test DDS hashes equal the unchanged baseline DDS (full chains).

Analyst inspected above.png: still soft, similar to baseline, not the visibly
sharper base-only result. Against unchanged baseline051922, above whole-frame
MAE RGB≈0.0975/0.0963/0.0969 and RMSE≈0.745/0.772/0.727; against base-only052216,
MAE≈1.137/0.984/1.038,RMSE≈6.83/6.11/6.15. Black background/stochastic rendering
mean these are not sharpness scores or causal proof. All three views/metrics saved
in mip-policy-comparison.json. No new screenshot edited or rescaled for comparison.

CONFIRMED: requested config variant produced no comparable visible improvement;
full mip chains/originals preserved. UNRESOLVED: whether the native renderer applied
the request, whether another layer overrides it, or whether this control affects
the relevant sampling path. Do not infer that -1 is merely insufficient; do not
increase bias blindly or adopt a new default. Base-only diagnostic remains stronger
evidence that mip availability contributes; actual native policy still unqualified.
Overall texture recovery remains PARTIAL; no fidelity/production policy/gate PASS.

## Evidence / handoff

Versionable changes: opt-in runner flag, probe addendum, this record and HANDOFF.
No source/installed assets or defaults changed. Verified43-file ZIP:
`artifacts/remix-ingest/evidence/20261016-mip-policy-minus1.zip`,597021bytes,
SHA256 `5e51c5b7da7dc8f9073184ad5f545e2141aa289dc79a91e53336451c9b6f1b1b`.
Includes config/requests/logs/texture copies/three PNGs/comparison metrics, portable
caches excluded; no raw/source evidence deleted or multi-GB output. No game/viewer
process active. HEAD unchanged/index empty,166 short-status entries after record;
inherited/new work unstaged, no commit. Diff check PASS.

Exact next smallest action after restart: verify whether the native preview loads
and honors the child mip-bias request before any stronger/different policy test.
Do not rerun capture/extraction/base-only proof, ask sponsor for another recognition
comparison, or widen into brightness/geometry/glow fixes. Stop this run here.

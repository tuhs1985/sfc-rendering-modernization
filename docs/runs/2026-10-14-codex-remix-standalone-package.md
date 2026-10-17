# Codex run — official standalone Remix Toolkit acquisition

- ID/date: `2026-10-14-remix-standalone-package`, America/New_York.
  Sponsor explicitly requested standalone after reporting NVIDIA-app installation
  failure. Scope: acquire/prepare Toolkit separately from SFC, not live Remix
  deployment, driver updates, renderer selection or a game/capture run.
- Start HEAD `fee152f`, 144 inherited pending Git status paths, cached diff empty.
  Read newest HANDOFF; preserve all inherited code/docs/evidence. Fuel Guard
  recent hook verified; direct sandbox connection denied, no daemon started.

## Provenance / tool choice

- Official [NVIDIA standalone instructions](https://docs.omniverse.nvidia.com/kit/docs/rtx_remix/latest/docs/installation/install-toolkit.html)
  checked2026-10-14; GitHub prebuilt distribution explicitly a potentially
  unstable **development package**, not the NVIDIA-app stable channel. Sponsor
  informed of development label before download. No mirror/runtime-only release.
- Official workflow: [toolkit-package.yml](https://github.com/NVIDIAGameWorks/toolkit-remix/actions/workflows/toolkit-package.yml).
  Live public GitHub API resolved successful run
  [38619866886](https://github.com/NVIDIAGameWorks/toolkit-remix/actions/runs/38619866886),
  created `2026-10-14T18:59:33Z`, workflow head
  `95b9aa4fe84475815f6249e012a0aba942c75387`.
- Artifact ID **11921797093**, name
  `rtx_remix@1.6.0-dev+main.3f23f80a.gl.windows-x86_64.release`, not expired.
  Package revision label differs from workflow head; do not conflate the two.
  Published ZIP size **2,118,847,088 bytes** and digest
  `83F3E5C2B6094CCF5084EE3AE2652D91D6F43F3F729274519741C130FDAFB781`.
  API URL: `https://api.github.com/repos/NVIDIAGameWorks/toolkit-remix/actions/artifacts/11921797093/zip`.
- PowerShell + existing `C:\Program Files\GitHub CLI\gh.exe`; default sandbox
  network attempt failed, including misleading invalid-login diagnostic. Approved
  network escalation verified existing keyring authentication works. No login,
  token recovery/exposure, account change or browser authentication automation.
  Only public NVIDIA repository metadata/artifact accessed.

## Material acquisition command / bounds

Create new external-to-SFC-repository directory
`C:\Project\RTXRemix-Standalone\download`. Refuse existing ZIP overwrite.
`Start-Process gh.exe` with arguments
`api repos/NVIDIAGameWorks/toolkit-remix/actions/artifacts/11921797093/zip`,
hidden window, stdout redirected as binary ZIP to
`C:\Project\RTXRemix-Standalone\download\rtx-remix-1.6.0-dev-main.3f23f80a.zip`,
stderr to adjacent `download.stderr.log`. Owned download PID33872.
Poll owned process at1s; 15-minute timeout / 2,200,000,000-byte hard stop, retain
partial on failure. SHA256 must equal published digest before any extraction.
No undocumented credentials or shell history required for reproduction.

At acquisition start C drive free space **242,183,598,080 bytes**. Download is
tooling, not a rendering capture; no change to existing capture/log limits.
Inspect ZIP directory for total expanded size and path confinement before
extraction into a short, separate new directory. Do not execute vendor scripts
or alter game DLLs merely to acquire the package.

## Result / evidence / final state

Download COMPLETE: exact published size **2,118,847,088 bytes**, published SHA256
matched. Existing authenticated GitHub CLI worked with approved network access;
no new authentication was needed. No token values persisted in source/docs.

ZIP preflight: **38,679 entries**, **4,866,493,006 expanded bytes**. All canonical
entry paths confined beneath new `C:\Project\RTXRemix\`; reject colon/ADS paths,
escaping paths and Unix symbolic links. Caps6,000,000,000 expanded bytes/50,000
entries. Destination must not exist; no merge/overwrite. .NET
`[IO.Compression.ZipFile]::ExtractToDirectory(zip, root)` used only after digest
and preflight. ZIP+payload total **6,985,340,094 bytes**, about6.99GB decimal,
excluding negligible filesystem/log overhead; no trace/capture generated.
No package deletion: original verified ZIP retained for reproducibility.

Extraction COMPLETE, no errors, into **`C:\Project\RTXRemix`**. Portable standalone
package acquired, not a registry/NVIDIA-app managed installation. App manifest
`apps/lightspeed.app.trex.kit` confirms `version = "1.6.0-dev"`.
`kit/kit.exe` Authenticode **Valid**, signer NVIDIA Corporation; FileVersion field
empty, so use manifest/package revision rather than inventing an EXE version.

Verified present: GUI launcher, ingestion CLI launcher, Kit EXE, GUI and CLI
app configs, model-ingestion schema, packman Python wrapper and CLI Python file.
Read launcher scripts without executing: GUI calls included Kit/app; CLI calls
packman Python + mass-validator CLI; `install.bat` only requests warm-up apps.
No vendor launcher/installer/warm-up/ingestion executed; no UI/login/license or
security prompts handled. Extraction is not proof of successful app launch or
SFC asset ingestion. No extra package/model/driver downloads initiated.

Pinned file SHA256:

- `lightspeed.app.trex.bat`:
  `F33EE9361CA734465B129D6AE0B1036F30D83815E365DEBC1F10F6A83DE5E0E7`.
- `lightspeed.app.trex.ingestcraft.cli.bat`:
  `FBAF58BCC1E6CC841AE0B7CA04B5FB938EBE6DF8441D001BD1325F56E7AC7E16`.
- `exts/lightspeed.trex.app.resources/data/validation_schema/model_ingestion.json`:
  `1860E98CFA28A3D0D0686A96E2DDAFAB92CC9B84BCDB29B29783028CD910C878`.

Reference and installed SFC clients independently hash-checked unchanged:
`4D65761D7DD69EF1504070261B81E9C200C0AF18105033E1C4D2222C62320C29`.
Only this run record, HANDOFF and Stage B runbook changed in the SFC repository;
no source/tools/build/test changes, so documentation/status checks suffice.
Final validation: referenced local paths/Markdown links and tracked/new-record
whitespace checks PASS. Git HEAD `fee152f`, **145 pending status paths**, cached
diff empty; nothing staged/committed. Download/extraction jobs completed; no
Toolkit process launched. No source changes requiring a build/test rerun.
No helper, source changes, stage/commit, driver/security setting changes or
game/reference modifications. No automatic raw cleanup/deletion.

Exact next action: validate standalone first launch from
`C:\Project\RTXRemix\lightspeed.app.trex.bat` in an accessible desktop, then
prepare the bounded Stage B ingestion runner for this exact package. No game
DLL deployment or actual mesh-ingestion claim; real ship capture still unexecuted.

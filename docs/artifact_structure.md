# Artifact structure

The public certificate records are stored under `certificate/`.

| Path | Purpose |
|---|---|
| `certificate/final_chain/` | Bundled component archives used by the replay commands. |
| `certificate/manifest/` | Hashes and manifest files fixing the certificate contents. |
| `certificate/public/` | Human-readable index, proof boundary, replay commands, and final status records. |

The structure intentionally avoids embedding the certified threshold in directory or file names; the target appears in the file contents and verification status.

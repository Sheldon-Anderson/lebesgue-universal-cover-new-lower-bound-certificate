# Release audit

The release audit verifies that the certificate manifest, hashes, final verification gate, final aggregation gate, archive/public mirror, paper claim boundary, and claim boundary are mutually consistent.

Expected release status:

- `theorem_ready = true`
- `final_blocker_count = 0`
- `claim_boundary_ok = true`
- `artifact_hashes_verified = true`
- `archive_public_mirror = passed`

The release package should not contain Python bytecode artifacts, LaTeX intermediate files, generated `runs/` output, or checked text files without a final newline.

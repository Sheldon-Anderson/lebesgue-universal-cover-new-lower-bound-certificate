# Reviewer checklist

1. Read `certificate/public/PROOF_BOUNDARY.md` and the paper's scope statement.
2. Run `python scripts/check_repository.py --root . --log-level INFO` on a clean unpacked repository tree.
3. Run `python scripts/replay_certificate_chain.py --root . --log-level INFO` if component-level replay detail is desired.
4. Confirm that the certificate verification reports `artifact_hashes_verified = true`.
5. Check that the certified threshold is `0.833`.
6. Confirm `final_blocker_count = 0` and `claim_boundary_ok = true` in the public status records.
7. Confirm that the archive/public mirror diagnostics pass for expanded CSV/JSON records.
8. Verify that the claim is restricted to the convex Brass-Sharifi three-test-set certificate model.
9. If running developer tests, use `python -B -m unittest discover -s tests` so the source tree remains bytecode-free.

10. Confirm that the release archive does not include `runs/`, Python bytecode, or LaTeX intermediate files.

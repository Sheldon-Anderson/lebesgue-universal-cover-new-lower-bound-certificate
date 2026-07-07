# Reviewer checklist

1. Read `certificate/public/PROOF_BOUNDARY.md` and the paper's scope statement.
2. Run `python scripts/check_repository.py --root . --log-level INFO`.
3. Run `python scripts/replay_certificate_chain.py --root . --log-level INFO` if component-level replay detail is desired.
4. Check that the certified threshold is `0.833`.
5. Confirm `final_blocker_count = 0` and `claim_boundary_ok = true` in the public status records.
6. Verify that the claim is restricted to the convex Brass-Sharifi three-test-set certificate model.

# Certificate index

This directory contains the public certificate records for the certified lower-bound threshold.

## Certified statement

The finite certificate verifies the exact decimal threshold

```math
\tau = 0.833
```

in the normalized convex Brass-Sharifi three-test-set certificate model. Together with the normalization principle, it gives the convex consequence

```math
\alpha_{\mathrm{cvx}} \ge 0.833.
```

## Public records

| Path | Purpose |
|---|---|
| `status/` | Final certificate status, final verification status, readiness gate, and claim-boundary status. |
| `data/` | Frozen record inventory, final verification ledger, event-aware interval replay records, witness/source records, thin extra records, and final aggregation gate. |
| `report/` | Human-readable final verification report. |
| `PROOF_BOUNDARY.md` | Claim scope and non-claims. |
| `REPLAY_COMMANDS.md` | Public replay commands. |
| `THEOREM_READY_SUMMARY.md` | Compact final-readiness summary. |

The public verifier checks the manifest, hashes, final verification gate, final aggregation gate, blocker count, and claim boundary.

# Verification design

The verifier is replay-only. It checks records already bundled with the release and does not perform the original geometric search.

The public certificate verification has four theorem-critical components:

1. per-record evidence checks for frozen supporting records;
2. construction-audit checks for event-aware and thin extra interval records;
3. witness-construction checks for witness and source-reconstruction records;
4. final verification checks for the aggregation gate, blocker count, and claim boundary.

The repository release check adds public-package checks around the certificate verification: Python compilation, package metadata, public script entry points, repository layout, Markdown math fragments, public narrative, claim-boundary restrictions, and certificate artifact hashes.

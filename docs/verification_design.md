# Verification design

The verifier is replay-only. It checks records already bundled with the release and does not perform the original geometric search.

The public certificate verification has four theorem-critical components:

1. per-record evidence checks for frozen supporting records;
2. construction-audit checks for event-aware and thin extra interval records;
3. witness-construction checks for witness and source-reconstruction records;
4. final verification checks for the aggregation gate, blocker count, and claim boundary.

The main certificate verification and certificate-chain replay also check the fixed SHA256 manifest for theorem-relevant artifacts before accepting the bundled records. These are finite-record checks on archived certificate data; they do not regenerate the search that produced the records.

The repository release check adds public-package checks around the certificate verification: Python compilation, package metadata, public script entry points, repository layout, bytecode-artifact exclusion, generated build artifact exclusion, text-file final-newline checks, Markdown math fragments, public narrative, README/docs claim-boundary restrictions, LaTeX paper claim-boundary restrictions, certificate artifact hashes, archive/public mirror consistency, and release/version consistency.

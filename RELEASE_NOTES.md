# Release notes for v0.15.4

This release verifies the exact decimal threshold `0.833` in the normalized convex Brass-Sharifi three-test-set certificate model.

Highlights:

- certified threshold: `0.833`;
- frozen certificate records: 3,411;
- final-replay-only records: 2,790;
- event-aware interval records: 493;
- witness/source records: 117;
- thin-extra records: 11;
- final blockers: 0;
- claim boundary: convex Brass-Sharifi three-test-set model only;
- runtime logging dependency: `loguru>=0.7.0`;
- repository release check includes release/version consistency diagnostics;
- main certificate verification and certificate-chain replay check the fixed SHA256 manifest;
- repository release check verifies archive/public mirror consistency for expanded CSV/JSON records;
- component-level replay CLI wrappers share a common runner to avoid duplicated command plumbing;
- repository release check rejects Python bytecode artifacts, LaTeX intermediate files, and checked text files missing a final newline;
- README display formulas use GitHub-safe fenced `math` blocks;
- the paper tables have manually balanced column widths for the release PDF;
- the paper source was cleaned for public release hygiene while preserving the manually balanced table layouts.

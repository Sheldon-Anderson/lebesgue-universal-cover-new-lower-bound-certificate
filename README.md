# A Certified Lower Bound for Lebesgue's Universal Cover Problem

Release: `v0.15.4`.

This repository contains the bundled finite certificate records and deterministic Python verifier for the certified threshold `0.833` in the convex Brass-Sharifi three-test-set framework. It is a verification package for records already included in the repository. It does not rerun the original geometric search, and it does not regenerate the certificate archives from scratch.

## 1. Certified statement

The bundled certificate verifies the exact decimal threshold $\tau=0.833$ for the normalized Brass-Sharifi three-test-set lower-bound problem. Together with the Brass-Sharifi normalization principle, this gives the convex certificate consequence

```math
\alpha_{\mathrm{cvx}} \ge 0.833.
```

Here $\alpha_{\mathrm{cvx}}$ is the infimum of the areas of convex universal covers. The proof uses a finite cover of the admissible normalized placement domain, supporting local records, witness-domain polygon records, outward-rounded interval estimates, and a final aggregation check.

## 2. Scope and non-claims

Claimed:

- finite-record verification of $\tau=0.833$ in the convex Brass-Sharifi three-test-set certificate setting;
- the corresponding convex certificate consequence for $\alpha_{\mathrm{cvx}}$;
- deterministic replay of theorem-relevant checks from the bundled certificate records.

Not claimed:

- a result for the unrestricted nonconvex problem;
- a proof-assistant formalization;
- completed independent external verification;
- a rerun of the original geometric search or regeneration of the certificate archives.

## 3. Repository layout

| Path | Purpose |
|---|---|
| `certificate/final_chain/` | Four theorem-relevant certificate-chain archives used by the public replay. |
| `certificate/manifest/` | SHA256 manifests and checksum notes for theorem-relevant artifacts. |
| `certificate/public/` | Expanded public certificate ledgers, status files, and proof-boundary notes. |
| `ucbs/config/` | Release metadata, certificate schemas/counts, archive member paths, logging policy, and repository policy configuration. |
| `ucbs/certificate/` | Certificate-chain readers and component replay checks. |
| `ucbs/verification/` | Repository-level checks, claim-boundary linting, artifact hashes, archive/public mirror checks, and release/version consistency checks. |
| `ucbs/cli/` | Command-line entry points and loguru-backed logging helpers. |
| `scripts/` | Direct source-tree wrappers for the public commands. |
| `tests/` | Developer regression tests for command help, validation helpers, logging, release metadata, README commands, archive mirrors, claim boundaries, and paper/count consistency. |
| `docs/` | Reproducibility notes, output fields, artifact policy, data dictionary, verification design, and reviewer checklist. |
| `paper/` | Compiled paper PDF and LaTeX source. |

The certificate data needed for public verification are already bundled. No external data download is required.

## 4. Verification design

The public verifier works at finite-record level. It checks the bundled archive members, schemas, row counts, pass/status fields, positive surplus fields where applicable, final-ledger class counts, zero final blockers, SHA256 hashes, and the convex claim boundary. It does not perform the original search that produced the certificate records.

The repository check also validates release hygiene: Python compilation, package metadata, release/version consistency, paper title consistency across LaTeX source, PDF metadata source, `CITATION.cff`, and README, script wrappers, repository layout, bytecode-artifact exclusion, generated-artifact exclusion, generated build artifacts, text-file final-newline hygiene, empty directories, English-only Python comments/docstrings, direct `print` avoidance, public Markdown math, narrative linting, README/docs claim boundaries, paper claim-boundary text, artifact hashes, archive/public mirror consistency, and the main certificate verification.

Runtime logging is implemented with `loguru` through `from loguru import logger`. Human-readable log files are written under `runs/<run-id>/log/`. Compact machine-readable summaries are still emitted to standard output as JSON.

## 5. Prerequisites

Use Python `>=3.10`.

Install the runtime dependency before running installed command-line entry points from a fresh environment:

```bash
python -m pip install -r requirements.txt
```

The only runtime dependency is:

```text
loguru>=0.7.0
```

## 6. Quick verification

Run the release check from a clean unpacked repository root:

```bash
python scripts/check_repository.py --root . --log-level INFO
```

A successful repository check also runs the main certificate verification internally. Editable installation is not required for `python scripts/...` commands.

Recommended review order:

1. Run the repository release check first on a clean unpacked tree.
2. Run the main certificate verification or component replays when more detail is needed.
3. If developer tests are needed, run them with `python -B` so the source tree remains bytecode-free.
4. Do not package the generated `runs/` directory.

## 7. Command reference

The direct source-tree commands below are the recommended review path. After an editable install, the equivalent installed command-line entry points are also available: `ucbs-verify-certificate`, `ucbs-check-repository`, `ucbs-replay-certificate-chain`, `ucbs-replay-per-record-evidence`, `ucbs-replay-construction-audit`, `ucbs-replay-witness-construction`, and `ucbs-replay-final-verification`.

### 7.1 Main certificate verification

```bash
python scripts/verify_certificate.py --root . --log-level INFO
```

This verifies the bundled certificate-chain records, including the fixed SHA256 manifest, and writes status files under `runs/certificate_verification/`.

### 7.2 Repository release check

```bash
python scripts/check_repository.py --root . --log-level INFO
```

This checks the public release package, including release/version consistency, paper title consistency, archive/public mirror consistency, paper claim-boundary text, generated build artifacts, final-newline discipline, artifact hashes, and the main certificate verification.

### 7.3 Certificate-chain replay only

```bash
python scripts/replay_certificate_chain.py --root . --log-level INFO
```

This replays the four certificate-chain components and checks the fixed SHA256 manifest, without README, documentation, repository-layout, or release/version checks.

### 7.4 Component-level replay

```bash
python scripts/replay_per_record_evidence.py --root . --log-level INFO
python scripts/replay_construction_audit.py --root . --log-level INFO
python scripts/replay_witness_construction.py --root . --log-level INFO
python scripts/replay_final_adjudication.py --root . --log-level INFO
```

These commands isolate the four replay components. See `docs/reproducibility.md` for details and expected output locations.

### 7.5 Developer regression tests

```bash
python -B -m unittest discover -s tests
```

These tests are not required to verify the mathematical certificate, but they are part of release maintenance. The `-B` flag prevents Python from writing `__pycache__` directories or `.pyc` files; the repository release check intentionally rejects those bytecode artifacts. The test suite currently covers:

- command help for public wrappers;
- shared certificate-validation helpers;
- GitHub-safe Markdown math linting;
- public narrative linting;
- loguru-backed file logging;
- release/version, dependency, citation, and paper title consistency, including `ucbs.__version__`;
- README command coverage;
- archive/public mirror consistency for expanded CSV/JSON certificate records;
- paper claim-boundary checks for `paper/source/main.tex`;
- agreement between configured certificate counts and the LaTeX paper tables.

## 8. Expected outputs

The main certificate verification should include:

```json
{
  "status": "passed",
  "certificate_verified": true,
  "threshold_proved": true,
  "certified_threshold": "0.833",
  "artifact_hashes_verified": true,
  "failed_component_count": 0
}
```

The repository release check should include:

```json
{
  "status": "passed",
  "failed_step_count": 0
}
```

For detailed output fields, see `docs/expected_outputs.md` and `docs/data_dictionary.md`.

## 9. Certificate records and hashes

The certificate-chain archives are stored under `certificate/final_chain/`. The key artifact hashes are listed in `certificate/manifest/key_artifacts_sha256.txt`, and the structured manifest is `certificate/manifest/final_certificate_manifest.json`.

`python scripts/verify_certificate.py --root . --log-level INFO`, `python scripts/replay_certificate_chain.py --root . --log-level INFO`, and `python scripts/check_repository.py --root . --log-level INFO` verify those hashes before accepting the bundled certificate records. The repository release check also verifies that the expanded public CSV/JSON files under `certificate/public/` match their corresponding ZIP members byte for byte.

## 10. Paper and citation

The compiled paper is:

`paper/A_Certified_Lower_Bound_for_Lebesgues_Universal_Cover_Problem.pdf`

The LaTeX source is under `paper/source/`. The repository release check requires `paper/source/main.tex`, `paper/source/macros.tex`, and `paper/source/figures/fig_placement.tex` to be present. Final release packages should not include LaTeX intermediate files such as `.aux`, `.log`, `.out`, `.fls`, `.fdb_latexmk`, or `.synctex.gz`.

Please cite this package using `CITATION.cff`.

## 11. Markdown math rendering

Display formulas in this README intentionally use fenced `math` blocks for GitHub rendering stability. Inline mathematics is kept to short fragments. The repository Markdown linter rejects unstable display delimiters and unsupported operator macros before release.

## 12. Troubleshooting

For reproducibility notes, see `docs/reproducibility.md`. For common questions and scope boundaries, see `docs/faq.md` and `docs/claim_scope.md`.

If a repository check fails after developer testing, remove generated `__pycache__` directories, `.pyc` files, LaTeX intermediate files, and the `runs/` directory, or rerun developer tests with `python -B -m unittest discover -s tests`.

## 13. License

The code and public documentation are released under the MIT license; see `LICENSE`.

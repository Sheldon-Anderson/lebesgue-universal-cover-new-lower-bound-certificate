# Reproducibility

Run commands from the repository root. The public verifier uses only the records bundled in `certificate/final_chain/` and `certificate/public/`; it does not rerun the original geometric search.

## Recommended review order

1. Start with a clean unpacked repository tree.
2. Run the full repository release check.
3. Run the main certificate verification or component replays for more detailed diagnostics when needed.
4. Run developer tests with `python -B` if release-maintenance checks are desired.
5. Do not package the generated `runs/` directory.

## Full repository release check

```bash
python scripts/check_repository.py --root . --log-level INFO
```

This command checks Python compilation, package metadata, public script entry points, repository layout, Python bytecode exclusion, generated build artifacts, final-newline discipline, Markdown math fragments, public narrative, README/docs claim boundaries, paper claim-boundary text, certificate artifact hashes, archive/public mirror consistency, and the main certificate verification.

## Main certificate verification

```bash
python scripts/verify_certificate.py --root . --log-level INFO
```

This command verifies the four theorem-critical certificate components, checks the fixed SHA256 manifest, and writes diagnostics under `runs/certificate_verification/`.

## Certificate-chain replay

```bash
python scripts/replay_certificate_chain.py --root . --log-level INFO
```

This command verifies the certificate-chain components and fixed SHA256 manifest without the README, documentation, repository-layout, and release-quality checks.

## Component-level replay commands

```bash
python scripts/replay_per_record_evidence.py --root . --log-level INFO
python scripts/replay_construction_audit.py --root . --log-level INFO
python scripts/replay_witness_construction.py --root . --log-level INFO
python scripts/replay_final_adjudication.py --root . --log-level INFO
```

These commands are useful for locating a failure within one certificate component. A successful run writes a compact JSON summary and a feedback ZIP under `runs/`.

## Developer regression tests

```bash
python -B -m unittest discover -s tests
```

The `-B` flag keeps the source tree free of `__pycache__` directories and `.pyc` files. The release check rejects those files intentionally.
